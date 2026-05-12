# PhaseA5.5 MCP Contract Tests 阶段报告

日期：2026-05-08

## 目标

在 PhaseA5.4 完成 registry / resources / dispatcher 拆分后，补齐小粒度 contract tests，防止后续继续开发时破坏 MCP tool registry、resource URI、legacy resource 兼容、V2 dispatch 和 archived blocked 行为。

## 本阶段改动

- 扩展 `backend/tests/test_data_service_mcp.py`。
- 新增 tool registry contract 测试：
  - `all_tool_specs()` 返回 38 个 tools。
  - tool name 无重复。
  - `V2_TOOL_MAP` 的 key/value 都存在于 tool registry。
  - workspace/source/build/session/query_v2 等关键 tool 不丢失。
- 新增 resource contract 测试：
  - `list_resources()` 返回 canonical URI：`data-service://summary`、`data-service://layout`。
  - `read_resource("data_service://layout")` 兼容旧 URI 输入并返回 canonical `data-service://layout`。
  - resource reader 可独立读取 summary markdown。
- 新增 dispatcher contract 测试：
  - 直接实例化 `MCPToolDispatcher`。
  - workspace archive 后 `knowledge_quality_feedback_v2` 返回 `blocked`。
  - unknown tool 抛出 `ValueError("Unknown tool: ...")`。

## 验收结果

- MCP 专项回归：`19 passed`
- Data Service / API / MCP 组合回归：`97 passed`
- PhaseA5.5 出门验证通过：
  - tool_count = 38
  - tool_unique = true
  - v2_count = 7
  - resources = `data-service://summary`、`data-service://layout`
  - legacy layout URI canonicalization 通过
  - build completed
  - query_v2 ok
  - direct dispatcher archived blocked
  - unknown tool error contract 通过

## 出门验证摘要

```json
{
  "tool_count": 38,
  "tool_unique": true,
  "v2_count": 7,
  "resource_uris": [
    "data-service://summary",
    "data-service://layout"
  ],
  "legacy_layout_uri": "data-service://layout",
  "workspace_id": "phasea55-contract",
  "source_count": 1,
  "build_final": "completed",
  "query_v2_status": "ok",
  "direct_blocked_status": "blocked",
  "direct_blocked_warning": "Workspace is archived and cannot be modified",
  "unknown_error": "Unknown tool: knowledge_missing_tool"
}
```

## 当前状态

- PhaseA MCP modularization 已具备 handler、runtime、registry、resources、dispatcher 和 contract test 基线。
- `mcp_stdio.py` 当前约 84 行，基本只承载 MCP SDK server 绑定与 stdio 入口。
- 下一阶段建议进入 PhaseB：Session GraphRAG Formalization，将 session graph build/query/community/neighbor 逐步下沉到 GraphRAG service 边界。
