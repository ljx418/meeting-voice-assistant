# Phase V1.6-C2 Graph Community Report

## 1. Scope

V1.6-C2 只开放 Graph Community minimal read-only surface：

- target HTTP：`GET /api/workspaces/{workspace_id}/graph/community`
- CLI nested command：`knowledge graph community`

本阶段不新增 MCP tool，不新增 CLI top-level command，不处理 graph query/session，不处理 session/quality。

## 2. Baseline

- V1.5 accepted immutable baseline：MCP tools = 40。
- CLI top-level commands：`build / graph / quality / query / source / trace / workspace`。
- V1.6-A Public Surface Guard：accepted。
- V1.6-B1/B2/B3 overlays：accepted。
- V1.6-C1 Graph Neighbors overlay：accepted。
- pre-C2 target HTTP route count：15。
- `/api/v1/knowledge/*` compatibility routes retained。
- `/knowledge` remains service governance console。

## 3. Phase Overlay

Overlay file：`docs/V1.6/public-surface-overlays/v1_6_c2.json`

Allowed target HTTP additions：

- `GET /api/workspaces/{workspace_id}/graph/community`

Allowed CLI nested additions：

- `knowledge graph community`

V1.5 baseline 未修改。

## 4. Implemented Route And Command

- `GET /api/workspaces/{workspace_id}/graph/community`
- `knowledge graph community`

`knowledge graph community` was not present before C2, and is recorded as the only allowed C2 nested CLI addition. CLI top-level commands remain unchanged.

## 5. Contract Summary

Graph community 使用 shared stable projection：

- `community_id` absent：list communities。
- `community_id` present：describe one community。
- `community_id + limit`：`limit` ignored for detail response。
- `limit` 范围：1-100，默认 20。
- `include_members=false` 默认不返回 members。
- `include_members=true` 返回 stable member projection。
- `include_edges` is not opened in C2。
- unknown community returns blocked envelope with `unknown_graph_community`。
- missing graph communities returns blocked envelope with `graph_community_unavailable`。
- response 使用 envelope，包含 `workspace_id`、`artifact_refs`、community stable fields、`warnings`、`next_actions`。
- 默认不暴露 GraphRAG cache path、workspace path、artifact physical path、raw parquet/json path 或其他 internal layout。
- read-only：不触发 build，不触发 GraphRAG index/materialization，不触发 session graph，不触发 quality write，不创建 operation，不修改 source registry，不写入 graph snapshot。

## 6. Public Surface Scan Result

- MCP baseline/current/diff：40 / 40 / none。
- CLI top-level baseline/current/diff：`build / graph / quality / query / source / trace / workspace` / same / none。
- CLI nested allowed addition：`graph.community`。
- HTTP baseline/current/accepted overlays：
  - V1.5 baseline 3 routes。
  - B1 overlay 4 routes。
  - B2 overlay 4 routes。
  - B3 overlay 3 routes。
  - C1 overlay 1 route。
  - C2 overlay 1 route。
- target HTTP final route count：16。
- new MCP tools：none。
- new CLI top-level commands：none。
- new non-C2 HTTP routes：none。
- compatibility HTTP retained。

## 7. Focused Tests

Covered:

- graph community target HTTP route。
- list/detail community。
- `community_id + limit` behavior。
- limit validation。
- `include_members` behavior。
- unknown workspace/community。
- graph community missing。
- no internal path leakage。
- no build/source/session/quality side effects。
- no graph query/session target HTTP。
- CLI graph community command。
- C1/B1/B2/B3 focused tests remain passing。

## 8. Regression Results

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`：5 passed。
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

Planned vs implemented check：C2 marked completed；C3/D/E/F remain planned. Existing MCP graph/session tools remain V1.5 baseline tools, not V1.6-C2 additions.

## 10. Blocking Issues

None.

## 11. Final Decision

accepted。

## 12. Next Phase Recommendation

下一阶段建议进入 V1.6-C3 Graph Query Target HTTP / CLI Minimal Surface。不要直接进入 graph session，不要同时实现 session/quality。
