# V4.0 UI Contract Map

文档状态：V4.0-C complete + Workflow Studio low-code shell refresh。本文定义 Workflow Console / Studio / AgentTalkWindow 前置 UI 可以消费的 RPC、事件和 BFF route，并记录当前 `apps/workflow-console` 已实现的页面边界。

## Terminology

| 中文术语 | Runtime Mapping | 说明 |
| --- | --- | --- |
| 节点库 | Station / descriptor catalog | 可拖入工作流的节点集合。 |
| 节点 | Station candidate | 节点库中的可用定义。 |
| 节点分类 | Station category / descriptor metadata | 节点库分组。 |
| 工作流节点 | Station in WorkflowTemplate / WorkflowDraft | 已进入某个 workflow 的节点。 |
| 连线 / 工作流边 | WorkflowEdge | 工作流节点之间的数据或控制关系。 |
| 节点配置 / Inspector | Station + ArtifactContract + QualityContract + approval policy | 通过 patch 修改 draft。 |
| Agent 助手 | AgentTalkWindow preparation shell | 只能 propose/diff，不直接 apply。 |

禁用混用术语：

```text
组件库
能力库
模块库
插件库
```

## UI State Classification

| State Class | Examples | Persistence Rule |
| --- | --- | --- |
| read-only state | board summary, station status, job status, artifact metadata, quality score | Read from V3.6 APIs; not written by UI. |
| action state | approval decision, context update, patch apply, publish | Written only through explicit action APIs. |
| editing state | patch draft, inspector form, diff preview | May be sent through patch APIs; never mutates published version directly. |
| UI-only transient state | selected node, canvas zoom, node x/y, panel collapsed, side panel width, active tab, filter keyword | Must not be written to V3.6 runtime contract. |

当前 `apps/workflow-console` 已落地的 UI-only transient state：

```text
left panel collapsed
right panel collapsed
selected station run
right tab: Inspector / Agent
bottom tab: events / trace / artifacts / quality / approvals / patch
canvas viewport x/y
canvas zoom
node x/y
drag state
```

这些状态只存在于前端，不写入 WorkflowTemplate、WorkflowDraft、WorkflowVersion、WorkflowInstance 或 StationRun。

## V4.0-0 Contract Mapping

Allowed RPC:

```text
workflow.template.list
workflow.template.get
workflow.version.list
workflow.version.get
```

Allowed events:

```text
none required
```

Allowed BFF routes:

```text
GET /bff/workflows
GET /bff/workflows/{workflow_template_id}
GET /bff/workflows/{workflow_template_id}/versions
```

Purpose: map Stitch / Workflow Studio prototype regions to real V3.6 APIs or UI-only transient state.

## V4.0-A Read-only Console

Implementation status: complete and refreshed into a canvas-first Workflow Studio shell. The UI contains top bar, left `节点库`, central draggable grid canvas, right Inspector / Agent panel and bottom run panel. It still consumes demo/read models and does not prove UI+BFF+runtime E2E.

Allowed RPC:

```text
workflow.instance.get
workflow.instance.list
workflow.instance.status
station.run.list
workflow.board.get
station.output.list
artifact.read_metadata
artifact.lineage
job.get
job.list
```

Dev/demo-only RPC:

```text
workflow.instance.start
```

`workflow.instance.start` may only be used for explicit demo fixture bootstrap in dev mode. The production console path selects an existing workflow instance.

Allowed events:

```text
approval.required
workflow.instance.started
workflow.instance.completed
workflow.instance.failed
station.run.started
station.run.completed
station.run.failed
station.run.waiting_approval
artifact.registered
workflow.context.updated
workflow.patch.applied
```

Allowed BFF routes:

```text
GET /bff/workflow-instances
GET /bff/workflow-instances/{workflow_instance_id}/status
GET /bff/workflow-instances/{workflow_instance_id}/board
GET /bff/stations/{station_id}/outputs
GET /bff/events/subscribe
```

Dev/demo-only BFF route:

```text
POST /bff/dev/demo-workflow-instances
```

Rules:

