# Historical question audit: released subset

This folder holds the fixed source-screen sample and the completed selected-item review:

- `blind_80/manifest.json` — the fixed-hash sample specification: selection seed,
  `SHA256(seed, corpus, source-question-id)` ordering, the five preregistered strata with
  their frame and sample counts, and input SHA-256 values.
- `blind_80/selected_questions.jsonl` — the key-free 80-item packet. Each row carries
  corpus, stratum, question, options, `audit_id` and the relative path of the source card.
  There is no answer key in this file.
- `blind_80/sources/` — the source cards and source documents the packet points at.
- `blind_80/answer_sheet_to_fill.csv` — blank template retained for inspecting the fixed sample.
- `model_triage_summary.json`, `sonnet5_deepseek_cross_summary.json`,
  `sonnet5_deepseek_sample_exclusion_sensitivity.json` — the aggregate model screen.
  These are model-screen counts over 80 items, not adjudicated key errors.
- `review_27/` — English author answers for 17 model-screen disagreements and ten stratified
  controls, followed by a separate source reconciliation and deletion sensitivity. The 27
  selected items do not estimate the defect rate of the full question frame.

The fixed-hash sample IDs for the stratified CUAD validation sample live separately at
`audit/t2_sample_ids.jsonl`, with `audit/t2_sampler.py` as the sampler.

**Not included.** Per-item model-screen judgements and the sealed historical key ledger.
The completed author record and the subsequent source assessment remain separate files so
that an answer disagreement is not mistaken for a confirmed wrong key.
