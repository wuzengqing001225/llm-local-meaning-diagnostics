#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carrier comparison (API reader version): bare / ctx_full / ctx_retrieved conditions answering on target / neighbor / standard / distractor question sets.
Usage: python3 run_carriers.py --eqa-usage runs/local/deepseek/v1/eqa_usage.jsonl --weights runs/local/deepseek/v1/weights.jsonl \
        --terms data/v1/v1_mains.jsonl --distractor data/v1/v1_distractor_qa.jsonl --out out/carriers_sonnet.jsonl
Output one line per question: {set, id, term, carrier→correct, retrieved_n}
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env
from carriers_common import build_question_sets, prompt_for, fmt_opts, MC_SYSTEM


def parse_letter(o):
    for ch in (o or "").strip().upper():
        if ch in "ABCD":
            return ch
        if ch.isalpha():
            break
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eqa-usage", required=True); ap.add_argument("--weights", required=True)
    ap.add_argument("--terms", required=True); ap.add_argument("--distractor", required=True)
    ap.add_argument("--channel", default="conflict"); ap.add_argument("--out", required=True)
    ap.add_argument("--carriers", nargs="+", default=["bare", "ctx_full", "ctx_retrieved"])
    ap.add_argument("--shard", default=None, help="k/n: only process questions where index %% n == k (sharding to avoid single-session token limit)")
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--cache-dir", default="data/cache")
    a = ap.parse_args()
    os.makedirs(a.cache_dir, exist_ok=True)
    reader = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    U, sets = build_question_sets(a.eqa_usage, a.weights, a.terms, a.distractor, a.channel)
    qs = [q for k in ("target", "neighbor", "standard", "distractor") for q in sets[k]]
    if a.shard:
        k_, n_ = map(int, a.shard.split("/")); qs = [q for i, q in enumerate(qs) if i % n_ == k_]
    print(f"[carriers] update set={len(U)} terms; questions: " + ", ".join(f"{k}={len(v)}" for k, v in sets.items()), file=sys.stderr)
    reqs, meta = [], []
    for k, q in enumerate(qs):
        for c in a.carriers:
            prefix, hit = prompt_for(c, U, q)
            if c == "ctx_retrieved":
                q["retrieved_n"] = hit
            reqs.append(dict(prompt=f"{prefix}{q['q']}\n{fmt_opts(q['options'])}\nAnswer:", system=MC_SYSTEM, max_tokens=24)); meta.append((k, c))
    outs = []
    for i in range(0, len(reqs), 200):
        outs.extend(reader.complete_many(reqs[i:i + 200])); print(f"\r[carriers] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    for (k, c), o in zip(meta, outs):
        qs[k][c] = 1.0 if parse_letter(o) == qs[k]["answer"] else 0.0
    with open(a.out, "w", encoding="utf-8") as f:
        for q in qs:
            f.write(json.dumps({kk: v for kk, v in q.items() if kk not in ("q", "options", "answer")}, ensure_ascii=False) + "\n")
    json.dump({i: {"term": u["term"], "gloss": u["gloss"]} for i, u in U.items()}, open(a.out.replace(".jsonl", "_updateset.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[done] {len(qs)} questions × {len(a.carriers)} carriers → {a.out}  reader_calls={len(reqs)}", file=sys.stderr)


if __name__ == "__main__":
    main()