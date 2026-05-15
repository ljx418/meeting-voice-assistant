# Phase V1.6-D2 Session Lifecycle Target HTTP Report

## 1. Scope

V1.6-D2 only opens minimal session lifecycle target HTTP: create, list, get, close and delete.

D2 does not open session ingest/query/build target HTTP, quality target HTTP, new MCP tools, CLI commands or CLI subcommands. C4 `/graph/session` remains graph-scoped read-only inspection and is not redefined as session lifecycle.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D1 accepted.
- Pre-D2 target HTTP route count: 18.
- MCP tool count: 40.
- CLI top-level and nested inventory unchanged from D1/C4 accepted baseline.
- `/api/v1/knowledge/*` compatibility routes retained.

## 3. Phase Overlay

D2 overlay file: `docs/V1.6/public-surface-overlays/v1_6_d2.json`.

Allowed additions:

- `POST /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`

V1.5 baseline was not modified.

## 4. Implemented Routes

- `POST /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`

## 5. Contract Summary

Session lifecycle target HTTP reuses `SessionKnowledgeService` and the shared stable projection in `session_lifecycle_contract.py`.

Stable fields include `workspace_id`, `session_id`, `status`, timestamps, sanitized `metadata`, `artifact_ref`, warnings, next actions and normalized error.

Close/delete/get/list behavior:

- Duplicate create follows existing session lifecycle semantics and returns the existing `session_id`.
- List defaults to `include_deleted=false`; `include_deleted=true` returns disposed sessions.
- Get deleted session follows existing lifecycle and returns the disposed session record.
- Close already closed remains closed.
- Close deleted session follows existing lifecycle and remains disposed.
- Delete active/closed/deleted sessions follows existing lifecycle and returns disposed state.
- Cross-workspace get/close/delete returns normalized `unknown_session_id` and does not affect the other workspace.
- Archived workspace create session is blocked with `workspace_archived`.

Delete uses existing lifecycle semantics. It is exposed externally as lifecycle disposal/deactivation; external callers do not receive or depend on physical storage layout.

## 6. Public Surface Scan

- Target HTTP route count: 23.
- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff: none.
- New target HTTP routes: exactly the D2 overlay.
- New MCP tools: none.
- New CLI commands/subcommands: none.
- No session ingest/query/build target HTTP.
- No quality target HTTP.
- No undeclared workspace/source/build/graph routes.
- Compatibility HTTP retained.

## 7. Tests and Regressions

Executed:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q` -> passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q` -> passed.
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_graph_neighbors.py backend/tests/test_graph_cli_neighbors.py backend/tests/test_target_http_graph_community.py backend/tests/test_graph_cli_community.py backend/tests/test_target_http_graph_query.py backend/tests/test_graph_cli_query.py -q` -> 15 passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q` -> 34 passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q` -> 32 passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q` -> 137 passed.

Frontend build: not touched.

Drawio XML validation: passed after `current-vs-target-gap.drawio` update.

## 8. Documentation Sync

Updated:

- `docs/V1.6/README.md`
- `docs/V1.6/development-plan.md`
- `docs/V1.6/acceptance-plan.md`
- `docs/V1.6/current-vs-target-gap.md`
- `docs/V1.6/current-vs-target-gap.drawio`
- `docs/V1.6/interface-convergence-plan.md`
- `docs/V1.6/target-architecture.md`
- `docs/V1.6/target-http-routes-plan.md`
- `docs/V1.6/public-surface-baseline.md`
- `docs/V1.6/session-graphrag-contract-plan.md`

Planned vs implemented check: D2 is marked completed; D3/E/F remain planned. Quality target HTTP and session ingest/query/build target HTTP are not described as implemented.

## 9. Blocking Issues

None.

## 10. Final Decision

Accepted.

## 11. Next Phase Recommendation

Next phase: V1.6-D3 Session Ingest / Query / Build Contract Planning.

D3 should remain a small contract planning slice and must not be merged with quality target HTTP or console polish.
