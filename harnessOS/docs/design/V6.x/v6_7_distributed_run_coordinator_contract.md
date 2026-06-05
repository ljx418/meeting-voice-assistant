# V6-7 Distributed Run Coordinator Contract

文档状态：V6-7 complete / ready for review contract。

## Coordinator Responsibilities

```text
create distributed run plan from approved workflow instance
assign serial and parallel station work to tenant-bound workers
record state checkpoint before worker dispatch
record assignment, timeout, retry and recovery events
preserve old attempts during retry
emit incident timeline refs
```

## Required Inputs

```text
tenant_id
workspace_id
workflow_instance_id
run_id
station_ids
policy_decision_ref
credential_decision_ref
correlation_id
request_id
```

## Required Outputs

```text
distributed_run_id
checkpoint_refs
worker_assignment_refs
attempt_refs
artifact_lineage_refs
incident_timeline_ref
audit_ref
```

## Failure Modes

```text
worker_lost -> recover_or_mark_failed
timeout -> retry_or_mark_failed
wrong_tenant_worker -> deny_assignment
credential_decision_missing -> deny_assignment
policy_decision_missing -> deny_assignment
```
