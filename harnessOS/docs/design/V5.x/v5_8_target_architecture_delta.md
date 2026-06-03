# V5-8 Target Architecture Delta

文档状态：V5-8 planning package；implementation has not started。

## Logical Components

```text
DistributedRunCoordinator
AgentWorkerRegistry
DistributedStateStore
AttemptHistoryStore
ArtifactLineageService
DistributedRecoveryManager
TenantRuntimeIsolationGuard
ProviderCredentialBoundary
```

## Data Flow

```text
WorkflowVersion
 -> DistributedRunCoordinator
 -> AgentWorkerRegistry
 -> Agent station execution
 -> AttemptHistoryStore
 -> ArtifactLineageService
 -> DistributedRecoveryManager
 -> Runtime Report / Evidence Chain / Audit Export
```

## Boundary

```text
Agent worker cannot bypass V5-1 tenant boundary
Agent worker cannot bypass V5-2 credential boundary
Distributed events cannot become runtime truth without store validation
```

