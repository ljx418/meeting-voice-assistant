# V3.5 Application Adaptation Layer Development Plan

文档状态：V3.5-MVP complete；V3.5-E1 complete；V3.5-E2 complete；V3.5-F Full BFF Template complete；V3.5-G complete；V3.5-H Embed Contract complete；V3.5-I Reference App complete。V3.5 complete at dev/local Application Adaptation Layer level。
执行范围：本计划用于后续代码实施；Phase0 只创建 scaffold、机器可读 contract inventory 和验证基线，不修改 Core runtime behavior，不重复验证历史 reference paths。

## 1. Goal

V3.5 的目标是在 Product UI / external business app 与 harnessOS Protocol App Server / Core 之间建立 Application Adaptation Layer，让外部业务 App 能低成本、安全、可治理地调用 harnessOS Core。

V3.5 早期以 dev/local-first 启动。正式外部 App 接入前必须补齐：

- protocol schema registry / error registry
- local capability token
- browser-friendly EventSource
- `approval.respond`
- REST scope support

V3.5 按 MVP -> Full 两段推进。MVP 当前可声明 `dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke`；Full 当前已完成 reference app，因此可以声明 `V3.5 complete at dev/local Application Adaptation Layer level`。

## 2. Scope

包含：

- `sdk/`、`templates/`、`examples/`、`docs/integration/` 的规划和后续实现。
- Protocol schema registry、event schema、error registry。
- Auth / capability token MVP。
- Browser Event Bridge。
- Python SDK MVP。
- Minimal BFF Smoke。
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

文档与 Phase0 新增或更新：

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
- `core/protocol/contracts/method_inventory.py`
- `core/protocol/contracts/event_inventory.py`
- `core/protocol/contracts/error_inventory.py`
- `tests/test_v3_5_contract_inventory.py`
- `tests/test_v3_5_scaffolding.py`
- `docs/integration/v3_5_phase0_baseline.md`

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

- `V3.5-0-PR1`：新增 `sdk/`、`templates/`、`examples/reference_app/`、`docs/integration/` scaffold；Phase0 只允许 README/.gitkeep 和基线文档，不创建可用 SDK API。
- `V3.5-0-PR2`：新增 `core/protocol/contracts/method_inventory.py`，区分 SDK default、SDK optional、legacy/debug/business forbidden。
- `V3.5-0-PR3`：新增 `event_inventory.py` 和 `error_inventory.py`，冻结 canonical events、aliases 和 planned errors。
- `V3.5-0-PR4`：新增 Phase0 contract/scaffold tests，记录当前验证基线。

验收：

- `core/protocol/contracts/` 文件头声明 non-runtime contract metadata only；不注册 handler，不改变行为。
- method entries 固定 `method/surface/status/capability/stability/planned_phase/handler_ref/forbidden_reason` 字段。
- Phase0 时 `events.subscribe` 与 `approval.respond` 为 default surface；V3.5-A 后 `approval.respond` 变为 implemented；V3.5-C 后 `events.subscribe` 变为 implemented。
- forbidden methods 必须有 `forbidden_reason`，legacy/debug/business wrapper 不进入 SDK default surface。
- event entries 固定 `type/channel/status/replayable/aliases`；`artifact.registered` 为 canonical，`artifact.created` 只作为 alias。
- error entries 固定 `code/status/category/retryable/planned_phase`；planned errors 必须有 planned_phase。
- `docs/design/V3.5/v3_5_contract_inventory.md` 作为人类可读摘要，机器可读 inventory 是 source of truth。
- `docs/integration/v3_5_phase0_baseline.md` 记录 baseline commit/date/python/env/test/drawio/external E2E exclusion。
- Phase0 完成后只能声明 `V3.5 implementation ready`，不能声明 SDK usable、external app ready 或 V3.5 complete。

### V3.5-A Protocol Schema Registry + Error Registry

PR slices：

- `V3.5-A-PR1`：新增 `core/protocol/schemas/methods.py`，覆盖 method name、capability、params schema、result schema、stability、sdk_exposure、runtime_handler。
- `V3.5-A-PR2`：新增 `events.py`，覆盖 chat/job/artifact/approval/trace/business event envelope。
- `V3.5-A-PR3`：新增 `errors.py` 和 `ProtocolError`，包装 `_error_code()`。
- `V3.5-A-PR4`：实现唯一新增 runtime method `approval.respond`；`events.subscribe` 仅保留 schema。
- `V3.5-A-PR5`：增加 JSON-RPC result/error 互斥 contract tests。
- `V3.5-A-PR6`：增加 contracts/schema 一致性和 method.list 行为 tests。

