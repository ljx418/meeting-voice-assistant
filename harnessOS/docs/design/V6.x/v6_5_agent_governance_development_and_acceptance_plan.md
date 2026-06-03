# V6-5 Governed Agent Execution Intent Pilot Development And Acceptance Plan

文档状态：V6-5 complete / ready for review。本文记录 V6-5 开发与验收门槛及完成边界。

## Allowed Claim

```text
V6-5 complete: governed Agent execution intent pilot gate ready for review.
```

## High-Risk Gate

V6-5 需要人工 high-risk proceed decision。没有人工确认不得进入实现。

Current decision:

```text
current_decision=V6_5_COMPLETE_READY_FOR_REVIEW
human_high_risk_proceed_decision_recorded=true
v6_5_runtime_implementation_allowed=true
```

## Goal

把 Agent 从 propose / explain / handoff 扩展到受治理 execution intent / handoff，但不授予 Agent 直接持久变更权限。

## Non-Goals

```text
Agent executor ready
autonomous workflow editing ready
full multi-Agent orchestration ready
```

## Development Scope

- AgentExecutionIntent：Agent 只能表达意图，不直接执行。
- AgentCapabilityDecision：根据 policy、capability、tenant、credential、risk 生成 allow/deny。
- AgentExecutionHandoff：转给用户确认、审批或 Review Console。
- AgentMutationDenialEvidence：记录 source=agent direct mutation denial。
- MiniMaxIntentInvocationEvidence：记录真实 MiniMax intent 生成证据，缺少 MiniMax key 时 V6-5 只能 BLOCKED。

## Detail Design Documents

```text
docs/design/V6.x/v6_5_agent_governance_prd.md
docs/design/V6.x/v6_5_agent_governance_architecture_delta.md
docs/design/V6.x/v6_5_agent_execution_intent_contract.md
docs/design/V6.x/v6_5_agent_policy_matrix.md
docs/design/V6.x/v6_5_minimax_intent_invocation_model.md
docs/design/V6.x/v6_5_test_matrix.md
docs/design/V6.x/v6_5_pre_implementation_audit.md
```

## PR Slices

```text
PR1 AgentExecutionIntent contract
PR2 AgentCapabilityDecision resolver
PR3 AgentExecutionHandoff to Review Console and Manual Confirmation UX
PR4 source=agent mutation denial evidence
PR5 evidence package, redaction scan, claim scan
```

PR execution completed within the documented high-risk authorization boundary.

## Architecture Delta

```text
Agent Panel / Mission Console
 -> AgentExecutionIntent read model
 -> AgentCapabilityDecision
 -> AgentExecutionHandoff
 -> Human Confirmation / Approval Gate
 -> V6-4 controlled executor only after human authorization
```

Agent Governance Plane cannot write WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun directly.

## Acceptance Gates

- Agent auto apply / publish / run / rerun denied。
- MiniMax real invocation evidence exists with provider/model/provider_config_source。
- Agent execution intent 必须变成 human-confirmed handoff。
- high-risk action 必须 approval-gated。
- Agent 无法读取 raw credential、raw prompt、raw artifact content。
- source=agent direct mutation denied。
- Evidence Chain 记录 agent_id、session_id、policy_decision、capability_decision。
 
If `MINIMAX_API_KEY` is missing or placeholder-only, V6-5 must be BLOCKED and cannot be marked PASS.

## Focused Tests

```text
tests/test_v6_5_agent_execution_intent.py
tests/test_v6_5_agent_capability_decision.py
tests/test_v6_5_agent_handoff.py
tests/test_v6_5_agent_mutation_denial.py
tests/test_v6_5_no_false_green.py
```

## Evidence Package

```text
docs/design/V6.x/evidence/v6-5-agent-governance/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  redaction-scan.md
  raw/minimax-intent-invocation.json
  raw/agent-intent.json
  raw/capability-decision.json
  raw/handoff.json
  raw/source-agent-denial.json
  raw/
```

## No False Green Stop Conditions

- Mission Console 或 Agent Panel 被描述为 Agent executor ready。
- Agent 可绕过 user confirmation。
- Agent 可读取 raw secret 或 raw artifact content。
- Forbidden claim scan 失败。
