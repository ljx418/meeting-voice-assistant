# V1.8-D Agent-Led Studio Output Validation Report

日期：2026-05-30

## 当前状态

`PASS_LIMITED`

本阶段新增并通过 Agent-led Studio output validation smoke，用于验证 Agent 在真实数字人资料基础上生成 Studio 四类轻量输出，并验证 citation 解析、Markdown / JSON export 和 fixture hygiene。

## 实现内容

| 项 | 状态 |
| --- | --- |
| Agent studio draft | IMPLEMENTED |
| Markdown import | IMPLEMENTED |
| PDF import | IMPLEMENTED |
| build/index polling | IMPLEMENTED |
| Studio Notes | IMPLEMENTED |
| Studio Study Guide | IMPLEMENTED |
| Studio Briefing Doc | IMPLEMENTED |
| Studio FAQ | IMPLEMENTED |
| section-level evidence refs | IMPLEMENTED |
| DocumentUnit resolution | IMPLEMENTED |
| EvidenceSpan resolution | IMPLEMENTED |
| Markdown export validation | IMPLEMENTED |
| JSON export validation | IMPLEMENTED |
| WorkflowRun / ValidationReport fixture | IMPLEMENTED |
| fixture path hygiene | PASS |

## 新增命令

```bash
npm run smoke:v1.8-agent-studio
```

## 验证范围

- 四类 Studio artifact 均真实生成。
- 每类 artifact 顶层 evidence_refs 非空。
- 每个 section 均有 evidence_refs。
- FAQ 每条答案有 citation 或明确未覆盖。
- 至少每类 artifact 的一条 citation 可解析到 DocumentUnit / EvidenceSpan。
- Markdown export 包含标题、summary、sections 和 citation metadata。
- JSON export 包含 `artifact_id`、`artifact_type`、`sections`、`evidence_refs`、`schema_version`、`exported_at`。
- export / fixtures 不含 raw local path、cache path、artifact physical path、API key、stack trace。

## 当前仍不可声明

- 普通用户 UX ready
- Studio 人工内容质量 ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- all-source-type Studio ready

## 已执行命令

```bash
npm run check
RN_V15_STUDIO_PROVIDER_MAX_ATTEMPTS=5 RN_V15_STUDIO_PROVIDER_RETRY_DELAY_MS=5000 npm run smoke:v1.5-c-studio
npm run smoke:v1.8-agent-studio
```

| 命令 | 结果 |
| --- | --- |
| `npm run check` | PASS |
| `RN_V15_STUDIO_PROVIDER_MAX_ATTEMPTS=5 RN_V15_STUDIO_PROVIDER_RETRY_DELAY_MS=5000 npm run smoke:v1.5-c-studio` | PASS_WITH_RETRY |
| `npm run smoke:v1.8-agent-studio` | PASS_LIMITED |

## 真实数据与 fixture

- 真实数据目录：`Desktop/技术分享/11-数字人`
- Markdown：数字人资料包中的行业概览与技术趋势资料
- PDF：AI 数字人产业发展报告
- fixture：`fixtures/real/v1_8/agent-studio/`
- export fixture：`export-notes.md/json`、`export-study_guide.md/json`、`export-briefing_doc.md/json`、`export-faq.md/json`
- fixture hygiene：未发现 `/Users`、`file://`、`cache_path`、`artifact_path`、`physical_path`、API key 或授权头。

## 风险与降级记录

| 项 | 结论 |
| --- | --- |
| 规格漂移风险 | LOW-MEDIUM |
| 虚假验收风险 | MEDIUM |
| provider 稳定性 | 第一次 V1.8-D smoke 出现 `response_schema_mismatch`，复跑通过；记录为 provider/schema 波动，不升级为人工质量 PASS |
| 收敛措施 | 只声明 Agent-led Studio scoped smoke；不声明 Studio 人工内容质量 ready |

## 决策

ResearchNotebook V1.8-D Agent-led Studio Output Validation is `PASS_LIMITED` for the approved AI digital human dataset.

下一阶段只能审计 V1.8-E Weak Frontend Shell，不得直接进入 V1.8-RC。
