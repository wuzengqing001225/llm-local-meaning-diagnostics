#!/usr/bin/env python3
"""Reviewer controls added 2026-09-26. Offline; reads released data only.

Usage (from the package root):
  python3 analysis/reviewer_controls/reviewer_controls_20260926.py \
      --root . --option-dist analysis/reviewer_controls/qwen7b_option_dist.jsonl \
      --out analysis/reviewer_controls/reviewer_controls_results.json

Sections of the output JSON:
  stability_by_class        greedy errors, identical-wrong, all-correct and majority-wrong counts by designed term class (761 questions)
  detection_by_class        AUROC [95% CI] of key-free reader signals, key-free proxy uncertainty and keyed proxy R, by class (456 questions)
  keyless_proxy             key-free proxy scores against DeepSeek V4 Flash and GPT-6-astra errors, and reproduction check of stored p_correct
  definition_arms_no_cue    four-arm synthetic accuracy on questions where no option is singled out by word overlap with any arm's text
  jev_761                   Jev confidence -> own error on the 761-question synthetic frame (both source-conflict items excluded)
  retrieval_definition_rate share of CUAD RAG questions whose retrieved passages contain the definition, per retriever
  territory_percentile      percentile of the Territory example in the 6,529-question CUAD risk frame
  error_nesting             share of GPT-6-astra errors also made by an older reader, on questions answered by all readers of a corpus
  redefinition_follow       Inverse Scaling redefine task (1,244 items): rate of following a stated redefinition, and of answering by usual meaning without it
  example_cases             GPT-5.6-terra outcomes and risk percentiles for the contract examples in the paper's example table
The key-free proxy distribution file is produced by proxy_option_dist.py (Qwen2.5-7B, same prompt as scripts/run_logprob_mc.py).
"""
import argparse, json, math, os, random, re
from collections import Counter, defaultdict

EX1 = {("v1:desk:interest", 1)}
EX2 = {("v1:desk:interest", 1), ("v1:desk:interest@mix0.7", 0)}
STOPW = set("the a an of to and or any in on for by is it its be as with that this which from at their they them are was were has have had not no but if then than such so do does did can may will would should could into over under about more most less very also only just all each other some one two three there here when where who whom what why how you your our we he she his her i me my us".split())


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else float("nan")


