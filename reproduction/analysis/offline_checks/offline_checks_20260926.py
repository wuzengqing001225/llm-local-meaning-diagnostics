#!/usr/bin/env python3
"""Offline checks computed 2026-09-23..26 from the released reproduction data. No model calls.

Usage:
  python3 offline_checks_20260926.py --data pd-reproduction/data \
      --recovered pd-reproduction/audit/recovered \
      --term-csv term_meaning_difference.csv --out offline_checks_results.json

Sections (keys in the output JSON):
  table2_duplicate_rows   R AUROC and term-cluster bootstrap CI for Synthetic/GPT6 and DeFi/DeepSeek
  reader_to_reader        proxy R vs other readers' actual failures, same questions
  r_by_category           R AUROC inside redefined/standard (synthetic) and glossary/control (Reddit) items
  control_arms            DeepSeek accuracy/repairs/harms: source definition, drafted gloss, truncated drafted gloss, model's own usual gloss
  leakage                 gloss-option lexical overlap; leak-free subset error rates, R and dp AUROC
  rag_leave_one_out       CUAD and Reddit gated-RAG accuracy with each question's own risk removed; exact where an existing arm matches, otherwise binary partial identification
  jev_self_error          Jev confidence -> its own error, by corpus and condition
  term_distance_glossG    question-free meaning distance vs term-level repair under the SOURCE definition (DeepSeek)
  shared_budget_sim       offline shared-library selection (freq x dp / cost vs freq / cost), B arm under drafted gloss and under source entry
  stable_errors           ten-sample stable-wrong statistic after the source-conflict exclusion
Convention: the 456-item matched proxy frame excludes one source-conflicted item;
the 761-item full synthetic frame excludes that item and a conflicted mix0.7 item.
"""
import argparse, csv, json, os, random, re
from collections import Counter, defaultdict

EXCL = {("v1:desk:interest", 1)}
FULL_SYNTHETIC_EXCL = EXCL | {("v1:desk:interest@mix0.7", 0)}


def mean(v):
    v = [x for x in v if x is not None and x == x]
    return sum(v) / len(v) if v else float("nan")


