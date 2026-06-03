# Historical V5-7 Attempt History / Lineage Model

文档状态：historical / superseded。Distributed multi-Agent runtime 已移动到 V5-8；本文不再是当前控制计划。

## Attempt History

```text
attempt_id
station_id
workflow_instance_id
worker_id
status
started_at
completed_at
error_ref
input_artifact_refs
output_artifact_refs
policy_decision
credential_decision
```

## Artifact Lineage

```text
artifact_id
producer_station_id
producer_attempt_id
input_artifact_refs
lineage_depth
quality_refs
evidence_refs
```

## Acceptance Rules

```text
lineage survives retry
lineage records producer attempt
failed attempt artifacts remain auditable
downstream stale state is explicit
```
