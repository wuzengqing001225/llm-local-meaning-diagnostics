# Reviewer controls (2026-09-26)

Offline analyses added in response to reviewer-style questions. No reader-model calls.

Files
- `proxy_option_dist.py`: scores the full option distribution of Qwen2.5-7B on the 457 synthetic diagnostic questions without a definition, using the prompt and letter scoring of `scripts/run_logprob_mc.py`. It is the only step that runs a model (local, CPU is sufficient).
- `ids.json`: the synthetic term identifiers scored.
- `qwen7b_option_dist.jsonl`: its output (one row per question with all four option probabilities). Stored p_correct is reproduced to within 0.005.
- `reviewer_controls_20260926.py`: computes every number below from released data plus the option-distribution file.
- `reviewer_controls_results.json`: the output.

Run from the package root:
    python3 analysis/reviewer_controls/reviewer_controls_20260926.py --root . \
        --option-dist analysis/reviewer_controls/qwen7b_option_dist.jsonl \
        --out analysis/reviewer_controls/reviewer_controls_results.json

Contents of the output
- Stability of DeepSeek V4 Flash synthetic errors by designed term class (761 questions): identical wrong answer in all ten samples, all ten samples correct, majority wrong.
- Error-detection AUROC with term-resampled 95% intervals by term class (456 questions) for key-free reader signals (sample disagreement, option entropy, stated confidence), key-free proxy uncertainty (one minus largest option probability, option entropy), and the keyed proxy score R.
- Four definition arms on synthetic questions (none, source definition, model-drafted gloss, model's own gloss under a domain prompt), on all 761 questions and on the 180 questions where no option is singled out by word overlap with any of the three texts.
- Jev confidence against its own errors on the 761-question frame.
- Share of CUAD retrieval questions whose retrieved passages contain the definition, by retriever.
- Percentile of the Territory example in the 6,529-question CUAD risk frame.
- Error nesting: share of GPT-6-astra errors also made by an older reader on questions answered by all readers of a corpus.
- Inverse Scaling redefine task: rate of following a stated redefinition, and of answering by the usual meaning when the redefinition is removed.
- Outcomes and risk percentiles of the contract examples shown in the paper.
