#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContractNLI preparation (external comprehension-type benchmark, W1 construct gap):
  (1) Merge NDAs from train/dev/test; (2) extract defined terms ("X" means / shall mean …) per NDA and all sentences where they occur;
  (3) Output terms_full format directly consumable by t1_draft.py (id/term/contract/contexts/def_raw/labels) + docs.jsonl (for NLI).
Sampling: --n-docs NDAs (default 150, fixed seed); keep only core redefinition terms (Confidential Information / Receiving Party /
Disclosing Party / Representatives / Affiliate(s) / Purpose / Agreement) and other defined terms with tf≥3.
"""
import argparse, glob, json, os, random, re
DEF_PAT = re.compile(r'(?:[“"]|\bterm\s+[“"]?)([A-Z][A-Za-z][A-Za-z \-/]{1,40})[”"]?\s*(?:\)|,)?\s*(?:\(?as used (?:herein|in this Agreement)\)?,?\s*)?(?:shall\s+)?(?:mean|means|refer to|refers to|includes?|has the meaning|is defined as|shall be defined as|shall include|will mean)\b([^.;]{10,600})', re.S)
CORE = {"Confidential Information", "Proprietary Information", "Evaluation Material", "Evaluation Materials", "Information", "Receiving Party", "Disclosing Party", "Recipient", "Representatives", "Affiliate", "Affiliates", "Purpose", "Agreement"}
def sents(text):
    return [s.strip() for s in re.split(r"(?<=[.;:])\s+(?=[A-Z(\"“])", re.sub(r"\s+", " ", text)) if 12 <= len(s.split()) <= 80]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="../cnli/contract-nli"); ap.add_argument("--out", default="data/cnli")
    ap.add_argument("--n-docs", type=int, default=150); ap.add_argument("--min-tf", type=int, default=3)
    ap.add_argument("--max-occ", type=int, default=8); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); rng = random.Random(a.seed)
    docs, labels = [], None
    for f in sorted(glob.glob(os.path.join(a.src, "*.json"))):
        D = json.load(open(f, encoding="utf-8")); docs += D["documents"]; labels = labels or D["labels"]
    rng.shuffle(docs); docs = docs[: a.n_docs]
    terms, n_def = [], 0
    with open(os.path.join(a.out, "docs.jsonl"), "w", encoding="utf-8") as fd:
        for d in docs:
            ci = d["id"]; text = re.sub(r"\s+", " ", d["text"]); ss = sents(text)
            defs = {}
            for m in DEF_PAT.finditer(text):
                t = m.group(1).strip()
                if t not in defs and (t in CORE or len(t.split()) <= 3): defs[t] = (m.group(0)[:700]).strip()
            ann = d["annotation_sets"][0]["annotations"]
            fd.write(json.dumps({"ci": ci, "file": d["file_name"], "text": text, "defs": defs,
                                 "labels": {h: v["choice"] for h, v in ann.items()}}, ensure_ascii=False) + "\n")
            for t, dr in defs.items():
                pat = re.compile(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])")
                ctx = [s for s in ss if pat.search(s) and not DEF_PAT.search(s)]
                if len(ctx) < a.min_tf and t not in CORE: continue
                rng.shuffle(ctx); n_def += 1
                terms.append({"id": f"cnli:{ci}:{t}", "term": t, "contract": ci, "contexts": ctx[: a.max_occ],
                              "def_raw": dr, "gloss_gold": dr, "labels": {"ci": ci, "tf": len(ctx), "core": t in CORE}})
    with open(os.path.join(a.out, "terms_full.jsonl"), "w", encoding="utf-8") as f:
        for t in terms: f.write(json.dumps(t, ensure_ascii=False) + "\n")
    json.dump(labels, open(os.path.join(a.out, "hypotheses.json"), "w", encoding="utf-8"), indent=1)
    from collections import Counter
    print(json.dumps({"docs": len(docs), "terms": len(terms), "core_terms": sum(1 for t in terms if t["labels"]["core"]),
                      "occurrences": sum(len(t["contexts"]) for t in terms),
                      "docs_with_CI_def": sum(1 for t in terms if t["term"] == "Confidential Information"),
                      "top_terms": Counter(t["term"] for t in terms).most_common(8)}, ensure_ascii=False))
if __name__ == "__main__":
    main()