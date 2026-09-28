# PACKAGING REPORT

Merge of the author's 2026-09-26 inputs into two packages, built by `build_packages.py`. Data bytes were copied verbatim or the file was dropped; the only in-place edit is the path-prefix anonymisation recorded below. No data value was altered and no script was changed.

## Packages

| Package | Files | Manifest entries | Purpose |
|---|---|---|---|
| `pd-reproduction-v2` | 808 | 821 | public reproduction package, GitHub-intended, English only |

## Files added, by area

| Area | Files | Source |
|---|---|---|
| `(root)` | 10 | release metadata, licences, new README, VERIFICATION, MANIFEST |
| `analysis` | 6 | A, 01_programs/reproduction/analysis |
| `analysis/offline_checks` | 7 | D, plus the runnable embedding script from A |
| `analysis/paper_audit` | 14 | B |
| `analysis_results` | 9 | A, release_20260923 shipped outputs |
| `audit` | 13 | A, release audit plus t2_sample_ids.jsonl from 02_data/derived_checks |
| `data (release corpora)` | 115 | A, release_20260923 data half |
| `data/development` | 257 | A, 02_data development experiments |
| `data/historical_question_audit` | 162 | A, 02_data/historical_question_audit (restricted subset) |
| `data/shared_library` | 31 | A, 02_data/shared_library |
| `pdwlib` | 4 | A, 01_programs/reproduction/pdwlib |
| `programs` | 124 | A, 01_programs |
| `provenance` | 17 | A, release_20260923 provenance |
| `scripts` | 39 | A, 01_programs/reproduction/scripts |

## Files and areas excluded, with reason

**Chinese README; documentation in the public package is English only. Where it documented a data folder, the adjacent manifest.json carries the same metadata** (3)

- `data/development/boundary_development_v5/formal_frame/final_review/review_batches/README.md`
- `programs/development/independent_B_v4/README_advanced.md`
- `programs/shared_library_runner/README_run.md`

**Chinese prompt, review-packet or parsing strings that cannot be translated without altering the experimental record; verbatim in the internal package** (29)

- `programs/development/boundary_development_v5/` — 7 files
- `programs/development/boundary_development_v6/` — 3 files
- `programs/development/contract_allocation_v7/` — 4 files
- `programs/development/corpus_budget_preflight/` — 3 files
- `programs/development/independent_B_v4/localrisk/` — 4 files
- `programs/development/v7_review/` — 2 files
- `programs/historical_source_audit/` — 6 files

  Individually listed in `build_report.json`.

**Chinese working documents and paper drafts; internal only** (1)

- `A/03_analysis/ (current_manuscript, paper_audits, reports, user_recalculation)`

**Chinese-language document** (3)

- `B/README.md`
- `B/README_DEFINITION_AUDIT.md`
- `B/README_SHARED_BUDGET.md`

**Chinese-language document, replaced by an English README** (2)

- `A/02_data/historical_question_audit/blind_80/README_read_first.md`
- `A/02_data/historical_question_audit/blind_80/human_blind_review_questions_and_sources.md`

**Chinese-language document, superseded by the English analysis/offline_checks/README.md** (2)

- `D/NUMBERS_FOR_PAPER.md`
- `D/README.md`

**Chinese-language report, replaced by an English summary in analysis/offline_checks/README.md** (4)

- `D/reports/PAPER_V3_CONTROL_ARMS.md`
- `D/reports/REVIEWER_CHECKS_5.md`
- `D/reports/SHARED_BUDGET_SIMULATION.md`
- `D/reports/TERM_MEANING_DIFFERENCE.md`

**GitLab raw web mirror (URL manifest retained)** (6)

- `A/02_data/gitlab_pilot/source_policy_pages/approvals.txt`
- `A/02_data/gitlab_pilot/source_policy_pages/external.txt`
- `A/02_data/gitlab_pilot/source_policy_pages/members.txt`
- `A/02_data/gitlab_pilot/source_policy_pages/permissions.txt`
- `A/02_data/gitlab_pilot/source_policy_pages/protected_branches.txt`
- `A/02_data/gitlab_pilot/source_policy_pages/visibility.txt`