def auroc(pos, neg):
    pos = [x for x in pos if x is not None and x == x]; neg = [x for x in neg if x is not None and x == x]
    if not pos or not neg: return float("nan")
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg]); rank = {}; i = 0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]: j += 1
        rank[allv[i][0]] = (i + j + 1) / 2; i = j
    return (sum(rank[v] for v in pos) - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def spearman(x, y):
    pr = [(a, b) for a, b in zip(x, y) if a is not None and b is not None and a == a and b == b]
    if len(pr) < 3: return float("nan"), len(pr)
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    a, b = rk([p[0] for p in pr]), rk([p[1] for p in pr]); ma, mb = mean(a), mean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b)); den = (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** 0.5
    return (num / den if den else float("nan")), len(pr)


class Data:
    """File lookup by name. When a name occurs more than once (only v1_weights.jsonl in the release),
    prefer the copy under raw_outputs/: that is the file whose gloss_used matches what the readers received
    (197/197 against the recovered prompts); the copy under inputs/ is an earlier weights run."""
    def __init__(self, root):
        self.idx = {}
        for dp, _, fs in sorted(os.walk(root)):
            for f in fs:
                if f.startswith("._"): continue
                p = os.path.join(dp, f)
                if f not in self.idx or ("raw_outputs" in p and "raw_outputs" not in self.idx[f]): self.idx[f] = p
    def rows(self, f): return [json.loads(l) for l in open(self.idx[f], encoding="utf-8")]
    def byid(self, f): return {r["id"]: r for r in self.rows(f)}


def qtable(D, lp, eq, excl=EXCL):
    LP, E = D.byid(lp), D.byid(eq); out = []
    for i, r in LP.items():
        e = E.get(i)
        if not e or not r.get("per_question"): continue
        qd = (r.get("labels") or {}).get("quadrant")
        for j, p in enumerate(r["per_question"]):
            if j >= len(e["questions"]) or (i, j) in excl: continue
            q = e["questions"][j]; c = q.get("correct") or {}
            if c.get("bare") is None: continue
            out.append(dict(term=i, j=j, quad=qd, R=1 - p["bare"]["p_correct"],
                            dp=(p["glossC"]["p_correct"] - p["bare"]["p_correct"]) if "glossC" in p else None,
                            fail=1 - c["bare"], c=c, q=q))
    return out


def a_R(rows): return auroc([r["R"] for r in rows if r["fail"]], [r["R"] for r in rows if not r["fail"]])


def boot_R(rows, B=2000, seed=0):
    g = defaultdict(list)
    for r in rows: g[r["term"]].append(r)
    keys = list(g); rng = random.Random(seed); vals = []
    for _ in range(B):
        vals.append(a_R([r for k in (rng.choice(keys) for _ in keys) for r in g[k]]))
    vals.sort(); return [vals[int(.025 * B)], vals[int(.975 * B) - 1]]


SETS = {"Synthetic": ("lpmc_v1.jsonl", {"DeepSeek": "v1_eqa.jsonl", "GPT6": "astra6_v1_eqa.jsonl"}, "v1_weights.jsonl"),
        "Reddit": ("lpmc_reddit.jsonl", {"DeepSeek": "reddit_eqa.jsonl", "GPT6": "astra6_reddit_eqa.jsonl"}, "reddit_weights.jsonl"),
        "DeFi": ("defi_strict_lpmc.jsonl", {"DeepSeek": "defi_strict_eqa.jsonl", "GPT5.6": "defi_strict_eqa_gpt.jsonl", "GPT6": "astra6_defi_strict_eqa.jsonl"}, "defi_strict_weights.jsonl")}


def table2_duplicate_rows(D):
    out = {}
    for lab, lp, eq in (("Synthetic/GPT6", "lpmc_v1.jsonl", "astra6_v1_eqa.jsonl"), ("DeFi/DeepSeek", "defi_strict_lpmc.jsonl", "defi_strict_eqa.jsonl")):
        rows = qtable(D, lp, eq); out[lab] = dict(n=len(rows), fails=sum(r["fail"] for r in rows), R_auroc=a_R(rows), ci_term_cluster=boot_R(rows))
    return out


def reader_to_reader(D):
    out = []
    for corp, (lp, readers, _) in SETS.items():
        LP = D.byid(lp); Rm = {(i, j): 1 - p["bare"]["p_correct"] for i, r in LP.items() for j, p in enumerate(r.get("per_question") or [])}
        F = {}
        for nm, f in readers.items():
            d = {}
            for i, e in D.byid(f).items():
                for j, q in enumerate(e["questions"]):
                    c = (q.get("correct") or {}).get("bare")
                    if c is not None: d[(i, j)] = 1 - c
            F[nm] = d
        for tgt in readers:
            oth = [o for o in readers if o != tgt]
            keys = [k for k in F[tgt] if k in Rm and all(k in F[o] for o in oth) and k not in EXCL]
            y = [F[tgt][k] for k in keys]; os_ = {k: sum(F[o][k] for o in oth) for k in keys}
            sc = lambda s: auroc([s[k] for k, t in zip(keys, y) if t], [s[k] for k, t in zip(keys, y) if not t])
            out.append(dict(corpus=corp, target=tgt, others="+".join(oth), n=len(keys), proxy_R=sc(Rm), other_readers=sc(os_), R_plus_others=sc({k: Rm[k] + os_[k] for k in keys})))
    return out


def r_by_category(D):
    out = []
    for corp in ("Synthetic", "Reddit"):
        lp, readers, _ = SETS[corp]
        for nm, f in readers.items():
            rows = qtable(D, lp, f)
            for q in sorted({r["quad"] for r in rows}, key=str):
                s = [r for r in rows if r["quad"] == q]
                out.append(dict(setting=f"{corp}/{nm}", category=q, n=len(s), bare_error=mean([r["fail"] for r in s]), R_auroc=a_R(s)))
    return out


def control_arms(D):
    out = {}
    for corp, f in (("Synthetic", "v1_eqa.jsonl"), ("Reddit", "reddit_eqa.jsonl"), ("DeFi", "defi_strict_eqa.jsonl")):
        arms = ("bare", "glossG", "glossC", "glossP", "glossM")
        cs = [q.get("correct") or {} for e in D.rows(f) for j, q in enumerate(e["questions"]) if (e["id"], j) not in FULL_SYNTHETIC_EXCL]
        cs = [c for c in cs if all(c.get(a) is not None for a in arms)]
        out[corp] = dict(n=len(cs), note="synthetic excludes the two source-conflict items",
                         **{a: dict(acc=mean([c[a] for c in cs]), repairs=sum(c["bare"] == 0 and c[a] == 1 for c in cs) if a != "bare" else None,
                                    harms=sum(c["bare"] == 1 and c[a] == 0 for c in cs) if a != "bare" else None) for a in arms})
    out["legend"] = {"glossG": "source definition", "glossC": "model-drafted gloss", "glossP": "drafted gloss truncated to its first 2/3 of words (run_eqa.py)", "glossM": "the model's own gloss under a domain prompt (prior_guess) or a word-form guess; not a context-free dictionary sense"}
    return out


STOP = set("the a an of to and or any in on for by is it its be as with that this which from at their they them are was were has have had not no but if then than such so do does did can may will would should could into over under about more most less very also only just all each other some one two three there here when where who whom what why how you your our we he she his her i me my us".split())


def cw(t, term=""):
    tw = set(re.findall(r"[a-z0-9]+", term.lower()))
    return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if len(w) > 2 and w not in STOP and w not in tw}


