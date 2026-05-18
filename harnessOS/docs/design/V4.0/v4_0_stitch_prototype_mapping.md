# V4.0 Stitch Prototype Mapping

文档状态：V4.0-C complete + Workflow Studio low-code shell refresh。本文把 Stitch 原型中的主要 UI 区域映射到 V3.6 API 或 UI-only transient state，并记录当前 `apps/workflow-console` 对 “harnessOS Workflow Studio - 左右双折叠交互设计” 的实现状态。

原型来源：

```text
https://stitch.withgoogle.com/projects/10240451325799222489
```

## Mapping Table

| Prototype Region | UI Term | Runtime Mapping | Source | First Phase |
| --- | --- | --- | --- | --- |
| 首页 / 工作流列表 | 工作流列表 | WorkflowTemplate / WorkflowVersion summary | `workflow.template.list`, `workflow.version.list` | V4.0-0 / A |
| 设计时画布 | 工作流节点 / 连线 | Station / WorkflowEdge | `workflow.template.get`, `workflow.patch.*` | V4.0-B |
| 节点库 | 节点库 / 节点分类 | Station descriptor catalog | future descriptor map; V3.6 Station-compatible shape | V4.0-B |
| 节点配置面板 | 节点配置 / Inspector | Station + ArtifactContract + QualityContract + approval policy | `workflow.patch.diff/apply` | V4.0-B |
| 运行时看板 | 工作流运行态 | PipelineBoard | `workflow.board.get`, `workflow.instance.status` | V4.0-A |
| 节点输出 | 工件摘要 | Artifact metadata / lineage | `station.output.list`, `artifact.read_metadata`, `artifact.lineage` | V4.0-A |
| 质量看板 | 质量评估 | QualityEvaluation summary | `quality.evaluation.get/list`, board summary | V4.0-D |
| 审批面板 | 审批决策 | Approval request + `approval.respond` | `approval.respond`, `approval.required` | V4.0-D |
| 上下文面板 | 业务上下文 | WorkflowContext business partition | `workflow.context.get/update` | V4.0-D |
| Agent 助手 | Agent proposal shell | Patch propose/diff + event feed | `workflow.patch.propose/diff`, EventBridge | V4.0-C |

## Current Implementation Snapshot

当前 `apps/workflow-console` 已按 Stitch 方向完成一版 low-code shell：

```text
Top bar:
  harnessOS Workflow Studio / workflow selector / version / instance / disabled save-run-publish actions

Left:
  节点库 / search / filters / categorized draggable node cards

Center:
  工作流画布 / light grid / node edges / node cards / background pan / node drag / zoom / fit view

Right:
  节点配置 Inspector / Agent 助手 tab

Bottom:
  事件 / Trace / 产物 / 质量 / 审批 / Patch run panel
```

当前实现仍是 shell，不等同于完整 Workflow Studio：

```text
node library drag does not create runtime Station
canvas node movement is UI-only transient state
edges are visual read model, not persisted WorkflowEdge edits
Inspector fields are read-only / disabled
Patch panel only displays proposal/diff/risk, not apply/reject/publish
Agent 助手 only displays suggestions, notices and summaries
```

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

## Production Path

Prototype UI must be implemented against the production default path:

```text
UI -> BFF / SDK / hooks / EventBridge proxy -> harnessOS
```

Direct `/v1/rpc` and `/v1/events/subscribe` usage is allowed only in explicit dev direct mode with restricted token and must not be the default production UI path.
