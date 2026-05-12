# V3.5 Acceptance Plan

文档状态：V3.5-MVP acceptance baseline with end-to-end SDK+BFF+EventBridge smoke；V3.5-E1 TypeScript SDK Core Client complete；V3.5-E2 React Hooks complete；V3.5-F Full BFF Template complete；V3.5-G Pack / Connector Template complete；V3.5-H Embed Contract complete；V3.5-I Reference App complete。V3.5 complete at dev/local Application Adaptation Layer level。

Completion evidence bundle: `docs/design/V3.5/v3_5_completion_evidence_bundle.md`。

## 1. Baseline

V3.5 启动基线：

- Application Adaptation Layer 以 dev/local-first 方式启动。
- 当前默认回归基线必须保持绿灯。
- 本阶段不把历史业务 E2E 重新作为 V3.5 完成条件。

## 2. Phase Acceptance

| 阶段 | 验收项 |
| --- | --- |
| V3.5-0 | `core/protocol/contracts/` 机器可读 inventory 完整；legacy/debug blacklist 明确；scaffold 目录 README-only/scaffold-only；Phase0 baseline 文档完整。 |
| V3.5-A | method/event/error schema registry；`approval.respond` runtime method；`events.subscribe` schema only with `runtime_handler=false`；result/error 互斥测试。 |
| V3.5-B | local capability token；AppProfile 权限上界；scope/capability/origin 校验；external transport guard；dev mode 显式开启。 |
| V3.5-C | `events.subscribe` runtime method；native EventSource signed URL；fetch stream bearer；scope/token/channel 校验；opaque cursor replay；heartbeat；local follow mode。 |
| V3.5-D | Python SDK MVP 方法全覆盖；runtime 不 import server internals；scope 透传；typed error / transport error 映射；token redaction；legacy/business wrappers excluded。 |
| V3.5-D2 | Platform-neutral Minimal BFF Smoke；Python SDK constrained proxy；EventSource proxy；scope binding；denylist；secret hygiene。 |
| V3.5-MVP E2E | 真实 Minimal BFF + 真实 Python SDK + harnessOS TestClient/ASGI transport；session/turn/events/approval/artifact/job/pack/connector/denylist/scope/redaction smoke。 |
| V3.5-E1 | TS SDK core client；schema default surface；runtime boundary；native EventSource / fetch stream descriptor handling；legacy/debug/business wrappers excluded。 |
| V3.5-E2 | React hooks；core TS SDK import 不强制依赖 React；no-auto-start session/turn/events；EventSource reconnect/cursor/dedupe；不得先于 V3.5-C 和 V3.5-E1。 |
| V3.5-F | Full BFF Template；BFF-side CapabilityPolicy；RPC safe subset；EventSource proxy；CORS/config/scope/secret hygiene；denylist。 |
| V3.5-G | Pack / Connector templates；templates not auto-discovered；dummy pack external path discovery；dummy connector external descriptor discovery；no-Core-change verification；version compatibility blocked/degraded envelope。 |
| V3.5-H | Static EmbedDefinition；runtime EmbedBootstrap；BFF-local EventSource bootstrap；allowed actions；event union；UI states；platform-neutral demo fixture。 |
| V3.5-I | Platform-neutral reference app；frontend BFF-only；BFF EventSource proxy；embed bootstrap safety；approval.respond flow；trace summary；external pack/connector discovery；scope isolation；token/subscription redaction。 |

## 3. MVP Exit Standard

V3.5-0 完成后只能声明：

- `V3.5 implementation ready`

V3.5-0 不能声明：

- supported public API changed
- SDK usable
- external app ready
- `dev/local adaptation layer ready`
- `V3.5 complete`

V3.5-A 完成后只能声明：

- `protocol schema and approval response contract ready`

V3.5-A 不能声明：

- `V3.5-MVP complete`
- SDK usable
- external app ready
- `events.subscribe` runtime ready

V3.5-B 完成后只能声明：

- `local capability token and external auth contract ready`

V3.5-B 不能声明：

- `V3.5-MVP complete`
- SDK usable
- external app ready
- production-ready auth
- `events.subscribe` runtime ready

V3.5-C 完成后只能声明：

- `browser event bridge contract and local runtime ready`

V3.5-C 不能声明：

- `V3.5-MVP complete`
- SDK usable
- external app ready
- complete event bus
- multi-worker / distributed real-time event consistency

V3.5-D 完成后只能声明：

- `Python SDK MVP usable for local/backend integration smoke`

V3.5-D 不能声明：

- SDK production-ready
- external app ready
- `V3.5-MVP complete`
- TypeScript SDK usable
- React hooks ready

V3.5-D2 完成后可以声明：

- `Minimal BFF Smoke proves JSON-RPC and EventSource proxy feasibility`

如果 V3.5-0/A/B/C/D/D2 全部绿灯，可以声明：

- `V3.5-MVP dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke`

V3.5-D2 不能声明：

- production-ready external app support
- full BFF template complete
- external app ready
- `V3.5 complete`

V3.5-MVP 完成后只能声明：

