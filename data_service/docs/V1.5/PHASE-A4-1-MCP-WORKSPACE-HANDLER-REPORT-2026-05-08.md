# V1.5 PhaseA4.1：Workspace MCP Handler 模块化报告

日期：2026-05-08

## 目标

完成 V1.5-PhaseA 的第四个小切片：把 workspace lifecycle MCP tool schema 和 handler 从 `mcp_stdio.py` 中拆出，继续压缩 stdio 入口职责，同时保持 workspace create/list/describe/archive 的外部契约兼容。

## 本阶段变更

- 新增 `backend/data_service/mcp_workspace_tools.py`。
- `mcp_stdio.py` 改为通过 `WORKSPACE_TOOL_SPECS` 注册 workspace lifecycle 工具。
- `mcp_stdio.py` 改为通过 `handle_workspace_tool(...)` 分发 workspace MCP 调用。
- 保留以下 tool 的输入与输出：
  - `knowledge_workspace_create`
  - `knowledge_workspace_list`
  - `knowledge_workspace_describe`
  - `knowledge_workspace_archive`
- 共享 helper 仍由 `mcp_stdio.py` 注入，避免本阶段引入 workspace root、meta、layout、envelope 行为变化。

## 验收结果

### 自动化回归

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_stdio.py backend/data_service/mcp_workspace_tools.py backend/data_service/mcp_core_tools.py backend/data_service/mcp_quality_tools.py backend/data_service/mcp_session_tools.py
```

结果：通过。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：

```text
16 passed
```

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

```text
94 passed
```

### 出门验证

通过 MCP handler 直接执行：

```text
knowledge_workspace_create
-> knowledge_workspace_describe
-> knowledge_workspace_list(owner/tag)
-> knowledge_workspace_archive
-> knowledge_workspace_describe
```

结果摘要：

```json
{
  "workspace_id": "phasea4-workspace",
  "create_status": "ok",
  "describe_status": "ok",
  "listed_count": 1,
  "archive_status": "ok",
  "archived_workspace_status": "archived",
  "describe_after_layout": true
}
```

## 当前边界

本阶段确认了当前 workspace contract 的一个既有约束：如果创建 workspace 时显式传入自定义 `root`，后续仅凭 `workspace_id` 解析时仍依赖同一个 `DATA_SERVICE_WORKSPACE_ROOT`。出门验证已在导入 MCP server 前设置 `DATA_SERVICE_WORKSPACE_ROOT`，保证 create/list/describe/archive 使用同一 root。

下一步 PhaseA4.2 应拆分 Source MCP handler：`knowledge_source_import`、`knowledge_source_list`、`knowledge_source_remove`。
