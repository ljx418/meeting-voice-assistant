# V4.0 Event Contract Map

文档状态：V4.0-Z complete。本文定义 V4.0 UI 可以消费的事件边界；当前 Workflow Console 已通过 BFF EventBridge proxy 接入真实 SSE replay/follow 路径，demo event feed 仅在显式 fixture mode 下使用。V4.0-Z 不新增 production auth、tenant、OAuth/SSO、token lifecycle、secret、observability、external app onboarding 或 executor runtime event。

## Consumption Path

Production default：

```text
UI -> BFF / hooks / EventBridge proxy -> harnessOS events.subscribe -> /v1/events/subscribe
```

Dev direct：

```text
UI -> TypeScript SDK direct event descriptor -> harnessOS
```

Dev direct 只允许显式 dev mode 与受限 token。V4.0 UI 生产默认路径不直接使用 `/v1/events/subscribe`。

## Live Events

V4.0-A2 status：`/bff/events/subscribe` 已覆盖 SSE `id/event/data` 保留、Last-Event-ID / cursor、auth failure precheck、upstream subscription token / signed URL hiding。UI 只把 live event 当作 refresh/display signal，事实源仍是 `workflow.board.get` / `workflow.instance.status`。

V4.0-D status：Approval / Context operation panels consume live `approval.required`, `business.event.received`, and `workflow.context.updated` only as refresh/display signals. `approval.respond`, `workflow.context.update`, and `business.event.emit` success paths refresh board/status/panel data through BFF DTO routes; the UI does not derive runtime state directly from event payloads.

V4.0-E status：Reference Workflow Console E2E 覆盖 BFF SSE `id/event/data` 保留、Last-Event-ID/cursor、upstream subscription token hiding、auth failure 不打开 stream，以及 fake event payload status 不被 UI 采信。`approval.respond` 与 `business.event.emit` 后的 UI 更新必须通过重新拉取 board/status/context/approval DTO 完成。

V4.0-F complete：Browser smoke 固定使用 Playwright，在 build 后 Vite preview 中验证 EventBridge 只触发 refresh/display。Playwright 已拦截浏览器网络请求，断言 UI 不直接调用 `/v1/events/subscribe`，并通过可控 test event 触发后重新拉取 board/status/context/approval BFF DTO，而不是从 event payload 构造 runtime truth。

V4.0-G complete：Patch apply/reject/publish 后的 workflow patch / publish-related events 仍只触发 refresh/display。UI 重新拉取 template/version/diff/status/board，不从 event payload 构造 draft/version truth。

V4.0-H complete：Canvas / Inspector proposal 创建后的事件仍只触发 refresh/display。UI 不从 event payload 自建 Station / WorkflowEdge truth，继续重新拉取 BFF patch/diff/board/status。

V4.0-I complete：Agent assistant timeline 可以展示 live event，但 event 仍只触发 refresh/display。Agent summary、suggestion 和 patch card 不直接采信 event payload；收到事件后重新拉取 board/status/context/patch DTO。Agent state 是 BFF/UI 层对象，不进入 V3.6 Workflow Runtime Contract。

V4.0-J complete：Agent action proposal queue 仍不把 EventBridge payload 当作执行事实。Event 只触发 Agent session/suggestion/action proposal、board/status/context/patch DTO refresh。J 阶段不新增 executor event，也不声明 controlled executor ready。

V4.0-K complete：AgentActionHandoff 不新增 executor event。handoff created/opened/used 只进入 BFF audit 记录；EventBridge 仍只触发 refresh/display，最终 mutation 继续通过用户显式确认的 Editing / Approval / Context operation panel 路径完成。

V4.0-L complete：handoff lifecycle / recovery / stale / blocked 状态仍不新增 runtime EventBridge event。handoff opened、dismissed、expired、stale、blocked、used 只进入 BFF append-only audit；URL recovery 读取 handoff DTO 并打开目标 panel，不触发 mutation，也不从 EventBridge payload 构造执行事实。

V4.0-M complete：operation evidence / governance review 不新增 runtime EventBridge event。EventBridge 仍只触发 refresh，UI 必须重新拉 `/bff/instances/{id}/agent/operation-evidence` 和 `/bff/instances/{id}/agent/governance-review`，不得从 event payload 构造 evidence truth。

V4.0-N complete：CanvasDraftProjection 不新增 runtime EventBridge event。EventBridge 仍只触发 refresh，UI 必须重新拉 `/bff/instances/{id}/canvas-projection`、board/status 和 patch DTO，不得从 event payload 构造 canvas truth。

V4.0-O complete：PatchQueueDTO、projection freshness、catalog versioning、Inspector mapping V2 和 edge validation V2 不新增 runtime EventBridge event。EventBridge 仍只触发 refresh，UI 必须重新拉 canvas projection、patch queue、catalog、board/status 和 diff DTO，不得从 event payload 构造 patch queue truth、catalog truth、edge truth 或 evidence truth。Browser smoke 必须继续使用 fake event payload 验证 UI 不采信事件中的伪造 draft_revision、station、edge、patch_status 或 evidence 字段。

