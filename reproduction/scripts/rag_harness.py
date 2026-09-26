#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-4 Appendix B v3: fair comparison of risk-gated injection × tiered RAG.

Fairness design (the five points reviewers will check):
 F1 Retrieval pool includes definition clauses: every "X means …" definition sentence per contract
    goes into the retrieval pool (--pool-with-defs, on by default; v2 only had definitions for 30% of terms in the pool).
 F2 Retrieval tiers named accurately: BM25 / T2 classic (single-path dense + cross-encoder) / T1 industrial
    (--hybrid: BM25+dense RRF fusion → large candidate set → reranker).
 F3 Token-matched arm rag_plus: add extra retrieved passages until total tokens ≈ gated arm, ruling out "longer context is just better".
 F4 Definition-recall arm rag_defrecall: equivalent of T0-style parent/child chunking or backtracking—attaches, without gating,
    the definitions of all defined terms that appear in the retrieved passages.
 F5 top-k tuned on the rag arm itself (--tune-k 3,5,8 on a separate tuning set --tune-questions), then used for all arms.
Arms: none | rag | rag_plus | rag_full | rag_gated | rag_defrecall | gated_only
"""
import argparse, json, math, os, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env

SYS = "You answer multiple-choice questions about a contract. Use the provided context if any. Answer with the letter only."
TOK = re.compile(r"[A-Za-z][A-Za-z0-9\-']*")
def toks(s): return [w.lower() for w in TOK.findall(s)]

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [toks(d) for d in docs]; self.k1, self.b = k1, b
        self.N = len(docs); self.avg = sum(len(d) for d in self.docs)/max(1, self.N)
        self.df = Counter(w for d in self.docs for w in set(d)); self.tf = [Counter(d) for d in self.docs]
    def score(self, q, i):
        s = 0.0
        for w in toks(q):
            if w not in self.tf[i]: continue
            idf = math.log(1 + (self.N - self.df[w] + 0.5)/(self.df[w] + 0.5)); f = self.tf[i][w]
            s += idf * f*(self.k1+1)/(f + self.k1*(1 - self.b + self.b*len(self.docs[i])/self.avg))
        return s
    def rank(self, q): return sorted(range(self.N), key=lambda i: -self.score(q, i))
    def top(self, q, k): return self.rank(q)[:k]

def rrf(*rankings, k=60):
    sc = defaultdict(float)
    for r in rankings:
        for pos, i in enumerate(r): sc[i] += 1.0/(k + pos + 1)
    return [i for i, _ in sorted(sc.items(), key=lambda kv: -kv[1])]

def build_retriever(a, pool):
    bm = {ci: BM25(p) for ci, p in pool.items()}
    dense = rr = None; demb = {}
    if a.dense:
        from sentence_transformers import SentenceTransformer
        dense = SentenceTransformer(a.dense)
        demb = {ci: dense.encode(pool[ci], normalize_embeddings=True, show_progress_bar=False, batch_size=64) for ci in pool}
    if a.rerank:
        from sentence_transformers import CrossEncoder
        rr = CrossEncoder(a.rerank, max_length=512)
    def retrieve(q, k):
        ci = q["ci"]; n = len(pool[ci]); cand_n = min(a.cand, n)
        if dense is None:
            cand = bm[ci].top(q["q"], cand_n if rr else k)
        else:
            import numpy as np
            qe = dense.encode([q["q"]], normalize_embeddings=True)[0]
            drank = list(np.argsort(-(demb[ci] @ qe)))
            cand = rrf(bm[ci].rank(q["q"]), drank)[:cand_n] if a.hybrid else [int(i) for i in drank[:cand_n]]
        if rr is not None:
            sc = rr.predict([(q["q"], pool[ci][i]) for i in cand])
            cand = [i for _, i in sorted(zip(sc, cand), key=lambda x: -x[0])]
        return cand[:k]
    return retrieve

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True); ap.add_argument("--terms", required=True)
    ap.add_argument("--occ", required=True); ap.add_argument("--risk", required=True)
    ap.add_argument("--arms", default="rag,rag_plus,rag_full,rag_gated,rag_defrecall")
    ap.add_argument("--topk", type=int, default=5); ap.add_argument("--cand", type=int, default=50, help="candidate count before reranking")
    ap.add_argument("--risk-th", type=float, default=0.5); ap.add_argument("--gloss-cap", type=int, default=60); ap.add_argument("--full-cap", type=int, default=30)
    ap.add_argument("--dense", default=None, help="T2: BAAI/bge-large-en-v1.5 | T1: BAAI/bge-m3")
    ap.add_argument("--rerank", default=None, help="T2: BAAI/bge-reranker-base | T1: BAAI/bge-reranker-v2-m3")
    ap.add_argument("--hybrid", action="store_true", help="T1: BM25 + dense RRF fusion followed by reranking")
    ap.add_argument("--pool-with-defs", dest="pool_with_defs", action="store_true", default=True)
    ap.add_argument("--no-pool-with-defs", dest="pool_with_defs", action="store_false", help="reproduce v2 (definition sentences not pooled)")
    ap.add_argument("--dump-prompts", default=None, help="do not call the reader: write each question's per-arm prompt components to this jsonl (for the white-box decoding baseline decode_baselines.py)")
    ap.add_argument("--n-examples", type=int, default=2, help="rag_examples arm: number of same-contract usage sentences given per term in place of the definition")
    ap.add_argument("--def-filter", action="store_true", help="gated arm skips pointer-style/tautological definitions (<8 words, or only pointing to Exhibit/Schedule/set forth/listed)")
    ap.add_argument("--tune-k", default=None, help="e.g. 3,5,8: run only the rag arm on --tune-questions to pick k, then run the main set")
    ap.add_argument("--tune-questions", default=None)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--mock", action="store_true")
    ap.add_argument("--cache-dir", default="data/cache_rag"); ap.add_argument("--out", required=True)
    a = ap.parse_args(); os.makedirs(a.cache_dir, exist_ok=True)
    cli = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    T = {json.loads(l)["id"]: json.loads(l) for l in open(a.terms, encoding="utf-8")}
    pool, gloss, is_def = defaultdict(list), defaultdict(dict), defaultdict(set)
    seen = defaultdict(set)
    for l in open(a.occ, encoding="utf-8"):
        o = json.loads(l); ci = str(o["ci"])
        if o["sent"] not in seen[ci]: seen[ci].add(o["sent"]); pool[ci].append(o["sent"])
    for i, t in T.items():
        ci = str(t["labels"]["ci"]); d = (t.get("def_raw") or "").strip()
        if not d: continue
        gloss[ci][t["term"]] = " ".join(d.split()[: a.gloss_cap])
        if a.pool_with_defs:
            ds = f'"{t["term"]}" {d}' if not d.lower().startswith(('"', t["term"].lower())) else d
            if ds not in seen[ci]: seen[ci].add(ds); is_def[ci].add(len(pool[ci])); pool[ci].append(ds)
    risk = {}
    for l in open(a.risk, encoding="utf-8"):
        r = json.loads(l)
        if r.get("per_question") and r["id"] in T:
            risk[(str(T[r["id"]]["labels"]["ci"]), T[r["id"]]["term"])] = max((1 - p["bare"]["p_correct"]) for p in r["per_question"] if "bare" in p)
    Q = [json.loads(l) for l in open(a.questions, encoding="utf-8")]
    if a.limit: Q = Q[: a.limit]
    need = {q["ci"] for q in Q}
    if a.tune_k and a.tune_questions: need |= {q["ci"] for q in map(json.loads, open(a.tune_questions, encoding="utf-8"))}
    retrieve = build_retriever(a, {ci: pool[ci] for ci in need})
    tier = "BM25" if not a.dense else ("T1-industrial(hybrid+%s+%s)" % (a.dense.split("/")[-1], (a.rerank or "").split("/")[-1]) if a.hybrid else "T2-classic(%s+%s)" % (a.dense.split("/")[-1], (a.rerank or "").split("/")[-1]))
    print(f"[rag] tier={tier} | pool_with_defs={a.pool_with_defs} | defs in pool: {sum(len(v) for v in is_def.values())}", file=sys.stderr)

    POINTER = re.compile(r"\b(set forth|listed|described|specified|identified|attached|defined) (in|on|under)\b|\b(exhibit|schedule|appendix|annex)\b|^(the )?\w+s? (offered|provided|sold|supplied|made available) by\b", re.I)
    def def_ok(t, gl_):
        if not a.def_filter: return True
        w = gl_.split()
        return len(w) >= 8 and not (POINTER.search(gl_) and len(w) < 25)
    def terms_in(ci, blob):
        b = blob.lower(); return [t for t in gloss[ci] if re.search(r"(?<![a-z])" + re.escape(t.lower()) + r"(?![a-z])", b)]
    def run(Qs, arms, k, tag):
        reqs, owners, dump_rows = [], [], []
        for q in Qs:
            ci = q["ci"]; opts = "\n".join(f"{'ABCD'[j]}. {o}" for j, o in enumerate(q["options"]))
            ranked = retrieve(q, max(k + 4, k)) if any(x.startswith("rag") for x in arms) else []
            psgs = [pool[ci][i] for i in ranked[:k]]
            present = terms_in(ci, q["q"] + " " + " ".join(psgs))
            gated = [(t, gloss[ci][t]) for t in present if risk.get((ci, t), 0) >= a.risk_th and def_ok(t, gloss[ci][t])]
            gated_tok = len(toks("\n".join(f"- {t}: {g}" for t, g in gated)))
            for arm in arms:
                gl, ps = [], psgs
                if arm == "rag_plus":           # token matching: add passages until reaching the gated arm's average extra tokens (use this question's gated tokens, or add 1 passage if zero)
                    extra = []; budget = max(gated_tok, 25)
                    for i in ranked[k:]:
                        if sum(len(toks(pool[ci][i])) for i in extra) >= budget: break
                        extra.append(i)
                    ps = psgs + [pool[ci][i] for i in extra]
                elif arm == "rag_full":
                    gl = sorted(gloss[ci].items(), key=lambda kv: -T.get(f"cuadfull:{ci}:{kv[0]}", {}).get("labels", {}).get("tf", 0))[: a.full_cap]
                elif arm == "rag_gated": gl = gated
                elif arm == "gated_only": gl = [(t, gloss[ci][t]) for t in terms_in(ci, q["q"]) if risk.get((ci, t), 0) >= a.risk_th]; ps = []
                elif arm == "rag_defrecall": gl = [(t, gloss[ci][t]) for t in present]      # ungated: all defined terms appearing in the retrieved passages
                elif arm == "rag_examples":     # in-context-learning style: gate the same set of terms, but give usage sentences instead of definitions
                    ex = []
                    for t2, _ in gated:
                        cs = [c_ for c_ in T.get(f"cuadfull:{ci}:{t2}", {}).get("contexts", []) if q["q"][:40] not in c_ and c_ not in psgs][: a.n_examples]
                        for c_ in cs: ex.append((t2, c_[:300]))
                    gl = ex
                elif arm == "none": ps = []
                ctx = ("Context passages:\n" + "\n".join("- " + p for p in ps) + "\n\n") if ps else ""
                gtxt = (("Usage examples (this contract):\n" if arm == "rag_examples" else "Definitions (this contract):\n") + "\n".join(f"- {t2}: {g}" for t2, g in gl) + "\n\n") if gl else ""
                if a.dump_prompts:
                    dump_rows.append({"qkey": q["qkey"], "term": q["term"], "ci": q["ci"], "risk": q.get("risk"), "arm": arm, "gtxt": gtxt, "ctx": ctx, "q": q["q"], "opts": opts,
                                      "answer": str(q["answer"]).strip().upper()[:1], "n_gloss": len(gl), "def_retrieved": int(any(i in is_def[ci] for i in ranked[:k])), "k": k, "tier": tier})
                reqs.append(dict(prompt=f"{gtxt}{ctx}{q['q']}\n{opts}\nANSWER_LETTER:", system=SYS, max_tokens=4, temperature=0.0))
                owners.append((q, arm, len(toks(gtxt)) + len(toks(ctx)), len(gl), any(i in is_def[ci] for i in ranked[:k]), k))
        if a.dump_prompts:
            with open(a.dump_prompts, "a", encoding="utf-8") as f:
                for r in dump_rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"[rag:{tag}] dumped {len(dump_rows)} prompts → {a.dump_prompts} (no reader calls)", file=sys.stderr); return []
        print(f"[rag:{tag}] {len(Qs)} × {len(arms)} arms = {len(reqs)} calls", file=sys.stderr)
        outs = []
        for i in range(0, len(reqs), 200):
            outs.extend(cli.complete_many(reqs[i:i + 200])); print(f"\r[rag:{tag}] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
        print(file=sys.stderr)
        rows = []
        for (q, arm, ntok, ngl, defhit, kk), o in zip(owners, outs):
            mm = re.search(r"[ABCD]", str(o).upper()); corr = int(mm.group(0) == str(q["answer"]).strip().upper()[:1]) if mm else 0
            rows.append({"qkey": q["qkey"], "term": q["term"], "ci": q["ci"], "risk": q.get("risk"), "arm": arm, "correct": corr,
                         "inject_tokens": ntok, "n_gloss": ngl, "def_retrieved": int(defhit), "k": kk, "tier": tier, "risk_th": a.risk_th, "def_filter": int(a.def_filter)})
        return rows
    m = lambda v: sum(v)/len(v) if v else float("nan")
    k = a.topk
    if a.tune_k and a.tune_questions:
        TQ = [json.loads(l) for l in open(a.tune_questions, encoding="utf-8")]; best = None
        for kk in [int(x) for x in a.tune_k.split(",")]:
            rows = run(TQ, ["rag"], kk, f"tune k={kk}"); acc = m([r["correct"] for r in rows])
            print(f"[tune] k={kk} rag acc={acc:.3f}", file=sys.stderr)
            if best is None or acc > best[1]: best = (kk, acc)
        k = best[0]; print(f"[tune] selected k={k}", file=sys.stderr)
    arms = a.arms.split(",")
    rows = run(Q, arms, k, "main")
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\ntier={tier} k={k}\n{'arm':14s} {'acc':>5s} {'acc@hi':>7s} {'acc@lo':>7s} {'acc@top-q':>9s} {'tok':>6s} {'def-retrieved':>13s}", file=sys.stderr)
    for arm in arms:
        rr_ = [r for r in rows if r["arm"] == arm]
        hi = [r["correct"] for r in rr_ if (r["risk"] or 0) >= .5]; lo = [r["correct"] for r in rr_ if (r["risk"] or 0) < .5]; tq = [r["correct"] for r in rr_ if (r["risk"] or 0) >= .75]
        print(f"{arm:14s} {m([r['correct'] for r in rr_]):5.3f} {m(hi):7.3f} {m(lo):7.3f} {m(tq):9.3f} {m([r['inject_tokens'] for r in rr_]):6.0f} {m([r['def_retrieved'] for r in rr_]):13.2f}", file=sys.stderr)

if __name__ == "__main__":
    main()