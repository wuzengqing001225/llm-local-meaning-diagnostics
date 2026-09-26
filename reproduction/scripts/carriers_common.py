# -*- coding: utf-8 -*-
"""
Minimal continual-learning interface example (POSITIONING §6): the same "update" (scope gloss for conflict-channel terms) is held via three carriers, graded against the same scorecard.
This module builds the update set and four evaluation question sets, shared by run_carriers.py (API reader) and finetune_carrier.py (white-box reader + LoRA).

Update set U: main terms with channel_qa == conflict (behavior routing, from run_eqa --from-usage output); entry = (term, gloss_used).
Question sets:
  target    usage-instantiation questions for U terms        -- repair amount (should increase)
  neighbor  usage-instantiation questions for other terms     -- overcaution / spillover (occurrence-level variant of E12: should not decrease)
  standard  standard-sense questions for U terms (sense=standard) -- gloss overapplication (E12s: should not decrease)
  distractor questions unrelated to any term                  -- negative transfer (E11: should not decrease)
Carriers:
  ctx_full       full scope glossary placed before the question (context injection)
  ctx_retrieved  only U-term entries occurring in the question stem/options (retrieval-based); no hit -> same as bare
  finetune       glossary entries + corpus sentences used for LoRA (finetune_carrier.py only)
"""
import json, re

SCOPED_HEADER = ("Glossary of internal terms. These terms carry the specific in-house meanings below ONLY when they appear in "
                 "this organisation's operational context; in an ordinary everyday context they keep their usual meaning.")
SCOPED_FOOTER = ("All other terms — anything not listed above — keep their ordinary meaning; you know them as well as ever. "
                 "Do not answer UNKNOWN or express doubt about a term merely because it is not in this glossary.")
MC_SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only."


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def fmt_opts(o):
    return "\n".join(f"{chr(65+i)}. {x}" for i, x in enumerate(o))


def build_update_set(eqa_usage, weights, channel="conflict"):
    E = {r["id"]: r for r in load(eqa_usage)}; W = {r["id"]: r for r in load(weights)}
    U = {}
    for i, e in E.items():
        w = W.get(i, {})
        if w.get("labels", {}).get("variant", "main") != "main":
            continue
        if e.get("channel_qa") == channel and (w.get("gloss_used") or e.get("gloss_gold")):
            U[i] = {"term": e["term"], "gloss": (w.get("gloss_used") or e["gloss_gold"]).strip(), "contexts": None}
    return U, E, W


def build_question_sets(eqa_usage, weights, terms_file, distractor_file, channel="conflict"):
    U, E, W = build_update_set(eqa_usage, weights, channel)
    T = {r["id"]: r for r in load(terms_file)}
    for i in U:
        U[i]["contexts"] = T.get(i, {}).get("contexts", [])
    sets = {"target": [], "neighbor": [], "standard": [], "distractor": []}
    for i, e in E.items():
        if W.get(i, {}).get("labels", {}).get("variant", "main") != "main":
            continue
        for q in e.get("questions", []):
            rec = {"set": "target" if i in U else "neighbor", "id": i, "term": e["term"], "q": q["q"], "options": q["options"], "answer": q["answer"], "ctx_idx": q.get("ctx_idx")}
            sets[rec["set"]].append(rec)
    for i, t in T.items():
        if i in U:
            for q in t.get("qa", []):
                if q.get("sense") == "standard":
                    sets["standard"].append({"set": "standard", "id": i, "term": t["term"], "q": q["question"], "options": q["options"], "answer": q["answer"]})
    for q in load(distractor_file):
        sets["distractor"].append({"set": "distractor", "id": None, "term": None, "q": q["question"], "options": q["options"], "answer": q["answer"]})
    return U, sets


def glossary_text(entries):
    body = "\n".join(f"- {e['term']}: {e['gloss']}" for e in entries)
    return f"{SCOPED_HEADER}\n{body}\n{SCOPED_FOOTER}\n\n"


def retrieve(U, q):
    text = (q["q"] + " " + " ".join(q["options"])).lower()
    return [U[i] for i in U if re.search(r"\b" + re.escape(U[i]["term"].lower()) + r"\b", text)]


def prompt_for(carrier, U, q):
    """Returns (prompt_prefix, retrieval_hit)"""
    if carrier == "bare" or carrier == "finetune":
        return "", None
    if carrier == "ctx_full":
        return glossary_text(list(U.values())), None
    if carrier == "ctx_retrieved":
        hits = retrieve(U, q)
        return (glossary_text(hits) if hits else ""), len(hits)
    raise ValueError(carrier)