# Phase V1.6-E4 Quality Correction Plan Target HTTP Report

Date: 2026-05-15

## 1. Scope

E4 only opens correction plan target HTTP:

- `GET /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`

E4 does not add MCP tools, CLI top-level commands, CLI nested commands, or quality build target HTTP. E4 only reads or generates the correction plan artifact.

## 2. Baseline

- V1.5 public surface baseline remains immutable.
- V1.6-A/B/C/D1-D6/E1/E2/E3 are accepted.
- Pre-E4 target HTTP route count: 32.
- MCP tool count: 40.
- CLI top-level/nested inventory unchanged.
- `/api/v1/knowledge/*` compatibility routes retained.

## 3. Phase Overlay

E4 overlay file:

- `docs/V1.6/public-surface-overlays/v1_6_e4.json`

Allowed target HTTP additions:

- `GET /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`

V1.5 baseline was not modified.

## 4. Implemented Routes

- `GET /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`

## 5. Contract Summary

- GET reads an existing correction plan stable projection and does not generate a plan.
- Missing plan returns normalized blocked/no_artifact envelope with `quality_correction_plan_no_artifact`.
- POST generates the correction plan artifact in plan-only / generate-only mode.
- POST repeated-call semantics are fixed: it overwrites the current plan artifact, does not retain previous plans, and keeps the same `plan_id` when the approved rules snapshot is unchanged.
- The plan binds an approved-rules snapshot and returns `rule_count`, `action_count`, `included_rule_ids`, `excluded_rule_counts`, and stable `actions[]` summaries.
- Draft/rejected/archived/revoked/active/applied rules are excluded from the plan by default.
- `actions[]` does not expose raw patch payloads, raw impact rows, raw GraphRAG rows, raw LLMWiki paths, raw artifact paths, or internal object dumps.
- E4 does not execute correction, apply plans, activate read-time governance, trigger quality build, or create build/session operations.
- Source/wiki/graph/session artifacts and correction rules remain unchanged by plan generation.
- Artifact refs use non-path `quality-correction-plan://{workspace_id}`.

## 6. Public Surface Scan

- Target HTTP count after E4: 34.
- New target HTTP routes: exactly the E4 overlay 2 routes.
- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff: none.
- Quality build target HTTP: not opened.
- Undeclared routes: none.
- Compatibility HTTP retained.

## 7. Tests and Regressions

Focused E4 tests cover:

- GET/POST route existence;
- missing plan behavior;
- plan generation from approved rules;
- approved rules snapshot binding and excluded rule counts;
- repeated POST semantics;
- archived workspace GET/POST behavior;
- stable actions projection;
- no internal path/layout leakage;
- before/after fingerprints for correction plan, correction rules, review artifacts, source/wiki/graph/session artifacts, governance state, and operations;
- no quality build target HTTP;
- API key boundary behavior.

Regression commands:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_plan.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_review.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_rules.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_feedback.py -q`
- `python3 -m pytest backend/tests/test_target_http_session_build.py -q`
- `python3 -m pytest backend/tests/test_data_service_api.py -q`
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q`
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"`

Frontend build: not touched.

## 8. Documentation Sync

Updated V1.6 documents distinguish:

- immutable V1.5 baseline;
- accepted E4 overlay;
- current target HTTP route count = 34;
- E4 correction plan read/generate-only semantics;
- quality build target HTTP remains planned / not opened;
- V1.6-F remains planned.

`current-vs-target-gap.md` and `current-vs-target-gap.drawio` were synchronized.

## 9. Blocking Issues

None.

## 10. Final Decision

accepted

## 11. Next Phase Recommendation

Next phase should be V1.6-E5 Quality Build Target HTTP Minimal Surface.

Do not combine quality build with console polish.
