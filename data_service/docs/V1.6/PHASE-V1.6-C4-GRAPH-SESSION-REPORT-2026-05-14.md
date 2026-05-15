# Phase V1.6-C4 Graph Session Target HTTP / CLI Report

## 1. Scope

V1.6-C4 只开放 graph-scoped session graph artifact inspection 的最小 read-only surface。

本阶段不开放 session lifecycle target HTTP，不进入完整 Session GraphRAG public contract，不处理 quality target HTTP，不新增 MCP tool，不新增 CLI top-level command。

## 2. Baseline

- V1.5 accepted immutable baseline：MCP tools = 40；CLI top-level = `build / graph / quality / query / source / trace / workspace`；target HTTP baseline = 3 routes。
- V1.6-A Public Surface Guard：accepted。
- V1.6-B1/B2/B3 overlays：accepted。
- V1.6-C1/C2/C3 overlays：accepted。
- Pre-C4 accepted target HTTP route count：17。

## 3. Phase Overlay

Overlay file：`docs/V1.6/public-surface-overlays/v1_6_c4.json`。

Allowed target HTTP addition：

- `GET /api/workspaces/{workspace_id}/graph/session`

Allowed CLI nested addition：

- `knowledge graph session`

V1.5 baseline 未修改。

## 4. Implemented Route And Command

- Target HTTP：`GET /api/workspaces/{workspace_id}/graph/session`
- CLI：`knowledge graph session`

`knowledge graph session` 是 C4 新增 nested command；CLI top-level commands 未变化。

## 5. Contract Summary

Route query params：

- `session_id` optional。缺失时只列出现有 session graph artifact summaries；存在时只描述单个现有 session graph artifact summary。
- `limit` default 20，range 1-100。
- `include_nodes` default false。
- `include_edges` default false。
- `node_limit` default 50，range 1-200。
- `edge_limit` default 100，range 1-500。

Unknown session 返回 normalized `unknown_session_id` blocked error。已知 session 但 graph artifact 缺失返回 `session_graph_no_artifact` blocked error，并且不会触发 build。Cross-workspace session lookup 返回 normalized not-found / blocked，不泄露其他 workspace session graph。

输出只保留稳定字段：`workspace_id`、`session_id`、`status`、`node_count`、`edge_count`、`community_count`、`artifact_ref`、`created_at`、`updated_at`、可选 capped `nodes[]` / `edges[]`、envelope/error/warnings/next_actions。

默认 response 不暴露 `workspace_path`、`root_path`、`filesystem_path`、`artifact_physical_path`、`graphrag_cache_path`、`cache_path`、`physical_path`、`internal_path`、`debug_paths`、raw parquet/json path、source/original/local path 或 llmwiki physical path。

## 6. Public Surface Scan Result

- MCP baseline/current/diff：40 / 40 / none。
- CLI top-level baseline/current/diff：`build / graph / quality / query / source / trace / workspace` / same / none。
- CLI nested allowed addition：`graph.session`。
- target HTTP baseline：V1.5 3 routes。
- accepted overlays：B1 +4，B2 +4，B3 +3，C1 +1，C2 +1，C3 +1，C4 +1。
- target HTTP current route count：18。
- New MCP tools：none。
- New CLI top-level commands：none。
- New non-C4 HTTP routes：none。
- `/api/v1/knowledge/*` compatibility routes：retained。

## 7. Boundary Result

- No session lifecycle target HTTP route opened。
- No quality target HTTP route opened。
- No new workspace/source/build/graph neighbors/community/query route opened。
- Graph session inspection is read-only。
- No build/index/materialization/quality side effect。
- No operation creation。
- No source registry mutation。
- No graph snapshot write。
- No session lifecycle state update。
- `/knowledge` remains service governance console。
- No upper-layer production dependency was introduced。

## 8. Focused Tests

- `backend/tests/test_target_http_graph_session.py`：passed, 3 tests。
- `backend/tests/test_graph_cli_session.py`：passed, 2 tests。
- C1/C2/C3 graph focused tests：passed。
- B1/B2/B3 focused tests：passed。

Focused tests cover list/detail behavior, unknown workspace/session, missing artifact, cross-workspace isolation, bounded limits, `include_nodes` / `include_edges`, path leakage prevention, no side effects, CLI JSON projection, and no session lifecycle / quality target HTTP route opening。

## 9. Regression Results

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`：5 passed。
- `python3 -m pytest backend/tests/test_target_http_graph_session.py -q`：3 passed。
- `python3 -m pytest backend/tests/test_graph_cli_session.py -q`：2 passed。
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
- Frontend build：not touched。
- Drawio XML validation：passed after documentation sync。

## 10. Documentation Sync

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

Docs distinguish immutable V1.5 baseline, accepted B/C overlays, completed C4, and planned D/E/F. Planned capabilities are not described as implemented。

## 11. Blocking Issues

None。

## 12. Final Decision

accepted。

Next phase recommendation：enter `V1.6-D1 Session GraphRAG Public Contract planning / contract hardening`。Do not directly enter full V1.6-D implementation, and do not implement quality target HTTP in the same phase。
