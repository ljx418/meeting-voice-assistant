# V3.5 Application Adaptation Layer Development Plan

文档状态：V3.5 development plan。  
执行范围：本计划用于后续代码实施；当前文档阶段不创建 SDK/API 代码目录、不修改 Core、不重复验证历史 reference paths。

## 1. Goal

V3.5 的目标是在 Product UI / external business app 与 harnessOS Protocol App Server / Core 之间建立 Application Adaptation Layer，让外部业务 App 能低成本、安全、可治理地调用 harnessOS Core。

V3.5 早期以 dev/local-first 启动。正式外部 App 接入前必须补齐：

- protocol schema registry / error registry
- local capability token
- browser-friendly EventSource
- `approval.respond`
- REST scope support

## 2. Scope

包含：

- `sdk/`、`templates/`、`examples/`、`docs/integration/` 的规划和后续实现。
- Protocol schema registry、event schema、error registry。
- Auth / capability token MVP。
- Browser Event Bridge。
- Python SDK MVP。
- TypeScript SDK core client。
- React hooks。
- App Gateway / BFF template。
- Pack / Connector template。
- Embed contract / AgentTalkWindow 前置。
- Reference app example。

不包含：

- Core 重构。
- 重新实现业务 reference paths。
- 完整 Workflow Studio。
- 完整 AgentTalkWindow。
- data_service 或 meeting-voice-assistant 开发。

## 3. Impacted Files And Future Directories

文档阶段新增或更新：

- `docs/design/V3.5/v3_5_contract_inventory.md`
- `docs/design/V3.5/v3_5_protocol_schema_registry_plan.md`
- `docs/design/V3.5/v3_5_auth_capability_token_plan.md`
- `docs/design/V3.5/v3_5_event_bridge_plan.md`
- `docs/design/V3.5/v3_5_sdk_plan.md`
- `docs/design/V3.5/v3_5_bff_template_plan.md`
- `docs/design/V3.5/v3_5_pack_connector_template_plan.md`
- `docs/design/V3.5/v3_5_embed_contract_plan.md`
- `docs/design/V3.5/v3_5_reference_app_plan.md`
- `docs/design/V3.5/v3_5_acceptance_plan.md`

后续代码实施会涉及：

- `apps/gateway/rpc_router.py`
- `apps/gateway/service.py`
- `apps/gateway/protocol.py`
- `apps/api/routers/runs.py`
- `apps/api/__init__.py`
- `core/apps/profiles.py`
- `core/protocol/`
- `sdk/python/harnessos_client/`
- `sdk/typescript/`
- `templates/bff/`
- `templates/pack/`
- `templates/connector/`
- `examples/reference_app/`
- `docs/integration/`

## 4. Phase Plan And PR Slices

### V3.5-0 Scaffolding & Contract Inventory

PR slices：

- `V3.5-0-PR1`：新增顶层目录规划文档，声明 `sdk/`、`templates/`、`examples/`、`docs/integration/` 的目标结构。
- `V3.5-0-PR2`：梳理 method inventory，区分 SDK default、SDK optional、legacy/debug forbidden。
- `V3.5-0-PR3`：梳理 event inventory 和 error inventory。
- `V3.5-0-PR4`：记录当前默认回归作为 V3.5 启动回归基线。

验收：

- 文档明确 SDK 默认面不包含 `meeting.*` legacy RPC 和 debug-only API。
- 文档明确当前缺失 `events.subscribe`、`approval.respond`、native EventSource auth、fetch stream auth、local capability token、REST scope support。

### V3.5-A Protocol Schema Registry + Error Registry

PR slices：

- `V3.5-A-PR1`：设计 method schema registry，覆盖 method name、capability、params schema、result schema、stability、sdk_exposure。
- `V3.5-A-PR2`：设计 event schema registry，覆盖 chat/job/artifact/approval/trace/business events。
- `V3.5-A-PR3`：设计 error registry，替代或包装 `_error_code()`。
- `V3.5-A-PR4`：定义 `approval.respond` 和 `events.subscribe` schema。
- `V3.5-A-PR5`：定义 JSON-RPC result/error 互斥 contract tests。
- `V3.5-A-PR6`：定义 handler/schema/SDK 一致性 contract tests。

验收：

