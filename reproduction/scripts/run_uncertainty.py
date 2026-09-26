#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-3 uncertainty baseline comparison (EXP_UNCERTAINTY_BASELINES.md) + API proxy mode.

Mode 1 (default, baseline trio; reader reads from LLM_* env vars, DeepSeek recommended):
  For each question, sample bare condition T=1.0 --sample-k times + one verbal confidence follow-up, output per question:
    consistency  = 1 − max_vote/k     (self-consistency uncertainty)
    mc_entropy   = entropy of option distribution (nats)  (MC form of semantic entropy)
    verb_conf    = model self-reported 0–100 confidence (complement taken as score)
  python3 run_uncertainty.py --eqa runs/local/deepseek/v1/eqa.jsonl --out unc_v1.jsonl --sample-k 10

Mode 2 (--api-proxy; use a small API model as proxy, answering "must it be local white-box?"):
  For each question, answer bare/glossC once each with max_tokens=1 + top_logprobs=20, obtain
  P(A..D) from the answer letter's logprob, normalize and output p_correct — same shape as run_logprob_mc, directly usable in the comparison table.
  Requires LLM_MODEL to support logprobs (gpt-5.6-luna works). --terms provides gloss_gold as glossC.
  python3 run_uncertainty.py --eqa ... --api-proxy --terms data/v1/v1_mains.jsonl --out apiproxy_v1.jsonl

Resumable run: --cache-dir (cached by (id,qi,mode,rep) key).
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env

MC = "{q}\n{opts}\nANSWER_LETTER:"
MC_G = "Term note: {term}: {gloss}\n\n{q}\n{opts}\nANSWER_LETTER:"
CONF = "{q}\n{opts}\nYour answer was: {ans}. On a scale of 0-100, how confident are you that this answer is correct? Reply with the number only.\nCONFIDENCE:"
SYS = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only."

def fmt_opts(opts):
    return "\n".join(f"{'ABCD'[k]}. {o}" for k, o in enumerate(opts))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eqa", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--sample-k", type=int, default=10); ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--api-proxy", action="store_true"); ap.add_argument("--terms")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--cache-dir", default="data/cache_unc")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.cache_dir, exist_ok=True)
    cli = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "unc.jsonl"))
    E = [json.loads(l) for l in open(a.eqa, encoding="utf-8")]
    if a.limit: E = E[: a.limit]
    gloss = {}
    if a.terms:
        for l in open(a.terms, encoding="utf-8"):
            t = json.loads(l); gloss[t["id"]] = t.get("gloss_gold") or t.get("def_raw") or ""
    reqs, owners = [], []
    for e in E:
        for qi, q in enumerate(e.get("questions", [])):
            opts = fmt_opts(q["options"])
            if a.api_proxy:
                reqs.append(dict(prompt=MC.format(q=q["q"], opts=opts), system=SYS, max_tokens=1,
                                 temperature=0.0, logprobs=20))
                owners.append((e["id"], qi, "bare", 0))
                g = gloss.get(e["id"])
                if g:
                    reqs.append(dict(prompt=MC_G.format(term=e["term"], gloss=g[:400], q=q["q"], opts=opts),
                                     system=SYS, max_tokens=1, temperature=0.0, logprobs=20))
                    owners.append((e["id"], qi, "glossC", 0))
            else:
                for r in range(a.sample_k):
                    reqs.append(dict(prompt=MC.format(q=q["q"], opts=opts), system=SYS, max_tokens=4,
                                     temperature=a.temperature, seed=r))
                    owners.append((e["id"], qi, "sample", r))
    print(f"[unc] {len(reqs)} calls ({'api-proxy' if a.api_proxy else f'k={a.sample_k}'})", file=sys.stderr)
    outs = []
    for i in range(0, len(reqs), 200):
        outs.extend(cli.complete_many(reqs[i:i + 200]))
        print(f"\r[unc] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    got = {}
    for (tid, qi, mode, r), o in zip(owners, outs):
        got.setdefault((tid, qi), {}).setdefault(mode, {})[r] = o
    ED = {e["id"]: e for e in E}
    # Verbal confidence second round (uses first-sample answer)
    if not a.api_proxy:
        reqs2, owners2 = [], []
        for (tid, qi), d in got.items():
            q = ED[tid]["questions"][qi]
            ans = str(d["sample"][0]).strip().upper()[:1]
            reqs2.append(dict(prompt=CONF.format(q=q["q"], opts=fmt_opts(q["options"]), ans=ans), system=SYS,
                              max_tokens=6, temperature=0.0))
            owners2.append((tid, qi))
        outs2 = []
        for i in range(0, len(reqs2), 200):
            outs2.extend(cli.complete_many(reqs2[i:i + 200]))
            print(f"\r[conf] {min(i+200, len(reqs2))}/{len(reqs2)}", end="", file=sys.stderr)
        print(file=sys.stderr)
        conf = {k: v for k, v in zip(owners2, outs2)}
    with open(a.out, "w", encoding="utf-8") as f:
        for e in E:
            rows = []
            for qi, q in enumerate(e.get("questions", [])):
                d = got.get((e["id"], qi), {})
                gold = str(q.get("answer", "")).strip().upper()[:1]
                if a.api_proxy:
                    def pc(mode):
                        o = d.get(mode, {}).get(0)
                        if o is None: return None
                        try:
                            lps = o if isinstance(o, dict) else json.loads(o)
                            probs = {k[-1].upper(): math.exp(v) for k, v in lps.items() if k.strip().upper()[-1:] in "ABCD"}
                            z = sum(probs.values()) or 1.0
                            return probs.get(gold, 0.0) / z
                        except Exception:
                            s = str(o).strip().upper()[:1]
                            return 1.0 if s == gold else 0.0
                        return None
                    rows.append({"q": q["q"][:80], "bare": {"p_correct": pc("bare")},
                                 "glossC": {"p_correct": pc("glossC")}})
                else:
                    votes = [str(v).strip().upper()[:1] for v in d.get("sample", {}).values()]
                    votes = [v for v in votes if v in "ABCD"]
                    from collections import Counter
                    cnt = Counter(votes)
                    k = len(votes) or 1
                    ent = -sum((c/k) * math.log(c/k) for c in cnt.values())
                    cv = conf.get((e["id"], qi), "")
                    try: vc = max(0.0, min(100.0, float(str(cv).strip().split()[0]))) / 100.0
                    except Exception: vc = None
                    rows.append({"q": q["q"][:80], "consistency": 1 - (cnt.most_common(1)[0][1]/k if cnt else 0),
                                 "mc_entropy": ent, "verb_conf": vc, "majority": cnt.most_common(1)[0][0] if cnt else None,
                                 "votes": dict(cnt)})
            f.write(json.dumps({"id": e["id"], "term": e["term"], "n_q": len(rows),
                                "per_question": rows}, ensure_ascii=False) + "\n")
    print(f"[done] → {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()