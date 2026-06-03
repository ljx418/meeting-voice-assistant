# V5-8 Development And Acceptance Plan

文档状态：V5-8 planning and acceptance plan。本文定义后续开发与验收，不直接实现 runtime。

## Stage Goal

V5-8 目标是生产级 distributed multi-Agent runtime 的规划和后续实现门禁：

```text
distributed run coordination
parallel / serial multi-agent runtime
distributed state recovery
attempt history retention
artifact lineage at scale
tenant / policy / credential boundary on every worker action
observability and audit export for distributed runs
```

## PR Slices

### V5-8A Distributed Runtime Planning Gate

交付：

```text
V5-8 PRD accepted
architecture delta accepted
state recovery model accepted
attempt history / lineage model accepted
tenant / policy / credential boundary accepted
test matrix accepted
No False Green guard accepted
```

允许声明：

```text
V5-8A complete: distributed multi-Agent runtime planning gate ready for review.
```

### V5-8B Distributed Run Coordination Slice

目标：

```text
DistributedRunCoordinator
AgentWorkerRegistry
worker assignment
run state transitions
coordinator restart recovery
```

验收：

```text
coordinator restart recovers run state
lost worker is detected
retry appends attempt
old attempt remains visible
tenant scope checked before worker assignment
```

### V5-8C Artifact Lineage And Attempt Recovery Slice

目标：

```text
AttemptHistoryStore
ArtifactLineageService
producer attempt tracking
lineage recovery after retry
```

验收：

```text
artifact lineage preserves producer attempt
rerun creates new attempt
old attempt retained
downstream stale/recovery visible
Runtime Report shows attempt lineage
```

### V5-8D Policy / Credential / Observability Slice

目标：

```text
TenantRuntimeIsolationGuard
ProviderCredentialBoundary
distributed audit event recording
incident timeline
audit export package
```

验收：

```text
cross-tenant worker denied
provider call requires credential boundary
source=agent direct durable mutation denied
distributed audit export includes worker/action/recovery evidence
redaction passes
```

### V5-8E Distributed Runtime Acceptance Package

目标：

```text
end-to-end serial multi-agent scenario
end-to-end parallel multi-agent scenario
failure/recovery scenario
audit export scenario
No False Green scan
```

允许声明：

```text
V5-8 complete: distributed multi-Agent runtime slice ready for review.
```

No False Green：该声明仍不等于：

```text
full multi-Agent orchestration ready
production-ready external app support
complete Workflow Studio ready
autonomous workflow editing ready
```

## Test Plan

Focused tests:

```text
./.venv/bin/python -m pytest tests/test_v5_8_*.py -q
```

Regression:

```text
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V5.x/v5_current_gap_analysis.drawio
```

## Stop Conditions

Stop if:

```text
source=agent durable mutation is required
V5-7B staging runtime is treated as production controlled executor ready
V4 dev/local multi-Agent evidence is treated as production distributed runtime
tenant boundary cannot be enforced for workers
credential boundary cannot be enforced for provider calls
attempt history cannot be retained
artifact lineage cannot preserve producer attempt
redaction fails
No False Green claim scan fails
```

## No False Green

V5-8 planning and implementation must keep these claims forbidden unless separately proven by full acceptance:

```text
distributed multi-Agent runtime ready
full multi-Agent orchestration ready
Agent executor ready
production controlled executor ready
production-ready external app support
complete Workflow Studio ready
autonomous workflow editing ready
```
