#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reddit RAG comparison (test of whether PD can be replaced by engineering heuristics): the corpus **has no definition clauses**; the glossary is written by community members, 5-31 entries per subreddit.
Retrieval pool = that subreddit's comment sentence pool; questions = reddit_eqa gold-anchored items (218 glossary-term items + 175 control-term items).
Arms: none / rag / rag_plus (token-balanced) / rag_full (full glossary gloss for that subreddit) / rag_gated (glossary terms appearing in question+retrieved passages with term-level proxy risk >= th)
    (no rag_defrecall: the corpus has no recallable definitions -- this is precisely the difference from CUAD)
Stratification: glossary-term items vs control-term items (control items = spillover/over-caution guard); binned by proxy item-level risk.
Pre-registration: H1 rag_gated >= rag, with gains concentrated in high-risk glossary-term items; H2 rag_full ~= rag_gated accuracy but entry count grows with glossary size (31 vs ~3); H3 no difference across the three arms on control items (no spillover).
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_harness import BM25, rrf, toks, build_retriever
from pdwlib.llm import client_from_env
SYS = "You answer multiple-choice questions about posts from an online community. Use the provided context if any. Answer with the letter only."
def sents(text): return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if 6 <= len(s.split()) <= 80]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", default="data/reddit/terms.jsonl"); ap.add_argument("--corpus", default="data/reddit/corpus.jsonl")
    ap.add_argument("--eqa", default="data/reddit/eqa.jsonl"); ap.add_argument("--risk", default="data/reddit/lpmc_reddit.jsonl")
    ap.add_argument("--full-glossary", default="data/reddit/glossaries.csv", help="rag_full arm uses the full community glossary (Lucy & Bamman's original table, tens to hundreds of entries per subreddit); pass an empty string to use only the 218-term filtered table")
    ap.add_argument("--arms", default="none,rag,rag_plus,rag_full,rag_gated"); ap.add_argument("--topk", type=int, default=6); ap.add_argument("--cand", type=int, default=50)
    ap.add_argument("--risk-th", type=float, default=0.5); ap.add_argument("--dense", default=None); ap.add_argument("--rerank", default=None); ap.add_argument("--hybrid", action="store_true")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--mock", action="store_true"); ap.add_argument("--cache-dir", default="data/cache_rag_reddit"); ap.add_argument("--out", required=True)
    a = ap.parse_args(); os.makedirs(a.cache_dir, exist_ok=True)
    cli = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    T = {json.loads(l)["id"]: json.loads(l) for l in open(a.terms, encoding="utf-8")}
    pool = {json.loads(l)["doc_id"][2:]: sents(json.loads(l)["text"]) for l in open(a.corpus, encoding="utf-8")}
    gloss = {}
    for t in T.values():
        if t["labels"]["quadrant"] == "glossary" and t.get("gloss_gold"): gloss.setdefault(t["labels"]["subreddit"], {})[t["term"]] = t["gloss_gold"]
    fullg = {}
    if a.full_glossary and os.path.exists(a.full_glossary):
        import csv
        for r in csv.DictReader(open(a.full_glossary, encoding="utf-8")):
            if r.get("term") and r.get("description"): fullg.setdefault(r["subreddit"], {})[r["term"].strip()] = r["description"].strip()
    LP = {json.loads(l)["id"]: json.loads(l) for l in open(a.risk, encoding="utf-8")}
    trisk = {}
    for i, r in LP.items():
        pq = [p for p in r.get("per_question", []) if "bare" in p]
        if pq: trisk[i] = sum(1 - p["bare"]["p_correct"] for p in pq) / len(pq)
    Qs = []
    for l in open(a.eqa, encoding="utf-8"):
        e = json.loads(l); t = T.get(e["id"])
        if not t or e["n_q"] == 0: continue
        pq = LP.get(e["id"], {}).get("per_question", [])
        for j, q in enumerate(e["questions"]):
            rk = (1 - pq[j]["bare"]["p_correct"]) if j < len(pq) and "bare" in pq[j] else None
            Qs.append(dict(qkey=f"{e['id']}#{j}", term=t["term"], ci=t["labels"]["subreddit"], quadrant=t["labels"]["quadrant"], q=q["q"], options=q["options"], answer=q["answer"], risk=rk, trisk=trisk.get(e["id"])))
    if a.limit: Qs = Qs[: a.limit]
    a.cand = a.cand; retrieve = build_retriever(a, pool)
    tier = "BM25" if not a.dense else f"{'hybrid+' if a.hybrid else ''}{a.dense.split('/')[-1]}{'+' + a.rerank.split('/')[-1] if a.rerank else ''}"
    arms = a.arms.split(","); reqs, own = [], []
    def present_terms(ci, blob):
        low = blob.lower(); return [t for t in gloss.get(ci, {}) if re.search(r"(?<![a-z])" + re.escape(t.lower()) + r"(?![a-z])", low)]
    tid = {(t["labels"]["subreddit"], t["term"]): i for i, t in T.items()}
    for q in Qs:
        ci = q["ci"]; opts = "\n".join(f"{'ABCD'[j]}. {o}" for j, o in enumerate(q["options"]))
        ranked = retrieve(q, a.topk + 6) if any(x.startswith("rag") for x in arms) else []
        psgs = [pool[ci][i] for i in ranked[: a.topk]]
        present = present_terms(ci, q["q"] + " " + " ".join(psgs))
        gated = [(t, gloss[ci][t]) for t in present if trisk.get(tid.get((ci, t)), 0) >= a.risk_th]
        gated_tok = len(toks("\n".join(f"- {t}: {g}" for t, g in gated)))
        for arm in arms:
            gl, ps = [], psgs
            if arm == "none": ps = []
            elif arm == "rag_plus":
                extra = []; budget = max(gated_tok, 20)
                for i in ranked[a.topk:]:
                    if sum(len(toks(pool[ci][i])) for i in extra) >= budget: break
                    extra.append(i)
                ps = psgs + [pool[ci][i] for i in extra]
            elif arm == "rag_full": gl = list((fullg.get(ci) or gloss.get(ci, {})).items())
            elif arm == "rag_gated": gl = gated
            ctx = ("Context (posts from r/" + ci + "):\n" + "\n".join("- " + p for p in ps) + "\n\n") if ps else ""
            gtxt = ("Community glossary (r/" + ci + "):\n" + "\n".join(f"- {t2}: {g}" for t2, g in gl) + "\n\n") if gl else ""
            reqs.append(dict(prompt=f"{gtxt}{ctx}{q['q']}\n{opts}\nANSWER_LETTER:", system=SYS, max_tokens=4, temperature=0.0))
            own.append((q, arm, len(toks(gtxt)) + len(toks(ctx)), len(gl), any(q["term"].lower() in p.lower() for p in psgs)))
    print(f"[rag-reddit] tier={tier} k={a.topk} | {len(Qs)} questions × {len(arms)} arms = {len(reqs)} calls | glossary entries/sub median {sorted(len(v) for v in gloss.values())[len(gloss)//2]} | full-glossary entries/sub median {(sorted(len(fullg.get(ci, gloss[ci])) for ci in gloss)[len(gloss)//2])}", file=sys.stderr)
    outs = []
    for i in range(0, len(reqs), 200):
        outs.extend(cli.complete_many(reqs[i:i + 200])); print(f"\r[rag-reddit] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    rows = []
    for (q, arm, ntok, ngl, hit), o in zip(own, outs):
        mm = re.search(r"[ABCD]", str(o).upper()); corr = int(mm.group(0) == str(q["answer"]).strip().upper()[:1]) if mm else 0
        rows.append({"qkey": q["qkey"], "term": q["term"], "ci": q["ci"], "quadrant": q["quadrant"], "risk": q["risk"], "trisk": q["trisk"], "arm": arm, "correct": corr,
                     "inject_tokens": ntok, "n_gloss": ngl, "term_in_passages": int(hit), "k": a.topk, "tier": tier, "risk_th": a.risk_th})
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    m = lambda v: sum(v)/len(v) if v else float("nan")
    print(f"\n{'arm':10s} {'acc(gloss)':>10s} {'hi-risk':>8s} {'acc(ctrl)':>9s} {'tok':>5s} {'entries':>7s}", file=sys.stderr)
    for arm in arms:
        rr = [r for r in rows if r["arm"] == arm]; g = [r for r in rr if r["quadrant"] == "glossary"]; c = [r for r in rr if r["quadrant"] == "control"]
        print(f"{arm:10s} {m([r['correct'] for r in g]):10.3f} {m([r['correct'] for r in g if (r['risk'] or 0) >= .5]):8.3f} {m([r['correct'] for r in c]):9.3f} {m([r['inject_tokens'] for r in rr]):5.0f} {m([r['n_gloss'] for r in g]):7.1f}", file=sys.stderr)
    print(f"[done] {len(rows)} rows → {a.out}", file=sys.stderr)
if __name__ == "__main__":
    main()