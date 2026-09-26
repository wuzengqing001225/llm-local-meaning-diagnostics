# V5 development budget check

**Exploratory only.** The plan was frozen without loading B gold or reader outcomes. The same five-rule pilot and paired outputs are evaluated here.

| Reader | Budget | Policy | Accuracy | Repairs | Harms | Notes |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| deepseek_reader | 25% | matched_fixed | 0.967 | 1 | 0 | 423 |
| deepseek_reader | 25% | dp | 0.967 | 1 | 0 | 404 |
| deepseek_reader | 25% | R | 0.933 | 0 | 0 | 383 |
| deepseek_reader | 25% | dp_per_token | 0.933 | 0 | 0 | 383 |
| deepseek_reader | 25% | random mean (20) | 0.945 | 0.35 | 0.00 | 416.2 |
| deepseek_reader | 50% | matched_fixed | 0.967 | 1 | 0 | 852 |
| deepseek_reader | 50% | dp | 0.967 | 1 | 0 | 846 |
| deepseek_reader | 50% | R | 0.967 | 1 | 0 | 840 |
| deepseek_reader | 50% | dp_per_token | 0.967 | 1 | 0 | 840 |
| deepseek_reader | 50% | random mean (20) | 0.970 | 1.10 | 0.00 | 844.1 |
| deepseek_reader | 75% | matched_fixed | 0.967 | 1 | 0 | 1260 |
| deepseek_reader | 75% | dp | 0.967 | 1 | 0 | 1281 |
| deepseek_reader | 75% | R | 0.967 | 1 | 0 | 1255 |
| deepseek_reader | 75% | dp_per_token | 0.967 | 1 | 0 | 1255 |
| deepseek_reader | 75% | random mean (20) | 0.980 | 1.40 | 0.00 | 1273.2 |
| gpt_reader | 25% | matched_fixed | 0.933 | 0 | 0 | 423 |
| gpt_reader | 25% | dp | 0.967 | 1 | 0 | 404 |
| gpt_reader | 25% | R | 0.967 | 1 | 0 | 383 |
| gpt_reader | 25% | dp_per_token | 0.967 | 1 | 0 | 383 |
| gpt_reader | 25% | random mean (20) | 0.948 | 0.45 | 0.00 | 416.2 |
| gpt_reader | 50% | matched_fixed | 0.933 | 0 | 0 | 852 |
| gpt_reader | 50% | dp | 0.967 | 1 | 0 | 846 |
| gpt_reader | 50% | R | 0.967 | 1 | 0 | 840 |
| gpt_reader | 50% | dp_per_token | 0.967 | 1 | 0 | 840 |
| gpt_reader | 50% | random mean (20) | 0.965 | 0.95 | 0.00 | 844.1 |
| gpt_reader | 75% | matched_fixed | 0.967 | 1 | 0 | 1260 |
| gpt_reader | 75% | dp | 0.967 | 1 | 0 | 1281 |
| gpt_reader | 75% | R | 0.967 | 1 | 0 | 1255 |
| gpt_reader | 75% | dp_per_token | 0.967 | 1 | 0 | 1255 |
| gpt_reader | 75% | random mean (20) | 0.975 | 1.25 | 0.00 | 1273.2 |

The development set is too small and too easy to establish a policy advantage. Use this output to verify accounting and choose the formal source-quality gate, not to make a paper claim.
