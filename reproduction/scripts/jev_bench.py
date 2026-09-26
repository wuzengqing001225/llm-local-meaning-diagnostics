#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jev (TypeSafe System One model) x silent misreading: two questions, one run.
  As reader: choice-task failure rate under bare / glossC / glossM conditions; whether RLCD-calibrated confidence can distinguish its own misreadings (by channel).
  As proxy: AUROC of 1-P(correct option) under bare condition predicting other readers' (DeepSeek / GPT / Astra / Sonnet) failure on the same questions; compared against Qwen-7B proxy.
Interface (official): POST https://api.typesafe.ai/v1/systemone  body={model:"jev-latest", state, questions:{answer:{type:"choice", instructions, options:[...]}}}
      Gateway: OpenRouter POST /api/alpha/decisions (model typesafe/jev-latest); AIMLAPI POST /v1/decisions (model typesafe/jev) -- specify with --path / --model
      Field names may differ slightly across gateways -- run --probe first to print one raw response; the script parses several common key names (choice/selected/answer, probabilities/probs, confidence).
Usage:
  export JEV_API_KEY=...  JEV_BASE_URL=https://api.typesafe.ai   (or gateway URL, e.g. https://tokenra.io / https://api.aimlapi.com)
  python3 jev_bench.py --probe                                   # look at one first
  python3 jev_bench.py --out jev_answers.jsonl                   # full question set, three conditions (~3.9k questions x 3 ~= 11.7k calls, cost negligible)
  python3 jev_bench.py --analyze jev_answers.jsonl               # produce two tables
