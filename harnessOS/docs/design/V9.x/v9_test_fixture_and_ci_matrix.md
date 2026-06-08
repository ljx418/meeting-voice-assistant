# V9 Test Fixture And CI Matrix

文档状态：V9 P0 test fixture plan / required before stage implementation。

## 1. Test Case Contract

Every V9 test case must specify:

```text
test_id
owner_stage
scenario_id
input_fixture
expected_output
expected_user_visible_output
expected_denied_state
expected_evidence_record
expected_audit_ref
expected_redaction_behavior
expected_rollback_or_correction_behavior
ci_command
blocking_severity
```

Current P0 fixture roots:

```text
docs/design/V9.x/fixtures/schema-negative/
docs/design/V9.x/fixtures/evidence/
docs/design/V9.x/fixtures/v9-2-controlled-executor/
docs/design/V9.x/fixtures/v9-3-orchestration/
docs/design/V9.x/fixtures/v9-4-coding-workflow/
docs/design/V9.x/fixtures/terminal/
```

User scenario fixture root:

```text
docs/design/V9.x/fixtures/user-scenarios/
```

## 2. Required Negative Fixtures

```text
source_agent_durable_mutation
expired_human_authorization_ref
wrong_tenant_human_authorization_ref
raw_secret_in_evidence
fan_in_missing_attribution
retry_overwrites_old_attempt
auto_commit_without_human_approval
auto_push_without_release_gate
auto_deploy_without_production_gate
terminal_workspace_escape
terminal_symlink_escape
studio_direct_runtime_write
studio_hidden_mutation_form
v9_8_with_planning_docs_only
```

## 3. CI Gates

Planned commands:

```text
python -m json.tool docs/design/V9.x/schemas/*.schema.json
python -m json.tool docs/design/V9.x/fixtures/schema-negative/*.json
python -m json.tool docs/design/V9.x/fixtures/evidence/*.json
xmllint --noout docs/design/V9.x/v9_current_gap_analysis.drawio
rg -in "<forbidden-claim-regex>" docs/design/V9.x
python -m pytest tests/test_v9_contracts_*.py -q
python -m pytest tests/test_v9_evidence_package_*.py -q
python -m pytest tests/test_v9_no_false_green_*.py -q
```

## 4. Blocking Severity

```text
P0 blocks stage implementation.
P1 blocks stage completion.
P2 requires documented proceed decision.
```

## 5. Acceptance Rule

No V9 implementation stage may start until its fixtures and CI commands are listed and accepted. No V9 stage may complete if a P0/P1 fixture fails.

No V9 final acceptance may run until the user scenario acceptance gate is reviewed. A technical test PASS does not replace a missing user-facing dashboard or report.

## 6. Front-Stage Fixture-To-Test Matrix

| Stage | Fixture | Expected Result |
| --- | --- | --- |
| V9-1 | `schema-negative/source_agent_durable_mutation.json` | rejected by envelope validator and CapabilityResolver |
| V9-1 | `fixtures/evidence/v9_1_contract_freeze_sample.json` | accepted only as contract_freeze, not runtime evidence |
| V9-2 | `schema-negative/expired_human_authorization_ref.json` | rejected by HumanAuthorizationRef validator |
| V9-2 | `schema-negative/raw_secret_in_evidence.json` | rejected by evidence schema and redaction scan |
| V9-3 | `schema-negative/artifact_lineage_missing_producer_attempt.json` | rejected by artifact lineage schema |
| V9-3 | `fixtures/v9-3-orchestration/serial_parallel_fan_in_out_recovery.json` | accepted as real_runtime_fixture input and covered by V9-3 runtime evidence |
| V9-3 | `fixtures/v9-3-orchestration/fan_in_missing_attribution.json` | rejected because fan-in synthesis lacks attribution |
| V9-3 | `fixtures/v9-3-orchestration/retry_overwrites_old_attempt.json` | rejected because retry must retain old attempt and old error |
| V9-3 | `fixtures/v9-3-orchestration/source_agent_direct_mutation_attempt.json` | rejected because source=agent cannot directly mutate runtime truth |
| V9-4 | `fixtures/v9-4-coding-workflow/no_auto_commit_push_deploy.json` | covered by V9-4 runtime evidence; auto commit / auto push / auto deploy denied and recorded |
| V9-8 | `fixtures/evidence/v9_8_reject_planning_only_sample.json` | final validator returns BLOCKED, not PASS |

