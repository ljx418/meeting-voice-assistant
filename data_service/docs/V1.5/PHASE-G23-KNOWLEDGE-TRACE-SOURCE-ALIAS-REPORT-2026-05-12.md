# PhaseG23 Knowledge Trace Source Alias Report

日期：2026-05-12

## 范围

PhaseG23 只开放 `knowledge trace source` 只读 alias。

本阶段不新增 MCP tool，不新增 HTTP route，不开放 `knowledge_source_trace` MCP tool，不改变 `data_service` 兼容 CLI 顶层命令。

## 实现

- 新增 `_add_trace_lifecycle_parser`，只挂载到 `_build_knowledge_parser()`。
- `knowledge trace` 当前只允许 `source` 子命令。
- `knowledge trace source` 复用 `source_trace_payload` shared serializer。
- 输出字段与 HTTP `/api/v1/knowledge/source/trace` 保持一致。
- 新增 `docs/V1.5/trace-cli-contract.md` 固化 contract 和漂移测试要求。

## 当前命令

```text
knowledge trace source --workspace-root ./workspaces --workspace-id research-vault --source-id source-123 --limit 12
```

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q`：29 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：30 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：130 passed。
- `npm run build`：通过。
- drawio XML 校验：通过。

## 对外能力检查

- 新增公开能力：仅 `knowledge trace source` CLI alias。
- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 `data_service trace` 兼容 CLI。
- 未开放 `knowledge_source_trace` MCP tool。
- 未改变 Source Trace 响应字段集合。

## 下一步

PhaseG24 已固化 `knowledge graph` advanced 子命令迁移窗口，PhaseG25 已开放 `knowledge workspace create/archive` 写入型 CLI alias，PhaseG26 已开放 `knowledge source import/remove` 写入型 CLI alias，PhaseG27 已开放 `knowledge build start/cancel` 写入型 CLI alias，PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