- `dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke`
- Python SDK MVP 可用于本地/后端 smoke。
- Minimal BFF Smoke 可证明 BFF 代理路径可行。

V3.5-MVP 不能声明：

- `V3.5 complete`
- `production-ready external app support`
- `full browser app integration ready`

V3.5-G 完成后只能声明：

- `Pack / Connector templates ready for dev/local external app integration scaffolding`

V3.5-G 不能声明：

- `V3.5 complete`
- Reference App complete
- Embed Contract complete
- production-ready external app support

V3.5-H 完成后只能声明：

- `Embed contract ready for dev/local AgentTalkWindow preparation`

V3.5-H 不能声明：

- AgentTalkWindow ready
- Workflow Studio ready
- external app ready
- `V3.5 complete`

V3.5-I 完成后可以声明：

- `V3.5 complete at dev/local Application Adaptation Layer level`

V3.5-I 不能声明：

- production-ready external app support
- complete AgentTalkWindow
- complete Workflow Studio
- enterprise auth/OAuth/SSO ready
- multi-tenant production control plane ready

V3.5-E1 完成后只能声明：

- `TypeScript SDK core client ready for dev/local protocol integration smoke`

V3.5-E1 不能声明：

- React hooks ready
- external app ready
- production-ready browser integration
- `V3.5 complete`

V3.5-E2 完成后只能声明：

- `React hooks ready for dev/local UI integration smoke`

V3.5-E2 不能声明：

- external app ready
- production-ready browser integration
- AgentTalkWindow ready
- Workflow Studio ready
- `V3.5 complete`

V3.5-F 完成后只能声明：

- `Full BFF Template ready for dev/local external app integration smoke`

V3.5-F 不能声明：

- production-ready external app support
- AgentTalkWindow ready
- Workflow Studio ready
- Pack/Connector template complete
- Reference app complete
- `V3.5 complete`

MVP 必须满足：

- method/event/error registry 可用。
- `approval.respond` 可用，且 repeated same decision、conflicting decision、invalid decision、not found、scope mismatch 测试通过。
- `events.subscribe` runtime 可用。
- local capability token 可用。
- browser EventBridge 可被 native EventSource 和 fetch stream 消费。
- Python SDK 可完成 session/turn/event/artifact/job/approval 基础流程。
- Minimal BFF Smoke 可代理 JSON-RPC 和 EventSource。
- MVP E2E 使用真实 Minimal BFF、真实 Python SDK 和 harnessOS ASGI/TestClient transport 串起 session、turn、events.subscribe、EventSource proxy、approval.respond、artifact/job/pack/connector 查询、denylist、scope isolation 和 redaction。
- SDK/BFF 不暴露 legacy/debug/admin/business wrapper。

## 4. Full Exit Standard

V3.5 完成必须满足：

- 至少一个平台中立 reference app 能不改 Core 接入。
- SDK/BFF/hooks/event bridge 均通过 contract tests。
- Auth/capability token 明确区分 dev-only 和 local production mode。
- Pack/Connector template 可生成可被 registry 发现的最小样例。
- Embed contract 能支撑 AgentTalkWindow 前置集成。
- 默认全量回归保持绿灯。

只有 Full 完成后，才能声明 `V3.5 complete`。

## 5. Required New Acceptance Tests