def gloss_picks_key(gloss, opts, key_idx, term):
    s = []
    for o in opts:
        ow = cw(o, term); s.append(len(ow & cw(gloss, term)) / len(ow) if ow else 0.0)
    top = max(s); return s[key_idx] == top and s.count(top) == 1 and top > 0


def leakage(D, seed=3):
    out = {}
    for corp in ("Synthetic", "Reddit", "DeFi"):
        lp, readers, wts = SETS[corp]; W = D.byid(wts); E = D.byid(readers["DeepSeek"])
        rows = [r for r in qtable(D, lp, readers["DeepSeek"]) if r["c"].get("glossC") is not None and r["term"] in W]
        for r in rows:
            k = "ABCD".index(str(r["q"]["answer"]).strip().upper()[0]); r["leak"] = gloss_picks_key(W[r["term"]].get("gloss_used") or "", r["q"]["options"], k, E[r["term"]]["term"])
        ids = sorted({r["term"] for r in rows}); gl = [W[i].get("gloss_used") or "" for i in ids]; rng = random.Random(seed); sh = []
        for _ in range(5):
            perm = gl[:]; rng.shuffle(perm); G = dict(zip(ids, perm))
            for r in rows:
                k = "ABCD".index(str(r["q"]["answer"]).strip().upper()[0]); sh.append(gloss_picks_key(G[r["term"]], r["q"]["options"], k, E[r["term"]]["term"]))
        lo = [r for r in rows if not r["leak"]]; errs = [r for r in rows if r["fail"]]; errs_lo = [r for r in lo if r["fail"]]
        out[corp] = dict(n=len(rows), drafted_gloss_picks_key=mean([r["leak"] for r in rows]), shuffled_gloss_baseline=mean(sh), leak_free_n=len(lo),
                         error_bare_all=mean([r["fail"] for r in rows]), error_def_all=mean([1 - r["c"]["glossC"] for r in rows]),
                         error_bare_leakfree=mean([r["fail"] for r in lo]), error_def_leakfree=mean([1 - r["c"]["glossC"] for r in lo]),
                         R_auroc_all=a_R(rows), R_auroc_leakfree=a_R(lo),
                         dp_repair_auroc_all=auroc([r["dp"] for r in errs if r["c"]["glossC"]], [r["dp"] for r in errs if not r["c"]["glossC"]]),
                         dp_repair_auroc_leakfree=auroc([r["dp"] for r in errs_lo if r["c"]["glossC"]], [r["dp"] for r in errs_lo if not r["c"]["glossC"]]))
    out["note"] = "Leak = the option with the unique highest content-word overlap with the drafted gloss is the keyed answer."
    return out


