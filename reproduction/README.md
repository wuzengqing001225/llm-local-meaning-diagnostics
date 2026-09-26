# Reproduction package

Reproduction package for *When Local Definitions Matter: Diagnosing Source-Linked Language Model Errors*, a study of errors on diagnostic questions about locally defined terms and source-grounded definition interventions.

This package merges the author's current reproduction release (release_20260923) with the
2026-09-26 offline supplementary checks and the paper-definition audit, and adds the
development experiments the paper cites. The main numerical analyses recompute offline: no API key,
model download, GPU, or network access. Exact regeneration of the historical definition-distance
embedding values is limited by an unarchived model weight revision; their downstream statistics
and the other archived outputs remain inspectable.

## Purpose

Three things should be possible with this package alone:

1. Recompute the completed statistical results of the paper from the original model
   outputs, and check them against the frozen expected values.
2. Re-run the 2026-09-26 supplementary checks (leakage, control arms, RAG leave-one-out
   partial identification, term-level meaning difference) and compare against the shipped
   output.
3. Inspect the development experiments behind the design decisions, including the ones
   that did not confirm a positive result.

## Layout

```
README.md                     this file
VERIFICATION.md               headline paper values vs recomputed values
REPRODUCTION_NOTES.md         the author's release notes for release_20260923
DATA_CARD.md                  per-corpus data description
LICENSE.md                    licences
CITATION.cff                  citation metadata
SOURCE_CATALOG.json           per-file corpus, kind, size and SHA-256 of the release data
RELEASE_STATUS.json           what is complete and what is still pending
MANIFEST.json                 SHA-256 over every shipped file of this package
TESTING.md                    the author's test notes
reproduce.py                  one-command numerical reproduction
verify_release.py             checks every file against MANIFEST.json
requirements.txt              numpy, scipy, matplotlib

analysis/                     current statistical code and frozen expected values
  recompute.py                main statistics
  recompute_extra.py          supplementary statistics
  verify_recovered.py         validates the recovered response views
  resolve_rag.py              RAG cache-to-arm linkage
  expected_main.json          frozen expected values for the main settings
  expected_extra.json         frozen expected values for the supplementary settings
  results/                    written by reproduce.py (not covered by MANIFEST.json)
  offline_checks/             2026-09-26 offline supplementary checks
  reviewer_controls/          2026-09-26 key-free proxy scores, by-class stability and detection, no-cue definition arms
  paper_audit/                paper-definition audit: table/figure rebuild and audit JSON

data/                         source inputs and original model outputs, by corpus
  <corpus>/inputs/            source inputs and question sets
  <corpus>/raw_outputs/       original experiment outputs, unchanged
  <corpus>/analysis/          original derived summaries, for provenance only
  shared_library/             shared definition-library development study
  historical_question_audit/  released subset of the historical question audit
  development/                development experiments cited by the paper

programs/                     programs for the added datasets
  development/<experiment>/   the program folder matching data/development/<experiment>/
  shared_library/             shared-library development programs
  shared_library_runner/      standalone runner for the shared-library study
  historical_source_audit/    programs behind data/historical_question_audit/

audit/                        recovered response views, sampler and fixed sample IDs
provenance/                   model revisions, confirmation records, cache evidence
analysis_results/             the outputs as shipped in release_20260923, for comparison
scripts/, pdwlib/             historical experiment implementations
  paper/                        current PDF and LaTeX source, split into source/section/ and source/appendix/
```

`data/<corpus>/analysis/` holds the original derived summaries and is kept for provenance.
It is not the entry point for current statistics; `analysis/` is.

## How to run each check

Python 3.10 or newer.

```sh
python -m pip install -r requirements.txt
```

**1. Release integrity.** Verifies every shipped file against `MANIFEST.json`:

```sh
python verify_release.py
```

**2. Main numerical reproduction.** Recomputes R and probability-change AUROCs, cluster
intervals, same-denominator uncertainty baselines, stratified CUAD estimates, paired
repairs and harms, and public-task outcomes; validates the recovered labels and the RAG
cache-to-arm mapping; and compares against `analysis/expected_main.json`:

```sh
python reproduce.py
```

Results are written to `analysis/results/`. Do not pass `--figures`: that option expects
the paper folder to contain `rebuild_tables_figures.py` and `data_summary.json`, and the
paper folder of this package holds only the paper itself. Use step 4 instead.

