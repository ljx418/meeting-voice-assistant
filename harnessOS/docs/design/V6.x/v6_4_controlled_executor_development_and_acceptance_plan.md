# V6-4 Production Controlled Executor Runtime Development And Acceptance Plan

文档状态：V6-4 complete / ready for review。本文记录 V6-4 开发与验收门槛及完成边界。

## Allowed Claim

```text
V6-4 complete: limited production controlled executor pilot slice ready for review.
```

## High-Risk Gate

V6-4 需要人工 high-risk proceed decision。没有人工确认不得进入实现。

V6-4 继承 V5-7B 约束：approved_api cannot bypass human_authorization_ref；service_account_with_human_authorization cannot become Agent executor；artifact.write append-only；quality.evaluation.create append-only；kill switch checked before runtime action；idempotency duplicate returns prior execution ref。

## Goal

实现有限 production-controlled action set：

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

## Non-Goals

```text
production controlled executor ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
unrestricted connector.call
unrestricted external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
```

## Development Scope

- ProductionExecutionEnvelope：绑定 tenant、workspace、app、actor、human_authorization_ref、target_refs。
- RuntimeActionAllowlist：只允许四个初始 action。
- ApprovalGateDecision：artifact.write 和 quality.evaluation.create 至少 medium risk 且 approval-gated。
- KillSwitchDecision：runtime action 前必须检查。
- IdempotencyKeyContract：重复请求返回 prior execution reference。
- ExecutionEvidence：记录 policy_decision、capability_decision、runtime_result_ref、redaction_status。

## Detail Design Documents

```text
docs/design/V6.x/v6_4_controlled_executor_prd.md
docs/design/V6.x/v6_4_controlled_executor_architecture_delta.md
docs/design/V6.x/v6_4_execution_contract_model.md
docs/design/V6.x/v6_4_runtime_state_model.md
docs/design/V6.x/v6_4_action_allowlist_and_policy_matrix.md
docs/design/V6.x/v6_4_test_matrix.md
docs/design/V6.x/v6_4_pre_implementation_audit.md
```

## Implementation Entry Conditions

V6-4 runtime implementation entry conditions were satisfied before implementation:

```text
human high-risk proceed decision is recorded
V6-4 external design review accepted
V6-4 pre-implementation audit has no critical PRD drift
V6-4 test matrix accepted
evidence package structure accepted
No False Green claim scan passes
ExecutionEnvelope conditional actor fields clarified
```

Current state remains:

```text
V6-4 complete: limited production controlled executor pilot slice ready for review.
human_high_risk_proceed_decision_recorded=true
v6_4_runtime_implementation_allowed=true
```

## Acceptance Gates

- workflow.instance.start 必须 user_confirmed 或 human_authorization_ref。
- station.rerun 保留 old attempt、创建 new attempt、标记 downstream stale。
- artifact.write append-only，不静默覆盖。
- quality.evaluation.create append-only，不静默覆盖。
- source=agent durable mutation denied。
- kill switch denial 可审计。

## Evidence Package

```text
docs/design/V6.x/evidence/v6-4-controlled-executor/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  raw/
```

## Stop Conditions

- source=agent 可执行 durable mutation。
- executor 绕过 approval / confirmation / kill switch。
- connector.call 或 external_llm.call 无限制开放。
- Forbidden claim scan 失败。
- 人工 high-risk proceed decision 缺失。
