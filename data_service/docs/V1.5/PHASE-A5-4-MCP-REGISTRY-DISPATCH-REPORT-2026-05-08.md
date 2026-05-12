# PhaseA5.4 MCP Registry / Dispatch 阶段报告

日期：2026-05-08

## 目标

继续按 MCP-first、最小粒度、微服务化方向收口 `mcp_stdio.py`，把 tool registry、resource reader 和 dispatch wiring 拆出，让 `mcp_stdio.py` 基本只保留 MCP SDK server 绑定与 stdio 入口。

## 本阶段改动

- 新增 `backend/data_service/mcp_tool_registry.py`：统一维护 legacy tools、V2 envelope tools 和聚合 tool specs。
- 新增 `backend/data_service/mcp_resources.py`：统一维护 MCP resource specs 和 resource reader。
- 新增 `backend/data_service/mcp_dispatcher.py`：集中处理 V2 wrapper、Session/Core/Quality/Workspace/Source/Build tool dispatch。
- `mcp_stdio.py` 降为 MCP SDK 适配层：`Server` 初始化、`list_resources`、`read_resource`、`list_tools`、`call_tool` 和 `main`。
- MCP resource URI 对外注册为合法 URL scheme：`data-service://summary`、`data-service://layout`；reader 继续兼容旧的 `data_service://summary`、`data_service://layout` 输入，并返回 canonical URI。

## 验收结果

- `py_compile` 通过：
  - `backend/data_service/mcp_stdio.py`
  - `backend/data_service/mcp_dispatcher.py`
  - `backend/data_service/mcp_resources.py`
  - `backend/data_service/mcp_tool_registry.py`
  - `backend/data_service/mcp_build_runtime.py`
  - `backend/data_service/mcp_workspace_runtime.py`
- MCP 专项回归：`16 passed`
- Data Service / API / MCP 组合回归：`94 passed`
- Tool list contract：`38 tools / missing=[]`
- Draw.io XML 校验通过。

## 出门验证

真实 MCP 调用链路：

1. `list_tools` 返回 38 个工具。
2. `list_resources` 返回 `data-service://summary` 与 `data-service://layout`。
3. `knowledge_workspace_create`
4. `knowledge_source_import`
5. `knowledge_build_start`
6. `knowledge_build_status` 轮询到 `completed`
7. `knowledge_query_v2` 通过 V2 dispatch 返回 `ok`
8. `read_resource(data-service://layout)` 返回 `application/json`
9. `read_resource(data-service://summary)` 返回 `text/markdown`
10. `read_resource(data_service://layout)` 旧 URI 输入兼容并返回 canonical `data-service://layout`
11. `knowledge_workspace_archive`
12. 归档后 `knowledge_quality_feedback_v2` 返回 `blocked`

出门验证摘要：

```json
{
  "workspace_id": "phasea54-wiring",
  "tool_count": 38,
  "resource_uris": [
    "data-service://summary",
    "data-service://layout"
  ],
  "source_count": 1,
  "build_final": "completed",
  "query_v2_status": "ok",
  "layout_mime": "application/json",
  "summary_mime": "text/markdown",
  "legacy_layout_uri": "data-service://layout",
  "archive_status": "archived",
  "blocked_status": "blocked",
  "blocked_warning": "Workspace is archived and cannot be modified"
}
```

## 当前状态

- `mcp_stdio.py` 当前约 84 行。
- PhaseA5.4 已完成，`mcp_stdio.py` 基本收敛为 MCP stdio adapter。
- 下一阶段建议进入 PhaseA5.5：补齐 MCP registry/dispatcher/resource 的小粒度单测与 resource URI contract 测试，随后进入 PhaseB Session GraphRAG Formalization。
