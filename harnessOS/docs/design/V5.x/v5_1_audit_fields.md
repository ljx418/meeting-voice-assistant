# V5-1 Audit Fields

文档状态：V5-1 pre-implementation planning。本文定义审计字段，不实现审计存储。

## 1. Required Audit Fields

Every production auth / tenant boundary decision must record:

```text
audit_event_id
created_at
request_id
correlation_id
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
user_id
service_account_id
agent_id
session_id
operation
target_resource_type
target_resource_id
policy_decision
scope_decision
risk_flags
denial_reason
redaction_status
evidence_ref
```

## 2. Redaction Rules

Audit records must not contain:

```text
capability_token
subscription_token
Authorization
Bearer
secret
raw_trace_payload
raw_artifact_content
raw_connector_payload
raw prompt
upstream signed URL
```

## 3. Evidence Linkage

Audit records should link to:

```text
workflow_spec_id
workflow_instance_id
station_run_id
artifact_id
evidence_id
report_id
handoff_id
```

These target refs must be explicit typed fields, not arbitrary objects.

## 4. No False Green

No False Green：audit field design does not prove production observability / audit export ready. V5-3 must prove retention, export, metrics, alerting, and incident timeline separately.