- `method.list` 后续可返回 schema metadata 或可关联 schema registry。
- 短期 schema 可手写，但必须通过 handler/schema/SDK 一致性测试。
- 中期 method registration 必须绑定 schema，缺 schema 的 handler 不进入 SDK default surface。
- `approval.respond` 是 protocol-level method，不只是 SDK 侧 helper。
- `approval.respond` 冻结 repeated same decision、conflicting decision、scope mismatch、approval not found、retry consumed 行为。
- `events.subscribe` 是 protocol-level subscription method，即使具体 transport 走 native EventSource 或 fetch stream。
- SDK 只能从 schema registry default surface 生成或手工对齐。

### V3.5-B Auth / Capability Token MVP

PR slices：

- `V3.5-B-PR1`：定义 local capability token envelope。
- `V3.5-B-PR2`：定义 token 与 `app_id/project_id/workspace_id/capabilities/origin` 的绑定规则。
- `V3.5-B-PR3`：扩展 AppProfile 文档字段：`allowed_origins`、`default_capabilities`、`embed_policy`。
- `V3.5-B-PR4`：定义 dev mode 显式开启规则。
- `V3.5-B-PR5`：定义 CORS 与 token scope 联动规则。

验收：

- 无 token 的外部接入只能在显式 dev mode 下工作。
- token scope 与 request scope 不一致时必须 blocked。
- capability 不足时必须返回稳定 authorization error。

### V3.5-C Browser Event Bridge

PR slices：

- `V3.5-C-PR1`：定义 `GET /v1/events/subscribe`。
- `V3.5-C-PR2`：定义 turn/job/artifact/approval/trace event channel。
- `V3.5-C-PR3`：定义 scope 校验和 token 校验。
- `V3.5-C-PR4`：定义 `Last-Event-ID` 或 replay cursor。
- `V3.5-C-PR5`：定义 `events.subscribe` RPC alias 与 EventSource transport 的关系。
- `V3.5-C-PR6`：定义 native EventSource mode：same-origin BFF cookie 或 short-lived signed subscription URL。
- `V3.5-C-PR7`：定义 fetch stream mode：允许 `Authorization: Bearer`。

验收：

- 浏览器可用原生 `EventSource` GET 订阅事件，且不依赖 Authorization header。
- `events.subscribe` 返回 `eventsource_url/subscription_token/replay_cursor`。
- `subscription_token` 短期有效、scope-limited、channel-limited，不能扩大 capability。
- 事件可按 scope 过滤。
- reconnect 可通过 cursor replay。
- approval-required、job progress、artifact registered、trace event 可被 UI 处理。

### V3.5-D Python SDK MVP

PR slices：

- `V3.5-D-PR1`：定义 `sdk/python/harnessos_client` package layout。
- `V3.5-D-PR2`：定义 transport client、scope helper、result/error models。
- `V3.5-D-PR3`：定义 session/turn/events/artifact/job/approval/connector/pack client methods。
- `V3.5-D-PR4`：定义 SDK contract tests。
- `V3.5-D-PR5`：定义 legacy/debug exclusion tests。

验收：

- SDK 支持用户指定 MVP 方法。
- SDK 默认所有调用透传 scope。
- SDK 将 JSON-RPC error 映射为 typed exception/result。
- SDK 默认不暴露 `meeting.*` 业务 legacy 方法。
- SDK 默认走 JSON-RPC；REST run/stream 只作为 simple compatibility path。
- SDK 只暴露 `approval.respond`，不暴露 approve/reject 双入口。

### V3.5-E1 TypeScript SDK Core Client

PR slices：

- `V3.5-E1-PR1`：定义 `sdk/typescript` package layout。
- `V3.5-E1-PR2`：定义 TS client types 和 generated/manual schema strategy。
- `V3.5-E1-PR3`：定义 JSON-RPC client、scope helper、error mapping。
- `V3.5-E1-PR4`：定义 native EventSource helper 和 fetch stream helper。
- `V3.5-E1-PR5`：定义 type tests 和 SDK default surface exclusion tests。

验收：

- TS SDK core client 不依赖业务 legacy 方法。
- TS SDK default surface 只来自 schema registry。
- TS SDK 支持 `events.subscribe` 返回的 native EventSource 和 fetch stream 模式。
- TS SDK 只暴露 `approval.respond`。

### V3.5-E2 React Hooks

React hooks 不得先于 EventBridge 和 TS SDK core client 实现。

PR slices：

- `V3.5-E2-PR1`：定义 hooks package layout。
- `V3.5-E2-PR2`：定义 hooks：`useHarnessSession`、`useTurn`、`useEvents`、`useArtifacts`、`useJobs`、`useApprovals`。
- `V3.5-E2-PR3`：定义最小 browser demo。
- `V3.5-E2-PR4`：定义 hook lifecycle tests。

