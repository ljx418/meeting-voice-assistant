# V9-3 Orchestration Coordinator Engineering Design

文档状态：V9-3 engineering design / planned only。

## 1. Coordinator Boundary

`OrchestrationCoordinatorService` coordinates station-bound Agents and runtime attempts. It does not bypass V9-2 controlled executor and does not make source=agent durable mutation legal.

## 2. Core Data Model

```text
orchestration_run
agent_message
branch_state
fan_out_dispatch
fan_in_join_decision
attempt_history_record
artifact_lineage_record
lost_worker_recovery_decision
conflict_review_record
incident_timeline_event
```

## 3. State Machines

Serial:

```text
WaitingForUpstream -> Ready -> Running -> Succeeded | Failed | AcceptedPartial
```

Parallel branch:

```text
BranchCreated -> BranchReady -> BranchRunning -> BranchSucceeded | BranchFailed | BranchRecovered
```

Fan-in:

```text
WaitingForInputs -> InputsComplete -> ConflictReviewRequired | ReadyToSynthesize -> Synthesized
```

## 4. Recovery Rules

```text
old attempts are never overwritten.
retry creates a new attempt_id.
lost worker recovery records previous_checkpoint_ref and replacement_worker_id.
timeout retry keeps old error_ref.
mark_failed preserves checkpoint.
artifact lineage must preserve producer_agent_id and producer_attempt_id.
```

## 5. E2E Fixture

```text
three_agent_serial_run
three_branch_parallel_run
fan_out_to_three_branches
fan_in_synthesis_with_attribution
one_branch_failure_and_retry
one_worker_lost_and_recovered
artifact_lineage_for_each_branch
incident_timeline_for_failure_and_recovery
```

## 6. Acceptance Tests

```text
serial_station_dependency_blocks_downstream
parallel_branch_states_are_independent
fan_out_dispatch_records_each_branch
fan_in_join_requires_all_required_inputs_or_partial_decision
conflict_review_records_conflicting_inputs
lost_worker_recovery_retains_old_attempt
artifact_lineage_preserves_producer_agent_id
artifact_lineage_preserves_producer_attempt_id
source_agent_message_cannot_mutate_runtime_truth
```
