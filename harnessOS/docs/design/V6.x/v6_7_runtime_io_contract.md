# V6-7 Runtime I/O Contract

文档状态：V6-7 complete / ready for review I/O contract。本文定义 V6-7 runtime pilot 的输入输出合同；仍不创建 production route。

## DistributedRunStartInput

```text
tenant_id
workspace_id
project_id
app_id
workflow_instance_id
run_id
station_graph_ref
source
actor_type
human_authorization_ref
policy_decision_ref
credential_decision_ref
idempotency_key
correlation_id
request_id
```

Allowed source:

```text
product_console
approved_api
```

Forbidden:

```text
source=agent direct durable mutation
unrestricted connector.call
unrestricted external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
```

## DistributedRunResult

```text
distributed_run_id
workflow_instance_id
run_state
branch_states
worker_assignment_refs
checkpoint_refs
attempt_refs
artifact_lineage_refs
incident_timeline_ref
audit_ref
redaction_status
```

## WorkerAssignmentInput

```text
worker_id
tenant_id
workspace_id
project_id
app_id
station_id
station_run_id
attempt_id
credential_decision_ref
policy_decision_ref
checkpoint_ref
correlation_id
request_id
```

## RecoveryInput

```text
distributed_run_id
station_id
station_run_id
failed_attempt_id
failure_type
recovery_strategy
replacement_worker_id
previous_checkpoint_ref
policy_decision_ref
credential_decision_ref
correlation_id
request_id
incident_timeline_ref
```

## Redaction Boundary

I/O contracts may contain redacted refs only. They must not contain raw secret, raw prompt, raw connector payload, raw artifact content, raw trace payload, Authorization header, Bearer token, API key, or signed URL.

## Idempotency

Duplicate `idempotency_key` for the same operation must return the prior distributed_run_id or recovery decision ref. It must not create duplicate attempts.
