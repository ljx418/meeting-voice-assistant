# PhaseA5.2 MCP Workspace Runtime 阶段报告

日期：2026-05-08

## 目标

继续按 MCP-first、最小粒度、微服务化方向收口 `mcp_stdio.py`，把 workspace/path/meta/layout runtime helper 从 stdio server 主文件拆出，降低 MCP server wiring 与 workspace runtime 的耦合。

## 本阶段改动

- 新增 `backend/data_service/mcp_workspace_runtime.py`。
- 将 workspace root、workspace meta path、lifecycle/source/operation path、workspace resolve、workspace meta ensure、archive status、layout payload 等 helper 收敛到 `WorkspaceRuntime`。
- `mcp_stdio.py` 保留兼容别名，外部 MCP tool name、payload、V2 envelope 和 resource contract 不变。
- 修复异步 build/status 并发读写 JSON operation 文件的瞬态问题：`mcp_common.write_json` 与 `session_service.write_json` 改为同目录临时文件加 `os.replace` 原子替换，避免轮询读到半截 JSON 后误判为 blocked。

## 验收结果

- `py_compile` 通过：
  - `backend/data_service/mcp_stdio.py`
  - `backend/data_service/mcp_common.py`
  - `backend/data_service/mcp_workspace_runtime.py`
  - `backend/data_service/session_service.py`
  - `backend/data_service/mcp_build_tools.py`
  - `backend/data_service/mcp_session_tools.py`
- MCP 专项回归：`16 passed`
- Data Service / API / MCP 组合回归：`94 passed`

## 出门验证

真实 MCP 调用链路：

1. `knowledge_workspace_create`
2. `knowledge_workspace_describe`
3. `knowledge_source_import` 导入文本 source
4. `knowledge_build_start`
5. `knowledge_build_status` 轮询到 `completed`
6. `knowledge_workspace_archive`
7. 归档后再次 `knowledge_build_start` 返回 `blocked`

出门验证摘要：

```json
{
  "workspace_id": "phasea52-runtime",
  "create_status": "ok",
  "describe_status": "ok",
  "source_count": 1,
  "build_start_status": "queued",
  "build_final_status": "completed",
  "build_stage": "completed",
  "archive_status": "archived",
  "blocked_status": "blocked",
  "blocked_warning": "Workspace is archived and cannot start builds"
}
```

## 当前状态

- `mcp_stdio.py` 当前约 605 行。
- PhaseA5.2 已完成，workspace runtime/helper 从 stdio server 主文件拆出。
- 下一阶段建议进入 PhaseA5.3：build queue/runtime 拆分，继续把 operation envelope、queue worker 和 status/cancel runtime 从 `mcp_stdio.py` 收口出去。
