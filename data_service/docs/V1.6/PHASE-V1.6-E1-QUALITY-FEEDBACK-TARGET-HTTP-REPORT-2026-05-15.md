# V1.6-E1 Quality Feedback Target HTTP Report

Date: 2026-05-15

## 1. Scope

V1.6-E1 only opens the minimal quality feedback target HTTP surface:

- `POST /api/workspaces/{workspace_id}/quality/feedback`

E1 does not add MCP tools, CLI top-level commands, CLI nested commands, quality correction rules target HTTP, quality correction review target HTTP, quality correction plan target HTTP, console polish, or any non-E1 route.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D1-D6 are accepted.
- Pre-E1 target HTTP route count: 28.
- MCP tool count: 40.
- CLI top-level commands remain `build / graph / quality / query / source / trace / workspace`.
- CLI nested inventory is unchanged by E1.
- `/api/v1/knowledge/*` compatibility routes are retained.

## 3. Phase Overlay

E1 adds `docs/V1.6/public-surface-overlays/v1_6_e1.json` with exactly one allowed target HTTP addition:

- `POST /api/workspaces/{workspace_id}/quality/feedback`

No MCP, CLI, CLI nested, or compatibility HTTP additions are declared.

## 4. Implemented Route

- `POST /api/workspaces/{workspace_id}/quality/feedback`

The route reuses `DataService.record_quality_feedback(...)` through `quality_contract.py` and projects the response to stable target HTTP fields.

## 5. Contract Summary

Allowed request fields:

- `target_type`
- `target_id`
- `action`
- `label`
- `suggested_value`
- `reason`
- `metadata`

Stable response fields include:

- `workspace_id`
- `feedback.feedback_id`
- `feedback.target_type`
- `feedback.target_id`
- `feedback.action`
- `feedback.label`
- `feedback.suggested_value`
- `feedback.reason`
- `feedback.status`
- `feedback.created_at`
- `feedback.artifact_ref`
- `summary`
- `warnings`
- `next_actions`

`artifact_ref` uses a non-path `quality-feedback://{feedback_id}` reference. Metadata is sanitized before persistence through the target HTTP route and before response projection. Default responses do not expose workspace path, source path, quality file path, correction rules path, correction plan path, debug paths, or raw filesystem layout.

The route is a non-destructive governance signal write. Existing helper behavior may refresh draft correction rules, but E1 does not expose correction rules/review/plan target HTTP and does not apply correction plans.

## 6. Public Surface Scan

- Target HTTP count after E1: 29.
- E1 HTTP diff: exactly `POST /api/workspaces/{workspace_id}/quality/feedback`.
- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff: none.
- No quality feedback list target HTTP.
- No quality correction rules/review/plan target HTTP.
- No undeclared route.
- Compatibility HTTP retained.

## 7. Tests and Regressions

Focused tests cover:

- quality feedback route success.
- stable non-path projection.
- metadata/path sanitization.
- required fields and unsupported fields.
- path-like `target_id` rejection.
- archived workspace blocking.
- unknown workspace error.
- compatibility quality feedback retention.
- API key boundary.
- no target HTTP quality correction routes.

Regression commands:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_quality_feedback.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_build.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_query.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_ingest.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` - passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q` - passed.
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q` - passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q` - passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q` - passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q` - passed.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"` - passed.

Frontend build: not touched.

## 8. Documentation Sync

Updated V1.6 docs record:

- V1.5 baseline remains immutable.
- E1 overlay adds exactly one route.
- Current target HTTP route count is 29.
- MCP tool count remains 40.
- CLI inventory remains unchanged.
- Remaining quality write routes remain planned.
- F console governance polish remains planned.

## 9. Blocking Issues

None.

## 10. Final Decision

Accepted.

## 11. Next Phase Recommendation

Next phase should be `V1.6-E2 Quality Correction Rules Target HTTP Minimal Surface`.

Do not open all remaining quality write routes at once. Do not combine quality correction review, correction plan, or console polish with E2.
