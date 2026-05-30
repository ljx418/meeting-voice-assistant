# ResearchNotebook V1.6 Completion And Manual Acceptance Summary

日期：2026-05-29

## 结论

V1.6 的自动化开发阶段已经推进到 RC 并完成用户人工截图 / UX 验收。当前可以进入 V1.6-FINAL scoped sync，但完成声明必须保持 PRD MVP scoped，不能扩大到 OCR、Phase 2/3 或 all-domain。

当前 RC 状态：

```text
V1.6_FINAL_ACCEPTANCE_PASS_SCOPED
```

## RC 自动化基线刷新

2026-05-28 16:35:34 CST 已刷新 RC 自动化基线：

| 命令 | 结果 | 说明 |
| --- | --- | --- |
| `npm run check` | PASS | boundary checks、lint、127 tests、build 均通过。 |
| `npm run smoke:v1.6-a-url` | PASS_LIMITED | 限定公开 URL source 链路通过。 |
| `npm run smoke:v1.6-b-quality` | CANDIDATE_READY_FOR_MANUAL_REVIEW | 三组真实数据集候选包生成；仍需人工质量评分。 |
| `npm run smoke:v1.6-e-research` | PASS_LIMITED_CONTRACT_SMOKE | Research 合同 smoke 通过；仍需人工内容质量检查。 |
| `drawio XML parse` | PASS | V1.6 gap drawio 可解析。 |
| `fixtures path hygiene` | PASS | V1.6 fixtures 未发现本地绝对路径或 artifact physical path。 |

2026-05-29 已追加验证：

| 命令 / 验收 | 结果 | 说明 |
| --- | --- | --- |
| `npm run check` | PASS | boundary checks、lint、128 tests、build 均通过。 |
| `npm run smoke:v1.5-e-e2e` | PASS | Guide / QA / Studio / refusal / cleanup 浏览器路径通过。 |
| `npm run smoke:v1.1-visible-user-e2e` | PASS | workspace / source / preview / citation / session 路径通过。 |
| 人工截图报告 | PASS | 用户确认 `v1_6_manual_quality_review_screenshot_report.html` 通过验收。 |

该刷新证明 V1.6 scoped acceptance 可进入 final handoff。仍不得声明 all-source、OCR、Phase 2/3 或 all-domain ready。

## V1.6 阶段完成状态

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| V1.6-0 Scope Rebase | PASS | V1.5 revalidation 与 V1.6 范围已确认，云同步 / 协作保持 OUT_OF_SCOPE。 |
| V1.6-A URL 正文抽取 | PASS_LIMITED | 限定公开 HTTP URL smoke 通过，不代表 all websites ready。 |
| V1.6-B 多数据集质量评估 | PASS_LIMITED_ACCEPTED | 三组真实数据集自动 smoke 已生成候选包，并经用户截图 / 关键文本验收接受。 |
| V1.6-C OCR / 扫描 PDF | CONTRACT_DISCOVERY_READY | `ocr=false` / `scanned_pdf_ocr=false`，扫描 PDF 返回 `ocr_required`，不声明 OCR ready。 |
| V1.6-D Studio 导出 | PASS_LIMITED_UI_TESTED | Markdown / JSON 导出自动化验证通过，真实浏览器下载文件人工检查留到 RC。 |
| V1.6-E Research 补源 / 冲突分析 | PASS_LIMITED_CONTRACT_SMOKE | 无来源拒答、补源后 structured Research report 与 evidence_refs 解析通过；Research 质量仍需人工检查。 |
| V1.6-F Phase 2/3 输出合同发现 | DISABLED_READY | Audio / PPT / Mindmap / Compare 仅 disabled shell，不生成真实输出。 |
| V1.6-RC Final Acceptance | V1.6_FINAL_ACCEPTANCE_PASS_SCOPED | ChromeCLI 路径、截图报告、关键文本和用户人工验收已闭环。 |

## 需要审计的开发计划与报告路径

