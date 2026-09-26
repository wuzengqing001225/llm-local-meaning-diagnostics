#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TechQA (IBM, real user questions + human-annotated Technote answer spans) × W1 screening. Criterion (a) human-written ✓ already satisfied; this script checks (b)(c).

Stage A (--stage a, local, zero API):
  1. Candidate "everyday words redefined by product usage": words significantly overrepresented in the Technote corpus relative to general English (zipf ≥ --min-zipf), e.g. queue / channel / listener / agent / node / broker.
  2. Coverage: among answerable questions, the fraction of question text / answer span / both containing ≥1 candidate word; answer span morphology (length, command/path ratio → locating-type vs meaning-type).
  3. Produce data/techqa/terms.jsonl + corpus.jsonl in our pipeline format (term = candidate word, context = Technote sentence), for stage B to compute PD via run_local.
Stage C (--stage c, after stage B has run):
  Using term-level PD / channel from runs/local/<reader>/techqa/{weights,eqa}.jsonl, go back to human-written questions: fraction of questions containing high-PD words, fraction of answer spans containing high-PD words → whether (c) holds.
Usage:
  python3 techqa_screen.py --stage a --techqa <extracted TechQA directory> --out data/techqa
  python3 techqa_screen.py --stage c --techqa <directory> --run runs/local/deepseek/techqa --out data/techqa
