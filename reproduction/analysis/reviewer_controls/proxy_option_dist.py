#!/usr/bin/env python3
"""Score the proxy's full option distribution (no definition) on the synthetic diagnostic questions.
Same prompt and letter scoring as scripts/run_logprob_mc.py; writes all option log-probabilities so that
key-free scores (max probability, entropy) can be compared with the keyed score R = 1 - p(correct)."""
import argparse, json, math, sys, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only.\n\n"
def build(q): return SYSTEM + q["q"] + "\n" + "\n".join(f"{chr(65+i)}. {x}" for i, x in enumerate(q["options"])) + "\nANSWER_LETTER:"
ap = argparse.ArgumentParser(); ap.add_argument("--eqa"); ap.add_argument("--ids"); ap.add_argument("--out"); ap.add_argument("--model", default="Qwen/Qwen2.5-7B"); a = ap.parse_args()
keep = set(json.load(open(a.ids)))
tok = AutoTokenizer.from_pretrained(a.model); torch.set_num_threads(14)
model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32).eval()
rows = [json.loads(l) for l in open(a.eqa, encoding="utf-8")]; n = 0
with open(a.out, "w") as out, torch.no_grad():
    for r in rows:
        if r["id"] not in keep: continue
        for j, q in enumerate(r.get("questions") or []):
            ids = tok(build(q), return_tensors="pt"); lp = torch.log_softmax(model(**ids).logits[0, -1].float(), -1)
            lps = [max(lp[c[0]].item() for c in (tok.encode(" " + chr(65 + i), add_special_tokens=False), tok.encode(chr(65 + i), add_special_tokens=False)) if c) for i in range(len(q["options"]))]
            z = math.log(sum(math.exp(x) for x in lps)); probs = [math.exp(x - z) for x in lps]
            out.write(json.dumps({"id": r["id"], "j": j, "gold": q["answer"], "probs": probs}) + "\n"); out.flush(); n += 1
            if n % 25 == 0: print(n, file=sys.stderr, flush=True)
print("done", n, file=sys.stderr)
