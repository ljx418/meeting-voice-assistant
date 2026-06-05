# V6-7 Failure Recovery Acceptance Matrix

文档状态：V6-7 complete / ready for review acceptance matrix。本文定义并记录 V6-7 实现后的验收矩阵。

## Required Test Cases

| Case | Expected Result |
| --- | --- |
| `worker_wrong_tenant_denied` | Worker assignment is denied and records audit_ref. |
| `worker_cross_tenant_reuse_without_binding_denied` | Reused worker id without explicit tenant binding is denied. |
| `worker_missing_credential_decision_denied` | Assignment fails before station dispatch. |
| `worker_missing_policy_decision_denied` | Assignment fails before station dispatch. |
| `source_agent_worker_assignment_denied` | source=agent cannot create worker assignment or durable mutation. |
| `serial_station_dependency_blocks_downstream` | Downstream station waits for upstream completion. |
| `parallel_branch_states_are_independent` | One branch failure does not overwrite sibling branch state. |
| `lost_worker_recovery_retains_old_attempt` | New attempt is appended; old attempt remains visible. |
| `timeout_retry_keeps_old_error` | Retry creates new attempt and preserves old error_ref. |
| `mark_failed_preserves_checkpoint` | Failed recovery keeps checkpoint_ref and incident event. |
| `artifact_lineage_preserves_producer_attempt_id` | Output artifact records producer_attempt_id. |
| `idempotent_retry_returns_prior_recovery_ref` | Duplicate retry does not create duplicate attempts. |
| `incident_timeline_records_assignment_timeout_retry_recovery` | Incident timeline has assignment, timeout, retry and recovery events. |
| `distributed_runtime_no_false_green` | Claim scan has zero forbidden completion claims. |

## Attempt History Conditional Test Cases

| Case | Expected Result |
| --- | --- |
| `attempt_number_1_allows_previous_attempt_null` | First attempt may have `previous_attempt_id=null`. |
| `attempt_number_gt_1_requires_previous_attempt_id` | Retry / later attempt must reference the prior attempt. |
| `retry_preserves_previous_attempt_and_error_ref` | New attempt keeps previous attempt and previous error refs auditable. |
| `old_attempt_not_overwritten` | Retry appends a new attempt and never overwrites old attempt content or status. |

## Branch State Test Cases

| Case | Expected Result |
| --- | --- |
| `parallel_checkpoint_requires_branch_id` | Parallel branch checkpoint records `branch_id`. |
| `parallel_checkpoint_requires_branch_state` | Parallel branch checkpoint records independent `branch_state`. |

## Evidence Package Requirements

```text
docs/design/V6.x/evidence/v6-7-distributed-runtime/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  redaction-scan.md
  raw/runtime-results.json
  raw/worker-assignments.json
  raw/attempt-history.json
  raw/artifact-lineage.json
  raw/incident-timeline.json
```

## Required Acceptance Summary Fields

```text
stage=V6-7
status=PASS|PARTIAL|FAIL|BLOCKED
evidence_scope=production_pilot_runtime_slice|staging_runtime_slice|planning_only
human_high_risk_decision_recorded=true
distributed_multi_agent_runtime_ready=false
full_multi_agent_orchestration_ready=false
agent_executor_ready=false
production_controlled_executor_ready=false
```

## Stop Conditions

- Any test passes by reading static docs only.
- Attempt history overwrites old attempts.
- Artifact lineage omits producer_attempt_id.
- source=agent creates worker assignment.
- V6-7 completion note claims full multi-Agent orchestration readiness.
