#!/usr/bin/env python3
"""Term frequency and rarity as error-ranking baselines (paper Table 2, column Freq.). Offline, released data only.

Usage (from the package root):
  python3 analysis/reviewer_controls/frequency_baseline.py --root . --out analysis/reviewer_controls/frequency_baseline_results.json

For each reader setting, every question with a bare outcome is scored by its term's corpus frequency (labels.tf).
AUROC is reported for frequency and for rarity (negated frequency), together with the proxy risk R = 1 - p_bare(key)
on the same questions. Table 2 prints the larger of the frequency and rarity AUROCs.
"""
import argparse, json, os

EXCL_SYNTH = {("v1:desk:interest", 1)}


def auroc(pos, neg):
    s = 0.0
    for a in pos:
        for b in neg:
            s += 1.0 if a > b else 0.5 if a == b else 0.0
    return s / (len(pos) * len(neg))


def index(root):
    idx = {}
    for dp, _, fs in sorted(os.walk(os.path.join(root, "data"))):
        for f in fs:
            p = os.path.join(dp, f)
            if f not in idx or ("raw_outputs" in p and "raw_outputs" not in idx[f]): idx[f] = p
    return idx


SETTINGS = [("Synthetic", "DeepSeek V4 Flash", "lpmc_v1.jsonl", "v1_eqa.jsonl", "v1_weights.jsonl"),
            ("Synthetic", "GPT-6-astra", "lpmc_v1.jsonl", "astra6_v1_eqa.jsonl", "v1_weights.jsonl"),
            ("Reddit", "DeepSeek V4.1 Flash", "lpmc_reddit.jsonl", "reddit_eqa.jsonl", "reddit_weights.jsonl"),
            ("Reddit", "GPT-6-astra", "lpmc_reddit.jsonl", "astra6_reddit_eqa.jsonl", "reddit_weights.jsonl"),
            ("DeFi", "DeepSeek V4.1 Flash", "defi_strict_lpmc.jsonl", "defi_strict_eqa.jsonl", "defi_strict_weights.jsonl"),
            ("DeFi", "GPT-5.6-terra", "defi_strict_lpmc.jsonl", "defi_strict_eqa_gpt.jsonl", "defi_strict_weights.jsonl"),
            ("DeFi", "GPT-6-astra", "defi_strict_lpmc.jsonl", "astra6_defi_strict_eqa.jsonl", "defi_strict_weights.jsonl")]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="."); ap.add_argument("--out", required=True); a = ap.parse_args()
    idx = index(a.root)
    rows = lambda f: [json.loads(l) for l in open(idx[f], encoding="utf-8")]
    byid = lambda f: {r["id"]: r for r in rows(f)}
    out = []
    for corp, reader, lp, eq, wf in SETTINGS:
        tf = {i: (w.get("labels") or {}).get("tf") for i, w in byid(wf).items()}
        LP, E = byid(lp), byid(eq); pts = []
        for i, r in LP.items():
            e = E.get(i)
            if not e or tf.get(i) is None: continue
            for j, p in enumerate(r.get("per_question") or []):
                if j >= len(e["questions"]) or (i, j) in EXCL_SYNTH or "bare" not in p: continue
                c = (e["questions"][j].get("correct") or {}).get("bare")
                if c is None: continue
                pts.append((tf[i], 1 - p["bare"]["p_correct"], 1 - c))
        f_ = auroc([t for t, _, y in pts if y], [t for t, _, y in pts if not y])
        R_ = auroc([x for _, x, y in pts if y], [x for _, x, y in pts if not y])
        out.append(dict(corpus=corp, reader=reader, n=len(pts), frequency_auroc=f_, rarity_auroc=1 - f_, better_of_two=max(f_, 1 - f_), R_auroc=R_))
    tf = {r["id"]: (r.get("labels") or {}).get("tf") for r in rows("terms_full.jsonl")}
    prox = {(r["id"], str(p["ctx_idx"])): 1 - p["bare"]["p_correct"] for r in rows("lpmc_full.jsonl") for p in (r.get("per_question") or []) if "bare" in p}
    pts = []
    for e in rows("t2_answers.jsonl"):
        for q in e["questions"]:
            c = (q.get("correct") or {}).get("bare"); k = (e["id"], str(q["ctx_idx"]))
            if c is None or k not in prox or tf.get(e["id"]) is None: continue
            pts.append((tf[e["id"]], prox[k], 1 - c))
    f_ = auroc([t for t, _, y in pts if y], [t for t, _, y in pts if not y]); R_ = auroc([x for _, x, y in pts if y], [x for _, x, y in pts if not y])
    out.append(dict(corpus="CUAD", reader="GPT-5.6-terra", n=len(pts), frequency_auroc=f_, rarity_auroc=1 - f_, better_of_two=max(f_, 1 - f_), R_auroc=R_, note="unweighted over the stratified sample"))
    json.dump(out, open(a.out, "w"), indent=1)
    for r in out: print(f"{r['corpus']:9s} {r['reader']:20s} n={r['n']:5d} freq/rarity best {r['better_of_two']:.3f}  R {r['R_auroc']:.3f}")


if __name__ == "__main__":
    main()