验收：

- `method.list` 默认只列 callable runtime methods，并为有 schema 的 method 返回 schema metadata。
- `method.list(include_planned=true)` 可返回 planned schema，例如 `events.subscribe`。
- 短期 schema 可手写，但必须通过 handler/schema/SDK 一致性测试。
- 中期 method registration 必须绑定 schema，缺 schema 的 handler 不进入 SDK default surface。
- `approval.respond` 是 protocol-level runtime method，不只是 SDK 侧 helper。
- `approval.respond` 冻结 repeated same decision、conflicting decision、scope mismatch、approval not found、invalid decision 行为。
- `events.subscribe` 是 protocol-level subscription schema，V3.5-A 不实现 runtime handler。
- SDK 只能从 schema registry default surface 生成或手工对齐。
- V3.5-A 完成后只能声明 `protocol schema and approval response contract ready`，不能声明 MVP ready、SDK usable、external app ready 或 `events.subscribe` runtime ready。

### V3.5-B Auth / Capability Token MVP

PR slices：

- `V3.5-B-PR1`：实现 local HMAC capability token；签发仅限 CLI/local admin/internal test helper，不开放 public HTTP issuance。
- `V3.5-B-PR2`：实现 AppProfile 权限上界，token origins/capabilities 必须是 profile 子集。
- `V3.5-B-PR3`：实现 method capability resolver，映射来自 inventory/schema/registry；`connector.health` 使用 `connectors.read`，`pack.list/get` 使用 `packs.read`。
- `V3.5-B-PR4`：实现 external transport guard，保护 `/v1/rpc`、`/v1/runs`、`/v1/runs/stream`、`/v1/sessions*`。
- `V3.5-B-PR5`：保护 legacy/debug HTTP routes，例如 `/api/agents`、`/api/routing`。
- `V3.5-B-PR6`：实现 scope normalization、dev mode、stream pre-auth rejection 和 token redaction tests。

验收：

- 无 token 的外部接入只能在显式 dev mode 下工作。
- token scope 与 request scope 不一致时必须 blocked；top-level scope 与 nested scope 冲突返回 `SCOPE_MISMATCH`。
- capability 不足时必须返回稳定 authorization error。
- `method.list(include_forbidden=true)` 只能由 admin/debug/internal capability 使用。
- Authorization header 和 token 字符串不得进入 trace、error、job、approval、artifact metadata。
- V3.5-B 完成后只能声明 `local capability token and external auth contract ready`。

### V3.5-C Browser Event Bridge

PR slices：

- `V3.5-C-PR1`：实现 `GET /v1/events/subscribe`，返回 `text/event-stream`。
- `V3.5-C-PR2`：实现 chat/job/artifact/approval/trace channel 的 persisted replay，本阶段不实现完整 event bus。
- `V3.5-C-PR3`：实现 scope、capability、subscription token 和 channel 校验。
- `V3.5-C-PR4`：实现 opaque replay cursor，并确保 `Last-Event-ID` 优先于 query cursor。
- `V3.5-C-PR5`：将 `events.subscribe` 从 schema-only 改为 runtime method，返回 signed `eventsource_url`。
- `V3.5-C-PR6`：实现 native EventSource mode：short-lived signed subscription URL，不依赖 Authorization header。
- `V3.5-C-PR7`：实现 fetch stream mode：允许 `Authorization: Bearer`。
- `V3.5-C-PR8`：实现 heartbeat、dedupe 和 `/v1/runs/stream` pre-auth compatibility 回归。

验收：

- 浏览器可用原生 `EventSource` GET 订阅事件，且不依赖 Authorization header。
- `events.subscribe` 返回 `eventsource_url/subscription_token/replay_cursor/expires_at/allowed_channels`。
- `subscription_token` 短期有效、scope-limited、channel-limited，不能扩大 capability。
- 事件可按 scope 过滤。
- reconnect 可通过 cursor replay。
- approval-required、job progress、artifact registered、trace event 可被 UI 处理。
- V3.5-C 完成后只能声明 `browser event bridge contract and local runtime ready`，不能声明 MVP complete、SDK usable 或 external app ready。

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
- SDK default export 不得包含 `generateMinutes()`、`ingestDocument()`、`runMeetingWorkflow()`、`generateVideo()`、`analyzePortfolio()` 等业务 wrapper。

