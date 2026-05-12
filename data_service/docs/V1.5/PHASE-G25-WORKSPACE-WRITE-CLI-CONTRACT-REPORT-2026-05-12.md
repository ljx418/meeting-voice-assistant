# PhaseG25 Workspace Write CLI Contract Report

日期：2026-05-12

## 范围

PhaseG25 开放 `knowledge workspace create/archive` 写入型治理 alias。

本阶段不新增 MCP tool，不新增 HTTP route，不改变 `data_service` 兼容 CLI 顶层命令。

## 当前命令

```text
knowledge workspace create --workspace-root ./workspaces --name "Research Vault" --owner harness --tag project
knowledge workspace archive --workspace-root ./workspaces --workspace-id research-vault --reason "done"
```

## 实现

- `knowledge workspace create` 转调现有 `knowledge_workspace_create` handler。
- `knowledge workspace archive` 转调现有 `knowledge_workspace_archive` handler。
- `knowledge workspace list/describe` 保持既有行为。
- archive 后 workspace status 进入 `archived`，后续 source/build 写保护继续由现有 handler 负责。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q`：31 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：30 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：132 passed。
- `npm run build`：通过。
- drawio XML 校验：通过。

## 对外能力检查

- 新增公开能力：仅 `knowledge workspace create/archive` CLI alias。
- 未新增 MCP tool。
- 未新增 HTTP route。
- 未改变 `data_service` 兼容 CLI。
- 未改变 workspace MCP / HTTP contract。

## 下一步

PhaseG26 已开放 `knowledge source import/remove` 写入型 CLI contract，PhaseG27 已开放 `knowledge build start/cancel` 写入型 CLI contract，PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
