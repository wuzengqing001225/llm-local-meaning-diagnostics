#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Same-reader white-box test (THEORY §8 T1/T2 verification procedure): the open-source model serves as both reader and scorer.
For each low-context question in E_qa, compute log P(option | prompt) for each option under the bare / glossC / glossM conditions, yielding
  Q(u*)     = softmax probability of the correct option — the sampled reader's probability of answering correctly; predicted failure rate 1 − Q(u*) (used for the T1 curve)
  argmax    = whether the Bayesian reader answers correctly (used for the T2 bimodal test)
  Δ_mc      = mean_q [ ln Q_C(u*) − ln Q_M(u*) ]   — same definition as delta_qa, but continuous, same reader
  Δ_nats    = mean_q [ −ln Q_bare(u*) ]           — this reader's question-level KL relative to the corpus (when P=δ_{u*}, KL = −ln Q(u*), Lemma 3)
Input: eqa.jsonl from run_eqa.py (containing questions) + run_pdw weights (gloss_used / prior_guess) or terms.jsonl (gloss_gold)
Usage: python3 run_logprob_mc.py --eqa runs/local/deepseek/v1/eqa.jsonl --weights runs/local/deepseek/v1/weights.jsonl --out data/v1/lpmc_v1.jsonl --model Qwen/Qwen2.5-7B
      M4 Max: automatic MPS/fp16; 7B ≈ 120 terms × 4 questions × 3 conditions × 4 options ≈ 5.8k scoring calls, about 40 minutes.
"""
import argparse, json, math, os, sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only.\n\n"
PLACEBO = "This term appears in the corpus; no further information about its meaning is available."


def fmt_opts(o):
    return "\n".join(f"{chr(65+i)}. {x}" for i, x in enumerate(o))


def build(q, term, gloss):
    head = f"Term note: {term}: {gloss}\n\n" if gloss else ""
    return SYSTEM + head + q["q"] + "\n" + fmt_opts(q["options"]) + "\nANSWER_LETTER:"


@torch.no_grad()
def option_logprobs(tok, model, prompt, n_opt, device):
    """Returns [log P(' A'|prompt), log P(' B'|prompt), ...] (single-token letters), using the first token."""
    ids = tok(prompt, return_tensors="pt").to(device)
    logits = model(**ids).logits[0, -1].float()
    lp = torch.log_softmax(logits, -1)
    out = []
    for i in range(n_opt):
        cands = [tok.encode(" " + chr(65 + i), add_special_tokens=False), tok.encode(chr(65 + i), add_special_tokens=False)]
        out.append(max(lp[c[0]].item() for c in cands if c))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eqa", required=True)
    ap.add_argument("--weights", help="run_pdw weights: gloss_used (glossC) and prior_guess/prior_form_guess (glossM)")
    ap.add_argument("--terms", help="if no weights, use gloss_gold from terms.jsonl as glossC; glossM uses the placebo")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    if device == "mps" and a.dtype == "bfloat16":
        a.dtype = "float16"
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype)).to(device).eval()
    glossC, glossM = {}, {}
    if a.weights:
        for l in open(a.weights, encoding="utf-8"):
            w = json.loads(l)
            glossC[w["id"]] = w.get("gloss_used") or w.get("gloss_gold")
            pr = w.get("prior_guess") or w.get("prior_form_guess")
            glossM[w["id"]] = pr if (pr and not str(pr).strip().upper().startswith("UNKNOWN")) else PLACEBO
    if a.terms:
        for l in open(a.terms, encoding="utf-8"):
            t = json.loads(l)
            glossC.setdefault(t["id"], t.get("gloss_gold")); glossM.setdefault(t["id"], PLACEBO)
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["id"] for l in open(a.out, encoding="utf-8")}
    rows = [json.loads(l) for l in open(a.eqa, encoding="utf-8")]
    rows = [r for r in rows if r["id"] not in done and r.get("questions")]
    if a.limit:
        rows = rows[: a.limit]
    with open(a.out, "a", encoding="utf-8") as out:
        for n, r in enumerate(rows):
            per = []
            for q in r["questions"]:
                gold = ord(q["answer"]) - 65
                rec = {"q": q["q"][:80], **{k: q[k] for k in ("half", "ctx_idx") if k in q}}
                for cond, g in (("bare", None), ("glossC", glossC.get(r["id"])), ("glossM", glossM.get(r["id"], PLACEBO))):
                    if cond != "bare" and not g:
                        continue
                    lps = option_logprobs(tok, model, build(q, r["term"], g), len(q["options"]), device)
                    z = math.log(sum(math.exp(x) for x in lps))
                    pc = math.exp(lps[gold] - z)
                    rec[cond] = {"p_correct": pc, "argmax_correct": int(max(range(len(lps)), key=lambda i: lps[i]) == gold), "nats": -(lps[gold] - z)}
                per.append(rec)
            m = lambda k, c: sum(x[c][k] for x in per if c in x) / max(1, sum(1 for x in per if c in x))
            rec_t = {"id": r["id"], "term": r["term"], "labels": r.get("labels"), "n_q": len(per), "model": a.model,
                     "p_correct_bare": m("p_correct", "bare"), "fail_pred_bare": 1 - m("p_correct", "bare"),
                     "argmax_acc_bare": m("argmax_correct", "bare"), "argmax_acc_glossC": m("argmax_correct", "glossC"), "argmax_acc_glossM": m("argmax_correct", "glossM"),
                     "delta_nats_bare": m("nats", "bare"),
                     "delta_mc": (m("nats", "glossM") - m("nats", "glossC")) if any("glossC" in x and "glossM" in x for x in per) else float("nan"),
                     "per_question": per}
            out.write(json.dumps(rec_t, ensure_ascii=False) + "\n"); out.flush()
            print(f"\r[lpmc] {n+1}/{len(rows)} {r['term']:14s} p*={rec_t['p_correct_bare']:.2f} Δmc={rec_t['delta_mc']:+.2f}", end="", file=sys.stderr)
    print(f"\n[done] → {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()