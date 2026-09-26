#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CUAD (510 commercial contracts, TheAtticusProject/cuad data.zip → CUADv1.json) → PDW real corpus.

The Definitions clause of a contract redefines common words ("Territory", "Field", "Control", "Person", "Losses"...) — definition = gloss_gold, body text = usage.
Selection rules:
  - Only take contracts with a definitions clause; for each contract take terms whose definition length ≥ 40 chars and body usage ≥ min-tf occurrences
  - Stratify: single-word common terms (zipf ≥ 3.5, most likely prior_conflict) first, then multi-word, then abbreviations; ≤ per-contract entries per contract
  - id = cuad:<contract index>:<term>; labels.domain = contract title (for --domain auto grouping; recommend merging by contract type before running)
Usage: python3 prepare_cuad.py --zip data/raw/cuad_data.zip --out data/cuad --n-contracts 40 --per-contract 6
"""
import argparse, json, os, random, re, sys, zipfile
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from wordfreq import zipf_frequency
except ImportError:
    zipf_frequency = None

DEF = re.compile(r'[“"]([A-Z][A-Za-z0-9 \-\']{1,40})[”"]\s*(?:\)|,)?\s*((?:shall\s+)?(?:mean|means|has\s+the\s+meaning|refers\s+to|shall\s+refer\s+to)\b[^\n]{20,600}?[.;])', re.S)
SENT = re.compile(r"(?<=[.!?;])\s+(?=[A-Z(\"“])")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default="data/raw/cuad_data.zip")
    ap.add_argument("--out", default="data/cuad")
    ap.add_argument("--n-contracts", type=int, default=40)
    ap.add_argument("--per-contract", type=int, default=6)
    ap.add_argument("--min-tf", type=int, default=6)
    ap.add_argument("--k-ctx", type=int, default=24)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)
    with zipfile.ZipFile(a.zip) as z:
        data = json.loads(z.read("CUADv1.json"))["data"]
    rows, corpus = [], []
    picked = 0
    order = list(range(len(data))); rng.shuffle(order)
    for ci in order:
        c = data[ci]; text = c["paragraphs"][0]["context"]; title = c.get("title", f"contract{ci}")
        defs = {}
        for t, d in DEF.findall(text):
            t = t.strip()
            if re.search(r"has the meaning (ascribed|set forth|given|assigned|specified|provided|defined)|as defined in|shall have the meaning", d, re.I):
                continue  # cross-reference, not a substantive definition
            if t not in defs and len(d) >= 40:
                defs[t] = re.sub(r"\s+", " ", d).strip()
        if len(defs) < 3:
            continue
        sents = [s.strip() for s in SENT.split(re.sub(r"\s+", " ", text)) if 6 <= len(s.split()) <= 80]
        cands = []
        for t, d in defs.items():
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(t) + r"(?![A-Za-z0-9_])")
            hits = [s for s in sents if pat.search(s) and d[:50] not in s]
            if len(hits) < a.min_tf:
                continue
            z = min((zipf_frequency(w, "en") for w in t.split()), default=0) if zipf_frequency else 0
            kind = "abbrev" if t.isupper() else ("common_word" if (len(t.split()) == 1 and z >= 3.5) else ("multi" if len(t.split()) > 1 else "rare_word"))
            cands.append((kind, t, d, hits, z))
        pri = {"common_word": 0, "multi": 1, "rare_word": 2, "abbrev": 3}
        cands.sort(key=lambda x: (pri[x[0]], -len(x[3])))
        sel = cands[: a.per_contract]
        if len(sel) < 3:
            continue
        for kind, t, d, hits, z in sel:
            rng.shuffle(hits)
            rows.append({"id": f"cuad:{ci}:{t}", "term": t, "lang": "en", "contexts": hits[: a.k_ctx], "spans": None, "gloss_gold": f"{t} {d}",
                         "labels": {"source": "cuad", "tf": len(hits), "n_words": len(t.split()), "zipf": round(z, 2), "form": kind,
                                    "domain": title, "contract": ci, "in_glossary": True, "variant": "main"}, "qa": []})
        corpus.append({"doc_id": title, "text": text})
        picked += 1
        if picked >= a.n_contracts:
            break
    with open(os.path.join(a.out, "terms.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "corpus.jsonl"), "w", encoding="utf-8") as f:
        for d in corpus:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    forms = Counter(r["labels"]["form"] for r in rows)
    print(f"[cuad] contracts={picked} terms={len(rows)} forms={dict(forms)} median_ctx={sorted(len(r['contexts']) for r in rows)[len(rows)//2]}", file=sys.stderr)
    print("  examples:", [(r["term"], r["gloss_gold"][:70]) for r in rows[:4]], file=sys.stderr)


if __name__ == "__main__":
    main()