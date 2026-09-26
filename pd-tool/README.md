# local-meaning risk index (`pd`)

This experimental tool drafts source-linked questions for locally defined terms, scores their keyed answers with a local
proxy, and ranks the resulting diagnostic uses for review. The paper establishes same-question error ranking on its tested
corpora. It does not establish that a newly generated risk map will predict arbitrary future user requests or diagnose the
cause of each error.

Paper: *When Local Definitions Matter: Diagnosing Source-Linked Language Model Errors* (under review). The reproduction materials are in `../reproduction/`.

## Install

```
pip install -e .            # Python >= 3.10; torch + transformers for the local proxy
pip install -e .[dev]       # adds pytest
```

## Inputs

Two JSONL files:

```
documents.jsonl   {"doc": "<id>", "text": "<full text>"}
glossary.jsonl    {"doc": "<id>" | "*", "term": "Trademarks", "definition": "<the document's own definition>"}
```
Contracts carry their glossary in definition clauses; communities publish theirs; teams keep them in their heads and must write
them down. Keep each definition to the stable class-level meaning; parameters, thresholds and case notes belong elsewhere.

## Pipeline

```
pd extract --documents documents.jsonl --glossary glossary.jsonl --out terms.jsonl
pd draft   --terms terms.jsonl --out questions.jsonl                # PD_DRAFT_MODEL / PD_DRAFT_BASE_URL / PD_DRAFT_API_KEY
pd score   --questions questions.jsonl --out riskmap.jsonl          # local proxy, default Qwen/Qwen2.5-7B
pd report  --riskmap riskmap.jsonl --out report.html
```

`draft` asks a model for one four-option question per occurrence. The key is proposed by that model, **not independently
verified**. The filters reject specified word and character overlaps with the definition; they cannot detect every paraphrase,
unsupported fact, duplicate option, or wrong key. Review questions against the complete source before using the scores. Use a
drafter from a different model family than the reader you plan to study. The paper's selected source review found invalid or
unanswerable questions, including contract redactions and ambiguous documentation statuses.

`score` runs a local proxy on each question with and without the definition and writes one row per occurrence:

| field | meaning |
|---|---|
| `p_bare` | proxy probability of the keyed option given only the sentence and question |
| `p_def` | the same with the document's definition shown |
| `risk` | `R = 1 - p_bare`, the paper's risk score: how little the proxy's reading supports the answer the document implies |
| `pd` | `p_def - p_bare`, the paper's probability change: how much this exact definition text moves the reading |
| `channel` | heuristic labels from fixed probability thresholds; **not** verified semantic classes |
| `repairable` | heuristic flag `p_def >= 0.75`, **not** an observed reader repair |

`report` renders a one-page summary: risk by document, highest-risk terms, and the sentences where the risk is concentrated.

## How to use the scores

- **Audit a scored question frame.** Sort reviewed diagnostic questions by `risk` and inspect the highest-ranked uses. In the
  paper, the top two of five risk bins held 23% of retained CUAD questions and 66% of their estimated reader errors. Cross-model
  error overlap motivates reuse, but ranking for a new reader should be checked rather than assumed.
- **Test a definition text.** `pd` belongs to the exact wording that was scored. Rewriting a definition changes it, so score a
  definition in the form in which it will be supplied.
- **Choose which definitions to write.** Term frequency is a transparent default. The paper did not confirm an improvement
  over frequency from its score-based allocation experiments.
- **Attach definitions to retrieved passages.** `pd gate --passages passages.jsonl --riskmap riskmap.jsonl --glossary glossary.jsonl --out gated.jsonl --threshold 0.5`
  attaches document-matched definitions above a chosen threshold, with a scope statement. A document-specific glossary entry
  overrides a global entry for the same term. The default threshold of 0.5 is an example, **not a validated operating point**;
  a threshold of 0 attaches every matched definition.

## What the scores mean and do not mean

In the paper, `risk` from Qwen2.5-7B ranked frontier models' errors on the same questions with AUROC 0.81 to 0.85 on synthetic
and contract questions, and improved with proxy size from 0.5B parameters. It also ranks errors on words that keep their usual
meaning, so it indicates where a reader is likely to be wrong, not why. It scores the drafted diagnostic questions, not incoming
user requests, and it does not measure the cost of an error.

## Benchmark

`pd bench --scores yourscores.jsonl --labels labels.jsonl` reports AUROC with a bootstrap interval and observed error by score bin for any
per-occurrence detector against released frontier-reader labels (CUAD, 1,500 occurrences; distributed with `pd-reproduction`).

## Example and tests

```
see examples/README.md
pytest                                     # unit tests, no model download
PD_TEST_MODEL=Qwen/Qwen2.5-0.5B pytest     # also exercises the proxy on CPU
```

## Licence
MIT for the code. The example contract sentences are from CUAD (CC BY 4.0).