| 文档 | 审计重点 |
| --- | --- |
| `docs/design/V1.6/v1_6_development_plan.md` | V1.6 总体阶段划分与边界。 |
| `docs/design/V1.6/v1_6_acceptance_plan.md` | V1.6 验收门槛、真实数据要求和打回规则。 |
| `docs/design/V1.6/v1_6_prd_coverage_matrix.md` | PRD 功能覆盖状态是否过度声明。 |
| `docs/design/V1.6/v1_6_current_gap_analysis.md` | 当前 gap、风险和下一阶段是否一致。 |
| `docs/design/V1.6/v1_6_current_gap_analysis.drawio` | drawio 状态是否与 markdown 一致。 |
| `docs/design/V1.6/v1_6_plan_audit.md` | 总计划审计意见是否闭环。 |
| `docs/design/V1.6/v1_6_a_url_extraction_report.md` | URL 抽取是否只声明限定公开站点。 |
| `docs/design/V1.6/v1_6_b_quality_eval_report.md` | 自动候选评估是否没有替代人工评分。 |
| `docs/design/V1.6/v1_6_b_manual_quality_review_template.md` | 人工评分维度是否足够覆盖 PRD 质量要求。 |
| `docs/design/V1.6/v1_6_c_ocr_contract_report.md` | OCR 是否仍保持 disabled / not ready。 |
| `docs/design/V1.6/v1_6_d_studio_export_report.md` | Studio 导出是否保留 citation metadata 且未泄漏路径。 |
| `docs/design/V1.6/v1_6_e_research_workflow_report.md` | Research 是否仍限定 source-grounded contract smoke。 |
| `docs/design/V1.6/v1_6_f_phase2_output_contract_report.md` | Phase 2/3 是否仅 disabled shell。 |
| `docs/design/V1.6/v1_6_rc_final_acceptance_plan.md` | RC 人工验收路径是否完整。 |
| `docs/design/V1.6/v1_6_rc_final_acceptance_plan_audit.md` | HIGH 风险是否要求停止自动推进。 |
| `docs/design/V1.6/v1_6_rc_final_acceptance_report.md` | 最终 scoped acceptance 状态和仍不能声明的能力边界。 |
| `docs/design/V1.6/v1_6_manual_quality_review_screenshot_report.html` | 人工截图验收证据。 |
| `docs/design/V1.6/v1_6_manual_quality_review_key_texts.md` | 人工验收关键文本。 |

## 人工验收总表

验收状态只能填写：

```text
PASS
FAIL
DEGRADED_ACCEPTED
NOT_READY
NOT_RUN
```

| 验收项 | 当前建议状态 | 人工验收结果 | 备注 |
| --- | --- | --- | --- |
| 打开 ResearchNotebook 浏览器页面 | PASS | PASS | ChromeCLI / screenshot report。 |
| 创建 Notebook | PASS | PASS | ChromeCLI / screenshot report。 |
| 导入数字人 P0 Markdown | PASS_LIMITED | PASS_LIMITED | 使用 `Desktop/技术分享/11-数字人`；限 Markdown/TXT/PDF/URL scoped path。 |
| 导入数字人 P0 PDF | PASS_LIMITED | PASS_LIMITED | 仅验收可抽取文本 PDF，不验收 OCR。 |
| Notebook Guide 展示 | PASS_LIMITED | PASS_LIMITED | 用户基于截图报告验收通过。 |
| Suggested Question 提问 | PASS_LIMITED | PASS_LIMITED | ChromeCLI QA path 通过。 |
| 引用问答回答 | PASS_LIMITED | PASS_LIMITED | citation 可见；不声明 all-domain QA。 |
| citation 回跳 | PASS_LIMITED | PASS_LIMITED | SourcePreview / DocumentUnit / EvidenceSpan 定位通过。 |
| Studio Notes 生成 | PASS_LIMITED | PASS_LIMITED | scoped Studio artifact。 |
| Studio Study Guide 生成 | PASS_LIMITED | PASS_LIMITED | scoped Studio artifact。 |
| Studio Briefing Doc 生成 | PASS_LIMITED | PASS_LIMITED | scoped Studio artifact。 |
| Studio FAQ 生成 | PASS_LIMITED | PASS_LIMITED | scoped Studio artifact。 |
| Markdown 导出 | PASS_LIMITED | PASS_LIMITED | V1.6-D 自动化验证通过。 |
| JSON 导出 | PASS_LIMITED | PASS_LIMITED | V1.6-D 自动化验证通过。 |
| 资料外问题拒答 | PASS_LIMITED | PASS_LIMITED | refusal path 通过。 |
| 补源建议 | PASS_LIMITED | PASS_LIMITED | Research contract smoke 通过。 |
| Research report 生成 | PASS_LIMITED_CONTRACT_SMOKE | PASS_LIMITED_CONTRACT_SMOKE | 不声明 all-domain Research ready。 |
| Phase 2/3 工具 disabled | PASS | PASS | Audio / PPT / Mindmap / Compare 不生成伪输出。 |
| cleanup / archive workspace | PASS | PASS | ChromeCLI cleanup 通过。 |

