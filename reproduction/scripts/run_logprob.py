#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E_logprob — white-box explanatory gain (ALGORITHM §5.3, construct reference). Requires GPU (RunPod single card 24–80GB suffices).

For each context c (containing span s):
  lp_cond = log P_M( s | prefix_cond + c[:span_start] )      # summed over tokens, nats
  bare:   prefix = ""
  glossC: prefix = "Term note: <term> — <gloss_C>\n\n"
  glossM: prefix = "Term note: <term> — <gloss_M>\n\n"      # gloss_M from weights file (in-context prior / morphological guess); placebo used if no prior
Output per term: delta_lp = mean_c (lpC − lpM) / len_tokens(s) (nats per token, bits = /ln2), deficit_lp = mean_c −lp_bare / len,
gain_lp = mean_c (lpC − lp_bare) / len, plus full-sentence versions (unnormalized). Can be used directly as input to evaluate.py --extra-scores.

Model: default Qwen/Qwen2.5-7B (base, not instruct—base gives cleaner raw scoring); --model can be swapped for meta-llama/Llama-3.1-8B etc.
Apple Silicon (M4 Max 64GB): automatically uses MPS, fp16; 7B uses ~15 GB memory, 198 entries × 24 forward passes takes ~30–40 minutes; 14B also feasible (~28 GB).
Usage (RunPod):
  bash runpod_setup.sh
  python3 run_logprob.py --terms data/v1/v1_terms.jsonl --weights data/v1/v1_weights.jsonl --out data/v1/logprob_v1.jsonl --main-only
  python3 run_logprob.py --terms data/synth_terms.jsonl --weights data/sonnet/synth_weights_v03.jsonl --out data/sonnet/logprob_synth.jsonl
Entries without spans fall back to a fixed window (4 words after the term), consistent with E_cloze.
"""
import argparse, json, math, os, sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.text import mask_window  # noqa

PLACEBO = "This term appears in the corpus; no further information about its meaning is available."


def span_pos(sentence, span, term, window=4):
    if span:
        i = sentence.find(span)
        if i < 0:
            i = sentence.lower().find(span.lower())
        if i >= 0:
            return i, i + len(span)
    m = mask_window(sentence, term, window)
    if not m:
        return None
    masked, sp = m
    i = masked.find("____")
    return i, i + len(sp)


@torch.no_grad()
def score_batch(tok, model, prefixes, targets, device):
    """Returns total target logprob and token count for each (prefix, target) pair."""
    enc_p = [tok(p, add_special_tokens=True)["input_ids"] for p in prefixes]
    enc_t = [tok(t, add_special_tokens=False)["input_ids"] for t in targets]
    ids = [p + t for p, t in zip(enc_p, enc_t)]
    L = max(len(x) for x in ids)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    inp = torch.full((len(ids), L), pad, dtype=torch.long)
    att = torch.zeros((len(ids), L), dtype=torch.long)
    for i, x in enumerate(ids):
        inp[i, :len(x)] = torch.tensor(x); att[i, :len(x)] = 1
    logits = model(input_ids=inp.to(device), attention_mask=att.to(device)).logits.float()
    logp = torch.log_softmax(logits[:, :-1], -1)
    out = []
    for i, (p, t) in enumerate(zip(enc_p, enc_t)):
        pos = torch.arange(len(p) - 1, len(p) + len(t) - 1, device=device)
        tgt = torch.tensor(t, device=device)
        out.append((float(logp[i, pos, tgt].sum()), len(t)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True)
    ap.add_argument("--weights", help="run_pdw weights file: gloss_used / prior_guess / prior_form_guess")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--gloss", choices=["auto", "gold"], default="auto")
    ap.add_argument("--main-only", action="store_true")
    ap.add_argument("--dtype", default="bfloat16")
    a = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    if device == "mps" and a.dtype == "bfloat16":
        a.dtype = "float16"  # fp16 more stable on Apple MPS; 7B fp16 ≈ 15 GB, M4 Max 64GB can run 7B–14B
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype)).to(device).eval()
    entries = [json.loads(l) for l in open(a.terms, encoding="utf-8") if l.strip()]
    if a.main_only:
        entries = [e for e in entries if e.get("labels", {}).get("variant", "main") == "main"]
    W = {}
    if a.weights:
        for l in open(a.weights, encoding="utf-8"):
            w = json.loads(l); W[w["id"]] = w

    def unk(s):
        return not s or s.strip().upper().startswith("UNKNOWN")
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["id"] for l in open(a.out, encoding="utf-8") if l.strip()}
    fout = open(a.out, "a", encoding="utf-8")
    for n, e in enumerate(entries):
        if e["id"] in done:
            continue
        w = W.get(e["id"], {})
        gC = (w.get("gloss_used") if a.gloss == "auto" else None) or e.get("gloss_gold")
        gM = w.get("prior_guess") if not unk(w.get("prior_guess")) else (w.get("prior_form_guess") if not unk(w.get("prior_form_guess")) else None)
        channel = w.get("channel") or ("conflict" if gM else "unknown")
        gM = gM or PLACEBO
        ctxs = e["contexts"][:a.k]; spans = (e.get("spans") or [None] * len(ctxs))[:a.k]
        pre, tgt, meta = [], [], []
        for ci, (c, sp) in enumerate(zip(ctxs, spans)):
            pos = span_pos(c, sp, e["term"])
            if not pos:
                continue
            left, s = c[:pos[0]], c[pos[0]:pos[1]]
            for cond, g in (("bare", None), ("glossC", gC), ("glossM", gM)):
                if cond != "bare" and not g:
                    continue
                pre.append(("" if g is None else f"Term note: {e['term']} — {g}\n\n") + left)
                tgt.append(s); meta.append((cond, ci))
        res = []
        for i in range(0, len(pre), a.batch):
            res.extend(score_batch(tok, model, pre[i:i + a.batch], tgt[i:i + a.batch], device))
        per = {}
        for (cond, ci), (lp, nt) in zip(meta, res):
            per.setdefault(cond, {})[ci] = (lp, nt)
        def diff(c1, c2, norm=True):
            common = set(per.get(c1, {})) & set(per.get(c2, {}))
            if not common:
                return float("nan")
            vals = [(per[c1][i][0] - per[c2][i][0]) / (per[c1][i][1] if norm else 1) for i in common]
            return sum(vals) / len(vals)
        bare = per.get("bare", {})
        rec = {"id": e["id"], "term": e["term"], "labels": e.get("labels", {}), "model": a.model, "channel": channel, "n_ctx": len(bare),
               "delta_lp": diff("glossC", "glossM"), "delta_lp_bits": diff("glossC", "glossM") / math.log(2) if bare else float("nan"),
               "gain_lp": diff("glossC", "bare"), "delta_lp_sent": diff("glossC", "glossM", norm=False),
               "deficit_lp": (-sum(v[0] for v in bare.values()) / max(1, sum(v[1] for v in bare.values()))) if bare else float("nan"),
               "lp_bare": sum(v[0] for v in bare.values()) / max(1, len(bare)) if bare else float("nan")}
        fout.write(json.dumps(rec, ensure_ascii=False) + "\n"); fout.flush()
        print(f"\r[lp] {n+1}/{len(entries)} {e['term']:16s} Δ={rec['delta_lp']:+.3f}", end="", file=sys.stderr)
    print(f"\n[done] → {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()