# ResearchNotebook V1.5-0 Plan Audit

日期：2026-05-26

## 当前文档状态

SUPERSEDED_BY_REVALIDATION。

本文件保留为 V1.5 早期历史审计记录。当时真实 LLM provider 尚未确认，因此 V1.5-A 被判定为 BLOCKED。当前有效状态以以下文档为准：

- `docs/design/V1.5/v1_5_revalidation_report.md`
- `docs/design/V1.5/v1_5_current_gap_analysis.md`
- `docs/design/V1.5/v1_5_rc_quality_release_handoff.md`

截至 2026-05-28，V1.5 已完成收紧复验：provider、Guide、Studio、QA 和 ChromeCLI / Manual E2E 均为 PASS_LIMITED。后续 V1.6 entry gate 不应再把本文件中的历史 BLOCKED 作为当前状态。

## 审计结论

V1.5-0 计划文档：PASS。

V1.5-A 实质开发：BLOCKED，等待用户确认或补齐真实 LLM provider 条件。

## 已确认

- PRD Phase 1 规格已映射到 V1.5。
- 真实验收数据已确认：`Desktop/技术分享/11-数字人`。
- V1.4 当前状态为 PASS_LIMITED，不伪装成 AI quality ready。
- V1.5 必须使用真实 LLM，不允许 deterministic fallback 冒充 AI 输出。

## 阻塞点

当前仓库未发现已冻结的 Claude / LLM provider 合同、认证配置、health probe 或模型调用 smoke。

因此，如果直接进入 V1.5-B/C/D，会产生重大虚假验收风险：

- Guide 可能仍是模板输出。
- Studio 可能仍是模板输出。
- 无法证明 AI 输出质量。
- 无法证明 PRD 中 “AI 驱动” 已满足。

## 风险评估

规格漂移风险：HIGH

原因：PRD 明确是 AI 驱动研究助手，且技术栈中指定 Claude API；当前只具备确定性合同和模板输出。

虚假验收风险：HIGH

原因：没有真实 LLM provider smoke 时继续开发 AI Guide / Studio，极易把模板输出当成 AI quality ready。

## 停止条件

按用户规则，风险为 HIGH，必须停止自动推进，等待用户确认下一步。

## 进入 V1.5-A 的最低条件

用户需要确认以下至少一种路径：

1. 提供可用 Claude / Anthropic API 环境变量和模型名。
2. 明确允许先做 V1.5-A provider contract shell，但不声明 AI quality ready。
3. 明确改用本地 OpenHarness / LightRAG 模型，并提供启动方式和 health check。
4. 明确 V1.5 暂不接真实 LLM，只继续做 UX hardening；但这将不满足 AI quality ready。

## 审计意见

建议下一步不要直接写 AI Guide / Studio 生成逻辑。

建议先执行：

```text
V1.5-A AI Provider Contract Enablement
```

但必须由用户确认 provider 路径后再进入实质开发。
