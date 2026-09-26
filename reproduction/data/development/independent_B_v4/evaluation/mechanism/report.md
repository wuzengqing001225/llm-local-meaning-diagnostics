# 局部含义机制检查

审查状态：automated_screen
弃答协议与预算实验的强制选项协议不同，不能把两者的准确率直接拼成同一表。

| 类别 | 条件 | n | 全题准确率 | 弃答率 | 实质错误率 | 普通义方向比例 |
|---|---|---:|---:|---:|---:|---:|
| all | bare | 28 | 0.821 | 0.179 | 0.000 | 0.0 |
| all | local_note | 28 | 1.000 | 0.000 | 0.000 | 0.0 |
| all | usual_note | 26 | 0.846 | 0.154 | 0.000 | 0.0 |
| all | irrelevant_note | 28 | 0.821 | 0.179 | 0.000 | 0.0 |
| control | bare | 16 | 0.938 | 0.062 | 0.000 | None |
| control | local_note | 16 | 1.000 | 0.000 | 0.000 | None |
| control | usual_note | 14 | 0.929 | 0.071 | 0.000 | None |
| control | irrelevant_note | 16 | 0.938 | 0.062 | 0.000 | None |
| local_binding | bare | 12 | 0.667 | 0.333 | 0.000 | 0.0 |
| local_binding | local_note | 12 | 1.000 | 0.000 | 0.000 | 0.0 |
| local_binding | usual_note | 12 | 0.750 | 0.250 | 0.000 | 0.0 |
| local_binding | irrelevant_note | 12 | 0.667 | 0.333 | 0.000 | 0.0 |

全部数值只支持实际类别/对照覆盖的范围。自动标注不能冒称人工确认，缺少规则证据不能证明第三类原因。