- Phase0 contract inventory tests：planned default methods 必须有 planned_phase；forbidden methods 必须有 forbidden_reason；default/optional/forbidden surfaces 不重叠；business wrappers 不进入 default surface；event aliases 不冲突；error codes 不重复。
- Phase0 scaffold tests：`sdk/`、`templates/`、`examples/reference_app/`、`docs/integration/` 只包含 README/.gitkeep 或 Phase0 baseline；SDK package 不暴露可 import 的可用 API。
- V3.5-A schema registry tests：contracts default methods 必须有 schema；schema methods 必须存在于 contracts inventory；forbidden_by_default 不进入 default schema exposure；planned methods 可以有 schema 但必须 `runtime_handler=false`。
- V3.5-A method.list tests：默认 excludes planned `events.subscribe`，includes `approval.respond`，schema metadata 可见。
- V3.5-C method.list tests：`events.subscribe` 转为 implemented 后默认 callable list 必须返回该方法，且 schema_ref 可解析。
- V3.5-A approval.respond tests：覆盖 idempotency、conflict、not found、invalid decision、scope mismatch，且 repeated same decision 不重复写 decision trace。
- native EventSource browser auth test：原生 `EventSource` 不设置 Authorization header，使用 same-origin BFF cookie 或 signed subscription URL 通过认证。
- approval.respond idempotency tests：覆盖 repeated same decision、conflicting decision、invalid decision、scope mismatch、approval not found、retry consumed。
- SDK default surface legacy/debug exclusion test：SDK 不能默认暴露 legacy/debug/admin bypass methods。
- SDK default export business wrapper exclusion test：SDK 不能默认导出 `generateMinutes()`、`ingestDocument()`、`runMeetingWorkflow()`、`generateVideo()`、`analyzePortfolio()` 等业务 wrapper。
- reference app neutrality test：reference app 不依赖 Meeting/Knowledge pack 或 legacy RPC。
- BFF cannot proxy forbidden methods test：BFF 对 legacy/debug/admin bypass method 返回稳定 forbidden error。
- REST scope compatibility test：`/v1/runs` 与 `/v1/runs/stream` 如保留，必须校验 app_id/project_id/workspace_id 和 token scope。
- V3.5-B auth tests：token 不能扩大 AppProfile origins/capabilities；method capability resolver 覆盖 SDK default methods；普通 token 不能 `include_forbidden`；legacy/debug HTTP route 默认不可无鉴权暴露；nested/top-level scope 冲突返回 `SCOPE_MISMATCH`；token 字符串不进入错误响应；dev mode 拒绝 non-local origin；`/v1/runs/stream` 鉴权失败不得打开 stream。
- V3.5-C event bridge tests：signed URL 无 Authorization header 可连接；fetch bearer 可连接；subscription token tamper/expired/scope/channel 被拒绝；event envelope 符合 `EVENT_SCHEMAS`；dedupe 生效；heartbeat 不持久化；`Last-Event-ID` 优先于 query cursor；`/v1/runs/stream` 保持 pre-auth compatibility。
- V3.5-D Python SDK tests：no server internals import；strict `__all__`；snapshot 与 server schema default/runtime subset 对齐；low-level `rpc()` 默认拒绝 forbidden；transport errors；token/subscription redaction；scope override conflict；approval repeated approve/reject idempotency；nested scope payload。
- V3.5-D2 Minimal BFF tests：platform-neutral config；no server internals import；identity/route/body scope conflict；`/bff/rpc` allowlist/denylist；EventSource proxy preserves `id/event/data`；does not call `/v1/runs/stream`; token/subscription redaction。
- V3.5-MVP E2E tests：真实 Minimal BFF + 真实 Python SDK + harnessOS ASGI/TestClient transport；覆盖 BFF session/turn、SDK `events.subscribe`、BFF EventSource proxy、`approval.respond`、artifact/job/pack/connector 基础查询、denylist、scope isolation、token/subscription redaction；不依赖 Meeting/Knowledge/外部 MCP。
- V3.5-E1 TypeScript SDK tests：no server internals import；public API surface；protocol snapshot vs server schema；low-level `rpc()` forbidden checks；`method.list(include_forbidden=true)` rejected；JSON-RPC response validation；token redaction；scope injection/conflict；EventSubscription relative/absolute URL；native EventSource no Authorization header；fetch stream bearer mode；session/turn/events/artifact/job/approval/connector/pack integration smoke。
- V3.5-E2 React hooks tests：no server internals import；core TS SDK import 不强制依赖 React；React public export surface；no business hooks；`useHarnessSession`/`useTurn` no-auto-start；`useEvents` no-auto-connect by default、native EventSource no Authorization header、close on unmount、StrictMode no duplicate live source、reconnect with cursor、dedupe；`useApprovals` only `approval.respond`；`useArtifacts` no inline `artifact.read`；`useJobs` no default polling；token/subscription redaction。
- V3.5-F Full BFF Template tests：config safety；demo identity explicit mode；BFF-side CapabilityPolicy；`/bff/rpc` rejects `events.subscribe`；structured routes；artifact external write capability；EventSource Last-Event-ID/cursor propagation；no `/v1/runs/stream` default path；secret redaction；no import from `fastapi_minimal` or server internals；platform-neutral E2E without Meeting/Knowledge/external MCP。

## 6. No False Green Rule

- 未实现 auth token 时，不得声明 production-ready external app support。
- 未实现 native EventSource browser auth 和 fetch stream bearer auth 时，不得声明 browser event bridge 完成。
- 未实现 protocol schema registry 时，不得声明 generated/typed SDK 完成。
- 只完成 V3.5-0 时，不得声明 SDK usable 或 external app ready。
- 只完成 V3.5-A 时，不得声明 MVP complete、SDK usable、external app ready 或 `events.subscribe` runtime ready。
- 只完成 V3.5-B 时，不得声明 SDK usable、external app ready、production-ready auth 或 V3.5-MVP complete。
- 只完成 V3.5-C 时，不得声明 SDK usable、external app ready、complete event bus 或 V3.5-MVP complete。
- 只完成 V3.5-D 时，不得声明 SDK production-ready、external app ready、TypeScript SDK usable、React hooks ready 或 V3.5-MVP complete。
- 只完成 V3.5-D2 且 V3.5 MVP E2E tests 未全绿时，不得声明 V3.5-MVP dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke。
- 只完成 V3.5-MVP 时，不得声明 V3.5 complete。
- 只完成 V3.5-E1 时，不得声明 React hooks ready、external app ready、production-ready browser integration 或 V3.5 complete。
- 只完成 V3.5-E2 时，不得声明 external app ready、production-ready browser integration、AgentTalkWindow ready、Workflow Studio ready 或 V3.5 complete。
- 只完成 V3.5-F 时，不得声明 production-ready external app support、AgentTalkWindow ready、Workflow Studio ready、Pack/Connector template complete、Reference app complete 或 V3.5 complete。
- 未通过平台中立 reference app 时，不得声明 V3.5 出门。
