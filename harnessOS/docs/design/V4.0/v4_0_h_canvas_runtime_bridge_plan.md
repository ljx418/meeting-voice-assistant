# V4.0-H Canvas-to-runtime Bridge Plan

文档状态：implementation plan。  
前置阶段：`V4.0-G complete: governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console`。

## 1. Stage Positioning

V4.0-H 只做 canvas / Inspector 操作到受控 WorkflowPatch proposal 的桥接。

允许：

```text
Node drag -> NodeAddIntent -> workflow.patch.propose(add_station)
Edge drag -> EdgeAddIntent -> workflow.patch.propose(update_edge + edge_patch.action=add/remove/update)
Inspector dirty state -> InspectorUpdateIntent -> workflow.patch.propose(update_station_prompt / update_connector / update_artifact_contract / update_quality_rule / update_approval_point)
继续复用 V4.0-G 的 apply / reject / publish
```

禁止：

```text
直接写 WorkflowStore
直接修改 WorkflowDraft / WorkflowVersion snapshot
Node drag 直接创建 Station
Edge drag 直接写 WorkflowEdge
Inspector 表单输入自动写 draft
Agent 自动 apply / publish
UI layout 写入 V3.6 runtime contract
```

完成后只能声明：

```text
V4.0-H complete: canvas-to-runtime patch bridge ready for dev/local Workflow Console.
```

不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full low-code canvas editing ready
```

## 2. Contract Model

新增前端 intent：

```text
CanvasPatchIntent
NodeAddIntent
EdgeAddIntent
InspectorUpdateIntent
```

这些 intent 只生成 patch proposal payload，不直接写 draft/store/runtime。

统一 BFF proposal route：

```text
POST /bff/workflows/{workflow_template_id}/patches
```

request 必须包含：

```text
source = canvas | inspector | workflow_console
intent_type = node_add | edge_add | inspector_update
operation
payload
workflow_instance_id?
```

proposal 不要求 `user_confirmed`。Apply / Reject / Publish 继续沿用 V4.0-G route，并要求 `user_confirmed=true`。

## 3. Runtime Mapping

| UI action | Intent | Patch operation | Runtime write timing |
| --- | --- | --- | --- |
| Drag node to canvas | NodeAddIntent | add_station | Only after G apply path |
| Add edge | EdgeAddIntent | update_edge with edge_patch.action=add | Only after G apply path |
| Inspector prompt change | InspectorUpdateIntent | update_station_prompt | Only after G apply path |
| Inspector connector change | InspectorUpdateIntent | update_connector | Only after G apply path |
| Inspector artifact contract change | InspectorUpdateIntent | update_artifact_contract | Only after G apply path |
| Inspector quality rule change | InspectorUpdateIntent | update_quality_rule | Only after G apply path |
| Inspector approval policy change | InspectorUpdateIntent | update_approval_point | Only after G apply path |

`x/y/zoom/selection/panelCollapsed/activeTab/viewport` remain UI-only transient state.

## 4. Validation

BFF validates:

- `source` / `intent_type` / `operation` alignment.
- add_station station descriptor comes from allowed node catalog.
- station_id is unique in current draft.
- edge add references existing stations.
- self-loop and duplicate edge are rejected.
- connector_refs / skill_refs are allowlisted.
- quality threshold is valid.
- approval policy payload uses supported shape.
- payload contains no token / Authorization / raw payload / UI layout fields.

## 5. Test Plan

Focused tests:

```text
tests/test_v4_0_canvas_runtime_bridge_bff.py
tests/test_v4_0_canvas_runtime_bridge_contract.py
tests/test_v4_0_canvas_runtime_bridge_redaction.py
apps/workflow-console/src/__tests__/canvasRuntimeBridge.test.tsx
apps/workflow-console/e2e/workflow-canvas-bridge-smoke.spec.ts
```

Regression:

```text
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
```
