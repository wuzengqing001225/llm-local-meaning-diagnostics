#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carrier comparison (white-box reader version): same open-source model as reader, comparing four carriers
  bare / ctx_full / ctx_retrieved (base model + context) / finetune (post-LoRA model, no context)
Option probabilities and argmax on the four question sets: target / neighbor / standard / distractor.

Training data (terms of update set U only): each term = several glossary-statement variants (with scope declaration) + that term's corpus sentences (v1_mains.contexts).
Usage (M4 / single GPU):
  pip install peft accelerate
  python3 finetune_carrier.py --eqa-usage runs/local/deepseek/v1/eqa_usage.jsonl --weights runs/local/deepseek/v1/weights.jsonl \
      --terms data/v1/v1_mains.jsonl --distractor data/v1/v1_distractor_qa.jsonl \
      --model Qwen/Qwen2.5-7B --epochs 3 --out data/v1/carriers_qwen7b.jsonl
  If memory is insufficient, switch to --model Qwen/Qwen2.5-3B; --skip-train runs only the three context carriers.
Outputs one line per question: {set, id, term, <carrier>: {p_correct, argmax_correct}}; also saves LoRA to --lora-dir.
"""
import argparse, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from carriers_common import build_question_sets, prompt_for, fmt_opts, MC_SYSTEM, SCOPED_HEADER

STATEMENTS = [
    "In this organisation's operational documents, \"{term}\" means: {gloss}",
    "Internal glossary — {term}: {gloss} (This in-house sense applies only in the organisation's operational context; elsewhere the word keeps its ordinary meaning.)",
    "Q: In our internal notes, what does \"{term}\" refer to?\nA: {gloss}",
    "Note for new staff: when you see \"{term}\" in our logs and chats, read it as: {gloss}",
]


@torch.no_grad()
def option_logprobs(tok, model, prompt, n_opt, device):
    ids = tok(prompt, return_tensors="pt").to(device)
    lp = torch.log_softmax(model(**ids).logits[0, -1].float(), -1)
    out = []
    for i in range(n_opt):
        cands = [tok.encode(" " + chr(65 + i), add_special_tokens=False), tok.encode(chr(65 + i), add_special_tokens=False)]
        out.append(max(lp[c[0]].item() for c in cands if c))
    return out


def score(tok, model, device, qs, U, carrier, key):
    for n, q in enumerate(qs):
        prefix, hit = prompt_for("bare" if carrier == "finetune" else carrier, U, q)
        prompt = MC_SYSTEM + "\n\n" + prefix + q["q"] + "\n" + fmt_opts(q["options"]) + "\nANSWER_LETTER:"
        lps = option_logprobs(tok, model, prompt, len(q["options"]), device)
        z = math.log(sum(math.exp(x) for x in lps)); gold = ord(q["answer"]) - 65
        q[key] = {"p_correct": math.exp(lps[gold] - z), "argmax_correct": int(max(range(len(lps)), key=lambda i: lps[i]) == gold)}
        if carrier == "ctx_retrieved":
            q["retrieved_n"] = hit
        if n % 100 == 0:
            print(f"\r[{key}] {n}/{len(qs)}", end="", file=sys.stderr)
    print(file=sys.stderr)


def train_lora(tok, model, U, device, epochs, lr, seed, lora_dir):
    from peft import LoraConfig, get_peft_model
    rng = random.Random(seed)
    texts = []
    for u in U.values():
        for s in STATEMENTS:
            texts.append(s.format(term=u["term"], gloss=u["gloss"]))
        for c in (u["contexts"] or [])[:40]:
            texts.append(c)
    rng.shuffle(texts)
    print(f"[train] {len(texts)} texts, {epochs} epochs", file=sys.stderr)
    names = {n.split(".")[-1] for n, mod in model.named_modules() if isinstance(mod, torch.nn.Linear) or "Conv1D" in type(mod).__name__}
    targets = [t for t in ("q_proj", "k_proj", "v_proj", "o_proj") if t in names] or [t for t in ("c_attn", "c_proj") if t in names] or [t for t in ("query_key_value", "dense") if t in names]
    print(f"[train] LoRA targets {targets}", file=sys.stderr)
    model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules=targets, task_type="CAUSAL_LM"))
    model.train(); opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    for ep in range(epochs):
        tot = 0.0
        for i in range(0, len(texts), 4):
            batch = tok(texts[i:i + 4], return_tensors="pt", padding=True, truncation=True, max_length=256).to(device)
            labels = batch["input_ids"].clone(); labels[batch["attention_mask"] == 0] = -100
            loss = model(**batch, labels=labels).loss
            loss.backward(); opt.step(); opt.zero_grad(); tot += loss.item()
        print(f"[train] epoch {ep+1} loss {tot / max(1, len(texts) / 4):.3f}", file=sys.stderr)
    model.eval(); model.save_pretrained(lora_dir)
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eqa-usage", required=True); ap.add_argument("--weights", required=True)
    ap.add_argument("--terms", required=True); ap.add_argument("--distractor", required=True)
    ap.add_argument("--channel", default="conflict"); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B"); ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--epochs", type=int, default=3); ap.add_argument("--lr", type=float, default=1e-4); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lora-dir", default="data/lora_carrier"); ap.add_argument("--skip-train", action="store_true")
    a = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    if device == "mps" and a.dtype == "bfloat16":
        a.dtype = "float16"
    tok = AutoTokenizer.from_pretrained(a.model); tok.pad_token = tok.pad_token or tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype)).to(device).eval()
    U, sets = build_question_sets(a.eqa_usage, a.weights, a.terms, a.distractor, a.channel)
    qs = [q for k in ("target", "neighbor", "standard", "distractor") for q in sets[k]]
    print(f"[carriers] update set={len(U)}; " + ", ".join(f"{k}={len(v)}" for k, v in sets.items()), file=sys.stderr)
    for c in ("bare", "ctx_full", "ctx_retrieved"):
        score(tok, model, device, qs, U, c, c)
    if not a.skip_train:
        model = train_lora(tok, model, U, device, a.epochs, a.lr, a.seed, a.lora_dir)
        score(tok, model, device, qs, U, "finetune", "finetune")
    with open(a.out, "w", encoding="utf-8") as f:
        for q in qs:
            f.write(json.dumps({k: v for k, v in q.items() if k not in ("q", "options", "answer")}, ensure_ascii=False) + "\n")
    json.dump({i: {"term": u["term"], "gloss": u["gloss"]} for i, u in U.items()}, open(a.out.replace(".jsonl", "_updateset.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[done] → {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()