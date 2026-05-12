# V3.5 Browser Event Bridge Plan

文档状态：V3.5-C implementation baseline；MVP/E2/F smoke verified。

当前阶段基线：V3.5-MVP complete；V3.5-E1 complete；V3.5-E2 complete；V3.5-F complete。

## 1. Goal

新增 browser-friendly event bridge，让 Product UI / React hooks / Embed contract 能通过 native EventSource 或 fetch stream 订阅 turn、job、artifact、approval、trace 和 reserved business events。

V3.5-C 已实现 `events.subscribe` runtime handler、`GET /v1/events/subscribe`、short-lived subscription token、opaque replay cursor 和本地 SSE transport，并通过 MVP E2E 验证 BFF EventSource proxy 可消费该 endpoint。

V3.5-F Full BFF Template 必须通过 `GET /bff/events/subscribe` 代理 EventSource。`/bff/rpc` 默认拒绝 `events.subscribe`，避免把 upstream `eventsource_url` / `subscription_token` 暴露给浏览器。

边界：

- V3.5-C 不实现完整 event bus。
- V3.5-C 支持 persisted event replay + local follow mode。
- V3.5-C 不保证多 worker / 分布式实时事件一致性。
- V3.5-C 完成后只能声明 `browser event bridge contract and local runtime ready`。

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

已实现 endpoint：

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
- `follow`
- `heartbeat_interval`

Headers：

- native EventSource mode：
  - `Cookie`，仅限 same-origin BFF cookie 模式。
  - `Last-Event-ID`
  - `Origin`
  - 不支持也不要求 `Authorization` header。
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

| Channel | Capability | Source | 说明 |
| --- | --- | --- | --- |
| `chat` | `events` + `turns` | session events | `turn.started`、`item.delta`、`turn.completed`、`turn.failed` |
| `job` | `events` + `jobs` | job events | `job.queued/running/completed/failed/cancelled` |
| `artifact` | `events` + `artifacts` | artifact records first, trace fills blocked read | canonical event 为 `artifact.registered`；`artifact.read_blocked` 来自 blocked read trace；`artifact.created` 只作为 alias |
| `approval` | `events` + `approvals` | approval records first | `approval.required/approved/rejected` |
| `trace` | `events` + `traces.read` | trace records | 默认 AppProfile 不开放，需要显式 token capability |
| `business` | reserved | none in V3.5-C | 只保留 namespace，不新增 Meeting/Knowledge 业务事件 |

## 6. Replay / Cursor

- `Last-Event-ID` 优先于 query `cursor`。
- cursor 为 opaque cursor，不能依赖内部结构。
- cursor 绑定 `app_id/project_id/workspace_id`。
- cursor 无效返回 `EVENT_CURSOR_INVALID`。
- cursor scope mismatch 返回 `SCOPE_MISMATCH`。
- reconnect 必须能 replay 已持久化事件。
- replay 不能跨 scope 返回事件。
- replay order 必须稳定。

## 7. Dedupe / Follow / Heartbeat

- dedupe key 为 `channel + event_id`，避免 artifact / approval / job 重复事件。
- local follow mode 通过 `follow=1` 打开；该模式只保证当前进程内连接保持，不提供分布式实时一致性。
- SSE heartbeat 使用 comment frame，例如 `: heartbeat`。
- heartbeat 不写入 persisted event records。

## 8. `events.subscribe` RPC Alias

`events.subscribe` 作为 protocol method 返回适合 native EventSource 和 fetch stream 的订阅信息。SDK 或 BFF 应先调用 `events.subscribe`，再选择连接模式。

V3.5-C 状态：

- 已进入 schema registry。
- `runtime_handler=true`。
- 默认 callable `method.list` 返回该方法。
- `/v1/events/subscribe` 是 transport endpoint，不是 RPC method。
- subscription token 只能由 `events.subscribe` 基于主 capability token 派生，不提供匿名外部签发。

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
- `transport`: `eventsource`
- `eventsource_url`
- `subscription_token`
- `replay_cursor`
- `expires_at`
- `allowed_channels`

`subscription_token` 生成规则：

- 从调用方 capability token 派生；same-origin BFF cookie 模式由 BFF 先完成业务身份校验后再换取订阅。
- 有效期短，默认建议按分钟级配置。
- 只绑定请求的 scope 和 channels。
- 不得包含原始 token 未拥有的 capability。
- 服务端必须在连接时重新校验 token、scope、channel 和 replay cursor。
- subscription token 和 signed URL 必须按 secret hygiene 规则 redact。

## 9. REST Compatibility

`/v1/events/subscribe` 是 browser event bridge 的正式 endpoint。历史 `/v1/runs/stream` 如保留，只能作为 simple compatibility path，并且必须支持：

- `app_id/project_id/workspace_id`
- token scope 校验
- channel/cursor/replay 约束

SDK 默认不以 REST run/stream 作为主接口；SDK 默认走 JSON-RPC `events.subscribe` 再连接 event bridge。

## 10. Contract Tests

- native EventSource browser auth test：不使用 Authorization header，通过 signed URL 连接。
- fetch stream auth test：使用 `Authorization: Bearer` 连接。
- GET EventSource returns `text/event-stream`。
- token 缺失、tamper、expired 或 scope mismatch 被阻断。
- `Last-Event-ID` 可 replay。
- channels filter 生效。
- approval、job、artifact、trace persisted records 可被订阅。
- job.running / job.completed、approval.required / approval.approved、trace.recorded、artifact.read_blocked 输出符合 `EVENT_SCHEMAS`。
- `subscription_token` 过期、跨 scope、跨 channel、扩大 capability 都必须被拒绝。
- heartbeat comment frame 不进入 persisted event records。
- `/v1/runs/stream` 继续作为 compatibility path，鉴权失败不得打开 stream。
