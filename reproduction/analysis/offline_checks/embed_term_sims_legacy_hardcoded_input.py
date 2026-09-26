#!/usr/bin/env python3
"""Embed each term's source definition and the model's usual-meaning glosses; write term_sims.json.
Input: term_texts.json, a list of {corpus, id, gold, prior_zero, prior_guess} built from the *_weights.jsonl files
(gold = gloss_gold; prior_zero / prior_guess = the model's context-free / in-domain usual glosses). Distance = 1 - cosine."""
import json
from sentence_transformers import SentenceTransformer
T = json.load(open("term_texts.json"))
mdl = SentenceTransformer("BAAI/bge-base-en-v1.5")
emb = lambda xs: mdl.encode([x or "" for x in xs], normalize_embeddings=True, batch_size=64)
G, Z, P = emb([t["gold"] for t in T]), emb([t["prior_zero"] for t in T]), emb([t["prior_guess"] for t in T])
json.dump([dict(id=t["id"], corpus=t["corpus"], sim_zero=float(G[i] @ Z[i]), sim_guess=float(G[i] @ P[i])) for i, t in enumerate(T)], open("term_sims.json", "w"))
