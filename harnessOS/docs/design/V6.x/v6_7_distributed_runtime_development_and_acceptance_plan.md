# V6-7 Distributed Multi-Agent Runtime Productization Development And Acceptance Plan

文档状态：V6-7 complete / ready for review。本文记录 V6-7 开发与验收门槛，当前已由 completion note 和 evidence package 闭环。

## Allowed Claim

```text
V6-7 complete: distributed multi-Agent runtime productization pilot slice ready for review.
```

## High-Risk Gate

V6-7 需要人工 high-risk proceed decision。没有人工确认不得进入实现。

Worker identity must be tenant-bound. Worker identity must not be reused across tenants without explicit binding.

Current implementation decision:

```text
V6-7 implementation completed after human high-risk proceed decision.
Allowed claim remains pilot slice ready for review only.
Forbidden: V6-9 final acceptance execution before V6-8 evidence package exists.
```

## Goal

把 V5-8 bounded distributed runtime slice 推进为生产试点级分布式多 Agent 运行时产品化切片。

## Non-Goals

```text
distributed multi-Agent runtime ready
full multi-Agent orchestration ready
Agent executor ready
production controlled executor ready
```

## Development Scope

- DistributedRunCoordinator：协调 serial / parallel station。
- AgentWorkerRegistry：记录 worker identity、tenant scope、explicit tenant binding、credential decision。
- DistributedStateCheckpoint：记录可恢复状态。
- AttemptHistoryStore：保留 old attempts、new attempts、error attempts。
- ArtifactLineageService：记录 producer_attempt_id、input/output refs。
- WorkerRecoveryDecision：处理 lost worker、timeout、retry、mark failed。

Detailed contract package:

```text
v6_7_distributed_runtime_prd.md
v6_7_target_architecture_delta.md
v6_7_pre_implementation_closure_plan.md
v6_7_distributed_run_coordinator_contract.md
v6_7_runtime_io_contract.md
v6_7_distributed_runtime_state_machine.md
v6_7_worker_lifecycle_model.md
v6_7_worker_assignment_policy.md
v6_7_failure_recovery_acceptance_matrix.md
v6_7_incident_timeline_contract.md
v6_7_no_false_green_guard.md
schemas/v6_7_agent_worker_registry_schema.json
schemas/v6_7_worker_assignment_schema.json
schemas/v6_7_distributed_state_checkpoint_schema.json
schemas/v6_7_attempt_history_store_schema.json
schemas/v6_7_artifact_lineage_service_schema.json
schemas/v6_7_worker_recovery_decision_schema.json
schemas/v6_7_incident_timeline_event_schema.json
```

## PR Slices

```text
PR1 DistributedRunCoordinator for serial / parallel station orchestration
PR2 tenant-bound AgentWorkerRegistry and worker assignment policy
PR3 DistributedStateCheckpoint and retry / recovery state
PR4 AttemptHistoryStore and old attempt preservation
PR5 ArtifactLineageService with producer_attempt_id
PR6 incident timeline, evidence package, claim scan
```

Pre-implementation documentation closure:

```text
V6-7A document-only closure must pass before implementation.
V6-7B runtime implementation remains blocked until a separate human high-risk proceed decision is recorded.
```

## Architecture Delta

```text
DistributedRunCoordinator
 -> AgentWorkerRegistry
 -> WorkerAssignmentPolicy
 -> DistributedStateCheckpoint
 -> AttemptHistoryStore
 -> ArtifactLineageService
 -> IncidentTimeline
```

Every worker action must pass tenant, credential, policy and capability checks inherited from V6-1 through V6-4.

## Acceptance Gates

- worker lost 后可恢复或标记 failed。
- retry 保留 old attempt 和 old error。
- artifact lineage 保留 producer_attempt_id。
- parallel branch 独立状态可见。
- tenant / credential / policy boundary 对每个 worker 生效。
- cross-tenant worker identity reuse denied unless explicit binding exists。
- incident timeline 覆盖 assignment、timeout、retry、recovery。

## Focused Tests

```text
tests/test_v6_7_distributed_run_coordinator.py
tests/test_v6_7_worker_registry_scope.py
tests/test_v6_7_worker_assignment_boundary.py
tests/test_v6_7_state_checkpoint_recovery.py
tests/test_v6_7_attempt_history.py
tests/test_v6_7_artifact_lineage.py
tests/test_v6_7_incident_timeline.py
tests/test_v6_7_no_false_green.py
```

## Evidence Package

```text
docs/design/V6.x/evidence/v6-7-distributed-runtime/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  raw/
```

## Stop Conditions

- V4/V5 provider-backed demo 被写成 full orchestration readiness。
- distributed worker 绕过 tenant / credential / policy boundary。
- attempt history 覆盖旧 attempt。
- Forbidden claim scan 失败。
