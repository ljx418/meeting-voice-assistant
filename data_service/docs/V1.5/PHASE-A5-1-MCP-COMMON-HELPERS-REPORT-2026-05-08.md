# V1.5 PhaseA5.1：MCP Common Helpers 模块化报告

日期：2026-05-08

## 目标

完成 V1.5-PhaseA 的第七个小切片：把无状态共享 MCP helper 从 `mcp_stdio.py` 中拆出，继续让 stdio 入口收敛为 tool registry、dispatch 和 server wiring。

## 本阶段变更

- 新增 `backend/data_service/mcp_common.py`。
- 从 `mcp_stdio.py` 迁移以下无状态 helper：
  - `now`
  - `bounded_int`
  - `slug`
  - `read_json`
  - `write_json`
  - `envelope`
  - `blocked`
- `mcp_stdio.py` 通过 `_now`、`_bounded_int`、`_slug`、`_read_json`、`_write_json`、`_envelope`、`_blocked` 别名导入，保持下游 handler 注入代码不变。

## 验收结果

### 自动化回归

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_stdio.py backend/data_service/mcp_common.py backend/data_service/mcp_build_tools.py backend/data_service/mcp_source_tools.py backend/data_service/mcp_workspace_tools.py backend/data_service/mcp_core_tools.py backend/data_service/mcp_quality_tools.py backend/data_service/mcp_session_tools.py
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
-> knowledge_build_start
-> knowledge_build_status(until completed)
-> knowledge_workspace_archive
-> knowledge_quality_feedback_v2(blocked)
```

结果摘要：

```json
{
  "workspace_id": "phasea51-common",
  "create_status": "ok",
  "source_count": 1,
  "start_status": "queued",
  "final_status": "completed",
  "blocked_status": "blocked",
  "blocked_warning": "Workspace is archived and cannot be modified"
}
```

## 当前边界

PhaseA5.1 完成后，`mcp_stdio.py` 仍保留 workspace/path helper、operation envelope、build queue/worker、resource reader 和 stdio server wiring。下一步 PhaseA5.2 应评估拆分 workspace runtime/helper 或 build queue runtime。
