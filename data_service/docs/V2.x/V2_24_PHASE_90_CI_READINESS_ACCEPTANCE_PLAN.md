# V2.24 Phase 90 Production Readiness & CI Hardening Acceptance Plan

## 1. Acceptance Rule

Phase 90 is accepted only if the readiness artifact and release report are generated from real evidence and all mandatory gates pass.

`skipped` and `not_run` are valid statuses, but they cannot be counted as `passed`.

## 2. Focused Tests

Required focused suite:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_24_ci_readiness.py -q
```

Required assertions:

1. CI readiness report is persisted.
2. Release readiness Markdown report is persisted.
3. Mandatory layers are present.
4. Skipped layers are not counted as passed.
5. Redaction failure creates a release blocker.
6. Missing required platform artifact creates a release blocker.
7. HTTP/MCP/CLI read outputs have matching stable fields.

## 3. Real Repository E2E

Real input repository:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Required flow:

1. Import current repo into an isolated `/private/tmp` workspace.
2. Generate snapshot.
3. Build V2.18-V2.23 platform artifacts required by the CI gate.
4. Build CI readiness artifact with real command evidence.
5. Read readiness through service, HTTP, MCP, and CLI.
6. Read release report.
7. Verify redaction and artifact refs.

Minimum E2E summary:

```text
overall_status
unit_status
contract_status
artifact_status
frontend_status
real_repo_e2e_status
warning_current
warning_budget
redaction_status
release_ready
blocker_count
artifact_refs_count
```

## 4. Regression Commands

Required before final acceptance:

```bash
npm run build
PYTHONPATH=backend python3 -m pytest backend/tests -q
git diff --check -- .
```

## 5. Public Contract Parity

HTTP/MCP/CLI must agree on:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `overall_status`
- `release_gate.ready`
- blocker count
- artifact ref count
- warning count
- redaction status

## 6. Security And Redaction Gate

Readiness and release outputs must not expose:

- local absolute repository path;
- `/private/tmp` workspace path;
- API keys or tokens;
- raw traceback;
- secret-like environment values.

Any redaction failure blocks readiness.

## 7. False-Green Rejection

Reject acceptance if any of these occur:

- skipped command is reported as passed;
- test command evidence is fabricated;
- release report exists but readiness JSON is missing;
- redaction gate fails but `overall_status` is `ready`;
- missing platform artifact does not create a blocker;
- full backend regression is skipped;
- real repo E2E uses only mock data;
- readiness report mutates source platform artifacts.

## 8. Final Acceptance Artifacts

The phase must write:

```text
docs/V2.x/V2_24_PHASE_90_CI_READINESS_ACCEPTANCE_AUDIT_REPORT.md
```

The report must include real command results, E2E summary, PRD/spec review, false-green review, and final exit decision.
