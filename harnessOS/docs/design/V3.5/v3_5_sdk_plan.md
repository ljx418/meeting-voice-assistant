# V3.5 SDK Plan

文档状态：V3.5-MVP complete；V3.5-E1 TypeScript SDK Core Client complete；V3.5-E2 React Hooks complete；V3.5-F Full BFF Template complete。

## 1. Goal

提供 Python SDK、TypeScript SDK core client 和 React hooks，让外部业务 App 通过稳定协议调用 harnessOS Core。

SDK 默认走 JSON-RPC method surface。REST `/v1/runs` 与 `/v1/runs/stream` 即使保留，也只作为 simple compatibility path，不作为 SDK 默认面。

Core SDK 必须保持 thin protocol client 边界。默认导出不得包含业务 wrapper，例如 `generateMinutes()`、`ingestDocument()`、`runMeetingWorkflow()`、`generateVideo()`、`analyzePortfolio()`。业务便利层只能存在于 BFF、optional extension、pack-generated client 或业务 App SDK。

V3.5-D 后，Python SDK MVP 已可用于 local/backend integration smoke。V3.5-E1 后，TypeScript SDK core client 已可用于 dev/local protocol integration smoke。SDK runtime 使用内置 protocol snapshot，不 import server internals；tests 负责将 snapshot 与 server schema registry 对齐。当前 MVP E2E 已验证真实 Python SDK 可通过 Minimal BFF 与 harnessOS ASGI/TestClient transport 串起 session、turn、events、approval、artifact、job、pack 和 connector 基础流程。

## 2. Python SDK MVP

实现目录：

```text
sdk/python/harnessos_client/
```

核心对象：

- `HarnessOSClient`
- `HarnessOSAsyncClient`
- `Scope`
- `RpcError`
- `CapabilityToken`
- `EventSubscription`
- `TransportError`
- typed protocol errors

MVP methods：

- `session.start`
- `turn.start`
- `events.subscribe`
- `artifact.list`
- `artifact.read_metadata`
- `artifact.register_external`
- `artifact.lineage`
- `job.get`
- `job.list`
- `approval.respond`
- `connector.health`
- `pack.list`
- `pack.get`

Behavior：

- 所有调用默认携带 scope。
- JSON-RPC `error` 映射为 typed exception。
- JSON-RPC `result` 返回 typed dict / model。
- JSON-RPC 同时包含 `result/error` 或两者都缺失时，client-side 拒绝。
- `harnessos_client` runtime 不 import `GatewayService`、`RuntimeAdapter`、Core Store、`apps.gateway.service` 或 server `METHOD_SCHEMAS`。
- SDK 不提供 token issuance/signing。
- `repr(client)`、`repr(EventSubscription)` 和 exception string 不泄露 capability token 或 subscription token。
- SDK default client 不暴露 `meeting.*` legacy methods。
- SDK default client 不暴露 debug/admin/legacy method。
- SDK default client 不暴露业务 workflow wrapper。
- 审批只暴露 `approval.respond`，不暴露 approve/reject 双入口。
- `events.subscribe` 返回 `eventsource_url/subscription_token/replay_cursor/expires_at/allowed_channels` 后，由 SDK 选择 native EventSource 或 fetch stream；该方法在 V3.5-C 已 runtime-ready。
- `events_subscribe()` 只获取 descriptor，不实现 SSE loop / reconnect。
- Sync client 是 MVP 主验证路径。
- `HarnessOSAsyncClient` 已有基础 smoke 覆盖：`session_start`、`events_subscribe` 和 error mapping；它不是完整生产级 async SDK。

V3.5-D 完成后只能声明：

```text
Python SDK MVP usable for local/backend integration smoke
```

不能声明：

```text
SDK production-ready
external app ready
V3.5-MVP complete
```

## 3. V3.5-E1 TypeScript SDK Core Client

实现目录：

```text
sdk/typescript/
```

核心对象：

- `HarnessOSClient`
- `Scope`
- `RpcError`
- `EventSubscription`
- request/result types
- transport types

Transport：

- HTTP JSON-RPC
- native EventSource mode：使用 `eventsource_url/subscription_token`，不依赖 Authorization header。
- fetch stream mode：可使用 `Authorization: Bearer`。

Constraints：

