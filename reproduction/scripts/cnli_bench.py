#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContractNLI external-comprehension benchmark (W1 construct gap): full NDA text (~1.5k words, entire document in context) × 17 human-written hypotheses × human three-way labels.
Adjudication depends on each NDA's specific definition of "Confidential Information" (or its aliases) — precisely “redefining common terms”.

Arms (same reader, same document, only annotations differ):
  plain      original text
  note_gated inline note [term: definition summary] inserted immediately after each occurrence of a defined term with agent risk ≥ --risk-th (occurrence-level carrier, Q14 form)
  note_all   inline notes at every occurrence of every defined term ("full" comparison)
Preregistered: H1 note_gated accuracy/macro-F1 ≥ plain, gains concentrated in NDAs where key terms carry high risk; note_gated ≈ note_all but with fewer annotation tokens.
        H2 plain arm's error rate correlates positively with NDA key-term risk. Both outcomes reported as observed.
Input: docs.jsonl / hypotheses.json (prepare_cnli.py), terms_full.jsonl + lpmc (risk produced by t1_draft → run_logprob_mc).
"""
import argparse, json, os, random, re, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env
from rag_harness import toks

SYS = ("You are a careful legal analyst. Read the NDA and decide whether the hypothesis is Entailment (the NDA says so), "
       "Contradiction (the NDA says the opposite), or NotMentioned (the NDA does not address it). Answer with exactly one word: "
       "Entailment, Contradiction, or NotMentioned.")
KEY = {"Confidential Information", "Proprietary Information", "Evaluation Material", "Evaluation Materials", "Information"}

def annotate(text, notes, cap=4):
    """notes: {term: def_snippet}; insert [term: snippet] after each occurrence, ≤cap times per term, skipping the definition sentence itself."""
    out = text; added = 0
    for term, snip in sorted(notes.items(), key=lambda kv: -len(kv[0])):
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])")
        n = 0; pos = 0; pieces = []
        for m in pat.finditer(out):
            if n >= cap: break
            window = out[max(0, m.start()-60): m.end()+60]
            if re.search(r"\b(means?|shall mean|defined|includes?)\b", window, re.I): continue
            pieces.append(out[pos:m.end()]); pieces.append(f" [{term}: {snip}]"); pos = m.end(); n += 1; added += 1
        pieces.append(out[pos:]); out = "".join(pieces)
    return out, added

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="data/cnli/docs.jsonl"); ap.add_argument("--hyps", default="data/cnli/hypotheses.json")
    ap.add_argument("--terms", default="data/cnli/terms_full.jsonl"); ap.add_argument("--risk", default="data/cnli/lpmc_cnli.jsonl")
    ap.add_argument("--out", required=True); ap.add_argument("--arms", default="plain,note_gated,note_all")
    ap.add_argument("--risk-th", type=float, default=0.5); ap.add_argument("--n-docs", type=int, default=180)
    ap.add_argument("--snip", type=int, default=220); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--cache-dir", default="data/cache_cnli")
    a = ap.parse_args(); os.makedirs(a.cache_dir, exist_ok=True); rng = random.Random(a.seed)
    cli = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    H = json.load(open(a.hyps, encoding="utf-8"))
    T = [json.loads(l) for l in open(a.terms, encoding="utf-8")]
    LP = {json.loads(l)["id"]: json.loads(l) for l in open(a.risk, encoding="utf-8")} if os.path.exists(a.risk) else {}
    if not LP and not a.mock: sys.exit("[cnli] risk file missing — run t1_draft.py + run_logprob_mc.py first")
    risk = defaultdict(dict); defs = defaultdict(dict)
    for t in T:
        lp = LP.get(t["id"], {}).get("per_question") or []
        r = sum(1 - p["bare"]["p_correct"] for p in lp if "bare" in p)/len(lp) if lp else (0.6 if a.mock else None)
        risk[str(t["contract"])][t["term"]] = r
        d = (t.get("def_raw") or "").strip(); d = re.sub(r"\s+", " ", d)
        defs[str(t["contract"])][t["term"]] = d[: a.snip] + ("…" if len(d) > a.snip else "")
    D = [json.loads(l) for l in open(a.docs, encoding="utf-8")]
    D = [d for d in D if any(k in d["defs"] for k in KEY) and str(d["ci"]) in defs]
    rng.shuffle(D); D = D[: a.n_docs]
    def key_risk(ci):
        vals = [risk[ci][t] for t in risk[ci] if t in KEY and risk[ci][t] is not None]
        return max(vals) if vals else None
    print(f"[cnli] NDAs {len(D)} | hypotheses {len(H)} | with key-term risk {sum(1 for d in D if key_risk(str(d['ci'])) is not None)}", file=sys.stderr)
    arms = a.arms.split(","); reqs, owners = [], []
    for d in D:
        ci = str(d["ci"]); variants = {"plain": (d["text"], 0)}
        gated = {t: defs[ci][t] for t in defs[ci] if (risk[ci].get(t) or 0) >= a.risk_th}
        if "note_gated" in arms: variants["note_gated"] = annotate(d["text"], gated)
        if "note_all" in arms: variants["note_all"] = annotate(d["text"], dict(defs[ci]))
        for hid, lab in d["labels"].items():
            hyp = H[hid]["hypothesis"]
            for arm in arms:
                doc, n_notes = variants[arm]
                prompt = f"NDA:\n\"\"\"\n{doc}\n\"\"\"\n\nHypothesis: {hyp}\nAnswer (Entailment / Contradiction / NotMentioned):"
                reqs.append(dict(prompt=prompt, system=SYS, max_tokens=6, temperature=0.0))
                owners.append((ci, hid, lab, arm, n_notes, len(toks(doc)) - len(toks(d["text"]))))
    print(f"[cnli] {len(D)} NDAs × {len(H)} hyps × {len(arms)} arms = {len(reqs)} calls", file=sys.stderr)
    outs = []
    for i in range(0, len(reqs), 100):
        outs.extend(cli.complete_many(reqs[i:i+100])); print(f"\r[cnli] {min(i+100, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    def parse(o):
        o = str(o or "").lower()
        return "Entailment" if "entail" in o else "Contradiction" if "contradict" in o else "NotMentioned" if "not" in o else None
    agg = defaultdict(list)
    with open(a.out, "w", encoding="utf-8") as f:
        for (ci, hid, lab, arm, nn, ntok), o in zip(owners, outs):
            pred = parse(o); corr = int(pred == lab)
            f.write(json.dumps({"ci": ci, "hyp": hid, "gold": lab, "arm": arm, "pred": pred, "correct": corr,
                                "key_risk": key_risk(ci), "n_notes": nn, "note_tokens": ntok}) + "\n")
            agg[arm].append((corr, key_risk(ci), lab, pred, ntok))
    m = lambda v: sum(v)/len(v) if v else float("nan")
    def macro_f1(rows):
        f1s = []
        for c in ("Entailment", "Contradiction", "NotMentioned"):
            tp = sum(1 for _, _, g, p, _ in rows if g == c and p == c); fp = sum(1 for _, _, g, p, _ in rows if g != c and p == c)
            fn = sum(1 for _, _, g, p, _ in rows if g == c and p != c)
            pr = tp/(tp+fp) if tp+fp else 0; rc = tp/(tp+fn) if tp+fn else 0; f1s.append(2*pr*rc/(pr+rc) if pr+rc else 0)
        return sum(f1s)/3
    print(f"\n{'arm':11s} {'acc':>6s} {'macroF1':>8s} {'acc@hi-risk NDA':>16s} {'acc@lo-risk NDA':>16s} {'note-tok':>9s}", file=sys.stderr)
    for arm in arms:
        rows = agg[arm]
        hi = [c for c, r, *_ in rows if (r or 0) >= a.risk_th]; lo = [c for c, r, *_ in rows if r is not None and r < a.risk_th]
        print(f"{arm:11s} {m([c for c,*_ in rows]):6.3f} {macro_f1(rows):8.3f} {m(hi):16.3f} {m(lo):16.3f} {m([x[4] for x in rows]):9.0f}", file=sys.stderr)

if __name__ == "__main__":
    main()