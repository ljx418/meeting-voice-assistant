# V3.5 SDK Plan

文档状态：V3.5-D/E1/E2 planning artifact。

## 1. Goal

提供 Python SDK、TypeScript SDK core client 和 React hooks，让外部业务 App 通过稳定协议调用 harnessOS Core。

SDK 默认走 JSON-RPC method surface。REST `/v1/runs` 与 `/v1/runs/stream` 即使保留，也只作为 simple compatibility path，不作为 SDK 默认面。

## 2. Python SDK MVP

目标目录：

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
- SDK default client 不暴露 `meeting.*` legacy methods。
- SDK default client 不暴露 debug/admin/legacy method。
- 审批只暴露 `approval.respond`，不暴露 approve/reject 双入口。
- `events.subscribe` 返回 `eventsource_url/subscription_token/replay_cursor` 后，由 SDK 选择 native EventSource 或 fetch stream。

## 3. V3.5-E1 TypeScript SDK Core Client

目标目录：

```text
sdk/typescript/
```

核心对象：

- `HarnessOSClient`
- `Scope`
- `RpcError`
- `EventSubscription`
- request/result types

Transport：

- HTTP JSON-RPC
- native EventSource mode：使用 `eventsource_url/subscription_token`，不依赖 Authorization header。
- fetch stream mode：可使用 `Authorization: Bearer`。

Constraints：

- E1 只能依赖 Protocol Schema Registry、Capability Token 和 Event Bridge 已冻结的合同。
- E1 default surface 只来自 schema registry default methods。
- E1 不暴露 legacy/debug API。
- E1 审批只调用 `approval.respond`。

## 4. V3.5-E2 React Hooks

React hooks 不得先于 EventBridge 和 TS SDK core client 实现。E2 的职责是把 E1 client 包装成前端状态模型，不重新定义协议。

Hooks：

- `useHarnessSession`
- `useTurn`
- `useEvents`
- `useArtifacts`
- `useJobs`
- `useApprovals`

Hook states：

- `idle`
- `loading`
- `streaming`
- `success`
- `error`
- `reconnecting`

Dependencies：

- V3.5-C Event Bridge 完成 native EventSource / fetch stream contract。
- V3.5-E1 TypeScript SDK core client 完成。

## 5. Tests

Python：

- scope passthrough
- result/error mapping
- blocked artifact read mapping
- `approval.respond`
- `approval.respond` idempotency
- forbidden legacy methods not present

TypeScript core：

- type tests
- default surface legacy/debug exclusion
- `events.subscribe` native EventSource result mapping
- fetch stream authorization mapping
- `approval.respond` idempotency error mapping

React hooks：

- event reconnect behavior
- loading/error lifecycle
- no business legacy dependency
