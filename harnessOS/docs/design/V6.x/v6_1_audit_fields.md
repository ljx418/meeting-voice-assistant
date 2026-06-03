# V6-1 Identity / Tenant Audit Fields

文档状态：V6-1 implementation-ready audit field contract。

## Required Audit Fields

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
service_account_scope_decision
identity_provider
identity_provider_status
identity_provider_evidence_scope
workflow_head_refs
risk_flags
denial_reason
redaction_status
evidence_ref
```

## Workflow Head Refs

Each allowed access should be projectable to:

```text
mission_console
workflow_blueprint
runtime_report
review_console
evidence_chain
workflow_spec_registry
```

## Sensitive Field Ban

Audit evidence must not contain:

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

## No False Green

V6-1 audit evidence does not prove V6-3 production observability / audit export ready.
