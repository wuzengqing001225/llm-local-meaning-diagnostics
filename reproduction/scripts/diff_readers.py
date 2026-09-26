#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-reader diff (E8 / invariant I4): comparison of weights for the same term set across different reader models.
Output: Spearman matrix of Δ̂ per reader; channel transition table (conflict↔guess↔unknown); list of terms "conflict for A, not for B" (|Δ̂_A − Δ̂_B| ≥ --thresh).
Usage: python3 diff_readers.py --weights runs/local/deepseek/v1/weights.jsonl runs/local/gpt/v1/weights.jsonl --names deepseek gpt --out diff_v1.md
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.text import spearman
from collections import Counter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", nargs="+", required=True)
    ap.add_argument("--names", nargs="+", required=True)
    ap.add_argument("--thresh", type=float, default=0.15)
    ap.add_argument("--out", default="diff.md")
    a = ap.parse_args()
    R = {}
    for n, p in zip(a.names, a.weights):
        R[n] = {json.loads(l)["id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()}
    ids = sorted(set.intersection(*(set(v) for v in R.values())))
    mains = [i for i in ids if R[a.names[0]][i]["labels"].get("variant", "main") == "main"]
    out = [f"# Reader diff: {' vs '.join(a.names)} (common terms {len(ids)}, main terms {len(mains)})", ""]
    out += ["## Δ̂ rank correlation", "", "| | " + " | ".join(a.names) + " |", "|---|" + "---|" * len(a.names)]
    for x in a.names:
        out.append(f"| {x} | " + " | ".join(f"{spearman([R[x][i]['delta_hat'] for i in mains], [R[y][i]['delta_hat'] for i in mains]):.2f}" for y in a.names) + " |")
    out += ["", "## Channel distribution", ""]
    for x in a.names:
        out.append(f"- {x}: {dict(Counter(R[x][i].get('channel') for i in mains))}; UNKNOWN prior {sum(1 for i in mains if R[x][i].get('prior_unknown'))}")
    for x in a.names:
        for y in a.names:
            if x >= y:
                continue
            rows = []
            for i in mains:
                dx, dy = R[x][i]["delta_hat"], R[y][i]["delta_hat"]
                if dx == dx and dy == dy and abs(dx - dy) >= a.thresh:
                    rows.append((i, R[x][i]["term"], R[x][i]["labels"].get("quadrant"), dx, dy, R[x][i].get("channel"), R[y][i].get("channel"),
                                 (R[x][i].get("prior_guess") or "")[:60], (R[y][i].get("prior_guess") or "")[:60]))
            out += ["", f"## {x} vs {y}: terms with |Δ̂ diff| ≥ {a.thresh} ({len(rows)})", "",
                    f"| term | design quadrant | Δ̂_{x} | Δ̂_{y} | channel_{x} | channel_{y} | prior_{x} | prior_{y} |", "|---|---|---|---|---|---|---|---|"]
            for r in sorted(rows, key=lambda r: -abs(r[3] - r[4])):
                out.append(f"| {r[1]} | {r[2]} | {r[3]:.2f} | {r[4]:.2f} | {r[5]} | {r[6]} | {r[7]} | {r[8]} |")
    txt = "\n".join(out) + "\n"
    open(a.out, "w", encoding="utf-8").write(txt); print(txt[:3000])


if __name__ == "__main__":
    main()