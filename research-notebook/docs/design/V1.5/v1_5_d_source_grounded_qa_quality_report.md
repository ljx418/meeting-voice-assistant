# ResearchNotebook V1.5-D Source-grounded QA Quality Report

日期：2026-05-27

## 执行状态

PASS_LIMITED。

V1.5-D 已完成真实 MiniMax source-grounded QA smoke。覆盖型问题、资料外拒答、推断型问题、citation 解析均通过。

## 真实数据

- 数据目录：`Desktop/技术分享/11-数字人`
- Markdown：`AI数字人资料包/01_industry_overview.md`
- Markdown：`AI数字人资料包/02_technology_trends.md`
- PDF：`AI数字人产业发展报告_2026-05-26.pdf`

## 验收问题

| 类型 | 问题 | 状态 |
| --- | --- | --- |
| 覆盖型问题 | 数字人 技术 趋势是什么？ | PASS |
| 覆盖型问题 | 数字人 风险 监管 政策有哪些？ | PASS |
| 资料外问题 | 火星采矿 农业机械 海洋运输的结论是什么？ | PASS |
| 推断型问题 | 基于资料推断，数字人未来商业化可能面临什么挑战？ | PASS |
| citation 定位 | unit detail + EvidenceSpan route | PASS |

## 命令证据

- `python3 -m pytest tests/test_target_http_evidence_spans.py -q`
  - 结果：9 passed。
- `npm run check`
  - 结果：boundary checks、lint、tests、build 均通过。
- `npm run smoke:v1.5-d-qa`
  - 结果：workspace/source/build/覆盖问答/拒答/推断/citation/cleanup 全部 PASS。

## Fixtures

保存位置：

- `fixtures/real/v1_5/source-grounded-qa/`

关键文件：

- `query-covered-technology.json`
- `query-covered-risk.json`
- `query-outside.json`
- `query-inference.json`
- `query-covered-technology-evidence-span.json`
- `query-covered-risk-evidence-span.json`
- `query-inference-evidence-span.json`
- `v1_5_d_source_grounded_qa_smoke_result.json`

脱敏检查：

- 未发现 `/Users`
- 未发现 `file://`
- 未发现 `cache_path`
- 未发现 `artifact_path`
- 未发现 `physical_path`
- 未发现 API key / Authorization / Bearer

## PRD 规格检视

覆盖项：

- 默认只基于当前 Notebook sources 回答：PASS_LIMITED。
- 每个关键断言必须带引用：PASS_LIMITED。
- 资料不足时拒答并提示补源：PASS。
- 区分来源结论和推断：PASS_LIMITED，推断型问题明确标注“基于来源的推断”。
- citation 可定位到 source / unit / EvidenceSpan：PASS_LIMITED。

边界：

- 仅覆盖数字人 P0 数据集。
- 不声明 all-source-type QA ready。
- 不声明 all-session QA ready。
- 不声明互联网 research ready。
- 不声明人工质量终审完成。

## 风险评估

- 规格漂移风险：LOW。
- 虚假验收风险：MEDIUM。

原因：

- 真实 provider、真实资料、真实 citation 路径已通过。
- 仍未完成 ChromeCLI / manual E2E 视觉路径和人工内容质量深审。
- 覆盖型趋势/风险问题被模型标为 `source_based_inference`，保守但需要人工验收时确认表达是否符合产品预期。

收敛措施：

- V1.5-E 必须用浏览器路径验证 Guide、QA、Studio 和 citation 点击。
- V1.5-E 必须保留人工质量检查，不允许仅凭 API smoke 声明完整 release-ready。

## 下一阶段审计意见

V1.5-E ChromeCLI / Manual E2E 可进入执行。

准入条件：

- V1.5-A provider PASS。
- V1.5-B Guide PASS_LIMITED。
- V1.5-C Studio PASS_LIMITED。
- V1.5-D QA PASS_LIMITED。
- `npm run check` 当前 PASS。

V1.5-E 不得扩大声明到 Audio / PPT / Mindmap / Compare，也不得把数字人 P0 数据集通过扩展为所有 source type ready。
