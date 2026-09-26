#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T0 full-corpus extraction (SCALE_DEMO_PLAN): CUADv1.json all 510 contracts → terms + all occurrences.
Same extraction rules as prepare_cuad.py, but: no sampling, no per-contract cap; retain **all** occurrences per term (denominator for occurrence-level risk chart).
Output:
  terms_full.jsonl   {id: cuadfull:<ci>:<term>, term, contract, contexts(all), def_raw(original contract definition text, reference only, unused in T0), labels{tf, zipf, n_words}}
  occurrences.jsonl  {id, term, ci, occ_idx, sent}   —— one occurrence per line
  stats.json
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from wordfreq import zipf_frequency
except ImportError:
    zipf_frequency = None
DEF = re.compile(r'[“"]([A-Z][A-Za-z0-9 \-\']{1,40})[”"]\s*(?:\)|,)?\s*((?:shall\s+)?(?:mean|means|has\s+the\s+meaning|refers\s+to|shall\s+refer\s+to)\b[^\n]{20,600}?[.;])', re.S)
SENT = re.compile(r"(?<=[.!?;])\s+(?=[A-Z(\"“])")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="data/raw/CUADv1.json")
    ap.add_argument("--out", default="data/cuad_full")
    ap.add_argument("--min-tf", type=int, default=3)
    ap.add_argument("--max-occ", type=int, default=60, help="max occurrences retained per term (prevents a few terms from overwhelming the set; 60 covers all occurrences for 95% of terms)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    data = json.load(open(a.json))["data"]
    tf_all, terms, occs = [], [], []
    n_def_contracts = 0
    for ci, c in enumerate(data):
        text = c["paragraphs"][0]["context"]; title = c.get("title", f"contract{ci}")
        defs = {}
        for t, d in DEF.findall(text):
            t = t.strip()
            if re.search(r"has the meaning (ascribed|set forth|given|assigned|specified|provided|defined)|as defined in|shall have the meaning", d, re.I):
                continue
            if t not in defs and len(d) >= 40:
                defs[t] = re.sub(r"\s+", " ", d).strip()
        if not defs:
            continue
        n_def_contracts += 1
        sents = [s.strip() for s in SENT.split(re.sub(r"\s+", " ", text)) if 6 <= len(s.split()) <= 80]
        for t, d in defs.items():
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(t) + r"(?![A-Za-z0-9_])")
            hits = [s for s in sents if pat.search(s) and d[:50] not in s]
            tf_all.append(len(hits))
            if len(hits) < a.min_tf:
                continue
            hits = hits[: a.max_occ]
            z = min((zipf_frequency(w, "en") for w in t.split()), default=0) if zipf_frequency else 0
            tid = f"cuadfull:{ci}:{t}"
            terms.append({"id": tid, "term": t, "contract": title, "contexts": hits, "def_raw": d,
                          "labels": {"tf": len(hits), "zipf": round(z, 2), "n_words": len(t.split()), "ci": ci}})
            for k, s in enumerate(hits):
                occs.append({"id": tid, "term": t, "ci": ci, "occ_idx": k, "sent": s})
    with open(os.path.join(a.out, "terms_full.jsonl"), "w", encoding="utf-8") as f:
        for t in terms: f.write(json.dumps(t, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "occurrences.jsonl"), "w", encoding="utf-8") as f:
        for o in occs: f.write(json.dumps(o, ensure_ascii=False) + "\n")
    st = {"contracts": len(data), "contracts_with_defs": n_def_contracts, "defined_terms_seen": len(tf_all),
          "terms_kept": len(terms), "occurrences": len(occs),
          "capped_terms": sum(1 for t in terms if t["labels"]["tf"] == a.max_occ)}
    json.dump(st, open(os.path.join(a.out, "stats.json"), "w"), indent=1)
    print(json.dumps(st))

if __name__ == "__main__":
    main()