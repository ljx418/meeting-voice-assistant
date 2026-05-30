# ResearchNotebook V1.6 Design Docs

日期：2026-05-29

V1.6 用来承接 V1.5 之后仍未闭环或未验收的 PRD 功能点。云同步 / 协作已从 V1.x 剩余范围剔除，不再作为 V1.6 目标。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `v1_6_development_plan.md` | V1.6 分阶段开发计划、门禁和风险控制。 |
| `v1_6_acceptance_plan.md` | V1.6 端到端验收标准、真实数据要求和打回规则。 |
| `v1_6_prd_coverage_matrix.md` | PRD 剩余功能覆盖矩阵。 |
| `v1_6_current_gap_analysis.md` | V1.6 当前 gap、风险和阶段边界。 |
| `v1_6_current_gap_analysis.drawio` | V1.6 gap 图。 |
| `v1_6_plan_audit.md` | V1.6 开发与验收计划自审、审计意见和闭环结果。 |
| `v1_6_0_scope_rebase_report.md` | V1.6-0 范围重基线、V1.5 revalidation 矛盾闭环和下一阶段准入结论。 |
| `v1_6_a_url_extraction_plan.md` | V1.6-A URL 正文抽取详细开发计划。 |
| `v1_6_a_url_extraction_acceptance.md` | V1.6-A URL 正文抽取验收标准。 |
| `v1_6_a_url_extraction_plan_audit.md` | V1.6-A 计划审计和风险评估。 |
| `v1_6_a_url_extraction_report.md` | V1.6-A URL 正文抽取执行报告，限定公开 URL smoke 已 PASS_LIMITED。 |
| `v1_6_b_quality_eval_plan.md` | V1.6-B 多数据集质量评估计划。 |
| `v1_6_b_quality_eval_acceptance.md` | V1.6-B 自动 smoke 与人工评分验收标准。 |
| `v1_6_b_quality_eval_plan_audit.md` | V1.6-B 计划审计；允许自动候选评估，但 PASS 声明 NO-GO。 |
| `v1_6_b_manual_quality_review_template.md` | V1.6-B 人工质量评分模板。 |
| `v1_6_b_quality_eval_report.md` | V1.6-B 自动候选评估报告，三组真实数据集已生成候选包，等待人工评分。 |
| `v1_6_c_ocr_contract_plan.md` | V1.6-C OCR / 扫描 PDF 合同发现计划。 |
| `v1_6_c_ocr_contract_plan_audit.md` | V1.6-C 合同发现计划审计。 |
| `v1_6_c_ocr_contract_report.md` | V1.6-C OCR / 扫描 PDF 合同发现报告，OCR 仍为 disabled。 |
| `v1_6_d_studio_export_plan.md` | V1.6-D Studio 导出计划。 |
| `v1_6_d_studio_export_plan_audit.md` | V1.6-D Studio 导出计划审计。 |
| `v1_6_d_studio_export_report.md` | V1.6-D Studio Markdown / JSON 导出执行报告，自动化验证已通过，最终人工下载检查后移到 RC。 |
| `v1_6_e_research_workflow_plan.md` | V1.6-E Research 补源 / 冲突分析计划。 |
| `v1_6_e_research_workflow_acceptance.md` | V1.6-E Research 验收标准。 |
| `v1_6_e_research_workflow_plan_audit.md` | V1.6-E Research 计划审计。 |
| `v1_6_e_research_workflow_report.md` | V1.6-E Research 受限合同 smoke 报告。 |
| `v1_6_f_phase2_output_contract_plan.md` | V1.6-F Phase 2/3 输出合同发现计划。 |
| `v1_6_f_phase2_output_contract_plan_audit.md` | V1.6-F Phase 2/3 输出合同发现计划审计。 |
| `v1_6_f_phase2_output_contract_report.md` | V1.6-F disabled shell 执行报告。 |
| `v1_6_rc_final_acceptance_plan.md` | V1.6-RC 最终 PRD 验收与人工质量评分计划。 |
| `v1_6_rc_final_acceptance_plan_audit.md` | V1.6-RC 计划审计，要求停止自动推进并进入人工验收。 |
| `v1_6_completion_and_manual_acceptance_summary.md` | V1.6 完成大纲、待人工验收总表和最终声明边界。 |
| `v1_6_rc_final_acceptance_report.md` | V1.6-RC 最终验收报告，当前为 V1.6_FINAL_ACCEPTANCE_PASS_SCOPED。 |
| `v1_6_frontend_prd_workflow_validation_report.md` | 前端创建工作区 404 修复、ChromeCLI PRD 主路径 smoke 和页面描述验收记录。 |
| `v1_6_manual_quality_review_key_texts.md` | ChromeCLI 路径关键文本、人工验收关注点和风险边界。 |
| `v1_6_manual_quality_review_screenshot_report.html` | 可点击全屏、缩放、拖动查看的人工截图验收报告；用户已确认通过验收。 |
| `v1_6_final_release_handoff.md` | V1.6 final scoped acceptance、验证命令、风险评估和提交同步计划。 |

## V1.6 总目标

1. 将 V1.5 的限定质量 smoke 扩展到更完整的 PRD MVP 闭环。
2. 补齐或明确打回 URL 抽取、OCR / 扫描 PDF、Studio 导出、Research 补源 / 冲突分析。
3. 对 Phase 2/3 输出能力做合同发现，不在合同和 smoke 通过前声明 ready。
4. 每个子阶段都必须包含 PRD 规格检视、规格漂移风险、虚假验收风险。

## V1.6 最终状态

```text
V1.6_FINAL_ACCEPTANCE_PASS_SCOPED
```

V1.6 已通过：

- `npm run check`
- `npm run smoke:v1.5-e-e2e`
- `npm run smoke:v1.1-visible-user-e2e`
- 用户人工查看并确认 `v1_6_manual_quality_review_screenshot_report.html`

完成声明只能限定为：

```text
ResearchNotebook V1.6 PRD MVP browser path and manual UX / quality screenshot review are accepted for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, Studio exports, and Research contract smoke on approved datasets.
```

## 不进入 V1.6 的能力

- 云同步 / 协作。
- 任意 Agent 自由执行。
- 未经合同冻结的多格式原生解析。
- 未经过真实数据和浏览器路径的 ready 声明。
