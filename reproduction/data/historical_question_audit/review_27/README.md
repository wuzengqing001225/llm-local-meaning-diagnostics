# Historical Question Source Review

This folder contains the English-language record of the 27-item source review reported in the paper (Section 6 and Appendix B). Quoted source text follows the licence of its corpus (see DATA_CARD.md). Source cards are in `../blind_80/sources/`.

| File | Content |
|---|---|
| `AUTHOR_REVIEW_27.md` | Readable question-by-question author answers and notes. |
| `author_review_27_en.csv` | Questions, options, source-card links, the author's source-first answers, quotations, and comments. |
| `source_reconciliation_27_en.csv` | Stored keys, prior model-screen categories, and a subsequent source-based assessment, kept separate from the author's answers. |
| `deletion_sensitivity_27.json` | Matched-setting estimates before and after deleting 14 clear problem items, with a three-item borderline extension. |
| `RESULTS_AND_SCOPE.md` | Design, aggregate findings, interpretation, and publication-safe wording. |

The 17 targeted items were selected for model-screen disagreements. The ten controls were stratified by corpus and model-screen agreement. These 27 items are **not** a probability sample of all historical questions. The subsequent source assessment is not a second blinded human annotation. No historical probabilities were relabeled, and no manuscript file was changed while preparing this record.

AUD-064 is encoded as `undetermined` because the author identified B, C, and D as simultaneously plausible, without selecting a unique option.

The deletion sensitivity is recomputed from the released data by `analysis/reviewer_controls/review27_deletion_check.py`.