def rag_leave_one_out(D):
    res = {}
    T = D.byid("terms_full.jsonl"); GL = defaultdict(dict)
    for i, t in T.items():
        d = (t.get("def_raw") or "").strip()
        if d: GL[str(t["labels"]["ci"])][t["term"]] = d
    LPF = D.byid("lpmc_full.jsonl")
    def maxrisk(tid, skip_ctx=None):
        pq = [p for p in LPF.get(tid, {}).get("per_question", []) if "bare" in p and str(p.get("ctx_idx")) != str(skip_ctx)]
        return max(1 - p["bare"]["p_correct"] for p in pq) if pq else None
    P = {(p["qkey"], p["arm"]): p for p in D.rows("prompts_t1.jsonl")}; A = {(r["qkey"], r["arm"]): int(r["correct"]) for r in D.rows("rag_v3_t1.jsonl")}
    st = Counter(); acc = defaultdict(list)
    for qk in sorted({k[0] for k in P}):
        tid, cx = qk.rsplit("#", 1); own = tid.split(":", 2)[2]
        orig = {ln[2:].split(":", 1)[0] for ln in P[(qk, "rag_gated")]["gtxt"].splitlines() if ln.startswith("- ")}; loo = set(orig)
        if own in orig:
            rl = maxrisk(tid, cx)
            if rl is None or rl < 0.5: loo.discard(own)
        if loo == orig: a = A[(qk, "rag_gated")]; st["unchanged"] += 1
        elif not loo: a = A[(qk, "rag")]; st["gated set becomes empty (rag answer)"] += 1
        else: a = None; st["no matching arm"] += 1
        for nm, v in (("rag", A[(qk, "rag")]), ("gated_in_sample", A[(qk, "rag_gated")]), ("all_matched", A[(qk, "rag_defrecall")]), ("full_glossary", A[(qk, "rag_full")]), ("loo", a)): acc[nm].append(v)
    n = len(acc["loo"]); known = [x for x in acc["loo"] if x is not None]
    res["CUAD_hybrid"] = dict(n=n, identified=len(known), counts=dict(st), rag=mean(acc["rag"]), gated_in_sample=mean(acc["gated_in_sample"]),
                              gated_loo_partial_identification=[sum(known) / n, (sum(known) + n - len(known)) / n],
                              all_matched=mean(acc["all_matched"]), full_glossary=mean(acc["full_glossary"]),
                              bounds_rule="unidentified items may be 0 or 1; interval = [all wrong, all right]. Scenario fills (retrieval answer / in-sample gated answer) are not bounds.")
    LPr = D.byid("lpmc_reddit.jsonl"); byq = defaultdict(dict)
    for r in D.rows("rag_reddit_t1.jsonl"): byq[r["qkey"]][r["arm"]] = r
    st = Counter(); rr = defaultdict(list)
    for qk, arms in byq.items():
        if not all(a in arms for a in ("rag", "rag_gated", "rag_full")): continue
        g = arms["rag_gated"]; tid, j = qk.rsplit("#", 1); j = int(j); isg = g["quadrant"] == "glossary"
        rest = [1 - p["bare"]["p_correct"] for jj, p in enumerate(LPr.get(tid, {}).get("per_question", [])) if "bare" in p and jj != j]
        tl = mean(rest) if rest else None; was = isg and float(g["trisk"]) >= 0.5; now = isg and tl is not None and tl >= 0.5
        if was == now: a = int(g["correct"]); st["unchanged"] += 1
        elif was and not now and int(g["n_gloss"]) == 1: a = int(arms["rag"]["correct"]); st["gated set becomes empty (rag answer)"] += 1
        else: a = None; st["no matching arm (" + ("drops" if was else "enters") + ")"] += 1
        rr["quad"].append(g["quadrant"]); rr["rag"].append(int(arms["rag"]["correct"])); rr["gated"].append(int(g["correct"])); rr["full"].append(int(arms["rag_full"]["correct"])); rr["loo"].append(a)
    for sub in ("glossary", "all"):
        ks = [k for k in range(len(rr["rag"])) if sub == "all" or rr["quad"][k] == sub]
        known = [rr["loo"][k] for k in ks if rr["loo"][k] is not None]; n = len(ks)
        res[f"Reddit_hybrid_{sub}"] = dict(n=n, identified=len(known), rag=mean([rr["rag"][k] for k in ks]), gated_in_sample=mean([rr["gated"][k] for k in ks]),
                                           gated_loo_partial_identification=[sum(known) / n, (sum(known) + n - len(known)) / n], full_glossary=mean([rr["full"][k] for k in ks]))
    res["Reddit_counts"] = dict(st); res["Reddit_note"] = "No all-matched arm exists for Reddit."
    return res


