# Example: one CUAD contract

`documents.jsonl` holds the sentences of one public contract (WORLDWIDESTRATEGIESINC_11_02_2005-EX-10-RESELLER AGREEMENT) that contain a defined term; `glossary.jsonl` holds the
contract's own definitions of 12 terms; `passages.jsonl` is a stand-in for retrieved passages.

```
pd extract --documents examples/contract/documents.jsonl --glossary examples/contract/glossary.jsonl --out work/terms.jsonl
pd draft   --terms work/terms.jsonl --out work/questions.jsonl --mock          # replace --mock with PD_DRAFT_* env vars for a real drafter
pd score   --questions work/questions.jsonl --out work/riskmap.jsonl --model Qwen/Qwen2.5-0.5B   # CPU-sized proxy; use Qwen2.5-7B on a GPU
pd gate    --passages examples/contract/passages.jsonl --riskmap work/riskmap.jsonl --glossary examples/contract/glossary.jsonl --out work/gated.jsonl
pd report  --riskmap work/riskmap.jsonl --out work/report.html
```
With `--mock` the questions are placeholders, so the risk map from this dry run is not meaningful; it exercises the pipeline end to end.
