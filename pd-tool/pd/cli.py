"""pd command line: extract, draft, score, gate, report, bench."""
import argparse, json, sys
from . import io as pio

def cmd_extract(a):
    docs, gl = pio.load_documents(a.documents), pio.load_glossary(a.glossary)
    terms = pio.extract_occurrences(docs, gl, min_contexts=a.min_contexts, max_contexts=a.max_contexts)
    pio.write_jsonl(a.out, terms); print(f"[pd extract] {len(terms)} (document, term) records, {sum(len(t['contexts']) for t in terms)} occurrences -> {a.out}", file=sys.stderr)

def cmd_draft(a):
    from .llm import client_from_env
    from .draft import draft_questions
    terms = pio.read_jsonl(a.terms)
    if a.limit: terms = terms[:a.limit]
    client = client_from_env(mock=a.mock, cache_path=a.cache)
    pio.write_jsonl(a.out, draft_questions(terms, client, cap=a.cap)); print(f"[pd draft] -> {a.out}", file=sys.stderr)

def cmd_score(a):
    from .score import Proxy, score_questions
    Q = pio.read_jsonl(a.questions)
    if a.limit: Q = Q[:a.limit]
    proxy = Proxy(a.model, dtype=a.dtype)
    pio.write_jsonl(a.out, score_questions(Q, proxy, own_gloss=not a.no_own_gloss)); print(f"[pd score] -> {a.out}", file=sys.stderr)

def cmd_gate(a):
    from .gate import gate_passages
    out = gate_passages(pio.read_jsonl(a.passages), pio.read_jsonl(a.riskmap), pio.load_glossary(a.glossary), threshold=a.threshold)
    pio.write_jsonl(a.out, out); print(f"[pd gate] {sum(bool(p['definitions']) for p in out)}/{len(out)} passages received definitions -> {a.out}", file=sys.stderr)

def cmd_report(a):
    from .report import render_report
    open(a.out, "w", encoding="utf-8").write(render_report(pio.read_jsonl(a.riskmap), title=a.title)); print(f"[pd report] -> {a.out}", file=sys.stderr)

def cmd_bench(a):
    from .bench import evaluate
    sc = {(r["id"], r["ctx_idx"]): r[a.field] for r in pio.read_jsonl(a.scores)}
    res = evaluate(sc, pio.read_jsonl(a.labels)); print(json.dumps(res, indent=1))

def main(argv=None):
    ap = argparse.ArgumentParser(prog="pd", description="source-linked diagnostic scoring for locally defined terms")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("extract", help="documents + glossary -> terms with every occurrence sentence"); p.add_argument("--documents", required=True); p.add_argument("--glossary", required=True); p.add_argument("--out", required=True); p.add_argument("--min-contexts", type=int, default=1); p.add_argument("--max-contexts", type=int, default=None); p.set_defaults(fn=cmd_extract)
    p = sp.add_parser("draft", help="one meaning-dependent question per occurrence (needs PD_DRAFT_* env or --mock)"); p.add_argument("--terms", required=True); p.add_argument("--out", required=True); p.add_argument("--cap", type=int, default=12); p.add_argument("--limit", type=int, default=0); p.add_argument("--mock", action="store_true"); p.add_argument("--cache", default=None); p.set_defaults(fn=cmd_draft)
    p = sp.add_parser("score", help="score with a local proxy -> risk map"); p.add_argument("--questions", required=True); p.add_argument("--out", required=True); p.add_argument("--model", default="Qwen/Qwen2.5-7B"); p.add_argument("--dtype", default="bfloat16"); p.add_argument("--limit", type=int, default=0); p.add_argument("--no-own-gloss", action="store_true", help="skip the proxy's own-gloss condition (channels then never read 'conflict')"); p.set_defaults(fn=cmd_score)
    p = sp.add_parser("gate", help="attach definitions to passages where risk >= threshold"); p.add_argument("--passages", required=True); p.add_argument("--riskmap", required=True); p.add_argument("--glossary", required=True); p.add_argument("--out", required=True); p.add_argument("--threshold", type=float, default=0.5); p.set_defaults(fn=cmd_gate)
    p = sp.add_parser("report", help="HTML summary of a risk map"); p.add_argument("--riskmap", required=True); p.add_argument("--out", required=True); p.add_argument("--title", default="Local-meaning risk map"); p.set_defaults(fn=cmd_report)
    p = sp.add_parser("bench", help="AUROC of a detector against released reader labels"); p.add_argument("--scores", required=True); p.add_argument("--labels", required=True); p.add_argument("--field", default="risk"); p.set_defaults(fn=cmd_bench)
    a = ap.parse_args(argv); a.fn(a)

if __name__ == "__main__":
    main()