**LaTeX build artefacts and scratch output** (1)

- `B/tmp/, B/__pycache__/, B/*.aux|log|fls|fdb_latexmk`

**MultiDoc2Dial raw section text mirror (preflight reports retained)** (1)

- `A/02_data/public_corpus_preflight/section_catalog.jsonl`

**bundle-assembly and superseded analysis helpers; paper_build is a byte-identical duplicate of analysis/paper_audit** (1)

- `A/01_programs/ (meta, paper_build, evidence_merge, question_quality, rag_resolution, two_signal_recompute, v4_analysis, human_rule_preparation)`

**byte-identical duplicate of the copy shipped from input D** (1)

- `A/01_programs/final_offline_checks/offline_checks_20260926.py`

**internal derived checks, superseded by analysis/offline_checks** (1)

- `A/02_data/derived_checks/ (except audit/t2_sample_ids.jsonl)`

**internal working copies, superseded by analysis/offline_checks and input B** (1)

- `A/02_data/current_paper_numbers/, final_offline_checks/, early_independent_B_pilot_aggregate/`

**older duplicate of the offline-checks scripts** (1)

- `A/01_programs/prior_offline_check_correction/`

**older internal project bundle; internal package only** (1)

- `E/PD_release_2026-09-22/ (whole bundle)`

**older public archive superseded by the 2026-09-23 release in bundle A; its DATA_CARD provenance wording is quoted in README.md** (1)

- `C/pd-reproduction/ (whole archive)`

**paper source v10: the paper/ folder is left for the lead to fill** (1)

- `B/paper.tex, appendix*.tex, section*.tex, table*.tex, tables*.tex, references.bib, paper.pdf, *.sty, *.bst, figs/`

**per-item packet for the 17 targeted + 10 control human review (in progress)** (2)

- `A/02_data/historical_question_audit/Sonnet5_DeepSeek_human_priority_recheck_no_answer_key.zip`
- `A/02_data/historical_question_audit/random_control_10_questions_no_answer_key.zip`

**provider response cache** (57)

- `A/02_data/independent_B_v4/evaluation/_work/draft_cache/` — 57 files

  Individually listed in `build_report.json`.

**sealed historical per-item answers and answer keys** (1)

- `A/02_data/90_sealed_historical_answers_open_only_after_17_plus_10/ (outside released_reproduction/)`

**user-downloaded literature PDFs and Scholar .bib** (1)

- `A/03_analysis/literature/`

## Secret scan

Patterns searched in every text file staged for the public package: `api_key` / `apikey` / `access_token` / `auth_token` / `secret_key` / `password` assigned a literal, an OpenAI-style `sk-` key, a `Bearer` literal, a PEM private key block, a URL with a bare IP address, `base_url` pointing at an IP, and RFC1918 `172.x` addresses.

**No API key, bearer token, password or private key was found anywhere in the inputs.** Every hit was one and the same private-range (RFC1918) address, recorded as the `base_url` of a local inference server. The address itself is not reproduced anywhere in this report or in the public package. To read it, open any of the dropped files listed below in the internal context package, where they are kept unredacted, for example `02_author_bundle_2026-09-26/02_data/independent_B_v4/_study/protocol.json`. `build_report.json` records only the path and the pattern name for each drop, not the matched text. Those files were dropped as instructed:

| File | Pattern |
|---|---|
| `data/development/boundary_development_v5/dev_pilot/reader_predictions.jsonl` | url_with_bare_ip,rfc1918_172_2_address |
| `data/development/contract_allocation_v7/config.example.json` | url_with_bare_ip,base_url_with_ip,rfc1918_172_2_address |
| `data/development/independent_B_v4/_study/protocol.json` | url_with_bare_ip,base_url_with_ip,rfc1918_172_2_address |
| `data/development/independent_B_v4/evaluation/_work/mechanism_plan/manifest.json` | url_with_bare_ip,base_url_with_ip,rfc1918_172_2_address |
| `data/development/independent_B_v4/evaluation/_work/mechanism_predictions.jsonl` | url_with_bare_ip,rfc1918_172_2_address |
| `data/development/independent_B_v4/evaluation/_work/plan/manifest.json` | url_with_bare_ip,base_url_with_ip,rfc1918_172_2_address |
| `data/development/independent_B_v4/evaluation/_work/predictions.jsonl` | url_with_bare_ip,rfc1918_172_2_address |
| `data/development/independent_B_v4/evaluation/_work/run_state.json` | url_with_bare_ip,base_url_with_ip,rfc1918_172_2_address |
| `programs/development/independent_B_v4/README.md` | url_with_bare_ip,rfc1918_172_2_address |
| `programs/development/independent_B_v4/tests/test_easy.py` | url_with_bare_ip,rfc1918_172_2_address |

These files carry no credential: the endpoint is an unroutable LAN address. If the author wants the `independent_B_v4` predictions in the public package, the `base_url` field can be removed and the files re-added; that is an edit to data and was not made here.

## Reported, not dropped: author-local paths

12 staged files recorded an absolute path of the machine the result was computed on. A filesystem path is not a credential and is not on the secret list this package was built against, and several of these files are required results — `rebuild_tables_figures.py` reads `interest_sensitivity.json`. They were kept and the user-home prefix was replaced with `<local>` (see the next section).

- `analysis/paper_audit/audit/gold_repair_auc.json`
- `analysis/paper_audit/interest_sensitivity.json`
- `data/development/boundary_development_v5/dev_pilot/manifest.json`
- `data/development/corpus_budget_preflight/interest_sensitivity.json`
- `data/development/corpus_budget_preflight/reddit_glossary_candidates_provisional.jsonl`
- `data/development/v7_review/legacy_synthetic_terms_source_consistency_pending.json`
- `data/shared_library/gold_aligned_development/analysis.json`
- `data/shared_library/gold_aligned_development/gold_repair_auc.json`
- `data/shared_library/simulation_audit.json`
- `programs/development/corpus_budget_preflight/preview_reddit_definition_budget.py` — dropped from the public package for another reason above
- `programs/historical_source_audit/make_blind_audit.py` — dropped from the public package for another reason above
- `programs/shared_library_runner/README_run.md` — dropped from the public package for another reason above

## Anonymisation for double-blind review (public package only)

Absolute user-home path prefixes were replaced with the placeholder `<local>` in the public package, so a recorded input path reads `<local>/Documents/.../data/synthetic_v1/raw_outputs/lpmc_v1.jsonl`. Only the path prefix was substituted. No numeric value, answer field, identifier or recorded SHA-256 was touched; every redacted JSON and JSONL file was re-parsed after the substitution. The internal package is left unredacted.

The redaction pattern is anchored so it cannot match inside a URL: TechQA corpus text contains `https://support...ibm.com/support/home/product/...`, which is unchanged, and `data/techqa/inputs/techqa_terms.jsonl` is byte-identical to the author's release.

| File | Replacements |
|---|---|
| `analysis/paper_audit/audit/gold_repair_auc.json` | 4 |
| `analysis/paper_audit/interest_sensitivity.json` | 8 |
| `data/development/boundary_development_v5/dev_pilot/manifest.json` | 1 |
| `data/development/corpus_budget_preflight/interest_sensitivity.json` | 8 |
| `data/development/corpus_budget_preflight/reddit_glossary_candidates_provisional.jsonl` | 3380 |
| `data/development/v7_review/legacy_synthetic_terms_source_consistency_pending.json` | 1 |
| `data/shared_library/gold_aligned_development/analysis.json` | 4 |
| `data/shared_library/gold_aligned_development/gold_repair_auc.json` | 4 |
| `data/shared_library/simulation_audit.json` | 8 |

All three checks were re-run after redaction. `reproduce.py` passes, the offline checks output is identical to the results the author shipped, and `rebuild_tables_figures.py` regenerates its tables and figure.

## Duplicate filenames with different bytes

40 filenames occur more than once in the public package with differing content. Most are per-experiment files that share a conventional name (`analysis.json`, `manifest.json`, `tasks_public.jsonl`) and are unambiguous from their directory. The cases that matter for reading the results:

