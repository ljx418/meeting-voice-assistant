# V6-4 Controlled Executor Architecture Delta

文档状态：V6-4 architecture delta / pre-implementation audit input。本文定义架构增量，不实现 runtime。

## 1. Architecture Delta

V6-4 在 V6 目标架构中补齐 `Production Controlled Execution Plane` 的生产试点切片。

```text
V6-1 Identity And Tenant Control Plane
  -> V6-4 Production Execution Envelope

V6-2 Credential And Provider Lifecycle Plane
  -> V6-4 CredentialDecisionRef / CredentialLeaseRef only

V6-4 Policy And Capability Gate
  -> action allowlist
  -> human authorization
  -> approval gate
  -> kill switch
  -> idempotency

V6-4 Pilot Runtime State Store
  -> workflow instance state
  -> station attempt history
  -> artifact versions
  -> quality evaluations

V6-3 Observability And Audit Export Plane
  -> audit events
  -> incident timeline refs
  -> audit export refs
```

## 2. Runtime Truth Boundary

V6-4 pilot runtime state is the only V6-4 mutation target.

V6-4 不得直接写：

```text
WorkflowDraft
WorkflowVersion
WorkflowStore
StationRun production truth store
ArtifactRegistry production truth store
Gateway internal object
EventBridge payload
Drawio / Blueprint
HTML Runtime Report
Evidence Chain
```

## 3. Required Dependencies

### V6-1 Identity

每个 request 必须继承：

```text
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
user_id or service_account_id
request_id
correlation_id
```

### V6-2 Credential Boundary

V6-4 只保存 redacted refs：

```text
credential_decision_ref
credential_lease_id
provider_profile_id
```

V6-4 不读取 raw secret，不发起 unrestricted provider invocation。

### V6-3 Audit

allow / deny / replay / kill switch / rollback 都必须生成 audit event 或 evidence ref：

```text
policy_decision
capability_decision
runtime_result_ref
incident_timeline_ref
audit_export_ref
redaction_status
```

## 4. Source And Actor Boundary

Allowed:

```text
source=product_console, actor_type=human_user
source=approved_api, actor_type=service_account_with_human_authorization
```

Denied:

```text
source=agent
actor_type=agent
autonomous workflow editing
unrestricted Agent execution
production admin override without human_authorization_ref
```

## 5. External App Boundary

V6-4 默认不启用 external app source。

如果未来 action 来自 external app，必须先通过 V6-6：

```text
tenant-bound app registration
domain verification before origin allowlist
quota / rate limit denial evidence
offboarding revocation evidence
SDK cannot call internal runtime route directly
```

## 6. Failure And Recovery Architecture

```text
workflow.instance.start:
  idempotent duplicate returns prior runtime_result_ref

station.rerun:
  old attempt retained
  new attempt created
  downstream stale recorded

artifact.write:
  append new artifact version
  correction / retract uses new artifact ref, not overwrite

quality.evaluation.create:
  append new evaluation
  correction keeps previous score

kill switch:
  checked before runtime mutation
  denial emits audit event only
```

## 7. No False Green Boundary

V6-4 架构增量只证明有限生产试点切片 ready for review，不证明：

```text
production controlled executor ready
Agent executor ready
distributed multi-Agent runtime ready
production-ready external app support
complete Workflow Studio ready
```
