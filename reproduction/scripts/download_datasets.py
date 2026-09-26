#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download and convert public datasets into unified PDW format (zero manual annotation).

  NEO-BENCH (Zheng, Ritter, Xu, ACL 2024) -> data/neobench_terms.jsonl
      Per neologism: contexts (minimal pair sentence + cloze sentence fill-back), gloss_gold (reference definition),
      labels.category in {lexical, morphological, semantic}, labels.quadrant mapping:
        semantic          -> prior_conflict   (existing word gains new sense: prior exists and conflicts)
        lexical/new phrase, morphological/* -> guessable (new form with guessable components)
        lexical/acronym, novel word, etc.   -> no_prior  (new form, not guessable)
      Negative controls are extracted from minimal pair sentence 2 by taking the substituted word: labels.quadrant = prior_consistent, is_target=false.
      Note: this mapping is an approximation of the dataset's original classification; the semantic class has only 87 items, and many sentences are definitional (high inferability).

  TempoWiC (Loureiro et al., 2022) -> data/tempowic_pairs.jsonl
      Two tweets with the same word, human-annotated for whether the meaning matches -> validation judge (ERROR_STANDARD J1).

Usage: python3 download_datasets.py --out data
"""
import argparse
import difflib
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

NEO_ZIP = "https://codeload.github.com/JonathanQZheng/NEO-BENCH/zip/refs/heads/main"
TWIC_ZIP = "https://codeload.github.com/cardiffnlp/TempoWiC/zip/refs/heads/main"


def fetch_zip(url, dest_dir, marker):
    if os.path.exists(os.path.join(dest_dir, marker)):
        return
    print(f"[download] {url}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as r:
        buf = io.BytesIO(r.read())
    with zipfile.ZipFile(buf) as z:
        z.extractall(dest_dir)


def quadrant_for(ltype, sub):
    ltype = (ltype or "").lower()
    sub = (sub or "").lower()
    if ltype == "semantic":
        return "prior_conflict"
    if ltype == "morphological":
        return "guessable"
    if ltype == "lexical":
        return "guessable" if "phrase" in sub else "no_prior"
    return "unlabeled"


def substitute_span(s1, s2):
    """S1 contains the neologism, S2 has an existing word substituted at the same position: extract the replaced span in S2 (1-4 words)."""
    if not s1 or not s2:
        return None
    a, b = s1.split(), s2.split()
    sm = difflib.SequenceMatcher(a=[w.lower() for w in a], b=[w.lower() for w in b])
    repl = [(j1, j2) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag == "replace"]
    if len(repl) != 1:
        return None
    j1, j2 = repl[0]
    span = " ".join(b[j1:j2]).strip(" ,.;:!?\"'()")
    return span if 1 <= len(span.split()) <= 4 and span.lower() not in s1.lower() else None


def convert_neobench(root, out_path):
    import openpyxl
    path = os.path.join(root, "NEO-BENCH-main", "Inputs.xlsx")
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0]
    idx = {}
    for i, h in enumerate(hdr):
        if h and h not in idx:
            idx[h] = i
    n_pos = n_neg = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for r in rows[1:]:
            term = (r[idx["Neologism"]] or "").strip() if r[idx["Neologism"]] else ""
            ltype = r[idx["Linguistic Type"]]
            if not term or not ltype:
                continue
            s1 = (r[idx["Minimal Pair Sentence 1"]] or "").strip()
            s2 = (r[idx["Minimal Pair Sentence 2"]] or "").strip()
            contexts = []
            if s1 and re.search(re.escape(term), s1, re.IGNORECASE):
                contexts.append(s1)
            for col in ("CLOZE Sentence 1", "CLOZE Sentence 2"):
                c = (r[idx[col]] or "").strip()
                if "___" in c:
                    contexts.append(c.replace("___", term))
            if not contexts:
                continue
            entry = {
                "id": f"neo:{term}", "term": term, "lang": "en",
                "contexts": contexts, "gloss_gold": (r[idx["Definition"]] or "").strip() or None,
                "labels": {"source": "neobench", "category": ltype,
                           "subcategory": r[idx["Linguistic Subcategory"]],
                           "quadrant": quadrant_for(ltype, r[idx["Linguistic Subcategory"]]),
                           "is_target": True, "n_words": len(term.split())},
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            n_pos += 1
            sub = substitute_span(s1, s2)
            if sub:
                neg = {
                    "id": f"neo-sub:{sub}", "term": sub, "lang": "en",
                    "contexts": [s2], "gloss_gold": None,
                    "labels": {"source": "neobench", "category": "substitute", "subcategory": None,
                               "quadrant": "prior_consistent", "is_target": False,
                               "paired_with": term, "n_words": len(sub.split())},
                }
                f.write(json.dumps(neg, ensure_ascii=False) + "\n")
                n_neg += 1
    print(f"[neobench] {n_pos} neologisms + {n_neg} substitute negatives -> {out_path}", file=sys.stderr)


def convert_tempowic(root, out_path):
    base = os.path.join(root, "TempoWiC-main", "data")
    n = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for split, dfile, lfile in (("validation", "validation.data.jl", "validation.labels.tsv"),
                                    ("trial", "trial.data.jl", "trial.gold.tsv")):
            labels = {}
            with open(os.path.join(base, lfile), encoding="utf-8") as lf:
                for line in lf:
                    p = line.strip().split("\t")
                    if len(p) == 2:
                        labels[p[0]] = int(p[1])
            with open(os.path.join(base, dfile), encoding="utf-8") as df:
                for line in df:
                    o = json.loads(line)
                    if o["id"] not in labels:
                        continue
                    f.write(json.dumps({"id": o["id"], "split": split, "word": o["word"],
                                        "text1": o["tweet1"]["text"], "text2": o["tweet2"]["text"],
                                        "same_meaning": labels[o["id"]]}, ensure_ascii=False) + "\n")
                    n += 1
    print(f"[tempowic] {n} usage pairs -> {out_path}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    args = ap.parse_args()
    raw = os.path.join(args.out, "raw")
    os.makedirs(raw, exist_ok=True)
    fetch_zip(NEO_ZIP, raw, "NEO-BENCH-main/Inputs.xlsx")
    fetch_zip(TWIC_ZIP, raw, "TempoWiC-main/data/validation.data.jl")
    convert_neobench(raw, os.path.join(args.out, "neobench_terms.jsonl"))
    convert_tempowic(raw, os.path.join(args.out, "tempowic_pairs.jsonl"))


if __name__ == "__main__":
    main()