### V3.5-D2 Minimal BFF Smoke

这是 MVP 内的最小 BFF smoke，不等同于 V3.5-F Full BFF Template。

PR slices：

- `V3.5-D2-PR1`：定义 `templates/bff/fastapi_minimal` structure。
- `V3.5-D2-PR2`：定义 Python SDK proxy smoke：session/turn。
- `V3.5-D2-PR3`：定义 EventSource proxy smoke。
- `V3.5-D2-PR4`：定义 approval.respond proxy smoke。
- `V3.5-D2-PR5`：定义 legacy/debug/admin/business wrapper denylist smoke。
- `V3.5-D2-PR6`：新增 MVP E2E smoke，使用真实 Minimal BFF、真实 Python SDK 和 harnessOS ASGI/TestClient transport。

验收：

- Minimal BFF 可启动并通过 Python SDK 调用 harnessOS。
- Minimal BFF 可代理 JSON-RPC 和 EventSource。
- Minimal BFF 不实现完整用户系统，只示范业务 identity 到 harnessOS scope/capability token 的绑定。
- Minimal BFF 不代理 legacy/debug/admin/business wrapper。
- MVP E2E 覆盖 BFF session/turn、SDK `events.subscribe`、BFF EventSource proxy、`approval.respond`、artifact/job/pack/connector 基础查询、denylist、scope isolation 和 redaction。

### V3.5-E1 TypeScript SDK Core Client

当前状态：已完成。

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

当前状态：已完成。

PR slices：

- `V3.5-E2-PR1`：定义 React package boundary，通过 `@harnessos/client/react` / `sdk/typescript/src/react` 暴露；core TS SDK import 不强制依赖 React，React 作为 peer dependency。
- `V3.5-E2-PR2`：定义 hooks：`useHarnessSession`、`useTurn`、`useEvents`、`useArtifacts`、`useJobs`、`useApprovals`。
- `V3.5-E2-PR3`：定义 hook side-effect policy：session/turn/events 默认不在 mount 时自动启动，`useEvents` 仅在 `enabled=true` 或显式 `connect()` 时打开 stream。
- `V3.5-E2-PR4`：定义 EventSource lifecycle：native mode 不设置 Authorization header，支持 reconnect、cursor、dedupe、close on unmount，React StrictMode 下不创建重复 live EventSource。
- `V3.5-E2-PR5`：定义 hook lifecycle、boundary 和 redaction tests。

验收：

- hooks 不依赖业务 legacy 方法。
- hooks 只依赖 E1 TS SDK public API，不 import server internals。
- hooks 支持适配各自场景的状态模型：session/turn/artifacts/jobs/approvals 使用 idle/loading/success/error；events 使用 idle/loading/streaming/reconnecting/error。
- event hook 基于 V3.5-E1 TS SDK core client，不重新定义协议。
- `useApprovals` 只调用 `approval.respond`，不暴露 approve/reject 双入口。
- `useArtifacts` 不默认调用 inline `artifact.read`，`useJobs` 不默认轮询。
- hook state 和 debug output 不泄露 capability token、subscription token 或 signed URL query。

### V3.5-F App Gateway / BFF Template

这是 Full 阶段的完整 BFF Template，不是 MVP smoke。

当前状态：已完成。

PR slices：

- `V3.5-F-PR1`：定义 `templates/bff/fastapi` structure。
- `V3.5-F-PR2`：定义 optional Node template。
- `V3.5-F-PR3`：定义 IdentityProvider、ScopeResolver、CapabilityPolicy、ErrorSanitizer 扩展点。
- `V3.5-F-PR4`：定义 constrained RPC proxy；`/bff/rpc` 默认拒绝 `events.subscribe`。
- `V3.5-F-PR5`：定义 structured routes、artifact external registration 写权限和 approval respond。
- `V3.5-F-PR6`：定义 EventSource proxy，透传 Last-Event-ID/cursor，不暴露 upstream subscription token。
- `V3.5-F-PR7`：定义 CORS/config safety、secret hygiene、legacy/debug proxy denylist。

验收：

- BFF template 不实现完整用户系统。
- BFF 不代理 forbidden legacy/debug APIs。
- BFF-side CapabilityPolicy 生效。
- `/bff/rpc` 默认拒绝 `events.subscribe`。
- structured routes 覆盖 session、turn、artifact、job、approval、pack、connector。
- EventSource proxy 透传 Last-Event-ID/cursor 且不泄露 upstream subscription token。
- Full BFF Template contract 和 E2E tests 全绿。
- BFF 所有请求绑定 scope。
- EventSource proxy 保留 event id 和 cursor。
- native EventSource 可通过 same-origin BFF cookie 或 signed URL 认证。

