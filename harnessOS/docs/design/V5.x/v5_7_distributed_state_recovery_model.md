# Historical V5-7 Distributed State Recovery Model

文档状态：historical / superseded。Distributed multi-Agent runtime 已移动到 V5-8；本文不再是当前控制计划。

文档状态：V5-7 implementation planning。

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
