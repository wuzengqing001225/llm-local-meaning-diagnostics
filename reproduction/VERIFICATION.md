# VERIFICATION

Headline values of the paper against what this package recomputes. Every recomputed value was read out of a file written by one of the author's own scripts during the build of this package. No data file and no script was changed to make a row agree.

**20 of 20 listed values reproduce.**

| Value | Paper | Recomputed | Script | Match |
|---|---|---|---|---|
| Synthetic stable wrong errors (10 samples identical and wrong, of greedy errors; 761-question frame) | 93/229 = 40.6% | 93/229 = 40.6% | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| R AUROC, synthetic / DeepSeek | 0.848 | 0.8479 | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| R AUROC, synthetic / GPT-6 | 0.809 | 0.8095 | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| R AUROC, CUAD 1,500-question validation | 0.815 | 0.8149 | `reproduce.py` | yes |
| Same-denominator uncertainty baselines on 456 questions (consistency / entropy / confidence) | 0.616 / 0.616 / 0.617 | 0.6163 / 0.6162 / 0.6166 (n=456) | `analysis/paper_audit (shipped audit output) interest_sensitivity.json` | yes |
| Synthetic 761-question accuracy: no definition / source definition / model's own domain gloss | 0.699 / 0.966 / 0.708 | 0.6991 / 0.9658 / 0.7083 (n=761) | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| Synthetic repairs / harms: source definition vs model's own gloss | 209 repairs, 6 harms vs 86 repairs, 79 harms | 209 / 6 vs 86 / 79 | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| Lexical-cue rule picks the keyed answer, synthetic | 0.686 | 0.6864 (shuffled baseline 0.0667) | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| Unflagged synthetic items: count, and error rate bare then with definition | 143 items, 0.308 -> 0.091 | 143 items, 0.3077 -> 0.0909 | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| CUAD strata failure rate, lowest stratum | 1.0% | 1.0% | `reproduce.py` | yes |
| CUAD strata failure rate, highest stratum | 52.3% | 52.3% | `reproduce.py` | yes |
| CUAD 1,500-question unweighted failure rate | 21.3% | 21.3% | `reproduce.py` | yes |
| CUAD inverse-inclusion-weighted failure rate | 13.2% | 13.2% | `reproduce.py` | yes |
| CUAD weighted R AUROC | 0.846 | 0.8456 | `reproduce.py` | yes |
| RAG leave-one-out partial identification, CUAD | [0.733, 0.893] | [0.7325, 0.8933] (identified 1007/1200) | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| RAG leave-one-out partial identification, Reddit all questions | [0.874, 0.919] | [0.8742, 0.9195] (identified 1328/1391) | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| Reddit community-entry A-to-B repair AUROC, with community-clustered interval | 0.600 [0.475, 0.717] | 0.5998 [0.4751, 0.7172] | `analysis/paper_audit (shipped audit output) audit/gold_repair_auc.json` | yes |
| Reddit A-to-B repaired of bare failures, and harms | 126/147 repaired, 4 harms | 126/147 repaired, 4 harms | `analysis/paper_audit (shipped audit output) audit/gold_repair_auc.json` | yes |
| Jev confidence predicts its own error, bare condition: synthetic / Reddit / CUAD | 0.643 / 0.660 / 0.636 | 0.6431 / 0.6604 / 0.6358 (synthetic n=761) | `analysis/offline_checks/offline_checks_20260926.py` | yes |
| Jev confidence predicts its own error, definition condition: synthetic | 0.815 | 0.8148 (n=761) | `analysis/offline_checks/offline_checks_20260926.py` | yes |

## How these were produced

```sh
python reproduce.py
python analysis/offline_checks/offline_checks_20260926.py \
    --data data --recovered audit/recovered \
    --term-csv analysis/offline_checks/term_meaning_difference.csv \
    --out analysis/offline_checks/results_rerun.json
cd analysis/paper_audit && python rebuild_tables_figures.py
python verify_release.py
```

Script exit codes from this build: `offline_checks_20260926.py` = 0, `rebuild_tables_figures.py` = 0, `reproduce.py` = 0.

`reproduce.py` reports `status: passed` and compares every main setting against the frozen values in `analysis/expected_main.json`; the settings it verified were Synthetic / DeepSeek, Synthetic / GPT6, Reddit / DeepSeek, Reddit / GPT6, DeFi / DeepSeek, DeFi / GPT5.6, DeFi / GPT6, CUAD library / GPT5.6. It made 0 API calls.

The offline checks rerun (`analysis/offline_checks/results_rerun.json`) is identical to the results the author shipped in `analysis/offline_checks/offline_checks_results.json`.

## Reading the two synthetic frames

The synthetic collection appears with two denominators and both are correct in their place. The archived frame has 763 questions, 457 of them in the proxy overlap. The 2026-09-26 correction excludes the two items whose source text and definition conflict, giving 761 questions and 456 in the overlap. The paper's same-denominator uncertainty baselines (0.616 / 0.616 / 0.617) are the corrected 456-question figures, recorded in `interest_sensitivity.json` under the `exclude_direct_2` scenario and consumed by `rebuild_tables_figures.py`. Running `reproduce.py` over the archived 457-question frame gives 0.6189 / 0.6188 / 0.6169 for the same three baselines. Both are in this package; the corrected pair is the one the paper reports.

## Not verified here

Table 2's two rows are reported by the author as 0.8094577 [0.7627638, 0.8560215] and 0.8093046 [0.7625671, 0.8555733], identical only at three decimals. The offline checks script uses a different bootstrap seed, so its interval endpoints differ slightly and must not be substituted for either row. The point estimates recompute: `offline_checks_results.json` gives `table2_duplicate_rows`.

## Human source review

`analysis/reviewer_controls/review27_deletion_check.py` recomputes the deletion sensitivity of the 27-item review from the released data.

| Quantity | Paper | Recomputed |
|---|---|---|
| Max change in R error-ranking AUROC, 14 invalid items removed | 0.00203 | 0.00203 |
| CUAD R AUROC, before / after | 0.815 / 0.817 | 0.8149 / 0.8169 |
| CUAD design-weighted AUROC, before / after | 0.8456 / 0.8467 | 0.8456 / 0.8467 |
| Max change, 17 items removed (with borderline) | not stated | 0.0018 |

The maximum change in same-question repair AUROC of the probability change is 0.00601, computed from `data/historical_question_audit/review_27/deletion_sensitivity_27.json`. The maximum change in R AUROC is 0.00203. The earlier one-decimal-upward values 0.0061 and 0.0021 remain conservative upper bounds, but the paper and verification table now use the unrounded values.
