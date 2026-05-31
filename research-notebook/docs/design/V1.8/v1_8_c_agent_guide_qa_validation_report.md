# V1.8-C Agent-Led Guide / QA / Citation Validation Report

日期：2026-05-30

## 当前状态

`PASS_LIMITED`

本阶段新增并通过 Agent-led Guide / QA / citation validation smoke，用于验证 Agent 在真实数字人资料基础上生成 Notebook Guide、发起 source-grounded QA，并解析 citation 到 DocumentUnit / EvidenceSpan。

## 实现内容

| 项 | 状态 |
| --- | --- |
| Agent draft | IMPLEMENTED |
| Markdown import | IMPLEMENTED |
| PDF import | IMPLEMENTED |
| build/index polling | IMPLEMENTED |
| Notebook Guide validation | IMPLEMENTED |
| Suggested Question QA | IMPLEMENTED |
| fixed covered QA | IMPLEMENTED |
| outside-question refusal | IMPLEMENTED |
| DocumentUnit resolution | IMPLEMENTED |
| EvidenceSpan resolution | IMPLEMENTED |
| WorkflowRun / ValidationReport fixture | IMPLEMENTED |
| fixture path hygiene | PASS |

## 新增命令

```bash
npm run smoke:v1.8-agent-guide-qa
```

## 验证范围

- Guide 非空。
- Overview 提及数字人。
- Key Topics 至少 3 个。
- Suggested Questions 至少 3 个。
- Guide evidence_refs 至少 1 个。
- 至少一个 Key Topic 带 evidence_refs。
- Suggested Question QA 返回带引用答案。
- 固定覆盖型 QA 返回带引用答案。
- 至少一个 citation 可解析到 DocumentUnit。
- 至少一个 citation 可解析到 EvidenceSpan。
- EvidenceSpan offset contract 为 `normalized_text / half_open / document_unit_text`。
- 资料外问题拒答。

## 当前仍不可声明

- 普通用户 UX ready
- Studio quality ready
- all-domain QA quality ready
- all-source-type ready
- all websites URL ready
- Research ready

## 已执行命令

```bash
npm run check
npm run smoke:v1.5-b-guide
RN_V15_QA_PROVIDER_MAX_ATTEMPTS=5 RN_V15_QA_PROVIDER_RETRY_DELAY_MS=5000 npm run smoke:v1.5-d-qa
npm run smoke:v1.8-agent-guide-qa
```

| 命令 | 结果 |
| --- | --- |
| `npm run check` | PASS |
| `npm run smoke:v1.5-b-guide` | PASS |
| `RN_V15_QA_PROVIDER_MAX_ATTEMPTS=5 RN_V15_QA_PROVIDER_RETRY_DELAY_MS=5000 npm run smoke:v1.5-d-qa` | PASS_WITH_RETRY |
| `npm run smoke:v1.8-agent-guide-qa` | PASS_LIMITED |

## 真实数据与 fixture

- 真实数据目录：`Desktop/技术分享/11-数字人`
- Markdown：数字人资料包中的行业概览与技术趋势资料
- PDF：AI 数字人产业发展报告
- fixture：`fixtures/real/v1_8/agent-guide-qa/`
- fixture hygiene：未发现 `/Users`、`file://`、`cache_path`、`artifact_path`、`physical_path`、API key 或授权头。

## 风险与降级记录

| 项 | 结论 |
| --- | --- |
| 规格漂移风险 | MEDIUM |
| 虚假验收风险 | MEDIUM-HIGH |
| 主要原因 | Agent 自动验证不能替代人工内容质量审查 |
| 收敛措施 | 只声明 Agent-led 受限 smoke；不声明普通用户 UX ready 或 all-domain QA quality ready |
| provider 稳定性 | V1.5-D 曾出现瞬时 fallback，使用保守重试后通过；V1.8-C smoke 默认重试参数已上调 |

## 决策

ResearchNotebook V1.8-C Agent-led Guide / QA / Citation Validation is `PASS_LIMITED` for the approved AI digital human dataset.

下一阶段只能审计 V1.8-D Agent Studio Validation，不得直接进入 V1.8-E 或 V1.8-RC。
