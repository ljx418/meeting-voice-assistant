# V2.36 Phase 102 Closure, UX Report & Governance Development Plan

## 1. 阶段目标

Phase 102 是 V2.31-V2.36 Task Navigation 主线的收口阶段，目标是把 Phase 97-101 的产物转换为人类和 Coding Agent 都能阅读的最终审阅包：

- HTML 用户报告。
- Mermaid 任务关系图。
- coverage matrix artifact。
- governance feedback target summary。
- data_service + HarnessOS benchmark summary。

本阶段不自动修改目标项目代码，不执行 handoff 中的 recommended commands，不声称 full call graph、runtime topology、data flow、control flow 或 type inference。

## 2. 开发范围

新增 focused modules：

```text
backend/data_service/code_assets/coding_agent_navigation/
  closure_report.py
  closure_persistence.py
```

扩展服务与三端入口：

```text
backend/data_service/code_assets/coding_agent_navigation/service.py
backend/app/api/v1/code_assets_coding_agent.py
backend/data_service/mcp_code_coding_agent_tools.py
backend/data_service/cli_code_coding_agent.py
backend/tests/test_public_surface_guard.py
frontend/src/data/mcpContract.ts
```

新增测试：

```text
backend/tests/test_v2_36_task_navigation_closure.py
```

## 3. 产物布局

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/
  reports/task_navigation_report.json
  reports/task_navigation_report.html
  reports/task_navigation_graph.mmd
  coverage_matrix.json
  governance_targets.json
  closure_audit_report.json
```

## 4. 最小数据模型

Closure report 必须包含：

- `summary`
- `task_navigation_summary`
- `relationship_summary`
- `impact_summary`
- `reading_pack_summary`
- `handoff_summary`
- `governance_targets`
- `benchmark_summary`
- `views.html_ref`
- `views.mermaid_ref`
- `warnings`
- `blockers`

HTML 必须从 persisted JSON 渲染，不得新增 JSON 中不存在的重要事实。

Mermaid 必须只引用 persisted node ids，不使用 raw path 作为 node id。

## 5. HTTP / MCP / CLI

HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/views/{view_id}
```

MCP：

```text
knowledge_code_task_navigation_closure_build
knowledge_code_task_navigation_closure_read
knowledge_code_task_navigation_closure_view
```

CLI：

```text
knowledge code coding-agent closure-build
knowledge code coding-agent closure
knowledge code coding-agent closure-view
```

## 6. 开发步骤

1. 实现 closure persistence。
2. 实现 closure report builder。
3. 从已有 navigation、relationship、impact、reading pack、handoff artifacts 汇总统计。
4. 生成 HTML 与 Mermaid。
5. 生成 governance target summary。
6. 扩展服务和三端 public contract。
7. 新增 focused test 和真实仓 E2E。
8. 更新 coverage matrix 与 closure audit report。

## 7. 出门条件

- Focused tests pass。
- V2.31-V2.36 regression pass。
- MCP/public surface contract pass。
- data_service 真实仓报告可生成、HTML/Mermaid 可读。
- HarnessOS 真实仓报告可生成，并显式展示 blocker / low-evidence 状态。
- HTML 不泄露绝对路径，不执行原始文档 HTML。
- Mermaid node id 可追踪到 persisted report JSON。
- 无 fatal/major open finding。