- E1 只能依赖 Protocol Schema Registry、Capability Token 和 Event Bridge 已冻结的合同。
- E1 runtime 使用 `protocolSnapshot.ts`；测试再与 server schema registry 对齐。
- `sdk/typescript/src` 不 import `apps/*`、`core/*`、GatewayService、RuntimeAdapter 或 server `METHOD_SCHEMAS`。
- E1 default surface 只来自 schema registry default methods。
- E1 不暴露 legacy/debug API。
- E1 不暴露业务 workflow wrapper。
- E1 审批只调用 `approval.respond`。
- E1 不提供 `issueToken` / `signToken`。
- Direct browser mode 只用于 dev/direct 或受限 token 场景；production recommended mode 仍是 `Business UI -> BFF -> harnessOS`。
- Browser 支持 native EventSource URL helper；Node 默认只保证 JSON-RPC fetch，Node EventSource implementation 由用户提供或留给后续。

V3.5-E1 完成后只能声明：

```text
TypeScript SDK core client ready for dev/local protocol integration smoke
```

不能声明：

```text
React hooks ready
external app ready
production-ready browser integration
V3.5 complete
```

## 4. V3.5-E2 React Hooks

React hooks 不得先于 EventBridge 和 TS SDK core client 实现。E2 的职责是把 E1 client 包装成前端状态模型，不重新定义协议、不实现 event bus、不实现 AgentTalkWindow state manager、不实现 workflow state machine。

Package boundary：

- React hooks 通过 `@harnessos/client/react` / `sdk/typescript/src/react` 暴露。
- Core TS SDK import 不强制依赖 React。
- React 是 peer dependency。
- Hooks 只依赖 E1 TS SDK public API，不 import `apps/*`、`core/*`、GatewayService、RuntimeAdapter 或 server schema registry。

Hooks：

- `useHarnessSession`
- `useTurn`
- `useEvents`
- `useArtifacts`
- `useJobs`
- `useApprovals`

Hook states：

- session/turn/artifacts/jobs/approvals：`idle`、`loading`、`success`、`error`
- events：`idle`、`loading`、`streaming`、`reconnecting`、`error`

Behavior：

- `useHarnessSession` 默认不 auto-start，只提供 `startSession()`。
- `useTurn` 默认不 auto-start，只提供 `startTurn()`。
- `useEvents` 默认不自动打开 EventSource，除非 `enabled=true` 或显式调用 `connect()`。
- `useEvents` 支持 basic reconnect、lastEventId/replay cursor、dedupe、close on unmount。
- React StrictMode 下不得创建重复 live EventSource。
- Native EventSource mode 不设置 Authorization header；fetch stream bearer mode 只能显式配置。
- `useApprovals` 只调用 `approval.respond`，不暴露 `approval.approve` / `approval.reject`，不默认调用 `approval.list`。
- `useArtifacts` 使用 `artifact.list/read_metadata/lineage`，不默认调用 `artifact.read` inline。
- `useJobs` 使用 `job.list/get`，不默认轮询。
- hook state 不保存 raw capability token，不暴露 subscription token；signed eventsource URL query 不进入 JSON/debug output。

Dependencies：

- V3.5-C Event Bridge 完成 native EventSource / fetch stream contract。
- V3.5-E1 TypeScript SDK core client 完成。

## 5. Tests

Python：

- no server internals import
- public `__all__` surface
- schema snapshot alignment
- low-level `rpc()` forbidden checks
- scope passthrough
- scope conflict local rejection
- token/subscription redaction
- result/error mapping
- transport error mapping
- blocked artifact read mapping
- `approval.respond`
- `approval.respond` idempotency
- forbidden legacy methods not present
- forbidden business wrapper exports not present

TypeScript core：

- type tests
- default surface legacy/debug exclusion
- default export business wrapper exclusion
- `events.subscribe` native EventSource result mapping
- fetch stream authorization mapping
- `approval.respond` idempotency error mapping

React hooks：

- no server internals import
- public React export surface
- no business hooks
- no-auto-start session/turn/events
- event reconnect behavior
- EventSource close on unmount
- StrictMode no duplicate live EventSource
- dedupe
- only `approval.respond`
- no inline artifact read
- no default job polling
- token/subscription redaction
- loading/error lifecycle
- no business legacy dependency
