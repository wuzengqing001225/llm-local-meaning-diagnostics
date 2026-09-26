#!/usr/bin/env python3
"""Deletion sensitivity for the 27-item human source review. Offline; reads released data only.

Usage (from the package root):
  python3 analysis/reviewer_controls/review27_deletion_check.py --root . \
      --out analysis/reviewer_controls/review27_deletion_results.json

Items are matched to question records by corpus and exact question text
(data/historical_question_audit/blind_80/selected_questions.jsonl). Two scenarios remove the
14 items judged invalid or source-insufficient, and those 14 plus the 3 borderline items.
Reported per setting: error-ranking AUROC of R = 1 - p_bare(key) with and without the items,
and for CUAD also the design-weighted AUROC over the five risk bins of the 6,529-question frame.
No stored key is changed.
"""
import argparse, csv, json, os, re
from collections import defaultdict

EXCL_SYNTH = {("v1:desk:interest", 1)}
POP = {0: 2529, 1: 1430, 2: 1085, 3: 980, 4: 505}


def auroc(pos, neg, wpos=None, wneg=None):
    wpos = wpos or [1.0] * len(pos); wneg = wneg or [1.0] * len(neg)
    num = den = 0.0
    for a, wa in zip(pos, wpos):
        for b, wb in zip(neg, wneg):
            w = wa * wb; den += w; num += w * (1.0 if a > b else 0.5 if a == b else 0.0)
    return num / den


class Data:
    def __init__(self, root):
        self.idx = {}
        for dp, _, fs in sorted(os.walk(os.path.join(root, "data"))):
            for f in fs:
                p = os.path.join(dp, f)
                if f not in self.idx or ("raw_outputs" in p and "raw_outputs" not in self.idx[f]): self.idx[f] = p

    def rows(self, f):
        return [json.loads(l) for l in open(self.idx[f], encoding="utf-8")]

    def by_id(self, f):
        return {r["id"]: r for r in self.rows(f)}


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip().lower()


SETTINGS = [("Synthetic / DeepSeek V4 Flash", "synthetic", "lpmc_v1.jsonl", "v1_eqa.jsonl"),
            ("Synthetic / GPT-6-astra", "synthetic", "lpmc_v1.jsonl", "astra6_v1_eqa.jsonl"),
            ("Reddit / DeepSeek V4.1 Flash", "reddit", "lpmc_reddit.jsonl", "reddit_eqa.jsonl"),
            ("Reddit / GPT-6-astra", "reddit", "lpmc_reddit.jsonl", "astra6_reddit_eqa.jsonl"),
            ("DeFi / DeepSeek V4.1 Flash", "defi", "defi_strict_lpmc.jsonl", "defi_strict_eqa.jsonl"),
            ("DeFi / GPT-5.6-terra", "defi", "defi_strict_lpmc.jsonl", "defi_strict_eqa_gpt.jsonl"),
            ("DeFi / GPT-6-astra", "defi", "defi_strict_lpmc.jsonl", "astra6_defi_strict_eqa.jsonl")]
EQA = {"synthetic": "v1_eqa.jsonl", "reddit": "reddit_eqa.jsonl", "defi": "defi_strict_eqa.jsonl", "cuad": "t2_answers.jsonl"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="."); ap.add_argument("--out", required=True); a = ap.parse_args()
    D = Data(a.root)
    base = os.path.join(a.root, "data", "historical_question_audit")
    sel = [json.loads(l) for l in open(os.path.join(base, "blind_80", "selected_questions.jsonl"), encoding="utf-8")]
    rec = list(csv.DictReader(open(os.path.join(base, "review_27", "source_reconciliation_27_en.csv"), encoding="utf-8")))
    status = {r["audit_id"]: r["posthoc_source_status"] for r in rec}
    qmap = {}
    for corp, f in EQA.items():
        for e in D.rows(f):
            for j, q in enumerate(e["questions"]):
                qmap[(corp, norm(q["q"]))] = (e["id"], j, str(q.get("ctx_idx")))
    loc = {x["audit_id"]: (x["corpus"], qmap[(x["corpus"], norm(x["question"]))]) for x in sel}
    scen = {"invalid_14": {k for k, v in status.items() if v == "invalid_or_insufficient"}}
    scen["invalid_plus_borderline_17"] = scen["invalid_14"] | {k for k, v in status.items() if v == "borderline"}
    res = dict(review_counts={}, settings=[], cuad=None, matched_items=len(loc))
    for corp in ("synthetic", "cuad", "reddit", "defi"):
        c = defaultdict(int)
        for r in rec:
            if r["corpus"] == corp: c[r["posthoc_source_status"]] += 1
        res["review_counts"][corp] = dict(c)

    def r_auc(lp, eq, drop):
        LP, E = D.by_id(lp), D.by_id(eq); pos, neg = [], []
        for i, r in LP.items():
            e = E.get(i)
            if not e: continue
            for j, p in enumerate(r.get("per_question") or []):
                if j >= len(e["questions"]) or (i, j) in EXCL_SYNTH or (i, j) in drop or "bare" not in p: continue
                c = (e["questions"][j].get("correct") or {}).get("bare")
                if c is None: continue
                (pos if c == 0 else neg).append(1 - p["bare"]["p_correct"])
        return auroc(pos, neg), len(pos) + len(neg)

    for name, corp, lp, eq in SETTINGS:
        row = dict(setting=name)
        row["original"], row["n"] = r_auc(lp, eq, set())
        for sn, ids in scen.items():
            drop = {loc[x][1][:2] for x in ids if loc[x][0] == corp}
            row[sn], row[f"n_{sn}"] = r_auc(lp, eq, drop)
        res["settings"].append(row)
    prox = {(r["id"], str(p["ctx_idx"])): 1 - p["bare"]["p_correct"] for r in D.rows("lpmc_full.jsonl") for p in (r.get("per_question") or []) if "bare" in p}

    def cuad(drop):
        pos, neg, wp, wn = [], [], [], []
        for e in D.rows("t2_answers.jsonl"):
            for q in e["questions"]:
                c = (q.get("correct") or {}).get("bare"); k = (e["id"], str(q["ctx_idx"]))
                if c is None or k not in prox or k in drop: continue
                w = POP[min(4, int(prox[k] * 5))] / 300
                if c == 0: pos.append(prox[k]); wp.append(w)
                else: neg.append(prox[k]); wn.append(w)
        return dict(unweighted=auroc(pos, neg), design_weighted=auroc(pos, neg, wp, wn), n=len(pos) + len(neg))
    res["cuad"] = {"original": cuad(set())}
    for sn, ids in scen.items():
        res["cuad"][sn] = cuad({(loc[x][1][0], loc[x][1][2]) for x in ids if loc[x][0] == "cuad"})
    res["max_abs_change_R_auroc"] = {sn: max([abs(r[sn] - r["original"]) for r in res["settings"]] + [abs(res["cuad"][sn]["unweighted"] - res["cuad"]["original"]["unweighted"])]) for sn in scen}
    json.dump(res, open(a.out, "w"), indent=1); print("wrote", a.out)


if __name__ == "__main__":
    main()