"""
import argparse, json, os, sys, time, math, random
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
SETS = {  # name: (eqa, weights, other readers' eqa on the SAME questions, qwen proxy lpmc)
    "v1":     ("data/v1_eqa.jsonl",     "data/v1_weights.jsonl",     {"DeepSeek": "data/v1_eqa.jsonl", "Sonnet": "data/eqa_v1_sonnet_samequestions.jsonl", "Astra6": "data/astra6_v1_eqa.jsonl"}, "data/lpmc_v1.jsonl"),
    "cuad":   ("data/cuad_eqa.jsonl",   "data/cuad_weights.jsonl",   {"DeepSeek": "data/cuad_eqa.jsonl"}, "data/lpmc_cuad_v2.jsonl"),
    "reddit": ("data/reddit_eqa.jsonl", "data/reddit_weights.jsonl", {"DeepSeek": "data/reddit_eqa.jsonl", "Astra6": "data/astra6_reddit_eqa.jsonl"}, "data/lpmc_reddit.jsonl"),
}
def L(p): return {json.loads(l)["id"]: json.loads(l) for l in open(p, encoding="utf-8")} if os.path.exists(p) else {}
PATH = "/v1/systemone"
LET = ["A", "B", "C", "D"]
def call(base, key, model, state, options, timeout=60):
    # Official schema: questions.<id> = {type:"choice", instructions, criteria:{key: description}}; response answers.<id> = {choice, probabilities:{key: p}, confidence}
    body = {"model": model, "state": state, "questions": {"answer": {"type": "choice", "instructions": "Which option correctly answers the question in the state?",
            "criteria": {LET[i]: o for i, o in enumerate(options)}}}}
    req = urllib.request.Request(base.rstrip("/") + PATH, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "tfpd-jev-bench/0.1"})
    for att in range(5):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504): time.sleep(2 * (att + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]}")
        except Exception: time.sleep(2 * (att + 1))
    raise RuntimeError("gave up")
def parse(resp, options):
    """Returns (probs[4] in the same order as options, confidence, chosen_index). Compatible with several key name variants."""
    a = resp.get("answers", resp).get("answer", resp.get("answers", resp))
    if isinstance(a, dict) and "answer" in a and isinstance(a["answer"], dict): a = a["answer"]
    probs = None
    for k in ("probabilities", "probs", "distribution", "option_probabilities"):
        if k in a: probs = a[k]; break
    if isinstance(probs, dict): probs = [float(probs.get(o, probs.get(str(i), 0.0))) for i, o in enumerate(options)]
    elif isinstance(probs, list) and probs and isinstance(probs[0], dict):
        d = {x.get("option", x.get("value", x.get("label"))): float(x.get("probability", x.get("p", 0))) for x in probs}; probs = [d.get(o, 0.0) for o in options]
    conf = None
    for k in ("confidence", "conf", "certainty"):
        if k in a: conf = float(a[k]); break
    chosen = None
    for k in ("choice", "selected", "value", "option", "answer"):
        if k in a and isinstance(a[k], (str, int)):
            v = a[k]; chosen = options.index(v) if v in options else (int(v) if isinstance(v, int) and 0 <= v < len(options) else None); break
    if chosen is None and probs: chosen = max(range(len(options)), key=lambda i: probs[i])
    return probs, conf, chosen
def build_state(q, prefix): return (prefix + "\n\n" if prefix else "") + q["q"]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("JEV_BASE_URL", "https://api.typesafe.ai")); ap.add_argument("--model", default=os.environ.get("JEV_MODEL", "jev-latest")); ap.add_argument("--path", default=os.environ.get("JEV_PATH", "/v1/systemone"))
    ap.add_argument("--sets", default="v1,cuad,reddit"); ap.add_argument("--conditions", default="bare,glossC,glossM"); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8); ap.add_argument("--probe", action="store_true"); ap.add_argument("--out", default=None); ap.add_argument("--analyze", default=None)
    a = ap.parse_args()
    global PATH; PATH = a.path
    if a.analyze: return analyze(a.analyze)
    key = os.environ.get("JEV_API_KEY"); assert key, "export JEV_API_KEY=..."
    jobs = []
    for s in a.sets.split(","):
        eqa_p, w_p, _, _ = SETS[s]; E, W = L(eqa_p), L(w_p)
        for i, e in E.items():
            if e.get("n_q", 0) == 0: continue
            w = W.get(i, {}); gC = w.get("gloss_used") or w.get("gloss_gold") or e.get("gloss_gold"); gM = w.get("prior_guess")
            for j, q in enumerate(e["questions"]):
                for cond in a.conditions.split(","):
                    if cond == "glossC" and not gC: continue
                    if cond == "glossM" and (not gM or w.get("prior_unknown")): continue
                    prefix = {"bare": "", "glossC": f"Definition used in this corpus: \"{e['term']}\" means {gC}", "glossM": f"Definition: \"{e['term']}\" means {gM}"}[cond]
                    jobs.append(dict(set=s, id=i, term=e["term"], qidx=j, cond=cond, state=build_state(q, prefix), options=q["options"], answer=str(q["answer"]).strip().upper()[:1],
                                     channel=w.get("channel"), quadrant=(e.get("labels") or {}).get("quadrant"), other_bare=(q.get("correct") or {}).get("bare")))
    if a.limit: jobs = jobs[: a.limit]
    if a.probe:
        j = jobs[0]; resp = call(a.base, key, a.model, j["state"], j["options"]); print(json.dumps(resp, ensure_ascii=False, indent=1)[:2500])
        print("\nparsed:", parse(resp, LET[:len(j["options"])]), "| gold:", j["answer"]); return
    done = set()
    if a.out and os.path.exists(a.out):
        for l in open(a.out, encoding="utf-8"):
            r = json.loads(l); done.add((r["set"], r["id"], r["qidx"], r["cond"]))
    jobs = [j for j in jobs if (j["set"], j["id"], j["qidx"], j["cond"]) not in done]
    print(f"[jev] {len(jobs)} calls to make (already done {len(done)})", file=sys.stderr)
    out = open(a.out, "a", encoding="utf-8"); n = 0
    def work(j):
        try:
            resp = call(a.base, key, a.model, j["state"], j["options"]); probs, conf, ch = parse(resp, LET[:len(j["options"])])
            gold = "ABCD".index(j["answer"]); pc = probs[gold] if probs else None
            return dict(j, probs=probs, confidence=conf, chosen=("ABCD"[ch] if ch is not None else None), correct=int(ch == gold) if ch is not None else None, p_correct=pc, raw=None)
        except Exception as ex: return dict(j, error=str(ex)[:200])
    with ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(work, jobs):
            r.pop("state", None); out.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
            if n % 100 == 0: out.flush(); print(f"\r[jev] {n}/{len(jobs)}", end="", file=sys.stderr)
    out.close(); print(f"\n[done] → {a.out}", file=sys.stderr); analyze(a.out)
def auroc(pos, neg): return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg)) if pos and neg else float("nan")
def analyze(path):
    m = lambda v: sum(v) / len(v) if v else float("nan")
    R = [json.loads(l) for l in open(path, encoding="utf-8")]; R = [r for r in R if r.get("correct") is not None]
    print(f"\n=== Jev as reader ({len(R)} valid rows; error rows {sum(1 for l in open(path) if 'error' in l)})")
    print(f"{'set':7s} {'cond':7s} {'n':>5s} {'fail':>6s} | conf→own-fail AUROC | conflict-ch AUROC | 1−P(chosen)→own-fail")
    for s in SETS:
        for cond in ("bare", "glossC", "glossM"):
            rr = [r for r in R if r["set"] == s and r["cond"] == cond]
            if not rr: continue
            fails = [1 - r["correct"] for r in rr]
            conf_a = auroc([-r["confidence"] for r in rr if r["confidence"] is not None and r["correct"] == 0], [-r["confidence"] for r in rr if r["confidence"] is not None and r["correct"] == 1])
            cf = [r for r in rr if (r.get("channel") == "conflict" or r.get("quadrant") == "prior_conflict") and r["confidence"] is not None]
            conf_c = auroc([-r["confidence"] for r in cf if r["correct"] == 0], [-r["confidence"] for r in cf if r["correct"] == 1])
            pmax = auroc([1 - max(r["probs"]) for r in rr if r["probs"] and r["correct"] == 0], [1 - max(r["probs"]) for r in rr if r["probs"] and r["correct"] == 1])
            print(f"{s:7s} {cond:7s} {len(rr):5d} {m(fails):6.3f} | {conf_a:19.3f} | {conf_c:17.3f} (n={len(cf)}) | {pmax:.3f}")
    print("\n=== Jev as proxy (bare condition 1-P(correct option) -> other readers' failure on same question)")
    print(f"{'set':7s} {'reader':9s} {'n':>5s} {'AUROC Jev':>9s} {'AUROC Qwen-7B':>13s}  Calibration (Jev risk bin -> reader failure rate <.2/.2-.5/.5-.8/>.8)")
    for s, (eqa_p, w_p, others, lp_p) in SETS.items():
        base = {(r["id"], r["qidx"]): r for r in R if r["set"] == s and r["cond"] == "bare" and r.get("p_correct") is not None}
        LP = L(lp_p)
        for name, p in others.items():
            E = L(p); qp = []; qq = []
            for (i, j), r in base.items():
                e = E.get(i)
                if not e or j >= len(e.get("questions", [])): continue
                c = (e["questions"][j].get("correct") or {}).get("bare")
                if c is None: continue
                qp.append((1 - r["p_correct"], c))
                lp = LP.get(i, {}).get("per_question", [])
                if j < len(lp) and "bare" in lp[j]: qq.append((1 - lp[j]["bare"]["p_correct"], c))
            if not qp: continue
            aj = auroc([x for x, c in qp if c == 0], [x for x, c in qp if c == 1]); aq = auroc([x for x, c in qq if c == 0], [x for x, c in qq if c == 1])
            cal = [m([1 - c for x, c in qp if lo <= x < hi]) for lo, hi in ((0, .2), (.2, .5), (.5, .8), (.8, 1.01))]
            print(f"{s:7s} {name:9s} {len(qp):5d} {aj:9.3f} {aq:13.3f}  " + " / ".join(f"{x:.2f}" for x in cal) + f"   (Qwen n={len(qq)})")
    print("\nPre-registration: reader-side H1 Jev bare failure rate is same order of magnitude as DeepSeek on the same questions (0.25-0.35); H2 its calibrated confidence AUROC for its own misreadings <=0.65, conflict channel <=0.55 (RLCD calibration cannot detect prior override);")
    print("      proxy-side H3 Jev-as-proxy AUROC falls at/below the Qwen-7B band (0.72-0.92) -- if significantly higher, this indicates RLCD probabilities track reader failure more closely than raw logits, upgrading the API proxy tier.")
if __name__ == "__main__":
    main()