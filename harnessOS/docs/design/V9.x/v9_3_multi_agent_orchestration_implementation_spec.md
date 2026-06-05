# V9-3 Multi-Agent Orchestration Runtime Implementation Spec

文档状态：V9-3 implementation-readiness spec / planned only。

## 1. Boundary

V9-3 targets a bounded multi-Agent orchestration runtime slice. It does not prove full multi-Agent orchestration ready, distributed runtime ready, or Agent executor ready.

Allowed claim:

```text
V9-3 complete: multi-Agent orchestration runtime slice ready for review.
```

## 2. Runtime Objects

Required objects:

```text
AgentDescriptor
StationAgentBinding
AgentMessageEnvelope
OrchestrationRun
BranchState
FanInJoinDecision
FanOutDispatchDecision
AttemptHistoryRecord
ArtifactLineageRecord
LostWorkerRecoveryDecision
ConflictReviewRecord
```

Every station-bound Agent must have:

```text
agent_id
role
goal
memory_refs
tool_refs
skill_refs
mcp_refs
model_ref
station_id
policy_ref
credential_decision_ref
```

## 3. Message Protocol

Agent message envelope required fields:

```text
message_id
orchestration_run_id
sender_agent_id
receiver_agent_id
station_id
station_run_id
attempt_id
branch_id
message_kind
payload_refs
artifact_refs
correlation_id
request_id
audit_ref
created_at
```

Rules:

```text
payload_refs are redacted refs only.
raw prompt / raw model response / raw artifact content fields are forbidden.
source=agent message cannot directly mutate runtime truth.
```

## 4. Serial / Parallel / Fan-In / Fan-Out

Required semantics:

```text
serial dependency blocks downstream until upstream reaches terminal success or accepted partial state.
parallel branch states are independent.
fan-out records one dispatch decision per target branch.
fan-in records join inputs, missing inputs, conflict inputs and synthesis decision.
failure recovery retains old attempts and old errors.
lost worker recovery records replacement worker and previous checkpoint.
artifact lineage records producer_agent_id and producer_attempt_id.
```

## 5. E2E Fixture

Fixture must include:

```text
serial_path_with_three_agents
parallel_path_with_three_branches
fan_out_dispatch
fan_in_synthesis
one_failed_attempt
one_lost_worker_recovery
artifact_lineage_with_producer_agent_id
artifact_lineage_with_producer_attempt_id
incident_timeline
```

## 6. Acceptance Tests

```text
serial_station_dependency_blocks_downstream
parallel_branch_states_are_independent
fan_out_dispatch_records_target_branches
fan_in_join_records_all_input_artifacts
fan_in_conflict_review_records_conflicting_inputs
lost_worker_recovery_retains_old_attempt
timeout_retry_keeps_old_error
artifact_lineage_preserves_producer_agent_id
artifact_lineage_preserves_producer_attempt_id
source_agent_message_cannot_directly_mutate_runtime
multi_agent_runtime_no_false_green
```

## 7. Stop Conditions

```text
V4/V8 dev-local evidence is upgraded to full orchestration proof.
old attempt is overwritten during retry.
producer_agent_id or producer_attempt_id is missing from lineage.
fan-in synthesis has no attribution.
parallel branch state is flattened into one global status.
```
