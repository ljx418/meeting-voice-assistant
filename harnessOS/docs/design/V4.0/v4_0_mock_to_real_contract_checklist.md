# V4.0 Mock-to-Real Contract Checklist

文档状态：V4.0-Z complete checklist。每个 V4.0 UI mock 字段都必须落入本表结构，不允许把 mock schema 直接提升为 runtime contract。

## Required Table Shape

| UI 区域 | UI 字段 | 来源 | 对应 API | 是否可持久化 | 是否可写回 runtime | 是否包含敏感信息 | 是否需要 redaction | mock 到期阶段 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Workflow Canvas | workflow title | V3.6 API | `workflow.template.get` | yes | yes, via patch/draft | no | no | V4.0-B |
| Workflow Canvas | selected node | UI-only transient | none | no | no | no | no | never persisted |
| Workflow Canvas | node x/y | UI-only transient | none | local UI only | no | no | no | never persisted |
| Workflow Canvas | canvas zoom | UI-only transient | none | local UI only | no | no | no | never persisted |
| Workflow Canvas | current station status | V3.6 API | `workflow.board.get` | server-owned | no | no | yes, if trace summary included | V4.0-A |
| Workflow Canvas | canvas projection | V4.0 BFF/UI read model | `/bff/instances/{id}/canvas-projection` | derived read model | no | possible source refs | yes | V4.0-N |
| Workflow Canvas | projection freshness | V4.0 BFF/UI read model | `/bff/instances/{id}/canvas-projection` | derived read model | no | no | no | V4.0-O |
| Workflow Canvas | patch queue selection | V4.0 BFF/UI read model + UI-only selected id | `/bff/workflows/{id}/patches` | BFF-local read model | no | possible patch summary | yes | V4.0-O |
| Node Library | controlled catalog item | V4.0 BFF controlled catalog | `/bff/workflows/{id}/node-catalog` | server-owned descriptor | no direct runtime write | no | no | V4.0-N |
| Node Library | catalog version mismatch | V4.0 BFF/UI read model | `/bff/workflows/{id}/node-catalog` | no | no | no | no | V4.0-O |
| Edge Editing | edge proposal payload | V3.6 patch API via BFF | `workflow.patch.propose` with `operation=update_edge` | proposal only | yes, through patch apply only | possible schema refs | yes | V4.0-N |
| Edge Editing | edge compatibility result | V4.0 BFF validation | `workflow.patch.propose` validation | no | no | no | no | V4.0-O |
| Inspector | node config | V3.6 API | `workflow.patch.diff/apply` | yes | yes, through patch only | possible | yes | V4.0-B |
| Inspector | dirty form state | UI-only transient | none until `生成 Patch` | local UI only | no | possible user text | yes before submit | V4.0-N |
| Inspector | field allowlist result | V4.0 BFF validation | `workflow.patch.propose` validation | no | no | possible rejected field names | yes | V4.0-O |
| Quality Panel | score | V3.6 API | `quality.evaluation.get/list` | server-owned | no | no | no | V4.0-D |
| Approval Panel | decision | V3.6 API | `approval.respond` | server-owned | yes, action API | possible reason text | yes | V4.0-D |
| Context Panel | business context value | V3.6 API | `workflow.context.get/update` | yes | yes, only `context.business` | possible | yes | V4.0-D |
| Reference Console | board DTO | V3.6 API via BFF DTO | `workflow.board.get` | server-owned | no | possible trace summary | yes | V4.0-E |
| Reference Console | seeded patch diff | V3.6 API via BFF DTO | `workflow.patch.diff` | server-owned | no apply in E | possible | yes | V4.0-E |
| Reference Console | business event binding result | V3.6 API via BFF DTO | `business.event.emit` + `workflow.context.get` | yes | yes, only `context.business` | possible payload | yes | V4.0-E |
| Reference Console | approval side-effect result | V3.6 API via BFF DTO | `approval.respond` + `workflow.instance.status` | server-owned | explicit user action only | possible reason text | yes | V4.0-E |
| Reference Console | event refresh | V3.6 EventBridge via BFF | `events.subscribe` / `/bff/events/subscribe` | no | no | possible event data | yes | V4.0-E |
| Browser Smoke | browser network calls | V3.5/V4.0 BFF contract | `/bff/*` only | no | no | possible headers | yes | V4.0-F |
| Browser Smoke | DOM text | redacted BFF DTO + UI state | BFF DTO routes | no | no | possible if DTO unsafe | yes | V4.0-F |
| Agent Assistant | agent session | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/session` | BFF-local dev/local only | no runtime write | possible message refs | yes | V4.0-I |
| Agent Assistant | agent message | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/messages` | BFF-local dev/local only | no runtime write | possible user text | yes | V4.0-I |
| Agent Assistant | agent suggestion | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/suggestions` | BFF-local dev/local only | no runtime write | possible patch summary | yes | V4.0-I |
| Agent Assistant | action intent | V4.0 BFF/UI layer | BFF validation + optional `workflow.patch.propose` | BFF-local / proposal only | no direct mutation | possible payload summary | yes | V4.0-I |
| Agent Governance | action proposal | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/action-proposals` | BFF-local dev/local only | no runtime write | possible payload summary | yes | V4.0-J |
| Agent Governance | action policy decision | V4.0 BFF/UI layer | BFF validation | BFF-local dev/local only | no execution | no | yes | V4.0-J |
| Agent Handoff | action handoff | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/action-proposals/{proposal_id}/handoff` | BFF-local dev/local only | no direct mutation | possible form prefill summary | yes | V4.0-K |
| Agent Handoff | suggested form prefill | V4.0 BFF/UI layer | operation panel receives handoff DTO | UI/BFF-local only | only after user-confirmed panel action | possible user text | yes | V4.0-K |
| Agent Handoff Lifecycle | handoff status | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/action-handoffs/{handoff_id}` | BFF-local dev/local only | no direct mutation | no | yes | V4.0-L |
| Agent Handoff Lifecycle | handoff audit summary | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/action-handoffs/{handoff_id}/audit` | BFF-local dev/local only | no | possible redacted resource refs | yes | V4.0-L |
| Agent Handoff Lifecycle | recovery handoff id | UI-only transient + BFF lookup | `?handoff_id=...` then BFF handoff DTO | local URL only | no | no | no | V4.0-L |
| Governance Review | operation evidence list | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/operation-evidence` | BFF-local dev/local only | no | possible redacted resource refs | yes | V4.0-M |
| Governance Review | evidence detail | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/operation-evidence/{evidence_id}` | BFF-local dev/local only | no | possible redacted runtime refs | yes | V4.0-M |
| Governance Review | governance summary | V4.0 BFF/UI layer | `/bff/instances/{id}/agent/governance-review` | derived read model | no | possible redacted audit refs | yes | V4.0-M |
| Executor Design Gate | policy / capability / sandbox contract | V4.0 design audit artifact | `v4_0_q_controlled_executor_design_gate_contract.json` | docs only | no | no raw payload | yes | V4.0-Q |
| Production Readiness Preflight | production gap register | V4.0 design audit artifact | `v4_0_r_production_readiness_preflight_contract.json` | docs only | no | possible evidence labels only | yes | V4.0-R |
| Side Panel | panel collapsed | UI-only transient | none | local UI only | no | no | no | never persisted |
| Side Panel | side panel width | UI-only transient | none | local UI only | no | no | no | never persisted |
| Tabs | active tab | UI-only transient | none | local UI only | no | no | no | never persisted |
| Filters | filter keyword | UI-only transient | none | local UI only | no | no | no | never persisted |

## Source Values

Allowed source values:

```text
V3.6 API
V3.5 adaptation
UI-only transient
future
```

## Rules

- `canvas x/y/zoom/selection/panel collapsed/side panel width/active tab/filter keyword` are UI-only transient state.
- UI-only transient state must not be written back to V3.6 runtime contracts.
- Any field containing trace summary, approval reason, context payload, patch diff, or user-provided metadata must be redaction-aware.
- Future fields must include a target phase before implementation.
- V4.0-F browser smoke must fail if real mode silently falls back to demoData.
- V4.0-F browser smoke must fail if DOM contains token/raw payload text or if browser network directly calls `/v1/rpc` or `/v1/events/subscribe`.
- V4.0-I Agent state is a BFF/UI layer dev/local baseline. It must not be written into V3.6 WorkflowTemplate, WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun, Core Store, or runtime contract objects.
- V4.0-I Agent action intents are non-executable by default. `source=agent` may propose patch, but apply/reject/publish/approval/context/business-event operations remain forbidden in the Agent panel.
- V4.0-J Agent action proposal is still non-executable. Proposal lifecycle must not include `executed`, and proposal cards must only expose details, diff, navigation, and dismiss controls.
- V4.0-L Agent handoff lifecycle remains BFF/UI-local. Handoff status may become `active/opened/used_for_user_confirmed_action/dismissed/expired/stale/blocked`, but it must not create an Agent executor path or write V3.6 runtime objects directly.
- V4.0-M operation evidence remains BFF/UI-local and append-only. Governance review is a derived read model and must not execute mutation or write V3.6 runtime objects directly.
- V4.0-N CanvasDraftProjection is a UI-only read model derived from WorkflowDraft/WorkflowTemplate, BoardDTO/InstanceStatusDTO and PatchDiffDTO. It must not include persisted layout state, secrets, raw trace payload, raw artifact content or raw connector payload.
- V4.0-O PatchQueueDTO, projection freshness markers and catalog version mismatch state remain BFF/UI read models. They must not write WorkflowTemplate, WorkflowDraft, WorkflowVersion or WorkflowStore directly.
- V4.0-O proposal payloads must reject `x/y/zoom/viewport/selectedNode/panelCollapsed/activeTab`, token fields, Authorization, raw trace payload, raw artifact content and raw connector payload.
- V4.0-Q controlled executor design gate contract is docs-only and must not become runtime configuration, executor allowlist, BFF route, or frontend executable control.
- V4.0-R production readiness preflight contract is docs-only and must not become production auth, OAuth/SSO, tenant admin, token rotation/revocation, quota, audit export, or production onboarding implementation.
- V4.0-S production auth / tenant boundary design contract is docs-only and must not become production auth middleware, OAuth/SSO/OIDC/SAML route, login callback, tenant control plane, token rotation/revocation, V3.6 runtime contract, or frontend production-ready UI.
## V4.0-Z Final Audit Update

T-Z add design contracts only. They do not promote token lifecycle, secret management, observability, audit export, external app onboarding, production auth, tenant control plane, or executor fields into V3.6 runtime contracts.

Allowed final claim:

```text
V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.
```

No False Green: mock-to-real coverage still forbids turning UI-only/design-gate objects into runtime truth. 不能声明 production-ready external app support, enterprise auth ready, multi-tenant control plane ready, controlled executor ready, complete Workflow Studio ready, or complete AgentTalkWindow ready.
