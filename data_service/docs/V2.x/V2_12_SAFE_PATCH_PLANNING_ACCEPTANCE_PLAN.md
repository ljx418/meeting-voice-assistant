# V2.12 Acceptance Plan: Safe Patch Planning

## 1. Required Acceptance Artifacts

- Patch plan JSON artifact.
- Focused unit and contract tests.
- Real data_service E2E result.
- Large-project accepted result or structured blocker.
- User scenario acceptance result.
- No-source-mutation proof.
- PRD/spec review.
- False-green audit.
- Closure audit report.

## 2. Focused Tests

Required tests:

```text
test_v2_12_patch_plan_artifact_schema
test_v2_12_patch_plan_no_source_mutation
test_v2_12_edit_candidates_require_evidence_or_needs_review
test_v2_12_validation_plan_is_descriptor_only
test_v2_12_rollback_scope_covers_all_files
test_v2_12_low_readiness_not_ready
test_v2_12_http_mcp_cli_parity
```

## 3. Real data_service E2E

Use real repo:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Required task scenarios:

1. HTTP API behavior change.
2. MCP/CLI capability registration change.
3. Test mapping and validation planning investigation.

Each scenario must produce:

- patch plan id;
- proposed files;
- edit regions;
- validation command descriptors;
- rollback scope;
- readiness score;
- evidence or `needs_review`.

## 4. Large Project E2E

Use HarnessOS or another large project.

Acceptance:

- accepted patch plan evidence; or
- structured blocker with exact reason.

False green rejection:

- do not claim accepted if the large project times out;
- do not add project-specific extractor logic;
- do not hide blockers.

## 5. User Scenario Acceptance

V2.12 cannot close only by unit tests and artifact checks. It must prove the user-facing project experience for:

1. API change patch planning.
2. MCP/CLI registration patch planning.
3. Documentation-code mismatch patch planning.
4. Large-project or low-confidence structured blocker.
5. Test coverage planning.
6. Code review preparation.

Each user scenario result must record:

- user input task;
- interface used;
- `patch_plan_id` or structured blocker id;
- observed user-facing sections;
- expected project experience result;
- pass/fail conclusion;
- evidence artifact refs;
- no-source-mutation result.
- whether the user could understand what to change, why, how to validate later, how to roll back, and whether the plan is ready/reviewable/blocked.

The scenario-level authority is:

```text
docs/V2.x/V2_12_SAFE_PATCH_PLANNING_USER_SCENARIO_ACCEPTANCE.md
```

False green rejection:

- do not close V2.12 if users cannot identify proposed files, evidence, validation descriptors, rollback scope, and readiness/blockers from the output;
- do not present validation descriptors as executed tests;
- do not present `ready_for_review` as permission to automatically edit code.
- do not close V2.12 if the user-facing result is only a raw JSON dump that does not expose proposed files, evidence, validation, rollback, and readiness in inspectable sections.

## 6. No-Mutation Gate

Before and after patch planning, compare source state.

Acceptance:

```text
planner-created artifacts may change;
source files must not change because of the planner.
```

The report must list checked paths and result.

## 7. Public Contract Gate

HTTP/MCP/CLI outputs must align on:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `patch_plan_id`
- artifact refs
- unresolved count
- needs_review count
- proposed file count
- `readiness.score`
- `readiness.status`
- warning count

## 8. Readiness Gate

`ready_for_review` requires:

- proposed edit count > 0;
- every proposed edit has evidence or `needs_review`;
- rollback scope covers all proposed files;
- validation plan exists;
- no fatal blockers.

If blockers exist, status must be `needs_review` or `blocked`.

Canonical schema rejection:

- reject if the implementation uses `edit_options` instead of `patch_options`;
- reject if readiness is exposed only as `readiness_score` without `readiness.status` and `readiness.reason_codes`;
- reject if structured blockers are hidden outside `unresolved` or `needs_review`.

## 9. False-Green Rejections

Reject closure if:

- source files are modified by V2.12;
- validation commands are executed;
- rollback scope is incomplete;
- low readiness is reported ready;
- evidence-free recommendation is accepted;
- HTTP works but MCP/CLI is missing;
- public payload leaks absolute paths, secrets, or raw tracebacks;
- mock-only testing is used as real E2E;
- user scenario acceptance is omitted.

## 10. Exit Criteria

V2.12 exits only when:

- all focused tests pass;
- data_service real E2E passes;
- large-project accepted or structured blocker is documented;
- user scenario acceptance passes;
- no source mutation is proven;
- coverage matrix V2.12 rows are updated;
- no open fatal or major findings remain.
