# V5-2 Audit Fields

文档状态：V5-2 implementation planning。

## 1. Provider Invocation Evidence

```text
provider_invocation_evidence_id
provider_profile_id
provider
model_ref
tenant_id
workspace_id
project_id
app_id
operation
capability_ref
input_artifact_refs
output_artifact_refs
prompt_template_ref
redacted_input_summary_ref
redacted_output_summary_ref
policy_decision
credential_decision
runtime_result_ref
request_id
correlation_id
redaction_status
created_at
created_by
```

## 2. Credential Lifecycle Evidence

```text
credential_event_id
credential_ref_id
provider_profile_id
operation
source
actor_type
actor_id
user_confirmed
tenant_id
workspace_id
project_id
app_id
policy_decision
risk_flags
previous_status
next_status
request_id
correlation_id
redaction_status
created_at
```

## 3. Redaction Requirements

No False Green：audit evidence must not include:

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

## 4. Cross-References

Audit evidence must link to:

```text
IdentityContext
ProviderProfileDTO
CredentialReferenceDTO
Runtime Report
Evidence Chain
```

