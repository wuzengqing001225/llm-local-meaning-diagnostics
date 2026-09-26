# Offline supplementary checks

The scripts here use archived model outputs and the Python standard library. They make no API calls. From the reproduction root:

```sh
python analysis/offline_checks/offline_checks_20260926.py \
  --data data --recovered audit/recovered \
  --term-csv analysis/offline_checks/term_meaning_difference.csv \
  --out analysis/offline_checks/results_rerun.json
```

`results_rerun.json` should match `offline_checks_results.json`. `term_texts_v1_reader_aligned.json` holds the source and prior glosses aligned to the synthetic reader arms. `embed_term_sims.py` can recalculate text embeddings with `BAAI/bge-base-en-v1.5`, but the exact historical weight revision and vectors were not archived. Downstream associations from the supplied CSV and the reader outcomes are reproducible; bitwise recovery of the original cosine values is not guaranteed. The legacy embedding script uses an absent hard-coded input filename and is retained only as provenance.

The checks establish several boundaries on the paper's interpretation:

- A seven-billion-parameter proxy score ranks reader errors on the same source-linked questions. It also ranks errors on designed usual-meaning terms and Reddit non-glossary controls, so it is not a detector specific to meaning conflict.
- On 761 synthetic questions, the source definition changes DeepSeek V4 Flash accuracy from 0.699 to 0.966; a domain-conditioned prior gloss reaches 0.708. A lexical-overlap screen can pick the correct answer from a drafted gloss on 0.686 of the 456 matched questions. The intervention remains positive on the 143 questions not flagged by that screen (error 0.308 to 0.091), without proving that all answer cues have been removed.
- The valid leave-one-question-out partial-identification interval for risk-gated retrieval accuracy is [0.733, 0.893] on CUAD, compared with retrieval accuracy 0.821. For Reddit it is [0.874, 0.919] over all questions, compared with 0.866. These are finite-workload bounds and not a held-out term or document evaluation.
- Question-independent definition distance distinguishes designed synthetic meaning classes (AUROC 0.946 on 66 terms without domain context; 0.977 on 157 with it). Coverage differs. Associations with repair on Reddit and DeFi are weak or inconsistent, so term distance cannot substitute for a question-level test.
- The definition text matters. A probability change computed for a model-drafted gloss must not be paired with a reader arm that received the community source entry. In source-entry-aligned development comparisons, score-based library selection has not shown an advantage over frequency.
- After excluding both source-conflicted synthetic items, Jev's confidence ranks its own bare errors at AUROC 0.643 and its definition-arm errors at 0.815, each on 761 questions. These are own-error diagnostics for a different reader.

The selected 27-question source review and its deletion sensitivity are under `data/historical_question_audit/review_27/`. Its category counts are not corpus-wide defect rates. `R_VS_DP_DECOMPOSITION.md` gives the algebraic relation between $R$ and the signed probability change.
