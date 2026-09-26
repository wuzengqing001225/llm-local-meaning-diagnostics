#!/usr/bin/env python3
"""Reconstruct the stratified 1,500-occurrence CUAD validation sample (paper Section 6, Figure t2).

Population: every scored occurrence in lpmc_full.jsonl (6,529). Risk = 1 - p_correct under the no-definition
condition. Five bins by floor(risk * 5) capped at 4, shuffled with random.Random(42), first 300 per bin.
Inclusion probability per bin (population 2529 / 1430 / 1085 / 980 / 505): 0.119 / 0.210 / 0.276 / 0.306 / 0.594.
Run from the archive root:  python3 audit/t2_sampler.py   -> prints the (id, ctx_idx) set size and whether it
matches data/cuad/raw_outputs/t2_answers.jsonl exactly."""
import json, os, random
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
def find(fn):
    for dp, _, fs in os.walk(os.path.join(ROOT, "data")):
        if fn in fs: return os.path.join(dp, fn)
    raise FileNotFoundError(fn)
def L(fn): return [json.loads(l) for l in open(find(fn), encoding="utf-8")]

rows = [dict(id=r["id"], ctx_idx=p["ctx_idx"], risk=1 - p["bare"]["p_correct"]) for r in L("lpmc_full.jsonl") for p in (r.get("per_question") or [])]
rng = random.Random(42); bins = {}
for r in rows: bins.setdefault(min(4, int(r["risk"] * 5)), []).append(r)
sample = []
for b, arr in sorted(bins.items()):
    rng.shuffle(arr); sample += arr[:300]
got = {(r["id"], str(r["ctx_idx"])) for r in sample}
shipped = {(e["id"], str(q["ctx_idx"])) for e in L("t2_answers.jsonl") for q in e["questions"]}
print("population per bin:", {b: len(a) for b, a in sorted(bins.items())})
print("inclusion probability per bin:", {b: round(300 / len(a), 3) for b, a in sorted(bins.items())})
print("regenerated:", len(got), "| shipped:", len(shipped), "| identical:", got == shipped)
if __name__ == "__main__" and "--write" in os.sys.argv:
    out = os.path.join(ROOT, "audit", "t2_sample_ids.jsonl")
    with open(out, "w") as f:
        for r in sample: f.write(json.dumps(r) + "\n")
    print("wrote", out)
