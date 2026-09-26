#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T1 full-corpus question generation (SCALE_DEMO_PLAN fallback route): for each term in cuad_full, up to cap occurrences, draft one MC question each.
Drafter reads from environment variables DRAFT_*  (or LLM_*) — DeepSeek recommended (different lineage from the Qwen proxy). Resumable via checkpoint (cache).
Reuses run_eqa's GEN_Q_USAGE prompt, stem-leak filter leak(), and option-level filter option_leak().
Output:
  t1_questions.jsonl  {id, term, n_q, questions: [{q, options, answer, ctx_idx}]}   —— directly consumable by run_logprob_mc.py
  t1_terms.jsonl      terms_full + gloss_gold=def_raw                               —— for run_logprob_mc --terms
Usage: python3 t1_draft.py --terms data/cuad_full/terms_full.jsonl --cap 12 --out data/cuad_full 
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_eqa import GEN_Q_USAGE, OPTION_RULE, leak, option_leak
from pdwlib.text import extract_json
from pdwlib.llm import client_from_env

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True); ap.add_argument("--cap", type=int, default=12)
    ap.add_argument("--out", default="data/cuad_full"); ap.add_argument("--mock", action="store_true")
    ap.add_argument("--cache-dir", default="data/cuad_full/cache"); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.cache_dir, exist_ok=True)
    drafter = client_from_env("DRAFT", mock=a.mock, cache_path=os.path.join(a.cache_dir, "draft.jsonl"))
    T = [json.loads(l) for l in open(a.terms, encoding="utf-8")]
    if a.limit: T = T[: a.limit]
    reqs, owners = [], []
    for t in T:
        gloss = t.get("def_raw") or t.get("gloss_gold") or ""
        for ci, sent in enumerate(t["contexts"][: a.cap]):
            pr = GEN_Q_USAGE.format(term=t["term"], gloss=gloss[:400], sentence=sent) + OPTION_RULE
            reqs.append(dict(prompt=pr, max_tokens=500, temperature=0.0))
            owners.append((t["id"], ci))
    print(f"[t1] {len(T)} terms → {len(reqs)} drafting calls", file=sys.stderr)
    outs = []
    for i in range(0, len(reqs), 200):
        outs.extend(drafter.complete_many(reqs[i:i + 200]))
        print(f"\r[t1] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    Q, n_skip, n_leak = {}, 0, 0
    TD = {t["id"]: t for t in T}
    for (tid, ci), o in zip(owners, outs):
        j = extract_json(o or "")
        t = TD[tid]
        if not j or not isinstance(j.get("options"), list) or len(j.get("options", [])) != 4 or str(j.get("answer", "")).strip().upper()[:1] not in ("A", "B", "C", "D"):
            n_skip += 1; continue
        if str(j.get("skip", "")).strip().upper().startswith(("Y", "TRUE")):
            n_skip += 1; continue
        g = t.get("def_raw") or ""
        others = [s for k, s in enumerate(t["contexts"][: a.cap]) if k != ci]
        if leak(j["q"], others) or (g and (leak(j["q"], [g], n=5) or option_leak(j, g))):
            n_leak += 1; continue
        Q.setdefault(tid, []).append({"q": j["q"], "options": [str(x) for x in j["options"]],
                                      "answer": str(j["answer"]).strip().upper()[:1], "ctx_idx": ci})
    with open(os.path.join(a.out, "t1_questions.jsonl"), "w", encoding="utf-8") as f:
        for t in T:
            qs = Q.get(t["id"], [])
            f.write(json.dumps({"id": t["id"], "term": t["term"], "n_q": len(qs), "questions": qs}, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "t1_terms.jsonl"), "w", encoding="utf-8") as f:
        for t in T:
            f.write(json.dumps({**t, "gloss_gold": t.get("def_raw")}, ensure_ascii=False) + "\n")
    print(f"[t1] questions={sum(len(v) for v in Q.values())} skipped={n_skip} leaked-and-dropped={n_leak} → {a.out}/t1_questions.jsonl", file=sys.stderr)

if __name__ == "__main__":
    main()