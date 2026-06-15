# V2.20 Phase 86 MCP Tool Discovery & Workflow Guide Development Plan

## 1. 阶段目标

Phase 86 将当前 MCP tool registry 转成 Agent 可消费的工具目录和目标导向 workflow guide。它不执行 workflow，只提供可审计的工具发现、分组、前置条件、输出说明、失败模式和推荐调用链。

## 2. 输出

```text
workspace/assets/codebase/{codebase_id}/platform/tool_catalog/mcp_tool_catalog.json
workspace/assets/codebase/{codebase_id}/platform/tool_catalog/workflow_guides.json
```

## 3. 新增接口

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog

MCP:
knowledge_code_platform_tool_catalog_build
knowledge_code_platform_tool_catalog_read

CLI:
knowledge code platform tool-catalog-build
knowledge code platform tool-catalog
```

## 4. 实现任务

1. 读取 `all_tool_specs()`。
2. 生成 tool catalog：tool name、group、required/optional input、description、goal tags。
3. 生成 workflow guides：project_reading、coding_task_preparation、architecture_review。
4. 检查 workflow chain 中每个 tool 必须存在于 catalog。
5. 输出 artifact refs 和 validation summary。

## 5. 非目标

- 不执行 MCP tool。
- 不根据自然语言动态规划 workflow。
- 不声称所有 workflow 都已完成运行。
- 不推荐 registry 中不存在的工具。
