# ResearchNotebook V1.5-RC Quality Release Handoff

日期：2026-05-28

## 当前状态

PASS_LIMITED。

V1.5 已完成真实 AI provider、AI Notebook Guide、AI Studio Outputs、Source-grounded QA、ChromeCLI / Manual E2E 的质量 smoke，并在 2026-05-28 按收紧后的审计门禁重新复验通过。所有声明均限定为数字人 P0 数据集和已验收的 PDF / TXT / Markdown 主路径。

## 已完成阶段

| 阶段 | 状态 | 证据 |
| --- | --- | --- |
| V1.5-A AI Provider Contract | PASS | MiniMax provider health route + real model call |
| V1.5-B AI Notebook Guide | PASS_LIMITED | 数字人 P0 数据集真实 Guide smoke |
| V1.5-C AI Studio Outputs | PASS_LIMITED | Notes / Study Guide / Briefing Doc / FAQ 真实 AI 输出 |
| V1.5-D Source-grounded QA | PASS_LIMITED | 覆盖问答 / 资料外拒答 / 推断标注 / citation 解析 |
| V1.5-E ChromeCLI / Manual E2E | PASS_LIMITED | 浏览器路径 Guide / QA / 高亮 / Studio / 拒答 / cleanup |
| V1.5 Revalidation | PASS_LIMITED | 重新执行 A/B/C/D/E smoke；provider 和 Sources P0 链路均通过 |

## 已验证命令

- `python3 -m pytest tests/test_target_http_ai_provider.py tests/test_target_http_notebook_guide.py tests/test_target_http_studio_artifacts.py tests/test_target_http_evidence_spans.py -q`
- `npm run smoke:v1.5-a-provider`
- `npm run smoke:v1.5-b-guide`
- `npm run smoke:v1.5-c-studio`
- `npm run smoke:v1.5-d-qa`
- `npm run smoke:v1.5-e-e2e`
- `npm run check`

2026-05-28 收紧复验重新执行：

- `npm run smoke:v1.5-a-provider`
- `npm run smoke:v1.5-b-guide`
- `npm run smoke:v1.5-c-studio`
- `npm run smoke:v1.5-d-qa`
- `npm run smoke:v1.5-e-e2e`

## 真实数据

- 数据目录：`Desktop/技术分享/11-数字人`
- Markdown：`AI数字人资料包/01_industry_overview.md`
- Markdown：`AI数字人资料包/02_technology_trends.md`
- PDF：`AI数字人产业发展报告_2026-05-26.pdf`

## Fixtures

- `fixtures/real/v1_5/ai-provider/`
- `fixtures/real/v1_5/ai-guide/`
- `fixtures/real/v1_5/ai-studio/`
- `fixtures/real/v1_5/source-grounded-qa/`
- `fixtures/real/v1_5/chromecli-manual-e2e/`

脱敏检查：

- 未发现 API key / Authorization / Bearer。
- 未发现 `/Users`、`file://`、`cache_path`、`artifact_path`、`physical_path`。
- Chrome 截图只保存到 `.smoke-artifacts/`，不纳入提交。

## PRD 覆盖结论

已达到 V1.5 质量 smoke 范围：

- Notebook Guide：PASS_LIMITED。
- 基于来源的引用问答：PASS_LIMITED。
- 资料不足拒答：PASS_LIMITED。
- Notes：PASS_LIMITED。
- Study Guide：PASS_LIMITED。
- Briefing Doc：PASS_LIMITED。
- FAQ：PASS_LIMITED。
- Citation 跳转和 EvidenceSpan 高亮：PASS_LIMITED。
- V1.4-C Sources P0 Markdown/PDF 导入、build 和 citation 路径：PASS_LIMITED。

仍不声明 ready：

- URL 正文抽取。
- OCR / 扫描 PDF。
- Word / PPT / audio / video 原生摄入。
- Audio Overview。
- PPT 生成。
- 思维导图。
- 文档对比。
- all-source-type ready。
- arbitrary Agent ready。

范围剔除：

- 云同步 / 协作不再作为 V1.x 剩余闭环目标；如未来恢复，应另开独立产品线和账户 / 权限 / 同步合同。

## 风险评估

- 规格漂移风险：LOW。
- 虚假验收风险：MEDIUM。

原因：

- 已经使用真实模型和真实浏览器路径。
- 验收材料仍是单一 P0 主题数据集，不能代表所有行业、所有 source type 或所有输出场景。
- 内容质量仍建议后续扩大评测集后做人工抽样评分。

停止条件评估：

- 未出现 HIGH 风险。
- 未发现 API key 或本地路径泄漏。
- 未发现 `/api/v1/knowledge/*` 新功能调用。
- `npm run check` PASS。

## 完成声明

ResearchNotebook V1.5 AI Guide, source-grounded QA, and Studio lightweight outputs are quality-smoke-ready for the AI digital human P0 dataset.

ResearchNotebook V1.5 ChromeCLI / Manual E2E is PASS_LIMITED for the same supported dataset and source path.

## 下一阶段建议

进入 V1.6 前先审计范围。建议优先级：

1. URL 正文抽取 P1 contract。
2. 更大 P0/P1 评测集和人工评分表。
3. OCR / 扫描 PDF 识别合同。
4. Studio 输出下载 / 导出。
5. Research 补源、冲突标注和综合输出。
6. Audio Overview / PPT / Mindmap / Document comparison 先做合同发现，不在 V1.5 声明 ready。