- **`v1_weights.jsonl`** — the case the author flagged on 2026-09-26. Two copies: `data/synthetic_v1/inputs/v1_weights.jsonl` (414,247 bytes) and `data/synthetic_v1/raw_outputs/v1_weights.jsonl` (446,209 bytes). **The `raw_outputs/` copy is canonical**: its glosses match what the readers actually received, 197/197 against the recovered prompts. The `inputs/` copy is an earlier weights run. Reading the `inputs/` copy is what produced the withdrawn leakage numbers, and `offline_checks_20260926.py` prefers `raw_outputs/` by name. Both are kept, for provenance.
- **`embed_term_sims.py`** — two variants exist across the inputs. The one shipped as `analysis/offline_checks/embed_term_sims.py` is the author's current version (1,339 bytes), which takes `--input`/`--out` and defaults to the term-texts file this package ships. Input D's copy (885 bytes) hard-codes `term_texts.json`, a filename this package does not contain, so it cannot run as shipped; it is kept verbatim beside it as `embed_term_sims_legacy_hardcoded_input.py`.
- **`verification.json`** — three unrelated files: the paper audit's (`analysis/paper_audit/verification.json`), the recovered-response check's (`analysis_results/recovered/verification.json`), and one development experiment's (`data/development/contract_allocation_v7/verification.json`). Not versions of each other.
- **`resolution.json`** — `analysis_results/resolution.json` (2,586 bytes) is the shipped output of the RAG linkage step; `provenance/resolution.json` (2,587 bytes) is the provenance copy. A fresh run writes `analysis/results/resolution.json`.
- **`rag_harness.py`, `llm.py`** — the copies under `provenance/rag_source/` are frozen snapshots of the code as it ran, and `analysis/resolve_rag.py` parses and hashes them byte-exactly. The copies under `scripts/` and `pdwlib/` are the current implementations. They must not be reconciled.

Full list:

