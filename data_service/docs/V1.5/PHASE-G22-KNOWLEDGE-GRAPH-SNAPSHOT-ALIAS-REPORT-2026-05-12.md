# PhaseG22 Knowledge Graph Snapshot Alias Report

日期：2026-05-12

## 范围

PhaseG22 只开放 `knowledge graph snapshot` 只读 alias。

本阶段不新增 MCP tool，不新增 HTTP route，不开放 `knowledge graph neighbors/community/query/session`。

## 实现

- 新增 `_add_graph_lifecycle_parser`，只挂载到 `_build_knowledge_parser()`。
- `data_service` 兼容 CLI 不新增 `graph` lifecycle alias。
- `knowledge graph snapshot` 转调现有 `handle_session_tool`。
- handler name 固定为 `knowledge_graph_snapshot`。
- CLI arguments 固定 `scope="workspace"`，只读取 workspace graph snapshot。
- 新增 `docs/V1.5/graph-cli-contract.md` 固化 contract 和漂移测试要求。

## 当前命令

```text
knowledge graph snapshot --workspace-root ./workspaces --workspace-id research-vault --max-nodes 200
```

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q`：28 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：30 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：129 passed。
- `npm run build`：通过。
- drawio XML 校验：通过。

## 对外能力检查

- 新增公开能力：仅 `knowledge graph snapshot` CLI alias。
- 未新增 MCP tool。
- 未新增 HTTP route。
- 未改变 `data_service` 兼容 CLI 顶层命令。
- 未开放 `knowledge graph neighbors/community/query/session`。
- 未开放 `knowledge distill/trace`。

## 下一步

后续按 PhaseG23 已完成 `knowledge trace source` 只读 alias，PhaseG24 已固化 `knowledge graph` advanced 子命令迁移窗口，PhaseG25 已开放 `knowledge workspace create/archive` 写入型 CLI alias，PhaseG26 已开放 `knowledge source import/remove` 写入型 CLI alias，PhaseG27 已开放 `knowledge build start/cancel` 写入型 CLI alias，PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
