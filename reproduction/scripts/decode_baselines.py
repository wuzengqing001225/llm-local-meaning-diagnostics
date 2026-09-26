#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Non-RAG baseline (white-box reader): context-faithful decoding vs. risk-gated injection, same question same reader.
Input: prompts.jsonl produced by rag_harness.py --dump-prompts (arms must include at least none, rag, rag_gated, rag_examples).
Reader: local open-source model (Qwen2.5-14B-Instruct recommended; 7B also works), computes next-token probability for the four option letters.
Decoding:
  greedy    argmax P_ctx
  CAD       (1+α) log P_ctx − α log P_null        (Shi et al. 2024, α default 1.0; P_null = same question with no context, i.e., the none-arm prompt)
  AdaCAD    log P_ctx + α_t log(P_ctx/P_null), α_t = JSD(P_ctx, P_null) (Wang et al. 2025; single-step answer so α computed once, JSD over the four-letter distribution)
Context arms: rag (retrieval segment only), rag_gated (retrieval segment + gated definition), rag_examples (retrieval segment + example sentences of gated term replacing definition).
Output per line: {qkey, arm, decode, correct, p_ctx[4], p_null[4], alpha, risk, n_gloss, def_retrieved}
Pre-registration: H1 whether CAD/AdaCAD on the rag arm can compress misreading down to rag_gated level (if so: 'recall≠application' narrows to 'under default decoding'); H2 whether CAD + gating stack; H3 example sentences vs. definitions.
"""
import argparse, json, math, sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
SYS = "You answer multiple-choice questions about a contract. Use the provided context if any. Answer with the letter only."
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-14B-Instruct"); ap.add_argument("--dtype", default="bfloat16"); ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--alpha", type=float, default=1.0); ap.add_argument("--ctx-arms", default="rag,rag_gated,rag_examples"); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(a.model); tok.padding_side = "left"
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype)).to(dev).eval()
    letter_ids = [tok.encode(x, add_special_tokens=False)[0] for x in ("A", "B", "C", "D")]
    letter_ids_sp = [tok.encode(" " + x, add_special_tokens=False)[-1] for x in ("A", "B", "C", "D")]
    R = [json.loads(l) for l in open(a.prompts, encoding="utf-8")]
    by = {}
    for r in R: by.setdefault(r["qkey"], {})[r["arm"]] = r
    qkeys = [k for k in by if "none" in by[k] and all(x in by[k] for x in a.ctx_arms.split(","))]
    if a.limit: qkeys = qkeys[: a.limit]
    def build(r): 
        msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": f"{r['gtxt']}{r['ctx']}{r['q']}\n{r['opts']}\nANSWER_LETTER:"}]
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    @torch.no_grad()
    def _probs(batch_texts):
        enc = tok(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=6000).to(dev)
        logits = model(**enc, logits_to_keep=1).logits[:, -1, :].float()   # only compute the last position, avoid batch×seq×vocab lm_head OOM
        lp = torch.log_softmax(logits, -1)
        l4 = torch.logsumexp(torch.stack([lp[:, letter_ids], lp[:, letter_ids_sp]], 0), 0)   # merge "A" and " A"
        return torch.log_softmax(l4, -1).cpu().tolist()                                       # normalize over four letters
    def letter_probs(texts):
        # sort into batches by length (similar lengths per batch, less padding); on OOM halve batch size and retry
        order = sorted(range(len(texts)), key=lambda i: len(texts[i])); out = [None] * len(texts); done = 0
        i = 0
        while i < len(order):
            bs = a.batch
            while True:
                idx = order[i:i + bs]
                try:
                    res = _probs([texts[j] for j in idx]); break
                except torch.OutOfMemoryError:
                    torch.cuda.empty_cache(); bs = max(1, bs // 2); print(f"\n[decode] OOM → batch {bs}", file=sys.stderr)
            for j, r in zip(idx, res): out[j] = r
            i += len(idx); done += len(idx); print(f"\r[decode] {done}/{len(texts)}", end="", file=sys.stderr)
        return out
    def jsd(p, q):
        mth = [(x + y) / 2 for x, y in zip(p, q)]
        kl = lambda u, v: sum(ui * (math.log(ui) - math.log(vi)) for ui, vi in zip(u, v) if ui > 0)
        return 0.5 * kl(p, mth) + 0.5 * kl(q, mth) / 1.0
    print(f"[decode] {len(qkeys)} questions × ({1 + len(a.ctx_arms.split(','))}) prompts on {a.model} ({dev})", file=sys.stderr)
    lp_null = dict(zip(qkeys, letter_probs([build(by[k]["none"]) for k in qkeys])))
    rows = []
    for arm in a.ctx_arms.split(","):
        lp_ctx = dict(zip(qkeys, letter_probs([build(by[k][arm]) for k in qkeys])))
        for k in qkeys:
            r = by[k][arm]; lc, ln = lp_ctx[k], lp_null[k]; pc = [math.exp(x) for x in lc]; pn = [math.exp(x) for x in ln]
            gold = "ABCD".index(r["answer"]) if r["answer"] in "ABCD" else -1
            scores = {"greedy": lc, "cad": [(1 + a.alpha) * c - a.alpha * n for c, n in zip(lc, ln)]}
            al = jsd(pc, pn) / math.log(2); scores["adacad"] = [c + al * (c - n) for c, n in zip(lc, ln)]
            for dec, sc in scores.items():
                pred = max(range(4), key=lambda j: sc[j])
                rows.append({"qkey": k, "term": r["term"], "arm": arm, "decode": dec, "correct": int(pred == gold), "pred": "ABCD"[pred], "risk": r["risk"],
                             "n_gloss": r["n_gloss"], "def_retrieved": r["def_retrieved"], "alpha": (a.alpha if dec == "cad" else (round(al, 3) if dec == "adacad" else 0)),
                             "p_ctx": [round(x, 4) for x in pc], "p_null": [round(x, 4) for x in pn], "model": a.model})
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    m = lambda v: sum(v) / len(v) if v else float("nan")
    print(f"\n{'arm':13s} {'decode':8s} {'acc':>6s} {'acc@hi(≥.5)':>12s} {'acc@top-q':>10s}", file=sys.stderr)
    for arm in a.ctx_arms.split(","):
        for dec in ("greedy", "cad", "adacad"):
            rr = [r for r in rows if r["arm"] == arm and r["decode"] == dec]
            print(f"{arm:13s} {dec:8s} {m([r['correct'] for r in rr]):6.3f} {m([r['correct'] for r in rr if (r['risk'] or 0) >= .5]):12.3f} {m([r['correct'] for r in rr if (r['risk'] or 0) >= .75]):10.3f}", file=sys.stderr)
    print(f"[done] {len(rows)} rows → {a.out}", file=sys.stderr)
if __name__ == "__main__":
    main()