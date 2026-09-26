import os
import pytest
from pd import io as pio
from pd.draft import stem_leak, option_leak, draft_questions
from pd.llm import MockClient
from pd.gate import gate_passages, SCOPE_STATEMENT
from pd.bench import evaluate
from pd.report import render_report

EX = os.path.join(os.path.dirname(__file__), "..", "examples", "contract")

def test_extract_and_draft_mock():
    docs, gl = pio.load_documents(f"{EX}/documents.jsonl"), pio.load_glossary(f"{EX}/glossary.jsonl")
    terms = pio.extract_occurrences(docs, gl)
    assert len(terms) == len(gl) and all(t["contexts"] for t in terms)
    Q = draft_questions(terms, MockClient(), cap=3)
    assert sum(q["n_q"] for q in Q) > 0
    for r in Q:
        for q in r["questions"]:
            assert len(q["options"]) == 4 and q["answer"] in "ABCD" and q["sentence"] in terms[[t["id"] for t in terms].index(r["id"])]["contexts"]

def test_leak_filters():
    assert stem_leak("the shorts pay the longs at settlement", ["When interest is negative the shorts pay the longs at 8:00"])
    assert not stem_leak("who settles the balance?", ["When interest is negative the shorts pay the longs at 8:00"])
    q = {"options": ["x", "the reseller must obtain prior written consent before selling", "y", "z"], "answer": "B"}
    assert option_leak(q, "Restricted Sale means any sale for which the reseller must obtain prior written consent")
    # capitalised tokens are treated as proper names and do not count as restatement
    assert not option_leak({"options": ["x", "worldwide except the United States", "y", "z"], "answer": "B"}, "Territory means worldwide except the United States")
    assert not option_leak({"options": ["x", "sales into Canada are permitted", "y", "z"], "answer": "B"}, "Territory means worldwide except the United States")

def test_gate_threshold():
    gl = [{"doc": "d1", "term": "Territory", "definition": "worldwide except the United States"}]
    risk = [{"doc": "d1", "term": "Territory", "sentence": "Distributor may sell in the Territory.", "risk": 0.8, "pd": 0.5, "channel": "instantiation", "repairable": True}]
    ps = [{"doc": "d1", "text": "Distributor may sell in the Territory."}, {"doc": "d1", "text": "Payment is due in 30 days."}]
    out = gate_passages(ps, risk, gl, threshold=0.5)
    assert out[0]["definitions"] and out[0]["text_gated"].startswith(SCOPE_STATEMENT) and not out[1]["definitions"]
    assert not gate_passages(ps, risk, gl, threshold=0.9)[0]["definitions"]

def test_document_definition_overrides_global_entry():
    gl = [{"doc": "*", "term": "Territory", "definition": "global scope"},
          {"doc": "d1", "term": "Territory", "definition": "document scope"}]
    risk = [{"doc": "d1", "term": "Territory", "risk": 0.8}]
    out = gate_passages([{"doc": "d1", "text": "Sales in the Territory."}], risk, gl, threshold=0.5)
    assert out[0]["definitions"] == [{"term": "Territory", "definition": "document scope", "risk": 0.8}]

def test_bench_and_report():
    labels = [{"id": "a", "ctx_idx": i, "reader_failed": int(i % 3 == 0)} for i in range(30)]
    scores = {("a", i): (0.9 if i % 3 == 0 else 0.1) for i in range(30)}
    r = evaluate(scores, labels, n_boot=50)
    assert r["n"] == 30 and r["auroc"] == 1.0
    html = render_report([{"doc": "d", "term": "t", "sentence": "s", "risk": 0.7, "pd": 0.4, "channel": "instantiation", "repairable": True}])
    assert "<table" in html and "risk map" in html

def test_bench_rejects_one_class_labels():
    with pytest.raises(ValueError, match="at least one matched reader error"):
        evaluate({("a", 0): 0.5}, [{"id": "a", "ctx_idx": 0, "reader_failed": 1}])

@pytest.mark.skipif(os.environ.get("PD_TEST_MODEL") is None, reason="set PD_TEST_MODEL (e.g. Qwen/Qwen2.5-0.5B) to run the proxy")
def test_score_small_model():
    from pd.score import Proxy, score_questions
    Q = [{"id": "d:Territory", "doc": "d", "term": "Territory", "definition": "worldwide except the United States, the Caribbean and cruise ships departing from US ports",
          "questions": [{"q": "A French distributor holds exclusive rights in the Territory. May it sell into Canada?",
                         "options": ["Yes, Canada is inside the Territory.", "No, Canada is outside a French distributor's region.", "Only with a separate licence.", "Only to cruise ships."],
                         "answer": "A", "ctx_idx": 0, "sentence": "Distributor has exclusive rights in the Territory."}]}]
    rows = score_questions(Q, Proxy(os.environ["PD_TEST_MODEL"]), own_gloss=True)
    r = rows[0]
    assert 0 <= r["p_bare"] <= 1 and 0 <= r["p_def"] <= 1 and r["channel"] in ("conflict", "instantiation", "consistent") and abs(r["pd"] - (r["p_def"] - r["p_bare"])) < 1e-3
