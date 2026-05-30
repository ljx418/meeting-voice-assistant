# ResearchNotebook V1.5 Design Docs

V1.5 目标是把 V1.4 的 PASS_LIMITED 从“确定性合同可用”推进到“真实 AI 输出质量可验收”。

本阶段执行规则：

- 每个子阶段先写开发计划和验收标准。
- 每个子阶段开始实质开发前必须完成 PRD 规格检视。
- 如果出现重大规格偏差或虚假验收 HIGH 风险，立即停止并等待用户确认。
- 每个子阶段完成后必须执行端到端验收。
- 验收不通过时，打回计划阶段重新审计。
- V1.5 使用真实数据：`Desktop/技术分享/11-数字人`。

## 文档索引

| 文档 | 说明 |
| --- | --- |
| `v1_5_prd_quality_gate.md` | V1.5 对 PRD 的规格基线、范围和不可伪装声明。 |
| `v1_5_development_plan.md` | V1.5 子阶段开发计划和阶段门禁。 |
| `v1_5_acceptance_plan.md` | V1.5 端到端验收标准、真实数据和失败打回规则。 |
| `v1_5_0_plan_audit.md` | V1.5-0 计划审计意见、风险评估和是否允许进入实质开发的决定。 |
| `v1_5_a_ai_provider_contract_plan.md` | V1.5-A AI provider 合同开发计划。 |
| `v1_5_a_ai_provider_contract_report.md` | V1.5-A 执行报告，MiniMax provider contract 和真实模型 smoke 已通过。 |
| `v1_5_b_ai_notebook_guide_plan.md` | V1.5-B AI Notebook Guide 开发和验收计划。 |
| `v1_5_b_ai_notebook_guide_report.md` | V1.5-B 执行报告，数字人 P0 数据集 AI Guide 已通过真实 MiniMax smoke。 |
| `v1_5_c_ai_studio_outputs_plan.md` | V1.5-C AI Studio 轻量输出开发和验收计划。 |
| `v1_5_c_ai_studio_outputs_report.md` | V1.5-C 执行报告，Notes / Study Guide / Briefing Doc / FAQ 已通过真实 MiniMax smoke。 |
| `v1_5_d_source_grounded_qa_quality_plan.md` | V1.5-D 真实 AI 引用问答质量计划。 |
| `v1_5_d_source_grounded_qa_quality_report.md` | V1.5-D 执行报告，覆盖问答、资料外拒答、推断标注和 citation 解析已通过真实 MiniMax smoke。 |
| `v1_5_e_chromecli_manual_e2e_plan.md` | V1.5-E ChromeCLI / 人工端到端验收计划。 |
| `v1_5_e_chromecli_manual_e2e_report.md` | V1.5-E 执行报告，真实浏览器主路径已通过。 |
| `v1_5_revalidation_report.md` | V1.5 收紧门禁复验报告，确认 provider、Sources P0、Guide、Studio、QA、ChromeCLI E2E 仍通过。 |
| `v1_5_rc_quality_release_handoff.md` | V1.5-RC 质量收口与 release handoff 占位。 |
| `v1_5_prd_coverage_matrix.md` | V1.5 PRD 覆盖矩阵。 |
| `v1_5_current_gap_analysis.md` | V1.5 当前差距分析。 |
| `v1_5_current_gap_analysis.drawio` | V1.5 gap 图。 |