### V3.5-G Pack / Connector Template

当前状态：已完成。

PR slices：

- `V3.5-G-PR1`：定义 `templates/pack` structure。
- `V3.5-G-PR2`：定义 `templates/connector` structure。
- `V3.5-G-PR3`：定义 `tests/fixtures/v3_5/dummy_pack` 和 `tests/fixtures/v3_5/dummy_connector`，作为模板实例化后的 runtime fixture。
- `V3.5-G-PR4`：定义 template acceptance tests，证明 templates 目录本身不会被 `pack.list` / `connector.health` 自动发现。
- `V3.5-G-PR5`：定义 no-Core-change verification，dummy discovery 只能来自 external pack path / connector descriptor path，不硬编码 dummy id。
- `V3.5-G-PR6`：定义 `manifest_schema_version/min_harnessos_version/target_harnessos_version` 兼容规则；`compatibility_warnings` 由 loader / assembly / health result 生成。

验收：

- dummy pack 通过 external pack path 显式注入后可被 `pack.list/pack.get` 发现。
- dummy connector 通过 external descriptor path 显式注入后可被 `connector.health` 消费。
- templates 目录本身不会被自动发现。
- connector template 包含 trust level、execution mode、allowed paths/commands/network policy。
- PackAssemblyResult 暴露 compatibility warnings。
- Connector discovery 只读取 `descriptor.json`，不执行 `health.py` / `tools.py`。

### V3.5-H Embed Contract / AgentTalkWindow 前置

PR slices：

- `V3.5-H-PR1`：拆分静态 `EmbedDefinition` 与运行时 `EmbedBootstrap`。
- `V3.5-H-PR2`：定义 `capabilityMode`、`transportMode`、`allowedEventChannels` 和 `allowedActions`。
- `V3.5-H-PR3`：在 BFF template 中提供 `GET /bff/embed/bootstrap` 示例 route，默认不创建 session，不泄露 upstream subscription token。
- `V3.5-H-PR4`：定义 chat/job/artifact/approval/trace/business event union，并与 `EVENT_SCHEMAS` 对齐。
- `V3.5-H-PR5`：新增 `sdk/typescript/src/embed.ts`，只导出类型和轻量 validation helper。
- `V3.5-H-PR6`：新增平台中立 `examples/embed_contract_demo` fixture。

验收：

- 未来 AgentTalkWindow 只依赖 contract，不依赖 Gateway 内部对象。
- `EmbedDefinition` 不包含 token/session/eventsourceUrl。
- `EmbedBootstrap` 不泄露 upstream `subscription_token`，默认返回 BFF-local EventSource URL。
- allowed actions 不包含 approve/reject、Meeting/Knowledge、scope_mode=all 或 debug/admin methods。
- trace channel 默认关闭。
- blocked、approval-required、auth-required、subscription-expired、failed、completed 状态可被 UI 区分。

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
V3.5-MVP
V3.5-0
  -> V3.5-A
  -> V3.5-B
  -> V3.5-C
  -> V3.5-D
  -> V3.5-D2

V3.5-Full
  -> V3.5-E1
  -> V3.5-E2
  -> V3.5-F
  -> V3.5-G / V3.5-H
  -> V3.5-I
```

## 6. Exit Standard

V3.5-MVP 出门标准：

- method/event/error registry 可用。
- `approval.respond` runtime 可用，`events.subscribe` runtime 可用。
- local capability token 可用。
- browser EventBridge 可被 native EventSource 和 fetch stream 消费。
- Python SDK 可完成 session/turn/event/artifact/job/approval 基础流程。
- Minimal BFF Smoke 可代理 JSON-RPC 和 EventSource。
- SDK/BFF 不暴露 legacy/debug/admin/business wrapper。
- 当前平台回归保持绿灯。

MVP 只能声明 `dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke`，不能声明 `V3.5 complete` 或 production-ready external app support。

V3.5 出门标准：

- 至少一个平台中立 reference app 能不改 Core 接入。
- SDK/BFF/hooks/event bridge 均通过 contract tests。
- Auth/capability token 明确区分 dev-only 和 local production mode。
- Pack/Connector template 可生成可被 registry 发现的最小样例。
- Embed contract 能支撑 AgentTalkWindow 前置集成。
- 当前平台回归保持绿灯。
