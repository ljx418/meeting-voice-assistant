# Historical V5-4D Production Controlled Executor Design Gate Plan

文档状态：historical / superseded。Production controlled executor 已按最新路线移动到 V5-7A / V5-7B，且必须在 V5-6 之后执行。本文不再是当前控制计划，仅保留历史审计上下文。

## Stage Goal

V5-4D 将 production controlled executor 纳入 V5 路线，但只冻结设计和验收边界：

```text
policy enforcement
tenant isolation
credential boundary
approval gate
runtime sandbox
timeout / kill switch
rollback / recovery
idempotency
audit retention / export
incident response
limited action allowlist
```

Allowed future claim, only after planning audit:

```text
V5-4D complete: production controlled executor design gate ready for review.
```

## P0 Boundary

```text
no production executor route
no production runtime worker
no Agent direct durable mutation
no unrestricted connector.call
no unrestricted external_llm.call
no production credential raw secret access
no direct WorkflowStore / WorkflowDraft / WorkflowVersion / StationRun write
no autonomous workflow editing
```

## Required Design Outputs

```text
ProductionControlledExecutorPolicyMatrix
ProductionExecutionEnvelope
TenantExecutionScopeGuard
CredentialAccessDecision
ApprovalGateDecision
SandboxInputDescriptor
RuntimeActionAllowlist
IdempotencyKeyContract
RollbackDescriptor
KillSwitchDecision
ExecutionEvidenceContract
IncidentTimelineRef
AuditExportRef
```

## Minimum Action Allowlist Candidate

V5-4D may define but not execute:

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

Excluded from initial production runtime:

```text
connector.call
external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
```

These excluded actions require separate approval policy, credential boundary, and incident response review before any production execution.

## Acceptance Criteria

```text
every candidate action has policy classification
source=agent direct execution denied
user_confirmed required for every durable mutation
high-risk action approval-gated
tenant / workspace / app scope checked before runtime action
credential refs only, no raw secrets
sandbox rejects raw payloads
kill switch checked before runtime action
idempotency key required
rollback descriptor required
execution evidence contract includes correlation_id / request_id / actor_id
audit export integration designed
incident timeline integration designed
No False Green claim scan passes
```

## Stop Conditions

```text
design requires source=agent direct mutation
design requires raw credential access
design bypasses tenant isolation
design bypasses approval gate for high-risk actions
design bypasses audit retention/export
design cannot define rollback or idempotency
design claims production controlled executor ready
```

## No False Green

V5-4D is a design gate only. It must not prove production controlled executor ready, Agent executor ready, autonomous workflow editing ready, complete Workflow Studio ready, production-ready external app support, or distributed multi-Agent runtime ready.
