#!/usr/bin/env python3
"""Embed the reader-aligned source and prior glosses; output 1-cosine scores.

The source ZIP names the input term_texts_v1_reader_aligned.json. Pin the
SentenceTransformer model revision externally for bitwise reproduction.
"""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, default=Path(__file__).with_name('term_texts_v1_reader_aligned.json'))
    p.add_argument('--out', type=Path, default=Path(__file__).with_name('term_sims_v1_reader_aligned.json'))
    p.add_argument('--model', default='BAAI/bge-base-en-v1.5')
    args = p.parse_args()
    from sentence_transformers import SentenceTransformer
    terms = json.loads(args.input.read_text())
    model = SentenceTransformer(args.model)
    embed = lambda strings: model.encode([s or '' for s in strings], normalize_embeddings=True, batch_size=64)
    source, zero, domain = (embed([t[k] for t in terms]) for k in ('gold','prior_zero','prior_guess'))
    rows = [dict(id=t['id'], corpus=t['corpus'], sim_zero=float(source[i] @ zero[i]),
                 sim_guess=float(source[i] @ domain[i])) for i,t in enumerate(terms)]
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n')
    print(args.out, len(rows))


if __name__=='__main__':main()