**3. Offline supplementary checks (2026-09-26).**

```sh
python analysis/offline_checks/offline_checks_20260926.py \
    --data data \
    --recovered audit/recovered \
    --term-csv analysis/offline_checks/term_meaning_difference.csv \
    --out analysis/offline_checks/results_rerun.json
```

See `analysis/offline_checks/README.md`, which also carries English summaries of the
author's Chinese reports for this round.

**4. Paper tables and figures.**

```sh
cd analysis/paper_audit && python rebuild_tables_figures.py
```

This reads `data_summary.json` and writes the table `.tex` fragments and `figs/`.

## Canonical file notes

Some filenames occur more than once with different bytes. The canonical copy for each:

- `B_candidates_private.jsonl` appears 2 times with different bytes: `data/development/gitlab_membership_pilot/B_candidates_private.jsonl` (20808 bytes); `data/development/gitlab_pilot/B_candidates_private.jsonl` (15972 bytes)
- `B_checks.jsonl` appears 2 times with different bytes: `data/development/contract_allocation_v7/B_checks.jsonl` (71393 bytes); `data/development/gitlab_pilot/B_checks.jsonl` (10030 bytes)
- `B_drafts.jsonl` appears 3 times with different bytes: `data/development/contract_allocation_v7/B_drafts.jsonl` (214149 bytes); `data/development/gitlab_membership_pilot/B_drafts.jsonl` (39546 bytes); `data/development/gitlab_pilot/B_drafts.jsonl` (27201 bytes)
- `__init__.py` appears 2 times with different bytes: `pdwlib/__init__.py` (114 bytes); `programs/development/independent_B_v4/localrisk/__init__.py` (97 bytes)
- `analysis.json` appears 4 times with different bytes: `data/development/boundary_development_v5/dev_pilot/analysis.json` (19718 bytes); `data/development/boundary_development_v6/analysis.json` (15101 bytes); `data/development/contract_allocation_v7/analysis.json` (11869 bytes); `data/shared_library/gold_aligned_development/analysis.json` (105859 bytes)
- `api_client.py` appears 2 times with different bytes: `programs/shared_library/api_client.py` (3194 bytes); `programs/shared_library_runner/api_client.py` (3265 bytes)
- `batch_01.md` appears 2 times with different bytes: `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_01.md` (32009 bytes); `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_01.md` (42894 bytes)
- `batch_02.md` appears 2 times with different bytes: `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_02.md` (33011 bytes); `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_02.md` (48701 bytes)
- `batch_03.md` appears 2 times with different bytes: `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_03.md` (38718 bytes); `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_03.md` (57371 bytes)
- `batch_04.md` appears 2 times with different bytes: `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_04.md` (43450 bytes); `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_04.md` (63762 bytes)
- `batch_05.md` appears 2 times with different bytes: `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_05.md` (48204 bytes); `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_05.md` (53575 bytes)
- `batch_06.md` appears 2 times with different bytes: `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_06.md` (43666 bytes); `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_06.md` (3355 bytes)
- `common.py` appears 2 times with different bytes: `programs/development/contract_allocation_v7/common.py` (2301 bytes); `programs/development/independent_B_v4/localrisk/common.py` (4160 bytes)
- `diagnostics_A.jsonl` appears 4 times with different bytes: `data/development/boundary_development_v5/dev_pilot/diagnostics_A.jsonl` (19579 bytes); `data/development/contract_allocation_v7/diagnostics_A.jsonl` (85981 bytes); `data/development/independent_B_v4/_study/diagnostics_A.jsonl` (4174372 bytes); `data/development/independent_B_v4/evaluation/_work/diagnostics_A.jsonl` (4174372 bytes)
- `execution_status.json` appears 2 times with different bytes: `data/development/corpus_budget_preflight/execution_status.json` (4808 bytes); `data/shared_library/execution_status.json` (4117 bytes)
- `llm.py` appears 2 times with different bytes: `pdwlib/llm.py` (13026 bytes); `provenance/rag_source/pdwlib/llm.py` (13963 bytes)
- `manifest.json` appears 9 times with different bytes: `data/development/boundary_development_v5/dev_pilot/manifest.json` (744 bytes); `data/development/boundary_development_v5/formal_frame/final_review/review_batches/manifest.json` (8401 bytes); `data/development/boundary_development_v5/formal_frame/review_packets_base/manifest.json` (6670 bytes); `data/development/boundary_development_v6/seed_frame/manifest.json` (620 bytes); `data/development/gitlab_pilot/source_policy_pages/manifest.json` (1231 bytes); `data/development/independent_B_v4/evaluation/_work/snapshot/manifest.json` (694 bytes); `data/development/independent_B_v4/evaluation/_work/tasks/manifest.json` (621 bytes); `data/historical_question_audit/blind_80/manifest.json` (2179 bytes); `data/shared_library/gold_aligned_development/manifest.json` (517 bytes)
- `plan_budget.py` appears 2 times with different bytes: `programs/development/boundary_development_v5/plan_budget.py` (5454 bytes); `programs/development/contract_allocation_v7/plan_budget.py` (2888 bytes)
- `plan_summary.json` appears 2 times with different bytes: `data/development/independent_B_v4/evaluation/_work/mechanism_plan/plan_summary.json` (391 bytes); `data/development/independent_B_v4/evaluation/_work/plan/plan_summary.json` (703 bytes)
- `rag_harness.py` appears 2 times with different bytes: `provenance/rag_source/rag_harness.py` (13728 bytes); `scripts/rag_harness.py` (14097 bytes)
- `reader_results.jsonl` appears 2 times with different bytes: `data/development/boundary_development_v6/reader_results.jsonl` (94387 bytes); `data/development/contract_allocation_v7/reader_results.jsonl` (329443 bytes)
- `report.md` appears 3 times with different bytes: `data/development/independent_B_v4/evaluation/analysis/report.md` (11227 bytes); `data/development/independent_B_v4/evaluation/mechanism/report.md` (1176 bytes); `data/development/independent_B_v4/evaluation/report.md` (11342 bytes)
- `requests.jsonl` appears 2 times with different bytes: `data/development/independent_B_v4/evaluation/_work/mechanism_plan/requests.jsonl` (207365 bytes); `data/development/independent_B_v4/evaluation/_work/plan/requests.jsonl` (699282 bytes)
- `requirements.txt` appears 2 times with different bytes: `programs/development/independent_B_v4/requirements.txt` (134 bytes); `requirements.txt` (49 bytes)
- `resolution.json` appears 2 times with different bytes: `analysis_results/resolution.json` (2586 bytes); `provenance/resolution.json` (2587 bytes)
- `run_B_reader.py` appears 2 times with different bytes: `programs/shared_library/run_B_reader.py` (10860 bytes); `programs/shared_library_runner/run_B_reader.py` (10829 bytes)
- `run_main.py` appears 3 times with different bytes: `programs/development/contract_allocation_v7/run_main.py` (1286 bytes); `programs/development/independent_B_v4/run_main.py` (87 bytes); `programs/shared_library_runner/run_main.py` (9314 bytes)
- `run_pilot.py` appears 2 times with different bytes: `programs/development/boundary_development_v6/run_pilot.py` (3149 bytes); `programs/development/gitlab_pilot/run_pilot.py` (12503 bytes)
- `score_A.py` appears 3 times with different bytes: `programs/development/boundary_development_v5/score_A.py` (6337 bytes); `programs/development/contract_allocation_v7/score_A.py` (3371 bytes); `programs/shared_library_runner/score_A.py` (9640 bytes)
- `scored_trials.jsonl` appears 2 times with different bytes: `data/development/independent_B_v4/evaluation/analysis/scored_trials.jsonl` (1373360 bytes); `data/development/independent_B_v4/evaluation/mechanism/scored_trials.jsonl` (64647 bytes)
- `scores_A.jsonl` appears 3 times with different bytes: `data/development/boundary_development_v5/dev_pilot/scores_A.jsonl` (16868 bytes); `data/development/independent_B_v4/_study/scores_A.jsonl` (931041 bytes); `data/development/independent_B_v4/evaluation/_work/scores_A.jsonl` (931041 bytes)
- `source_cards.jsonl` appears 2 times with different bytes: `data/development/contract_allocation_v7/source_cards.jsonl` (94122 bytes); `data/development/gitlab_pilot/source_cards.jsonl` (3551 bytes)
- `source_checks.jsonl` appears 3 times with different bytes: `data/development/boundary_development_v6/source_checks.jsonl` (25558 bytes); `data/development/contract_allocation_v7/source_checks.jsonl` (24290 bytes); `data/shared_library/gold_aligned_development/source_checks.jsonl` (128605 bytes)
- `summary.json` appears 3 times with different bytes: `data/development/independent_B_v4/evaluation/analysis/summary.json` (82838 bytes); `data/development/independent_B_v4/evaluation/mechanism/summary.json` (21974 bytes); `data/development/independent_B_v4/evaluation/summary.json` (83729 bytes)
- `tasks_B.jsonl` appears 3 times with different bytes: `data/development/boundary_development_v5/dev_pilot/tasks_B.jsonl` (30920 bytes); `data/development/independent_B_v4/_study/tasks_B.jsonl` (298057 bytes); `data/development/independent_B_v4/evaluation/_work/tasks_B.jsonl` (298057 bytes)
- `tasks_private.jsonl` appears 2 times with different bytes: `data/development/boundary_development_v6/tasks_private.jsonl` (14967 bytes); `data/development/contract_allocation_v7/tasks_private.jsonl` (49869 bytes)
- `tasks_public.jsonl` appears 3 times with different bytes: `data/development/boundary_development_v6/tasks_public.jsonl` (10235 bytes); `data/development/contract_allocation_v7/tasks_public.jsonl` (29038 bytes); `data/development/independent_B_v4/evaluation/_work/tasks/tasks_public.jsonl` (50304 bytes)
- `trials.jsonl` appears 2 times with different bytes: `data/development/independent_B_v4/evaluation/_work/mechanism_plan/trials.jsonl` (43237 bytes); `data/development/independent_B_v4/evaluation/_work/plan/trials.jsonl` (1237757 bytes)
- `v1_weights.jsonl` appears 2 times with different bytes: `data/synthetic_v1/inputs/v1_weights.jsonl` (414247 bytes); `data/synthetic_v1/raw_outputs/v1_weights.jsonl` (446209 bytes)
- `verification.json` appears 3 times with different bytes: `analysis/paper_audit/verification.json` (559 bytes); `analysis_results/recovered/verification.json` (8561 bytes); `data/development/contract_allocation_v7/verification.json` (296 bytes)
- `data/synthetic_v1/raw_outputs/v1_weights.jsonl` is the canonical copy of that filename: its glosses match what the readers actually received (197/197 against the recovered prompts). `data/synthetic_v1/inputs/v1_weights.jsonl` is an earlier weights run and is kept only for provenance. Both the offline checks script and this note follow the author's 2026-09-26 correction; reading the `inputs/` copy is what produced the withdrawn leakage numbers.
- `analysis/offline_checks/embed_term_sims.py` is the runnable entry point, taken from the author's current programs folder. `embed_term_sims_legacy_hardcoded_input.py` is the copy shipped in the 2026-09-26 offline-checks package; it hard-codes an input filename this package does not contain.
- `analysis/paper_audit/rebuild_tables_figures.py` is byte-identical to the copy in the author's paper-build programs folder, so there is no ambiguity for that filename.

