# V5-3 Observability Event Model

文档状态：V5-3 implementation planning。

## Event Families

```text
auth.scope.denied
credential.lifecycle.changed
provider.invocation.recorded
workflow.operation.requested
workflow.operation.completed
workflow.operation.failed
audit.export.requested
audit.export.completed
alert.triggered
incident.timeline.updated
```

## Required Fields

```text
event_id
event_type
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
request_id
correlation_id
operation
target_refs
policy_decision
redaction_status
created_at
```

## Forbidden Fields

No False Green：event payload 禁止包含：

```text
capability_token
subscription_token
Authorization
Bearer
secret
API key
raw prompt
raw_trace_payload
raw_artifact_content
raw_connector_payload
upstream signed URL
```

