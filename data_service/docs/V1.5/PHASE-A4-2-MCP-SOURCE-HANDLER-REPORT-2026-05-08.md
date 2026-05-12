# V1.5 PhaseA4.2：Source MCP Handler 模块化报告

日期：2026-05-08

## 目标

完成 V1.5-PhaseA 的第五个小切片：把 source registry MCP tool schema 和 handler 从 `mcp_stdio.py` 中拆出，继续压缩 stdio 入口职责，同时保持 source import/list/remove 的外部契约兼容。

## 本阶段变更

- 新增 `backend/data_service/mcp_source_tools.py`。
- `mcp_stdio.py` 改为通过 `SOURCE_TOOL_SPECS` 注册 source registry 工具。
- `mcp_stdio.py` 改为通过 `handle_source_tool(...)` 分发 source MCP 调用。
- 保留以下 tool 的输入与输出：
  - `knowledge_source_import`
  - `knowledge_source_list`
  - `knowledge_source_remove`
- 保留文本导入、文件导入、sha256 去重、manifest 读写、归档 workspace 写保护等既有行为。

## 验收结果

### 自动化回归

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_stdio.py backend/data_service/mcp_source_tools.py backend/data_service/mcp_workspace_tools.py backend/data_service/mcp_core_tools.py backend/data_service/mcp_quality_tools.py backend/data_service/mcp_session_tools.py
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
-> knowledge_source_import(text)
-> knowledge_source_import(duplicate text)
-> knowledge_source_list
-> knowledge_source_remove
-> knowledge_source_list(status="removed")
-> knowledge_workspace_archive
-> knowledge_source_remove(blocked)
```

结果摘要：

```json
{
  "workspace_id": "phasea42-source",
  "import_status": "ok",
  "imported_source_count": 1,
  "duplicate_status": "duplicate",
  "listed_count": 1,
  "removed_status": "removed",
  "removed_list_count": 1,
  "blocked_status": "blocked"
}
```

## 当前边界

PhaseA4.2 完成后，`mcp_stdio.py` 仍主要承载 build lifecycle：`knowledge_build_start`、`knowledge_build_status`、`knowledge_build_cancel` 以及 build worker/operation helpers。下一步 PhaseA4.3 应拆分 Build MCP handler，并决定 build queue helper 是继续注入还是独立为 runtime 模块。
