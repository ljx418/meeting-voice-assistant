# V4.0-N Canvas Editing Readiness Plan

阶段定位：V4.0-N 在 V4.0-H canvas patch bridge 之上补齐 dev/local Workflow Console 的画布编辑准备基线。Canvas 仍只是 UI projection 和 patch proposal surface，不是 runtime truth，不直接写 `WorkflowDraft`、`WorkflowVersion` 或 `WorkflowStore`。

完成后最多声明：

```text
V4.0-N complete: canvas editing readiness baseline ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete Workflow Studio ready
full low-code canvas editing ready
direct canvas-to-runtime mutation ready
complete AgentTalkWindow ready
controlled executor ready
autonomous workflow editing ready
production-ready external app support
```

## PR Slices

| Slice | 目标 | 边界 |
| --- | --- | --- |
| N-PR1 Controlled node catalog | 将前端轻量节点库收敛为 `NodeCatalogItem / NodeTemplateDescriptor / StationDescriptorMapping` 控制契约。 | 前端可渲染 catalog data，但不独立定义 runtime semantics。 |
| N-PR2 CanvasDraftProjection | 新增 UI-only `CanvasDraftProjection` read model。 | Projection 从 draft/template、board/status、patch diff 派生；不持久化 layout，不携带 raw payload。 |
| N-PR3 Node proposal flow | 节点 click/drag 生成 ghost node 和 `NodeAddIntent`，只创建 patch proposal。 | Apply 前 board/status/draft revision 不变；Apply 仍走 Editing Panel 用户确认路径。 |
| N-PR4 Edge proposal flow | 连线只使用 `operation=update_edge` 与 `edge_patch.action`。 | 不新增 `add_edge` route/RPC；不直接写 `WorkflowEdge`。 |
| N-PR5 Inspector form mapping | Inspector typing 只更新 local dirty state；“生成 Patch”调用 proposal route。 | 仅允许五类 inspector operations 和字段白名单。 |
| N-PR6 Layout boundary | `x/y/zoom/viewport/selectedNode/panelCollapsed/activeTab` 只作为 transient UI state。 | 不写入 template/draft/version/patch payload。 |

## Contract Requirements

Controlled catalog item 必须包含：

```text
catalog_id
catalog_version
node_template_id
station_kind
schema_version
allowed_skill_refs
allowed_connector_refs
allowed_artifact_kinds
allowed_quality_rules
allowed_approval_policies
```

BFF 必须拒绝：

- unknown node type。
- unsupported `skill_refs` / `connector_refs`。
- token / Authorization / raw trace / raw artifact / raw connector payload 字段。
- UI layout 字段进入 proposal payload。
- same-scope wrong-template / wrong-draft、cross-scope resource binding。

## CanvasDraftProjection

Truth precedence 固定为：

```text
1. WorkflowDraft / WorkflowTemplate for design structure
2. BoardDTO / InstanceStatusDTO for runtime state
3. PatchDiffDTO for pending proposal / diff state
4. UI local state only for selection, zoom, viewport, ghost nodes
```

Projection metadata 必须包含：

```text
source_refs
generated_at
draft_revision
board/status freshness marker
```

Projection 不得包含 persisted layout state、secrets、raw trace payload、raw artifact content 或 raw connector payload。

## Test Plan

新增 / 更新：

```text
tests/test_v4_0_canvas_editing_readiness_bff.py
tests/test_v4_0_canvas_editing_readiness_contract.py
tests/test_v4_0_canvas_editing_readiness_scope.py
tests/test_v4_0_canvas_editing_readiness_redaction.py
apps/workflow-console/src/__tests__/canvasEditingReadiness.test.tsx
apps/workflow-console/e2e/workflow-canvas-editing-readiness-smoke.spec.ts
```

验收覆盖：

- `NodeCatalogItem -> StationDescriptorMapping`。
- unknown node、unsupported refs、layout/sensitive/raw payload rejection。
- node add creates proposal only，apply 前 board/status/draft revision 不变。
- duplicate station id returns stable `WORKFLOW_PATCH_INVALID`。
- edge add only uses `update_edge`，self-loop / duplicate / missing station / cycle / incompatible artifact contracts rejected。
- Inspector typing 不发网络请求，“生成 Patch”才发 proposal。
- Apply/reject/publish 继续通过 governed Editing Panel，`user_confirmed=true` 且 `source=editing_panel`。
- high-risk governance blocks direct apply。
- Agent 不能 auto apply/publish/respond/update/emit/start/rerun。
- Browser 不请求 `/v1/rpc` 或 `/v1/events/subscribe`。
- DTO / DOM redaction。

## Risk Controls

- Canvas 不是 runtime truth。
- Node drag 不创建 Station。
- Edge drag 不写 WorkflowEdge。
- Inspector 不直接写 draft。
- Apply/reject/publish 仍要求用户显式确认。
- `requires_approval=true` 仍由 V4.0-G governance 阻断。
- EventBridge 只触发 refresh；UI 不从 event payload 构造 projection truth。
- UI layout 持久化是未来工作，必须使用独立 UI layout descriptor，不复用 V3.6 runtime objects。
