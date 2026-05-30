# ResearchNotebook V1.6-RC Final Acceptance Report

日期：2026-05-29

状态：

```text
V1.6_FINAL_ACCEPTANCE_PASS_SCOPED
```

## 环境

| 项 | 值 |
| --- | --- |
| frontend URL | `http://127.0.0.1:5173/` |
| data_service URL | `http://127.0.0.1:8003` |
| browser / ChromeCLI | ChromeCLI / Chrome DevTools Protocol |
| smoke timestamp | 2026-05-29 11:42-11:46 CST |
| frontend commit / branch | `c5797a0f` / `main` |
| data_service commit / branch | `c5797a0f` / `main` |

## 使用数据

| 数据集 | 路径 | 结果 |
| --- | --- | --- |
| 数字人 P0 Markdown | `Desktop/技术分享/11-数字人/AI数字人资料包/` | PASS_LIMITED，已进入 ChromeCLI / screenshot 人工验收链路 |
| 数字人 P0 PDF | `Desktop/技术分享/11-数字人/AI数字人产业发展报告_2026-05-26.pdf` | PASS_LIMITED，仅限可抽取文本 PDF，不声明 OCR |
| 多数据集质量候选包 | `fixtures/real/v1_6/quality-eval/` | PASS_LIMITED，经用户人工验收接受，仍限 approved datasets |

## 自动化基线

| 项 | 当前状态 | 证据 |
| --- | --- | --- |
| V1.6-A URL | PASS_LIMITED | `v1_6_a_url_extraction_report.md` |
| V1.6-B quality candidate | CANDIDATE_READY_FOR_MANUAL_REVIEW | `v1_6_b_quality_eval_report.md` |
| V1.6-C OCR | CONTRACT_DISCOVERY_READY | `v1_6_c_ocr_contract_report.md` |
| V1.6-D Studio export | PASS_LIMITED_UI_TESTED | `v1_6_d_studio_export_report.md` |
| V1.6-E Research | PASS_LIMITED_CONTRACT_SMOKE | `v1_6_e_research_workflow_report.md` |
| V1.6-F Phase 2/3 | DISABLED_READY | `v1_6_f_phase2_output_contract_report.md` |

## RC 自动化复核记录

| 命令 | 结果 | 备注 |
| --- | --- | --- |
| `npm run check` | PASS | 2026-05-29 复跑通过：boundary checks、lint、128 tests、build 均通过。 |
| `npm run smoke:v1.6-a-url` | PASS_LIMITED | URL source import、source preview / unit / evidence chain、Guide / Studio URL evidence 通过；仍不代表 all websites ready。 |
| `npm run smoke:v1.6-b-quality` | CANDIDATE_READY_FOR_MANUAL_REVIEW | 三组真实数据集候选包生成；provider timeout 出现重试降级记录，仍需人工质量评分。 |
| `npm run smoke:v1.6-e-research` | PASS_LIMITED_CONTRACT_SMOKE | 无来源拒答、补源后 Research report、evidence resolution 和 cleanup 通过；Research 内容质量仍需人工检查。 |
| `npm run smoke:v1.5-e-e2e` | PASS | 2026-05-29 复跑通过：Guide / QA / Studio / refusal / cleanup 浏览器路径可达。 |
| `npm run smoke:v1.1-visible-user-e2e` | PASS | 2026-05-29 复跑通过：workspace / source / preview / citation / session 路径可达。 |
| `drawio XML parse` | PASS | `v1_6_current_gap_analysis.drawio` 可解析，`mxCell=17`。 |
| `fixtures path hygiene` | PASS | `fixtures/real/v1_6` 未发现 `/Users`、`file://`、cache path、artifact physical path、`/private/tmp`、`/tmp/`。 |

自动化复核不能单独替代人工验收。本次最终 PASS 依赖用户对截图报告和关键文本的人工验收结论。

## 人工验收证据

