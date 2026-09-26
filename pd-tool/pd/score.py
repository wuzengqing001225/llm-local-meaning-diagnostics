"""Score proposed question keys with a local white-box proxy under three conditions.

Conditions: no definition (bare), the document's definition (def), and the proxy's own gloss of the term (own) if supplied.
Output per occurrence:
  p_bare, p_def[, p_own]   probability the proxy assigns to the keyed option (softmax over the four option letters)
  risk = 1 - p_bare        predicted misread risk; pd = p_def - p_bare  prior divergence
  channel                  heuristic threshold label, not an adjudicated semantic mechanism
  repairable               heuristic p_def >= 0.75, not an observed reader repair
"""
import math, sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only.\n\n"
OWN_GLOSS_PROMPT = "In internal documents of an organisation the word \"{term}\" is used. In one sentence, what does \"{term}\" most likely mean there?\nAnswer:"

def _fmt(o): return "\n".join(f"{chr(65 + i)}. {x}" for i, x in enumerate(o))
def build_prompt(q, term, gloss=None):
    head = f"Term note: {term}: {gloss}\n\n" if gloss else ""
    return SYSTEM + head + q["q"] + "\n" + _fmt(q["options"]) + "\nANSWER_LETTER:"

class Proxy:
    def __init__(self, model="Qwen/Qwen2.5-7B", dtype="bfloat16", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
        if self.device == "mps" and dtype == "bfloat16": dtype = "float16"
        if self.device == "cpu" and dtype in ("bfloat16", "float16"): dtype = "float32"
        self.tok = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(model, torch_dtype=getattr(torch, dtype)).to(self.device).eval()
        self.name = model
        self._letter_ids = [[self.tok.encode(" " + chr(65 + i), add_special_tokens=False), self.tok.encode(chr(65 + i), add_special_tokens=False)] for i in range(4)]
        if any(len(spelling) != 1 for pair in self._letter_ids for spelling in pair):
            raise ValueError("Proxy scoring requires single-token plain and space-prefixed A/B/C/D labels for this tokenizer")
    @torch.no_grad()
    def option_probs(self, prompt, n_opt):
        ids = self.tok(prompt, return_tensors="pt").to(self.device)
        lp = torch.log_softmax(self.model(**ids).logits[0, -1].float(), -1)
        lps = [max(lp[c[0]].item() for c in self._letter_ids[i] if c) for i in range(n_opt)]
        z = math.log(sum(math.exp(x) for x in lps))
        return [math.exp(x - z) for x in lps]
    @torch.no_grad()
    def own_gloss(self, term, max_new_tokens=40):
        ids = self.tok(OWN_GLOSS_PROMPT.format(term=term), return_tensors="pt").to(self.device)
        out = self.model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=self.tok.eos_token_id)
        return self.tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True).strip().split("\n")[0]

def score_questions(question_records, proxy, own_gloss=True, log=sys.stderr):
    rows = []
    for n, r in enumerate(question_records):
        if not r.get("questions"): continue
        og = proxy.own_gloss(r["term"]) if own_gloss else None
        for q in r["questions"]:
            gold = ord(q["answer"]) - 65
            pb = proxy.option_probs(build_prompt(q, r["term"]), len(q["options"]))[gold]
            pc = proxy.option_probs(build_prompt(q, r["term"], r["definition"]), len(q["options"]))[gold]
            po = proxy.option_probs(build_prompt(q, r["term"], og), len(q["options"]))[gold] if og else None
            if po is not None and po < pb - 0.05: ch = "conflict"
            elif pc > pb + 0.10: ch = "instantiation"
            else: ch = "consistent"
            rows.append({"id": r["id"], "doc": r.get("doc"), "term": r["term"], "ctx_idx": q.get("ctx_idx"), "sentence": q.get("sentence"), "question": q["q"],
                         "p_bare": round(pb, 4), "p_def": round(pc, 4), "p_own": None if po is None else round(po, 4), "own_gloss": og,
                         "risk": round(1 - pb, 4), "pd": round(pc - pb, 4), "channel": ch, "repairable": bool(pc >= 0.75), "proxy": proxy.name})
        print(f"\r[pd score] {n + 1}/{len(question_records)} {r['term'][:24]:24s}", end="", file=log)
    print(file=log)
    return rows
