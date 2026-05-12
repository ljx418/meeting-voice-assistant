# PhaseG24 Graph Advanced CLI Migration Window Report

日期：2026-05-12

## 范围

PhaseG24 固化 `knowledge graph` advanced 子命令迁移窗口。

本阶段不新增 MCP tool，不新增 HTTP route，不开放 `knowledge graph neighbors/community/query/session`。

## planned advanced CLI

```text
knowledge graph neighbors --workspace-root ./workspaces --workspace-id research-vault --node-id node-123 --limit 20
knowledge graph community --workspace-root ./workspaces --workspace-id research-vault --community-id community-123
knowledge graph query --workspace-root ./workspaces --workspace-id research-vault "graph question" --top-k 8
knowledge graph session --workspace-root ./workspaces --workspace-id research-vault --session-id session-123 --max-nodes 200
```

## 实现

- 扩展 `docs/V1.5/graph-cli-contract.md`，记录 advanced 子命令 planned contract。
- 新增 drift test，确认 `knowledge graph` 当前仍只允许 `snapshot`。
- 新增 drift test，确认 `data_service` 兼容 CLI 仍不新增 `graph` 顶层命令。
- 明确后续开放任一 advanced 子命令时必须单独设计、单独验收。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q`：30 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：30 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：131 passed。
- `npm run build`：通过。
- drawio XML 校验：通过。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI command。
- 未开放 `knowledge graph neighbors/community/query/session`。
- `knowledge graph` 当前仍只开放 `snapshot`。
- 未改变 `knowledge graph snapshot` 输出字段。

## 下一步

PhaseG25 已开放 `knowledge workspace create/archive` 写入型 CLI alias，PhaseG26 已开放 `knowledge source import/remove` 写入型 CLI alias，PhaseG27 已开放 `knowledge build start/cancel` 写入型 CLI alias，PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
