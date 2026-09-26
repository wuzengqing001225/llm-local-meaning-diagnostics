# What the proxy scores measure: term-level systematic divergence vs question-level difficulty (2026-09-23)

Data: released per-question records (proxy Qwen2.5-7B; readers as labelled). Term = one defined word in one corpus (CUAD: word × contract). 'Other questions of the term' = leave-one-out mean over the term's remaining questions.

## T1. Is reader failure a property of the term or of the question?

| setting | fail rate | reader's own failures on other q's of the term → this q | proxy R, own q | proxy R, other q's of term | proxy R, within term only |
|---|---|---|---|---|---|
| synthetic/DeepSeek | 0.287 | 0.723 | 0.848 | 0.738 | 0.761 |
| synthetic/GPT6 | 0.182 | 0.771 | 0.809 | 0.760 | 0.727 |
| Reddit/DeepSeek | 0.301 | 0.711 | 0.808 | 0.677 | 0.771 |
| Reddit/GPT6 | 0.146 | 0.803 | 0.720 | 0.637 | 0.732 |
| DeFi/DeepSeek | 0.282 | 0.710 | 0.809 | 0.678 | 0.818 |
| CUAD/GPT5.6 | 0.224 | 0.477 | 0.815 | 0.511 | 0.822 |

(CUAD row restricted to the 848 questions whose word×contract has ≥2 sampled occurrences.)

## T2–T4. Which score carries the local-vs-usual difference?

Among failures only (the reader was wrong without the definition), AUROC for 'the definition repairs it' vs 'still wrong with the definition':

| setting | failures | share repaired | R (own q) | Δp (own q) | local−usual contrast (own q) | R (other q's) | Δp (other q's) | contrast (other q's) |
|---|---|---|---|---|---|---|---|---|
| synthetic/DeepSeek | 131 | 0.91 | 0.458 | 0.983 | 0.789 | 0.487 | 0.907 | 0.74 |
| synthetic/GPT6 | 83 | 0.92 | 0.421 | 0.962 | 0.915 | 0.374 | 0.976 | 0.942 |
| Reddit/DeepSeek | 419 | 0.6 | 0.453 | 0.858 | 0.816 | 0.465 | 0.824 | 0.806 |
| Reddit/GPT6 | 203 | 0.52 | 0.554 | 0.812 | 0.758 | 0.562 | 0.864 | 0.81 |
| DeFi/DeepSeek | 107 | 0.56 | 0.501 | 0.863 | 0.537 | 0.389 | 0.85 | 0.505 |
| CUAD/GPT5.6 | 320 | 0.51 | 0.462 | 0.712 | 0.704 | 0.486 | 0.622 | 0.599 |

Design-label checks (term level): contrast = p(correct | local gloss) − p(correct | reader's own usual gloss) on the proxy.
- Synthetic: separates redefined common words from standard-meaning words at AUROC 0.916 (R 0.818, Δp 0.779); mean contrast +0.409 / +0.240 / +0.021 for redefined / invented / standard.
- Inside standard-meaning terms (no local meaning by construction) R still predicts failure at 0.921 (DeepSeek) and 0.846 (GPT 6).
- Reddit: glossary vs control words separate weakly for every score (R 0.671, Δp 0.551, contrast 0.535); control-word failure is 0.235 (DeepSeek) and R predicts it at 0.842.

## Reading
1. R = 1 − p_bare is mostly a question-difficulty score shared by proxy and reader. It has a term component in synthetic/Reddit/DeFi (other-q AUROC 0.64–0.76) and none in CUAD (0.51), predicts failure equally well where no local meaning exists, and is at chance (0.37–0.56) for telling local-meaning failures from other failures.
2. Δp (and the local−usual contrast) carries the systematic local-vs-usual difference. Among failures it separates definition-repairable from unrepairable at 0.71–0.98, and the value computed on OTHER questions of the same term does almost as well (0.62–0.98): it is a transferable term-level property.
3. Half of the failures on real corpora are not definition-repairable (repaired share 0.51–0.60 vs 0.91–0.92 on synthetic), so R's headline AUROC on real corpora ranks a mixture of local-meaning and other errors.
4. The product R×Δp does not beat R for the joint event (fails and is repaired), because the event requires failure first. The two scores answer two sequential questions and should be used as a two-stage triage, not multiplied.