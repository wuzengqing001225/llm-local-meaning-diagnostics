#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthetic world v1: expand sentences (with meaning_span), MC QA, and standard-sense sentences (for mixture variants) from the seeds_v1 spec using a generation model,
code-side validation (span occurs in sentence, does not contain the term, no ≥3-gram overlap with gloss, sentence does not restate the definition), judge consistency audit, output in the same format as v0.1.

Usage (inside python kernel via runpy; generation model = LLM_MODEL, audit = JUDGE_MODEL):
  python3 gen_world_v1.py --domain desk --out data/v1 [--mock]
Output: data/v1/{domain}_terms.jsonl, {domain}_corpus.jsonl, {domain}_distractor_qa.jsonl, {domain}_gen_report.json
"""
import argparse
import json
import os
import random
import re
import sys

_sys_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _sys_dir)
from pdwlib.llm import client_from_env, MockClient  # noqa
from pdwlib.text import extract_json, norm_tokens, find_term  # noqa
from seeds_v1 import SEEDS, DOMAINS, QUERY_FREQ_RULE  # noqa

GEN_PROMPT = """You are writing realistic internal documents for this organisation: {domain}.

{meaning_block}
Write a JSON object with these fields:

"sentences": a list of {n_sent} distinct sentences from internal notes/chat/reports that USE the term "{term}" in its INTERNAL meaning.
   Rules: (1) each sentence contains the exact token "{term}" once; (2) NEVER define, explain or paraphrase the term — the sentences
   must read like normal operational text written by insiders who take the meaning for granted; (3) vary style: chat lines,
   log entries, report sentences, questions; include concrete numbers, names, dates; (4) {rule4} (5) do NOT reuse the wording of the
   INTERNAL MEANING above — use different words for the same idea.
"spans": a list aligned with "sentences": for each sentence, copy EXACTLY (character for character) a short phrase (2–6 words)
   from that sentence that a reader can only predict correctly if they understand the internal meaning. The span must NOT
   contain the term "{term}", must not be a number, name or date, and must not appear in the INTERNAL MEANING text.
"qa": a list of {n_qa} multiple-choice questions about a concrete situation in these documents whose correct answer depends on
   the INTERNAL meaning of "{term}". Each item: {{"q": "...", "options": ["...","...","...","..."], "answer": "A"|"B"|"C"|"D"}}.
   Exactly one correct option. {distractor_rule} Do not include the internal meaning in the question text.
{standard_block}
Output JSON only."""

MEANING_CONFLICT = """In these documents the term "{term}" has a SPECIFIC internal meaning:
  INTERNAL MEANING: {corpus}
  STANDARD MEANING (what outsiders would assume): {standard}"""
MEANING_CONSISTENT = """In these documents the term "{term}" is used in its ordinary, standard sense. For the purposes of the JSON fields below,
treat this ordinary sense as the "INTERNAL MEANING":
  INTERNAL MEANING: {corpus}
(No divergence from common usage is intended; simply write natural internal documents that use the term correctly.)"""
MEANING_NOPRIOR = """In these documents the term "{term}" has a SPECIFIC internal meaning:
  INTERNAL MEANING: {corpus}
"""
RULE4_CONFLICT = "the sentence must be one where a\n   reader who assumed the STANDARD meaning would draw a wrong or nonsensical conclusion;"
RULE4_PLAIN = "the sentence must be one where a reader who does not know the meaning could not predict the span;"
STD_BLOCK = """"standard_sentences": a list of 6 sentences from the SAME organisation's documents where "{term}" is used in its
   ordinary STANDARD meaning (these will be mixed in to simulate mixed usage). Same style rules; each contains "{term}" once.
