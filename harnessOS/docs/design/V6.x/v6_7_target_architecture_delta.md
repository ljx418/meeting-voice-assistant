# V6-7 Target Architecture Delta

文档状态：V6-7 complete / ready for review architecture delta。

## Architecture Delta

```text
DistributedRunCoordinator
 -> WorkerAssignmentPolicy
 -> AgentWorkerRegistry
 -> DistributedStateCheckpoint
 -> AttemptHistoryStore
 -> ArtifactLineageService
 -> WorkerRecoveryDecision
 -> IncidentTimeline
 -> AuditExportPackage
```

## Boundary Requirements

```text
worker identity must be tenant-bound
worker identity must not be reused across tenants without explicit binding
credential decision must be applied per worker
policy boundary must be applied per worker
old attempts must be retained
retry must not overwrite old error
producer_attempt_id must be preserved in lineage
parallel branches must expose independent state
lost worker recovery must be auditable
```

## Runtime Truth Boundary

V6-7 read models and dashboards do not construct runtime truth. Runtime truth remains in workflow instance, station run, attempt history and artifact lineage stores.