`analysis_results/` is the set of outputs as shipped in release_20260923. A fresh
`reproduce.py` run writes to `analysis/results/`. Both are kept so that a reader can
compare, and `analysis/results/` is excluded from `MANIFEST.json` because it is generated.

## What is excluded and why

- A/01_programs/ (meta, paper_build, evidence_merge, question_quality, rag_resolution, two_signal_recompute, v4_analysis, human_rule_preparation) — bundle-assembly and superseded analysis helpers; paper_build is a byte-identical duplicate of analysis/paper_audit
- A/01_programs/final_offline_checks/offline_checks_20260926.py — byte-identical duplicate of the copy shipped from input D
- A/01_programs/prior_offline_check_correction/ — older duplicate of the offline-checks scripts
- A/02_data/90_sealed_historical_answers_open_only_after_17_plus_10/ (outside released_reproduction/) — per-item historical answers kept sealed during the human review, retained in the authors' internal archive
- A/02_data/current_paper_numbers/, final_offline_checks/, early_independent_B_pilot_aggregate/ — internal working copies, superseded by analysis/offline_checks and input B
- A/02_data/derived_checks/ (except audit/t2_sample_ids.jsonl) — internal derived checks, superseded by analysis/offline_checks
- A/02_data/gitlab_pilot/source_policy_pages/approvals.txt — GitLab raw web mirror (URL manifest retained)
- A/02_data/gitlab_pilot/source_policy_pages/external.txt — GitLab raw web mirror (URL manifest retained)
- A/02_data/gitlab_pilot/source_policy_pages/members.txt — GitLab raw web mirror (URL manifest retained)
- A/02_data/gitlab_pilot/source_policy_pages/permissions.txt — GitLab raw web mirror (URL manifest retained)
- A/02_data/gitlab_pilot/source_policy_pages/protected_branches.txt — GitLab raw web mirror (URL manifest retained)
- A/02_data/gitlab_pilot/source_policy_pages/visibility.txt — GitLab raw web mirror (URL manifest retained)
- A/02_data/historical_question_audit/Sonnet5_DeepSeek_human_priority_recheck_no_answer_key.zip — per-item review packet, superseded by the English record in data/historical_question_audit/review_27/
- A/02_data/historical_question_audit/blind_80/README_read_first.md — Chinese-language document, replaced by an English README
- A/02_data/historical_question_audit/blind_80/human_blind_review_questions_and_sources.md — Chinese-language document, replaced by an English README
- A/02_data/historical_question_audit/random_control_10_questions_no_answer_key.zip — per-item review packet, superseded by the English record in data/historical_question_audit/review_27/
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/09500889f05d138304c3269f9bac26648bce29e8cd1b2d45eec1e9b3a95aad70.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/09c4a66cfc429bcdce00bfccc0fb511775a34a21a0e9f8c295bbaa9a68ec3015.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/0bbf2eb336357dbd5677365729965b54bdd6d5e14680b4695e3da1b7834a5f3e.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/0c18a007573387b67a068b5398b96b7b392a15b240397327a4059a0d437d9c8f.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/162bb3527c71f43662b624f4437b31b0ef2d7b7d1a54440268e3331317cbc14a.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/189b9d2c5c91337b29826c30a654cf423329535914572d6021d6e2072928ff95.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/2732e97b8a56c75b80bbe7de474d7df6286f2113fc7dbe318d988fb560aff6d6.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/2a970072e2a7bce0ab30a1db8068116d1631882d631298df27857a1ee2ca8d2b.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/2e287967554e54efc0b661e2a193e69acc7701b3972c2c82bd6e6f6d5a31e0e4.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/2fe8deb9a76aa63fde98c1ef09bda7271385ad24f5565286c1f8453abe9cef6d.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/36c73eff023ff67562800139d25440b4b975abff2f6ce1975ed08e44e8cb9737.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/3781323d131929c6b7128b4970c7f640a2ecea7ca4476d42475dd0111abe0ed1.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/38f12a1f6306b443bb412a9fe65227438fd6544f7552df1e2d1bac0f43af8a29.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/3b07e13008205f955757a0f8a2162758fe3c7aaa323b6483c563fcf9a9ab71e8.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/41d876a626266545dd7f7609810d8d8ae9b06d02a40b6972a5130acfccf564af.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/4338e9578fd9f13ec582079fa13dc11c8de8e8750f734458a446db5104928460.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/4a22f6ac772c9b6d1ee10cfba96b2e8d42c6a869457828cbfc8c7be219e45a5d.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/4a9dff5812de7a4eecd54aa3db060541d8b8e7554896875f65dde34131ceee78.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/4d7652de1e63173693a7cab6fad8f887ff3f1eb8e0d6e0e1f28d062a583f0e33.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/53ad4b8dd3d31e87d0b838ec4e3a6398381049bf83e9576df155f15b236e7c10.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/5842e588d3e80a93ee350c7dff581da2db8dff8f08bb6bd6c34c57682e8e546b.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/5ab3420d6c3583170f129ab480f5a0f3c1a0e8806c8c85a608a38b46f134e3e7.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/5e120c4f28b94ee3eaee797d56ed8c8dcea07580f17ec6b5c256bd108ee9f992.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/5ea58ad8b59b698cef1c639337b2a078ec18534ba27d16ec3f5c083d61e03214.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/60080dce195a63bfb0d4d8efb2fdb983643b8eeb5bc0fe5190086695d464927e.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/6035234708695d37a3b653a4e40fd5c0c1034013bd2394c62b1254c287b788ca.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/65b6a3d704560782a2bb11e136fb19541955d7084d32024061e1a59cd14fdbb7.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/6744e1671eab21c95d4b327daafe7e8a01e3b1053d68852ca67a46a06a421dd8.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/67e39367cce211ad502869a5ddea7e91e0837b57a8129d092b6e5f44fc5c1509.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/715aa2d072106cd50587743094ae34d85d1d38ebd563eb303722c67129909114.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/7617122f4030e3aa9e772c79a0024b6853859a5481ffe9b3399781488b78fb5f.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/763f6e44c6c41443ba55e1c9982e7e6244272b27623a77d6ce285350c4e11fbf.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/80fedf0767ee84f5f9057e01fa72d426e0e4fe92f7a5fbc3ea539255e21068c9.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/86b4a29e6f5c1896bd531708b7412c58788a6e2db8436b0a810d28d58cf3a14d.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/974695712b839ac6c2fa8692a6baebda7567aadb8a24ad2e3a114f9b76dafa74.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/9b048912ff45c20e3d236c44676da3f21e253c370e9f3e526183bdd707456a0f.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/9bed798ded4a8e4717e628a5e16b33af89374c57ad3f8dfa359b064144ff4da1.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/9bfe4219e629cc2270294cea36e58b2fbfd609555026fe7978efc08482d72ab4.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/ab2a516d20590566db85b9e21fdb90ac155d3c0aa1e8bfb8610319e404d0b32c.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/b97b333e92caa39f771df669a5088330984565a667841173af1705c8b3fefb04.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/bacd99259d0c82d1666c212bf0ad94acd1498691472cab52a64ad8f45da323e4.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/bb458b43d113f61fabe592f2312719296b2e134dafcc9a8b85e04385245af8a9.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/bdef2482c2ee8a1323eb84ac8c08abf263c47f13870c9a9f40f883687a635cd0.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/c19a50937ec897526cbf5578e2bb5592aa20c20b863ec360ac5f31a70d5551b9.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/cde9f5429d93b43639c0b5aeae875ba9bfceec180e886c2597c960fb4004133d.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/d1b8d9f3b89bdf9bbb1e727882f640b63695e03c016327eef9e1cd270c951f27.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/d315958e3b0ef451ec2f95437a8fff1d5a321af441febd86daf5f922a0887042.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/d8f5c2e2ef980d1493d80129b50f5fee7672fc4c149df257bb9e04be8806a48d.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/ddde07b60a11d32d55ae0bef7b62ea4be3bcf04a57cecff8d9c43291e4208734.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/e03ce1eb97b9328256ddd7ac0531a0fdb7deef795d9957f11b9aa30be9d5cb26.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/e72908d4ef87652eeeb99d7305f76521fcb53de87c50f2321a8686ca14d41b2f.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/e8992e9a69dcb7aa63836e44f49d9399c72508e813ad1cfee2df91190c557482.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/ef581ca963f0245df0259ed2a75d1416454929a37ef79f61b41460ad105d928c.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/f338405ce9bb926e640a739106e1b0ee70fea923b39a19433fb31929625b8dae.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/f64b29f364e073d49851a5ff69c64012042e84a7e9bd118a322f11562c18ee71.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/f9a2290da023f201802fb8fe847621e50ba463137ca1cd46197dbb833be73c57.json — provider response cache
- A/02_data/independent_B_v4/evaluation/_work/draft_cache/fdff7e7fbc032ba774d06edc4dd6f8b45fe4799f482e18b818bd1b7e587b19ca.json — provider response cache
- A/02_data/public_corpus_preflight/section_catalog.jsonl — MultiDoc2Dial raw section text mirror (preflight reports retained)
- A/03_analysis/ (current_manuscript, paper_audits, reports, user_recalculation) — Chinese working documents and paper drafts; internal only
- A/03_analysis/literature/ — user-downloaded literature PDFs and Scholar .bib
- B/README.md — Chinese-language document
- B/README_DEFINITION_AUDIT.md — Chinese-language document
- B/README_SHARED_BUDGET.md — Chinese-language document
- B/paper.tex, appendix*.tex, section*.tex, table*.tex, tables*.tex, references.bib, paper.pdf, *.sty, *.bst, figs/ — paper source v10: the paper/ folder is left for the lead to fill
- B/tmp/, B/__pycache__/, B/*.aux|log|fls|fdb_latexmk — LaTeX build artefacts and scratch output
- C/pd-reproduction/ (whole archive) — older public archive superseded by the 2026-09-23 release in bundle A; its DATA_CARD provenance wording is quoted in README.md
- D/NUMBERS_FOR_PAPER.md — Chinese-language document, superseded by the English analysis/offline_checks/README.md
- D/README.md — Chinese-language document, superseded by the English analysis/offline_checks/README.md
- D/reports/PAPER_V3_CONTROL_ARMS.md — Chinese-language report, replaced by an English summary in analysis/offline_checks/README.md
- D/reports/REVIEWER_CHECKS_5.md — Chinese-language report, replaced by an English summary in analysis/offline_checks/README.md
- D/reports/SHARED_BUDGET_SIMULATION.md — Chinese-language report, replaced by an English summary in analysis/offline_checks/README.md
- D/reports/TERM_MEANING_DIFFERENCE.md — Chinese-language report, replaced by an English summary in analysis/offline_checks/README.md
- E/PD_release_2026-09-22/ (whole bundle) — older internal project bundle; internal package only
- data/development/boundary_development_v5/formal_frame/final_review/review_batches/README.md — Chinese README; documentation in the public package is English only. Where it documented a data folder, the adjacent manifest.json carries the same metadata
- programs/development/boundary_development_v5/approve_B.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v5/audit_lexical_overlap.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v5/generate_dev.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v5/make_B_review_sample.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v5/make_rule_review_batches.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v5/parse_rule_reviews.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v5/sample_historical_A_audit.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v6/analyze_pilot.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v6/build_seeds.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/boundary_development_v6/freeze_pilot.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/contract_allocation_v7/analyze.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/contract_allocation_v7/make_review_packet.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/contract_allocation_v7/postrun_audit.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/contract_allocation_v7/prepare.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/corpus_budget_preflight/lock_sample_size.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/corpus_budget_preflight/preview_reddit_definition_budget.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/corpus_budget_preflight/write_audit_report.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/independent_B_v4/README_advanced.md — Chinese README; documentation in the public package is English only. Where it documented a data folder, the adjacent manifest.json carries the same metadata
- programs/development/independent_B_v4/localrisk/analysis.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/independent_B_v4/localrisk/easy.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/independent_B_v4/localrisk/mechanism.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/independent_B_v4/localrisk/prepare.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/v7_review/record_review.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/development/v7_review/replay_online_costs.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/historical_source_audit/analyze_targeted_review.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/historical_source_audit/build_claude_package.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/historical_source_audit/build_random_controls.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/historical_source_audit/cross_screen_sonnet5.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/historical_source_audit/make_blind_audit.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/historical_source_audit/triage_model_stage.py — Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package
- programs/shared_library_runner/README_run.md — Chinese README; documentation in the public package is English only. Where it documented a data folder, the adjacent manifest.json carries the same metadata
- Source paths that are Chinese-named in the author's bundle are referred to above by an English label. The label-to-original mapping lives in the builder script and in the internal context package.
- 10 files dropped by the secret scan (all of them carried a private-range provider endpoint; no API key, token or private key was found anywhere in the inputs) — listed in PACKAGING_REPORT.md

## Non-English data files

The public package carries no Chinese in any code, comment, documentation or manifest.
Corpus text in other languages is data and is kept unchanged. Files containing
non-English corpus text:

- `data/cuad/inputs/occurrences.jsonl`
- `data/cuad/inputs/terms_full.jsonl`
- `data/development/boundary_development_v5/dev_pilot/budget_plan.json`
- `data/development/boundary_development_v5/dev_pilot/manifest.json`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_01.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_02.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_03.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_04.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_05.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_06.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_07.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_08.md`
- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_09.md`
- `data/development/boundary_development_v5/formal_frame/frame_manifest.json`
- `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_01.md`
- `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_02.md`
- `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_03.md`
- `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_04.md`
- `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_05.md`
- `data/development/boundary_development_v5/formal_frame/review_packets_base/batch_06.md`
- `data/development/boundary_development_v6/freeze_manifest.json`
- `data/development/corpus_budget_preflight/execution_status.json`
- `data/development/corpus_budget_preflight/reddit_glossary_candidates_provisional.jsonl`
- `data/development/independent_B_v4/_study/input_terms.jsonl`
- `data/development/independent_B_v4/evaluation/analysis/report.md`
- `data/development/independent_B_v4/evaluation/mechanism/report.md`
- `data/development/independent_B_v4/evaluation/report.md`
- `data/development/v7_review/human_rule_review.json`
- `data/historical_question_audit/blind_80/sources/cuad_full_contracts/4b26012ee988_0.26_8473102_EX-10.26_Content_License_Agreement1.txt`
- `data/shared_library/execution_status.json`
- `data/structural_twin/inputs/MIRROR_SPEC.json`
- `data/structural_twin/inputs/mirror_corpus.jsonl`
- `data/structural_twin/inputs/mirror_glossary.csv`
- `data/structural_twin/inputs/mirror_terms.jsonl`
- `data/structural_twin/raw_outputs/mirror_eqa_gold.jsonl`
- `data/structural_twin/raw_outputs/mirror_selfreport.jsonl`
- `data/structural_twin/raw_outputs/mirror_weights.jsonl`
- `data/synthetic_v1/analysis/glossary_layering_sheet.csv`
- `data/synthetic_v1/inputs/base_v1.jsonl`
- `data/techqa/inputs/techqa_terms.jsonl`
- `provenance/rag_source/data/cuad_full/terms_full.jsonl`

Three code files outside `data/` also contain Chinese, as a deliberate and documented
exception. Their Chinese strings are the experimental record, not commentary:
`analysis/resolve_rag.py` parses the system prompt out of
`provenance/rag_source/rag_harness.py` and records the SHA-256 of
`provenance/rag_source/pdwlib/llm.py`, so both must stay byte-exact or the RAG linkage
step cannot run; and `scripts/gen_mirror.py` holds the prompts that generated the Chinese
structural-twin corpus that ships under `data/structural_twin/`. Translating any of them
would change what the experiment did.

- `provenance/rag_source/pdwlib/llm.py`
- `provenance/rag_source/rag_harness.py`
- `scripts/gen_mirror.py`

## Anonymisation

This package is prepared for double-blind review. Several result and provenance files
record the absolute path of the input they were computed from. In this package the
user-home prefix of those paths is replaced by the placeholder `<local>`, so a recorded
path reads `<local>/Documents/.../data/synthetic_v1/raw_outputs/lpmc_v1.jsonl`. Only the
path prefix was replaced. No numeric value, answer field, identifier or recorded SHA-256
was touched, the redacted files still parse, and all checks were re-run after redaction
with identical results. The files affected are listed in `PACKAGING_REPORT.md`.

## Licensing

Code (`scripts/`, `pdwlib/`, `analysis/`, `programs/`, `reproduce.py`): MIT License.
Copyright (c) 2026 the authors. Data and documents created by the authors: Creative
Commons Attribution 4.0 (CC BY 4.0). Third-party material retains its own licence, and
model outputs are subject to each provider's terms of use. Per-corpus provenance, quoted
from the project's data card:

- **CUAD** (Hendrycks et al., 2021), CC BY 4.0. We add definition-clause extraction,
  drafted questions, proxy scores and reader labels. Contract identifiers are the
  dataset's own filenames.
- **Reddit**: glossary entries from the community-glossary release of Lucy & Bamman
  (2021); comments from a public archive of the same communities. Usernames are not
  included; only sentence-level comment text needed for a question is stored.
- **Post-cutoff DeFi**: Uniswap protocol documentation, files created after May 2026 by
  repository history (open-source licence of the repository applies). Commit dates
  recorded per term.
- **Synthetic collection**: generated by Claude Sonnet 5 from hand-written
  specifications; fully released.
- **Structural twin**: generated from the private notebook's distributional parameters
  only; released as a format illustration, not as evidence.

ICLR style files, where a paper build adds them, keep their own terms. The private
operations notebook is not part of this release.

## Human source review (17 targeted + 10 control items)

An author answered 27 diagnostic questions from their source cards before seeing the stored
keys: 17 on which two screening models disagreed and 10 stratified controls. After
reconciliation with the sources, 10 stored keys are supported, 14 questions are invalid or not
answerable from the preserved source, and 3 are borderline. The sample is enriched for
disagreement, so these counts are not defect rates. The record is in
`data/historical_question_audit/review_27/`. The deletion sensitivity reported in the paper
recomputes from the released data with

```sh
python analysis/reviewer_controls/review27_deletion_check.py --root . \
    --out analysis/reviewer_controls/review27_deletion_results.json
```

Removing the 14 invalid items changes the error-ranking AUROC of R by at most 0.002 across the
eight reader settings, and the CUAD design-weighted AUROC from 0.8456 to 0.8467. No stored key
is changed. The model screen in `data/historical_question_audit/blind_80/` is a triage list,
not adjudicated key errors.

## Status

`RELEASE_STATUS.json` records what is complete. The development experiments on independently
written questions and request budgets (`data/development/`) are released for inspection. The
paper makes no completed-result claim that depends on them.
