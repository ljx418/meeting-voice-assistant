# V3.5 Browser Event Bridge Plan

文档状态：V3.5-C planning artifact。

## 1. Goal

新增 browser-friendly event bridge，让 Product UI / React hooks / Embed contract 能通过 native EventSource 或 fetch stream 订阅 turn、job、artifact、approval、trace 和 business events。

## 2. Subscription Modes

V3.5-C 必须区分两种浏览器订阅模式，因为原生浏览器 `EventSource` 不能设置 `Authorization` header。

### 2.1 Native EventSource Mode

适用场景：浏览器直接使用 `new EventSource(url)`。

认证方式只能使用：

- same-origin BFF cookie：由业务 BFF 完成用户身份校验，并把 cookie 约束在同源路径下。
- short-lived signed subscription URL：由 `events.subscribe` 返回短期有效的签名 URL。

限制：

- 不依赖 `Authorization: Bearer` header。
- `subscription_token` 必须短期有效。
- `subscription_token` 必须绑定 scope：`app_id/project_id/workspace_id`。
- `subscription_token` 必须绑定 channels，例如 `job/artifact/approval/trace`。
- `subscription_token` 不能扩大原始 capability token 的权限，只能收窄。
- token 或 signed URL 泄漏后的影响面必须小于原始 capability token。

### 2.2 Fetch Stream Mode

适用场景：SDK、BFF、现代浏览器或 Node client 使用 `fetch()` 读取 streaming body。

认证方式：

- `Authorization: Bearer <capability-token>`。
- 可同时使用 `Last-Event-ID` 或 request body/query cursor。

限制：

- fetch stream 可以使用 bearer token，但仍必须校验 scope、channel、origin 和 capability。
- fetch stream 的 event framing 应与 SSE envelope 兼容，方便 SDK 复用 parser。

## 3. Endpoint

目标 endpoint：

```text
GET /v1/events/subscribe
```

Query params：

- `channels`
- `subscription_token`
- `session_id`
- `job_id`
- `artifact_id`
- `approval_id`
- `trace_id`
- `app_id`
- `project_id`
- `workspace_id`
- `cursor`
- `since`

Headers：

- native EventSource mode：
  - `Cookie`，仅限 same-origin BFF cookie 模式。
  - `Last-Event-ID`
  - `Origin`
- fetch stream mode：
  - `Authorization: Bearer <capability-token>`
  - `Last-Event-ID`
  - `Origin`

## 4. EventSource Shape

每条 SSE：

```text
id: <cursor>
event: <event_type>
data: <json event envelope>
```

event envelope：

- `event_id`
- `type`
- `channel`
- `cursor`
- `timestamp`
- `scope`
- `session_id`
- `turn_id`
- `job_id`
- `artifact_id`
- `approval_id`
- `trace_id`
- `data`

## 5. Channels

- `chat`
- `job`
- `artifact`
- `approval`
- `trace`
- `business`

## 6. Replay / Cursor

- `Last-Event-ID` 优先于 query `cursor`。
- cursor 无效返回 `EVENT_CURSOR_INVALID`。
- reconnect 必须能 replay 已持久化事件。
- replay 不能跨 scope 返回事件。

## 7. `events.subscribe` RPC Alias

`events.subscribe` 作为 protocol method 返回适合 native EventSource 和 fetch stream 的订阅信息。SDK 或 BFF 应先调用 `events.subscribe`，再选择连接模式。

Params：

- `channels`
- `mode`: `native_eventsource | fetch_stream`
- `session_id`
- `job_id`
- `artifact_id`
- `approval_id`
- `trace_id`
- `app_id`
- `project_id`
- `workspace_id`
- `cursor`
- `since`
- `last_event_id`

Result：

- `subscription_id`
- `transport`: `eventsource | fetch_stream`
- `eventsource_url`
- `subscription_token`
- `replay_cursor`
- `expires_at`
- `scope`
- `allowed_channels`

`subscription_token` 生成规则：

- 从调用方 capability token 或 same-origin BFF identity 派生。
- 有效期短，默认建议按分钟级配置。
- 只绑定请求的 scope 和 channels。
- 不得包含原始 token 未拥有的 capability。
- 服务端必须在连接时重新校验 token、scope、channel 和 replay cursor。

## 8. REST Compatibility

`/v1/events/subscribe` 是 browser event bridge 的正式 endpoint。历史 `/v1/runs/stream` 如保留，只能作为 simple compatibility path，并且必须支持：

- `app_id/project_id/workspace_id`
- token scope 校验
- channel/cursor/replay 约束

SDK 默认不以 REST run/stream 作为主接口；SDK 默认走 JSON-RPC `events.subscribe` 再连接 event bridge。

## 9. Contract Tests

- native EventSource browser auth test：不使用 Authorization header，通过 same-origin cookie 或 signed URL 连接。
- fetch stream auth test：使用 `Authorization: Bearer` 连接。
- GET EventSource returns `text/event-stream`。
- token 缺失或 scope mismatch 被阻断。
- `Last-Event-ID` 可 replay。
- channels filter 生效。
- approval-required、job progress、artifact registered、trace recorded 可被订阅。
- `subscription_token` 过期、跨 scope、跨 channel、扩大 capability 都必须被拒绝。
