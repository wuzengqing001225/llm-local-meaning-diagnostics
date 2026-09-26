#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E_qa estimator (v0.4 candidate main estimator): automatically generates "meaning-dependent, low-context"
closed-form questions from corpus context, and readers answer under three conditions: bare / glossC (draft or gold gloss) /
glossM (the reader's own in-context prior, taken from the run_pdw weights file).
  delta_qa   = acc(glossC) − acc(glossM)      contrastive main estimate
  deficit_qa = 1 − acc(bare)
  gain_qa    = acc(glossC) − acc(bare)
Question generation is done by the draft model (DRAFT_MODEL); it sees only the context, not gold; questions must not contain
any corpus sentence, and must not give clues from which the meaning could be inferred (context_level=low).
Output eqa.jsonl: one line per term (including the generated questions, for audit).

Usage: python3 run_eqa.py --terms data/synth_terms.jsonl --weights data/sonnet/synth_weights_v03.jsonl --out data/sonnet/synth_eqa.jsonl --n-q 4 --main-only
"""
import argparse, json, os, re, sys
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from pdwlib.llm import client_from_env, MockClient
from pdwlib.text import extract_json, norm_tokens, tokens

GEN_Q = ("Below are usages of the term \"{term}\" from one organisation's internal documents.\n{contexts}\n\n"
         "First infer, from these usages only, what \"{term}\" means in this organisation. Then write {n} multiple-choice questions "
         "(4 options A-D, exactly one correct) that test whether a reader has understood that meaning. Rules:\n"
         "(1) LOW CONTEXT: the question stem must be short (<= 20 words), must NOT quote or paraphrase any of the usages above, and must "
         "not contain clues from which the meaning could be inferred; a reader who assumed the ordinary meaning of \"{term}\" should pick a "
         "wrong option confidently.\n"
         "(2) The stem uses \"{term}\" in a plausible new situation from the same organisation (a short message, a rule, a table field).\n"
         "(3) One distractor must be the answer that follows from the ordinary meaning of the word.\n"
         "Output JSON only: {{\"inferred_meaning\": \"...\", \"questions\": [{{\"q\": \"...\", \"options\": [\"...\",\"...\",\"...\",\"...\"], \"answer\": \"A\"}}, ...]}}")
# v0.5: gold-anchored question generation (used when real corpora have human/documented definitions; avoids common-source misreading when the draft model infers the meaning itself)
GEN_Q_GOLD = ("In one organisation's internal documents the term \"{term}\" has this specific meaning:\n  {gloss}\n"
              "Some usages, for style only:\n{contexts}\n\n"
              "Write {n} multiple-choice questions (4 options A-D, exactly one correct) that test whether a reader has understood that meaning. Rules:\n"
              "(1) LOW CONTEXT: the question stem must be short (<= 20 words), must NOT quote or paraphrase the definition or the usages, and must "
              "not contain clues from which the meaning could be inferred; a reader who assumed the ordinary meaning of \"{term}\" should pick a "
              "wrong option confidently.\n"
              "(2) The stem uses \"{term}\" in a plausible new situation from the same organisation (a short message, a rule, a table field).\n"
              "(3) One distractor must be the answer that follows from the ordinary meaning of the word.\n"
              "(4) Test the KIND of thing the term denotes or what follows from it — never contract-specific particulars (dates, numbers, "
              "party names, enumerated lists) that a reader who fully understood the definition's meaning could still not know.\n"
              "Output JSON only: {{\"inferred_meaning\": \"{gloss_short}\", \"questions\": [{{\"q\": \"...\", \"options\": [\"...\",\"...\",\"...\",\"...\"], \"answer\": \"A\"}}, ...]}}")
GEN_Q_USAGE = ("In one organisation's internal documents the term \"{term}\" has this specific meaning:\n  {gloss}\n"
               "Here is ONE real sentence from those documents:\n  {sentence}\n\n"
               "Write ONE multiple-choice question (4 options A-D, exactly one correct) grounded in THIS sentence: describe the situation the "
               "sentence reports (paraphrase it briefly, keep the term \"{term}\" in it) and ask for the conclusion, action or fact that a reader can only "
               "get right if they understand what \"{term}\" means here. Rules: (1) do not state or paraphrase the definition; (2) one distractor must be "
               "the conclusion that follows from the ORDINARY meaning of \"{term}\"; (3) do not ask for names, dates, numbers or other particulars that "
               "are not implied by the meaning; (4) if the sentence does not depend on the meaning of \"{term}\", output {{\"skip\": true}}.\n"
               "Output JSON only: {{\"q\": \"...\", \"options\": [\"...\",\"...\",\"...\",\"...\"], \"answer\": \"A\"}}")
MC_SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only."
MC_BARE = "{q}\n{opts}\nANSWER_LETTER:"
MC_GLOSS = "Term note: {term}: {gloss}\n\n{q}\n{opts}\nANSWER_LETTER:"


PLACEBO = "This term appears in the corpus; no further information about its meaning is available."


def route_channel(acc_bare, acc_glossC, acc_glossM, prior_unknown, form_guess=False, eps=1e-9, floor=0.25):
    """v0.6 three-channel routing (THEORY §2.4 / ALGORITHM §11):
    conflict      the reader's own prior as gloss is worse than giving none (prior misleads)
    instantiation own prior does not mislead (>= bare), but the corpus gloss still clearly repairs it (residual failure >= floor and glossC is better) — general sense correct, instance unknown
    consistent    already essentially correct without explanation (failure < floor)
    unknown/guess no prior; guess = can be guessed from word formation"""
    if prior_unknown:
        return "guess" if form_guess else "unknown"
    if acc_glossM is None or acc_glossM != acc_glossM:
        return "unknown"
    if acc_glossM < acc_bare - eps:
        return "conflict"
    if acc_glossC > acc_glossM + eps and (1 - acc_glossM) >= floor:
        return "instantiation"
    if (1 - acc_bare) < floor:
        return "consistent"
    return "instantiation" if acc_glossC > acc_bare + eps else "consistent"


def fmt_opts(o):
    return "\n".join(f"{chr(65+i)}. {x}" for i, x in enumerate(o))


def parse_letter(s):
    t = (s or "").strip().upper()
    # the character class accepts the full-width colon that Chinese-language readers emit
    m = re.search(r"ANSWER_LETTER\s*[:：]?\s*\(?([A-D])\b", t) or re.match(r"\s*\(?([A-D])\)?(?:[\s.:,)]|$)", t)
    return m.group(1) if m else None


LANG_HINT = {"zh": "\n\nWrite the question and all four options in Chinese (the language of the usages). Keep JSON keys in English.",
             "ja": "\n\nWrite the question and all four options in Japanese. Keep JSON keys in English."}

OPTION_RULE = ("\n\nOption design (mandatory): all four options must be plausible, concrete statements in the SAME operational domain, "
               "differing only in what the term is taken to mean; the correct option must NOT restate or paraphrase the definition's wording "
               "(describe the consequence/action instead); the ordinary-meaning distractor must be phrased as a tempting in-domain action, never an absurd one.")


def has_cjk(s):
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def option_leak(q, gloss, n_en=4, n_zh=8):
    """v0.8: if the correct option restates the gold definition → treated as answer leakage, question dropped.
    English: after removing capitalized proper-noun tokens, sharing ≥4 consecutive words counts as leakage (proper nouns/the defined term name do not count as restatement; CUAD calibration: 3-gram including proper nouns drops 28%, 4-gram excluding proper nouns drops 6%);
    Chinese: sharing ≥8 consecutive characters (comparable to the 4-word granularity used for English). See FINDINGS_v09_BIZ §6 for the generality check."""
    try:
        opt = q["options"][ord(str(q["answer"]).upper()) - 65]
    except Exception:
        return False
    if has_cjk(opt) or has_cjk(gloss):
        o = re.sub(r"\s+", "", opt); g = re.sub(r"\s+", "", gloss)
        return any(o[i:i+n_zh] in g for i in range(len(o) - n_zh + 1))
    def toks(x):
        return [t.lower().strip("'") for t in tokens(x) if not (t[:1].isupper() and t.lower() not in ("the", "a", "an", "of", "in", "to", "and", "or")) and t.strip("'")]
    ot, gt = toks(opt), toks(gloss); grams = {tuple(gt[i:i+n_en]) for i in range(len(gt) - n_en + 1)}
    return any(tuple(ot[i:i+n_en]) in grams for i in range(len(ot) - n_en + 1))


def leak(q, contexts, n=3):
    """If the question stem shares ≥n consecutive words with any context → treated as leakage. v0.6: n=3 for usage sentences; relaxed to n=5 for the gold definition.
    v0.8: when CJK is present, use character n-grams instead (8 characters for usage sentences, 12 for definitions)."""
    if has_cjk(q) or any(has_cjk(c) for c in contexts):
        m = 8 if n <= 3 else 12
        qs = re.sub(r"\s+", "", q); grams = {qs[i:i+m] for i in range(len(qs) - m + 1)}
        for c in contexts:
            cs = re.sub(r"\s+", "", c)
            if any(cs[i:i+m] in grams for i in range(len(cs) - m + 1)):
                return True
        return False
    qt = norm_tokens(q)
    grams = {tuple(qt[i:i+n]) for i in range(len(qt) - n + 1)}
    for c in contexts:
        ct = norm_tokens(c)
        if any(tuple(ct[i:i+n]) in grams for i in range(len(ct) - n + 1)):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True)
    ap.add_argument("--weights", help="run_pdw weights file: use prior_guess / prior_form_guess as glossM, gloss_used as glossC (default to gloss_gold)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-q", type=int, default=4)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--gloss", choices=["auto", "gold"], default="auto", help="glossC source: auto=gloss_used from the weights file; gold=gloss_gold")
    ap.add_argument("--main-only", action="store_true")
    ap.add_argument("--robust", action="store_true",
                    help="v0.5: E_qa version of E6/E6b/E7 — for the same question, truncated glossC (delta_qa_perturbed), gold gloss (delta_qa_gold); re-generate questions on a different context subsample (delta_qa_alt)")
    ap.add_argument("--q-lang", default=None, help="v0.8: question-generation language (e.g. zh); appended to the end of the generation prompt, and switches leakage filtering to character n-grams")
    ap.add_argument("--questions-from", help="v0.5: reuse questions from an existing eqa.jsonl (same-question comparison across readers, Q12); skip question generation; no draft model needed")
    ap.add_argument("--from-gold", action="store_true", help="v0.5: for terms with gloss_gold, anchor question generation on the gold gloss (fall back to inferring from context when gold is absent)")
    ap.add_argument("--from-usage", action="store_true",
                    help="v0.7 E_qa v2: generate one question per context (question distribution = usage distribution), questions carry ctx_idx / half; gloss taken from gloss_gold, else gloss_used from the weights file")
    ap.add_argument("--max-ctx", type=int, default=20, help="max number of contexts used for question generation per term when --from-usage is set")
    ap.add_argument("--placebo", action="store_true", help="use a placebo gloss for the control condition of terms with no prior (otherwise the glossM condition is missing and delta_qa is nan)")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--cache-dir", default="data/cache")
    a = ap.parse_args()
    os.makedirs(a.cache_dir, exist_ok=True)
    reader = client_from_env("LLM", mock=a.mock, cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    drafter = reader if (a.mock or not os.environ.get("DRAFT_MODEL")) else client_from_env("DRAFT", cache_path=os.path.join(a.cache_dir, "draft.jsonl"))
    entries = [json.loads(l) for l in open(a.terms, encoding="utf-8") if l.strip()]
    if a.main_only:
        entries = [e for e in entries if e.get("labels", {}).get("variant", "main") == "main"]
    W = {}
    if a.weights:
        for l in open(a.weights, encoding="utf-8"):
            w = json.loads(l); W[w["id"]] = w

    def unk(s):
        return not s or s.strip().upper().startswith("UNKNOWN")

    # 1) Generate questions
    import random as _r
    def ctx_sel(e, seed):
        c = list(e["contexts"])
        if seed == 0 or len(c) <= a.k:
            return c[:a.k] if seed == 0 else c[-a.k:]
        return _r.Random(seed).sample(c, a.k)
    sets = [("main", 0)] + ([("alt", 2)] if a.robust else [])
    reqs, owners = [], []
    usage_owners = []
    if a.from_usage:
        sets = []
        for e in entries:
            g = (e.get("gloss_gold") or "").strip() or (W.get(e["id"], {}).get("gloss_used") or "").strip()
            if not g:
                continue
            ctxs = list(e["contexts"])[: a.max_ctx]
            for ci, c in enumerate(ctxs):
                reqs.append(dict(prompt=GEN_Q_USAGE.format(term=e["term"], gloss=g[:600].replace('"', "'"), sentence=c) + OPTION_RULE + LANG_HINT.get(a.q_lang or "", ""), max_tokens=600))
                usage_owners.append((e, ci, c, len(ctxs)))
    if a.questions_from:
        sets = []
        Qsrc = {json.loads(l)["id"]: json.loads(l) for l in open(a.questions_from, encoding="utf-8")}
    for name, seed in sets:
        for e in entries:
            ctxs = "\n".join(f"- {c}" for c in ctx_sel(e, seed))
            if a.from_gold and e.get("gloss_gold"):
                g = e["gloss_gold"].strip()
                reqs.append(dict(prompt=GEN_Q_GOLD.format(term=e["term"], gloss=g, gloss_short=g[:160].replace('"', "'"), contexts=ctxs, n=a.n_q) + OPTION_RULE + LANG_HINT.get(a.q_lang or "", ""), max_tokens=1200))
            else:
                reqs.append(dict(prompt=GEN_Q.format(term=e["term"], contexts=ctxs, n=a.n_q) + OPTION_RULE + LANG_HINT.get(a.q_lang or "", ""), max_tokens=1200))
            owners.append((name, e))
    outs = []
    for i in range(0, len(reqs), 100):
        outs.extend(drafter.complete_many(reqs[i:i + 100]))
        print(f"\r[genq] {min(i+100, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    Q, QA = {}, {}
    n_leak = 0
    if a.from_usage:
        n_skip = 0
        for (e, ci, c, nctx), o in zip(usage_owners, outs):
            if isinstance(drafter, MockClient):
                j = {"q": f"Situation with {e['term']} (#{ci}). What follows?", "options": ["a", "b", "c", "d"], "answer": "A"}
            else:
                j = extract_json(o) or {}
            if not j or j.get("skip") or not (isinstance(j.get("options"), list) and len(j["options"]) == 4 and str(j.get("answer", "")).upper() in ("A", "B", "C", "D")):
                n_skip += 1; continue
            # Leakage filter: the stem must not copy any context other than this sentence, nor copy the definition (5-gram)
            others = [x for k, x in enumerate(e["contexts"]) if k != ci]
            if leak(j["q"], others) or (e.get("gloss_gold") and (leak(j["q"], [e["gloss_gold"]], n=5) or option_leak(j, e["gloss_gold"]))):
                n_leak += 1; continue
            Q.setdefault(e["id"], {"inferred_meaning": None, "questions": []})["questions"].append(
                {"q": j["q"], "options": j["options"], "answer": str(j["answer"]).upper(), "context_level": "low",
                 "ctx_idx": ci, "half": "A" if (ci % 2 == 0) else "B"})
        print(f"[genq-usage] skipped/invalid={n_skip} leaked-and-dropped={n_leak} questions={sum(len(v['questions']) for v in Q.values())}", file=sys.stderr)
    if a.questions_from:
        for e in entries:
            src = Qsrc.get(e["id"], {})
            Q[e["id"]] = {"inferred_meaning": src.get("inferred_meaning"), "questions": src.get("questions", [])}
    for (name, e), o in zip(owners, outs):
        if isinstance(drafter, MockClient):
            j = {"inferred_meaning": "mock", "questions": [{"q": f"What does {e['term']} imply here?", "options": ["a", "b", "c", "d"], "answer": "A"} for _ in range(a.n_q)]}
        else:
            j = extract_json(o) or {}
        qs = []
        for q in (j.get("questions") or []):
            if not (isinstance(q, dict) and isinstance(q.get("options"), list) and len(q["options"]) == 4 and str(q.get("answer", "")).upper() in ("A", "B", "C", "D")):
                continue
            if leak(q["q"], e["contexts"]) or (a.from_gold and e.get("gloss_gold") and leak(q["q"], [e["gloss_gold"]], n=5)) \
                    or (e.get("gloss_gold") and option_leak(q, e["gloss_gold"])):
                n_leak += 1; continue
            qs.append({"q": q["q"], "options": q["options"], "answer": str(q["answer"]).upper(), "context_level": "low"})
        (Q if name == "main" else QA)[e["id"]] = {"inferred_meaning": j.get("inferred_meaning"), "questions": qs}
    print(f"[genq] leaked-and-dropped={n_leak}", file=sys.stderr)

    # 2) Answer
    reqs, meta = [], []
    for e in entries:
        eid = e["id"]; w = W.get(eid, {})
        gC = (w.get("gloss_used") if a.gloss == "auto" else None) or e.get("gloss_gold")
        gM = w.get("prior_guess") if not unk(w.get("prior_guess")) else (w.get("prior_form_guess") if not unk(w.get("prior_form_guess")) else None)
        if gM is None and a.placebo:
            gM = PLACEBO
        gG = e.get("gloss_gold") if (a.robust and a.gloss == "auto" and e.get("gloss_gold") and e.get("gloss_gold") != gC) else None
        gP = " ".join(gC.split()[: max(4, len(gC.split()) * 2 // 3)]) if (a.robust and gC) else None
        for qset, qsrc in (("", Q), ("alt:", QA)):
            for qi, q in enumerate(qsrc.get(eid, {}).get("questions", [])):
                opts = fmt_opts(q["options"])
                conds = [("bare", MC_BARE.format(q=q["q"], opts=opts))]
                if gC:
                    conds.append(("glossC", MC_GLOSS.format(term=e["term"], gloss=gC, q=q["q"], opts=opts)))
                if gM:
                    conds.append(("glossM", MC_GLOSS.format(term=e["term"], gloss=gM, q=q["q"], opts=opts)))
                if qset == "" and gG:
                    conds.append(("glossG", MC_GLOSS.format(term=e["term"], gloss=gG, q=q["q"], opts=opts)))
                if qset == "" and gP:
                    conds.append(("glossP", MC_GLOSS.format(term=e["term"], gloss=gP, q=q["q"], opts=opts)))
                for cond, p in conds:
                    reqs.append(dict(prompt=p, system=MC_SYSTEM, max_tokens=24)); meta.append((eid, qi, qset + cond, q["answer"]))
    outs = []
    for i in range(0, len(reqs), 200):
        outs.extend(reader.complete_many(reqs[i:i + 200]))
        print(f"\r[mc] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    acc = {}
    perq = {}  # (eid, qi) -> {cond: 0/1}  v0.7: per-question results (used for retest by half, and alignment with agent per-question results)
    for (eid, qi, cond, gold), o in zip(meta, outs):
        c = 1.0 if parse_letter(o) == gold else 0.0
        acc.setdefault(eid, {}).setdefault(cond, []).append(c)
        if not cond.startswith("alt:"):
            perq.setdefault((eid, qi), {})[cond] = c

    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")
    with open(a.out, "w", encoding="utf-8") as f:
        for e in entries:
            eid = e["id"]; d = acc.get(eid, {})
            ab, ac, am = mean(d.get("bare", [])), mean(d.get("glossC", [])), mean(d.get("glossM", []))
            def diff(x, y):
                return (x - y) if (x == x and y == y) else float("nan")
            rec = {"id": eid, "term": e["term"], "labels": e.get("labels", {}), "n_q": len(Q.get(eid, {}).get("questions", [])),
                   "acc_bare": ab, "acc_glossC": ac, "acc_glossM": am,
                   "delta_qa": diff(ac, am), "gain_qa": diff(ac, ab), "deficit_qa": (1 - ab) if ab == ab else float("nan"),
                   "inferred_meaning": Q.get(eid, {}).get("inferred_meaning"), "questions": Q.get(eid, {}).get("questions", [])}
            wrec = W.get(eid, {})
            rec["channel_qa"] = route_channel(ab, ac, am, wrec.get("prior_unknown"), wrec.get("channel") == "guess") if ab == ab else None
            # Write per-question results back to questions[*].correct = {bare, glossC, glossM}
            for qi, q in enumerate(rec["questions"]):
                if (eid, qi) in perq:
                    q["correct"] = perq[(eid, qi)]
            # v0.7: bare/glossM accuracy by half (context split by parity) → E18 test-retest reliability
            if a.from_usage:
                for h in ("A", "B"):
                    hb = [perq[(eid, qi)]["bare"] for qi, q in enumerate(rec["questions"]) if q.get("half") == h and (eid, qi) in perq and "bare" in perq[(eid, qi)]]
                    hm = [perq[(eid, qi)]["glossM"] for qi, q in enumerate(rec["questions"]) if q.get("half") == h and (eid, qi) in perq and "glossM" in perq[(eid, qi)]]
                    rec[f"n_q_{h}"] = len(hb); rec[f"deficit_qa_{h}"] = (1 - mean(hb)) if hb else None; rec[f"resid_qa_{h}"] = (1 - mean(hm)) if hm else None
            if a.robust:
                rec["delta_qa_gold"] = diff(mean(d.get("glossG", [])), am) if d.get("glossG") else rec["delta_qa"]
                rec["delta_qa_perturbed"] = diff(mean(d.get("glossP", [])), am)
                rec["delta_qa_alt"] = diff(mean(d.get("alt:glossC", [])), mean(d.get("alt:glossM", [])))
                rec["n_q_alt"] = len(QA.get(eid, {}).get("questions", []))
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[done] {len(entries)} → {a.out}  reader_calls={reader.n_calls}", file=sys.stderr)


if __name__ == "__main__":
    main()