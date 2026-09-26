# Model cutoffs and document exposure

Official OpenAI model pages list knowledge cutoffs of **2026-02-16** for `gpt-5.6-terra` and **2026-04-30** for `gpt-6-astra`. Their release announcements are dated 2026-07-09 and 2026-09-03, respectively. These facts support a temporal distinction only for source statements demonstrably first published after each cutoff.

The local DeFi collection contains `file_dates.json` for 117 Uniswap documentation paths. It labels 68 paths 2026-07-17 and includes older dates. The 97 term records with reader questions each link 4--20 documentation files (median 18), and the 379 questions do not identify the particular source file or first publication date needed for their key. A repository migration or document update date does not prove the underlying rule was new. Uniswap's previous documentation repository was publicly archived on 2026-04-08; Uniswap v4 launched in January 2025 and Unichain mainnet in February 2025. Thus at least some relevant protocol knowledge existed before both GPT cutoffs.

**Inference limit:** DeFi R AUROC 0.792/0.764 measures how well a small proxy ranks GPT readers' bare errors. It is not a test of whether either reader memorized a particular answer. Even if a question relied on genuinely post-cutoff text, the model could infer the answer from prior protocol knowledge, the question/options, or source-related generalization. We should say that the model cutoffs precede the assembled documentation snapshot, not that memorization has been ruled out. A stronger test would link each answer to a precisely dated, newly introduced rule and evaluate the post-cutoff subset separately.

DeepSeek officially announced V4.1 Flash on 2026-09-10. Its documented API model ID is `deepseek-flash`; the legacy ID `deepseek-v4-flash` routed to V4.1 only after release. The experiment operator has now confirmed that the synthetic DeepSeek reader used V4 Flash before September 10 and the later Reddit/DeFi readers used V4.1 Flash. The manuscript labels these separately and does not assign an unreported knowledge cutoff to either DeepSeek version.

Primary sources:
- OpenAI GPT-5.6 Terra model page: https://developers.openai.com/api/docs/models/gpt-5.6-terra
- OpenAI GPT-6 Astra model page: https://developers.openai.com/api/docs/models/gpt-6-astra
- DeepSeek V4.1 Flash announcement: https://www.deepseek.com/en/news/deepseek-v4-1-flash/
- DeepSeek API change log: https://api-docs.deepseek.com/updates/
- Archived Uniswap documentation repository: https://github.com/Uniswap/docs-content
- Uniswap v4 January 2025 launch: https://blog.uniswap.org/uniswap-v4-is-here
- Unichain February 2025 launch: https://blog.uniswap.org/unichain-mainnet-is-here
