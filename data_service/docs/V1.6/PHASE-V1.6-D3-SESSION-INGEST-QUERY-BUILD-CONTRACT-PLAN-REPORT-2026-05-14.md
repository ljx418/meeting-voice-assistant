# Phase V1.6-D3 Session Ingest / Query / Build Contract Plan Report

## 1. Scope

D3 is a planning and contract hardening phase only. It opens no public surface.

D3 only adds contract inventory, future phase split, guard tests, documentation sync and this report. It does not open session ingest/query/build target HTTP, quality target HTTP, new MCP tools, CLI commands or CLI subcommands.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D1/D2 accepted.
- Target HTTP route count remains 23.
- MCP tool count remains 40.
- CLI top-level and nested diff remains none.
- `/api/v1/knowledge/*` compatibility routes retained.

## 3. Inventory Summary

MCP session ingest/query/build tools already exist in the V1.5 baseline:

- `knowledge_session_ingest`
- `knowledge_session_query`
- `knowledge_session_build_start`
- `knowledge_session_build_status`
- `knowledge_session_build_cancel`

CLI session surfaces:

- `knowledge graph session` exists as C4 graph-scoped artifact inspection.
- D3 adds no session ingest/query/build CLI command.

Target HTTP current status:

- D2 lifecycle create/list/get/close/delete accepted.
- Session ingest/query/build target HTTP remains planned / not opened.
- C4 `/graph/session` remains graph-scoped inspection and is not session query/build.

## 4. Contract Plan Summary

The contract matrix is documented in `docs/V1.6/session-ingest-query-build-contract-plan.md`.

Future split:

- D4 candidate: Session Ingest Target HTTP Minimal Surface.
- D5 candidate: Session Query Target HTTP Minimal Surface.
- D6 candidate: Session Build Target HTTP Minimal Surface.

Ingest future contract must define request fields, whether operation_id is used, artifact_ref shape, side effects, and graph materialization boundary.

Query future contract must remain read-only by default, avoid operation_id unless existing semantics require it, and define answer/graph context and missing artifact behavior.

Build future contract must use real operation_id from existing session operation lifecycle, define terminal cancel semantics and cross-workspace operation isolation.

All future contracts must use stable IDs and artifact refs, not physical paths.

## 5. Public Surface Guard Result

- HTTP diff from D2 accepted surface: none.
- MCP diff: none.
- CLI diff: none.
- Target HTTP route count: 23.
- No session ingest target HTTP route.
- No session query target HTTP route.
- No session build target HTTP route.
- No quality target HTTP route.
- No graph route additions.

## 6. Tests and Regressions

Executed:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` -> passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q` -> passed.
- `python3 -m pytest backend/tests/test_session_ingest_query_build_contract_plan.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` -> passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q` -> passed.
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q` -> passed.
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q` -> passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q` -> 34 passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q` -> 32 passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q` -> 137 passed.

Frontend build: not touched.

Drawio XML validation: passed after `current-vs-target-gap.drawio` update.

## 7. Documentation Sync

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

Planned vs implemented check: D3 is marked completed; D4/D5/D6/E/F remain planned. Session ingest/query/build target HTTP and quality target HTTP are not described as implemented.

## 8. Blocking Issues

None.

## 9. Final Decision

Accepted.

## 10. Next Phase Recommendation

Next phase: V1.6-D4 Session Ingest Target HTTP Minimal Surface.

D4 must not implement query/build together and must not enter quality target HTTP.
