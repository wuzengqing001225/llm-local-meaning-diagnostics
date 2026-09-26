# Historical reader identity and date evidence

The requested aliases `deepseek-flash`, `gpt-5.6-terra`, and `gpt-6-astra`, and DeepSeek service versions v4/v4.1, were confirmed by the experiment operator on 2026-09-23 in `provenance/model_confirmation.json`. This confirmation date is **not** an API call date. Recovered response rows carry alias-like model fields but no provider response ID or call timestamp.

The original output files below are SHA-256 identical to the released copies. Their filesystem modification dates are useful leads for finding execution logs, **not verified call dates**. A run may span more than one day, and copying or editing files can change timestamps.

| Setting | Original output modification time (JST) | SHA equals released file |
|---|---|---|
| Synthetic / `deepseek-flash` | 2026-09-07 00:19 | yes |
| Synthetic / `gpt-6-astra` | 2026-09-15 21:46 | yes |
| Reddit / `deepseek-flash` | 2026-09-15 14:22 | yes |
| Reddit / `gpt-6-astra` | 2026-09-16 03:12 | yes |
| DeFi / `deepseek-flash` | 2026-09-11 08:42 | yes |
| DeFi / `gpt-5.6-terra` | 2026-09-14 02:23 | yes |
| DeFi / `gpt-6-astra` | 2026-09-15 23:42 | yes |
| CUAD / `gpt-5.6-terra` | 2026-09-10 04:32 | yes |

If execution logs or provider usage records confirm a call date or date range for each setting, replace the manuscript's explicit missing-date statement with those dates. Do not relabel this table as API call dates without such confirmation.
