#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q14 occurrence-level A/B (v0.7): answer usage-instantiated questions (run_eqa --from-usage output) one by one:
  bare      question stem as-is
  inline    insert an in-context gloss note for the term before the stem ("Note: in these documents, "<term>" means <gloss_C>.")
  spill     insert a gloss note for **another** term (same corpus, high proxy risk) before the stem -- tests spillover from irrelevant notes
Output occ_ab.jsonl: each question {corpus, id, term, ctx_idx, risk(proxy 1-P), gold, bare, inline, spill?, spill_term}
"""
import argparse, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env


def parse_letter(o):
    s = (o or "").strip().upper()
    for ch in s:
        if ch in "ABCD":
            return ch
        if ch.isalpha():
            break
    return None

MC_SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only."
BARE = "{q}\n{opts}\nAnswer:"
NOTE = "Note: in these documents, \"{term}\" means {gloss}\n\n{q}\n{opts}\nAnswer:"

def fmt_opts(o):
    return "\n".join(f"{chr(65+i)}. {x}" for i, x in enumerate(o))

def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", nargs="+", required=True, help="corpus=eqa_usage.jsonl=lpmc_usage.jsonl=weights.jsonl triple")
    ap.add_argument("--n-spill", type=int, default=300, help="number of spillover-paired questions per corpus")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--cache-dir", default="data/cache")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    os.makedirs(a.cache_dir, exist_ok=True)
    reader = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    reqs, meta, rows = [], [], []
    for spec in a.sets:
        corpus, ep, lp, wp = spec.split("=")
        E = {r["id"]: r for r in load(ep)}; L = {r["id"]: r for r in load(lp)}; W = {r["id"]: r for r in load(wp)}
        occ = []
        for i, e in E.items():
            if e.get("labels", {}).get("variant", "main") != "main" or e["n_q"] == 0 or i not in L:
                continue
            g = (W.get(i, {}).get("gloss_used") or e.get("gloss_gold") or "").strip()
            if not g:
                continue
            for q, pq in zip(e["questions"], L[i]["per_question"]):
                if "bare" not in pq:
                    continue
                occ.append(dict(corpus=corpus, id=i, term=e["term"], ctx_idx=q.get("ctx_idx"), risk=1 - pq["bare"]["p_correct"], gold=q["answer"],
                                q=q["q"], opts=fmt_opts(q["options"]), gloss=g))
        # High-risk term pool (top 25% by term-level proxy risk), used as source for spillover notes
        trisk = sorted(((L[i]["fail_pred_bare"], i) for i in L if i in E and E[i].get("labels", {}).get("variant", "main") == "main"), reverse=True)
        pool = [i for _, i in trisk[: max(5, len(trisk) // 4)]]
        spill_idx = set(rng.sample(range(len(occ)), min(a.n_spill, len(occ))))
        base = len(rows)
        for k0, o in enumerate(occ):
            k = base + k0
            reqs.append(dict(prompt=BARE.format(q=o["q"], opts=o["opts"]), system=MC_SYSTEM, max_tokens=24)); meta.append((k, "bare"))
            reqs.append(dict(prompt=NOTE.format(term=o["term"], gloss=o["gloss"], q=o["q"], opts=o["opts"]), system=MC_SYSTEM, max_tokens=24)); meta.append((k, "inline"))
            if k0 in spill_idx:
                cands = [i for i in pool if i != o["id"]]
                x = rng.choice(cands); gx = (W.get(x, {}).get("gloss_used") or E[x].get("gloss_gold") or "").strip()
                o["spill_term"] = E[x]["term"]
                reqs.append(dict(prompt=NOTE.format(term=E[x]["term"], gloss=gx, q=o["q"], opts=o["opts"]), system=MC_SYSTEM, max_tokens=24)); meta.append((k, "spill"))
        rows.extend(occ)
        print(f"[{corpus}] occurrences={len(occ)} spill={len(spill_idx)} pool={len(pool)}", file=sys.stderr)
    outs = []
    for i in range(0, len(reqs), 200):
        outs.extend(reader.complete_many(reqs[i:i + 200]))
        print(f"\r[ab] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    for (k, cond), o in zip(meta, outs):
        rows[k][cond] = 1.0 if parse_letter(o) == rows[k]["gold"] else 0.0
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if k not in ("q", "opts", "gloss")}, ensure_ascii=False) + "\n")
    print(f"[done] {len(rows)} occurrences → {a.out}  reader_calls={len(reqs)}", file=sys.stderr)

if __name__ == "__main__":
    main()