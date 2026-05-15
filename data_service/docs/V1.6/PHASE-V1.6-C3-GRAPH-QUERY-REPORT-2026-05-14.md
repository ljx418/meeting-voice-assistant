# Phase V1.6-C3 Graph Query Report

## 1. Scope

V1.6-C3 只开放 Graph Query minimal read-only surface：

- target HTTP：`GET /api/workspaces/{workspace_id}/graph/query`
- CLI nested command：`knowledge graph query`

本阶段不新增 MCP tool，不新增 CLI top-level command，不处理 graph session，不处理 session/quality，不修改 B1/B2/B3/C1/C2 已 accepted 行为。

## 2. Baseline

- V1.5 accepted immutable baseline：unchanged。
- V1.6-A/B1/B2/B3/C1/C2：accepted。
- MCP tool count：40。
- CLI top-level commands：`build / graph / quality / query / source / trace / workspace`。
- pre-C3 target HTTP route count：16。
- `/api/v1/knowledge/*` compatibility routes retained。

## 3. Phase Overlay

Overlay file：`docs/V1.6/public-surface-overlays/v1_6_c3.json`

Allowed target HTTP addition：

- `GET /api/workspaces/{workspace_id}/graph/query`

Allowed CLI nested addition：

- `knowledge graph query`

V1.5 baseline 未修改。

## 4. Implemented Route And Command

- `GET /api/workspaces/{workspace_id}/graph/query`
- `knowledge graph query`

`knowledge graph query` was not present before C3, and is recorded as the only allowed C3 nested CLI addition. CLI top-level commands remain unchanged.

## 5. Contract Summary

- request：`q` 必填，`top_k` bounded to 1-50。
- optional projection flags：`include_nodes` default true，`include_edges` default true，`include_communities` default false。
- graph artifacts missing：returns normalized blocked envelope with `graph_query_unavailable`，does not trigger build。
- stable output：`workspace_id`、`query`、`top_k`、`answer/summary`、`nodes[]`、`edges[]`、`communities[]` when requested、`artifact_refs`、`warnings`、`next_actions`。
- read-only：不触发 build/index/materialization/session graph/quality write，不创建 operation，不修改 source registry，不写入 graph snapshot。
- default response 不暴露 workspace path、GraphRAG cache path、DB path、artifact physical path、source/original/local path 或 raw parquet/json path。

## 6. Public Surface Scan Result

- MCP baseline/current/diff：40 / 40 / none。
- CLI top-level baseline/current/diff：`build / graph / quality / query / source / trace / workspace` / same / none。
- CLI nested allowed addition：`graph.query`。
- target HTTP current surface：
  - V1.5 baseline 3 routes。
  - B1 overlay 4 routes。
  - B2 overlay 4 routes。
  - B3 overlay 3 routes。
  - C1 overlay 1 route。
  - C2 overlay 1 route。
  - C3 overlay 1 route。
  - total：17 routes。
- new MCP tools：none。
- new CLI top-level commands：none。
- new non-C3 HTTP routes：none。
- graph session、session target HTTP、quality target HTTP：not opened。

## 7. Focused Tests

Covered:

- graph query target HTTP stable payload。
- graph artifacts exists/missing behavior。
- `q` required and `top_k` validation。
- include nodes/edges/communities projection policy。
- no internal path/layout leakage。
- no build operation creation。
- no source registry mutation。
- no graph session/session/quality target HTTP route opened。
- CLI `knowledge graph query` inventory and JSON payload。
- C1/C2/B1/B2/B3 focused tests still pass。

## 8. Regression Results

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`：5 passed。
- `python3 -m pytest backend/tests/test_target_http_graph_query.py -q`：3 passed。
- `python3 -m pytest backend/tests/test_graph_cli_query.py -q`：2 passed。
- `python3 -m pytest backend/tests/test_target_http_graph_community.py -q`：3 passed。
- `python3 -m pytest backend/tests/test_graph_cli_community.py -q`：2 passed。
- `python3 -m pytest backend/tests/test_target_http_graph_neighbors.py -q`：3 passed。
- `python3 -m pytest backend/tests/test_graph_cli_neighbors.py -q`：2 passed。
- `python3 -m pytest backend/tests/test_target_http_build.py -q`：4 passed。
- `python3 -m pytest backend/tests/test_target_http_source.py -q`：5 passed。
- `python3 -m pytest backend/tests/test_target_http_workspace.py -q`：5 passed。
- `python3 -m pytest backend/tests/test_data_service_api.py -q`：34 passed。
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q`：32 passed。
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：137 passed。
- frontend `npm run build`：not touched。
- drawio XML validation：passed。

## 9. Documentation Sync

Updated:

- `docs/V1.6/README.md`
- `docs/V1.6/development-plan.md`
- `docs/V1.6/acceptance-plan.md`
- `docs/V1.6/current-vs-target-gap.md`
- `docs/V1.6/current-vs-target-gap.drawio`
- `docs/V1.6/target-http-routes-plan.md`
- `docs/V1.6/interface-convergence-plan.md`
- `docs/V1.6/public-surface-baseline.md`
- `docs/V1.6/target-architecture.md`

Planned vs implemented check：C3 marked completed；graph session、D/E/F remain planned. Existing MCP graph/session tools remain V1.5 baseline tools, not V1.6-C3 additions.

## 10. Blocking Issues

None.

## 11. Final Decision

accepted。

## 12. Next Phase Recommendation

下一阶段建议进入 V1.6-C4 Graph Session Target HTTP / CLI Minimal Surface。不要直接进入完整 session/quality，不要同时实现 session target HTTP 和 quality write target HTTP。
