# V3.5 Protocol Schema Registry + Error Registry Plan

文档状态：V3.5-A planning artifact。

## 1. Goal

建立 method/event/error schema registry，让 SDK、BFF、Event Bridge、Embed Contract 有稳定的协议源，而不是从 Python handler 或文档里猜字段。

## 2. Schema Registry As Single Source Of Truth

短期可以手写 schema，但 schema 不能只是文档。每个 default SDK method 必须通过 contract tests 校验三方一致：

- handler 实际参数和返回 shape
- schema registry 中的 params/result/error schema
- Python SDK / TypeScript SDK 暴露的默认方法和类型

中期 method registration 必须绑定 schema：

- 注册 method 时声明 `method_schema_id` 或内联 schema ref。
- handler 缺少 schema 时不能进入 SDK default surface。
- legacy/debug method 即使存在 handler，也默认不可进入 SDK default surface。

SDK 生成或手工实现规则：

- SDK 只能从 schema registry default surface 生成，或手工与该 default surface 对齐。
- SDK 不得从全部 JSON-RPC handler 自动暴露方法。
- SDK/BFF 必须以 schema registry 的 capability、scope、error registry 为准。

## 3. Method Schema Registry

每个 method schema 至少包含：

- `method`
- `capability`
- `stability`: `stable | beta | legacy | debug`
- `sdk_exposure`: `default | optional | forbidden`
- `params_schema`
- `result_schema`
- `errors`
- `scope_required`
- `auth_required`
- `deprecated_by`

首批 default methods：

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

## 4. Event Schema Registry

每个 event schema 至少包含：

- `type`
- `channel`
- `scope`
- `session_id`
- `turn_id`
- `job_id`
- `artifact_id`
- `approval_id`
- `trace_id`
- `timestamp`
- `data_schema`
- `cursor`

首批 channels：

- `chat`
- `job`
- `artifact`
- `approval`
- `trace`
- `business`

## 5. Error Registry

将现有 `_error_code()` 升级为集中 registry 或 wrapper registry。

每个 error entry 至少包含：

- `code`
- `http_status`
- `message_template`
- `retryable`
- `sdk_exception`
- `data_schema`

首批 error codes：

- `INVALID_PARAMS`
- `METHOD_NOT_FOUND`
- `SESSION_NOT_FOUND`
- `ARTIFACT_READ_BLOCKED`
- `AUTH_REQUIRED`
- `AUTH_INVALID`
- `AUTH_FORBIDDEN`
- `CAPABILITY_DENIED`
- `SCOPE_MISMATCH`
- `EVENT_CURSOR_INVALID`
- `SUBSCRIPTION_TOKEN_EXPIRED`
- `SUBSCRIPTION_TOKEN_SCOPE_MISMATCH`
- `SUBSCRIPTION_TOKEN_CHANNEL_DENIED`
- `APPROVAL_NOT_FOUND`
- `APPROVAL_ALREADY_RESOLVED`
- `APPROVAL_CONFLICT`
- `APPROVAL_RETRY_CONSUMED`
- `RUNTIME_ERROR`

## 6. New Protocol Methods

### `approval.respond`

目标：统一 approve/reject，避免 SDK 暴露两个不一致入口。

Params：

- `approval_id`
- `decision`: `approve | reject`
- `reason`
- `scope`

Result：

- `approval`
- `status`
- `trace_id`
- `idempotent`

内部可路由到现有 `approval.approve` / `approval.reject`，但 method registry 必须把 `approval.respond` 作为正式方法暴露。SDK 和 BFF 只能统一调用 `approval.respond`，不得暴露 `approval.approve` / `approval.reject` 双入口作为默认面。

Idempotency / error behavior：

| 场景 | 期望行为 |
| --- | --- |
| repeated same decision | 返回当前 approval 状态，`idempotent=true`，不得重复触发 side effect。 |
| conflicting decision | 返回 `APPROVAL_CONFLICT`，不得覆盖已完成决策。 |
| scope mismatch | 返回 `SCOPE_MISMATCH`，trace 记录被阻断。 |
| approval not found | 返回 `APPROVAL_NOT_FOUND`。 |
| retry consumed | 返回 `APPROVAL_RETRY_CONSUMED`，不得再次执行审批后续动作。 |
| already resolved but same decision | 返回 `APPROVAL_ALREADY_RESOLVED` 或 idempotent success，具体策略必须在 schema 中冻结。 |

### `events.subscribe`

目标：提供 protocol-level subscription contract。实际 transport 可映射到 native EventSource 或 fetch stream。

Params：

- `channels`
- `mode`: `native_eventsource | fetch_stream`
- `session_id`
- `job_id`
- `artifact_id`
- `approval_id`
- `trace_id`
- `since`
- `last_event_id`
- `scope`

Result：

- `subscription_id`
- `transport`
- `eventsource_url`
- `subscription_token`
- `replay_cursor`
- `expires_at`
- `allowed_channels`

`subscription_token` 只服务 native EventSource/signed URL 场景，必须短期有效、scope-limited、channel-limited，并且不能扩大调用方原有 capability。

## 7. REST Scope Support

SDK 默认走 JSON-RPC method surface，不默认使用 REST run path。

如果 `/v1/runs` 与 `/v1/runs/stream` 保留：

- 必须支持 `app_id/project_id/workspace_id`。
- 必须按 capability token scope 校验。
- 必须复用 error registry。
- 必须定位为 simple compatibility path，不作为默认 SDK 面。

## 8. Contract Tests

必须覆盖：

- `method.list` 可发现 schema metadata 或 schema refs。
- default SDK methods 均有 params/result schema。
- forbidden legacy/debug methods 不进入 SDK default surface。
- JSON-RPC `result` 和 `error` 不同时出现。
- known exceptions 映射到 error registry。
- handler/schema/SDK 对 default method 的参数、返回、错误保持一致。
- method registration 缺 schema 时不能进入 default SDK surface。
- `approval.respond` approve/reject 两条路径和幂等行为。
- repeated same decision、conflicting decision、scope mismatch、approval not found、retry consumed 均命中稳定错误或 idempotent success。
- `events.subscribe` schema 与 native EventSource / fetch stream contract。
- `events.subscribe` 返回 `eventsource_url/subscription_token/replay_cursor`。
