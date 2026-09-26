#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Q16 context gate: computes proxy bare risk 1-P(correct) for standard (standard-sense questions with updated terminology) and distractor items, for gate simulation.
Usage: python3 score_standard_risk.py --terms data/v1_mains.jsonl --distractor data/v1_distractor_qa.jsonl \
        --updateset carriers_deepseek_v1_updateset.json --model Qwen/Qwen2.5-7B --out standard_risk_qwen7b.jsonl
Approx. 75 forward passes; one to two minutes on MPS."""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from carriers_common import load, fmt_opts, MC_SYSTEM

@torch.no_grad()
def option_logprobs(tok, model, prompt, n_opt, device):
    ids = tok(prompt, return_tensors="pt").to(device)
    lp = torch.log_softmax(model(**ids).logits[0, -1].float(), -1)
    out = []
    for i in range(n_opt):
        cands = [tok.encode(" " + chr(65 + i), add_special_tokens=False), tok.encode(chr(65 + i), add_special_tokens=False)]
        out.append(max(lp[c[0]].item() for c in cands if c))
    return out

ap = argparse.ArgumentParser()
ap.add_argument("--terms", required=True); ap.add_argument("--distractor", required=True); ap.add_argument("--updateset", required=True)
ap.add_argument("--model", default="Qwen/Qwen2.5-7B"); ap.add_argument("--dtype", default="bfloat16"); ap.add_argument("--out", required=True)
a = ap.parse_args()
device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
if device == "mps" and a.dtype == "bfloat16": a.dtype = "float16"
tok = AutoTokenizer.from_pretrained(a.model); model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype)).to(device).eval()
U = json.load(open(a.updateset)); T = {r["id"]: r for r in load(a.terms)}
qs = []
for i in U:
    for q in T.get(i, {}).get("qa", []):
        if q.get("sense") == "standard":
            qs.append({"set": "standard", "id": i, "term": T[i]["term"], "q": q["question"], "options": q["options"], "answer": q["answer"]})
for q in load(a.distractor):
    qs.append({"set": "distractor", "id": None, "term": None, "q": q["question"], "options": q["options"], "answer": q["answer"]})
with open(a.out, "w", encoding="utf-8") as f:
    for k, q in enumerate(qs):
        lps = option_logprobs(tok, model, MC_SYSTEM + "\n\n" + q["q"] + "\n" + fmt_opts(q["options"]) + "\nANSWER_LETTER:", len(q["options"]), device)
        z = math.log(sum(math.exp(x) for x in lps)); gold = ord(q["answer"]) - 65
        f.write(json.dumps({"set": q["set"], "id": q["id"], "term": q["term"], "idx": k, "risk": 1 - math.exp(lps[gold] - z), "q": q["q"][:80]}, ensure_ascii=False) + "\n")
print(f"[done] {len(qs)} → {a.out}", file=sys.stderr)