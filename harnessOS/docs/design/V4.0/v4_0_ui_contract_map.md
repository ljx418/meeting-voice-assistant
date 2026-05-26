# V4.0 UI Contract Map

文档状态：V4.0-Z complete。本文定义 Workflow Console / Studio / AgentTalkWindow 前置 UI 可以消费的 RPC、事件和 BFF route，并记录当前 `apps/workflow-console` 已实现的页面边界。V4.0-Z 只完成 final audit / release gate，不新增 production auth、OAuth/SSO、OIDC/SAML、login callback、tenant admin、token lifecycle、quota、audit export、onboarding UI route 或 executor UI route。

## Terminology

| 中文术语 | Runtime Mapping | 说明 |
| --- | --- | --- |
| 节点库 | Station / descriptor catalog | 可拖入工作流的节点集合。 |
| 节点 | Station candidate | 节点库中的可用定义。 |
| 节点分类 | Station category / descriptor metadata | 节点库分组。 |
| 工作流节点 | Station in WorkflowTemplate / WorkflowDraft | 已进入某个 workflow 的节点。 |
| 连线 / 工作流边 | WorkflowEdge | 工作流节点之间的数据或控制关系。 |
| 节点配置 / Inspector | Station + ArtifactContract + QualityContract + approval policy | 通过 patch 修改 draft。 |
| Agent 助手 | Governed stateful Agent assistant baseline + handoff lifecycle | BFF/UI 层 session/message/suggestion/action proposal/handoff；handoff 支持 lifecycle、audit、recovery 和 stale/blocked guard；只能 explain/summarize/propose/show diff/交接到用户确认面板，不直接 apply/reject/publish/respond。 |
| Production readiness preflight | Gap / audit read model only | R 阶段只登记生产化 gap，不新增 OAuth/SSO、tenant admin、token rotate/revoke、quota、audit export 或 production onboarding UI。 |
| Production auth / tenant boundary design | Design contract only | S 阶段只登记 identity matrix、tenant isolation、OAuth / SSO gap 和 capability token binding，不新增 production auth、OAuth/SSO、tenant control plane 或 token lifecycle UI。 |

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
ghost node
drag state
active handoff
handoff recovery target
production preflight contract review state
production auth tenant design review state
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

Implementation status: complete and refreshed into a canvas-first Workflow Studio shell. V4.0-A2 has connected the shell to real BFF read/event data. The UI contains top bar, left `节点库`, Stitch latest light visual tokens, ComfyUI-like full workbench canvas, right Agent 工作流助手 / Inspector / Patch Diff tabs and bottom run panel. The canvas is the bottom workbench layer; node library, Agent panel, Inspector, canvas toolbar and run panel float above it. Default mode now consumes BFF frontend DTOs; demo/read models are explicit `VITE_HARNESSOS_DEMO_MODE=true` fixtures only.

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

V4.0-A2 implemented BFF routes:

```text
GET /bff/workflows
GET /bff/workflows/{workflow_template_id}
GET /bff/workflows/{workflow_template_id}/versions
GET /bff/instances
GET /bff/instances/{workflow_instance_id}/status
GET /bff/instances/{workflow_instance_id}/board
GET /bff/stations/{station_run_id}/outputs
GET /bff/instances/{workflow_instance_id}/stations/{station_run_id}/outputs
GET /bff/artifacts/{artifact_id}/metadata
GET /bff/artifacts/{artifact_id}/lineage
GET /bff/instances/{workflow_instance_id}/artifacts/{artifact_id}/metadata
GET /bff/instances/{workflow_instance_id}/artifacts/{artifact_id}/lineage
GET /bff/events/subscribe
```

Dev/demo-only BFF route:

```text
POST /bff/dev/demo-workflow-instances
```

Rules:

