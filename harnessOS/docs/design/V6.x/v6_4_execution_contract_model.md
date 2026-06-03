# V6-4 Execution Contract Model

文档状态：V6-4 contract model / pre-implementation audit input。本文定义 DTO 和字段合同，不实现代码。

## 1. V6ProductionExecutionEnvelope

Common required fields:

```text
envelope_id
operation
source
actor_type
tenant_id
workspace_id
project_id
app_id
actor_id
human_authorization_ref
authorization_expires_at
target_refs
payload_refs
credential_decision_ref
credential_lease_id
provider_profile_id
approval_gate_decision_ref
kill_switch_decision_ref
timeout_policy_ref
idempotency_key
request_id
correlation_id
created_at
```

Conditional actor fields:

```text
actor_type=human_user:
  requires user_id
  service_account_id optional / null

actor_type=service_account_with_human_authorization:
  requires service_account_id
  requires human_authorization_ref
  requires authorization_subject_actor_id or user_id as authorizing human
```

Rules:

```text
additionalProperties=false
source must be product_console or approved_api
actor_type must be human_user or service_account_with_human_authorization
source=agent denied
human_authorization_ref required for all durable mutation
payload_refs must be redacted refs only
target_refs are operation-specific
```

## 2. Operation Target Refs

```text
workflow.instance.start:
  workflow_instance_id

station.rerun:
  workflow_instance_id
  station_id
  station_run_id

artifact.write:
  workflow_instance_id
  artifact_id or output_artifact_target_id

quality.evaluation.create:
  workflow_instance_id
  quality_evaluation_id or station_id or artifact_id
```

## 3. V6ControlledExecutionResult

Required fields:

```text
result_id
operation
status
policy_decision
capability_decision
runtime_result_ref
execution_evidence_ref
workflow_state_ref
blocked_reason
idempotent_replay
request_id
correlation_id
redaction_status
production_ready=false
pilot_slice_ready_for_review=true
```

Allowed statuses:

```text
applied_limited_runtime_slice
blocked
idempotent_replay
```

## 4. V6ExecutionEvidence

Required fields:

```text
execution_evidence_id
operation
tenant_id
workspace_id
project_id
app_id
target_refs
actor_type
actor_id
source
user_confirmed
human_authorization_ref
approval_gate_decision_ref
policy_decision
capability_decision
credential_decision_ref
runtime_result_ref
idempotency_key
rollback_descriptor_ref
kill_switch_decision_ref
timeout_policy_ref
incident_timeline_ref
audit_export_ref
correlation_id
request_id
redaction_status
created_at
```

Evidence rules:

```text
allow path creates execution evidence
deny path creates denial audit event, not successful execution evidence
idempotent replay returns prior execution reference
raw secret / raw prompt / raw artifact content forbidden
```

## 5. ApprovalGateDecision

Required fields:

```text
approval_gate_decision_ref
operation
risk_level
requires_user_confirmation
requires_approval_gate
policy_decision
approved_by_actor_id
approved_at
expires_at
target_refs
correlation_id
```

Rules:

```text
artifact.write risk_level >= medium
quality.evaluation.create risk_level >= medium
approval gate must be checked before runtime mutation
```

## 6. KillSwitchDecision

Required fields:

```text
kill_switch_decision_ref
tenant_id
workspace_id
operation
checked_at
checked_by
policy_ref
correlation_id
checked_before_runtime_action=true
decision
reason
```

Allowed decisions:

```text
allow
deny
```

## 7. IdempotencyKeyContract

Required fields:

```text
idempotency_key
operation
tenant_id
workspace_id
actor_id
target_refs_hash
prior_runtime_result_ref
prior_execution_evidence_ref
created_at
expires_at
```

Rule:

```text
same idempotency_key with same operation/scope/target returns prior execution reference
same idempotency_key with different operation/scope/target is denied
```
