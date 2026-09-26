"""Input formats and occurrence extraction.

documents.jsonl   {"doc": "<document id>", "text": "<full text>"}
glossary.jsonl    {"doc": "<document id or '*' for all documents>", "term": "Territory", "definition": "<the document's own definition>"}
terms.jsonl       (produced by extract_occurrences) {"id": "<doc>:<term>", "doc", "term", "definition", "contexts": ["sentence", ...]}
"""
import json, re

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def load_documents(path):
    docs = read_jsonl(path)
    for d in docs:
        if "doc" not in d or "text" not in d:
            raise ValueError("documents.jsonl rows need 'doc' and 'text'")
    return docs

def load_glossary(path):
    rows = read_jsonl(path)
    for r in rows:
        if "term" not in r or "definition" not in r:
            raise ValueError("glossary.jsonl rows need 'term' and 'definition'")
        r.setdefault("doc", "*")
    return rows

# sentence boundaries: ASCII terminators followed by a capital or quote, blank lines, and CJK full-width terminators
_SENT = re.compile(r"(?<=[.!?;])\s+(?=[A-Z(\"'])|\n{2,}|(?<=[。！？；])")

def split_sentences(text):
    parts = [p.strip() for p in _SENT.split(text) if p and p.strip()]
    return [p for p in parts if len(p) >= 8]

def extract_occurrences(documents, glossary, min_contexts=1, max_contexts=None):
    """One record per (document, term) with every sentence in which the term occurs.

    A glossary row with doc='*' applies to every document; a row with a specific doc applies to that document only
    and overrides a '*' row for the same term."""
    by_doc = {d["doc"]: split_sentences(d["text"]) for d in documents}
    out = []
    for d in documents:
        sents = by_doc[d["doc"]]
        entries = {g["term"]: g for g in glossary if g["doc"] == "*"}
        entries.update({g["term"]: g for g in glossary if g["doc"] == d["doc"]})
        for term, g in entries.items():
            pat = re.compile(r"(?<![\w])" + re.escape(term) + r"(?![\w])", re.I) if re.search(r"[A-Za-z]", term) else re.compile(re.escape(term))
            ctx = [s for s in sents if pat.search(s)]
            if len(ctx) < min_contexts:
                continue
            if max_contexts:
                ctx = ctx[:max_contexts]
            out.append({"id": f"{d['doc']}:{term}", "doc": d["doc"], "term": term, "definition": g["definition"], "contexts": ctx})
    return out