## 6.1 User Scenario Fixture-To-Test Matrix

| Scenario | Fixture | Expected Result |
| --- | --- | --- |
| US-V9-01 | `fixtures/user-scenarios/us_v9_01_controlled_runtime_review.json` | user can open V9-2 dashboard and verify four allowed operations plus source=agent denial |
| US-V9-02 | `fixtures/user-scenarios/us_v9_02_orchestration_review.json` | satisfied by V9-3 runtime dashboard and lineage evidence package |
| US-V9-03 | `fixtures/user-scenarios/us_v9_03_coding_workflow_review.json` | satisfied by V9-4 runtime dashboard, diff proposal, sandboxed test, review summary, fix-loop and no-auto-commit/push/deploy denial evidence |
| US-V9-04 | `fixtures/user-scenarios/us_v9_04_terminal_worker_review.json` | satisfied by V9-5 terminal worker dashboard, command tier decisions, transcript, diff capture and denial evidence |
| US-V9-05 | `fixtures/user-scenarios/us_v9_05_studio_review.json` | user scenario remains BLOCKED until Studio BFF/browser evidence exists |
| US-V9-06 | `fixtures/user-scenarios/us_v9_06_final_dashboard_review.json` | final user scenario remains BLOCKED until US-V9-01..US-V9-09 are PASS or accepted PARTIAL |
| US-V9-07 | `fixtures/user-scenarios/us_v9_07_roman_forum_debate.json` | satisfied by V9-3 role-specific debate, multi-round message and attribution-preserving synthesis evidence |
| US-V9-08 | `fixtures/user-scenarios/us_v9_08_video_storyboard_workflow.json` | explicitly BLOCKED for provider-backed image generation in local V9-3 fixture; not allowed to count as provider-backed PASS |
| US-V9-09 | `fixtures/user-scenarios/us_v9_09_nl_workflow_optimization.json` | satisfied by V9-3 WorkflowDiff proposal evidence and no-mutation-before-confirmation evidence |

## 7. V9-3 Schema Parse Set

```text
docs/design/V9.x/schemas/v9_3_agent_descriptor.schema.json
docs/design/V9.x/schemas/v9_3_station_agent_binding.schema.json
docs/design/V9.x/schemas/v9_3_orchestration_run.schema.json
docs/design/V9.x/schemas/v9_3_branch_state.schema.json
docs/design/V9.x/schemas/v9_3_fan_out_dispatch.schema.json
docs/design/V9.x/schemas/v9_3_fan_in_join_decision.schema.json
docs/design/V9.x/schemas/v9_3_attempt_history_record.schema.json
docs/design/V9.x/schemas/v9_3_lost_worker_recovery_decision.schema.json
docs/design/V9.x/schemas/v9_3_conflict_review_record.schema.json
```

## 8. Creative User Scenario Test Matrix

```text
v9_3_roman_forum_has_role_specific_agents
v9_3_roman_forum_has_multi_round_messages
v9_3_roman_forum_synthesis_preserves_attribution_refs
v9_3_video_workflow_generates_brief_script_shot_list_and_storyboard_prompts
v9_3_video_storyboard_has_minimum_four_shots
v9_3_video_image_generation_records_provider_model_refs
v9_3_video_missing_provider_key_blocks_real_image_pass
v9_3_video_redacts_forbidden_provider_content
v9_6_nl_optimization_generates_workflow_diff_proposal
v9_6_nl_optimization_requires_user_confirmation_before_apply
v9_6_nl_optimization_denies_source_agent_direct_mutation
```
