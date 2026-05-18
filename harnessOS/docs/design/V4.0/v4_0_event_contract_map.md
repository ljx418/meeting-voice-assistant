# V4.0 Event Contract Map

文档状态：V4.0-C event contract baseline。本文定义 V4.0 UI 可以消费的事件边界；当前 Workflow Console 已用 demo event feed 和 AgentTalk preparation shell 展示 workflow / approval / business / context / patch events，真实 BFF/EventBridge E2E 仍留到 V4.0-E。

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

V4.0-C status：`workflow.patch.proposed/applied/rejected` 已进入 Workflow Console event feed 与 AgentTalk shell 合同测试；AgentEventTimeline 会标注 `live / demo / trace_only` source。当前仍是 demo event data，不声明真实 live EventBridge UI E2E ready。

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
