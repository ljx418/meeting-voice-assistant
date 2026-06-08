# V9-3 Development And Acceptance Plan

文档状态：V9-3 detailed development and acceptance plan / implementation candidate.

## 1. Current Entry Baseline

V9-3 may enter implementation only from this bounded baseline:

```text
V9-1 complete: Agent Executor Safety Gate implementation ready for review.
V9-2 complete: limited controlled Agent executor runtime slice ready for review.
```

V9-2 remains bounded:

```text
allowed_operations=[workflow.instance.start, station.rerun, artifact.write, quality.evaluation.create]
source=agent durable mutation denied
runtime_executor_route_created=false
runtime_worker_created=false
controlled_executor_ready=false
agent_executor_ready=false
```

## 2. V9-3 Scope

V9-3 implements a bounded multi-Agent orchestration runtime slice:

```text
station-bound Agent registry
serial station dependency
parallel branch state isolation
fan-out dispatch
fan-in join / synthesis decision
attempt history retention
lost worker recovery
artifact lineage with producer_agent_id and producer_attempt_id
incident timeline refs
```

V9-3 must include user-facing orchestration fixtures, not only schema-level records:

```text
Roman Forum debate workflow: role-specific Agents discuss a philosophy topic, challenge each other and synthesize attributed conclusions.
Video creation storyboard workflow: user idea becomes creative brief, script, shot list, storyboard prompts, image artifact refs and visual consistency review.
Natural-language workflow optimization remains proposal-only: it produces WorkflowDiff / handoff and waits for user confirmation before mutation.
```

V9-3 must not implement:

```text
不得声明 full multi-Agent orchestration ready
不得声明 distributed multi-Agent runtime ready
不得声明 Agent executor ready
不得允许 source=agent direct durable mutation
不得开放 connector.call
不得开放 external_llm.call
不得执行 git.commit / git.push / production.deploy
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-3A Agent registry and station binding | AgentDescriptor and StationAgentBinding records | each station has exactly one bound Agent in fixture; model/tool/skill/MCP refs are redacted refs |
| V9-3B Orchestration run and branch state | OrchestrationRun and BranchState records | serial and parallel states are distinct and auditable |
| V9-3C Fan-out / fan-in coordinator | FanOutDispatch and FanInJoinDecision records | fan-out target branches and fan-in attribution are complete |
| V9-3D Attempt history and recovery | AttemptHistoryRecord and LostWorkerRecoveryDecision records | retry retains old attempt and old error; lost worker recovery records replacement worker |
| V9-3E Artifact lineage and conflict review | ArtifactLineageRecord and ConflictReviewRecord records | lineage preserves producer_agent_id and producer_attempt_id |
| V9-3F Creative scenario fixtures | Roman Forum and video storyboard fixtures | role-specific discussion, attributed synthesis, storyboard artifacts and provider boundary are auditable |
| V9-3G Evidence package and dashboard | V9-3 acceptance data and HTML dashboard | claim scan, redaction scan and runtime fixture checks PASS |

## 4. Required Runtime Schemas

V9-3 implementation must validate these schemas before runtime acceptance:

```text
schemas/v9_3_agent_descriptor.schema.json
schemas/v9_3_station_agent_binding.schema.json
schemas/v9_3_orchestration_run.schema.json
schemas/v9_3_branch_state.schema.json
schemas/v9_3_fan_out_dispatch.schema.json
schemas/v9_3_fan_in_join_decision.schema.json
schemas/v9_3_attempt_history_record.schema.json
schemas/v9_3_lost_worker_recovery_decision.schema.json
schemas/v9_3_conflict_review_record.schema.json
schemas/orchestration_message.schema.json
schemas/artifact_lineage_record.schema.json
```

## 5. E2E Fixture Contract

Primary fixture:

```text
fixtures/v9-3-orchestration/serial_parallel_fan_in_out_recovery.json
```

The fixture must contain:

```text
three station-bound Agents
one serial dependency path
three parallel branches
one fan-out dispatch decision
one fan-in join decision with attribution
one failed attempt retained
one lost worker recovery decision
artifact lineage for every branch output
incident timeline refs for failure and recovery
```

Required negative fixtures:

```text
fixtures/v9-3-orchestration/fan_in_missing_attribution.json
fixtures/v9-3-orchestration/retry_overwrites_old_attempt.json
fixtures/v9-3-orchestration/source_agent_direct_mutation_attempt.json
```

Required user-facing scenario fixtures:

```text
fixtures/user-scenarios/us_v9_07_roman_forum_debate.json
fixtures/user-scenarios/us_v9_08_video_storyboard_workflow.json
fixtures/user-scenarios/us_v9_09_nl_workflow_optimization.json
```

## 6. Acceptance Tests

```text
v9_3_agent_registry_binds_one_agent_per_station
v9_3_serial_station_dependency_blocks_downstream
v9_3_parallel_branch_states_are_independent
v9_3_fan_out_dispatch_records_each_target_branch
v9_3_fan_in_join_records_all_input_artifacts
v9_3_fan_in_missing_attribution_denied
v9_3_lost_worker_recovery_retains_old_attempt
v9_3_retry_does_not_overwrite_old_error
v9_3_artifact_lineage_preserves_producer_agent_id
v9_3_artifact_lineage_preserves_producer_attempt_id
v9_3_source_agent_message_cannot_directly_mutate_runtime_truth
v9_3_roman_forum_debate_preserves_role_identity_and_attribution
v9_3_video_storyboard_records_provider_model_and_image_refs
v9_3_natural_language_optimization_outputs_diff_before_mutation
v9_3_no_false_green_scan_pass
v9_3_redaction_scan_pass
```

## 7. Evidence Package

V9-3 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
runtime_fixture_ref
schema_validation_result
test_run_refs
claim_scan_result
redaction_scan_result
source_refs
```

V9-3 may complete only if:

```text
status=PASS
evidence_scope=real_runtime_fixture
runtime_backed=true
serial_parallel_fan_in_fan_out=PASS
attempt_history=PASS
artifact_lineage=PASS
failure_recovery=PASS
lost_worker_recovery=PASS
source_agent_direct_mutation_denied=PASS
roman_forum_debate_fixture=PASS
video_storyboard_fixture=PASS or explicitly BLOCKED when provider capability is unavailable
natural_language_optimization_diff_only=PASS
fallback_demo_only=false
```

## 8. Stop Conditions

```text
V9-3 claims full multi-Agent orchestration ready.
V9-3 claims distributed multi-Agent runtime ready.
source=agent directly mutates durable runtime truth.
fan-in synthesis has no attribution.
retry overwrites old attempt or old error.
artifact lineage lacks producer_agent_id or producer_attempt_id.
parallel branch state is flattened into one global status.
planning docs are counted as runtime evidence.
raw prompt / raw model response / raw artifact content appears in evidence.
Roman Forum debate is described as full multi-Agent orchestration readiness.
Video storyboard placeholder images are described as provider-backed image generation.
Natural-language optimization applies workflow mutations before user confirmation.
```
