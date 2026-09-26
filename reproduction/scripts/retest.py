#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E18 ground-truth retest reliability: eqa.jsonl produced by --from-usage (containing deficit_qa_A/B, resid_qa_A/B) or run_logprob_mc output (per_question with half).
Outputs Spearman and n for term-level failure rate across the two halves."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.text import spearman

ap = argparse.ArgumentParser()
ap.add_argument("--eqa", help="run_eqa --from-usage output")
ap.add_argument("--lpmc", help="run_logprob_mc output (question-level p_correct, requires half field)")
ap.add_argument("--min-q", type=int, default=3, help="minimum questions per half")
a = ap.parse_args()
if a.eqa:
    R = [json.loads(l) for l in open(a.eqa, encoding="utf-8")]
    ok = [r for r in R if (r.get("n_q_A") or 0) >= a.min_q and (r.get("n_q_B") or 0) >= a.min_q]
    print(f"[E18 reader] n={len(ok)} terms with >= {a.min_q} q per half")
    print(f"  bare deficit  A vs B: Spearman={spearman([r['deficit_qa_A'] for r in ok], [r['deficit_qa_B'] for r in ok]):.3f}")
    okm = [r for r in ok if r.get("resid_qa_A") is not None and r.get("resid_qa_B") is not None]
    if okm:
        print(f"  residual after own prior A vs B: Spearman={spearman([r['resid_qa_A'] for r in okm], [r['resid_qa_B'] for r in okm]):.3f} (n={len(okm)})")
if a.lpmc:
    R = [json.loads(l) for l in open(a.lpmc, encoding="utf-8")]
    def pc(q, cond="bare"):
        return q[cond]["p_correct"] if isinstance(q.get(cond), dict) else q.get(f"p_correct_{cond}")
    xs, ys, xm, ym = [], [], [], []
    for r in R:
        A = [q for q in r.get("per_question", []) if q.get("half") == "A" and pc(q) is not None]
        B = [q for q in r.get("per_question", []) if q.get("half") == "B" and pc(q) is not None]
        if len(A) >= a.min_q and len(B) >= a.min_q:
            xs.append(1 - sum(pc(q) for q in A) / len(A)); ys.append(1 - sum(pc(q) for q in B) / len(B))
            AM = [pc(q, "glossM") for q in A if pc(q, "glossM") is not None]; BM = [pc(q, "glossM") for q in B if pc(q, "glossM") is not None]
            if AM and BM:
                xm.append(1 - sum(AM) / len(AM)); ym.append(1 - sum(BM) / len(BM))
    print(f"[E18 proxy] n={len(xs)}  1-P(correct) bare  A vs B: Spearman={spearman(xs, ys):.3f}")
    if xm:
        print(f"             n={len(xm)}  1-P(correct) after own prior (glossM) A vs B: Spearman={spearman(xm, ym):.3f}")