| Filename | Copies |
|---|---|
| `B_candidates_private.jsonl` | `data/development/gitlab_membership_pilot/B_candidates_private.jsonl` (20808 B, sha256 d0f2c8a746…)<br>`data/development/gitlab_pilot/B_candidates_private.jsonl` (15972 B, sha256 16852a3ac5…) |
| `B_checks.jsonl` | `data/development/contract_allocation_v7/B_checks.jsonl` (71393 B, sha256 d9f28fe10f…)<br>`data/development/gitlab_pilot/B_checks.jsonl` (10030 B, sha256 c28c30314a…) |
| `B_drafts.jsonl` | `data/development/contract_allocation_v7/B_drafts.jsonl` (214149 B, sha256 670ac8679a…)<br>`data/development/gitlab_membership_pilot/B_drafts.jsonl` (39546 B, sha256 a20b63ab40…)<br>`data/development/gitlab_pilot/B_drafts.jsonl` (27201 B, sha256 e8b6a3edb0…) |
| `__init__.py` | `pdwlib/__init__.py` (114 B, sha256 a9eb18ca28…)<br>`programs/development/independent_B_v4/localrisk/__init__.py` (97 B, sha256 1f987d687b…) |
| `analysis.json` | `data/development/boundary_development_v5/dev_pilot/analysis.json` (19718 B, sha256 41de8e9e5e…)<br>`data/development/boundary_development_v6/analysis.json` (15101 B, sha256 17412697cc…)<br>`data/development/contract_allocation_v7/analysis.json` (11869 B, sha256 4729904baa…)<br>`data/shared_library/gold_aligned_development/analysis.json` (105859 B, sha256 03edf5ae41…) |
| `api_client.py` | `programs/shared_library/api_client.py` (3194 B, sha256 0855f02d43…)<br>`programs/shared_library_runner/api_client.py` (3265 B, sha256 0df332632f…) |
| `batch_01.md` | `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_01.md` (32009 B, sha256 89ee0dfc43…)<br>`data/development/boundary_development_v5/formal_frame/review_packets_base/batch_01.md` (42894 B, sha256 31d85a8119…) |
| `batch_02.md` | `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_02.md` (33011 B, sha256 0777a6b28c…)<br>`data/development/boundary_development_v5/formal_frame/review_packets_base/batch_02.md` (48701 B, sha256 e9a7467f8b…) |
| `batch_03.md` | `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_03.md` (38718 B, sha256 eb5d9e9e6a…)<br>`data/development/boundary_development_v5/formal_frame/review_packets_base/batch_03.md` (57371 B, sha256 37c4ca0c04…) |
| `batch_04.md` | `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_04.md` (43450 B, sha256 67a1dd605d…)<br>`data/development/boundary_development_v5/formal_frame/review_packets_base/batch_04.md` (63762 B, sha256 dd39009cbd…) |
| `batch_05.md` | `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_05.md` (48204 B, sha256 e974044cfe…)<br>`data/development/boundary_development_v5/formal_frame/review_packets_base/batch_05.md` (53575 B, sha256 346ad3d026…) |
| `batch_06.md` | `data/development/boundary_development_v5/formal_frame/final_review/review_batches/batch_06.md` (43666 B, sha256 aa3ac18656…)<br>`data/development/boundary_development_v5/formal_frame/review_packets_base/batch_06.md` (3355 B, sha256 8b23327860…) |
| `common.py` | `programs/development/contract_allocation_v7/common.py` (2301 B, sha256 8d61abd47a…)<br>`programs/development/independent_B_v4/localrisk/common.py` (4160 B, sha256 b253ff6826…) |
| `diagnostics_A.jsonl` | `data/development/boundary_development_v5/dev_pilot/diagnostics_A.jsonl` (19579 B, sha256 eff0872baa…)<br>`data/development/contract_allocation_v7/diagnostics_A.jsonl` (85981 B, sha256 52ef610ec7…)<br>`data/development/independent_B_v4/_study/diagnostics_A.jsonl` (4174372 B, sha256 5989a7a73e…)<br>`data/development/independent_B_v4/evaluation/_work/diagnostics_A.jsonl` (4174372 B, sha256 5989a7a73e…) |
| `execution_status.json` | `data/development/corpus_budget_preflight/execution_status.json` (4808 B, sha256 34e4397c6f…)<br>`data/shared_library/execution_status.json` (4117 B, sha256 ee70abaf7e…) |
| `llm.py` | `pdwlib/llm.py` (13026 B, sha256 bb530cbec7…)<br>`provenance/rag_source/pdwlib/llm.py` (13963 B, sha256 be6b7dfbef…) |
| `manifest.json` | `data/development/boundary_development_v5/dev_pilot/manifest.json` (744 B, sha256 4b8246a54b…)<br>`data/development/boundary_development_v5/formal_frame/final_review/review_batches/manifest.json` (8401 B, sha256 688512c440…)<br>`data/development/boundary_development_v5/formal_frame/review_packets_base/manifest.json` (6670 B, sha256 0def8533f9…)<br>`data/development/boundary_development_v6/seed_frame/manifest.json` (620 B, sha256 57cf32cb2d…)<br>`data/development/gitlab_pilot/source_policy_pages/manifest.json` (1231 B, sha256 667c181d07…)<br>`data/development/independent_B_v4/evaluation/_work/snapshot/manifest.json` (694 B, sha256 e5c3635bb4…)<br>`data/development/independent_B_v4/evaluation/_work/tasks/manifest.json` (621 B, sha256 edf6484603…)<br>`data/historical_question_audit/blind_80/manifest.json` (2179 B, sha256 78584b4b9b…)<br>`data/shared_library/gold_aligned_development/manifest.json` (517 B, sha256 72d023f389…) |
| `plan_budget.py` | `programs/development/boundary_development_v5/plan_budget.py` (5454 B, sha256 93f0b8fcfe…)<br>`programs/development/contract_allocation_v7/plan_budget.py` (2888 B, sha256 62176b7594…) |
| `plan_summary.json` | `data/development/independent_B_v4/evaluation/_work/mechanism_plan/plan_summary.json` (391 B, sha256 e752b15310…)<br>`data/development/independent_B_v4/evaluation/_work/plan/plan_summary.json` (703 B, sha256 779077e930…) |
| `rag_harness.py` | `provenance/rag_source/rag_harness.py` (13728 B, sha256 70739ad4d0…)<br>`scripts/rag_harness.py` (14097 B, sha256 36d444c93f…) |
| `reader_results.jsonl` | `data/development/boundary_development_v6/reader_results.jsonl` (94387 B, sha256 1e04a90d10…)<br>`data/development/contract_allocation_v7/reader_results.jsonl` (329443 B, sha256 25943f844c…) |
| `report.md` | `data/development/independent_B_v4/evaluation/analysis/report.md` (11227 B, sha256 5464d37e9b…)<br>`data/development/independent_B_v4/evaluation/mechanism/report.md` (1176 B, sha256 653545f0aa…)<br>`data/development/independent_B_v4/evaluation/report.md` (11342 B, sha256 d7ab309e82…) |
| `requests.jsonl` | `data/development/independent_B_v4/evaluation/_work/mechanism_plan/requests.jsonl` (207365 B, sha256 e361a52890…)<br>`data/development/independent_B_v4/evaluation/_work/plan/requests.jsonl` (699282 B, sha256 4d7c2838b8…) |
| `requirements.txt` | `programs/development/independent_B_v4/requirements.txt` (134 B, sha256 fb39463d77…)<br>`requirements.txt` (49 B, sha256 4ff86467ed…) |
| `resolution.json` | `analysis_results/resolution.json` (2586 B, sha256 66dab5e6d2…)<br>`provenance/resolution.json` (2587 B, sha256 0b1475f5df…) |
| `run_B_reader.py` | `programs/shared_library/run_B_reader.py` (10860 B, sha256 9bc631dc3f…)<br>`programs/shared_library_runner/run_B_reader.py` (10829 B, sha256 949b8ac941…) |
| `run_main.py` | `programs/development/contract_allocation_v7/run_main.py` (1286 B, sha256 df37d02269…)<br>`programs/development/independent_B_v4/run_main.py` (87 B, sha256 c91cf27286…)<br>`programs/shared_library_runner/run_main.py` (9314 B, sha256 2470666b0e…) |
| `run_pilot.py` | `programs/development/boundary_development_v6/run_pilot.py` (3149 B, sha256 c6e810cefe…)<br>`programs/development/gitlab_pilot/run_pilot.py` (12503 B, sha256 835e5f930e…) |
| `score_A.py` | `programs/development/boundary_development_v5/score_A.py` (6337 B, sha256 2bb92864c4…)<br>`programs/development/contract_allocation_v7/score_A.py` (3371 B, sha256 03ed6f58f2…)<br>`programs/shared_library_runner/score_A.py` (9640 B, sha256 bfe643cafa…) |
| `scored_trials.jsonl` | `data/development/independent_B_v4/evaluation/analysis/scored_trials.jsonl` (1373360 B, sha256 8e6f2bf2f4…)<br>`data/development/independent_B_v4/evaluation/mechanism/scored_trials.jsonl` (64647 B, sha256 aaa78807d2…) |
| `scores_A.jsonl` | `data/development/boundary_development_v5/dev_pilot/scores_A.jsonl` (16868 B, sha256 340bf918b9…)<br>`data/development/independent_B_v4/_study/scores_A.jsonl` (931041 B, sha256 0f2ae1dad9…)<br>`data/development/independent_B_v4/evaluation/_work/scores_A.jsonl` (931041 B, sha256 0f2ae1dad9…) |
| `source_cards.jsonl` | `data/development/contract_allocation_v7/source_cards.jsonl` (94122 B, sha256 aae9629c60…)<br>`data/development/gitlab_pilot/source_cards.jsonl` (3551 B, sha256 d2009541d1…) |
| `source_checks.jsonl` | `data/development/boundary_development_v6/source_checks.jsonl` (25558 B, sha256 01bc18e578…)<br>`data/development/contract_allocation_v7/source_checks.jsonl` (24290 B, sha256 0a920e3bac…)<br>`data/shared_library/gold_aligned_development/source_checks.jsonl` (128605 B, sha256 a58267d22c…) |
| `summary.json` | `data/development/independent_B_v4/evaluation/analysis/summary.json` (82838 B, sha256 1f18899bd9…)<br>`data/development/independent_B_v4/evaluation/mechanism/summary.json` (21974 B, sha256 cb347e2d2c…)<br>`data/development/independent_B_v4/evaluation/summary.json` (83729 B, sha256 abebce72d5…) |
| `tasks_B.jsonl` | `data/development/boundary_development_v5/dev_pilot/tasks_B.jsonl` (30920 B, sha256 1bef27d37c…)<br>`data/development/independent_B_v4/_study/tasks_B.jsonl` (298057 B, sha256 381d6ee077…)<br>`data/development/independent_B_v4/evaluation/_work/tasks_B.jsonl` (298057 B, sha256 381d6ee077…) |
| `tasks_private.jsonl` | `data/development/boundary_development_v6/tasks_private.jsonl` (14967 B, sha256 f44377981f…)<br>`data/development/contract_allocation_v7/tasks_private.jsonl` (49869 B, sha256 0a3424a119…) |
| `tasks_public.jsonl` | `data/development/boundary_development_v6/tasks_public.jsonl` (10235 B, sha256 e3bd08c168…)<br>`data/development/contract_allocation_v7/tasks_public.jsonl` (29038 B, sha256 2cc25bb68b…)<br>`data/development/independent_B_v4/evaluation/_work/tasks/tasks_public.jsonl` (50304 B, sha256 ee9dde20d3…) |
| `trials.jsonl` | `data/development/independent_B_v4/evaluation/_work/mechanism_plan/trials.jsonl` (43237 B, sha256 35f55e80d1…)<br>`data/development/independent_B_v4/evaluation/_work/plan/trials.jsonl` (1237757 B, sha256 b6c0c37c2a…) |
| `v1_weights.jsonl` | `data/synthetic_v1/inputs/v1_weights.jsonl` (414247 B, sha256 a8a744a293…)<br>`data/synthetic_v1/raw_outputs/v1_weights.jsonl` (446209 B, sha256 1ef9396281…) |
| `verification.json` | `analysis/paper_audit/verification.json` (559 B, sha256 699426c56b…)<br>`analysis_results/recovered/verification.json` (8561 B, sha256 b3f66784a5…)<br>`data/development/contract_allocation_v7/verification.json` (296 B, sha256 532355213e…) |

