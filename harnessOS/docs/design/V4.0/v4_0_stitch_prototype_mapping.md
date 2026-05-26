# V4.0 Stitch Prototype Mapping

文档状态：V4.0-Z complete mapping。本文把 Stitch 原型和 PRD v0.2 中的主要 UI 区域映射到 V3.6 API、V4.0 BFF read model 或 UI-only transient state，并记录当前 `apps/workflow-console` 对 “harnessOS Workflow Studio + Agent 工作流助手” 的实现状态；不代表 complete Workflow Studio、complete AgentTalkWindow、controlled executor 或 production-ready support。

原型来源：

```text
https://stitch.withgoogle.com/projects/10240451325799222489
```

## Mapping Table

| Prototype Region | UI Term | Runtime Mapping | Source | First Phase |
| --- | --- | --- | --- | --- |
| 首页 / 工作流列表 | 工作流列表 | WorkflowTemplate / WorkflowVersion summary | `workflow.template.list`, `workflow.version.list` | V4.0-0 / A |
| 设计时画布 | 工作流节点 / 连线 | Station / WorkflowEdge via CanvasDraftProjection | `/bff/instances/{id}/canvas-projection`, `workflow.patch.*` | V4.0-N |
| 节点库 | 节点库 / 节点分类 | Controlled Station descriptor catalog | `/bff/workflows/{id}/node-catalog` | V4.0-N |
| 节点配置面板 | 节点配置 / Inspector | Station + ArtifactContract + QualityContract + approval policy | `workflow.patch.propose/diff/apply` through governed panel | V4.0-N |
| Patch 队列 | Patch 建议 / Diff 状态 | PatchQueueDTO + PatchDiffDTO | `/bff/workflows/{id}/patches`, `workflow.patch.diff` | V4.0-O |
| 运行时看板 | 工作流运行态 | PipelineBoard | `workflow.board.get`, `workflow.instance.status` | V4.0-A |
| 节点输出 | 工件摘要 | Artifact metadata / lineage | `station.output.list`, `artifact.read_metadata`, `artifact.lineage` | V4.0-A |
| 质量看板 | 质量评估 | QualityEvaluation summary | `quality.evaluation.get/list`, board summary | V4.0-D |
| 审批面板 | 审批决策 | Approval request + `approval.respond` | `approval.respond`, `approval.required` | V4.0-D |
| 上下文面板 | 业务上下文 | WorkflowContext business partition | `workflow.context.get/update` | V4.0-D |
| Agent 工作流助手 | Agent natural-language workflow copilot | Natural-language workflow draft / node optimization / Patch proposal shell | `workflow.patch.propose/diff`, EventBridge, UI-only fixture copy | V4.0-C |

## Current Implementation Snapshot

当前 `apps/workflow-console` 已按 Stitch 方向完成一版 low-code shell，并在 V4.0-Z final audit 中确认具备 controlled catalog、CanvasDraftProjection、node/edge/Inspector proposal flow、layout boundary、governed proposal workflow 和 AgentTalk interaction E2E baseline：

```text
Top bar:
  harnessOS Workflow Studio / workflow selector / version / instance / disabled save-run-publish actions

Left:
  节点库 / search / filters / categorized draggable node cards

Center:
  工作流画布 / Stitch latest light workbench / ComfyUI-like bottom layer / light dotted grid / node edges / white node cards / background pan / node drag / zoom / fit view

Right:
  Agent 工作流助手 / 节点配置 / Patch Diff tabs, default Agent 助手

Bottom:
  事件 / Trace / 产物 / 质量 / 审批 / Patch run panel
```

当前实现仍是 shell，不等同于完整 Workflow Studio：

```text
node library drag creates proposal only, not runtime Station
canvas node movement is UI-only transient state
edges are projection/proposal state, not direct WorkflowEdge writes
Inspector typing is local dirty state until Generate Patch
Patch apply/reject/publish must use governed Editing Panel path
Agent 工作流助手 displays natural-language workflow generation, node optimization suggestions and Patch/Diff confirmation semantics
```

## Visual Token Mapping

当前 `apps/workflow-console` 已按 Stitch 最新可见原型和 PRD v0.2 切换到浅色高保真视觉：

```text
background: light SaaS workspace / #f9f9f9 family
primary accent: blue-purple / #4648d4 and #7c3aed family
panels: white and light-gray surfaces
canvas: white infinite dotted grid with clear node edges
nodes: white cards with status and warning emphasis
```

这些 token 只属于 Product UI visual layer，不能反向定义 V3.6 runtime schema。

## UI-only Transient State

The following prototype state is UI-only and must not be written to V3.6 runtime contracts:

```text
selected node
canvas zoom
node x/y
panel collapsed
side panel width
active tab
filter keyword
hover state
drag state
temporary connection preview
```

当前画布的 `canvas viewport x/y`、`canvas zoom`、`node x/y`、折叠状态和 active tab 均属于 UI-only transient state。

画布层级要求：

```text
canvas is the workspace bottom layer
left node library floats above canvas
right Inspector / Agent floats above canvas
canvas toolbar floats above canvas
bottom run panel floats above canvas
```

因此后续不能退回到 “left / middle canvas card / right” 的普通三栏 Dashboard 布局。

## Production Path

Prototype UI must be implemented against the production default path:

```text
UI -> BFF / SDK / hooks / EventBridge proxy -> harnessOS
```

Direct `/v1/rpc` and `/v1/events/subscribe` usage is allowed only in explicit dev direct mode with restricted token and must not be the default production UI path.