- Read-only console must not call patch apply, approval respond, or context update.
- UI refreshes board state through BFF / hooks / EventBridge proxy.
- Real mode API errors render an error state and must not silently fallback to demoData.
- BFF routes return redacted frontend DTOs instead of raw Gateway RPC payloads.
- EventBridge events only trigger refresh/display; UI reloads `workflow.board.get` / `workflow.instance.status` and does not construct runtime state from event payloads.
- Station details come from `workflow.board.get` and `station.output.list`; V4.0-A does not add a UI-only station detail API.
- V4.0-A console token should only need `workflows.read`, `board.read`, `stations.read`, `artifacts.read`, `jobs.read`, `quality.read`, `approvals.read`, and `events`.
- The current canvas drag model is UI-only: background pan, node drag, zoom and fit-view do not mutate V3.6 runtime objects.
- The current visual model is UI-only: light surfaces, blue-purple accents, dotted grid density, card styling and panel spacing must not be written into V3.6 runtime contracts.
- Agent Copilot copy and suggestion cards are UI preparation content: natural-language draft generation, node optimization suggestions and disabled apply-to-draft wording do not mutate runtime state until a later BFF/runtime E2E phase.
- Canvas z-order is part of the UI contract: the canvas must remain a first-class workbench layer behind panels, not a nested middle-column card.
- Narrow viewport behavior is part of the UI contract: on compact screens, the header must stay compact, side panels must default to floating drawer triggers, and the canvas must remain visible as the primary workbench surface.

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

