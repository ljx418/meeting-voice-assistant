# PhaseC2 MCP Error Code Contract 阶段报告

日期：2026-05-09

## 目标

PhaseC1 已将 MCP 外部 payload 的内部 path 收敛到 `artifact_ref` / `debug_paths`。PhaseC2 继续收敛 blocked / failed / disposed 响应，确保外部 Agent 不再依赖 warning/message 文本判断错误类型。

## 本阶段改动

- 更新 `backend/data_service/mcp_common.py`：
  - `envelope(...)` 对 `blocked`、`failed`、`disposed` 状态自动补齐 `data.error`。
  - `blocked(...)` 默认输出稳定 `data.error.code/message/retryable`。
  - 出站 sanitizer 将 operation error 的 `type` 归一为 `code`。
  - 增加 message 到 code 的保守映射：
    - `unknown_source_id`
    - `unknown_operation_id`
    - `unknown_session_id`
    - `workspace_archived`
    - `source_path_outside_allowed_roots`
    - `workspace_id_outside_root`
    - `path_outside_workspace`
    - `payload_too_large`
    - `session_closed`
    - `session_disposed`
- 更新 `backend/data_service/mcp_build_runtime.py`：
  - interrupted build error 显式携带 retryable。
  - no-active-source blocked operation 显式携带 `no_active_sources`。
- 更新 MCP contract tests：
  - unknown source / unknown operation 校验 `data.error.code`。
  - interrupted failed operation 校验 `server_interrupted`。
  - disposed session graph 校验 `session_disposed`。

## 出门验证

编译检查：

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_common.py backend/data_service/mcp_build_runtime.py backend/data_service/mcp_dispatcher.py backend/data_service/mcp_session_tools.py
```

结果：通过。

MCP 专项回归：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：22 passed。

组合回归：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：100 passed。

## 验收覆盖

- blocked 响应稳定包含 `data.error.code/message/retryable`。
- failed operation error 的 legacy `type` 不作为外部稳定字段暴露，出站归一为 `code`。
- disposed session graph 稳定返回 `session_disposed`。
- legacy warning/message 仍保留，不破坏旧客户端的人工可读提示。

## 下一步

PhaseC3：评估 HTTP v2 envelope 是否复用 MCP external payload sanitizer，并补齐 HTTP/API 层 no-internal-path 与 error code contract。
