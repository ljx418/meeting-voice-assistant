# ResearchNotebook V1.9 设计与验收索引

日期：2026-05-31

## 阶段定位

V1.9 接在 V1.8 Agent-led PRD MVP capability validation 之后，聚焦 Research 质量、冲突标注和最终人工 UX 验收包。

V1.9 不扩大到 OCR、Audio Overview、PPT、Mindmap、Document comparison、all-source-type、all websites URL、cloud sync / collaboration。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `v1_9_development_plan.md` | V1.9 总开发及验收计划。 |
| `v1_9_remaining_development_and_acceptance_plan.md` | V1.9 剩余开发及验收收口计划。 |
| `v1_9_0_scope_rebase_report.md` | V1.9 基线与 V1.8 承接报告。 |
| `v1_9_plan_audit.md` | V1.9 自审和风险闭环。 |
| `v1_9_a_research_quality_plan.md` | Research 质量验收计划。 |
| `v1_9_a_research_quality_report.md` | Research 质量执行报告。 |
| `v1_9_b_conflict_labeling_plan.md` | 冲突标注真实 smoke 计划。 |
| `v1_9_b_conflict_labeling_fix_plan.md` | V1.9-B conflict labeling 修复计划与执行结果。 |
| `v1_9_b_conflict_labeling_report.md` | 冲突标注执行报告。 |
| `v1_9_c_human_ux_acceptance_plan.md` | 人工 UX 验收包计划。 |
| `v1_9_c_human_ux_acceptance_report.md` | 人工 UX 验收包执行报告。 |
| `v1_9_rc_final_prd_acceptance_report.md` | V1.9 RC 聚合验收报告。 |
| `v1_9_prd_coverage_matrix.md` | V1.9 PRD 覆盖矩阵。 |

## 停止规则

- 资料外硬答。
- conflict 未真实存在却写成 PASS。
- Agent smoke 被写成人工 UX ready。
- 自动 smoke 被写成人工质量终审。
- fixtures / reports 泄露本地绝对路径、cache path、artifact physical path、API key。

## 当前状态

V1.9 自动化 RC 已通过到人工验收入口：

- Research quality：`PASS_LIMITED`
- Conflict labeling：`PASS_LIMITED`
- Human UX package：`READY_FOR_HUMAN_ACCEPTANCE`
- RC decision：`V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE`

仍需人工审查 Research / conflict / UX 内容质量后才能 final accepted。