Implementation status: complete for dev/local operation panels. `apps/workflow-console` now includes `QualityPanel`, `ApprovalPanel`, and `ContextPanel`, backed by structured BFF DTO routes. Quality remains read-only; approval response requires explicit user confirmation from the approval panel; context updates are limited to path-based writes under `context.business`; business events are concrete `business.*` events only.

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
GET /bff/instances/{workflow_instance_id}/quality
GET /bff/instances/{workflow_instance_id}/quality/{evaluation_id}
GET /bff/instances/{workflow_instance_id}/approvals
POST /bff/instances/{workflow_instance_id}/approvals/{approval_id}/respond
GET /bff/instances/{workflow_instance_id}/context
POST /bff/instances/{workflow_instance_id}/context/update
POST /bff/instances/{workflow_instance_id}/business-events
```

Rules:

- Context panel may only write `context.business`.
- Quality panel reads quality records; it does not run evaluators by itself.
- `business.event.bind` remains part of the V3.6 workflow context contract. The V4.0-D BFF surface does not expose a standalone bind route; it accepts a constrained optional binding descriptor only through the instance-scoped business event route.
- Approval panel is the only UI component that can call workflow-bound approval response in this phase; Agent shell must not auto-approve.
- BFF routes must validate both scope and instance ownership: same-scope wrong-instance resources are rejected.
- BFF returns redacted `ApprovalDTO`, `QualityEvaluationDTO`, `ContextDTO`, `BusinessEventDTO`, and `OperationResultDTO`; it does not pass through raw Gateway payloads.
- EventBridge remains a refresh/display signal. The UI reloads board/status/panels after operation events and does not build runtime truth from event payloads.
- V4.0-D must not expose `workflow.patch.apply/reject`, `workflow.template.publish`, `workflow.instance.start`, or `quality.evaluation.create/attach`.

## V4.0-E Reference Console E2E

Implementation status: complete at component-level + BFF integration E2E. V4.0-E 使用平台中立 runtime fixture，通过 Gateway / V3.6 runtime 生成真实 board/status/output/artifact metadata/lineage/approval/quality/context/patch DTO，并通过 frontend component tests 渲染 BFF-style real DTO。V4.0-F 已补齐 browser-level Playwright smoke，因此当前可声明 browser smoke baseline。

Allowed RPC:

```text
All V4.0-A through V4.0-D allowed RPCs
workflow.patch.diff
```

Allowed events:

```text
All V4.0-A through V4.0-D live events
```

Allowed BFF routes:

```text
All V4.0-A through V4.0-D BFF routes
GET /bff/instances/{workflow_instance_id}/patches/{workflow_patch_id}/diff
```

Rules:

- Reference console must use a platform-neutral workflow.
- It must not depend on Meeting / Knowledge / Video / external MCP.
- It must prove scope isolation and redaction.
- BusinessEventBinding is part of the fixture: `business.video.scene.selected` maps `event.payload.scene_id` to `context.business.selected_scene`.
- Seeded patch diff must come from the V3.6 patch repository or backend fixture, not frontend demoData.
- UI may render PatchDiffDTO and risk flags, but must not call patch apply/reject/publish.
- Approval respond must be explicit user action from the approval panel and must prove workflow-bound side-effect in board/status refresh.
- EventBridge is refresh/display only; the UI must reload BFF DTOs and must not trust event payload as runtime state.
- E2E mode must not import demoData and must fail if BFF/runtime fixture is unavailable.

## V4.0-F Browser Smoke Baseline

Implementation status: complete. V4.0-F does not add new mutation capabilities; it validates the existing V4.0-E integration baseline in a real browser with fixed Playwright, `npm run build`, and Vite preview.

Allowed RPC:

```text
Same as V4.0-E through BFF structured routes only.
```

Allowed browser-visible routes:

```text
/bff/*
```

Forbidden browser-visible routes:

```text
/v1/rpc
/v1/events/subscribe
```

Browser smoke must cover:

```text
open workflow console
select workflow instance
render board
render station / artifact / approval / quality / trace summary
approve via ApprovalPanel
update context.business
receive EventBridge refresh
```

Rules:

- Browser smoke must run in real mode, not silent demo fallback.
- CI smoke uses build output through Vite preview; dev server is only for local debugging.
- The browser must connect to the same test BFF / V3.6 runtime fixture server.
- `VITE_HARNESSOS_DEMO_MODE=false` is required, and the DOM must not show `Demo / Fixture`.
- EventBridge refresh must be triggered through a controlled test event path; fake event status payload must not be trusted as runtime truth.
- Browser network interception must fail the test if the UI directly calls `/v1/rpc` or `/v1/events/subscribe`.
- DOM must not contain token, Authorization, subscription token, raw trace payload, raw artifact content, raw connector payload, or secret fixture values.
- Playwright should use stable `data-testid` selectors for console, instance selector, board, panels, approve button, context update, and event feed.
- Patch apply/reject/publish UI actions are now enabled only through user-confirmed BFF structured routes.
- This phase upgrades the claim to `V4.0-G complete: governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console`.

## V4.0-H Canvas-to-runtime Bridge

Implementation status: complete. V4.0-H maps canvas and Inspector actions to WorkflowPatch proposals. It does not create Station / WorkflowEdge directly and does not persist UI layout.

Completion evidence:

- `NodeAddIntent` creates `add_station` proposal payload from the allowed node catalog.
- `EdgeAddIntent` uses `operation=update_edge` with `edge_patch.action=add/remove/update`; no arbitrary `add_edge` RPC surface was added.
- `InspectorUpdateIntent` maps local dirty state to controlled patch proposals only after the user clicks `生成 Patch`.
- UI layout state (`x/y/zoom/selection/panelCollapsed/activeTab/viewport`) remains UI-only transient state and is rejected by the BFF proposal validator.
- Apply / Reject / Publish continue to use V4.0-G governed routes and require explicit user confirmation.

Allowed BFF routes:

```text
POST /bff/workflows/{workflow_template_id}/patches
GET /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/apply
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/reject
POST /bff/workflows/{workflow_template_id}/publish
```

Proposal request shape:

```text
source = canvas | inspector | workflow_console
intent_type = node_add | edge_add | inspector_update
operation = add_station | update_edge | update_station_prompt | update_connector | update_artifact_contract | update_quality_rule | update_approval_point
payload = controlled patch payload
```

Rules:

- Node drag creates a ghost node and `NodeAddIntent`; it does not write Station.
- Edge interaction creates `EdgeAddIntent` using `operation=update_edge` with `edge_patch.action=add/remove/update`; it does not write WorkflowEdge.
- Inspector typing is local dirty state; only `生成 Patch` sends `InspectorUpdateIntent`.
- `x/y/zoom/selection/panelCollapsed/activeTab/viewport` remain UI-only transient state.
- Apply / Reject / Publish still use V4.0-G user-confirmed routes.
- High-risk patch governance remains active.

## V4.0-N/O Canvas Editing Readiness And Proposal Workflow

Implementation status: V4.0-O complete and preserved through V4.0-Z final audit. V4.0-N added controlled catalog, CanvasDraftProjection, node/edge/Inspector proposal flow and layout boundary. V4.0-O hardened the proposal workflow with patch queue selection, projection freshness, catalog versioning, Inspector mapping V2, edge validation V2, fixture isolation and claim guard tests.

Allowed BFF routes:

```text
GET /bff/instances/{workflow_instance_id}/canvas-projection
GET /bff/workflows/{workflow_template_id}/node-catalog
GET /bff/workflows/{workflow_template_id}/patches
POST /bff/workflows/{workflow_template_id}/patches
GET /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/apply
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/reject
POST /bff/workflows/{workflow_template_id}/publish
```

Required UI read models:

```text
CanvasDraftProjection
PatchQueueDTO
NodeCatalogItem
NodeTemplateDescriptor
StationDescriptorMapping
PatchDiffDTO
```

Rules:

- CanvasDraftProjection is UI-only read model derived from BFF truth; it must include source_refs, generated_at, draft_revision and board/status freshness markers.
- PatchQueueDTO is a BFF/UI read model for proposal selection. It must not become WorkflowDraft truth.
- selected_patch_id, selectedNode, viewport, zoom, x/y, panelCollapsed and activeTab remain UI-only transient state.
- Node catalog semantics come from BFF controlled catalog. The frontend may render catalog data, but must not define runtime semantics independently.
- Inspector typing is local dirty state. Only `生成 Patch` sends one proposal request.
- Edge create/update/remove continues to use `operation=update_edge`; there is no new direct add_edge RPC.
- EventBridge payload only triggers refresh. The UI must reload canvas projection, patch queue, board/status and diff DTOs from BFF routes.
- V4.0-O must not introduce direct `/v1/rpc`, direct `/v1/events/subscribe`, direct WorkflowStore access, or layout fields in proposal payloads.

## V4.0-I AgentTalkWindow Stateful Assistant

Implementation status: complete for dev/local governed Agent assistant baseline. V4.0-I adds BFF/UI layer `AgentTalkSession`, `AgentMessage`, `AgentSuggestion`, and `AgentActionIntent` objects. These objects do not enter the V3.6 Workflow Runtime Contract and do not write WorkflowTemplate, WorkflowDraft, WorkflowVersion, StationRun, or Core Store records.

Allowed Agent action intents:

```text
explain_workflow
summarize_events
suggest_patch
show_patch_diff
show_approval_notice
show_context_summary
navigate_to_editing_panel
```

Forbidden Agent action intents:

```text
apply_patch
reject_patch
publish_version
respond_approval
update_context
emit_business_event
start_workflow
rerun_station
```

Allowed BFF routes:

```text
GET /bff/instances/{workflow_instance_id}/agent/session
POST /bff/instances/{workflow_instance_id}/agent/messages
GET /bff/instances/{workflow_instance_id}/agent/suggestions
POST /bff/instances/{workflow_instance_id}/agent/suggestions/{suggestion_id}/dismiss
POST /bff/workflows/{workflow_template_id}/patches
GET /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff
```

Capability profile:

```text
agent_talk.read
agent_talk.write
agent_suggestions.read
agent_suggestions.write
workflows.read
board.read
stations.read
artifacts.read
quality.read
approvals.read
workflow_context.read
workflow_patches.read
events
```

Rules:

- Agent routes must not require or hold `workflow_patches.write`, `workflow_versions.publish`, `approvals`, `workflow_context.write`, `business_events.write`, or `workflows.execute`.
- `source=agent` may create a patch proposal, but cannot apply, reject, publish, approve, update context, emit business event, start workflow, or rerun station.
- Deterministic Agent suggestions are fixture/rule-backed and do not call external LLM, external MCP, connector, or model executor.
- Agent panel must not show Apply Patch, Reject Patch, Publish Version, Approve, Reject, 自动应用, 自动发布, or 已帮你修改并发布.
- Agent timeline and event display use EventBridge only as refresh/display signal. Agent summary is refreshed from board/status/context/patch DTOs and does not trust event payload as runtime truth.

## V4.0-J AgentTalk Governance

Implementation status: complete. V4.0-J adds BFF/UI layer Agent action proposals. These proposals are not executable operations and do not enter V3.6 Workflow Runtime Contract objects.

Allowed BFF routes:

```text
GET /bff/instances/{workflow_instance_id}/agent/action-proposals
POST /bff/instances/{workflow_instance_id}/agent/action-proposals
GET /bff/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}
POST /bff/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}/dismiss
```

Forbidden Agent BFF routes:

```text
/execute
/run
/apply
/publish
```

Rules:

- Agent action proposal lifecycle must not include `executed`.
- Proposal cards can show details, show diff, navigate to a panel, or dismiss.
- Proposal cards must not apply patch, reject patch, publish version, approve/reject approval, update context, emit business event, start workflow, rerun station, call connector, or call external LLM.
- `agent_actions.read/write` governs this surface.

## V4.0-K/L/M Agent Handoff And Evidence

Implementation status: complete through V4.0-M. Agent action handoff and operation evidence are BFF/UI-layer objects. They do not enter V3.6 Workflow Runtime Contract and do not create an executor path.

Allowed BFF routes:

```text
POST /bff/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}/handoff
GET /bff/instances/{workflow_instance_id}/agent/action-handoffs
GET /bff/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}
POST /bff/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}/dismiss
GET /bff/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}/audit
GET /bff/instances/{workflow_instance_id}/agent/operation-evidence
GET /bff/instances/{workflow_instance_id}/agent/operation-evidence/{evidence_id}
GET /bff/instances/{workflow_instance_id}/agent/governance-review
```

Capability profile:

```text
agent_handoffs.read
agent_handoffs.write
agent_audit.read
operation_evidence.read
governance_review.read
```

Rules:

- Handoff routes only create/read/dismiss handoff DTOs; they do not execute mutation.
- Operation evidence is created only after user-confirmed operation route attempts.
- Governance Review Panel is read-only and may only navigate back to existing operation panels.
- UI must not construct evidence truth from EventBridge payload; it must reload evidence/governance DTOs.
- Agent panel still must not show Apply, Publish, Approve, Reject, Execute, Run, 自动应用, 自动发布, or 已帮你修改并发布.

## V4.0-Q/R/S Design Gates

Implementation status: complete through V4.0-S. Q/R/S contracts are docs-only audit artifacts, not runtime configuration.

Forbidden production BFF / UI routes:

```text
/oauth/*
/sso/*
/oidc/*
/saml/*
/login/callback
/tenant/*
/admin/tenant/*
/production/onboarding
/token/rotate
/token/revoke
/quota/*
/audit/export
```

Rules:

- V4.0-Q controlled executor design contract must not create frontend executor controls, executor client methods, or runtime mutation routes.
- V4.0-R production readiness preflight contract must not create frontend OAuth/SSO, tenant admin, token rotation/revocation, quota, audit export, production onboarding, enterprise auth, or production-ready copy.
- V4.0-S production auth / tenant boundary design contract must not create frontend OAuth/SSO/OIDC/SAML/callback, tenant admin, token rotation/revocation, production auth middleware, enterprise auth, or production-ready copy.
## V4.0-Z Final Audit Update

V4.0-Z does not add UI runtime capability. It only records the final audit package for governed dev/local Workflow Console and production readiness design gates.

Allowed final claim:

```text
V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.
```

UI boundary remains unchanged: workflow-console must use BFF DTOs and must not add production auth, tenant admin, token lifecycle, secret manager, audit export, production onboarding, or executor UI routes. No False Green: 不能声明 complete Workflow Studio ready, complete AgentTalkWindow ready, controlled executor ready, Agent executor ready, enterprise auth ready, multi-tenant control plane ready, OAuth ready, SSO ready, or production-ready external app support.
