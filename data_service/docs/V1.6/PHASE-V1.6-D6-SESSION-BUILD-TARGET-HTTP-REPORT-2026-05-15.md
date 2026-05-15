# Phase V1.6-D6 Session Build Target HTTP Report

Date: 2026-05-15

## 1. Scope

D6 only opens session build start/status/cancel target HTTP.

D6 does not open quality target HTTP, does not add MCP tools, does not add CLI top-level commands, and does not add CLI nested commands. D6 is not the full Session GraphRAG public contract.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D1-D5 were accepted before D6.
- Pre-D6 target HTTP route count: 25.
- MCP tool count: 40.
- CLI top-level and nested inventory unchanged from D5.

## 3. Phase Overlay

D6 added `docs/V1.6/public-surface-overlays/v1_6_d6.json`.

Allowed additions:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`

V1.5 baseline was not modified.

## 4. Implemented Routes

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`

## 5. Contract Summary

- Request fields: D6 target HTTP exposes `mode` for build start, using existing `SESSION_BUILD_MODES`. Unsupported request fields are rejected by the API boundary.
- Operation lifecycle: build start returns a real session operation id from `SessionKnowledgeService.start_build`; no fake `operation_id` is produced.
- Status/cancel: status and cancel require operation ownership by `workspace_id + session_id`. Cross-workspace and cross-session operations return normalized not-found style blocked responses and do not leak or mutate the original operation.
- Cancel behavior: queued operations are cancelled; terminal operation cancel is idempotent and returns the existing terminal operation with a warning.
- Side effects: D6 permits existing session-scoped build/materialization side effects only. It does not trigger workspace-level build or quality write.
- Artifact refs: target HTTP projects operation/artifact paths to stable `session-build://...` and `session-artifact://...` refs.
- Path projection: operation artifacts, diagnostics, logs, details, stage errors, error metadata, operation metadata and stage result are sanitized before response.

## 6. Public Surface Scan

- target HTTP count: 28.
- MCP diff: none.
- CLI diff: none.
- Quality target HTTP routes: none.
- Undeclared routes: none.
- `/api/v1/knowledge/*` compatibility retained.

## 7. Tests and Regressions

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_session_build.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_session_query.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_session_ingest.py -q` -> passed.
- `python3 -m pytest backend/tests/test_session_ingest_query_build_contract_plan.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` -> passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q` -> passed.
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q` -> passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q` -> passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q` -> passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q` -> passed.
- drawio validation -> passed.
- frontend build -> not touched.

## 8. Documentation Sync

Updated V1.6 docs distinguish immutable V1.5 baseline, accepted overlays through D6, and planned E/F.

Updated:

- `README.md`
- `development-plan.md`
- `acceptance-plan.md`
- `current-vs-target-gap.md`
- `current-vs-target-gap.drawio`
- `interface-convergence-plan.md`
- `target-architecture.md`
- `target-http-routes-plan.md`
- `public-surface-baseline.md`
- `session-ingest-query-build-contract-plan.md`

Planned vs implemented check: D6 is marked completed; E/F remain planned. Quality target HTTP is not described as implemented.

## 9. Blocking Issues

None.

## 10. Final Decision

Accepted.

## 11. Next Phase Recommendation

Next phase should be V1.6-E1 Quality Feedback Target HTTP Minimal Surface.

Do not open all quality write routes at once. Do not combine with console polish.
