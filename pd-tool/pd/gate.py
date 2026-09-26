"""Experimental passage-level definition attachment for a scored corpus."""
import re

SCOPE_STATEMENT = ("The definitions below apply only within this document's own context. Words that are not listed keep their ordinary meaning, "
                   "and a listed word used outside this document keeps its ordinary meaning.")

def gate_passages(passages, riskmap, glossary, threshold=0.5):
    """passages: [{"doc", "text", ...}]; riskmap: rows from pd.score; glossary: rows from pd.io.load_glossary.
    Attaches the definition of every glossary term that occurs in the passage and whose scored risk at that sentence
    (or, if the sentence is not scored, the term's maximum risk in that document) is >= threshold."""
    global_defs = {}
    document_defs = {}
    for g in glossary:
        if g.get("doc", "*") == "*":
            global_defs[g["term"]] = g["definition"]
        else:
            document_defs.setdefault(g["doc"], {})[g["term"]] = g["definition"]
    risk_doc, risk_sent = {}, {}
    for r in riskmap:
        k = (r.get("doc"), r["term"]); risk_doc[k] = max(risk_doc.get(k, 0.0), r["risk"])
        if r.get("sentence"): risk_sent[(k, r["sentence"].strip())] = max(risk_sent.get((k, r["sentence"].strip()), 0.0), r["risk"])
    out = []
    for p in passages:
        doc, text = p.get("doc"), p["text"]; attached = []
        defs = {**global_defs, **document_defs.get(doc, {})}
        for term, g in defs.items():
            pat = re.compile(r"(?<![\w])" + re.escape(term) + r"(?![\w])", re.I) if re.search(r"[A-Za-z]", term) else re.compile(re.escape(term))
            if not pat.search(text): continue
            rk = max([v for (k, s), v in risk_sent.items() if k == (doc, term) and s in text] or [risk_doc.get((doc, term), 0.0)])
            if rk >= threshold: attached.append({"term": term, "definition": g, "risk": round(rk, 4)})
        block = (SCOPE_STATEMENT + "\nDefinitions (this document):\n" + "\n".join(f"- {a['term']}: {a['definition']}" for a in attached) + "\n\n") if attached else ""
        out.append({**p, "definitions": attached, "text_gated": block + text})
    return out
