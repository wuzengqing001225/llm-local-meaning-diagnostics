#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External benchmark check (Q-9 correction route): use CUAD's own human-written clause questions + human-annotated answer spans to validate the risk map and risk-gated injection.
Questions were not drafted by us, ground truth is not given by an LLM, scoring is SQuAD-style token-F1/EM (zero judge).

Three arms (same reader, same retrieval, injection differs only):
  rag        BM25 retrieves top-k passages within this contract
  rag_full   + all defined terms of this contract (<= --full-cap entries, by tf)
  rag_gated  + only definitions of terms that appear in retrieved passages/question and whose proxy risk >= --risk-th
(No "none" arm: span extraction without contract text is meaningless; a full contract ~14k tokens x 2k questions is too costly, so no full-context arm is set; see README.)

Pre-registration (README_CUADBENCH.md):
  H1 rag_gated F1 >= rag, with gains concentrated on term_bearing=True questions (gold span contains a term defined in this contract); no gain on the term_free stratum.
  H2 the F1 loss of the rag arm can be predicted by the proxy risk of question-relevant terms (risk_gold_span / risk_retrieved).
Output per line: {qid, ci, category, term_bearing, risk_gold_span, risk_retrieved, arm, f1, em, pred, inject_tokens, n_gloss}
"""
import argparse, json, math, os, random, re, string, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env
from rag_harness import BM25, toks

SYS = ("You are extracting clauses from a contract. Using ONLY the provided passages, quote verbatim the text that answers "
       "the question. If several passages apply, quote the most relevant one. If nothing in the passages answers it, reply exactly: None.")
META = {"Document Name", "Parties", "Agreement Date", "Effective Date", "Expiration Date", "Governing Law"}  # metadata category, excluded a priori

def norm(s):
    s = s.lower(); s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())

def f1_em(pred, golds):
    p = norm(pred).split(); best_f1 = 0.0; best_em = 0
    if norm(pred) in ("none", "") and not golds: return 1.0, 1
    for g in golds:
        gt = norm(g).split(); common = Counter(p) & Counter(gt); ns = sum(common.values())
        if ns == 0: f = 0.0
        else:
            pr, rc = ns/len(p), ns/len(gt); f = 2*pr*rc/(pr+rc)
        best_f1 = max(best_f1, f); best_em = max(best_em, int(norm(pred) == norm(g)))
    return best_f1, best_em

def chunks(text, n_words=90, stride=60):
    w = text.split(); out = []
    for i in range(0, max(1, len(w) - n_words + stride), stride):
        out.append(" ".join(w[i:i + n_words]))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cuad", default="data/raw/CUADv1.json"); ap.add_argument("--terms", default="data/cuad_full/terms_full.jsonl")
    ap.add_argument("--risk", default="data/cuad_full/lpmc_full.jsonl"); ap.add_argument("--out", required=True)
    ap.add_argument("--per-contract", type=int, default=10, help="max questions per contract (term_bearing / term_free split evenly)")
    ap.add_argument("--topk", type=int, default=8); ap.add_argument("--risk-th", type=float, default=0.5)
    ap.add_argument("--full-cap", type=int, default=30); ap.add_argument("--arms", default="rag,rag_full,rag_gated")
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--cache-dir", default="data/cache_cuadbench")
    a = ap.parse_args()
    os.makedirs(a.cache_dir, exist_ok=True); rng = random.Random(a.seed)
    cli = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))

    # terms and risk (contract name -> {term: (gloss, risk)})
    T = [json.loads(l) for l in open(a.terms, encoding="utf-8")]
    LP = {json.loads(l)["id"]: json.loads(l) for l in open(a.risk, encoding="utf-8")} if os.path.exists(a.risk) else {}
    gloss, risk = defaultdict(dict), defaultdict(dict)
    for t in T:
        lp = LP.get(t["id"], {}).get("per_question") or []
        r = sum(1 - p["bare"]["p_correct"] for p in lp if "bare" in p)/len(lp) if lp else None
        g = t.get("gloss_gold") or t.get("def_raw")
        if g: gloss[t["contract"]][t["term"]] = g; risk[t["contract"]][t["term"]] = r
    D = json.load(open(a.cuad, encoding="utf-8"))
    contracts = [c for c in D["data"] if c["title"] in gloss]
    print(f"[bench] contracts with risk map: {len(contracts)}", file=sys.stderr)

    def terms_in(text, ci):
        blob = text.lower()
        return [t for t in gloss[ci] if re.search(r"(?<![a-z])" + re.escape(t.lower()) + r"(?![a-z])", blob)]
    def max_risk(ts, ci):
        vals = [risk[ci][t] for t in ts if risk[ci].get(t) is not None]
        return max(vals) if vals else None

    # sample questions: answerable, non-metadata; per contract, term_bearing / term_free each <= per_contract/2
    Q = []
    for c in contracts:
        ci = c["title"]; ctx = c["paragraphs"][0]["context"]
        tb, tf_ = [], []
        for qa in c["paragraphs"][0]["qas"]:
            if qa.get("is_impossible") or not qa["answers"]: continue
            m = re.search(r'related to "([^"]+)"', qa["question"]); cat = m.group(1) if m else "?"
            if cat in META: continue
            golds = [x["text"] for x in qa["answers"]]
            gts = sorted({t for g in golds for t in terms_in(g, ci)})
            row = dict(qid=qa["id"], ci=ci, category=cat, question=qa["question"], golds=golds,
                       term_bearing=bool(gts), gold_terms=gts, risk_gold_span=max_risk(gts, ci))
            (tb if gts else tf_).append(row)
        rng.shuffle(tb); rng.shuffle(tf_); half = a.per_contract // 2
        Q += tb[:half] + tf_[:half]
    rng.shuffle(Q)
    if a.limit: Q = Q[:a.limit]
    print(f"[bench] questions: {len(Q)} | term_bearing {sum(q['term_bearing'] for q in Q)} | categories {len({q['category'] for q in Q})}", file=sys.stderr)

    pool = {c["title"]: chunks(c["paragraphs"][0]["context"]) for c in contracts if c["title"] in {q["ci"] for q in Q}}
    bm = {ci: BM25(p) for ci, p in pool.items()}
    arms = a.arms.split(","); reqs, owners = [], []
    for q in Q:
        ci = q["ci"]; qtext = q["question"].split("Details:")[-1].strip() if "Details:" in q["question"] else q["question"]
        psgs = [pool[ci][i] for i in bm[ci].top(qtext + " " + q["category"], a.topk)]
        rt = terms_in(" ".join(psgs) + " " + qtext, ci); q["risk_retrieved"] = max_risk(rt, ci)
        for arm in arms:
            gl = []
            if arm == "rag_full":
                gl = sorted(gloss[ci].items(), key=lambda kv: -len(kv[1]))[: a.full_cap]
            elif arm == "rag_gated":
                gl = [(t, gloss[ci][t]) for t in rt if (risk[ci].get(t) or 0) >= a.risk_th]
            gtxt = ("Definitions (this contract):\n" + "\n".join(f"- {t2}: {g[:400]}" for t2, g in gl) + "\n\n") if gl else ""
            ctx = "Contract passages:\n" + "\n".join(f"[{k+1}] {p}" for k, p in enumerate(psgs)) + "\n\n"
            prompt = f"{gtxt}{ctx}Question: {q['question']}\nAnswer (verbatim quote or None):"
            reqs.append(dict(prompt=prompt, system=SYS, max_tokens=300, temperature=0.0))
            owners.append((q, arm, len(toks(gtxt)), len(gl)))
    print(f"[bench] {len(Q)} × {len(arms)} arms = {len(reqs)} calls", file=sys.stderr)
    outs = []
    for i in range(0, len(reqs), 200):
        outs.extend(cli.complete_many(reqs[i:i + 200])); print(f"\r[bench] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    agg = defaultdict(list)
    with open(a.out, "w", encoding="utf-8") as f:
        for (q, arm, ntok, ngl), o in zip(owners, outs):
            pred = str(o or "").strip().strip('"')
            f1, em = f1_em(pred, q["golds"])
            agg[arm].append((f1, q["term_bearing"], q.get("risk_gold_span")))
            f.write(json.dumps({"qid": q["qid"], "ci": q["ci"], "category": q["category"], "term_bearing": q["term_bearing"],
                                "gold_terms": q["gold_terms"], "risk_gold_span": q.get("risk_gold_span"), "risk_retrieved": q.get("risk_retrieved"),
                                "arm": arm, "f1": round(f1, 4), "em": em, "pred": pred[:400], "inject_tokens": ntok, "n_gloss": ngl}, ensure_ascii=False) + "\n")
    m = lambda v: sum(v)/len(v) if v else float("nan")
    print(f"\n{'arm':10s} {'F1':>6s} {'F1@term':>8s} {'F1@free':>8s} {'F1@hi-risk':>10s} {'inject-tok':>10s}", file=sys.stderr)
    for arm in arms:
        rows = agg[arm]; ntk = [ntok for (q_, ar, ntok, _) in owners if ar == arm]
        print(f"{arm:10s} {m([r[0] for r in rows]):6.3f} {m([r[0] for r in rows if r[1]]):8.3f} {m([r[0] for r in rows if not r[1]]):8.3f} "
              f"{m([r[0] for r in rows if (r[2] or 0) >= a.risk_th]):10.3f} {m(ntk):10.0f}", file=sys.stderr)

if __name__ == "__main__":
    main()