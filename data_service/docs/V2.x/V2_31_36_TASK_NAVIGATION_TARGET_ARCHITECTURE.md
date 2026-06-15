# V2.31-V2.36 目标架构：Task-Aware Navigation + Lightweight Impact Graph

## 1. 架构目标

V2.31-V2.36 的目标架构把 V2.0-V2.30 的事实层、架构意图层和公共合同层组合成一个面向 Coding Agent 的任务导航平台。

目标不是“自动写代码”，而是：

```text
给开发任务生成最小可信阅读路径、轻量影响关系、测试建议和可压缩上下文。
```

## 2. 架构原则

- 证据优先：开发建议必须来自 persisted facts、line evidence、relationship evidence，或显式标记 `needs_review`。
- 关系分层：direct AST call、handler dispatch、import dependency、config declaration、test reference、heuristic relation 必须分开。
- 语义克制：轻量调用关系不是完整 call graph；影响路径不是运行时路径。
- 读写分离：本阶段不修改目标项目代码，只生成导航、影响、阅读包和报告。
- Token 可解释：任何上下文裁剪都必须记录 omitted reason，并保留建议对应 evidence。
- 通用优先：HarnessOS 是大项目验收样例，不是专用规则来源。
- 入口不伪造：Public Surface Inventory 的 MCP surface 只能来自目标仓库生产源码中可解析的 MCP `TOOL_SPECS`，不能导入当前运行中的 data_service registry 来填充外部项目。
- 无入口可降级：没有 HTTP/MCP/CLI 等确定性 public surface 的大型项目不能硬失败；必须继续基于 files/symbols/imports/tests/docs 生成阅读结果，并用结构化 blocker 标记 public surface 缺失。
- accepted 严格化：accepted relationship 必须有 repo-relative path、line_range 和 evidence_refs；缺任一项必须降级为 `needs_review`。

## 3. 当前架构与目标架构差异

| 能力 | 当前状态 | V2.31-V2.36 目标 |
| --- | --- | --- |
| 项目事实 | 已有 snapshot、inventory、symbols、evidence、architecture intent | 作为只读输入消费，不重建上游事实 |
| 任务导航 | Context Pack 有任务上下文，但阅读集合不够严格 | task -> minimal reads / surfaces / symbols / tests |
| 调用关系 | 明确避免 full call graph，但轻量关系层不完整 | accepted / heuristic / blocked relationship 分层 |
| 影响分析 | 架构报告能展示风险，但不够任务导向 | change impact + test selection + guardrail check |
| Token 管理 | Context Pack 有裁剪 | token ledger、omitted reason、cache key、evidence floor |
| Agent 集成 | 报告读取式 HTTP/MCP/CLI | task-level MCP/HTTP/CLI workflows |

## 4. 目标数据流

```text
V2.0-V2.30 Artifacts
  snapshot / inventory / surfaces / symbols / evidence
  graph / quality / architecture intent / context packs
        |
        v
Task Navigation Index
  task taxonomy / capability match / surface match / symbol match / test match
        |
        v
Lightweight Relationship Graph
  direct_call_ast / handler_dispatch / registry_declared
  import_dependency / config_declared / test_reference / heuristic_related
        |
        v
Impact & Test Recommendation
  impacted files / symbols / surfaces / tests / docs / guardrails / blockers
        |
        v
Module Reading Pack + Token Ledger
  required reads / optional reads / skipped reads / reuse patterns / omitted items
        |
        v
Copilot Agent APIs
  task_navigation / impact_v2 / test_selection / context_compress / handoff
        |
        v
Human UX + Governance
  HTML report / Mermaid graph / governance target summary / accepted vs needs_review
```

## 5. 核心组件

### 5.1 Task Navigation Index

职责：

- 将 task 文本映射到 capability、surface、symbol、test、doc、architecture guardrail。
- 支持任务类型：新增 API、修改 MCP tool、调整 workflow、修复 bug、增加 provider、更新测试、修改文档、架构审查。
- 输出 ranked candidates、evidence、needs_review、blockers。

存储：

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/
  navigation_index.json
  task_queries/{task_id}.json
```

### 5.2 Lightweight Relationship Graph

职责：

- 从 AST、imports、symbol refs、route handler、MCP registry、CLI parser、config manifest、test references 中生成浅层关系。
- 每条边必须包含 `relationship_type`、`confidence`、`semantic_limit`、`evidence_refs`、`truth_status`。

允许关系：

```text
direct_call_ast
method_call_candidate
handler_dispatch
surface_handled_by
registry_declared
config_declared
module_imports_module
symbol_references_symbol
test_references_symbol
capability_related_to_surface
heuristic_related
dynamic_unresolved
```

禁止关系：

```text
full_call_graph
runtime_call_accepted
data_flow
control_flow
runtime_topology
type_inferred
production_runtime_topology
```

### 5.3 Change Impact & Test Recommendation

职责：

- 给定 task/file/symbol/capability，输出影响范围。
- 区分 upstream、downstream、reference、test、doc、architecture impact。
- 推荐测试并说明依据、置信度、覆盖缺口。

### 5.4 Module Reading Pack + Token Ledger

职责：

- 输出 `required_reads`、`optional_reads`、`skip_reads`。
- 生成 token budget ledger、cache key、omitted reason。
- 确保 recommendation 不会在 evidence 被裁剪后继续保留为高置信建议。

### 5.5 Copilot Agent Public Contracts

HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2/{task_id}
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack/{pack_id}
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff/{handoff_id}
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/views/{view_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/{task_id}
```

说明：`test_selection` 作为 `impact-v2` payload 的一部分返回；`reuse_patterns` 作为 `reading-pack` payload 的一部分返回，本阶段不提供独立 test-recommendations 或 reuse-patterns endpoint。

MCP：

```text
knowledge_code_task_navigation_prepare
knowledge_code_task_impact_analyze
knowledge_code_task_impact_read
knowledge_code_module_reading_pack
knowledge_code_module_reading_pack_read
knowledge_code_agent_handoff
knowledge_code_agent_handoff_read
knowledge_code_task_navigation_closure_build
knowledge_code_task_navigation_closure_read
knowledge_code_task_navigation_closure_view
```

CLI：

```text
knowledge code coding-agent task-navigation
knowledge code coding-agent impact-v2
knowledge code coding-agent impact-v2-read
knowledge code coding-agent reading-pack
knowledge code coding-agent reading-pack-read
knowledge code coding-agent handoff
knowledge code coding-agent handoff-read
knowledge code coding-agent closure-build
knowledge code coding-agent closure
knowledge code coding-agent closure-view
```

## 6. 存储布局

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/
  navigation_index.json
  relationship_graph.json
  relationships.jsonl
  relationship_blockers.jsonl
  impacts/
    {task_id}.json
  reading_packs/
    {pack_id}.json
    {pack_id}.md
  token_ledgers/
    {pack_id}.json
  handoff/
    {handoff_id}.json
  reports/
    task_navigation_report.html
    task_navigation_graph.mmd
```

## 7. 架构门禁

- 不修改 `backend/app/api/v1/data_service.py`。
- 不修改 `backend/data_service/service.py`。
- 新逻辑进入 focused `code_assets/coding_agent_navigation/` 或既有 coding-agent focused modules。
- `research_notebook`、source registry、V2.0-V2.30 source artifacts 不被静默改写。
- public payload 不暴露绝对路径、secret、traceback。
- 对 HarnessOS 若无法建立 accepted relationship，必须输出 blocker。
- 任何 full call graph / data flow / control flow / type inference 声明为 fatal 规格偏差。