def jev_self_error(D):
    J = D.rows("jev_answers.jsonl"); out = []
    for k in sorted({(r["set"], r["cond"]) for r in J}):
        rows = [r for r in J if (r["set"], r["cond"]) == k and r.get("correct") not in (None, "", "None") and r.get("confidence") not in (None, "", "None")]
        if k[0] == "v1": rows = [r for r in rows if (r["id"], int(r["qidx"])) not in FULL_SYNTHETIC_EXCL]
        y = [1 - int(float(r["correct"])) for r in rows]; c = [-float(r["confidence"]) for r in rows]
        out.append(dict(set=k[0], condition=k[1], n=len(rows), own_error=mean(y), auroc_confidence_to_own_error=auroc([a for a, t in zip(c, y) if t], [a for a, t in zip(c, y) if not t])))
    return out


def term_distance_glossG(D, csv_path):
    if not csv_path or not os.path.exists(csv_path): return {"skipped": "term_meaning_difference.csv not given"}
    T = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    def fl(x):
        try: return float(x)
        except (TypeError, ValueError): return None
    G = {}
    for corp, f in (("v1", "v1_eqa.jsonl"), ("reddit", "reddit_eqa.jsonl"), ("defi", "defi_strict_eqa.jsonl")):
        for e in D.rows(f):
            rep = [int(c["bare"] == 0 and c["glossG"] == 1) for c in (q.get("correct") or {} for q in e["questions"]) if c.get("bare") is not None and c.get("glossG") is not None]
            if rep: G[(corp, e["id"])] = mean(rep)
    DIV = {"narrower", "shifted", "opposite", "unknown"}; out = {}
    for corp in ("v1", "reddit", "defi"):
        rows = [r for r in T if r["corpus"] == corp and (corp, r["id"]) in G]; y = [G[(corp, r["id"])] for r in rows]
        sp = {k: spearman([fl(r.get(k)) for r in rows], y) for k in ("dist_zero", "dist_guess", "self_report", "contrast", "dp", "R")}
        dv = [G[(corp, r["id"])] for r in rows if r.get("tier") in DIV]; nd = [G[(corp, r["id"])] for r in rows if r.get("tier") == "none"]
        out[corp] = dict(spearman_with_source_definition_repair={k: dict(rho=v[0], n=v[1]) for k, v in sp.items()},
                         tier_divergent_repair=mean(dv), tier_none_repair=mean(nd), tier_auroc=auroc(dv, nd), n_div=len(dv), n_none=len(nd))
    out["note"] = "Reader = DeepSeek; repair = bare wrong and correct with the source definition (glossG). dp and contrast use the drafted gloss, to show version dependence."
    return out


