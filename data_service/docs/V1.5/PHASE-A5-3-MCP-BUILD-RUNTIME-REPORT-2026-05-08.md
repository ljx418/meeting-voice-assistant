# PhaseA5.3 MCP Build Runtime 阶段报告

日期：2026-05-08

## 目标

继续按 MCP-first、最小粒度、微服务化方向收口 `mcp_stdio.py`，把 workspace build queue、operation envelope、worker lifecycle 和 build execution runtime 从 stdio server 主文件拆出。

## 本阶段改动

- 新增 `backend/data_service/mcp_build_runtime.py`。
- 将 build operation envelope、operation payload、source ingest status 更新、operation 更新、取消检查、interrupted running operation 标记、单 workspace build queue、worker 启动和 build execution 移入 `BuildRuntime`。
- `mcp_stdio.py` 只保留 `BuildRuntime` 实例化和 handler wiring；MCP tool name、payload、V2 envelope 和 build lifecycle 行为保持兼容。
- 继续沿用 PhaseA5.2 的原子 JSON 写入，避免异步 status 轮询读到半截 operation 文件。

## 验收结果

- `py_compile` 通过：
  - `backend/data_service/mcp_stdio.py`
  - `backend/data_service/mcp_build_runtime.py`
  - `backend/data_service/mcp_build_tools.py`
  - `backend/data_service/mcp_common.py`
  - `backend/data_service/mcp_workspace_runtime.py`
- MCP 专项回归：`16 passed`
- Data Service / API / MCP 组合回归：`94 passed`

## 出门验证

真实 MCP 调用链路：

1. `knowledge_workspace_create`
2. `knowledge_source_import` 导入文本 source
3. 连续两次 `knowledge_build_start`，两个 operation 均进入 queued
4. `knowledge_build_status` 分别轮询两个 operation 到 `completed`
5. `knowledge_source_list` 确认 source ingest_status 为 `built`
6. `knowledge_workspace_archive`
7. 归档后再次 `knowledge_build_start` 返回 `blocked`

出门验证摘要：

```json
{
  "workspace_id": "phasea53-queue",
  "source_count": 1,
  "first_start": "queued",
  "second_start": "queued",
  "first_final": "completed",
  "second_final": "completed",
  "first_stage": "completed",
  "second_stage": "completed",
  "source_ingest_status": "built",
  "archive_status": "archived",
  "blocked_status": "blocked",
  "blocked_warning": "Workspace is archived and cannot start builds"
}
```

## 当前状态

- `mcp_stdio.py` 当前约 366 行。
- PhaseA5.3 已完成，build queue/runtime 从 stdio server 主文件拆出。
- 下一阶段建议进入 PhaseA5.4：resource reader / stdio wiring / tool registry 收口，进一步让 `mcp_stdio.py` 只保留 MCP server 入口注册与 dispatch。