"standard_spans": aligned spans for standard_sentences, same rules.
"standard_qa": a list of 2 multiple-choice questions (same format) whose correct answer depends on the STANDARD meaning of "{term}" in an ordinary situation at this organisation."""
CONFLICT_DISTRACTOR = "One of the wrong options must be the answer a reader would give if they assumed the STANDARD meaning."
PLAIN_DISTRACTOR = "Wrong options must be plausible for someone who does not know the term."

DISTRACTOR_PROMPT = """Organisation: {domain}.
Write {n} multiple-choice questions about ordinary situations at this organisation whose answers depend only on common sense
and general knowledge — NOT on any internal jargon or redefined terms. Avoid using any of these words: {avoid}.
Format: JSON list of {{"q": "...", "options": ["...","...","...","..."], "answer": "A"|"B"|"C"|"D"}}. JSON only."""

AUDIT_PROMPT = """JUDGE_DEFINITION. Term: "{term}". Intended meaning of the term in the sentences below: {meaning}
For EACH numbered sentence decide: is it consistent with the intended meaning (a reader knowing that meaning finds it sensible),
and does it avoid explicitly defining the term? Answer with a JSON list of "CORRECT"/"INCORRECT" strings, one per sentence, in order.
{sentences}
JSON list only."""
AUDIT_BATCH = 8


def ngrams(toks, n=3):
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def validate(term, gloss, sents, spans):
    """Returns (list of qualifying (sentence, span) pairs, list of problems). When a span does not qualify, it is downgraded to None (falls back to window)."""
    out, problems = [], []
    g3 = ngrams(norm_tokens(gloss))
    seen = set()
    for i, s in enumerate(sents or []):
        s = (s or "").strip()
        if not s or s.lower() in seen:
            problems.append(f"dup/empty sentence {i}"); continue
        seen.add(s.lower())
        if not find_term(s, term):
            problems.append(f"term missing in sentence {i}"); continue
        if len(ngrams(norm_tokens(s)) & g3) >= 2:
            problems.append(f"sentence {i} paraphrases gloss"); continue
        sp = spans[i] if spans and i < len(spans) else None
        if sp:
            sp = sp.strip().strip('"').strip()
            ok = (sp in s) and (not find_term(sp, term)) and 1 <= len(norm_tokens(sp)) <= 7 \
                and not re.fullmatch(r"[\d\W]+", sp) and sp.lower() not in gloss.lower()
            if not ok:
                problems.append(f"span {i} rejected: {sp!r}"); sp = None
        out.append((s, sp))
    return out, problems


def validate_qa(qa, n_min):
    good = []
    for q in qa or []:
        try:
            opts = [str(o) for o in q["options"]]
            if len(opts) == 4 and str(q["answer"]).strip().upper()[:1] in "ABCD" and q.get("q"):
                good.append({"q": q["q"], "options": opts, "answer": str(q["answer"]).strip().upper()[:1]})
        except Exception:  # noqa
            pass
    return good


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, choices=list(DOMAINS))
    ap.add_argument("--out", default="data/v1")
    ap.add_argument("--n-sent", type=int, default=10)
    ap.add_argument("--n-qa", type=int, default=3)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cache-dir", default="data/v1/cache")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True); os.makedirs(args.cache_dir, exist_ok=True)
    gen = client_from_env("LLM", mock=args.mock, cache_path=os.path.join(args.cache_dir, "gen.jsonl"))
    judge = gen if (args.mock or not os.environ.get("JUDGE_MODEL")) else \
        client_from_env("JUDGE", cache_path=os.path.join(args.cache_dir, "judge.jsonl"))
    rng = random.Random(args.seed)
    dom = DOMAINS[args.domain]
    seeds = SEEDS[args.domain]
    report = {"domain": args.domain, "terms": {}}

    def build_prompt(sd, n_sent):
        conflict = sd["quadrant"] == "prior_conflict"
        if conflict:
            mb = MEANING_CONFLICT.format(term=sd["term"], corpus=sd["corpus"], standard=sd["standard"])
        elif sd["quadrant"] == "prior_consistent":
            mb = MEANING_CONSISTENT.format(term=sd["term"], corpus=sd["corpus"])
        else:
            mb = MEANING_NOPRIOR.format(term=sd["term"], corpus=sd["corpus"])
        return GEN_PROMPT.format(domain=dom, term=sd["term"], corpus=sd["corpus"], n_sent=n_sent, n_qa=args.n_qa,
                                 meaning_block=mb, rule4=RULE4_PLAIN if sd["quadrant"] == "prior_consistent" else RULE4_CONFLICT,
                                 distractor_rule=CONFLICT_DISTRACTOR if conflict else PLAIN_DISTRACTOR,
                                 standard_block=STD_BLOCK.format(term=sd["term"]) if conflict else "")

    def mock_pack(sd):
        n = args.n_sent
        s = [f"Log {i}: the {sd['term']} was noted by desk {i} at {9+i}:00 with {i*3} items pending review." for i in range(n)]
        sp = ["items pending review"] * n
        qa = [{"q": f"Q{i} about {sd['term']}?", "options": ["a", "b", "c", "d"], "answer": "A"} for i in range(args.n_qa)]
        d = {"sentences": s, "spans": sp, "qa": qa}
        if sd["quadrant"] == "prior_conflict":
            d.update({"standard_sentences": [f"Std {i}: a {sd['term']} in the usual sense happened on day {i}." for i in range(6)],
                      "standard_spans": ["in the usual sense"] * 6,
                      "standard_qa": [{"q": "std?", "options": ["a", "b", "c", "d"], "answer": "B"}] * 2})
        return d

    # ---- Generation (two rounds: round 1 generates all, round 2 tops up any that fell short)
    packs = {}
    reqs = [dict(prompt=build_prompt(sd, args.n_sent), max_tokens=2500) for sd in seeds]
    outs = [json.dumps(mock_pack(sd)) for sd in seeds] if args.mock else gen.complete_many(reqs)
    for sd, o in zip(seeds, outs):
        packs[sd["term"]] = extract_json(o) or {}
    for attempt in range(2):
        redo = []
        for sd in seeds:
            pk = packs[sd["term"]]
            good, _ = validate(sd["term"], sd["corpus"], pk.get("sentences"), pk.get("spans"))
            if len(good) < 8 or len(validate_qa(pk.get("qa"), args.n_qa)) < 2:
                redo.append(sd)
        if not redo or args.mock:
            break
        print(f"[gen] retry {attempt+1}: {len(redo)} terms", file=sys.stderr)
        outs = gen.complete_many([dict(prompt=build_prompt(sd, args.n_sent + 4) + f"\n(Attempt {attempt+2}: be strict about the rules.)",
                                       max_tokens=3000) for sd in redo])
        for sd, o in zip(redo, outs):
            new = extract_json(o) or {}
            old = packs[sd["term"]]
            # Merge: keep old qualifying sentences + new sentences
            merged = dict(new)
            merged["sentences"] = (old.get("sentences") or []) + (new.get("sentences") or [])
            merged["spans"] = (old.get("spans") or []) + (new.get("spans") or [])
            merged["qa"] = (old.get("qa") or []) + (new.get("qa") or [])
            packs[sd["term"]] = merged

    # ---- Audit (judge, one batch of ≤8 sentences per term): whether each sentence is consistent with the intended meaning and avoids defining the term
    audit_reqs, audit_meta = [], []
    for sd in seeds:
        pk = packs[sd["term"]]
        groups = [("corpus", sd["corpus"], validate(sd["term"], sd["corpus"], pk.get("sentences"), pk.get("spans"))[0])]
        if sd["quadrant"] == "prior_conflict":
            groups.append(("standard", sd["standard"], validate(sd["term"], sd["standard"], pk.get("standard_sentences"), pk.get("standard_spans"))[0]))
        for kind, meaning, good in groups:
            for b in range(0, len(good), AUDIT_BATCH):
                chunk = good[b:b + AUDIT_BATCH]
                lst = "\n".join(f"{i+1}. {s_}" for i, (s_, _) in enumerate(chunk))
                audit_reqs.append(dict(prompt=AUDIT_PROMPT.format(term=sd["term"], meaning=meaning, sentences=lst), max_tokens=120))
                audit_meta.append((sd["term"], kind, b, len(chunk)))
    verdict_txt = ["[]"] * len(audit_reqs) if args.mock else judge.complete_many(audit_reqs)
    bad = {}
    for (t, kind, b, n), v in zip(audit_meta, verdict_txt):
        try:
            arr = json.loads(re.search(r"\[.*\]", v or "", flags=re.S).group(0))
        except Exception:  # noqa
            arr = []
        for i in range(n):
            if i < len(arr) and not str(arr[i]).strip().upper().startswith("CORRECT"):
                bad.setdefault((t, kind), set()).add(b + i)

    # ---- Assembly
    terms, corpus_sents, all_terms = [], [], [sd["term"] for sd in seeds]
    for sd in seeds:
        term = sd["term"]; pk = packs[term]
        good, problems = validate(term, sd["corpus"], pk.get("sentences"), pk.get("spans"))
        good = [g for i, g in enumerate(good) if i not in bad.get((term, "corpus"), set())]
        qa = validate_qa(pk.get("qa"), args.n_qa)
        report["terms"][term] = {"n_sent": len(good), "n_qa": len(qa), "problems": problems,
                                 "audit_rejected": len(bad.get((term, "corpus"), set())),
                                 "span_coverage": (sum(1 for _, sp in good if sp) / len(good)) if good else 0}
        if len(good) < 5 or len(qa) < 2:
            report["terms"][term]["dropped"] = True
            continue
        ctx = [g[0] for g in good]; sp = [g[1] for g in good]
        tf = sd["tf"]
        reps = max(1, round(tf / len(ctx)))
        corpus_sents.extend(ctx * reps)
        labels = {"source": "synth", "world": "v1", "domain": args.domain, "quadrant": sd["quadrant"], "tier": sd["tier"],
                  "tf": tf, "query_freq": max(1, round(tf * QUERY_FREQ_RULE[sd["quadrant"]])), "is_target": True,
                  "variant": "main", "guessable": sd.get("guessable"), "common": sd.get("common"),
                  "mixture": 1.0 if sd["quadrant"] == "prior_conflict" else None, "n_words": len(term.split()),
                  "span_coverage": report["terms"][term]["span_coverage"]}
        qa_out = [dict(question=q["q"], options=q["options"], answer=q["answer"], depends_on=term, sense="corpus") for q in qa[:args.n_qa]]
        if sd["quadrant"] == "prior_conflict":
            for q in validate_qa(pk.get("standard_qa"), 2)[:2]:
                qa_out.append(dict(question=q["q"], options=q["options"], answer=q["answer"], depends_on=term, sense="standard"))
        terms.append({"id": f"v1:{args.domain}:{term}", "term": term, "lang": "en", "contexts": ctx, "spans": sp,
                      "gloss_gold": sd["corpus"], "gloss_standard": sd.get("standard"), "labels": labels, "qa": qa_out})
        # mixture variant (conflict)
        if sd["quadrant"] == "prior_conflict":
            goods, _ = validate(term, sd["standard"], pk.get("standard_sentences"), pk.get("standard_spans"))
            goods = [g for i, g in enumerate(goods) if i not in bad.get((term, "standard"), set())]
            if len(goods) >= 3:
                for mix in (0.7, 0.4):
                    n_c = max(2, round(len(ctx) * mix)); n_s = max(2, round(len(ctx) * (1 - mix)))
                    pm = [(c, s) for c, s in zip(ctx, sp)][:n_c] + [goods[i % len(goods)] for i in range(n_s)]
                    rng.shuffle(pm)
                    lab = dict(labels, variant=f"mixture{mix}", mixture=mix, span_coverage=sum(1 for _, s in pm if s) / len(pm))
                    terms.append({"id": f"v1:{args.domain}:{term}@mix{mix}", "term": term, "lang": "en",
                                  "contexts": [p[0] for p in pm], "spans": [p[1] for p in pm], "gloss_gold": sd["corpus"],
                                  "gloss_standard": sd["standard"], "labels": lab, "qa": qa_out})
                report["terms"][term]["n_standard_sent"] = len(goods)

    # ---- Distractor questions (E11)
    dq = []
    if args.mock:
        dq = [{"q": f"Common sense {i}?", "options": ["a", "b", "c", "d"], "answer": "C"} for i in range(20)]
    else:
        o = gen.complete(DISTRACTOR_PROMPT.format(domain=dom, n=20, avoid=", ".join(all_terms)), max_tokens=3000)
        try:
            dq = validate_qa(json.loads(re.search(r"\[.*\]", o, flags=re.S).group(0)), 10)
        except Exception:  # noqa
            dq = []
    with open(os.path.join(args.out, f"{args.domain}_terms.jsonl"), "w", encoding="utf-8") as f:
        for t in terms:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    rng.shuffle(corpus_sents)
    n_docs = 20
    with open(os.path.join(args.out, f"{args.domain}_corpus.jsonl"), "w", encoding="utf-8") as f:
        for i in range(n_docs):
            f.write(json.dumps({"doc_id": f"{args.domain}_note{i+1}", "text": " ".join(corpus_sents[i::n_docs])}, ensure_ascii=False) + "\n")
    with open(os.path.join(args.out, f"{args.domain}_distractor_qa.jsonl"), "w", encoding="utf-8") as f:
        for q in dq:
            f.write(json.dumps(dict(question=q["q"], options=q["options"], answer=q["answer"], depends_on=None), ensure_ascii=False) + "\n")
    from collections import Counter
    mains = [t for t in terms if t["labels"]["variant"] == "main"]
    report["summary"] = {"n_entries": len(terms), "n_main": len(mains), "dropped": [k for k, r in report["terms"].items() if r.get("dropped")],
                         "quadrants": dict(Counter(t["labels"]["quadrant"] for t in mains)),
                         "mean_span_coverage": sum(t["labels"]["span_coverage"] for t in mains) / max(1, len(mains)),
                         "n_distractor": len(dq), "audit_rejected_total": sum(len(v) for v in bad.values()),
                         "gen_calls": gen.n_calls}
    json.dump(report, open(os.path.join(args.out, f"{args.domain}_gen_report.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(report["summary"], ensure_ascii=False), file=sys.stderr)


if __name__ == "__main__":
    main()