- Read-only console must not call patch apply, approval respond, or context update.
- UI refreshes board state through BFF / hooks / EventBridge proxy.
- Station details come from `workflow.board.get` and `station.output.list`; V4.0-A does not add a UI-only station detail API.
- V4.0-A console token should only need `workflows.read`, `board.read`, `stations.read`, `artifacts.read`, `jobs.read`, `quality.read`, `approvals.read`, and `events`.
- The current canvas drag model is UI-only: background pan, node drag, zoom and fit-view do not mutate V3.6 runtime objects.

## V4.0-B Editing

Implementation status: preparation shell complete. `apps/workflow-console` displays patch diff, risk flags and high-risk governance state through BFF structured route boundaries. It does not expose apply/reject/publish in the current C-stage shell. Real BFF/runtime E2E remains a later gate.

Allowed RPC:

```text
workflow.patch.propose
workflow.patch.diff
workflow.version.get
workflow.version.list
```

Future editing RPC, not exposed in the current shell:

```text
workflow.patch.apply
workflow.patch.reject
workflow.template.update_draft
workflow.template.publish
```

Allowed events:

```text
workflow.patch.proposed
workflow.patch.applied
workflow.patch.rejected
```

Allowed BFF routes:

```text
POST /bff/workflows/{workflow_template_id}/patches
GET /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff
```

Future BFF routes, not exposed in the current shell:

```text
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/apply
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/reject
POST /bff/workflows/{workflow_template_id}/publish
```

Rules:

- Patch apply changes draft only.
- High-risk patch with `requires_approval=true` must not be silently applied.
- Published version snapshot must not be mutated.
- Current shell only shows `查看 Diff`, `等待用户确认`, and `前往编辑面板`; it does not present direct Apply / Reject / Publish controls.

## V4.0-C AgentTalkWindow Shell

Implementation status: V4.0-C complete. `apps/workflow-console` now contains a fixture-first AgentTalk preparation shell with event source labels, patch proposal/diff display, approval notice, read-only `context.business` summary and non-mutating allowed actions. It is not a real UI+BFF+runtime E2E.

Allowed RPC:

```text
events.subscribe
workflow.patch.propose
workflow.patch.diff
workflow.context.get
workflow.board.get
```

Future operation RPC, not exposed in the current C-stage shell:

```text
approval.respond
```

Allowed events:

```text
approval.required
business.event.received
workflow.context.updated
workflow.patch.proposed
workflow.patch.applied
workflow.patch.rejected
```

Allowed BFF routes:

```text
GET /bff/embed/bootstrap
GET /bff/events/subscribe
POST /bff/workflows/{workflow_template_id}/patches
GET /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff
```

Future operation BFF route, not exposed in the current C-stage shell:

```text
POST /bff/approvals/{approval_id}/respond
```

Rules:

- Agent can propose/diff only.
- AgentTalkWindow shell is not a full workflow state machine.
- AgentTalk fixture allowed actions are limited to `explain_workflow`, `summarize_events`, `show_patch_diff`, `show_approval_notice`, and `show_context_summary`.
- AgentTalkShell must not expose patch apply/reject/publish, approval respond, context update, business event emit, or workflow start actions.

## V4.0-D Operation Panels

Allowed RPC:

```text
quality.evaluation.get
quality.evaluation.list
approval.respond
workflow.context.get
workflow.context.update
business.event.emit
business.event.bind
workflow.board.get
```

Allowed events:

```text
approval.required
business.event.received
workflow.context.updated
```

Allowed BFF routes:

```text
GET /bff/quality-evaluations
POST /bff/approvals/{approval_id}/respond
GET /bff/workflow-instances/{workflow_instance_id}/context
PATCH /bff/workflow-instances/{workflow_instance_id}/context
POST /bff/workflow-instances/{workflow_instance_id}/business-events
POST /bff/workflow-instances/{workflow_instance_id}/business-event-bindings
```

Rules:

- Context panel may only write `context.business`.
- Quality panel reads quality records; it does not run evaluators by itself.

## V4.0-E Reference Console E2E

Allowed RPC:

```text
All V4.0-A through V4.0-D allowed RPCs
```

Allowed events:

```text
All V4.0-A through V4.0-D live events
```

Allowed BFF routes:

```text
All V4.0-A through V4.0-D BFF routes
```

Rules:

- Reference console must use a platform-neutral workflow.
- It must not depend on Meeting / Knowledge / Video / external MCP.
- It must prove scope isolation and redaction.
