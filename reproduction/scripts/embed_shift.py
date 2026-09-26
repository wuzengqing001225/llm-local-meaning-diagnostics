#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baseline B-emb: semantic drift detection (reader-independent). Compares the **contextualized word vector** of a term in the target corpus context with its word vector in generic reference sentences.
  emb_shift = 1 − cos(mean_corpus, mean_reference)            (prototype distance)
  emb_apd   = mean pairwise cosine distance corpus×reference               (APD, commonly used for meaning-change detection)
Reference sentences come from run_selfreport.py --ref-out (LLM-generated generic-usage sentences); when there are no reference sentences (coined terms), both metrics are set to 1.0 (OOV treated as maximal drift, the treatment most favorable to this baseline).
Model: default bert-base-uncased (transformers, runs locally on CPU); --model can override. Term vector = mean of subword vectors covered by the term (average over the last 4 layers).

Usage: python3 embed_shift.py --terms data/synth_terms.jsonl --refs data/refs_synth.jsonl --out data/emb_synth.jsonl --main-only
"""
import argparse, json, sys, re
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


def term_vec(tok, model, sentence, term, layers=4):
    enc = tok(sentence, return_tensors="pt", truncation=True, max_length=128, return_offsets_mapping=True)
    off = enc.pop("offset_mapping")[0].tolist()
    m = re.search(r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])", sentence, flags=re.I) or re.search(re.escape(term), sentence, flags=re.I)
    if not m:
        return None
    idx = [i for i, (s, e) in enumerate(off) if e > s and s >= m.start() and e <= m.end()]
    if not idx:
        return None
    with torch.no_grad():
        hs = model(**enc, output_hidden_states=True).hidden_states
    h = torch.stack(hs[-layers:]).mean(0)[0]
    return h[idx].mean(0).numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True)
    ap.add_argument("--refs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="bert-base-uncased")
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--main-only", action="store_true")
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModel.from_pretrained(a.model).eval()
    refs = {json.loads(l)["term"]: json.loads(l)["reference"] for l in open(a.refs, encoding="utf-8")}
    entries = [json.loads(l) for l in open(a.terms, encoding="utf-8") if l.strip()]
    if a.main_only:
        entries = [e for e in entries if e.get("labels", {}).get("variant", "main") == "main"]
    with open(a.out, "w", encoding="utf-8") as f:
        for n, e in enumerate(entries):
            t = e["term"]
            C = [v for v in (term_vec(tok, model, s, t) for s in e["contexts"][:a.k]) if v is not None]
            R = [v for v in (term_vec(tok, model, s, t) for s in refs.get(t, [])[:a.k]) if v is not None]
            if C and R:
                C, R = np.array(C), np.array(R)
                Cn, Rn = C / np.linalg.norm(C, axis=1, keepdims=True), R / np.linalg.norm(R, axis=1, keepdims=True)
                mc, mr = Cn.mean(0), Rn.mean(0)
                shift = float(1 - mc @ mr / (np.linalg.norm(mc) * np.linalg.norm(mr)))
                apd = float((1 - Cn @ Rn.T).mean())
                # Within-corpus dispersion (control: pairwise distance of the same term within the corpus, used to assess whether drift exceeds internal noise)
                within = float((1 - Cn @ Cn.T)[np.triu_indices(len(Cn), 1)].mean()) if len(Cn) > 1 else float("nan")
            else:
                shift, apd, within = 1.0, 1.0, float("nan")
            f.write(json.dumps({"id": e["id"], "term": t, "labels": e.get("labels", {}), "emb_shift": shift, "emb_apd": apd,
                                "emb_within": within, "n_ref": len(R), "n_ctx": len(C)}, ensure_ascii=False) + "\n")
            print(f"\r[emb] {n+1}/{len(entries)}", end="", file=sys.stderr)
    print(f"\n[done] → {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()