V4.0-Q complete：Controlled Executor Design Gate 不新增 executor event。EventBridge payload 不得构造 executor truth、agent action truth、patch truth、approval truth、evidence truth、board/status truth 或 context truth。

V4.0-R complete：Production Readiness Preflight 不新增 production readiness event。Auth/tenant/token/observability/external-app production gaps 只记录在机器可读 preflight contract 和文档中，不从 event payload 构造 production readiness truth。

V4.0-S complete：Production Auth / Tenant Boundary Follow-up Design 不新增 auth、tenant、OAuth、SSO、OIDC、SAML、login callback、token lifecycle 或 control-plane event。Identity matrix、tenant isolation matrix、OAuth / SSO gap 和 capability token binding 只记录在机器可读设计合同和文档中，不从 event payload 构造 auth truth、tenant truth、token truth 或 executor truth。

| Event | Channel | Source | V4.0 Usage | First UI Phase |
| --- | --- | --- | --- | --- |
| `workflow.instance.started` | workflow | V3.6 workflow runtime | Board refresh / status display | V4.0-A |
| `workflow.instance.completed` | workflow | V3.6 workflow runtime | Board refresh / status display | V4.0-A |
| `workflow.instance.failed` | workflow | V3.6 workflow runtime | Board refresh / status display | V4.0-A |
| `station.run.started` | workflow | V3.6 workflow runtime | Station board refresh | V4.0-A |
| `station.run.completed` | workflow | V3.6 workflow runtime | Station board refresh | V4.0-A |
| `station.run.failed` | workflow | V3.6 workflow runtime | Station board refresh | V4.0-A |
| `station.run.waiting_approval` | workflow | V3.6 workflow runtime | Station board refresh / approval summary | V4.0-A |
| `approval.required` | approval | V3.6 approval point | Approval panel / AgentTalkWindow shell | V4.0-A / V4.0-C |
| `artifact.registered` | artifact | Artifact registry | Artifact summary refresh | V4.0-A |
| `business.event.received` | business | V3.6 business event bridge | Context panel event feed | V4.0-D |
| `workflow.context.updated` | workflow_context | V3.6 workflow context | Context panel refresh | V4.0-D |
| `workflow.patch.proposed` | workflow_patch | V3.6 workflow patch | Patch diff feed / Agent proposal | V4.0-B / V4.0-C |
| `workflow.patch.applied` | workflow_patch | V3.6 workflow patch | Editing confirmation / board refresh | V4.0-B |
| `workflow.patch.rejected` | workflow_patch | V3.6 workflow patch | Editing status | V4.0-B |

## Trace-only Events

| Event | Reason | UI Handling |
| --- | --- | --- |
| `quality.evaluated` | V3.6-J does not declare live quality streaming ready. | UI reads quality through `quality.evaluation.get/list` or board summary. |
| station completion internals | Board API is the V4.0 read model. | UI reads station state from `workflow.board.get` / `workflow.instance.status`. |

## Future Events

| Event | Condition Before Use |
| --- | --- |
| live quality evaluation events | Requires EVENT_SCHEMAS update, SSE tests, docs update. |
| Workflow Studio canvas collaboration events | Requires a new V4.x collaboration contract. |
| production multi-user presence events | Requires auth/session model beyond V4.0 dev/local baseline. |

## No False Green

`quality.evaluated` must not be used as a V4.0-A or V4.0-C live EventBridge exit criterion until the runtime event schema and SSE tests exist.

V4.0-A2 仍不把 `quality.evaluated` 作为 live 出门条件；Quality 只从 board summary 或 `quality.evaluation.*` read API 消费。

V4.0-D 仍不把 `quality.evaluated` 作为 live 出门条件；Quality Panel 是 read-only + refresh，不调用 `quality.evaluation.create/attach`，也不要求 live quality SSE。

V4.0-E 仍不把 `quality.evaluated` 作为 live 出门条件；reference console 通过 quality read DTO 与 board summary 展示质量结果。

V4.0-F 仍不把 `quality.evaluated` 作为 live 出门条件；browser smoke 只验证 quality read DTO 在页面可见，不要求 live quality SSE。

V4.0-I 仍不把 `quality.evaluated` 作为 live 出门条件；Agent assistant 只通过 board/quality/context/patch DTO 展示摘要，不以 quality event payload 构造状态。

V4.0-O/R/S 仍不新增 canvas collaboration、catalog update、patch queue runtime event、production readiness runtime event 或 auth/tenant runtime event。若未来需要 live catalog/collaboration/production-readiness/auth/tenant event，必须先补 EVENT_SCHEMAS、SSE tests、BFF DTO redaction 和本文件更新。
## V4.0-Z Final Audit Update

V4.0-Z does not change EventBridge semantics. EventBridge still only triggers refresh and must not construct canvas truth, AgentTalk truth, token truth, secret truth, executor truth, evidence truth, board/status truth, or production tenant/auth truth from event payload.

Allowed final claim:

```text
V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.
```

No False Green: event coverage remains a dev/local Workflow Console and design-gate baseline. 不能声明 production-ready external app support, enterprise auth ready, multi-tenant control plane ready, controlled executor ready, or Agent executor ready.