## Chinese filenames renamed to English

| Original | In this package |
|---|---|
| A/02_data/historical_question_audit/blind_80/answer_sheet_to_fill.csv | `data/historical_question_audit/blind_80/answer_sheet_to_fill.csv` |
| data/development/v7_review/legacy_synthetic_terms_source_consistency_pending.json | `data/development/v7_review/legacy_synthetic_terms_source_consistency_pending.json` |

File contents were not changed by the rename.

## Language of the public package

No Chinese appears in any README, manifest, or generated document, and no file has a Chinese name. 32 files whose Chinese strings are working parts of the experiment — model prompts, the templates that generated the Chinese review packets, and regular expressions that parse the Chinese review forms — were dropped rather than machine-translated, because translating them would change what the experiment did. They are listed under the exclusions above and are present verbatim in the internal package.

Three code files keep their Chinese as a documented exception, because the reproduction depends on their exact bytes or content:

- `provenance/rag_source/pdwlib/llm.py`
- `provenance/rag_source/rag_harness.py`
- `scripts/gen_mirror.py`

`analysis/resolve_rag.py` parses the system prompt out of `provenance/rag_source/rag_harness.py` and records the SHA-256 of `provenance/rag_source/pdwlib/llm.py`, so neither can be altered or removed without breaking the RAG linkage step. `scripts/gen_mirror.py` holds the prompts that generated the Chinese structural-twin corpus shipped under `data/structural_twin/`.