## 人工质量评分总表

| 维度 | PASS 标准 | 人工结果 | 备注 |
| --- | --- | --- | --- |
| 资料相关性 | 输出明确来自当前资料，不是泛泛行业描述。 | PASS_LIMITED | 用户基于截图报告验收通过；限 approved datasets。 |
| 覆盖完整性 | 覆盖问题要求的主要方面，不明显漏掉关键来源。 | PASS_LIMITED | 不声明 all-domain。 |
| citation 正确性 | 每个关键结论有可定位 citation。 | PASS_LIMITED | 限 data_service-supported evidence refs。 |
| 拒答正确性 | 资料不足时明确拒答并引导补源。 | PASS_LIMITED | 限测试问题。 |
| 中文表达 | 可读、自然、适合知识工作者。 | PASS_LIMITED | 后续可继续 UX polish。 |
| 幻觉风险 | 不出现资料中没有的硬结论、公司、政策或数据。 | PASS_LIMITED | 不声明全域无幻觉。 |

## Studio 导出人工检查

| 检查项 | 人工结果 | 备注 |
| --- | --- | --- |
| Markdown 文件可下载并打开 |  |  |
| Markdown 包含标题、summary、sections |  |  |
| Markdown 包含 citation metadata |  |  |
| JSON 文件可下载并打开 |  |  |
| JSON 包含 artifact_id / artifact_type |  |  |
| JSON 包含 sections / evidence_refs |  |  |
| JSON 包含 schema_version / exported_at |  |  |
| 文件内容不含 `/Users`、`file://`、cache path、artifact physical path |  |  |

## Research 人工检查

| 检查项 | 人工结果 | 备注 |
| --- | --- | --- |
| 无来源时拒答 |  |  |
| 补源后可生成 structured report |  |  |
| supported_conclusions 来自来源 |  |  |
| supported_conclusions 绑定 evidence_refs |  |  |
| inferences 明确标注为基于来源的推断 |  |  |
| conflicts 为空时没有宣称完整冲突分析 ready |  |  |
| missing_evidence 合理 |  |  |
| suggested_source_actions 可执行 |  |  |
| 未自动联网搜索 |  |  |

## 最终声明决策

人工验收通过后，最多允许声明：

```text
ResearchNotebook V1.6 PRD MVP path is broader-smoke-ready for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, Studio exports, and Research contract smoke on approved datasets.
```

仍不能声明：

- all websites URL extraction ready
- OCR ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- all-domain Research ready
- cloud sync / collaboration ready

## 当前阻塞

V1.6-RC 人工验收已通过。当前无 V1.6-FINAL release handoff 阻塞。

下一步进入：

```text
V1.6-FINAL Release Handoff / Scoped Sync
```