"""
import argparse, glob, json, math, os, re, sys
from collections import Counter, defaultdict
try:
    from wordfreq import zipf_frequency
except ImportError:
    print("pip install wordfreq", file=sys.stderr); raise

def find(root, pat):
    hits = [p for p in glob.glob(os.path.join(root, "**", pat), recursive=True) if "._" not in os.path.basename(p)]
    return sorted(hits)

def kget(d, *names):
    low = {k.lower(): k for k in d}
    for n in names:
        if n.lower() in low: return d[low[n.lower()]]
    return None

def load_qa(root):
    out = []
    for p in find(root, "*Q_A.json") + find(root, "*Q_A*.jsonl"):
        raw = json.load(open(p, encoding="utf-8")) if p.endswith(".json") else [json.loads(l) for l in open(p, encoding="utf-8")]
        items = raw if isinstance(raw, list) else (raw.get("data") or list(raw.values()))
        for it in items:
            if not isinstance(it, dict): continue
            ans = kget(it, "ANSWER", "answer"); answerable = kget(it, "ANSWERABLE", "answerable")
            out.append(dict(split=os.path.basename(p), qid=kget(it, "QUESTION_ID", "id"), title=kget(it, "QUESTION_TITLE", "title") or "",
                            text=kget(it, "QUESTION_TEXT", "question", "text") or "", doc=kget(it, "DOCUMENT", "doc_id"),
                            answer=ans or "", answerable=(str(answerable).upper() in ("Y", "YES", "TRUE", "1")) if answerable is not None else bool(ans)))
    if out: print(f"[qa] {len(out)} questions from {len(find(root, '*Q_A.json'))} files; example keys ok", file=sys.stderr)
    return out

def load_notes(root):
    p = find(root, "training_dev_technotes.json")
    if not p: sys.exit("cannot find training_dev_technotes.json (under training_and_dev_MRC/)")
    raw = json.load(open(p[0], encoding="utf-8")); notes = {}
    items = raw.items() if isinstance(raw, dict) else ((kget(x, "id", "doc_id"), x) for x in raw)
    for k, v in items:
        if isinstance(v, dict): notes[k] = (kget(v, "title") or "") + "\n" + (kget(v, "text", "content", "body") or "")
        else: notes[k] = str(v)
    print(f"[notes] {len(notes)} technotes", file=sys.stderr); return notes

WORD = re.compile(r"[A-Za-z][a-z]{2,}")
STOP = set("the and for with that this from are was were you your can will not have has been but all any our use used using when which while where there their than then them they into also may should would could about after before between during each more most other some such these those only over under into upon".split())
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])|\n+")

def stage_a(a):
    qa = load_qa(a.techqa); notes = load_notes(a.techqa)
    # 1) Candidate words: Technote document frequency vs general frequency
    df = Counter(); ndoc = 0; cap = Counter(); tot = Counter()
    MID = re.compile(r"(?<![.!?:]\s)(?<!\n)(?<!^)(?<![.!?:])\b([A-Za-z][a-z]{2,})\b")
    for t in notes.values():
        ndoc += 1; df.update({w.lower() for w in WORD.findall(t)})
        # capitalization ratio for mid-sentence (non-sentence-initial) occurrences: product component names / defined terms (Fix Pack, Cell, Node, Profile) tend to appear capitalized
        for mm in MID.finditer(t):
            w = mm.group(1); tot[w.lower()] += 1
            if w[0].isupper(): cap[w.lower()] += 1
    cands = []
    IT_GENERIC = set("com http https www java html xml json sql php exe dll jar zip url ftp ssl tcp ip api cpu gpu ram usb pdf gov org net edu".split())
    NAMES = set("january february march april may june july august september october november december jan feb mar apr jun jul aug sep sept oct nov dec monday tuesday wednesday thursday friday saturday sunday "
                "english chinese japanese german french spanish russian italian korean portuguese dutch american canada france paris america india china japan europe asia "
                "how why what when where which who thanks however yes none inc pro john ibm microsoft google apple oracle linux unix".split())
    # occurrence count in human-written questions (lowercased): candidate word must appear in ≥ --min-q questions, otherwise it is irrelevant to (c)
    qcount = Counter()
    for q in qa:
        qcount.update({w.lower() for w in WORD.findall(q["title"] + " " + q["text"])})
    for w, c in df.items():
        if w in STOP or w in IT_GENERIC or w in NAMES or c < a.min_df: continue
        if qcount[w] < a.min_q: continue
        if c > a.max_df_frac * ndoc: continue             # boilerplate text (footer appearing in every document: united states, etc.)
        z = zipf_frequency(w, "en")
        if z < a.min_zipf: continue                       # keep only everyday common words (rare words are the unknown channel, not the target of this screen)
        cr = cap[w] / tot[w] if tot[w] >= a.min_df else 0.0
        cands.append((w, c, z, cr))
    # keep "mixed-usage" words: mid-sentence capitalization ratio within [min_cap, max_cap] -- used both as an ordinary word and as a name/defined term (always-capitalized words are just proper nouns, readers' prior is unknown, not redefinition)
    band = [x for x in cands if a.min_cap <= x[3] <= a.max_cap]
    band.sort(key=lambda x: (-qcount[x[0]], -x[3]))          # sort by occurrence count in human-written questions (directly relevant to (c))
    top = [w for w, *_ in band[:a.top_k]]
    print(f"\n[cands] {len(cands)} everyday words (zipf≥{a.min_zipf}, df≥{a.min_df}, in ≥{a.min_q} questions); {len(band)} with mixed-case usage cap∈[{a.min_cap:.2f},{a.max_cap:.2f}] (kept, top-{a.top_k}, sorted by #questions):", file=sys.stderr)
    print("  " + ", ".join(f"{w}(q{qcount[w]},cap{cr:.2f})" for w, c, z, cr in band[:a.top_k]), file=sys.stderr)
    cands = [x for x in cands if x[0] in set(top)]
    # 2) Coverage
    A = [q for q in qa if q["answerable"] and q["answer"]]
    def has(s): return {w for w in (x.lower() for x in WORD.findall(s)) if w in top}
    cq = [has(q["title"] + " " + q["text"]) for q in A]; ca = [has(q["answer"]) for q in A]
    both = sum(1 for x, y in zip(cq, ca) if x and y)
    L = sorted(len(q["answer"].split()) for q in A)
    codey = [len(re.findall(r"[/\\=_\-]|\b[A-Z]{2,}\b|\d", q["answer"])) / max(1, len(q["answer"].split())) for q in A]
    print(f"\n[coverage] answerable={len(A)}/{len(qa)} | question has cand: {sum(1 for x in cq if x)/len(A):.2f} | answer span has cand: {sum(1 for x in ca if x)/len(A):.2f} | both: {both/len(A):.2f}", file=sys.stderr)
    print(f"[answer span] words median {L[len(L)//2]} p90 {L[int(.9*len(L))]} | code/path/number density median {sorted(codey)[len(codey)//2]:.2f} (high = locating/command type)", file=sys.stderr)
    hit = Counter(w for s in cq for w in s); print("[most frequent cands in questions]", hit.most_common(25), file=sys.stderr)
    # 3) pipeline-format output
    os.makedirs(a.out, exist_ok=True)
    sents_by = defaultdict(list)
    for did, t in notes.items():
        for s in SENT.split(t):
            s = s.strip()
            if 40 <= len(s) <= 400:
                for w in set(x.lower() for x in WORD.findall(s)):
                    if w in top and len(sents_by[w]) < 400: sents_by[w].append(s)
    with open(os.path.join(a.out, "terms.jsonl"), "w", encoding="utf-8") as f:
        for w, c, z, l in cands:
            ctx = sents_by.get(w, [])[:a.max_ctx]
            if len(ctx) < 5: continue
            f.write(json.dumps(dict(id=f"techqa:{w}", term=w, lang="en", contexts=ctx, gloss_gold=None,
                                    labels=dict(source="techqa", quadrant="unknown", tier="unknown", tf=c, zipf=z, cap_ratio=round(l, 2), is_target=True, variant="main")), ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "corpus.jsonl"), "w", encoding="utf-8") as f:
        for did, t in list(notes.items())[:a.max_docs]: f.write(json.dumps(dict(doc_id=did, text=t[:20000]), ensure_ascii=False) + "\n")
    json.dump(dict(candidates=[dict(term=w, df=c, zipf=z, cap_ratio=round(l, 2)) for w, c, z, l in cands], n_answerable=len(A),
                   q_cov=sum(1 for x in cq if x)/len(A), a_cov=sum(1 for x in ca if x)/len(A), both=both/len(A)),
              open(os.path.join(a.out, "stage_a.json"), "w"), indent=1)
    print(f"[out] {a.out}/terms.jsonl, corpus.jsonl, stage_a.json", file=sys.stderr)
    print("\nInterpretation: both ≥ 0.25 and answer-span code density median < 0.3 → worth advancing to stage B; both < 0.10 or density > 0.5 → locating-type task (same shape as CUAD extraction), stop.", file=sys.stderr)

def stage_c(a):
    qa = [q for q in load_qa(a.techqa) if q["answerable"] and q["answer"]]
    wp = a.run if a.run.endswith(".jsonl") else os.path.join(a.run, "weights.jsonl")
    W = {json.loads(l)["term"]: json.loads(l) for l in open(wp, encoding="utf-8")}
    a.run = os.path.dirname(wp) if a.run.endswith(".jsonl") else a.run
    E = {}
    for fn in ("eqa_usage.jsonl", "eqa.jsonl", "eqa_gold.jsonl"):
        p = os.path.join(a.run, fn)
        if os.path.exists(p): E = {json.loads(l)["term"]: json.loads(l) for l in open(p, encoding="utf-8")}; break
    pd = {t: (E[t].get("deficit_qa") if t in E else None) for t in W}
    ch = {t: (E[t].get("channel_qa") if t in E else None) for t in W}
    print(f"[terms] {len(W)} scored; channel dist {Counter(ch.values())}" if E else f"[terms] {len(W)} scored (detection layer only)", file=sys.stderr)
    tier = {t: W[t].get("tier") for t in W}
    div = {t for t, v in tier.items() if v in ("shifted", "narrower", "opposite", "unknown")}
    print(f"[detection] tiers {Counter(tier.values())} | divergent (shifted/narrower/opposite/unknown): {len(div)}: {sorted(div)[:60]}", file=sys.stderr)
    if E:
        hi = {t for t, v in pd.items() if v is not None and v >= a.hi}
        print(f"[high-PD terms fail≥{a.hi}] {len(hi)}: {sorted(hi)[:40]}", file=sys.stderr)
    else:
        hi = div; print("[note] no eqa file → using detection-layer divergent terms as the high set", file=sys.stderr)
    def has(s, S): return {w for w in (x.lower() for x in WORD.findall(s)) if w in S}
    q_div = [q for q in qa if has(q["title"] + " " + q["text"], div)]; a_div = [q for q in qa if has(q["answer"], div)]
    print(f"[intersection/detection] questions touching divergent terms: {len(q_div)/len(qa):.2f} | answer spans: {len(a_div)/len(qa):.2f} | both: {sum(1 for q in q_div if has(q['answer'], div))/len(qa):.2f}", file=sys.stderr)
    print("[divergent terms most frequent in questions]", Counter(w for q in qa for w in has(q["title"] + " " + q["text"], div)).most_common(25), file=sys.stderr)
    q_hi = [q for q in qa if has(q["title"] + " " + q["text"], hi)]; a_hi = [q for q in qa if has(q["answer"], hi)]
    both = [q for q in q_hi if has(q["answer"], hi)]
    print(f"[intersection] questions touching high-PD terms: {len(q_hi)/len(qa):.2f} | answer spans: {len(a_hi)/len(qa):.2f} | both: {len(both)/len(qa):.2f} (n={len(qa)})", file=sys.stderr)
    conf = {t for t, c in ch.items() if c == "conflict"}
    if E: print(f"[conflict-channel terms in questions] {sum(1 for q in qa if has(q['title']+' '+q['text'], conf))/len(qa):.2f}", file=sys.stderr)
    with open(os.path.join(a.out, "stage_c_questions.jsonl"), "w", encoding="utf-8") as f:
        for q in both: f.write(json.dumps(dict(q, hi_terms=sorted(has(q["title"] + " " + q["text"] + " " + q["answer"], hi))), ensure_ascii=False) + "\n")
    print("Interpretation: both ≥ 0.2 → phenomenon intersects with human-written tasks, proceed to three-arm (plain / note_gated / note_all, answer-span F1); otherwise same as CUAD extraction, record as the fourth null and write up the reason.", file=sys.stderr)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["a", "c"], required=True); ap.add_argument("--techqa", required=True); ap.add_argument("--out", default="data/techqa")
    ap.add_argument("--run", default="runs/local/deepseek/techqa"); ap.add_argument("--min-zipf", type=float, default=4.2); ap.add_argument("--min-df", type=int, default=30)
    ap.add_argument("--top-k", type=int, default=150); ap.add_argument("--min-cap", type=float, default=0.15); ap.add_argument("--max-cap", type=float, default=0.90); ap.add_argument("--min-q", type=int, default=3); ap.add_argument("--max-df-frac", type=float, default=0.35); ap.add_argument("--max-ctx", type=int, default=16); ap.add_argument("--max-docs", type=int, default=3000); ap.add_argument("--hi", type=float, default=0.5)
    a = ap.parse_args(); stage_a(a) if a.stage == "a" else stage_c(a)
