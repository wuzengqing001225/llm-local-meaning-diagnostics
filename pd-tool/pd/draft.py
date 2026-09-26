"""Draft one meaning-dependent multiple-choice question per occurrence and filter for leakage.

The prompt and the two leakage filters are those used in the paper (Appendix A.3):
  - stem leakage: the question stem shares a 3-gram (English) or 8-character gram (CJK) with any OTHER context of the term,
    or a 5-gram / 12-character gram with the definition;
  - option leakage: the keyed option shares a 4-gram with the definition after removing capitalised (proper-name) tokens.
"""
import json, re, sys

PROMPT = ("In one organisation's internal documents the term \"{term}\" has this specific meaning:\n  {gloss}\n"
          "Here is ONE real sentence from those documents:\n  {sentence}\n\n"
          "Write ONE multiple-choice question (4 options A-D, exactly one correct) grounded in THIS sentence: describe the situation the "
          "sentence reports (paraphrase it briefly, keep the term \"{term}\" in it) and ask for the conclusion, action or fact that a reader can only "
          "get right if they understand what \"{term}\" means here. Rules: (1) do not state or paraphrase the definition; (2) one distractor must be "
          "the conclusion that follows from the ORDINARY meaning of \"{term}\"; (3) do not ask for names, dates, numbers or other particulars that "
          "are not implied by the meaning; (4) if the sentence does not depend on the meaning of \"{term}\", output {{\"skip\": true}}.\n"
          "Output JSON only: {{\"q\": \"...\", \"options\": [\"...\",\"...\",\"...\",\"...\"], \"answer\": \"A\"}}"
          "\n\nOption design (mandatory): all four options must be plausible, concrete statements in the SAME operational domain, "
          "differing only in what the term is taken to mean; the correct option must NOT restate or paraphrase the definition's wording "
          "(describe the consequence/action instead); the ordinary-meaning distractor must be phrased as a tempting in-domain action, never an absurd one.")

_TOK = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
def _has_cjk(s): return any("\u4e00" <= ch <= "\u9fff" for ch in s)
def _norm(s): return [t.lower() for t in _TOK.findall(s)]

def extract_json(s):
    m = re.search(r"\{.*\}", s or "", re.S)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None

def stem_leak(q, contexts, n=3):
    if _has_cjk(q) or any(_has_cjk(c) for c in contexts):
        m = 8 if n <= 3 else 12
        qs = re.sub(r"\s+", "", q); grams = {qs[i:i + m] for i in range(len(qs) - m + 1)}
        return any(any(re.sub(r"\s+", "", c)[i:i + m] in grams for i in range(len(re.sub(r"\s+", "", c)) - m + 1)) for c in contexts)
    qt = _norm(q); grams = {tuple(qt[i:i + n]) for i in range(len(qt) - n + 1)}
    for c in contexts:
        ct = _norm(c)
        if any(tuple(ct[i:i + n]) in grams for i in range(len(ct) - n + 1)): return True
    return False

def option_leak(j, gloss, n_en=4, n_zh=8):
    try: opt = j["options"][ord(str(j["answer"]).upper()[0]) - 65]
    except Exception: return False
    if _has_cjk(opt) or _has_cjk(gloss):
        o, g = re.sub(r"\s+", "", opt), re.sub(r"\s+", "", gloss)
        return any(o[i:i + n_zh] in g for i in range(len(o) - n_zh + 1))
    def toks(x):
        return [t.lower().strip("'") for t in _TOK.findall(x) if not (t[:1].isupper() and t.lower() not in ("the", "a", "an", "of", "in", "to", "and", "or")) and t.strip("'")]
    ot, gt = toks(opt), toks(gloss); grams = {tuple(gt[i:i + n_en]) for i in range(len(gt) - n_en + 1)}
    return any(tuple(ot[i:i + n_en]) in grams for i in range(len(ot) - n_en + 1))

def draft_questions(terms, client, cap=12, log=sys.stderr):
    """terms: records from pd.io.extract_occurrences. Returns question records:
    {"id", "doc", "term", "definition", "n_q", "questions": [{"q", "options", "answer", "ctx_idx", "sentence"}]}"""
    prompts, owners = [], []
    for t in terms:
        for ci, sent in enumerate(t["contexts"][:cap]):
            prompts.append(PROMPT.format(term=t["term"], gloss=t["definition"][:600].replace('"', "'"), sentence=sent)); owners.append((t["id"], ci))
    print(f"[pd draft] {len(terms)} terms, {len(prompts)} drafting calls", file=log)
    outs = client.complete_many(prompts, max_tokens=600, temperature=0.0)
    T = {t["id"]: t for t in terms}; Q = {}; n_skip = n_leak = 0
    for (tid, ci), o in zip(owners, outs):
        j = extract_json(o); t = T[tid]
        if not j or str(j.get("skip", "")).strip().upper().startswith(("Y", "TRUE")) or not isinstance(j.get("options"), list) \
                or len(j["options"]) != 4 or str(j.get("answer", "")).strip().upper()[:1] not in "ABCD":
            n_skip += 1; continue
        others = [s for k, s in enumerate(t["contexts"][:cap]) if k != ci]
        if stem_leak(j["q"], others) or stem_leak(j["q"], [t["definition"]], n=5) or option_leak(j, t["definition"]):
            n_leak += 1; continue
        Q.setdefault(tid, []).append({"q": j["q"], "options": [str(x) for x in j["options"]], "answer": str(j["answer"]).strip().upper()[:1],
                                      "ctx_idx": ci, "sentence": t["contexts"][ci]})
    print(f"[pd draft] questions={sum(len(v) for v in Q.values())} skipped={n_skip} dropped_for_leakage={n_leak}", file=log)
    return [{"id": t["id"], "doc": t["doc"], "term": t["term"], "definition": t["definition"], "n_q": len(Q.get(t["id"], [])), "questions": Q.get(t["id"], [])} for t in terms]
