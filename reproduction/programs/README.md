# Programs for the added datasets

Each folder holds the programs that produced the matching dataset:

| Folder | Dataset |
|---|---|
| `development/independent_B_v4/` | `data/development/independent_B_v4/` |
| `development/boundary_development_v5/` | `data/development/boundary_development_v5/` |
| `development/boundary_development_v6/` | `data/development/boundary_development_v6/` |
| `development/contract_allocation_v7/` | `data/development/contract_allocation_v7/` |
| `development/v7_review/` | `data/development/v7_review/` |
| `development/corpus_budget_preflight/` | `data/development/corpus_budget_preflight/` |
| `development/public_corpus_preflight/` | `data/development/public_corpus_preflight/` |
| `development/gitlab_pilot/` | `data/development/gitlab_pilot/` |
| `development/gitlab_membership_pilot/` | `data/development/gitlab_membership_pilot/` |
| `shared_library/` | `data/shared_library/` |
| `shared_library_runner/` | standalone runner for the shared-library study |
| `historical_source_audit/` | `data/historical_question_audit/` |

These programs are the historical implementations. Re-running them needs provider
credentials and reaches a reader model, so they are here to explain how each dataset was
produced, not as an offline entry point. The offline entry points are `reproduce.py` and
`analysis/offline_checks/offline_checks_20260926.py`.

**Incomplete by design.** Some program files are not shipped here. Their Chinese strings
are working parts of the experiment rather than commentary: model prompts, the templates
that generated the Chinese review packets, and regular expressions that parse the Chinese
review forms. Translating them would change what the experiment did, and two of them also
embedded an author-local filesystem path. Every omitted file is listed with its reason in
`PACKAGING_REPORT.md`, and all of them are present verbatim in the internal context
package. The datasets they produced are complete and unmodified.
