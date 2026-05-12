# V3.5 Embed Contract / AgentTalkWindow Preparation Plan

文档状态：V3.5-H Embed Contract complete；V3.5-I Reference App complete。

## 1. Goal

定义未来 AgentTalkWindow 所需的 embed contract。本阶段只做 contract、BFF bootstrap 示例和最小 demo fixture，不实现完整 AgentTalkWindow、React UI component 或 Workflow Studio。

完成后只能声明：

```text
Embed contract ready for dev/local AgentTalkWindow preparation
```

不能声明：

```text
AgentTalkWindow ready
Workflow Studio ready
external app ready
V3.5 complete
```

## 2. EmbedDefinition vs EmbedBootstrap

`EmbedDefinition` 是静态嵌入定义，不包含一次运行态字段。

字段：

- `schemaVersion`
- `embedId`
- `appId`
- `defaultProjectId`
- `defaultWorkspaceId`
- `capabilityMode`
- `transportMode`
- `allowedEventChannels`
- `allowedActions`
- `initialView`
- `artifactPreviewPolicy`
- `approvalPolicy`
- `tracePolicy`
- `theme`
- `metadata`

`EmbedBootstrap` 是运行时启动 payload，可包含：

- `embedDefinition`
- `session`
- `thread`
- `eventSubscription`

`sessionId`、`threadId`、`eventsourceUrl` 属于 bootstrap runtime payload，不进入静态 definition。

## 3. Token And Transport Boundary

`EmbedDefinition` 不得包含长期 capability token。`EmbedBootstrap` 不得返回 upstream `subscription_token`。

默认生产路径：

```text
capabilityMode=bff
transportMode=bff_proxy
Business UI -> BFF -> harnessOS
```

Dev/direct 只允许：

```text
capabilityMode=dev_direct
transportMode=direct_eventsource
受限 token / 显式 dev mode / short-lived signed URL
```

`eventsourceUrl` 默认必须是 BFF-local URL。JSON fixture、`JSON.stringify`、logs、debug output 不得包含 token 或 upstream signed URL query。

## 4. Allowed Actions

`allowedEventChannels` 只描述可观察的事件通道；`allowedActions` 描述可执行动作。

允许动作示例：

- `session.start`
- `turn.start`
- `events.subscribe`
- `approval.respond`
- `artifact.read_metadata`
- `artifact.lineage`
- `job.get`
- `pack.get`
- `connector.health`

禁止动作：

- `approval.approve`
- `approval.reject`
- `meeting.*`
- `knowledge.*`
- `scope_mode=all`
- legacy/debug/admin methods

## 5. Bootstrap Contract

`GET /bff/embed/bootstrap` 只是 BFF template / reference app 示例 route，不进入 harnessOS Core。

规则：

- 默认不创建 session。
- 只有 `create_session=true` 时才经过 BFF identity/scope/capability policy 和 SDK `session.start`。
- trace channel 默认不开放，除非具备 `traces.read/debug`。
- Browser 不看到 upstream `subscription_token`。
- Bootstrap 返回 BFF-local EventSource URL。

## 6. Event Union

事件 union 必须继续与 `EVENT_SCHEMAS` 对齐：

- chat: `turn.started`, `item.delta`, `turn.completed`, `turn.failed`
- job: `job.queued`, `job.running`, `job.completed`, `job.failed`, `job.cancelled`
- artifact: `artifact.registered`, `artifact.updated`, `artifact.read_blocked`
- approval: `approval.required`, `approval.approved`, `approval.rejected`
- trace: `trace.recorded`
- business: `business.*`

`artifact.created` 只能作为 `artifact.registered` alias，不作为 canonical event。

## 7. UI States

Embed consumer 必须能区分：

- `idle`
- `connecting`
- `streaming`
- `approval_required`
- `auth_required`
- `subscription_expired`
- `blocked`
- `failed`
- `completed`
- `reconnecting`
- `closed`

hooks 可以消费这些状态，但不承担完整 AgentTalkWindow 状态机。本阶段不实现 workflow graph editor。

## 8. Host Business Event

Host business event 只定义 shape：

```ts
{
  type: "business.*";
  payload: Record<string, unknown>;
  scope?: {
    appId?: string;
    projectId?: string;
    workspaceId?: string;
  };
}
```

本阶段只定义 shape，不实现 workflow context update 或 routing。`business.*` 仍只作为 namespace，不新增 Meeting/Knowledge 业务事件。

## 9. TypeScript Boundary

`sdk/typescript/src/embed.ts` 只导出类型和轻量 validation helper：

- `EmbedDefinition`
- `EmbedBootstrap`
- `HostBusinessEvent`
- `validateEmbedDefinition`
- `sanitizeEmbedBootstrapForLog`

禁止：

- React UI component
- AgentTalkWindow
- workflow state machine
- imports from `apps.*`, `core.*`, `GatewayService`, `RuntimeAdapter`

## 10. Minimal Demo

`examples/embed_contract_demo/` 只展示 contract shape。

要求：

- 不依赖 Meeting / Knowledge。
- 不依赖 data_service / voice_service / funasr。
- 不包含真实 token、真实 signed URL、真实外部服务路径。
- 不实现完整前端产品。

## 11. Acceptance

- `EmbedDefinition` 不包含 token/session/eventsourceUrl。
- `EmbedBootstrap` 不泄露 upstream `subscription_token`。
- allowed actions 不包含 forbidden legacy/debug/business/admin methods。
- trace channel 默认关闭。
- event union 与 `EVENT_SCHEMAS` 对齐。
- demo fixture 平台中立。
- TS embed contract 不 import server internals。
