# V4.0 Event Contract Map

文档状态：V4.0-E event bridge integration baseline。本文定义 V4.0 UI 可以消费的事件边界；当前 Workflow Console 已通过 BFF EventBridge proxy 接入真实 SSE replay/follow 路径，demo event feed 仅在显式 fixture mode 下使用。

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
