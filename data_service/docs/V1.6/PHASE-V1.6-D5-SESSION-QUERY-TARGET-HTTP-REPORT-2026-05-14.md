# V1.6-D5 Session Query Target HTTP Report

Date: 2026-05-14

## 1. Scope

D5 only opens session query target HTTP:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`

D5 is read-only. It adds no MCP tool, no CLI top-level command, no CLI nested command, no session build target HTTP, and no quality target HTTP.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D1/D2/D3/D4 were accepted before D5.
- Pre-D5 target HTTP route count: 24.
- MCP tool count: 40.
- CLI top-level and nested inventory unchanged.
- `/api/v1/knowledge/*` compatibility routes retained.

## 3. Phase Overlay

D5 overlay: `docs/V1.6/public-surface-overlays/v1_6_d5.json`

Allowed addition:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`

V1.5 baseline was not modified.

## 4. Implemented Route

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`

The route reuses `SessionKnowledgeService.query_session(...)` through `session_query_contract.py`. It does not add or alter MCP session tools.

## 5. Contract Summary

Request fields:

- `query`: required non-empty string, max length 4096.
- `top_k`: optional, default 8, range 1-50.
- Unsupported request fields are rejected by the target HTTP request model.
- `include_workspace_context` is not part of the D5 target HTTP contract.

Projection:

- Stable fields include `workspace_id`, `session_id`, `query`, `top_k`, `answer`, `results` / `items`, optional safely projected `nodes` / `edges` / `communities`, `artifact_ref`, `warnings`, and `next_actions`.
- `artifact_ref` uses a stable non-path `graph-session://...` reference.
- Raw GraphRAG rows, raw dataframe rows, raw prompts, raw model messages, embedding vectors, provider raw responses, full diagnostics, and internal path/layout fields are not returned.

Read-only/no-side-effect proof:

- Focused tests fingerprint session ingest storage and related lifecycle directories before and after query.
- Query does not create build operations, session build routes, quality writes, graph cache artifacts, temporary graph artifacts, or workspace source registry changes.
- Missing graph/session artifact returns normalized blocked/no-artifact style behavior and does not auto-build.

Error behavior:

- Unknown workspace/session, cross-workspace session access, empty query, invalid `top_k`, disposed session, and missing artifact are normalized through the existing envelope/error helper.

## 6. Public Surface Scan

- Target HTTP count: 25.
- HTTP diff from D4 accepted surface: exactly one D5 route.
- MCP baseline/current/diff: 40 / 40 / none.
- CLI top-level diff: none.
- CLI nested diff: none.
- Session build target HTTP: not opened.
- Quality target HTTP: not opened.
- Compatibility HTTP: retained.
- New non-D5 HTTP routes: none.

## 7. Tests and Regressions

Passed:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q` -> 5 passed.
- `python3 -m pytest backend/tests/test_target_http_session_query.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_target_http_session_ingest.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_session_ingest_query_build_contract_plan.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` -> 2 passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q` -> 2 passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q` -> 34 passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q` -> 32 passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q` -> 137 passed.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"` -> `drawio xml ok`.

Frontend build: not touched.

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
- `docs/V1.6/session-ingest-query-build-contract-plan.md`

Planned vs implemented check:

- D5 is accepted.
- D6/E/F remain planned.
- Session build target HTTP remains not opened.
- Quality target HTTP remains not opened.

## 9. Blocking Issues

None.

## 10. Final Decision

Accepted.

## 11. Next Phase Recommendation

Next phase should be V1.6-D6 Session Build Target HTTP Minimal Surface.

Do not enter quality target HTTP yet.
