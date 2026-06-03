# Phase V1.6-E5 Quality Correction Rules Build Target HTTP Report

Date: 2026-05-15

## 1. Scope

E5 only opens quality correction-rules artifact build target HTTP:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`

E5 does not add MCP tools, CLI top-level commands, CLI nested commands, correction apply target HTTP, workspace build, session build, correction plan build, or full quality build semantics. The route is limited to rebuilding the correction-rules artifact from existing feedback.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D/E1/E2/E3/E4 are accepted.
- target HTTP pre-E5 route count = 34.
- MCP tool count = 40.
- CLI top-level and nested inventory unchanged.
- `/api/v1/knowledge/*` compatibility routes retained.

## 3. Phase Overlay

E5 overlay: `docs/V1.6/public-surface-overlays/v1_6_e5.json`

Allowed target HTTP addition:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`

No MCP, CLI, nested CLI, or compatibility HTTP additions.

## 4. Implemented Route

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`

The request body accepts only `{}`. Extra fields such as `status`, `review`, `approve`, `apply`, `rebuild_plan`, `path`, `source_path`, `rules_path`, and `plan_path` are rejected by the target HTTP request model.

## 5. Contract Summary

- E5 build is correction-rules artifact build only.
- It is not quality build, workspace build, session build, correction plan build, or correction apply.
- It reuses existing `DataService.build_quality_correction_rules()` semantics and projects the result through stable target HTTP fields.
- Existing approved / rejected / archived / revoked / active / applied rule statuses are preserved according to existing helper semantics.
- Newly inferred rules from feedback remain draft rules.
- The response prefers summary/count fields and returns bounded stable `rules[]` projection with `limit` and `truncated`.
- If a correction plan already exists, E5 does not update it; the response reports `correction_plan_may_be_stale` in warnings and includes `knowledge_correction_plan` in next actions.
- No raw correction rules file, raw paths, or internal layout fields are returned.
- The static `build` route segment is reserved and does not get treated as a review `rule_id`.

## 6. Public Surface Scan

- target HTTP route count = 35.
- MCP diff = none.
- CLI top-level diff = none.
- CLI nested diff = none.
- no undeclared route.
- compatibility HTTP retained.

## 7. Tests and Regressions

Focused and regression commands run:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_rules_build.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_review.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_plan.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_rules.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_feedback.py -q`
- `python3 -m pytest backend/tests/test_data_service_api.py -q`
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q`
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py backend/tests/test_session_ingest_query_build_contract_plan.py -q`
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`

All listed commands passed.

Drawio validation:

- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"`

Frontend build: not touched.

## 8. Documentation Sync

Updated docs:

- `docs/V1.6/README.md`
- `docs/V1.6/development-plan.md`
- `docs/V1.6/acceptance-plan.md`
- `docs/V1.6/current-vs-target-gap.md`
- `docs/V1.6/current-vs-target-gap.drawio`
- `docs/V1.6/interface-convergence-plan.md`
- `docs/V1.6/target-architecture.md`
- `docs/V1.6/target-http-routes-plan.md`
- `docs/V1.6/public-surface-baseline.md`
- `docs/V1.x/data_service/README.md`

V1.5 baseline JSON was not modified. F remains planned, not implemented.

## 9. Blocking Issues

None.

## 10. Final Decision

accepted

## 11. Next Phase Recommendation

Next phase should be V1.6-F1 Console Governance Evidence Polish Planning.

Do not add backend public surface in F1. Do not combine console polish with new quality write or correction apply behavior.