| 证据 | 路径 | 结果 |
| --- | --- | --- |
| 人工截图报告 | `docs/design/V1.6/v1_6_manual_quality_review_screenshot_report.html` | PASS，用户确认通过验收。 |
| 关键文本记录 | `docs/design/V1.6/v1_6_manual_quality_review_key_texts.md` | PASS，记录 ChromeCLI 路径关键文本和人工判断点。 |
| 前端 PRD 工作流报告 | `docs/design/V1.6/v1_6_frontend_prd_workflow_validation_report.md` | PASS，记录 404、来源导入、问答反馈、布局重叠修复和 ChromeCLI 结果。 |
| 最新 Guide / QA / Studio 截图 | `.smoke-artifacts/v1_5_e_chromecli_manual_e2e/1780026136870/` | PASS，用于人工质量查看，不纳入 git。 |
| 最新 visible-user 截图 | `.smoke-artifacts/v1_1_visible_user_e2e/1780026263488/` | PASS，用于人工质量查看，不纳入 git。 |

## 人工验收结果

| 验收项 | 结果 | 备注 |
| --- | --- | --- |
| 浏览器打开 app | PASS | ChromeCLI 路径通过。 |
| 创建 Notebook | PASS | ChromeCLI 路径通过。 |
| 导入 Markdown | PASS_LIMITED | 限定 Markdown / TXT / 可抽取文本 PDF / limited URL。 |
| 导入 PDF | PASS_LIMITED | 限定可抽取文本 PDF；扫描 PDF / OCR 仍 NOT_READY。 |
| Notebook Guide | PASS_LIMITED | 用户基于截图报告验收通过；仍限 approved datasets。 |
| 引用问答 | PASS_LIMITED | ChromeCLI citation 可见；用户基于截图报告验收通过。 |
| citation 回跳 | PASS_LIMITED | SourcePreview / DocumentUnit / EvidenceSpan 路径通过。 |
| Studio 四类轻量输出 | PASS_LIMITED | Notes / Study Guide / Briefing Doc / FAQ 路径通过；用户基于截图报告验收通过。 |
| Markdown / JSON 导出 | PASS_LIMITED | V1.6-D 自动化验证通过；导出内容仍限 scoped Studio artifacts。 |
| 资料外问题拒答 | PASS_LIMITED | ChromeCLI refusal 可见；不声明 all-domain refusal quality。 |
| Research report | PASS_LIMITED_CONTRACT_SMOKE | 受限合同 smoke 通过；不声明 all-domain Research ready。 |
| Phase 2/3 disabled shell | PASS | disabled shell 可见；不生成真实输出。 |
| cleanup | PASS | ChromeCLI cleanup 通过。 |

## 人工质量评分

| 维度 | 结果 | 备注 |
| --- | --- | --- |
| 资料相关性 | PASS_LIMITED | 用户基于截图报告验收通过；限 approved datasets。 |
| 覆盖完整性 | PASS_LIMITED | 用户基于截图报告验收通过；不声明 all-domain。 |
| citation 正确性 | PASS_LIMITED | citation 路径和截图验收通过；仍限 data_service-supported evidence refs。 |
| 拒答正确性 | PASS_LIMITED | refusal 路径和截图验收通过；仍限测试问题。 |
| 中文表达 | PASS_LIMITED | 用户验收通过；后续 UX polish 可继续优化。 |
| 幻觉风险 | PASS_LIMITED | 本阶段未发现阻塞性问题；不声明全域无幻觉。 |

## 风险评估

| 风险 | 当前等级 | 说明 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 已有人为验收结论，但完成声明必须保持 PRD MVP scoped，不扩大到 OCR、Phase 2/3 或 all-domain。 |
| 虚假验收 | MEDIUM | 已使用真实数据、ChromeCLI 和人工截图验收；仍需避免把 limited pass 写成 all-source/all-domain ready。 |

## Final Decision

最终决策：

```text
V1.6_FINAL_ACCEPTANCE_PASS_SCOPED
```

完成声明：

```text
ResearchNotebook V1.6 PRD MVP browser path and manual UX / quality screenshot review are accepted for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, Studio exports, and Research contract smoke on approved datasets.
```

仍不能声明：

```text
all websites URL extraction ready
OCR ready
Audio Overview ready
PPT generation ready
Mindmap ready
Document comparison ready
all-domain Research ready
cloud sync / collaboration ready
```
