# Phase V1.6-D1 Session GraphRAG Contract Report

## 1. Scope

V1.6-D1 only does contract planning / hardening. It does not add public surface, session lifecycle target HTTP, quality target HTTP, MCP tools, CLI commands or business capability.

D1 does not implement full Session GraphRAG public contract. It hardens inventory, stable projection, error envelope, artifact_ref rules and regression guard.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B1/B2/B3/C1/C2/C3/C4 are accepted.
- Target HTTP current route count remains 18.
- MCP tool count remains 40.
- CLI top-level commands remain `build / graph / quality / query / source / trace / workspace`.
- CLI nested inventory is unchanged from the C4 accepted baseline.
- `/api/v1/knowledge/*` compatibility routes remain retained.

## 3. Contract Inventory Summary

Added `docs/V1.6/session-graphrag-contract-plan.md`.

The matrix covers:

- V1.5 MCP session tools: `knowledge_session_create/get/list/close/delete/ingest/build_start/build_status/build_cancel/query`, plus session graph-related MCP tools `knowledge_graph_snapshot`, `knowledge_graph_neighbors`, `knowledge_community_summary`, and `knowledge_actor_summary`.
- C4 target HTTP graph-scoped inspection route: `GET /api/workspaces/{workspace_id}/graph/session`.
- C4 CLI graph-scoped inspection command: `knowledge graph session`.
- Compatibility HTTP session surfaces as retained compatibility, not D1 target contract expansion.
- Planned session lifecycle target HTTP: `/api/workspaces/{workspace_id}/sessions*`, not opened in D1.
- Planned quality target HTTP: not opened in D1.

The matrix records request schema summary, response schema summary, error schema summary, artifact_ref behavior, operation_id behavior, side effects, path exposure risk, owner/helper and next phase candidate.

## 4. Stable Projection Audit

C4 graph session target HTTP and CLI continue to use the shared `graph_session_contract.py` projection. D1 did not change accepted C4 behavior.

Stable fields confirmed:

- `workspace_id`
- `session_id`
- `operation_id` only where existing session operation lifecycle uses a real operation
- `artifact_ref` / `artifact_refs`
- `status`
- `node_count`
- `edge_count`
- `community_count`
- `created_at`
- `updated_at`
- `warnings`
- `next_actions`
- normalized `error`

Focused tests compare target HTTP and CLI core JSON projection for graph session detail and verify internal path/layout keys are absent.

## 5. Error Contract

D1 fixed current error shapes without defining a new envelope layout:

- unknown workspace: target HTTP current helper returns HTTP 404.
- unknown session: status `blocked`, `data.error.code = unknown_session_id`.
- known session but missing graph artifact: status `blocked`, `data.error.code = session_graph_no_artifact`.
- cross-workspace session: normalized blocked/not-found behavior without leaking another workspace graph.
- invalid limit: target HTTP HTTP 400; CLI exits with code 2.
- invalid operation_id: existing MCP session build tools retain normalized `unknown_operation_id`.
- artifact unavailable: blocked/error payload, no automatic build trigger.

## 6. Artifact Ref Contract

D1 documents and tests that Session GraphRAG `artifact_ref`:

- is not an absolute path.
- is not a raw relative filesystem path.
- does not contain workspace root.
- does not expose raw parquet/json/md physical path.
- uses stable refs such as `graph-session://{workspace_id}/{session_id}`.
- should be resolved through the service rather than direct filesystem reads.

Debug / console-only path fields remain non-contract.

## 7. Public Surface Scan

- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff from C4 baseline: none.
- HTTP diff from C4 baseline: none.
- Target HTTP remains 18 routes.
- No `/api/workspaces/{workspace_id}/sessions*` routes.
- No quality target HTTP routes.
- No hidden route/tool/command diff.

## 8. Tests And Regressions

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`: passed.
- `python3 -m pytest backend/tests/test_session_graphrag_contract.py -q`: passed.
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q`: passed.
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q`: passed.
- C1/C2/C3 graph focused tests: passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q`: passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q`: passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`: passed.
- drawio XML validation: passed.
- frontend build: not touched.

## 9. Documentation Sync

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

Added:

- `docs/V1.6/session-graphrag-contract-plan.md`
- `docs/V1.6/PHASE-V1.6-D1-SESSION-GRAPHRAG-CONTRACT-REPORT-2026-05-14.md`

Planned vs implemented check: D1 marked completed; D2/E/F remain planned. D1 is not full Session GraphRAG implementation.

## 10. Blocking Issues

None.

## 11. Final Decision

accepted.

## 12. Next Phase Recommendation

If accepted, next phase should enter `V1.6-D2 Session Lifecycle Target HTTP Minimal Surface`.

D2 must remain small. It must not be combined with quality target HTTP or console polish.
