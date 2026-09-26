#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scorecard evaluation v0.2 (ERROR_STANDARD v0.2).

Input: weights.jsonl (run_pdw), failures.jsonl (run_downstream mc/definition), distractor failures, judge_pairs,
      synth_corpus.jsonl (E14 candidate recall).
Output: scorecard.md. Each AUROC comes with a bootstrap 95% CI; slices with n<15 are reported only, not judged ("underpowered").
Ablation A: main score taken as E2, P, U of delta_hat / gain_bare_hat / deficit / rarity respectively.
"""
import argparse
import json
import os
import random
import re
from collections import defaultdict

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from pdwlib.text import (auroc, auroc_ci, spearman, spearman_perm_p, mean, partial_spearman, tokens)

TIER_ORD = {"none": 0, "narrower": 1, "shifted": 2, "opposite": 3, "unknown": 2}
MIN_N = 15
EXTRA_KEYS = ("self_report", "self_extract", "emb_shift", "emb_apd", "delta_qa", "deficit_qa", "gain_qa", "delta_lp", "deficit_lp", "gain_lp",
              "delta_qa_gold", "delta_qa_perturbed", "delta_qa_alt")
ABL_SCORES = ("delta_hat", "delta_hat_cloze", "gain_bare_hat", "deficit", "rarity") + EXTRA_KEYS


def load_jsonl(paths):
    out = []
    for p in paths or []:
        if p and os.path.exists(p):
            out += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return out


def ok(v):
    return v is not None and v == v


def fmt(v, nd=3):
    return f"{v:.{nd}f}" if ok(v) else "n/a"


def ci_txt(pos, neg):
    lo, hi = auroc_ci(pos, neg)
    return f"[{fmt(lo,2)},{fmt(hi,2)}]" if ok(lo) else ""


def budget_curve(ts, order_key, fails, wkey=None):
    """Independence approximation: acc(B) = Σ_t w_t·[gloss_acc if t∈topB else bare_acc] / Σ w_t. Returns normalized area under curve."""
    ts = [t for t in ts if t["id"] in fails and ok(fails[t["id"]].get("bare")) and ok(fails[t["id"]].get("gloss"))]
    if len(ts) < 3:
        return float("nan"), []
    w = {t["id"]: (t["labels"].get(wkey) or 1) if wkey else 1 for t in ts}
    tot = sum(w.values())
    ts_sorted = sorted(ts, key=order_key)
    curve = []
    for B in range(len(ts) + 1):
        top = {t["id"] for t in ts_sorted[:B]}
        curve.append(sum(w[t["id"]] * (fails[t["id"]]["gloss"] if t["id"] in top else fails[t["id"]]["bare"]) for t in ts) / tot)
    return mean(curve), curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", nargs="+", required=True)
    ap.add_argument("--failures", nargs="*")
    ap.add_argument("--distractor-failures")
    ap.add_argument("--judge-pairs")
    ap.add_argument("--corpus", help="synth_corpus.jsonl (E14)")
    ap.add_argument("--tf-min", type=int, default=5)
    ap.add_argument("--score", default="delta_hat", choices=["delta_hat", "gain_bare_hat", "deficit", "rarity", "weight"])
    ap.add_argument("--out", default="scorecard.md")
    ap.add_argument("--main-score", choices=["delta_hat", "delta_qa"], default="delta_hat",
                    help="v0.5: main score. For delta_qa, E6/E7/E6b use delta_qa_perturbed / delta_qa_alt / delta_qa_gold (requires run_eqa --robust)")
    ap.add_argument("--extra-scores", nargs="*", default=[], help="v0.4: baseline/other estimator score files (jsonl, merged into weight rows by id): self_report, self_extract, emb_shift, emb_apd, delta_qa, deficit_qa, gain_qa")
    args = ap.parse_args()

    W_all = load_jsonl(args.weights)
    extra = {}
    for r in load_jsonl(args.extra_scores):
        extra.setdefault(r["id"], {}).update({k: v for k, v in r.items() if k in EXTRA_KEYS and ok(v)})
        if r.get("channel_qa"):  # v0.6 routing channel (string, not included in ablation)
            extra[r["id"]]["channel_qa"] = r["channel_qa"]
    for w in W_all:
        w.update(extra.get(w["id"], {}))
    if args.main_score == "delta_qa":
        # Use E_qa as the main score: rename fields globally so all downstream delta_hat* references point to the E_qa version; keep original cloze value as delta_hat_cloze
        for w in W_all:
            w["delta_hat_cloze"] = w.get("delta_hat")
            w["delta_hat"] = w.get("delta_qa", float("nan"))
            w["weight"] = (w.get("tf_norm", 1.0) * max(w["delta_hat"], 0.0)) if ok(w.get("delta_hat")) else float("nan")
            w["delta_hat_gloss_perturbed"] = w.get("delta_qa_perturbed", float("nan"))
            w["delta_hat_alt"] = w.get("delta_qa_alt", float("nan"))
            w["delta_hat_gold"] = w.get("delta_qa_gold", float("nan"))
            w["deficit"] = w.get("deficit_qa", w.get("deficit", float("nan")))
    W = [w for w in W_all if ok(w.get(args.score))]
    S = lambda w: w[args.score]  # noqa
    by_src = defaultdict(list)
    for w in W:
        by_src[w["labels"].get("source", "?")].append(w)
    synth = by_src.get("synth", [])
    neo = by_src.get("neobench", [])
    main_s = [w for w in synth if w["labels"].get("variant") == "main"]
    rows, notes = [], []

    def add(code, name, value_text, threshold, passed, n=None):
        if n is not None and n < MIN_N:
            rows.append((code, name, value_text, threshold, None))
        else:
            rows.append((code, name, value_text, threshold, bool(passed)))

    def auc_row(code, name, pos, neg, thr, need, pos_r=None, neg_r=None, margin=None):
        a = auroc(pos, neg)
        ar = auroc(pos_r, neg_r) if pos_r is not None else float("nan")
        txt = f"AUROC={fmt(a)} {ci_txt(pos, neg)}"
        if ok(ar):
            txt += f"(rarity baseline {fmt(ar)})"
        passed = ok(a) and a >= need and (margin is None or not ok(ar) or a - ar >= margin)
        add(code, f"{name}, n+={len(pos)} n-={len(neg)}", txt, thr, passed, n=min(len(pos), len(neg)) * 2)
        return a, ar

    # ---------------- E1 ----------------
    if main_s:
        cc = [w for w in main_s if w["labels"]["quadrant"] == "prior_conflict" and w["labels"]["tf"] >= 16]
        rc = [w for w in main_s if w["labels"]["quadrant"] == "prior_consistent" and w["labels"].get("common") is False]
        auc_row("E1", "Frequency confound (synthetic, weight)", [w["weight"] for w in cc], [w["weight"] for w in rc], "≥0.80", 0.80,
                [w["rarity"] for w in cc], [w["rarity"] for w in rc])

    # ---------------- E2 ----------------
    def e2(rows_, label, code="E2"):
        pos = [w for w in rows_ if w["labels"]["quadrant"] == "prior_conflict"]
        neg = [w for w in rows_ if w["labels"]["quadrant"] == "prior_consistent"]
        return auc_row(code, f"Redefined common-word blind spot ({label})", [S(w) for w in pos], [S(w) for w in neg],
                       "≥0.75 and ≥baseline+0.15", 0.75, [w["rarity"] for w in pos], [w["rarity"] for w in neg], margin=0.15)
    if main_s:
        e2(main_s, "Synthetic")
    if neo:
        e2(neo, "NEO-BENCH semantic vs substitute")
        common_sem = [w for w in neo if w["labels"]["quadrant"] == "prior_conflict" and ok(w.get("rarity")) and w["rarity"] <= 4.5]
        subs = [w for w in neo if w["labels"]["quadrant"] == "prior_consistent"]
        if len(common_sem) >= 5:
            auc_row("E2c", "Redefined common-word blind spot (NEO-BENCH common form semantic)", [S(w) for w in common_sem], [S(w) for w in subs],
                    "≥0.75 and ≥baseline+0.15", 0.75, [w["rarity"] for w in common_sem], [w["rarity"] for w in subs], margin=0.15)

    # ---------------- E3 ----------------
    mix = [w for w in synth if ok(w["labels"].get("mixture"))]
    if len(mix) >= 4:
        rho, p = spearman_perm_p([w["labels"]["mixture"] for w in mix], [S(w) for w in mix])
        add("E3", f"Mixed usage (synthetic, n={len(mix)})", f"Spearman={fmt(rho)} p={fmt(p)}", ">0 and p<0.05",
            ok(rho) and rho > 0 and p < 0.05, n=len(mix))

    # ---------------- E4 ----------------
    inf = {w["term"]: S(w) for w in synth if w["labels"].get("variant") == "inferable"}
    if inf:
        diffs = [S(w) - inf[w["term"]] for w in main_s if w["term"] in inf]
        add("E4", f"Context-inferable confound (synthetic, n={len(diffs)})", f"Δ̂_opaque−Δ̂_inferable={fmt(mean(diffs))}", "Report (<0 flagged)",
            mean(diffs) >= 0, n=len(diffs))

    # ---------------- E5 ----------------
    if main_s:
        opq = [S(w) for w in main_s if w["labels"]["quadrant"] == "no_prior" and w["labels"].get("guessable") is False]
        gss = [S(w) for w in main_s if w["labels"]["quadrant"] == "no_prior" and w["labels"].get("guessable") is True]
        auc_row("E5", "Word-formation guessability (synthetic, opaque>guessable)", opq, gss, "≥0.60", 0.60)
    if neo:
        o = [w for w in neo if w["labels"]["quadrant"] == "no_prior"]
        g = [w for w in neo if w["labels"]["quadrant"] == "guessable"]
        auc_row("E5", "Word-formation guessability (NEO-BENCH novel/acronym > phrase/morph)", [S(w) for w in o], [S(w) for w in g], "≥0.60", 0.60,
                [w["rarity"] for w in o], [w["rarity"] for w in g])

    # ---------------- E6 / E7 / E6b ----------------
    b6 = [w for w in W if ok(w.get("delta_hat_gloss_perturbed")) and ok(w.get("delta_hat"))]
    if len(b6) >= 5:
        r = spearman([w["delta_hat"] for w in b6], [w["delta_hat_gloss_perturbed"] for w in b6])
        add("E6", f"Gloss-sensitive (n={len(b6)})", f"Spearman={fmt(r)}", "≥0.80", ok(r) and r >= 0.80, n=len(b6))
    b7 = [w for w in W if ok(w.get("delta_hat_alt")) and ok(w.get("delta_hat"))]
    if len(b7) >= 5:
        r = spearman([w["delta_hat"] for w in b7], [w["delta_hat_alt"] for w in b7])
        add("E7", f"Perturbation instability (context subsampling, n={len(b7)})", f"Spearman={fmt(r)}", "≥0.80", ok(r) and r >= 0.80, n=len(b7))
    gold = [w for w in W if ok(w.get("delta_hat_gold")) and ok(w.get("delta_hat"))]
    if len(gold) >= 5:
        r = spearman([w["delta_hat"] for w in gold], [w["delta_hat_gold"] for w in gold])
        add("E6b", f"auto gloss vs gold gloss (n={len(gold)})", f"Spearman={fmt(r)}", "Report (<0.5 flagged)", ok(r) and r >= 0.5, n=len(gold))

    # ---------------- E10 ----------------
    if neo:
        vals = {}
        for lab, cond in (("single-word", lambda w: w["labels"].get("n_words", 1) == 1), ("multi-word", lambda w: w["labels"].get("n_words", 1) >= 2)):
            pos = [S(w) for w in neo if w["labels"]["quadrant"] == "prior_conflict" and cond(w)]
            neg = [S(w) for w in neo if w["labels"]["quadrant"] == "prior_consistent" and cond(w)]
            vals[lab] = (auroc(pos, neg), len(pos), len(neg))
        a1, a2 = vals["single-word"][0], vals["multi-word"][0]
        add("E10", f"Term granularity (NEO-BENCH, single-word n+={vals['single-word'][1]}, multi-word n+={vals['multi-word'][1]})",
            f"E2 AUROC single-word={fmt(a1)} multi-word={fmt(a2)}", "multi-word≥single-word−0.10", ok(a1) and ok(a2) and a2 >= a1 - 0.10,
            n=min(vals["single-word"][1], vals["multi-word"][1]) * 2)

    # ---------------- Construct C ----------------
    if main_s:
        rho, p = spearman_perm_p([TIER_ORD[w["labels"]["tier"]] for w in main_s], [S(w) for w in main_s])
        add("C", f"Construct validity: {args.score} vs design tier (synthetic main, n={len(main_s)})", f"Spearman={fmt(rho)} p={fmt(p)}", "≥0.5",
            ok(rho) and rho >= 0.5, n=len(main_s))
        conf = [S(w) for w in main_s if w["labels"]["quadrant"] == "prior_conflict"]
        cons = [S(w) for w in main_s if w["labels"]["quadrant"] == "prior_consistent"]
        nop = [S(w) for w in main_s if w["labels"]["quadrant"] == "no_prior"]
        notes.append(f"- Synthetic main four-quadrant {args.score} median: prior_conflict={fmt(sorted(conf)[len(conf)//2]) if conf else 'n/a'},"
                     f"no_prior={fmt(sorted(nop)[len(nop)//2]) if nop else 'n/a'}, prior_consistent={fmt(sorted(cons)[len(cons)//2]) if cons else 'n/a'}")
        if all(ok(w.get("delta_raw")) for w in main_s):
            neg_raw = [w["term"] for w in main_s if w["delta_raw"] < -0.05]
            notes.append(f"- Terms with delta_raw < −0.05 (prior gloss actually more helpful / gloss suspicious): {', '.join(neg_raw) or 'none'}")
        unk = [w["term"] for w in main_s if w.get("prior_unknown")]
        notes.append(f"- Terms self-reported as UNKNOWN by readers ({len(unk)}): {', '.join(unk) or 'none'}")

    # ---------------- P / U / E12 / E15 (requires failures) ----------------
    F = load_jsonl(args.failures)
    fails = {}
    if F:
        acc = defaultdict(lambda: defaultdict(list))
        std = defaultdict(lambda: defaultdict(list))
        for f in F:
            if f.get("qid") == "def":
                continue
            if f.get("sense", "corpus") == "standard":   # Standard-sense items for conflict terms: report separately (E12s), not included in P/U
                std[f["id"]][f["condition"]].append(1.0 if f["correct"] else 0.0)
                continue
            acc[f["id"]][f["condition"]].append(1.0 if f["correct"] else 0.0)
        if std:
            sb = [mean(d["bare"]) for d in std.values() if d.get("bare")]
            si = [mean(d["inject"]) for d in std.values() if d.get("inject")]
            sg = [mean(d["gloss"]) for d in std.values() if d.get("gloss")]
            notes.append(f"- E12s (report) **standard-sense** items for conflict terms: acc bare={fmt(mean(sb),2)} gloss={fmt(mean(sg),2)} inject={fmt(mean(si),2)} (n={len(sb)} terms)——"
                         f"After the glossary states X is an internal sense, can the model still answer per the usual sense in clearly everyday contexts")
        fails = {i: {c: mean(v) for c, v in d.items()} for i, d in acc.items()}
        for name, rows_ in (("synthetic", main_s), ("NEO-BENCH", [w for w in neo if w["labels"].get("is_target")])):
            if name == "NEO-BENCH":
                accd = defaultdict(list)
                for f in F:
                    if f.get("qid") == "def" and f["condition"] == "bare" and f["id"].startswith("neo:"):
                        accd[f["id"]].append(1.0 if f["correct"] else 0.0)
                fd = {i: {"bare": mean(v)} for i, v in accd.items()}
            else:
                fd = fails
            ts = [w for w in rows_ if w["id"] in fd and ok(fd[w["id"]].get("bare"))]
            if len(ts) < 6:
                continue
            bare_fail = [1 - fd[w["id"]]["bare"] for w in ts]
            pos = [S(w) for w, bf in zip(ts, bare_fail) if bf >= 0.5]
            neg = [S(w) for w, bf in zip(ts, bare_fail) if bf < 0.5]
            a = auroc(pos, neg)
            ar = auroc([w["rarity"] for w, bf in zip(ts, bare_fail) if bf >= 0.5], [w["rarity"] for w, bf in zip(ts, bare_fail) if bf < 0.5])
            rho, p = spearman_perm_p([S(w) for w in ts], bare_fail)
            pr = partial_spearman(bare_fail, [S(w) for w in ts], [[w["rarity"] for w in ts], [w["tf_norm"] for w in ts]])
            add("P", f"Predictive validity: {args.score}->bare failure ({name}, n={len(ts)}, failure rate {fmt(mean(bare_fail),2)})",
                f"AUROC={fmt(a)} {ci_txt(pos, neg)} (rarity baseline {fmt(ar)}); Spearman={fmt(rho)} p={fmt(p)}; partial correlation (controlling rarity,tf)={fmt(pr)}",
                "AUROC>=0.70 and increment>0", ok(a) and a >= 0.70 and ok(pr) and pr > 0, n=len(ts))
            if name == "synthetic":
                # v0.3 dual channel: use delta_hat for conflict channel, deficit for unknown channel, report P separately; U adds within-channel percentile ranking
                for ch, sc in (("conflict", "delta_hat"), ("guess", "delta_hat"), ("unknown", "deficit")):
                    tc = [w for w in ts if w.get("channel", "conflict") == ch and ok(w.get(sc))]
                    if len(tc) >= 4:
                        bfc = [1 - fd[w["id"]]["bare"] for w in tc]
                        pos_c = [w[sc] for w, b in zip(tc, bfc) if b >= 0.5]; neg_c = [w[sc] for w, b in zip(tc, bfc) if b < 0.5]
                        add(f"P-{ch}", f"Predictive validity ({ch} channel, {sc}->bare failure, n={len(tc)}, failure rate {fmt(mean(bfc),2)})",
                            f"AUROC={fmt(auroc(pos_c, neg_c))} {ci_txt(pos_c, neg_c)}", "AUROC≥0.70", ok(auroc(pos_c, neg_c)) and auroc(pos_c, neg_c) >= 0.70, n=len(tc))
                if any("channel" in w for w in ts):
                    from collections import Counter as _C
                    notes.append("- Channel distribution (synthetic main):" + str(dict(_C(w.get("channel") for w in ts))) +
                                 "; conflict channel within-quadrant counts:" + str(dict(_C(w["labels"]["quadrant"] for w in ts if w.get("channel") == "conflict"))))
                    # Within-channel percentile x tf ranking
                    pr = {}
                    for ch in ("conflict", "guess", "unknown"):
                        tc = [w for w in ts if w.get("channel") == ch]
                        sc = "deficit" if ch == "unknown" else "delta_hat"
                        vals = sorted(w[sc] for w in tc if ok(w.get(sc)))
                        for w in tc:
                            pr[w["id"]] = (sum(1 for v in vals if v <= w[sc]) / len(vals)) if (vals and ok(w.get(sc))) else 0.0
                    a_2ch, _ = budget_curve(ts, lambda w: -(w["tf_norm"] * pr.get(w["id"], 0.0)), fd)
                    notes.append(f"- U (dual-channel percentile x tf ranking) budget curve AUC = {fmt(a_2ch)}")
                gains = [fd[w["id"]].get("gloss", float("nan")) - fd[w["id"]]["bare"] for w in ts]
                if all(ok(g) for g in gains):
                    rho2, p2 = spearman_perm_p([S(w) for w in ts], gains)
                    add("P2", f"Predictive validity: {args.score}->explanation gain Delta acc (synthetic, n={len(ts)})", f"Spearman={fmt(rho2)} p={fmt(p2)}", "report", True, n=len(ts))
                    a_pdw, _ = budget_curve(ts, lambda w: -(w["tf_norm"] * w[args.score]), fd)
                    a_rar, _ = budget_curve(ts, lambda w: -w["rarity"], fd)
                    rng = random.Random(0)
                    a_rnd = mean([budget_curve(ts, lambda w, r=rng.random(): r, fd)[0] for _ in range(20)])
                    a_orc, _ = budget_curve(ts, lambda w: -(fd[w["id"]]["gloss"] - fd[w["id"]]["bare"]), fd)
                    add("U", f"Utility validity: budget curve area (synthetic, tf x {args.score} ranking, independent approximation)",
                        f"PDW={fmt(a_pdw)} rarity={fmt(a_rar)} random={fmt(a_rnd)} oracle={fmt(a_orc)}", "PDW≥rarity+0.05",
                        ok(a_pdw) and ok(a_rar) and a_pdw >= a_rar + 0.05, n=len(ts))
                    # E15: budget curve weighted by query frequency, comparing w_use=tf vs w_use=query_freq
                    a_tf, _ = budget_curve(ts, lambda w: -(w["labels"]["tf"] * w[args.score]), fd, wkey="query_freq")
                    a_qf, _ = budget_curve(ts, lambda w: -(w["labels"].get("query_freq", w["labels"]["tf"]) * w[args.score]), fd, wkey="query_freq")
                    add("E15", f"Exposure weight source (synthetic, weighted by query distribution, n={len(ts)})",
                        f"AUC(w=query_freq)={fmt(a_qf)} vs AUC(w=tf)={fmt(a_tf)}", "query_freq version >= tf version",
                        ok(a_qf) and ok(a_tf) and a_qf >= a_tf, n=len(ts))
                # E12 over-suspicion: prior_consistent terms inject vs bare
                pc = [w for w in ts if w["labels"]["quadrant"] == "prior_consistent" and ok(fd[w["id"]].get("inject"))]
                if pc:
                    d = mean([fd[w["id"]]["inject"] - fd[w["id"]]["bare"] for w in pc])
                    add("E12", f"Over-suspicion (synthetic prior_consistent items, injected top-B glossary, n={len(pc)})",
                        f"acc_inject-acc_bare={fmt(d)} (bare={fmt(mean([fd[w['id']]['bare'] for w in pc]),2)})", "≥−0.05", d >= -0.05, n=len(pc))
                    # Also: repair amount for prior_conflict items under actual injection (realized budget effect)
                    pf = [w for w in ts if w["labels"]["quadrant"] == "prior_conflict" and ok(fd[w["id"]].get("inject"))]
                    if pf:
                        inb = [f.get("in_glossary") for f in F if f["condition"] == "inject" and f["id"] in {w["id"] for w in pf}]
                        notes.append(f"- After actually injecting top-B glossary, prior_conflict items: acc bare={fmt(mean([fd[w['id']]['bare'] for w in pf]),2)} -> "
                                     f"inject={fmt(mean([fd[w['id']]['inject'] for w in pf]),2)} (gloss upper bound {fmt(mean([fd[w['id']].get('gloss', float('nan')) for w in pf]),2)};"
                                     f"glossary coverage {sum(1 for x in inb if x)}/{len(inb)} items)")
        # E13 abstention retention: synthetic no_prior and opaque definition items UNKNOWN rate inject vs bare
        dq = defaultdict(lambda: defaultdict(list))
        for f in F:
            if f.get("qid") == "def" and f["id"].startswith("synth:") and "unknown" in f:
                dq[f["id"]][f["condition"]].append(1.0 if f["unknown"] else 0.0)
        opq_ids = {w["id"] for w in main_s if w["labels"]["quadrant"] == "no_prior" and w["labels"].get("guessable") is False}
        rows13 = [(mean(dq[i]["bare"]), mean(dq[i]["inject"])) for i in opq_ids if "bare" in dq[i] and "inject" in dq[i]]
        if rows13:
            ub, ui = mean([r[0] for r in rows13]), mean([r[1] for r in rows13])
            add("E13", f"Abstention retention (synthetic opaque definition items, n={len(rows13)})", f"UNKNOWN rate bare={fmt(ub,2)} inject={fmt(ui,2)}, diff={fmt(ui-ub)}",
                "≥−0.10", ui - ub >= -0.10, n=len(rows13))
            allp = [(mean(dq[i]["bare"]), mean(dq[i]["inject"])) for i in dq if "bare" in dq[i] and "inject" in dq[i]]
            notes.append(f"- Synthetic all-term definition items UNKNOWN rate: bare={fmt(mean([r[0] for r in allp]),2)} inject={fmt(mean([r[1] for r in allp]),2)} (n={len(allp)})")

    # ---------------- E11 ----------------
    D = load_jsonl([args.distractor_failures] if args.distractor_failures else [])
    if D:
        b = mean([1.0 if d["correct"] else 0.0 for d in D if d["condition"] == "bare"])
        i = mean([1.0 if d["correct"] else 0.0 for d in D if d["condition"] == "inject"])
        add("E11", f"Negative transfer (distractor items n={len(D)//2}, budget={D[0].get('budget')})", f"acc_inject-acc_bare={fmt(i - b)} (bare={fmt(b,2)})", "≥−0.02", i - b >= -0.02)

    # ---------------- E14 candidate recall ----------------
    if args.corpus and os.path.exists(args.corpus) and main_s:
        cnt = defaultdict(int)
        docs = [json.loads(l)["text"] for l in open(args.corpus, encoding="utf-8")]
        for d in docs:
            for t in tokens(d):
                cnt[t.lower()] += 1
        cand = {t for t, c in cnt.items() if c >= args.tf_min}
        conf = [w for w in main_s if w["labels"]["quadrant"] == "prior_conflict"]

        def in_cand(term):
            return all(any(re.sub(r"s$", "", p.lower()) == re.sub(r"s$", "", c) for c in cand) for p in term.split())
        hit = [w["term"] for w in conf if in_cand(w["term"])]
        miss = [w["term"] for w in conf if w["term"] not in hit]
        add("E14", f"Candidate recall (synthetic corpus, tf>={args.tf_min}, {len(cand)} candidate words)", f"prior_conflict entering candidates {len(hit)}/{len(conf)}" + (f", missed: {', '.join(miss)}" if miss else ""),
            "=1.00", not miss)

    # ---------------- J1 ----------------
    J = load_jsonl([args.judge_pairs] if args.judge_pairs else [])
    if J:
        accj = mean([1.0 if j["pred_same"] == j["gold_same"] else 0.0 for j in J])
        maj = max(mean([j["gold_same"] for j in J]), 1 - mean([j["gold_same"] for j in J]))
        add("J1", f"judge prior contamination (TempoWiC, n={len(J)})", f"acc={fmt(accj)} (majority class baseline {fmt(maj)})", "≥0.70 and >baseline", accj >= 0.70 and accj > maj, n=len(J))

    # ---------------- Global quantities ----------------
    if main_s and all(ok(w.get("delta_hat")) for w in main_s):
        total = sum(w["tf_norm"] * w["delta_hat"] for w in main_s)
        notes.insert(0, f"- Synthetic corpus total correction Σ tf_norm·Δ̂ = {total:.3f} (term count {len(main_s)})")

    # ---------------- Ablation A (output only when main score is delta_hat) ----------------
    abl = []
    if args.score == "delta_hat" and main_s:
        for sc in ABL_SCORES:
            ws = [w for w in main_s if ok(w.get(sc))]
            if len(ws) < 6:
                continue
            pos = [w[sc] for w in ws if w["labels"]["quadrant"] == "prior_conflict"]
            neg = [w[sc] for w in ws if w["labels"]["quadrant"] == "prior_consistent"]
            e2a = auroc(pos, neg)
            cc = [w[sc] for w in ws if w["labels"]["quadrant"] == "prior_conflict" and w["labels"]["tf"] >= 16]
            rc = [w[sc] for w in ws if w["labels"]["quadrant"] == "prior_consistent" and w["labels"].get("common") is False]
            e1a = auroc([w["labels"]["tf"] / 40 * x for w, x in zip([w for w in ws if w["labels"]["quadrant"] == "prior_conflict" and w["labels"]["tf"] >= 16], cc)],
                        [w["labels"]["tf"] / 40 * x for w, x in zip([w for w in ws if w["labels"]["quadrant"] == "prior_consistent" and w["labels"].get("common") is False], rc)]) if sc not in ("rarity", "self_report", "self_extract", "emb_shift", "emb_apd", "deficit_lp") else auroc(cc, rc)
            rho_c, _ = spearman_perm_p([TIER_ORD[w["labels"]["tier"]] for w in ws], [w[sc] for w in ws], n_perm=200)
            pa = ua = float("nan")
            if fails:
                ts = [w for w in ws if w["id"] in fails and ok(fails[w["id"]].get("bare"))]
                if len(ts) >= 6:
                    bf = [1 - fails[w["id"]]["bare"] for w in ts]
                    pa = auroc([w[sc] for w, b in zip(ts, bf) if b >= 0.5], [w[sc] for w, b in zip(ts, bf) if b < 0.5])
                    ua, _ = budget_curve(ts, lambda w: -(w["tf_norm"] * w[sc]), fails)
            abl.append((sc, e1a, e2a, rho_c, pa, ua))

    out = ["# PDW scorecard (ERROR_STANDARD v0.3.1)", "",
           f"- Main score: `{args.score}`" + ("(E_qa version: delta_hat = delta_qa, E6/E7/E6b use E_qa variants)" if args.main_score == "delta_qa" else "(cloze version)") + f"; weight files: {', '.join(args.weights)}",
           "- Term entries: " + ", ".join(f"{k}={len(v)}" for k, v in by_src.items()),
           f"- Decision rule: slices with n<{MIN_N} are reported only, not judged (marked \"insufficient power\"); AUROC includes bootstrap 95% interval", ""]
    out += notes + ["", "| No. | Failure mode / validity | Result | Threshold | Verdict |", "|---|---|---|---|---|"]
    for code, name, val, thr, passed in rows:
        verdict = "Insufficient power (report only)" if passed is None else ("Pass" if passed else "Fail")
        out.append(f"| {code} | {name} | {val} | {thr} | {verdict} |")
    gate = [r for r in rows if r[0] in ("E1", "E2", "E5")]
    if gate:
        if any(r[4] is None for r in gate):
            g = "Threshold slices contain items with insufficient power; no release decision made this round (see ERROR_STANDARD §3 rule 6)"
        else:
            g = "All passed" if all(r[4] for r in gate) else "Contains failed items; estimator not releasable (see ERROR_STANDARD §3)"
        out += ["", "**Release threshold (E1/E2/E5):** " + g]
    guards = [r for r in rows if r[0] in ("E11", "E12", "E13", "E14", "E15")]
    if guards:
        bad = [r[0] for r in guards if r[4] is False]
        out += ["", "**Invariant guards (E11–E15):** " + ("No degradation" if not bad else "Degradation: " + ", ".join(bad))]
    if abl:
        out += ["", "## Ablation A (synthetic main)", "", "| Main score | E1 AUROC | E2 AUROC | C Spearman | P AUROC | U AUC |", "|---|---|---|---|---|---|"]
        for sc, e1a, e2a, rc_, pa, ua in abl:
            out.append(f"| {sc} | {fmt(e1a)} | {fmt(e2a)} | {fmt(rc_)} | {fmt(pa)} | {fmt(ua)} |")
    # ---- v0.5: real corpus segment (when no design quadrant labels): use E_qa low-context questions as behavioral ground truth
    unl = [w for w in W_all if not w.get("labels", {}).get("quadrant") and ok(w.get("deficit_qa"))]
    if len(unl) >= 10:
        out += ["", "## Real corpus (no design labels; ground truth = E_qa low-context questions)", ""]
        fq = {w["id"]: {"bare": 1 - w["deficit_qa"], "gloss": (1 - w["deficit_qa"]) + w["gain_qa"] if ok(w.get("gain_qa")) else float("nan")} for w in unl}
        bf = [w["deficit_qa"] for w in unl]
        gm_harm = [-(w["gain_qa"] - w["delta_qa"]) for w in unl if ok(w.get("gain_qa")) and ok(w.get("delta_qa"))]  # acc_bare − acc_glossM
        out += [f"- Terms n={len(unl)}; low-context question bare failure rate mean {fmt(mean(bf),2)}; failure rate after corpus gloss {fmt(mean([1 - fq[w['id']]['gloss'] for w in unl if ok(fq[w['id']]['gloss'])]),2)}; "
                f"accuracy difference between reader's own prior as gloss vs bare {fmt(-mean(gm_harm),2) if gm_harm else 'n/a'} (negative = prior misleading)"]
        forms = {}
        for w in unl:
            forms.setdefault(w["labels"].get("form") or ("multi" if w["labels"].get("n_words", 1) > 1 else "single"), []).append(w["deficit_qa"])
        out.append("- Bare failure rate by word form: " + "; ".join(f"{k} {fmt(mean(v),2)} (n={len(v)})" for k, v in sorted(forms.items())))
        # v0.6: grouped by three-channel routing (channel_qa from run_eqa) -- conflict / instantiation / unknown / guess / consistent
        chans = defaultdict(list)
        for w in unl:
            if w.get("channel_qa"):
                chans[w["channel_qa"]].append(w)
        if chans:
            def _fm(w):  # 1 − acc_glossM = deficit − gain + delta
                return w["deficit_qa"] - w["gain_qa"] + w["delta_qa"] if ok(w.get("gain_qa")) and ok(w.get("delta_qa")) else None
            out.append("- By behavioral routing channel (channel_qa): " + "; ".join(
                f"{k} n={len(v)} bare failure {fmt(mean([w['deficit_qa'] for w in v]),2)} / after own prior {fmt(mean([x for x in map(_fm, v) if x is not None]),2) if any(_fm(w) is not None for w in v) else 'n/a'} / after corpus gloss {fmt(mean([w['deficit_qa'] - w['gain_qa'] for w in v if ok(w.get('gain_qa'))]),2)}"
                for k, v in sorted(chans.items(), key=lambda kv: -len(kv[1]))))
            out.append("  How to read: conflict = prior misleading (needs negated-scope gloss); instantiation = general sense correct, instance unknown (one definitional hint suffices); unknown/guess = no prior (needs definition); consistent = no explanation needed.")
        hi = [w for w in unl if w["deficit_qa"] >= 0.5]
        out.append(f"- Terms with failure rate ≥0.5 {len(hi)}: " + ", ".join(sorted(w["term"] for w in hi)[:30]))
        out += ["", "| Score | P: AUROC predicting low-context failure | Spearman(score, failure rate) | U: budget curve AUC (tf×score) |", "|---|---|---|---|"]
        for sc in ("self_report", "delta_lp", "emb_apd", "emb_shift", "delta_hat", "deficit", "rarity", "tf_norm"):
            if sc == "deficit" and args.main_score == "delta_qa":
                continue  # In E_qa mode, deficit has been replaced by deficit_qa, which shares source with ground truth (circular), so it is not listed
            ws = [w for w in unl if ok(w.get(sc))]
            if len(ws) < 10:
                continue
            pos = [w[sc] for w in ws if w["deficit_qa"] >= 0.5]; neg = [w[sc] for w in ws if w["deficit_qa"] < 0.5]
            au = auroc(pos, neg) if (pos and neg) else float("nan")
            rho = spearman([w[sc] for w in ws], [w["deficit_qa"] for w in ws])
            ua, _ = budget_curve(ws, lambda w: -(w["tf_norm"] * w[sc]), fq)
            out.append(f"| {sc} | {fmt(au)} {ci_txt(pos, neg) if (len(pos) > 1 and len(neg) > 1) else ''} | {fmt(rho)} | {fmt(ua)} |")
        ua_r, _ = budget_curve(unl, lambda w: random.Random(0).random(), fq); ua_o, _ = budget_curve(unl, lambda w: -(w["tf_norm"] * (fq[w["id"]]["gloss"] - fq[w["id"]]["bare"]) if ok(fq[w["id"]]["gloss"]) else 0), fq)
        out.append(f"| random / oracle | | | {fmt(ua_r)} / {fmt(ua_o)} |")
        out.append("")
        out.append("- How to read: the P row answers \"can the detection-layer score predict misreading under real usage\"; delta_qa itself shares source with ground truth (circular), so not listed. When E_qa question generation is gold-anchored, question quality does not depend on the drafting model's understanding of the corpus.")
    text = "\n".join(out) + "\n"
    open(args.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
