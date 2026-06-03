# V6-5 Agent Governance Architecture Delta

文档状态：V6-5 detailed planning / architecture delta。本文定义 V6-5 架构增量，不授权 runtime implementation。

## 1. Current Boundary

V6-5 继承 V6-1 到 V6-4 的边界：

```text
tenant / workspace / project / app scope required
credential refs are redacted
audit export is read-only
V6-4 controlled executor accepts only limited action set
source=agent direct durable mutation is denied
```

## 2. New Plane Delta

新增 Agent Governance Plane 的实现切片：

```text
Mission Console / Review Console
 -> Redacted Runtime Context
 -> MiniMax Intent Generator
 -> AgentExecutionIntent
 -> AgentCapabilityDecision Resolver
 -> AgentExecutionHandoff
 -> Human Confirmation / Approval Gate
 -> V6-4 Controlled Executor
```

## 3. Runtime Truth Boundary

Agent Governance Plane 不得直接写入：

```text
WorkflowDraft
WorkflowVersion
WorkflowInstance
StationRun
Artifact
QualityEvaluation
Credential lifecycle state
Audit export package
```

Agent Governance Plane 只能产生 read-model intent、decision 和 handoff evidence。

## 4. MiniMax Boundary

MiniMax 只能接收：

```text
redacted runtime status summary
redacted station failure summary
operation allowlist summary
target_refs without raw payload
policy hint refs
```

MiniMax 不得接收：

```text
raw credential
raw prompt
raw artifact content
raw connector payload
capability token
subscription token
Authorization header
Bearer token
```

## 5. Handoff Boundary

AgentExecutionHandoff 可以打开 human confirmation UX，但不能执行 mutation。只有用户确认后，系统才能创建 `human_authorization_ref` 并交给 V6-4 controlled executor。

## 6. No False Green Boundary

V6-5 architecture delta 不证明：

```text
Agent executor ready
autonomous workflow editing ready
production controlled executor ready
full multi-Agent orchestration ready
```
