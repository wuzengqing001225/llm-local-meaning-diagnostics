# Reproduction notes

This package supports *Language Models Cannot Tell When a Definition Is Missing*. The numerical reproduction uses archived question sets, proxy scores, and reader outputs. It requires no API key, model download, GPU, or network call:

```sh
python -m pip install -r requirements.txt
python verify_release.py
python reproduce.py
```

`reproduce.py` writes its results under `analysis/results/`. Paper-specific corrected analyses are in `analysis/offline_checks/` and `analysis/paper_audit/`; see `README.md` and `VERIFICATION.md` for their commands. The former 2026-09-23 raw frames are preserved for provenance. The current synthetic analysis excludes two source-conflicted questions, leaving 761 repeated-sampling questions and 456 matched proxy-reader questions. Running the baseline reproduction on the original 457 matched questions does not silently apply that later exclusion.

The 671-question CUAD definition-anchored task is separate from the 1,500-question risk-stratified validation. The 1,500-question CUAD task uses extracted contract definitions; synthetic, Reddit, and DeFi matched tasks use model-drafted source-based glosses. The source-definition arms in the intervention table are separate observations. `delta_mc`, signed probability change, and $R$ are distinct statistics.

Original response files are authoritative for each archived arm. The two hybrid-RAG gated records are corrected by call order, since a prompt hash alone is not a unique arm-response identifier when repeated requests share a cache key. The in-sample retrieval result is not an independently held-out definition-selection test; valid leave-one-question-out identification ranges are reported separately.

The 27-item English source review is in `data/historical_question_audit/review_27/`. Its 17 targeted questions and ten stratified controls are not a probability sample of all historical questions. Removing 14 clearly problematic reviewed questions barely changes the reported AUROCs, but does not validate unreviewed keys. No key was changed using probabilities computed for the old key.

The command-line `pd` tool lives in the sibling `pd-tool/` directory. It is an experimental interface for new corpora, not a validated deployment policy. The private notebook, credentials, provider caches, and per-item model-screen judgements are excluded. Third-party source material retains its own licence, as detailed in `LICENSE.md` and `DATA_CARD.md`.
