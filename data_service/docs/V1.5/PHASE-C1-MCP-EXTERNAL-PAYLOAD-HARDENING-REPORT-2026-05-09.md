# PhaseC1 MCP External Payload Hardening 阶段报告

日期：2026-05-09

## 目标

PhaseC 的目标是让外部稳定 contract 默认依赖 opaque `artifact_ref`，真实 path 只作为 debug / console 语义出现。本子阶段先在 MCP envelope 层做统一出站清洗，避免各 handler 继续手工暴露内部 workspace layout。

## 本阶段改动

- 更新 `backend/data_service/mcp_common.py`：
  - `envelope(...)` 统一规范化 `artifact_refs`。
  - 字符串 artifact/path 转为 `artifact://{sha256-prefix}`。
  - public payload 中的 `path`、`paths`、`workspace_path`、`original_path`、`artifacts` 等字段移入 `debug_paths`。
  - `artifacts` 同时转换为 public `artifact_refs`。
  - 对象型 `workspace` 保持业务语义；字符串型 `workspace` 路径移入 `debug_paths.workspace`。
- 更新 MCP contract 测试：
  - 新增 no-internal-path scanner。
  - 覆盖 workspace create、source import、build start/status、workspace describe。
  - 更新 v2 quality feedback 对路径字段的预期为 `debug_paths.workspace`。

## 出门验证

编译检查：

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_common.py backend/data_service/mcp_workspace_tools.py backend/data_service/mcp_source_tools.py backend/data_service/mcp_build_tools.py backend/data_service/mcp_session_tools.py
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

- 外部 MCP payload 不再公开 `path`、`paths`、`workspace_path`、`original_path`、`artifacts` 等 public keys。
- `artifact_refs` 中的 path 类值转换为 opaque `artifact://...`。
- 真实路径保留在 `debug_path` / `debug_paths`，便于 console 或调试使用。
- 内部 source manifest、operation 文件、workspace layout 不变。
- legacy 非 envelope 工具保持既有行为；v2 envelope 进入 hardened contract。

## 下一步

- PhaseC2：收敛 blocked / failed / disposed error code，减少仅靠 message 判断状态的外部依赖。
- PhaseC3：评估 HTTP v2 envelope 是否复用同一 external payload sanitizer。