验收：

- hooks 不依赖业务 legacy 方法。
- hooks 支持 loading/error/data/reconnect。
- event hook 基于 V3.5-E1 TS SDK core client，不重新定义协议。

### V3.5-F App Gateway / BFF Template

PR slices：

- `V3.5-F-PR1`：定义 `templates/bff/fastapi` structure。
- `V3.5-F-PR2`：定义 optional Node template。
- `V3.5-F-PR3`：定义 RPC proxy、EventSource proxy、approval respond。
- `V3.5-F-PR4`：定义 CORS、token validation、scope binding。
- `V3.5-F-PR5`：定义 legacy/debug proxy denylist。
- `V3.5-F-PR6`：定义业务 identity 到 harnessOS scope/capability token 的绑定样例。

验收：

- BFF template 不实现完整用户系统。
- BFF 不代理 forbidden legacy/debug APIs。
- BFF 所有请求绑定 scope。
- EventSource proxy 保留 event id 和 cursor。
- native EventSource 可通过 same-origin BFF cookie 或 signed URL 认证。

### V3.5-G Pack / Connector Template

PR slices：

- `V3.5-G-PR1`：定义 `templates/pack` structure。
- `V3.5-G-PR2`：定义 `templates/connector` structure。
- `V3.5-G-PR3`：定义 dummy pack manifest 和 dummy connector descriptor。
- `V3.5-G-PR4`：定义 template acceptance tests。
- `V3.5-G-PR5`：定义 no-Core-change verification。
- `V3.5-G-PR6`：定义 `manifest_schema_version/min_harnessos_version/target_harnessos_version/compatibility_warnings`。

验收：

- dummy pack 不改 Core 可被 `pack.list/pack.get` 发现。
- dummy connector 不改业务 Gateway 可被 `connector.health` 消费。
- connector template 包含 trust level、execution mode、allowed paths/commands/network policy。
- PackAssemblyResult 暴露 compatibility warnings。

### V3.5-H Embed Contract / AgentTalkWindow 前置

PR slices：

- `V3.5-H-PR1`：定义 `EmbedDefinition`。
- `V3.5-H-PR2`：定义 chat/job/artifact/approval/trace/business event union。
- `V3.5-H-PR3`：定义 embed bootstrap、scope、token、session handoff。
- `V3.5-H-PR4`：定义最小 demo contract。

验收：

- 未来 AgentTalkWindow 只依赖 contract，不依赖 Gateway 内部对象。
- blocked、approval-required、failed、fallback、completed 状态可被 UI 区分。

### V3.5-I Reference App Example

PR slices：

- `V3.5-I-PR1`：定义 `examples/reference_app` structure。
- `V3.5-I-PR2`：定义 SDK + BFF + hooks flow。
- `V3.5-I-PR3`：定义 session、turn、events、artifacts、jobs、approvals、traces views。
- `V3.5-I-PR4`：定义 approval.respond flow。
- `V3.5-I-PR5`：定义 scope isolation E2E。

验收：

- reference app 不使用业务特权路径。
- reference app 不依赖 Meeting/Knowledge pack 或 legacy RPC。
- reference app 使用 dummy pack / dummy connector 或 generic workflow。
- reference app 可证明外部业务不改 Core 接入。

## 5. Ordering Recommendation

先做 Protocol Schema Registry，再做 Auth / Capability Token。

原因：

- SDK、BFF、Event bridge、Embed contract 都依赖稳定 method/event/error schema。
- token capability 应绑定 method/capability registry；没有 registry 会导致权限模型散落。
- EventSource 和 BFF 必须从一开始带 token/scope，但 token 的 capability 名称应从 schema registry 派生。

最终推荐顺序：

```text
V3.5-0
  -> V3.5-A
  -> V3.5-B
  -> V3.5-C
  -> V3.5-D
  -> V3.5-E1
  -> V3.5-E2
  -> V3.5-F
  -> V3.5-G / V3.5-H
  -> V3.5-I
```

## 6. Exit Standard

V3.5 出门标准：

- 至少一个平台中立 reference app 能不改 Core 接入。
- SDK/BFF/hooks/event bridge 均通过 contract tests。
- Auth/capability token 明确区分 dev-only 和 local production mode。
- Pack/Connector template 可生成可被 registry 发现的最小样例。
- Embed contract 能支撑 AgentTalkWindow 前置集成。
- 当前平台回归保持绿灯。
