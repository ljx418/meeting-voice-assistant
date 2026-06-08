# V2.16 目标架构设计

## 1. 架构目标

V2.16 的目标架构不是新增一个孤立系统，而是在 V2.11-V2.15 已验收的 Coding Agent Actionability 链路上增加一层“能力增强与自动化安全边界”。

核心原则：

1. **事实分层**：代码事实、文档声明、provider 推断、runtime 结果、patch preview 必须分开存储。
2. **证据优先**：所有 accepted 输出必须有 evidence；否则只能是 `needs_review` 或 blocker。
3. **默认拒绝**：runtime、provider、patch apply 都默认拒绝，必须通过 profile、配置或人工审批打开。
4. **可追溯**：每个用户可见结果都能追溯到 artifact、source file、line range、provider decision 或 runtime run。
5. **不伪装能力**：provider unavailable、weak match、optional provider skipped 都不能写成 accepted。

## 2. 当前架构

已验收的 V2.11-V2.15 链路：

```text
V2.0-V2.10 Project Intelligence Artifacts
  -> V2.11 Actionability Index
  -> V2.11 Impact Analysis
  -> V2.11 Task-to-Edit Plan
  -> V2.12 Safe Patch Plan
  -> V2.13 Controlled Runtime Evidence
  -> V2.14 Incremental Intelligence
  -> V2.15 Review Workbench
  -> HTTP / MCP / CLI
```

当前架构能力：

- 能抽取 AST definitions/references。
- 能生成任务影响分析。
- 能生成只读 patch plan。
- 能执行 allowlist-only runtime command。
- 能生成 snapshot diff。
- 能生成静态 workbench HTML/Mermaid。

当前架构不足：

- provider 能力没有统一治理层。
- 语义 provider 没有统一 orchestrator。
- runtime command 缺少 profile 化。
- workbench 不是完整审查体验。
- 大项目架构抽象解释还不够深。
- patch 还没有 sandbox preview 和 approval state。

## 3. V2.16 目标架构总览

```text
Accepted V2.11-V2.15 Artifacts
  |
  +-- Provider Capability Registry
  |     +-- Provider Decision Records
  |     +-- Provider Health / Config / Execution Support
  |
  +-- Semantic Provider Orchestrator
  |     +-- AST Mandatory Provider
  |     +-- Optional tree-sitter / LSP / Jedi Providers
  |     +-- Merged Semantic Fact Index
  |
  +-- Runtime Profile Manager
  |     +-- Profile Registry
  |     +-- Approved Command Templates
  |     +-- Profile Runs + Redacted Logs
  |
  +-- Workbench v2 View Model
  |     +-- Filterable Review Payload
  |     +-- 风险分层视图 / Blocker 看板
  |     +-- Evidence Navigation
  |
  +-- Large Project Abstraction Advisor
  |     +-- Generic Pattern Adapter Catalog
  |     +-- Taxonomy Mapping
  |     +-- Architecture Blocker Explanation
  |
  +-- Human-Gated Patch Sandbox
        +-- Preview Artifact
        +-- Diff Artifact
        +-- Rollback Artifact
        +-- Approval State
```

## 3.1 目标体验架构

V2.16 的用户体验由四层组成：

```text
事实层
  snapshot / surfaces / symbols / evidence / docs / graph / V2.11-V2.15 artifacts

能力增强层
  provider registry / semantic facts / runtime profiles / large-project abstraction / patch sandbox

审查体验层
  workbench v2 payload / risk lanes / blocker board / evidence navigation / patch readiness

用户出口层
  HTML report / Mermaid graph / JSON export / HTTP / MCP / CLI / closure audit package
```

体验层不生成新事实。它只把 persisted artifacts 组合成用户可读视图。

用户在页面中看到的每个结论，都必须能追溯到：

- 代码证据。
- 文档声明。
- provider decision。
- runtime profile run。
- patch preview artifact。
- blocker 或 `needs_review`。

## 3.2 用户验收入口

V2.16 至少提供四类用户入口：

| 入口 | 用户目标 | 背后消费的架构组件 |
| --- | --- | --- |
| Provider 能力页 | 判断 provider 是否可用、为什么不可用。 | Provider Capability Registry、Provider Decision Records。 |
| Workbench v2 页面 | 审查项目状态、任务风险、证据、blocker。 | Workbench v2 View Model、Semantic Index、Runtime Runs。 |
| 大项目审计报告 | 理解文档目标架构和代码事实差异。 | Large Project Abstraction Advisor、V2.7/V2.8/V2.9/V2.10 artifacts。 |
| Patch Sandbox 页面 | 查看 diff、rollback、validation 和审批状态。 | Safe Patch Plan、Runtime Profiles、Patch Sandbox。 |

这些入口都必须支持同一条原则：

```text
可读展示只是视图；artifact 才是事实源；高风险动作默认 blocked。
```

## 4. 组件设计

### 4.1 Provider Capability Registry

职责：

- 维护 provider 名称、类型、能力、配置状态、执行状态。
- 记录 provider decision。
- 区分 `known`、`configured`、`execution_supported`。
- 输出 provider matrix 给用户和 Agent。

核心字段：

