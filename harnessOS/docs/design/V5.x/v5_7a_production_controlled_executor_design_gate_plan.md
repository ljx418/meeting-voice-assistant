# V5-7A Production Controlled Executor Design Gate Plan

文档状态：V5-7A planning package。本文只做 production controlled executor 设计门禁，不实现生产执行器。

## Stage Goal

V5-7A 将 production controlled executor 纳入 V5 路线，但只冻结设计和验收边界：

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
V5-7A complete: production controlled executor design gate ready for review.
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

V5-7A must expand these names into auditable contracts:

```text
docs/design/V5.x/v5_7a_policy_matrix.md
docs/design/V5.x/v5_7a_execution_envelope.schema.json
docs/design/V5.x/v5_7a_runtime_action_allowlist.json
docs/design/V5.x/v5_7a_sandbox_input_descriptor.schema.json
docs/design/V5.x/v5_7a_rollback_descriptor.schema.json
docs/design/V5.x/v5_7a_kill_switch_decision.schema.json
docs/design/V5.x/v5_7a_execution_evidence.schema.json
```

These contracts are design artifacts only. They are not executable runtime code, not BFF route definitions, and not permission to start V5-7B.

## Minimum Action Allowlist Candidate

V5-7A may define but not execute:

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

## Runtime Action Allowlist Requirements

Each candidate action must define:

```text
risk_level
requires_user_confirmation
requires_approval_gate
rollback_strategy
idempotency_required
audit_required
incident_timeline_required
```

`artifact.write` and `quality.evaluation.create` must be at least medium risk and must require rollback or correction design. They must not be treated as low-risk default writes.

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
design allows source=agent durable mutation
design allows unrestricted connector.call
design allows unrestricted external_llm.call
design treats artifact.write or quality.evaluation.create as low risk by default
design omits incident timeline or audit export refs
```

## No False Green

V5-7A is a design gate only. It must not prove production controlled executor ready, Agent executor ready, autonomous workflow editing ready, complete Workflow Studio ready, production-ready external app support, or distributed multi-Agent runtime ready.
