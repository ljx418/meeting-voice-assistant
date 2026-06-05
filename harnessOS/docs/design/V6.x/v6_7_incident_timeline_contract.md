# V6-7 Incident Timeline Contract

文档状态：V6-7 complete / ready for review contract。

## Required Timeline Events

```text
distributed_run_created
worker_assignment_created
worker_started
checkpoint_written
worker_timeout
worker_lost
retry_scheduled
attempt_created
attempt_failed
attempt_recovered
artifact_lineage_recorded
distributed_run_completed
distributed_run_marked_failed
```

## Required Fields

```text
tenant_id
workspace_id
run_id
workflow_instance_id
station_id
station_run_id
attempt_id
worker_id
event_type
correlation_id
request_id
audit_ref
created_at
```

Incident timeline is a read model and must not construct runtime truth.
