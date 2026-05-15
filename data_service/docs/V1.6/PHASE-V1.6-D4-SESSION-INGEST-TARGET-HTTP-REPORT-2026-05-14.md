# V1.6-D4 Session Ingest Target HTTP Report

Date: 2026-05-14

## 1. Scope

V1.6-D4 only opens session ingest target HTTP:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`

D4 does not add MCP tools, CLI top-level commands, CLI nested commands, session query/build target HTTP, quality target HTTP, or compatibility HTTP routes.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D1/D2/D3 accepted.
- Target HTTP pre-D4 route count: 23.
- MCP tool count: 40.
- CLI top-level/nested inventory: unchanged.
- `/api/v1/knowledge/*` compatibility routes retained.

## 3. Phase Overlay

Overlay file:

- `docs/V1.6/public-surface-overlays/v1_6_d4.json`

Allowed addition:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`

V1.5 baseline was not modified.

## 4. Implemented Route

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`

Implementation uses `SessionKnowledgeService.ingest(...)` through the stable projection helper `session_ingest_contract.py`.

## 5. Contract Summary

Request fields are limited to existing session ingest semantics:

- `source_type`
- `content_format`
- `title`
- `content`
- `records`
- `metadata`
- `related_source_ids`
- `source_refs`
- `auto_link`
- `allow_closed_write`

Content and records are mutually exclusive in the target HTTP contract. At least one of them is required. `related_paths` is rejected by default and is not part of the D4 stable contract.

Returned source IDs are session-scoped. `source_id` / `session_source_id` must not be assumed to be a workspace source registry ID.

Artifact refs use stable non-path refs:

- `session-source://{session_id}/{source_id}`

D4 session ingest does not trigger session query, session build, GraphRAG index, GraphRAG materialization, quality write, or build operation creation.

Default responses sanitize metadata and do not expose internal path/layout fields.

## 6. Public Surface Scan

- Target HTTP route count: 24.
- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff: none.
- New MCP tools: none.
- New CLI commands/subcommands: none.
- New non-D4 HTTP routes: none.
- Session query target HTTP: not opened.
- Session build target HTTP: not opened.
- Quality target HTTP: not opened.
- Compatibility HTTP: retained.

## 7. Tests And Regressions

Passed:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q` -> 5 passed.
- `python3 -m pytest backend/tests/test_target_http_session_ingest.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_session_ingest_query_build_contract_plan.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` -> 2 passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q` -> 3 passed.
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q` -> 2 passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q` -> 34 passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q` -> 32 passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q` -> 137 passed.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"` -> passed.

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
- `docs/V1.6/session-ingest-query-build-contract-plan.md`

Planned vs implemented status was updated: D4 is accepted; D5/D6/E/F remain planned.

## 9. Blocking Issues

None.

## 10. Final Decision

accepted

## 11. Next Phase Recommendation

Next phase should be V1.6-D5 Session Query Target HTTP Minimal Surface.

Do not implement session build in D5. Do not enter quality target HTTP yet.
