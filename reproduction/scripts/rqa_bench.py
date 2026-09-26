#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reddit natural questions × three arms (plain / note_gated / note_all). Questions and gold answers come from real user posts and top-voted replies; options rewritten by drafters.
Gating: the term's proxy-metric risk ≥ --risk-th (from lpmc_reddit.jsonl). Metric: agreement rate with top-voted reply; stratified by depends_on_sense."""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env
SYS = "You answer a multiple-choice question posted in an online community. Pick the option that matches how the community itself would answer. Answer with the letter only."
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="data/rqa/rqa_items.jsonl"); ap.add_argument("--risk", default="data/reddit/lpmc_reddit.jsonl")
    ap.add_argument("--risk-th", type=float, default=0.5); ap.add_argument("--arms", default="plain,note_gated,note_all")
    ap.add_argument("--out", required=True); ap.add_argument("--mock", action="store_true"); ap.add_argument("--cache-dir", default="data/cache_rqa")
    a = ap.parse_args(); os.makedirs(a.cache_dir, exist_ok=True)
    cli = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    risk = {}
    if os.path.exists(a.risk):
        for l in open(a.risk, encoding="utf-8"):
            r = json.loads(l); pq = [p for p in r.get("per_question", []) if "bare" in p]
            if pq: risk[r["id"]] = sum(1 - p["bare"]["p_correct"] for p in pq)/len(pq)
    I = [json.loads(l) for l in open(a.items, encoding="utf-8")]; arms = a.arms.split(","); reqs, own = [], []
    for it in I:
        opts = "\n".join(f"{'ABCD'[j]}. {o}" for j, o in enumerate(it["options"])); rk = risk.get(it["term_id"], 0.0)
        for arm in arms:
            note = ""
            if arm == "note_all" or (arm == "note_gated" and rk >= a.risk_th):
                note = f"Note — in r/{it['subreddit']}, \"{it['term']}\" means: {it['gloss_gold']}\n\n"
            reqs.append(dict(prompt=f"{note}Community: r/{it['subreddit']}\nQuestion: {it['q']}\n{opts}\nANSWER_LETTER:", system=SYS, max_tokens=4, temperature=0.0)); own.append((it, arm, rk, bool(note)))
    outs = []
    for i in range(0, len(reqs), 200): outs.extend(cli.complete_many(reqs[i:i+200])); print(f"\r[rqa] {min(i+200,len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    m = lambda v: sum(v)/len(v) if v else float("nan"); rows = []
    for (it, arm, rk, noted), o in zip(own, outs):
        mm = re.search(r"[ABCD]", str(o).upper()); pred = mm.group(0) if mm else None
        rows.append({"qid": it["qid"], "term": it["term"], "subreddit": it["subreddit"], "arm": arm, "risk": round(rk, 3), "noted": int(noted), "depends_on_sense": it["depends_on_sense"],
                     "pred": pred, "correct": int(pred == it["answer"]), "chose_everyday": int(pred == it.get("everyday_distractor"))})
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n{'arm':11s} {'acc':>5s} {'acc@depends':>11s} {'acc@indep':>9s} {'acc@hi-risk':>11s} {'everyday%':>9s} noted", file=sys.stderr)
    for arm in arms:
        rr = [r for r in rows if r["arm"] == arm]
        print(f"{arm:11s} {m([r['correct'] for r in rr]):5.3f} {m([r['correct'] for r in rr if r['depends_on_sense']]):11.3f} {m([r['correct'] for r in rr if not r['depends_on_sense']]):9.3f} "
              f"{m([r['correct'] for r in rr if r['risk']>=a.risk_th]):11.3f} {m([r['chose_everyday'] for r in rr]):9.3f} {m([r['noted'] for r in rr]):.2f}", file=sys.stderr)
if __name__ == "__main__":
    main()