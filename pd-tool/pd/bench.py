"""Evaluate a detector against the released frontier-reader labels.

A detector produces one score per occurrence (higher = more likely to be misread). Given the released labels file
(rows with "id", "ctx_idx" and "reader_failed"), this reports AUROC with a bootstrap interval and calibration by score bin.
"""
import random

def auroc(pos, neg):
    if not pos or not neg: return float("nan")
    return sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))

def evaluate(scores, labels, n_boot=500, seed=0):
    """scores: {(id, ctx_idx): float}; labels: [{"id", "ctx_idx", "reader_failed": 0/1}]"""
    pairs = [(scores[(l["id"], l["ctx_idx"])], l["reader_failed"]) for l in labels if (l["id"], l["ctx_idx"]) in scores]
    pos = [s for s, f in pairs if f]; neg = [s for s, f in pairs if not f]
    if not pos or not neg:
        raise ValueError("AUROC requires at least one matched reader error and one matched correct answer")
    a = auroc(pos, neg); rng = random.Random(seed); bs = []
    for _ in range(n_boot):
        smp = [rng.choice(pairs) for _ in pairs]
        sample_pos = [s for s, f in smp if f]
        sample_neg = [s for s, f in smp if not f]
        if sample_pos and sample_neg:
            bs.append(auroc(sample_pos, sample_neg))
    bs.sort()
    bins = []
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
        b = [f for s, f in pairs if lo <= s < hi]
        bins.append({"bin": f"[{lo:.1f},{min(hi, 1):.1f})", "n": len(b), "reader_fail": (sum(b) / len(b)) if b else None})
    ci = [bs[int(.025 * (len(bs) - 1))], bs[int(.975 * (len(bs) - 1))]] if bs else None
    return {"n": len(pairs), "n_fail": len(pos), "auroc": a, "ci95": ci, "calibration": bins}
