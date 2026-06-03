# V5-4A Agent Executor Design & Safety Gate PRD

文档状态：V5-4A core slice implemented for review。本文只定义安全门禁，不实现 Agent executor。

## Stage Goal

V5-4A 建立 Agent executor 进入前的安全设计门禁：

```text
policy matrix
capability decision
approval gate
executor sandbox boundary
kill switch
runtime evidence
```

## Acceptance Criteria

```text
all executor candidate operations have policy classification
agent_executable=false remains default for durable mutation
high-risk action is approval-gated
kill switch is defined and auditable
sandbox boundary rejects raw token / raw connector payload
runtime evidence schema exists
```

## No False Green

No False Green：V5-4A 不证明 Agent executor ready、controlled executor ready、production controlled executor ready 或 autonomous workflow editing ready。

## Current Implementation Scope

```text
Implemented:
- ExecutorPolicyMatrix
- CapabilityDecisionService
- ApprovalGatePlanner
- ExecutorSandboxBoundary
- KillSwitchRegistry
- RuntimeEvidenceContract shape

Not implemented:
- Agent executor route
- source=agent durable mutation
- controlled executor runtime
- production kill-switch route
- production rollback route
```