```json
{
  "provider_id": "semantic:jedi",
  "provider_name": "jedi",
  "capability": "semantic_index",
  "kind": "local",
  "known": true,
  "configured": false,
  "execution_supported": false,
  "status": "provider_unavailable",
  "reason": "optional provider not installed",
  "evidence": [],
  "needs_review": []
}
```

架构边界：

- provider health 只是“知道这个 provider”，不是“能执行”。
- provider execution 必须有 adapter。
- external provider 不能默认接收代码内容。

### 4.2 Semantic Provider Orchestrator

职责：

- 统一 AST、tree-sitter、LSP、Jedi 等 provider 的输出。
- 给每条 semantic fact 标注 provider、confidence、extractor。
- 合并或冲突标记。
- 输出 merged semantic index。

数据流：

```text
snapshot files
  -> provider adapters
  -> provider facts
  -> conflict / confidence policy
  -> merged semantic index
  -> actionability / workbench / context export
```

核心规则：

- AST 是 mandatory baseline。
- optional provider unavailable 不阻塞系统。
- provider conflict 不能静默覆盖。
- import/reference 不等于 runtime call。

### 4.3 Runtime Profile Manager

职责：

- 管理 runtime profiles。
- 定义允许执行的 command templates。
- 把 patch plan validation plan 映射到 profile。
- 执行 profile run。
- 分类运行结果。
- 存储 redacted logs。

profile 示例：

```json
{
  "profile_id": "pytest_file",
  "label": "Run one pytest file",
  "command_template": "python -m pytest {test_path} -q",
  "allowed_args": ["test_path"],
  "approval_required": false,
  "timeout_seconds": 30,
  "network": "disabled",
  "writes_source": false
}
```

结果分类：

```text
passed
failed
timeout
blocked
profile_not_approved
profile_arg_invalid
```

### 4.4 Workbench v2 View Model

职责：

- 汇总 actionability、patch plan、runtime、incremental、provider、semantic、large-project artifacts。
- 生成 filterable review payload。
- 渲染 HTML/Mermaid。
- 提供 context export。

用户可见区域：

1. 项目概览。
2. 当前任务状态。
3. Provider 能力矩阵。
4. Impact 和 patch options。
5. Runtime profile 结果。
6. 大项目架构抽象和 blockers。
7. Evidence navigation。
8. 下一步建议。

边界：

- Workbench 只消费 persisted artifacts。
- Workbench 不能生成新事实。
- Workbench 不能隐藏 blocker。

### 4.5 Large Project Abstraction Advisor

职责：

- 针对大型项目进行更泛化的架构抽象。
- 解释文档声明、代码事实和 pattern evidence 的关系。
- 输出更精确 blocker。
- 避免 HarnessOS-only 逻辑。

输入：

- V2.6 scale profile。
- V2.7 document claims。
- V2.8 dashboard / graph / intent。
- V2.9 evidence / relationship / report。
- V2.10 pattern adapters。
- V2.11-V2.15 actionability artifacts。

输出：

- abstraction report。
- architecture blocker list。
- accepted / needs_review / blocked 分类。
- generic improvement suggestions。

### 4.6 Human-Gated Patch Sandbox

职责：

- 基于 safe patch plan 生成 sandbox preview。
- 生成 diff artifact。
- 生成 rollback artifact。
- 关联 validation profile。
- 管理 approval state。

状态机：

```text
draft_preview
  -> ready_for_human_review
  -> approved_for_apply
  -> applied
  -> validated
  -> rollback_required
  -> rolled_back
```

安全规则：

- `draft_preview` 不修改 source repo。
- `approved_for_apply` 必须来自人类审批。
- git commit/push 不属于默认流程。

## 5. Artifact 布局

```text
workspace/assets/codebase/{codebase_id}/coding_agent/v2_16/
  providers/
    capability_registry.json
    decisions/{decision_id}.json
  semantic/
    provider_facts/{provider}/{snapshot_id}.jsonl
    merged_semantic_index.json
    conflicts.jsonl
  runtime_profiles/
    profiles.json
    runs/{run_id}.json
    logs/{run_id}.stdout.redacted.txt
    logs/{run_id}.stderr.redacted.txt
  workbench_v2/
    payload.json
    report.html
    graph.mmd
    exports/{export_id}.json
  large_project/
    abstraction_report.json
    blockers.jsonl
    taxonomy_mapping.json
  patch_sandbox/
    previews/{preview_id}.json
    diffs/{preview_id}.diff
    rollback/{preview_id}.json
    approvals/{approval_id}.json
```

## 6. Public Contract

HTTP 目标：

```text
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/providers
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/semantic/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/semantic
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/runtime-profiles/run
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/runtime-profiles/runs/{run_id}
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/workbench/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/workbench
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/large-project/abstract
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/v2_16/patch-sandbox/preview
```

MCP / CLI 必须提供等价能力。

## 7. 架构门禁

- 不把 V2.16 核心逻辑塞进 `backend/app/api/v1/data_service.py`。
- 不把 V2.16 核心逻辑塞进 `backend/data_service/service.py`。
- API/MCP/CLI 只做薄封装。
- provider adapters 必须独立。
- runtime profile 必须 default-deny。
- public payload 不允许绝对路径、secret、raw traceback、raw provider body。
- patch sandbox preview 不允许修改源码。