Two files contain a single fullwidth colon inside a regular-expression character class, `[:：]`, which accepts either colon form in model output: `scripts/run_eqa.py` and `programs/shared_library/run_configured_gold_reader_dev.py`. That is a functional token, not prose, and was left alone.

41 data files contain non-English corpus or experiment text and are kept unchanged; they are listed in the package README. The largest groups are the Chinese structural-twin corpus under `data/structural_twin/`, the Chinese rule review packets under `data/development/boundary_development_v5/formal_frame/`, and one CUAD contract that contains Chinese text.

## Verification

19 of 19 headline values reproduce exactly. See `VERIFICATION.md` in the public package for the full table.

**No mismatches.** Nothing was patched to reach that result: the checks are the author's own scripts run against the merged tree.

Script exit codes: `offline_checks_20260926.py` = 0, `rebuild_tables_figures.py` = 0, `reproduce.py` = 0, `verify_release.py` = 0 (Verified 821 release files.).

## Judgement calls

- **Two synthetic denominators, both kept.** The archived frame is 763 questions (457 in the proxy overlap); the 2026-09-26 correction excludes the two source-conflict items, giving 761 (456 in the overlap). The paper's uncertainty baselines are the corrected 456-question figures, which live in `interest_sensitivity.json`, not in `reproduce.py`'s output. Both are shipped and `VERIFICATION.md` explains which is which, rather than picking one.
- **The embedding script shipped is the author's current version, not input D's.** D's copy hard-codes an input filename this package does not contain and cannot run as shipped. D's copy is kept verbatim under a `_legacy_hardcoded_input` name so nothing is lost.
- **Development-experiment programs whose Chinese strings are functional were dropped, not translated.** Translating a model prompt or a review-form parser would alter the experimental record, and no language model was used for this packaging work. The datasets those programs produced are complete and unmodified.
- **GitLab page dumps dropped, their URL manifest kept.** `data/development/gitlab_pilot/source_policy_pages/manifest.json` retains the source URLs, byte counts and SHA-256 of each page, so a reader can re-fetch them from docs.gitlab.com; the mirrored `.txt` page bodies are not redistributed.
- **MultiDoc2Dial section text dropped, preflight reports kept.** `section_catalog.jsonl` (5.3 MB of mirrored source-document sections) is excluded; `multidoc_source_preflight.json`, `download_manifest.json` and `candidate_requests_top20.jsonl` are kept, since they are screening output rather than a corpus mirror.
- **`biz` was not treated as a private-notebook marker.** It occurs as a `.biz` domain in CUAD contract text, in `ibm.biz` URLs in the TechQA corpus, and as a corpus label in the author's own cross-corpus analysis. Matching on it would have removed unrelated corpus data. The notebook exclusion was matched on `desk notebook`, the Chinese words for "private" and "notebook", and `FINDINGS_v*_BIZ` instead, and the private notebook's text, glossary and per-item outputs are absent from both packages.
- **Aggregate-only notebook-derived numbers in the author's release were left in place.** `data/cross_corpus/analysis/crossgen_gradient.json` and `data/cuad/analysis/dep_dist.json` carry a `biz` series that aggregates over the private corpus. These are hash-verified files of the author's own release and contain no notebook text, matching the author's stated policy that only aggregate numbers leave that corpus.
- **Development programs were included for `shared_library` and `historical_source_audit` as well.** The task named nine development experiments; these two were added because their datasets are in the public package and the programs are what produced them.
- **Files named `*_private.jsonl` inside the development experiments were kept.** They hold frozen task and gold material for those studies, not personal data and not the private notebook. They are part of the experimental record the paper cites. Flagged here because the name invites a second look before publishing.
- **`analysis_results/` was kept at the release root.** It is the set of outputs the author shipped in release_20260923 and is not listed in the release manifest, so its intended location was ambiguous. Keeping the author's path preserves the bytes and lets a reader compare a fresh `analysis/results/` run against it.



## Removed on 2026-09-26

The 18 Markdown review notes under `data/development/` (the three `independent_B_v4/evaluation` reports and the `boundary_development_v5` review batches) were removed because they were written in Chinese. They documented development experiments that are not part of the paper's claims. The structured data files in those folders are unchanged. Paths to these notes listed above no longer resolve.
