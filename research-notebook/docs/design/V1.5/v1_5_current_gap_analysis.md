# ResearchNotebook V1.5 Current Gap Analysis

日期：2026-05-28

## 一句话结论

V1.5-A/B/C/D/E 已按收紧后的审计门禁重新复验通过：真实 MiniMax provider、数字人 P0 Markdown/PDF 来源链路、AI Notebook Guide、AI Studio 轻量输出、Source-grounded QA、ChromeCLI / Manual E2E 均为 PASS_LIMITED。

## 当前状态

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| V1.5 计划文档 | PASS | 已补齐开发计划、验收计划和阶段文档。 |
| AI Provider Contract | PASS | MiniMax OpenAI-compatible health route、真实模型调用、脱敏 fixture、focused tests 均通过。 |
| AI Notebook Guide | PASS_LIMITED | MiniMax 真实 AI Guide 已通过数字人 P0 数据集 smoke；不声明 all-source-type ready。 |
| AI Studio Outputs | PASS_LIMITED | Notes / Study Guide / Briefing Doc / FAQ 均通过真实 MiniMax smoke；每个 section 带 evidence_refs。 |
| AI Source-grounded QA | PASS_LIMITED | 覆盖型问题、资料外拒答、推断标注、citation 解析均通过真实 smoke。 |
| ChromeCLI / Manual E2E | PASS_LIMITED | Guide、QA citation、高亮、Studio 四类输出、资料外拒答和 cleanup 已通过浏览器 E2E。 |
| V1.5 收紧复验 | PASS_LIMITED | 2026-05-28 重新执行 A/B/C/D/E smoke，未出现 HIGH 风险。 |

## 主要缺口

1. V1.6 需要承接 PRD 中仍未闭环或未验收的功能点。
2. URL 正文抽取、OCR / 扫描 PDF、Studio 导出、Research 补源和冲突分析仍未完成。
3. Phase 2/3 的 Audio Overview、PPT、思维导图、文档对比仍未进入可声明 ready 状态。
4. PRD 原始 Stitch 文档仍建议后续重新同步；当前以用户粘贴 PRD 作为规格基线。

## V1.x 范围剔除

云同步 / 协作不再作为 V1.x 剩余闭环目标；它需要账户、权限、同步、冲突合并和协作审计模型，已超出当前 PRD MVP 收口范围。

## 风险

规格漂移风险：LOW。

虚假验收风险：MEDIUM。

原因：V1.5 主路径已按收紧门禁重新通过真实数据和浏览器 smoke，但数据集仍限定为数字人 P0；不能扩大为 all-source-type 或所有行业 ready。
