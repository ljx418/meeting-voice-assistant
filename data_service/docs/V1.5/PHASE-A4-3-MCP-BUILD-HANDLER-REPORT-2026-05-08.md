# V1.5 PhaseA4.3：Build MCP Handler 模块化报告

日期：2026-05-08

## 目标

完成 V1.5-PhaseA 的第六个小切片：把 build lifecycle MCP tool schema 和 handler 从 `mcp_stdio.py` 中拆出，继续压缩 stdio 入口职责，同时保持 build start/status/cancel 的外部契约兼容。

## 本阶段变更

- 新增 `backend/data_service/mcp_build_tools.py`。
- `mcp_stdio.py` 改为通过 `BUILD_TOOL_SPECS` 注册 build lifecycle 工具。
- `mcp_stdio.py` 改为通过 `handle_build_tool(...)` 分发 build MCP 调用。
- 保留以下 tool 的输入与输出：
  - `knowledge_build_start`
  - `knowledge_build_status`
  - `knowledge_build_cancel`
- 保留异步 build worker、operation json、terminal operation warning、归档 workspace 写保护等既有行为。

## 验收结果

### 自动化回归

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_stdio.py backend/data_service/mcp_build_tools.py backend/data_service/mcp_source_tools.py backend/data_service/mcp_workspace_tools.py backend/data_service/mcp_core_tools.py backend/data_service/mcp_quality_tools.py backend/data_service/mcp_session_tools.py
```

结果：通过。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：

```text
16 passed
```

说明：首次运行时 `test_data_service_mcp_session_scope_isolates_two_sessions` 出现一次 session 异步构建 `blocked`，调试脚本同链路成功，MCP 专项回归复跑为 16 passed。

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
-> knowledge_build_start
-> knowledge_build_status(until completed)
-> knowledge_build_cancel(terminal operation warning)
-> knowledge_workspace_archive
-> knowledge_build_start(blocked)
```

结果摘要：

```json
{
  "workspace_id": "phasea43-build",
  "source_count": 1,
  "start_status": "queued",
  "operation_id_prefix": "op",
  "final_status": "completed",
  "final_stage": "completed",
  "cancel_terminal_status": "completed",
  "cancel_warning_count": 1,
  "blocked_status": "blocked"
}
```

## 当前边界

PhaseA4.3 完成后，MCP tool schema/handler 已按 Core、Quality、Workspace、Source、Build、Session 六类拆分。`mcp_stdio.py` 仍保留共享 runtime/helper：workspace 解析、meta、json IO、operation envelope、build queue/worker、resource reader 和 stdio server wiring。

下一步 PhaseA5 应评估并拆分共享 envelope/error/helper 与 build queue runtime，进一步把 `mcp_stdio.py` 收敛为 tool registry、dispatch 和 server wiring。
