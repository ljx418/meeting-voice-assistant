# V9 API And Service Boundary Spec

文档状态：V9 P0 API/service boundary plan / required before runtime implementation。

## 1. Purpose

本文件定义 V9 的服务边界，防止 Studio、Agent、terminal worker 或 browser 绕过 BFF / DTO / policy / evidence 边界直接写 runtime truth。

## 2. Service Planes

```text
WorkflowStudioBFF
MissionTuiBFF
AgentExecutionService
CapabilityResolverService
HumanAuthorizationService
ControlledExecutorService
OrchestrationCoordinatorService
TerminalWorkerService
EvidencePackageService
AuditExportService
```

## 3. Route Classes

Allowed read routes:

```text
GET /bff/v9/runtime-report
GET /bff/v9/evidence-chain
GET /bff/v9/workflow-blueprint
GET /bff/v9/studio-state
GET /bff/v9/audit-export
```

Proposal / handoff routes:

```text
POST /bff/v9/workflow-diff-proposal
POST /bff/v9/agent-execution-proposal
POST /bff/v9/manual-confirmation
POST /bff/v9/human-authorization-ref
POST /bff/v9/review-handoff
```

Representative request contract for `POST /bff/v9/human-authorization-ref`:

```text
tenant_id
workspace_id
project_id
app_id
operation
target_refs
authorization_subject_actor_id
allowed_sources
allowed_actor_types
expires_at
correlation_id
request_id
```

Representative response contract:

```text
human_authorization_ref
operation_hash
audit_ref
created_at
expires_at
redaction_status
```

Internal-only routes:

```text
POST /internal/v9/capability-resolver/evaluate
POST /internal/v9/controlled-executor/execute
POST /internal/v9/orchestration/dispatch
POST /internal/v9/evidence-package/record
```

Explicit browser denylist:

```text
/v1/rpc
/v1/events/subscribe
/v1/internal/runtime
/v1/internal/executor
/v1/internal/workflow-store
/v1/internal/station-run
/internal/v9/*
```

## 4. Mutation Rules

```text
source=agent can propose but cannot directly call durable mutation routes.
Every mutation route requires CapabilityResolver decision.
Durable mutation requires user_confirmed=true OR valid human_authorization_ref.
High-risk mutation additionally requires ApprovalGateDecision.
Studio can submit proposals or handoffs, not direct runtime truth writes.
Browser can only call BFF routes.
```

## 5. Explicitly Non-Existent Routes

```text
POST /bff/v9/agent-auto-execute
POST /bff/v9/auto-commit
POST /bff/v9/auto-push
POST /bff/v9/auto-deploy
POST /bff/v9/direct-workflow-store-write
POST /bff/v9/direct-station-run-write
POST /bff/v9/unrestricted-terminal-command
```

## 6. Acceptance Tests

```text
browser_direct_internal_route_denied
browser_direct_v1_rpc_denied
studio_direct_runtime_truth_write_denied
source_agent_mutation_route_denied
mutation_without_capability_decision_denied
durable_mutation_without_user_confirmation_or_human_authorization_denied
high_risk_mutation_without_approval_gate_denied
```

## 7. Error Codes

```text
SOURCE_AGENT_MUTATION_DENIED
MISSING_CAPABILITY_DECISION
MISSING_HUMAN_AUTHORIZATION
EXPIRED_HUMAN_AUTHORIZATION
WRONG_TENANT_SCOPE
APPROVAL_GATE_REQUIRED
KILL_SWITCH_DENIED
BROWSER_DIRECT_ROUTE_DENIED
RUNTIME_TRUTH_WRITE_DENIED
```
