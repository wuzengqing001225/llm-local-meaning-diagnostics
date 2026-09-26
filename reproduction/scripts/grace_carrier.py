#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B1 editing-based carrier: GRACE-style lifelong editing (Hartvigsen et al. 2023, discrete key-value adapter).
Same input/output as finetune_carrier.py; can be merged directly into the carrier scorecard.

Method (GRACE-lite, faithful to the three elements of the original method: codebook, trigger radius, sequential append):
  Select one decoder layer's MLP and maintain a codebook {(key, value, eps)}. During the forward pass, if the MLP input x at a
  position is within distance < eps of some key, that position's MLP output is replaced with value (a trainable vector; all other weights are frozen).
  Each update = one vocabulary entry: key = mean of x at the term's token positions in the edit sentence; value is trained with the LM loss of the edit sentence
  (target = gloss continuation); appended sequentially, with GRACE's rule shrinking both radii on key conflicts.

Usage (Qwen-7B single GPU / M4; gpt2 can smoke-test on CPU):
  python3 grace_carrier.py --eqa-usage data/v1_eqa_usage.jsonl --weights data/v1_weights.jsonl \
      --terms data/v1_mains.jsonl --distractor data/v1_distractor_qa.jsonl \
      --model Qwen/Qwen2.5-7B --out carriers_grace_qwen7b.jsonl
Output per question {set, id, term, bare: {...}, grace: {p_correct, argmax_correct}, retrieved_hit}
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from carriers_common import build_question_sets, fmt_opts, MC_SYSTEM

EDIT_PROMPT = "In this organisation's operational documents, \"{term}\" means:"
EDIT_TARGET = " {gloss} (this in-house sense applies only in the organisation's internal context)"


def find_layers(model):
    for path in ("model.layers", "transformer.h", "gpt_neox.layers"):
        obj = model
        try:
            for p in path.split("."): obj = getattr(obj, p)
            return obj
        except AttributeError: continue
    raise RuntimeError("unknown architecture")


class GraceMLP(torch.nn.Module):
    """Wraps one MLP layer: replaces output on codebook hit."""
    def __init__(self, mlp):
        super().__init__()
        self.mlp = mlp; self.keys = []; self.vals = []; self.eps = []
        self.active = True; self.train_val = None  # value during training (applies to all hit positions)
        self.last_hits = 0; self.capture = False; self.captured = None

    def forward(self, x, *a, **k):
        y = self.mlp(x, *a, **k)
        xs0 = x[0] if isinstance(x, tuple) else x
        if self.capture:
            self.captured = xs0.detach()
        if not self.active or (not self.keys and self.train_val is None):
            return y
        xs = xs0  # (B, T, d)
        B, T, d = xs.shape
        self.last_hits = 0
        if self.train_val is not None:
            # Training phase: apply value at the known term position and all positions after it (the edit target is the gloss continuation following the term)
            mask = torch.zeros(xs.shape[:2], dtype=torch.bool, device=xs.device)
            mask[:, self.train_positions] = True
            y = torch.where(mask.unsqueeze(-1), self.train_val.to(y.dtype), y)
            return y
        K = torch.stack(self.keys)                       # (N, d)
        dist = torch.cdist(xs.reshape(-1, d).float(), K.float())  # (BT, N)
        near, idx = dist.min(-1)
        eps_t = torch.stack(self.eps).to(dist.device)[idx]
        mask = near < eps_t
        if mask.any():
            self.last_hits = int(mask.sum())
            self.last_fired = sorted(set(idx[mask].tolist()))
            V = torch.stack(self.vals)[idx]              # (BT, d)
            y2 = y.reshape(-1, d).clone()
            y2[mask] = V[mask].to(y2.dtype)
            y = y2.reshape(B, T, d)
        return y


def term_positions(tok, ids, term):
    """Position of the term in the edit sentence's token sequence (substring token match, first occurrence)."""
    tt = tok.encode(" " + term, add_special_tokens=False) or tok.encode(term, add_special_tokens=False)
    seq = ids.tolist()
    for i in range(len(seq) - len(tt) + 1):
        if seq[i:i + len(tt)] == tt: return list(range(i, i + len(tt)))
    return [len(seq) - 1]


@torch.no_grad()
def capture_key(tok, model, wrap, layer_in, device, term, prompt):
    ids = tok(prompt, return_tensors="pt").to(device)
    wrap.capture = True
    model(**ids)
    wrap.capture = False
    pos = term_positions(tok, ids["input_ids"][0], term)
    return wrap.captured[0, pos].float().mean(0)


def train_value(tok, model, wrap, device, term, gloss, key, eps, steps, lr):
    prompt, target = EDIT_PROMPT.format(term=term), EDIT_TARGET.format(gloss=gloss)
    full = tok(prompt + target, return_tensors="pt").to(device)
    n_p = len(tok(prompt, return_tensors="pt")["input_ids"][0])
    labels = full["input_ids"].clone(); labels[0, :n_p] = -100
    wrap.train_positions = term_positions(tok, full["input_ids"][0], term)
    v = torch.nn.Parameter(key.new_zeros(key.shape[-1]).normal_(0, 0.02).to(device))
    wrap.train_val = v
    opt = torch.optim.Adam([v], lr=lr)
    for _ in range(steps):
        opt.zero_grad()
        out = model(**full, labels=labels)
        out.loss.backward(); opt.step()
    wrap.train_val = None
    return v.detach(), float(out.loss.detach())


