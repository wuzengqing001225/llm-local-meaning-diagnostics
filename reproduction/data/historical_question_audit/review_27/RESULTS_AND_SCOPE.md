# Source Validity of 27 Historical Questions

## Design and observations

An 80-question source-audit sample had been fixed by hash before this review, with 20 questions from each of synthetic data, CUAD, Reddit, and DeFi. The author reviewed 27 of these questions against the available source material. Seventeen were selected because two source-screening models disagreed about the stored answer or whether the source supported an answer. Ten additional controls were sampled within corpus and model-screen strata. Consequently, the 27 reviewed questions cannot estimate a corpus-wide defect rate.

The author's source-first record contains **16 undetermined answers** and **11 selected options**. Five selected options differ from their stored keys. A differing option is not automatically a wrong key: for example, the source definitions support the stored keys in AUD-016 (`varnok`) and AUD-068 (*Multi-party Contract*). Conversely, AUD-064 was marked undetermined, yet its stored option A is contradicted by the contract: user guides and technical manuals are Documentation, for which the agreement expressly grants Allscripts rights. This item should be removed or rewritten rather than relabeled from the available old-key probabilities.

A subsequent source reconciliation, performed after reading the author record and stored keys, assigned the following **provisional** categories:

| Corpus | Stored key supported by available source | Invalid or source-insufficient | Borderline | Reviewed |
|---|---:|---:|---:|---:|
| Synthetic | 3 | 1 | 0 | 4 |
| CUAD | 2 | 6 | 1 | 9 |
| Reddit | 3 | 1 | 1 | 5 |
| DeFi | 2 | 6 | 1 | 9 |
| **Total** | **10** | **14** | **3** | **27** |

The 17 targeted questions account for 6 supported, 9 invalid/insufficient, and 2 borderline items. The ten controls account for 4 supported, 5 invalid/insufficient, and 1 borderline item. These are **descriptive counts within an intentionally enriched review**, not prevalence estimates. The reconciliation is a second look at sources, not an independent blinded second-rater study; no agreement coefficient is available.

The clearest item defects are the placeholder choices in AUD-069, the mandatory-removal wording in AUD-071 where the contract says the provider *may* remove objectionable content, and the near-duplicate SEC/Commission options in AUD-076. Other items omit a needed source condition. In AUD-052 and AUD-054, “swapping blocked/unavailable” does not say whether a token is legally unsupported or temporarily unquotable due to liquidity. The source-based interpretation also matters in the other direction: the glossary entries for *Fill*, *Burst*, and *Standard* are sufficient to interpret their constructed scenarios without requiring the exact scenarios to occur in an archived Reddit post. Three items, AUD-026, AUD-077, and AUD-056, remain borderline under a strict requirement that every clause of the keyed option be supported.

## Deletion sensitivity

For an exploratory check, the 14 clear problem items were removed from the existing matched analyses without changing any historical answer key. The maximum absolute change in error-ranking AUROC for \(R\) over the eight settings was **0.00203**; the maximum change in same-item conditional-repair AUROC for \(\Delta p\) was **0.00601**. The CUAD design-weighted \(R\) AUROC was **0.8456 before** and **0.8467 after** deletion. The synthetic repeated-sampling count of identical wrong answers remained **93 of 229 greedy errors**. A second scenario additionally removes the three borderline items; both scenarios are recorded in `deletion_sensitivity_27.json`.

These small changes show only that the **reviewed problem items** do not drive the published point estimates. Most historical questions were not reviewed. This is not a validated-only AUROC, an estimate of the overall defect rate, or evidence that the unreviewed keys are sound. Historical proxy probabilities refer to the original keyed answer; an item whose key changes requires fresh scoring or exclusion.

## Scope for the manuscript

The source review supports a limited statement: the diagnostic estimates are locally insensitive to removing the reviewed problem items, while question validity remains a material limitation, especially for the exploratory Reddit and DeFi settings. It does not turn model-authored questions into independently validated downstream requests. The paper's other boundaries also remain: \(R\) ranks errors on supplied questions but is not specific to local-meaning conflict; \(\Delta p\) measures response to an exact definition text on the same question and has not established a better advance definition-selection policy than frequency.

The review can be reported without an additional annotation round if submission timing requires stopping here. In that case, describe its nonrepresentative selection and do **not** report 14/27 as a population defect rate, five answer disagreements as five corrected keys, or the deletion analysis as validation of the full dataset.

### Concise manuscript wording

> In a source review of 27 previously selected diagnostic questions, an author independently answered 17 model-screen disagreement cases and ten stratified controls. Subsequent source reconciliation found ten items whose stored keys were supported, 14 with insufficient or invalid questions, and three borderline cases. This selected sample does not estimate the defect rate of the full dataset. Removing the 14 clear problem items from the matched analyses changed \(R\) error-ranking AUROC by at most 0.00203 and same-item conditional-repair \(\Delta p\) AUROC by at most 0.00601. This sensitivity check does not validate the unreviewed questions.
