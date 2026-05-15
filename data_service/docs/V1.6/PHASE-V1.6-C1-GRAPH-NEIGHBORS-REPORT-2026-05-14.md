# Phase V1.6-C1 Graph Neighbors Report

## 1. Scope

V1.6-C1 只开放 Graph Neighbors minimal surface：

- target HTTP：`GET /api/workspaces/{workspace_id}/graph/neighbors`
- CLI nested command：`knowledge graph neighbors`

本阶段不新增 MCP tool，不新增 CLI top-level command，不开放 graph community/query/session、session target HTTP 或 quality target HTTP。

## 2. Baseline

- V1.5 accepted immutable baseline：MCP tools = 40。
- CLI top-level commands：`build / graph / quality / query / source / trace / workspace`。
- V1.6-A Public Surface Guard：accepted。
- V1.6-B1/B2/B3 overlays：accepted。
- pre-C1 target HTTP route count：14。
- `/api/v1/knowledge/*` compatibility routes retained。
- `/knowledge` remains service governance console。

## 3. Phase Overlay

Overlay file：`docs/V1.6/public-surface-overlays/v1_6_c1.json`

Allowed target HTTP additions：

- `GET /api/workspaces/{workspace_id}/graph/neighbors`

Allowed CLI nested additions：

- `knowledge graph neighbors`

V1.5 baseline 未修改。

## 4. Implemented Route And Command

- `GET /api/workspaces/{workspace_id}/graph/neighbors`
- `knowledge graph neighbors`

`knowledge graph neighbors` was not present before C1, and is recorded as the only allowed nested CLI addition. CLI top-level commands remain unchanged.

## 5. Contract Summary

Graph neighbors 使用 shared stable projection：

- `node_id` / `entity_id` one-of required；两者同时提供返回 normalized validation error。
- `depth` 范围：1-3，默认 1。
- `max_nodes` 范围：1-500，默认 80。
- response 使用 envelope，包含 `workspace_id`、`artifact_refs`、`nodes[]`、`edges[]`、`depth`、`max_nodes`、`truncated`。
- nodes / edges 只返回稳定字段，不默认暴露 GraphRAG cache path、workspace path、artifact physical path、raw parquet/json path 或其他 internal layout。
- read-only：不触发 build，不触发 GraphRAG index，不触发 session graph，不触发 quality write，不创建 operation，不修改 source registry。

## 6. Public Surface Scan Result

- MCP baseline/current/diff：40 / 40 / none。
- CLI top-level baseline/current/diff：`build / graph / quality / query / source / trace / workspace` / same / none。
- CLI nested allowed addition：`graph.neighbors`。
- HTTP baseline/current/accepted overlays：
  - V1.5 baseline 3 routes。
  - B1 overlay 4 routes。
  - B2 overlay 4 routes。
  - B3 overlay 3 routes。
  - C1 overlay 1 route。
- target HTTP final route count：15。
- new MCP tools：none。
- new CLI top-level commands：none。
- new non-C1 HTTP routes：none。
- compatibility HTTP retained。

## 7. Focused Tests

Covered:

- graph neighbors target HTTP route。
- graph artifact exists / missing。
- node_id / entity_id validation。
- unknown workspace / node。
- depth / max_nodes bounds。
- no internal path leakage。
- no build/source/session/quality side effects。
- CLI graph neighbors command。
- B1/B2/B3 focused tests remain passing。
- source trace unchanged。
- API key boundary smoke。

## 8. Regression Results

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`：5 passed。
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

Planned vs implemented check：C1 marked completed；C2/C3/D/E/F remain planned. Existing MCP graph/session tools remain V1.5 baseline tools, not V1.6-C1 additions.

## 10. Blocking Issues

None.

## 11. Final Decision

accepted。

## 12. Next Phase Recommendation

下一阶段建议进入 V1.6-C2 Graph Community Target HTTP / CLI Minimal Surface。不要直接进入完整 V1.6-C，不要同时实现 graph query/session/quality。