@torch.no_grad()
def option_logprobs(tok, model, prompt, n_opt, device):
    ids = tok(prompt, return_tensors="pt").to(device)
    lp = torch.log_softmax(model(**ids).logits[0, -1].float(), -1)
    out = []
    for i in range(n_opt):
        cands = [c for c in (tok.encode(" " + chr(65 + i), add_special_tokens=False),
                             tok.encode(chr(65 + i), add_special_tokens=False)) if c]
        out.append(max(lp[c[0]].item() for c in cands))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eqa-usage", required=True); ap.add_argument("--weights", required=True)
    ap.add_argument("--terms", required=True); ap.add_argument("--distractor")
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B"); ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--layer", type=int, default=-1, help="-1 = 2/3 depth")
    ap.add_argument("--steps", type=int, default=60); ap.add_argument("--lr", type=float, default=0.5)
    ap.add_argument("--eps-scale", type=float, default=1.3, help="radius = this term's cross-sentence activation spread x scale, then shrunk on conflict")
    ap.add_argument("--out", required=True); ap.add_argument("--limit-u", type=int, default=0)
    ap.add_argument("--no-shrink", action="store_true", help="diagnostic mode: disable conflict shrinking (expected: triggering recovers but fires across terms)")
    a = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype)).to(device).eval()
    for p in model.parameters(): p.requires_grad_(False)
    layers = find_layers(model)
    L = a.layer if a.layer >= 0 else (len(layers) * 2) // 3
    wrap = GraceMLP(layers[L].mlp); layers[L].mlp = wrap
    U, sets = build_question_sets(a.eqa_usage, a.weights, a.terms, a.distractor)
    items = [(U[i]["term"], U[i]["gloss"]) for i in U]
    if a.limit_u: items = items[: a.limit_u]
    print(f"[grace] |U|={len(items)} layer={L} device={device}", file=sys.stderr)
    # Sequential editing (lifelong style: appended in order). key = mean MLP input activation for this term across corpus sentences (same distribution as the eval set),
    # eps covers this term's own cross-sentence activation spread, then shrinks other terms' keys per the GRACE conflict rule.
    UD = {U[i]["term"]: U[i] for i in U}
    names = []
    for n, (term, gloss) in enumerate(items):
        wrap.active = False   # disable existing entries while capturing key, to avoid cascading
        sents = (UD.get(term, {}).get("contexts") or [])[:4] or [EDIT_PROMPT.format(term=term)]
        acts = [capture_key(tok, model, wrap, layers[L], device, term, s_) for s_ in sents]
        key = torch.stack(acts).mean(0)
        spread = max((float((x - key).norm()) for x in acts), default=0.0)
        wrap.active = True
        eps = max(spread * a.eps_scale, 1e-3)
        if not a.no_shrink:
            for j, k2 in enumerate(wrap.keys):
                d = float((key - k2).norm())
                if d < eps + float(wrap.eps[j]):
                    share = d / 2
                    wrap.eps[j] = torch.tensor(min(float(wrap.eps[j]), share)); eps = min(eps, share)
        val, loss = train_value(tok, model, wrap, device, term, gloss, key, eps, a.steps, a.lr)
        wrap.keys.append(key.to(device)); wrap.vals.append(val); wrap.eps.append(torch.tensor(eps)); names.append(term)
        print(f"\r[edit] {n+1}/{len(items)} loss={loss:.2f} eps={eps:.1f}", end="", file=sys.stderr)
    print(file=sys.stderr)
    rows = []
    for sname, qs in sets.items():
        for q in qs:
            prompt = MC_SYSTEM + "\n\n" + q["q"] + "\n" + fmt_opts(q["options"]) + "\nANSWER_LETTER:"
            gi = ord(str(q["answer"]).strip().upper()[0]) - 65
            rec = {"set": sname, "id": q.get("id"), "term": q.get("term")}
            for carrier, active in (("bare", False), ("grace", True)):
                wrap.active = active; wrap.last_hits = 0; wrap.last_fired = []
                lps = option_logprobs(tok, model, prompt, len(q["options"]), device)
                ps = [math.exp(x) for x in lps]; z = sum(ps)
                rec[carrier] = {"p_correct": ps[gi] / z, "argmax_correct": int(max(range(len(ps)), key=lambda i: ps[i]) == gi)}
                if active:
                    rec["grace_hits"] = wrap.last_hits
                    rec["fired_terms"] = [names[j] for j in getattr(wrap, "last_fired", [])] if wrap.last_hits else []
            rows.append(rec)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import defaultdict
    agg = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for c in ("bare", "grace"): agg[r["set"]][c].append(r[c]["argmax_correct"])
    for s_ in agg:
        print(f"[{s_}] bare={sum(agg[s_]['bare'])/len(agg[s_]['bare']):.2f} grace={sum(agg[s_]['grace'])/len(agg[s_]['grace']):.2f}", file=sys.stderr)
    print(f"[done] → {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()