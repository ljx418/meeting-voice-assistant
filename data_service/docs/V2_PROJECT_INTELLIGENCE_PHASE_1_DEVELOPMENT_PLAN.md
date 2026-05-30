# V2 Phase 1 Development Plan: Codebase Registry + Artifact Foundation

## Summary

Phase 1 只实现 PR1：把本地代码仓库登记为独立 `codebase` asset，并通过 HTTP / MCP / CLI 暴露最小导入、列表、详情、归档能力。该阶段不做 snapshot、public surface、symbol extraction、mapping、Agent Context Pack，也不改现有 source registry。

## Architecture Changes

新增独立 V2 package：

- `backend/data_service/code_assets/models.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/data_service/code_assets/security.py`
- `backend/data_service/code_assets/registry.py`

新增边界模块：

- `backend/app/api/v1/code_assets.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`

只允许最小修改：

- `backend/app/api/__init__.py`
- `backend/data_service/mcp_tool_registry.py`
- `backend/data_service/mcp_dispatcher.py`
- `backend/data_service/__main__.py`

禁止修改：

- `backend/app/api/v1/data_service.py`
- `backend/data_service/service.py`
- existing source registry schema / source import behavior

## Data Contract

`codebase.json` 内部持久化结构必须包含：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `name`
- `root_path`
- `status`
- `created_at`
- `updated_at`
- `archived_at`
- `archive_reason`
- `metadata`
- `scan_policy`

默认 external response 不返回 absolute `root_path`，只返回 `codebase_id`, `name`, `status`, `artifact_refs`, `warnings`, `next_actions` 等安全字段。

## Phase Scope

Phase 1 实现：

- codebase import
- codebase list
- codebase describe
- codebase archive
- duplicate import idempotency
- codebase_id conflict detection
- path allow-list validation
- HTTP / MCP / CLI 最小入口

Phase 1 不实现：

- repo snapshot
- public surface inventory
- Python symbol index
- code evidence trace
- Agent Context Pack
- DevWiki / code graph / quality extension

