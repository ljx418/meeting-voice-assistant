# V6-7 Worker Lifecycle Model

文档状态：V6-7 complete / ready for review model。本文定义 worker 生命周期和边界，当前已由 pilot runtime slice 验证。

## Worker Identity Requirements

Every worker must include:

```text
worker_id
tenant_id
workspace_id
project_id
app_id
worker_type
explicit_tenant_binding=true
credential_decision_ref
policy_decision_ref
created_at
audit_ref
```

Worker identity must not be reused across tenants without an explicit binding record. Cross-tenant reuse without binding is denied.

## Lifecycle States

```text
registered: worker descriptor exists and is tenant-bound
available: worker can be assigned after policy and credential checks
assigned: worker is bound to workflow_instance_id / station_id / station_run_id
running: worker has an active attempt
lost: heartbeat or checkpoint is missing
timeout: timeout policy fired
recovered: replacement or resumed worker completed recovery
failed: worker cannot recover and station remains failed
released: worker is no longer assigned to the station attempt
```

## Assignment Requirements

Worker assignment requires:

- tenant_id / workspace_id / project_id / app_id match.
- source is `product_console` or `approved_api`.
- source=agent direct assignment denied.
- credential_decision_ref present and scoped to the worker action.
- policy_decision_ref present and scoped to the station operation.
- human_authorization_ref inherited when assignment leads to durable runtime action.

## Denial Cases

```text
worker_wrong_tenant_denied
worker_cross_tenant_reuse_without_binding_denied
worker_missing_credential_decision_denied
worker_missing_policy_decision_denied
source_agent_worker_assignment_denied
worker_assignment_without_checkpoint_denied
```

## Evidence Requirements

Each assignment and lifecycle transition must record:

```text
worker_id
station_id
station_run_id
attempt_id
policy_decision_ref
credential_decision_ref
correlation_id
request_id
incident_timeline_ref
audit_ref
```
