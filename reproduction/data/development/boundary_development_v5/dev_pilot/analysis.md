# V5 development pilot results

**Exploratory only.** Five source rules, controlled hypothetical B facts, and shared A/B generator. This report is not a confirmatory independent-request result.

- B tasks: 30; paired predictions: 120 / 120; complete: True.

| Reader | Pairs | Bare accuracy | With definition | Repairs | Harms |
| --- | ---: | ---: | ---: | ---: | ---: |
| deepseek_reader | 30 | 0.933 | 1.000 | 2 | 0 |
| gpt_reader | 30 | 0.933 | 1.000 | 2 | 0 |

Bare wrong cases (all paired with definition outcomes in the JSON report):

- deepseek_reader: `B:cuadfull:170:Products:b_doughnut`, `B:cuadfull:38:New Product:b_new_hardware`
- gpt_reader: `B:cuadfull:170:Products:b_doughnut`, `B:cuadfull:38:New Product:b_firmware_update`

| Definition | A n | Mean R(A) | Mean Δp(A) |
| --- | ---: | ---: | ---: |
| cuadfull:108:Third Party | 4 | 0.573 | 0.302 |
| cuadfull:170:Products | 4 | 0.377 | 0.187 |
| cuadfull:171:Confidential Information | 4 | 0.399 | 0.200 |
| cuadfull:250:System Images | 4 | 0.512 | 0.178 |
| cuadfull:38:New Product | 4 | 0.457 | 0.297 |

The A means are not candidate population estimates; all five rules were source-picked for a development feasibility check. Formal sampling must include low, middle and high Δp after scoring a broader eligible source frame.