def auroc(pos, neg):
    if not pos or not neg: return float("nan")
    allv = sorted([(x, 1) for x in pos] + [(x, 0) for x in neg]); ranks = {}; i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]: j += 1
        for k in range(i, j + 1): ranks.setdefault(allv[i][0], (i + j) / 2 + 1)
        i = j + 1
    rp = sum(ranks[x] for x in pos)
    return (rp - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def boot(keys, score, fail, B=2000, seed=0):
    g = defaultdict(list)
    for k in keys: g[k[0]].append(k)
    T = list(g); rng = random.Random(seed); v = []
    for _ in range(B):
        s = [k for t in (rng.choice(T) for _ in T) for k in g[t]]
        p = [score(k) for k in s if fail[k]]; n = [score(k) for k in s if not fail[k]]
        if p and n: v.append(auroc(p, n))
    v.sort(); return [v[int(.025 * len(v))], v[int(.975 * len(v)) - 1]]


class Data:
    def __init__(self, root):
        self.idx = {}
        for dp, _, fs in sorted(os.walk(root)):
            for f in fs:
                if f.startswith("._"): continue
                p = os.path.join(dp, f)
                if f not in self.idx or ("raw_outputs" in p and "raw_outputs" not in self.idx[f]): self.idx[f] = p
    def rows(self, f): return [json.loads(l) for l in open(self.idx[f], encoding="utf-8")]
    def by_id(self, f): return {r["id"]: r for r in self.rows(f)}


def fails(E):
    return {(i, j): 1 - q["correct"]["bare"] for i, e in E.items() for j, q in enumerate(e["questions"]) if (q.get("correct") or {}).get("bare") is not None}


def overlap(gloss, opt, term):
    tw = set(re.findall(r"[a-z0-9]+", term.lower()))
    cw = lambda t: {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if len(w) > 2 and w not in STOPW and w not in tw}
    o = cw(opt); return len(o & cw(gloss)) / len(o) if o else 0.0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="."); ap.add_argument("--option-dist", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    D = Data(a.root); res = {}
    W = D.by_id("v1_weights.jsonl"); quad = {i: (w.get("labels") or {}).get("quadrant") for i, w in W.items()}
    cls = lambda i: quad.get(i.split("@")[0])
    CLASSES = [("prior_conflict", "redefined common word"), ("no_prior", "coinage"), ("prior_consistent", "usual meaning"), (None, "all")]
    # stability
    U = [json.loads(l) for l in open(D.idx["unc_v1_raw_samples.jsonl"], encoding="utf-8")]
    for r in U:
        if isinstance(r["samples"], str): r["samples"] = json.loads(r["samples"].replace("'", '"').replace("None", "null"))
        r["qi"] = int(r["qi"])
    U = [r for r in U if (r["id"], r["qi"]) not in EX2]
    st = {}
    for c, nm in CLASSES:
        rows = [r for r in U if c is None or cls(r["id"]) == c]; f = [r for r in rows if r["greedy"] is not None and r["greedy"] != r["gold"]]
        full = lambda r: [x for x in r["samples"] if x]
        st[nm] = dict(questions=len(rows), greedy_errors=len(f),
                      identical_wrong=sum(len(full(r)) == 10 and len(set(full(r))) == 1 and full(r)[0] != r["gold"] for r in f),
                      all_ten_correct=sum(len(full(r)) == 10 and all(x == r["gold"] for x in full(r)) for r in f),
                      majority_wrong=sum(Counter(full(r)).most_common(1)[0][0] != r["gold"] for r in f if full(r)))
    res["stability_by_class"] = st
    # detection
    LP = D.by_id("lpmc_v1.jsonl"); E1 = D.by_id("v1_eqa.jsonl"); EG = D.by_id("astra6_v1_eqa.jsonl"); F1, FG = fails(E1), fails(EG)
    UQ = {}
    for r in D.rows("unc_v1.jsonl"):
        for j, pq in enumerate(r["per_question"]): UQ[(r["id"], j)] = pq
    KD = {}
    for l in open(a.option_dist):
        r = json.loads(l); KD[(r["id"], r["j"])] = r
    R = {(i, j): 1 - p["bare"]["p_correct"] for i, r in LP.items() for j, p in enumerate(r["per_question"])}
    keys = [k for k in R if k in UQ and k in F1 and k in KD and k not in EX1]
    gold = lambda k: "ABCD".index(KD[k]["gold"])
    S = {"sample_disagreement": lambda k: float(UQ[k]["consistency"]), "option_entropy": lambda k: float(UQ[k]["mc_entropy"]),
         "stated_confidence": lambda k: -float(UQ[k]["verb_conf"]), "proxy_one_minus_max_prob_keyfree": lambda k: 1 - max(KD[k]["probs"]),
         "proxy_entropy_keyfree": lambda k: -sum(p * math.log(p) for p in KD[k]["probs"] if p > 0), "proxy_R_keyed": lambda k: R[k]}
    det = {}
    for c, nm in CLASSES:
        ks = [k for k in keys if c is None or cls(k[0]) == c]; det[nm] = {"errors": sum(F1[k] for k in ks), "questions": len(ks)}
        for sn, f in S.items():
            det[nm][sn] = [auroc([f(k) for k in ks if F1[k]], [f(k) for k in ks if not F1[k]])] + boot(ks, f, F1)
    res["detection_by_class"] = det
    diffs = [abs(KD[k]["probs"][gold(k)] - LP[k[0]]["per_question"][k[1]]["bare"]["p_correct"]) for k in KD if k[0] in LP and k[1] < len(LP[k[0]]["per_question"])]
    kg = [k for k in keys if k in FG]
    res["keyless_proxy"] = dict(reproduction_max_abs_diff_p_correct=max(diffs), n_scored=len(KD),
        gpt6={sn: [auroc([f(k) for k in kg if FG[k]], [f(k) for k in kg if not FG[k]])] + boot(kg, f, FG) for sn, f in S.items() if sn.startswith("proxy")},
        gpt6_redefined={sn: auroc([f(k) for k in kg if FG[k] and cls(k[0]) == "prior_conflict"], [f(k) for k in kg if not FG[k] and cls(k[0]) == "prior_conflict"]) for sn, f in S.items() if sn.startswith("proxy")})
    # definition arms without lexical cues
    rows4 = []
    for i, e in E1.items():
        w = W.get(i)
        if not w: continue
        for j, q in enumerate(e["questions"]):
            if (i, j) in EX2 or not q.get("options") or not q.get("answer"): continue
            c = q.get("correct") or {}
            if any(c.get(x) is None for x in ("bare", "glossG", "glossC", "glossM")): continue
            k = "ABCD".index(str(q["answer"]).strip().upper()[0])
            def flag(g):
                s = [overlap(g or "", o, e["term"]) for o in q["options"]]; t = max(s); return s[k] == t and s.count(t) == 1 and t > 0
            rows4.append(dict(c=c, cue=flag(w.get("gloss_gold")) or flag(w.get("gloss_used")) or flag(w.get("prior_guess") or w.get("prior_form_guess"))))
    def arms(sub):
        o = {"n": len(sub), "bare_acc": mean([r["c"]["bare"] for r in sub])}
        for x in ("glossG", "glossC", "glossM"):
            o[x] = dict(acc=mean([r["c"][x] for r in sub]), repairs=sum(r["c"]["bare"] == 0 and r["c"][x] == 1 for r in sub), harms=sum(r["c"]["bare"] == 1 and r["c"][x] == 0 for r in sub))
        return o
    res["definition_arms_no_cue"] = dict(all=arms(rows4), no_cue=arms([r for r in rows4 if not r["cue"]]), legend="glossG source definition, glossC model-drafted gloss, glossM model's own gloss under a domain prompt")
    # Jev on the 761 frame
    J = D.rows("jev_answers.jsonl"); jv = {}
    for cd in ("bare", "glossC"):
        rr = [r for r in J if r["set"] == "v1" and r["cond"] == cd and (r["id"], int(r["qidx"])) not in EX2 and r.get("correct") not in (None, "", "None") and r.get("confidence") not in (None, "", "None")]
        y = [1 - int(float(r["correct"])) for r in rr]; cf = [-float(r["confidence"]) for r in rr]
        jv[cd] = dict(n=len(rr), own_error=mean(y), auroc=auroc([x for x, t in zip(cf, y) if t], [x for x, t in zip(cf, y) if not t]))
    res["jev_761"] = jv
    # retrieval definition rate
    res["retrieval_definition_rate"] = {f: mean([int(float(r["def_retrieved"])) for r in D.rows(f) if r["arm"] == "rag"]) for f in ("rag_v3_bm25.jsonl", "rag_v3_t2.jsonl", "rag_v3_t1.jsonl") if f in D.idx}
    # Territory percentile
    LF = D.rows("lpmc_full.jsonl"); risks = [1 - p["bare"]["p_correct"] for r in LF for p in (r.get("per_question") or []) if "bare" in p]
    tr = next(1 - p["bare"]["p_correct"] for r in LF if r["id"] == "cuadfull:167:Territory" for p in r["per_question"] if str(p.get("ctx_idx")) == "3")
    res["territory_percentile"] = dict(risk=tr, percentile=sum(v <= tr for v in risks) / len(risks), frame=len(risks))
    # error nesting across readers
    SETS = {"Synthetic": [("DeepSeek V4 Flash", "v1_eqa.jsonl"), ("GPT-6-astra", "astra6_v1_eqa.jsonl")],
            "Reddit": [("DeepSeek V4.1 Flash", "reddit_eqa.jsonl"), ("GPT-6-astra", "astra6_reddit_eqa.jsonl")],
            "DeFi": [("DeepSeek V4.1 Flash", "defi_strict_eqa.jsonl"), ("GPT-5.6-terra", "defi_strict_eqa_gpt.jsonl"), ("GPT-6-astra", "astra6_defi_strict_eqa.jsonl")]}
    nest = {}
    for c, rd in SETS.items():
        F = {n: {k: v for k, v in fails(D.by_id(f)).items() if k not in EX2} for n, f in rd}
        ks = set.intersection(*[set(v) for v in F.values()]); newest = rd[-1][0]; ne = [k for k in ks if F[newest][k]]
        nest[c] = dict(questions=len(ks), error_rates={n: mean([F[n][k] for k in ks]) for n, _ in rd}, newest_errors=len(ne),
                       also_wrong_for_an_older_reader=sum(any(F[o][k] for o, _ in rd[:-1]) for k in ne))
    res["error_nesting"] = nest
    red = {}
    for nm, f in (("GPT-5.6-terra", "redefine_gpt56.jsonl"), ("GPT-6-astra", "redefine_astra6.jsonl"), ("DeepSeek V4.1 Flash", "redefine_ds41.jsonl")):
        R_ = D.rows(f); red[nm] = dict(items=len(R_), follow_stated=mean([int(r["given"] == r["gold"]) for r in R_]), usual_meaning_without=mean([int(r["bare"] != r["gold"]) for r in R_]))
    res["redefinition_follow"] = red
    T2 = D.rows("t2_answers.jsonl"); T2m = {(e["id"], str(q["ctx_idx"])): q for e in T2 for q in e["questions"]}
    P = {(r["id"], str(p["ctx_idx"])): 1 - p["bare"]["p_correct"] for r in LF for p in (r.get("per_question") or []) if "bare" in p}
    res["example_cases"] = {f"{t}#{c}": dict(correct=T2m[(t, c)]["correct"], risk=P[(t, c)], percentile=sum(v <= P[(t, c)] for v in risks) / len(risks))
                            for t, c in (("cuadfull:355:Products", "7"), ("cuadfull:379:Trademarks", "2"), ("cuadfull:86:Term", "5"), ("cuadfull:167:Territory", "3"))}
    json.dump(res, open(a.out, "w"), indent=1); print("wrote", a.out)


if __name__ == "__main__":
    main()