def shared_budget_sim(D, frac=0.25):
    TF = {}
    for f in ("v1_weights.jsonl", "reddit_weights.jsonl"):
        for r in D.rows(f): TF[r["id"]] = ((r.get("labels") or {}).get("tf"), r.get("gloss_gold"))
    out = {}
    for corp, lp, eq in (("Synthetic/DeepSeek", "lpmc_v1.jsonl", "v1_eqa.jsonl"), ("Reddit/DeepSeek", "lpmc_reddit.jsonl", "reddit_eqa.jsonl")):
        for arm in ("glossC", "glossG"):
            LP, E = D.byid(lp), D.byid(eq); Q = defaultdict(list)
            for i, r in LP.items():
                e = E.get(i)
                if not e or not r.get("per_question"): continue
                for p, q in zip(r["per_question"], e["questions"]):
                    c = q.get("correct") or {}
                    if c.get("bare") is None or c.get(arm) is None: continue
                    Q[i].append(dict(dp=p["glossC"]["p_correct"] - p["bare"]["p_correct"], net=c[arm] - c["bare"]))
            for swap in (False, True):
                U = []
                for t, qs in Q.items():
                    tf, d = TF.get(t, (None, None))
                    try: tf = float(tf)
                    except (TypeError, ValueError): tf = None
                    if len(qs) < 2 or not tf or not d: continue
                    A, B = (qs[1::2], qs[0::2]) if swap else (qs[0::2], qs[1::2])
                    U.append(dict(tf=tf, cost=len(d.split()), dpA=mean([x["dp"] for x in A]), val=tf * mean([x["net"] for x in B])))
                budget = frac * sum(u["cost"] for u in U)
                def pick(key):
                    tot = sp = 0
                    for u in sorted(U, key=key, reverse=True):
                        if sp + u["cost"] <= budget: sp += u["cost"]; tot += u["val"]
                    return tot
                o = pick(lambda u: u["val"] / u["cost"]); a = pick(lambda u: u["tf"] * max(u["dpA"], 0) / u["cost"]); b = pick(lambda u: u["tf"] / u["cost"])
                out[f"{corp}|B arm={arm}|{'swap' if swap else 'orig'}"] = dict(terms=len(U), freq_dp_cost_share_of_oracle=a / o, freq_cost_share_of_oracle=b / o, diff_share_of_total_tf=(a - b) / sum(u["tf"] for u in U))
    out["note"] = "A-side dp is the drafted-gloss proxy score. Only glossG rows use the source entry for B; glossC rows mix versions (cost priced on the source entry) and document the correction."
    return out


def stable_errors(recovered_dir):
    p = os.path.join(recovered_dir or "", "unc_v1_raw_samples.jsonl")
    if not os.path.exists(p): return {"skipped": "unc_v1_raw_samples.jsonl not found"}
    U = [json.loads(l) for l in open(p, encoding="utf-8")]; ex = FULL_SYNTHETIC_EXCL
    def st(rows):
        f = [r for r in rows if r["greedy"] is not None and r["greedy"] != r["gold"]]
        same = [r for r in f if None not in r["samples"] and len(set(r["samples"])) == 1]
        sw = [r for r in same if r["samples"][0] != r["gold"]]
        return dict(questions=len(rows), greedy_errors=len(f), ten_identical=len(same), ten_identical_wrong=len(sw), share=len(sw) / len(f))
    return dict(archived=st(U), excluding_two_conflict_items=st([r for r in U if (r["id"], r["qi"]) not in ex]))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--recovered", default=None)
    ap.add_argument("--term-csv", default=None); ap.add_argument("--out", default="offline_checks_results.json"); a = ap.parse_args()
    D = Data(a.data)
    res = dict(table2_duplicate_rows=table2_duplicate_rows(D), reader_to_reader=reader_to_reader(D), r_by_category=r_by_category(D), control_arms=control_arms(D),
               leakage=leakage(D), rag_leave_one_out=rag_leave_one_out(D), jev_self_error=jev_self_error(D), term_distance_glossG=term_distance_glossG(D, a.term_csv),
               shared_budget_sim=shared_budget_sim(D), stable_errors=stable_errors(a.recovered))
    json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False); print("wrote", a.out)


if __name__ == "__main__":
    main()
