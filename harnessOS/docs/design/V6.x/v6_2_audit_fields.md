# V6-2 Credential / Provider Audit Fields

文档状态：V6-2 implementation-ready audit field contract。

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
provider_profile_id
provider
model_ref
capability_ref
credential_ref_id
credential_lease_id
audience
operation
policy_decision
credential_decision
lease_decision
provider_config_source
input_artifact_refs
output_artifact_refs
prompt_template_ref
redacted_input_summary_ref
redacted_output_summary_ref
runtime_result_ref
redaction_status
denial_reason
```

## Sensitive Field Ban

```text
api_key
Authorization
Bearer
secret value
raw prompt
raw_trace_payload
raw_artifact_content
raw_connector_payload
raw_provider_payload
upstream signed URL
```

## Evidence Linkage

Provider invocation evidence must link to:

```text
provider_profile_id
credential_ref_id
credential_lease_id
input_artifact_refs
output_artifact_refs
runtime_result_ref
```

## No False Green

V6-2 audit fields do not prove V6-3 audit export ready.
