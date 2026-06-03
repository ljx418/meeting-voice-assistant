# V5-8 Distributed State Recovery Model

文档状态：V5-8 planning package；implementation has not started。

## Recovery Fields

```text
run_id
workflow_instance_id
station_id
attempt_id
worker_id
lease_id
checkpoint_ref
last_heartbeat_at
recovery_status
recovered_by
```

## Required Scenarios

```text
worker lost
lease expired
station retry
partial artifact write
downstream stale propagation
coordinator restart
```

## Acceptance Rules

```text
old attempt remains visible
new attempt has separate attempt_id
recovery event is audited
artifact lineage preserves producer attempt
```

