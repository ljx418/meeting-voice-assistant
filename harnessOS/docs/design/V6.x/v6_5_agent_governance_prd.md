# V6-5 Governed Agent Execution Intent Pilot PRD

文档状态：V6-5 complete / ready for review。本文定义 V6-5 产品规格；runtime implementation 已由用户 high-risk proceed decision 授权后完成，并由 completion note 与 evidence package 闭环。

## 1. Current Decision

```text
current_decision=COMPLETE_READY_FOR_REVIEW
human_high_risk_proceed_decision_recorded=true
MiniMax real invocation is required for V6-5 PASS
```

V6-5 进入实现前曾要求完成本 PRD、架构增量、合同、测试矩阵和实现前审计闭环，并由用户单独记录 high-risk proceed decision。当前这些前置门禁已由 completion note 和 evidence package 取代为完成状态。V6-5 仍不证明 Agent executor ready。

## 2. Product Goal

V6-5 的目标是把 Agent 从 propose / explain / handoff 推进到受治理的 execution intent / handoff：

```text
MiniMax Agent observes redacted runtime/evidence refs
 -> generates AgentExecutionIntent
 -> AgentCapabilityDecision validates intent against policy
 -> AgentExecutionHandoff waits for human confirmation / approval
 -> V6-4 controlled executor may run only after human authorization
```

## 3. Target User Experience

用户在 Mission Console / Review Console 中看到 Agent 对失败、重跑、写入 artifact 或 quality evaluation 的建议。Agent 可以解释建议并生成 execution intent，但所有 durable action 都必须转成人类确认的 handoff。

## 4. In Scope

```text
AgentExecutionIntent contract
AgentCapabilityDecision resolver
AgentExecutionHandoff contract
MiniMax-backed intent generation evidence
source=agent direct durable mutation denial
redacted runtime/evidence refs only
human-confirmed handoff to V6-4 controlled executor
```

## 5. No False Green Non-Goals

V6-5 不证明：

```text
Agent executor ready
autonomous workflow editing ready
full multi-Agent orchestration ready
production controlled executor ready
complete Workflow Studio ready
```

## 6. Acceptance

V6-5 PASS 需要：

```text
MiniMax invocation evidence exists with provider/model/provider_config_source
AgentExecutionIntent is generated from redacted inputs only
policy resolver independently validates MiniMax intent
source=agent direct durable mutation is denied
human confirmation is required before V6-4 controlled executor handoff
raw credential / raw prompt / raw artifact content does not leak
No False Green claim scan passes
```

缺少 `MINIMAX_API_KEY` 或等价 provider credential 时，V6-5 必须标记 BLOCKED，不能标记 PASS。
