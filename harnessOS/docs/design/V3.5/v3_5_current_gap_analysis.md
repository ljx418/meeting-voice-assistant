# V3.5 Current Gap Analysis

文档状态：V3.5-MVP complete；V3.5-E1 TypeScript SDK Core Client complete；V3.5-E2 React Hooks complete；V3.5-F Full BFF Template complete；V3.5-G Pack / Connector Template complete；V3.5-H Embed Contract complete；V3.5-I Reference App complete。V3.5 complete at dev/local Application Adaptation Layer level。  
配套图：`v3_5_current_gap_analysis.drawio`。

本文与 `v3_5_current_gap_analysis.drawio` 是 V3.5 后续规划、验收和与用户交互时的核心维护文件。两者必须同步更新：本文承载文字合同，drawio 承载同一套七层目标架构、差距矩阵和阶段路线图。

## 1. 文档定位

本文只描述 V3.5 Application Adaptation Layer 的当前差距、目标架构和阶段影响范围。历史阶段信息只作为背景，不进入本文主叙事。

V3.5 不再沿用“六大平面 + 历史路标”的 gap 主线。当前目标架构已经升级为七层：

```text
Plane-0 Product UI / External Business App
Plane-1 Application Adaptation Layer
Plane-2 Protocol App Server
Plane-3 Harness Core
Plane-4 Runtime Adapter
Plane-5 Domain Pack
Plane-6 Connector / Tool / Store
```

V3.5 的新增工作面主要落在 `Plane-1 Application Adaptation Layer`，并向上服务 `Plane-0`，向下消费 `Plane-2` 到 `Plane-6`。因此，V3.5 gap 不应再被描述成 Core 重构、Pack 迁移或业务 workflow 迁移。

V3.5 按 MVP -> Full 两段推进。MVP 已证明 dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke；Full 当前已完成 reference app，因此可以声明 V3.5 complete at dev/local Application Adaptation Layer level。

## 2. 当前状态

当前 harnessOS 已具备 V3.5 dev/local Application Adaptation Layer，并通过 SDK+BFF+EventBridge 与平台中立 Reference App smoke 验证；V3.5-E1 TypeScript SDK Core Client、V3.5-E2 React Hooks、V3.5-F Full BFF Template、V3.5-G Pack / Connector Template、V3.5-H Embed Contract 与 V3.5-I Reference App 已完成。当前可以声明 V3.5 complete at dev/local Application Adaptation Layer level，但不能声明 production-ready external app support。

当前事实：

- Protocol App Server 已有 JSON-RPC / HTTP / stdio 等基础入口。
- Core 已有 scope、job、artifact、trace、approval、pack、connector 等可消费对象。
- Pack / Connector / Job / Artifact / Governance 合同可作为适配层消费对象。
- 已有 protocol schema registry、`approval.respond`、local capability token、browser event bridge、Python SDK MVP、TypeScript SDK Core Client 和 Minimal BFF Smoke。
- 已有平台中立 MVP E2E smoke，覆盖真实 Minimal BFF、真实 Python SDK 与 harnessOS ASGI/TestClient transport。
- TypeScript SDK E1、React Hooks E2、Full BFF Template F、Pack/Connector Template G、Embed Contract H 与 Reference App I 已通过 contract/E2E 测试。

当前 V3.5 的剩余缺口不再是“dev/local 适配层能不能跑”，而是：

> 如何把 dev/local reference app 证明过的适配层升级为 production-ready external app support，包括企业级 auth、长期运维、多租户控制面和完整产品化 UI。

## 3. 七层目标架构

| 平面 | 名称 | 职责 | V3.5 关系 |
| --- | --- | --- | --- |
| Plane-0 | Product UI / External Business App | 业务前端、业务 BFF consumer、嵌入式面板、外部产品体验。 | V3.5 的直接使用方。 |
| Plane-1 | Application Adaptation Layer | SDK、BFF template、React hooks、Event bridge、Pack/Connector template、Embed contract、capability token。 | V3.5 主工作面。 |
| Plane-2 | Protocol App Server | JSON-RPC、HTTP、SSE/EventSource、stdio、method/event/error schema。 | V3.5 通过 schema 和 event bridge 强化，不改业务语义。 |
| Plane-3 | Harness Core | AppProfile、ScopeContext、Session、Turn、Job、Artifact、Trace、Approval、Policy、Retry、Store。 | V3.5 消费 Core 合同，不重构 Core。 |
| Plane-4 | Runtime Adapter | 执行边界、runtime 适配、治理注入。 | V3.5 不新增 runtime 入口，只通过协议和 Core 调用。 |
| Plane-5 | Domain Pack | workflow、skill、policy、artifact kind、pack assembly。 | V3.5 提供模板和发现方式，不重新迁移业务 pack。 |
| Plane-6 | Connector / Tool / Store | MCP、stdio/http connector、外部服务、本地工具、持久化事实源。 | V3.5 提供 connector template 和 health/capability 接入样板。 |

## 4. 目标状态

V3.5 完成后，外部业务 App 的标准接入路径应为：

```text
Product UI / External Business App
  -> SDK / React hooks
  -> BFF template
  -> capability token + scope binding
  -> JSON-RPC / native EventSource / fetch stream
  -> Core job / artifact / approval / trace
  -> Pack / Connector as needed
```

前端接入模式分为两类：

```text
Production recommended:
  Business UI -> BFF -> harnessOS

Dev/direct:
  Business UI -> TypeScript SDK -> harnessOS
```

生产默认路径不应让浏览器长期持有广权限 capability token。Dev/direct 只允许受限 capability token、短期 token 或显式 dev mode。

目标状态必须满足：

- 外部 App 不直接访问 Core Store。
- 外部 App 不调用 legacy/debug API 作为默认路径。
- SDK/BFF 默认携带 scope。
- token 绑定 scope、origin、capabilities。
- browser event bridge 支持 native EventSource、fetch stream 和 replay cursor。
- Pack / Connector template 可以生成 registry 可发现的最小样例。
- 平台中立 reference app 能不改 Core 完成接入。

## 5. 开发计划摘要

### 5.1 当前开发阶段

当前项目处于 **V3.5-I Reference App 已完成，V3.5 complete at dev/local Application Adaptation Layer level** 的阶段。V3.5 的目标架构、MVP/Full 分段、SDK thin client 边界、EventSource 认证模式、`approval.respond` 幂等语义和出门口径已经明确；Phase0 已把约定落成仓库内的机器可读 inventory、脚手架目录和验收测试，V3.5-A/B/C/D/D2 已分别把协议 schema、auth boundary、EventBridge、Python SDK 和 Minimal BFF Smoke 落成可测试实现，并新增 MVP E2E 将真实 Minimal BFF、真实 Python SDK 和 harnessOS ASGI transport 串联验证。E1 已把 TypeScript SDK 从 scaffold-only 升级为可 import、可构建、可测试的 core client，E2 已把 React hooks 落成可 import、可测试的 UI integration smoke 层，F 已把 Full FastAPI BFF Template 落成可复制模板，G 已把 Pack / Connector 模板与显式 fixture discovery 落地，H 已把静态 `EmbedDefinition`、运行时 `EmbedBootstrap`、allowed actions、event union、UI states 和平台中立 demo fixture 落地，I 已把平台中立 reference app、BFF-only frontend、approval.respond flow、trace summary、external pack/connector discovery 和 scope isolation smoke 落地。

当前已经完成或正在落地的是“实施入口和合同事实源”：

- V3.5 的主目标已固定为 Application Adaptation Layer。
- 七层目标架构已固定，V3.5 主工作面是 Plane-1。
- MVP 与 Full 的边界已固定。
- 生产推荐路径已固定为 `Business UI -> BFF -> harnessOS`。
- Dev/direct 路径已限制为受限 capability token 或显式 dev mode。
- SDK 已明确为 thin protocol client，不承载业务 workflow wrapper。
- Phase0 新增 `core/protocol/contracts/` 作为 method / event / error inventory 的机器可读 source of truth。
- Phase0 新增 `sdk/`、`templates/`、`examples/reference_app/`、`docs/integration/` 脚手架入口，但不提供可 import 的 SDK API。
- V3.5-A 新增 `core/protocol/schemas/` 作为 params/result/event/error schema source of truth。
- V3.5-A 新增正式 runtime method `approval.respond`，冻结 idempotency、conflict、not found、invalid decision、scope mismatch 错误语义。
- V3.5-C 将 `events.subscribe` 从 schema-only 升级为 runtime method，并返回 `eventsource_url/subscription_token/replay_cursor/expires_at/allowed_channels`。
- V3.5-B 新增 local capability token、AppProfile auth fields、method capability resolver 和 external HTTP/RPC auth guard。
- V3.5-B 保护 `/v1/rpc`、`/v1/runs`、`/v1/runs/stream`、`/v1/sessions*`、`/api/agents`、`/api/routing`。
- V3.5-C 新增 `GET /v1/events/subscribe`，支持 signed URL native EventSource 和 bearer fetch stream。
- V3.5-C 实现 persisted event replay、opaque cursor、channel capability 校验、heartbeat 和 `/v1/runs/stream` pre-auth compatibility tests。
- V3.5-D 新增 `sdk/python/harnessos_client`，提供不 import server internals 的 thin JSON-RPC client。
- V3.5-D SDK 默认 surface 来自本地 protocol snapshot，并由测试与 server schema registry 对齐。
- V3.5-D SDK 已覆盖 scope 透传、typed error mapping、token/subscription redaction、`approval.respond` 幂等和 `events.subscribe` descriptor。
- V3.5-D2 新增 platform-neutral `templates/bff/fastapi_minimal`，证明 Python SDK constrained proxy、EventSource proxy、scope binding 和 denylist 可行。
- V3.5-D2 BFF 使用 `reference_app/demo/local` 默认配置，不硬编码 Meeting/Knowledge。
- V3.5-G 已要求 `templates/pack` / `templates/connector` 只作为可复制模板，不作为 runtime instances。
- V3.5-G 已要求 dummy pack / connector 放在 fixture 或 reference app 目录，并通过 external pack path / connector descriptor path 显式注入。
- V3.5-G 已要求 compatibility warnings 由 loader / assembly / health result 生成，manifest / descriptor 不自声明为事实。
- V3.5-H 已要求 `EmbedDefinition` 不包含 token/session/eventsourceUrl，一次运行态信息进入 `EmbedBootstrap`。
- V3.5-H 已要求 `GET /bff/embed/bootstrap` 只作为 BFF template / reference app 示例 route，不进入 Core。
- V3.5-I 已新增平台中立 reference app，frontend 默认只调用 `/bff/*`，不直接调用 `/v1/rpc` 或 `/v1/events/subscribe`。
- V3.5-I 已验证 `/bff/rpc` 拒绝 `events.subscribe`，Browser 事件订阅必须走 `/bff/events/subscribe`。
- V3.5-I 已验证 approval 只通过 `/bff/approvals/{approval_id}/respond` 调 `approval.respond`，不暴露 `approval.approve/reject`。
- V3.5-I 已验证 reference pack / connector 通过 external path / descriptor path 注入，不在 Core/Gateway 默认 registry 中硬编码。
- V3.5-D2 与新增 MVP E2E 完成后，V3.5-MVP 可声明 `dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke`。
- V3.5-E1 新增 `sdk/typescript` core client，覆盖 JSON-RPC、scope、typed errors、capability token、EventSubscription descriptor、native EventSource helper、fetch stream bearer helper 和 default wrappers。
- V3.5-E1 测试覆盖 no server internals import、public API surface、snapshot vs server schema、forbidden methods、response validation、redaction、scope conflict、EventSubscription URL、native EventSource/fetch stream 和 integration smoke。
- V3.5-E2 新增 React hooks，覆盖 session、turn、events、artifacts、jobs、approvals，且 hooks 默认不 auto-start，不暴露业务 hooks，不强制 core TS SDK 依赖 React。
- V3.5-F 新增独立 `templates/bff/fastapi` Full BFF Template，覆盖 config safety、BFF-side CapabilityPolicy、constrained RPC、structured routes、EventSource proxy、secret hygiene 和 platform-neutral BFF E2E。

V3.5-I 完成后，“完整外部 App 接入体系”的 dev/local 证明链路已经闭合：

- Embed contract 已完成，`EmbedDefinition` / `EmbedBootstrap` 分离，BFF bootstrap 不泄露 upstream token。
- 平台中立 reference app 已完成，frontend 默认只走 `/bff/*`，并验证 approval、events、artifact、job、trace summary、pack/connector 与 scope isolation。
- Completion evidence bundle 已落盘到 `docs/design/V3.5/v3_5_completion_evidence_bundle.md`。

### 5.2 已完成 Phase：V3.5-0

V3.5-0 的任务不是把接入层跑起来，而是把后续实现的边界变成仓库里的事实源。它要解决的是“后续开发按什么方法表、事件表、错误表、目录结构和禁止面来做”的问题。

本 Phase 要交付四类东西：

| 类别 | 交付物 | 当前状态 | 用途 |
| --- | --- | --- | --- |
| 工程入口 | `sdk/`、`templates/`、`examples/reference_app/`、`docs/integration/` 骨架和 README | 已落地；Python SDK 在 V3.5-D 已升级为可 import MVP，TypeScript SDK 在 V3.5-E1 已升级为 core client。 | 给后续 SDK、BFF、template、reference app 放置稳定入口。 |
| 协议清单 | `core/protocol/contracts/method_inventory.py`、`event_inventory.py`、`error_inventory.py` | 已落地，文件声明 non-runtime metadata only。 | 给 V3.5-A schema registry、V3.5-C EventBridge、V3.5-D SDK 提供输入。 |
| 禁止面 | SDK default / optional / forbidden surface 和 thin client boundary | 已落地，`approval.respond` 与 `events.subscribe` 均为 implemented default；legacy/debug/business facade 为 forbidden_by_default。 | 防止 `meeting.*`、debug API、业务 wrapper 进入 core SDK 默认面。 |
| 验收基线 | `tests/test_v3_5_contract_inventory.py`、`tests/test_v3_5_scaffolding.py`、`docs/integration/v3_5_phase0_baseline.md` | 已新增，验证结果以 baseline 文档为准。 | 证明 V3.5 后续实施没有从口头约定开始。 |

Phase0 的具体开发点与完成口径：

| 开发点 | 计划要求 | 当前状态 |
| --- | --- | --- |
| Inventory 位置 | 使用 `core/protocol/contracts/`，不做 handler registration，不改变运行时行为。 | 已完成。 |
| Method inventory | 固定 method/surface/status/capability/stability/planned_phase/handler_ref/forbidden_reason 字段。 | 已完成。 |
| Event inventory | 固定 type/channel/status/replayable/aliases 字段；`artifact.registered` 为 canonical，`artifact.created` 仅为 alias。 | 已完成。 |
| Error inventory | 固定 code/status/category/retryable/planned_phase 字段；补齐 subscription、method、scope、app profile、pack、connector、approval errors。 | 已完成。 |
| Source of truth | 机器可读 inventory 为 source of truth，本文档与 contract inventory 文档为人类可读摘要。 | 已完成。 |
| SDK scaffold | Phase0 只创建 README/.gitkeep；V3.5-D 开始允许 Python SDK 可 import，V3.5-E1 开始允许 TypeScript SDK core client 可 import/build/test。 | 已完成并已更新测试。 |
| Baseline 文档 | 记录 baseline_commit/date/python_env/pytest/drawio/external E2E exclusion。 | 已完成，已记录 Phase0 targeted、默认 tests 和 drawio 校验结果。 |
| Tests | 覆盖 planned phase、forbidden reason、surface overlap、business wrapper、event alias、duplicate error、scaffold-only。 | 已完成，Phase0 targeted tests 通过。 |

V3.5-0 已完成，项目已从“规划完成”进入“协议合同可实施”状态。该阶段本身不声明 SDK 可用或外部 App 可接入；后续 V3.5-D/E/F/I 已分别完成 SDK、BFF、hooks 和 reference app 证明。

### 5.3 已完成 Phase：V3.5-A

V3.5-A 的任务是把 Phase0 inventory 升级为可执行协议 schema，并新增唯一正式 runtime method `approval.respond`。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| Schema registry | `core/protocol/schemas/` 已新增 method/event/error schema registry。 | contracts.default methods 必须有 schema；schema methods 必须存在于 contracts inventory。 |
| Error registry | `ProtocolError` 已作为稳定错误入口，`approval.respond` 不依赖裸 `LookupError`/`ValueError`。 | 新 protocol methods 应抛稳定 protocol error。 |
| `approval.respond` | 已注册 runtime method，legacy approve/reject 保持兼容。 | repeated same decision idempotent；conflict/not found/invalid/scope mismatch 返回稳定错误码。 |
| `events.subscribe` | V3.5-C 已注册 runtime method，`runtime_handler=true`。 | 默认 callable method list 返回该方法；可签发短期 subscription token。 |
| JSON-RPC response | 已增加 result/error 互斥校验。 | both result and error、neither result nor error 均 invalid。 |
| method.list | 默认只列 callable runtime methods，并为有 schema 的 method 返回 schema metadata。 | planned schema 只能显式 include_planned 查询。 |

V3.5-A 检视修复状态：

| 检视问题 | 当前处理 |
| --- | --- |
| `approval.respond` 可用 `scope_mode=all` 绕过跨 scope 写操作。 | 已修复。审批写操作始终校验 approval 所属 scope，跨 scope 返回 `SCOPE_MISMATCH`。 |
| 默认 `method.list` / `initialize` 暴露 forbidden legacy/debug methods。 | 已修复。默认 discovery 过滤 forbidden；`include_forbidden=true` 才返回 legacy/debug metadata。 |
| conflict error metadata 可能返回 stale status。 | 已修复。`APPROVAL_CONFLICT` 使用锁内 current_status。 |
| `events.subscribe` 缺少 runtime event bridge regression。 | 已补测试。V3.5-C 后 direct call 无外部 auth 返回 `AUTH_REQUIRED`，带 token 可返回 signed URL。 |

V3.5-A 单阶段完成后只能声明：

```text
protocol schema and approval response contract ready
```

不能声明：

```text
V3.5-MVP complete
SDK usable
external app ready
events.subscribe runtime ready
```

### 5.4 已完成 Phase：V3.5-B

V3.5-B 的任务是实现 dev/local-first 的 external auth boundary，不开放匿名 HTTP token issuance，不实现 SDK/BFF/EventBridge。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| Local capability token | 已新增 HMAC token helper；签发仅限 CLI/local admin/internal test helper。 | token 绑定 app scope、capabilities、origins、expiry。 |
| AppProfile auth fields | 已扩展 `allowed_origins/default_capabilities/embed_policy`。 | AppProfile 是 token origins/capabilities 上界。 |
| Capability resolver | 已从 inventory/schema 解析 method capability。 | SDK default methods 必须可解析；`connector.health` -> `connectors.read`，`pack.list/get` -> `packs.read`。 |
| External guard | 已保护 `/v1/rpc`、runs、sessions、agents、routing。 | 无 token 默认 blocked；dev mode 必须显式开启。 |
| Scope normalization | 已校验 token scope、request scope、resource scope 和 `scope_mode=all`。 | scope mismatch 返回稳定 `SCOPE_MISMATCH`。 |
| Stream pre-auth | `/v1/runs/stream` 在打开 stream 前鉴权。 | 鉴权失败不得返回 event-stream。 |
| Secret hygiene | auth error redaction 已测试。 | token 不进入错误响应。 |

V3.5-B 单阶段完成后只能声明：

```text
local capability token and external auth contract ready
```

不能声明：

```text
V3.5-MVP complete
SDK usable
external app ready
production-ready auth
events.subscribe runtime ready
```

### 5.5 已完成 Phase：V3.5-C

V3.5-C 的任务是实现 browser-friendly event bridge，但不实现完整 event bus。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| `events.subscribe` runtime | 已注册 runtime method，默认 `method.list` 可见。 | 无外部 capability token 时返回 `AUTH_REQUIRED`；带 token 时签发 subscription descriptor。 |
| Native EventSource | 已支持 signed `eventsource_url` + `subscription_token`。 | 原生 EventSource 不依赖 Authorization header。 |
| Fetch stream | 已支持 `GET /v1/events/subscribe` + bearer token。 | 请求进入 stream 前完成 auth/scope/capability 校验。 |
| Channel capability | 已实现 chat/job/artifact/approval/trace 映射。 | trace 需要 `traces.read`，默认 AppProfile 不开放。 |
| Replay cursor | 已实现 opaque cursor，绑定 scope。 | `Last-Event-ID` 优先 query cursor；invalid cursor 返回 `EVENT_CURSOR_INVALID`。 |
| Persisted replay | 已从 session/job/artifact/approval/trace records 组装 envelope。 | event envelope 符合 `EVENT_SCHEMAS`；`artifact.registered` 为 canonical。 |
| Heartbeat / follow | 已支持 heartbeat comment frame 和 local follow mode。 | heartbeat 不进入 persisted event records。 |
| Compatibility | `/v1/runs/stream` 继续 pre-auth。 | 鉴权失败不得打开 stream。 |

V3.5-C 单阶段完成后只能声明：

```text
browser event bridge contract and local runtime ready
```

不能声明：

```text
V3.5-MVP complete
SDK usable
external app ready
complete event bus
distributed real-time event consistency
```

### 5.6 已完成 Phase：V3.5-D

V3.5-D 的任务是实现 Python SDK MVP，但保持 SDK 是 thin protocol client，不把业务能力或 server internals 带入 SDK runtime。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| Python package | `sdk/python/harnessos_client` 已可 import。 | Python SDK MVP 可用于 local/backend integration smoke。 |
| Runtime boundary | SDK runtime 使用本地 protocol snapshot。 | 不 import `apps.*`、`core.*`、GatewayService、RuntimeAdapter、Core Store 或 server `METHOD_SCHEMAS`。 |
| Public API | `__all__` 严格限定 client、models 和 typed errors。 | 不导出 Meeting/Knowledge client 或业务 wrapper。 |
| Default wrappers | 已覆盖 schema default/runtime method 子集。 | 不包装 planned/schema-only、legacy/debug/admin/business facade。 |
| Low-level `rpc()` | 默认检查 SDK snapshot surface。 | unknown/forbidden/default-excluded method 本地拒绝。 |
| Scope | client init 接收 default Scope，per-call same scope override allowed。 | app/project/workspace 明显冲突本地拒绝为 `ScopeMismatchError`。 |
| Errors | 已实现 typed protocol errors 和 `TransportError`。 | malformed JSON-RPC、transport failure、known protocol errors 均有稳定映射。 |
| Redaction | client、subscription、exception repr/string 均 redacts token。 | capability token / subscription token 不进入 repr/log。 |
| EventSubscription | `events_subscribe()` 只获取 descriptor。 | relative URL 转 absolute，不实现 SSE loop。 |

V3.5-D 单阶段完成后只能声明：

```text
Python SDK MVP usable for local/backend integration smoke
```

不能声明：

```text
SDK production-ready
external app ready
V3.5-MVP complete
TypeScript SDK usable
React hooks ready
```

### 5.7 已完成 Phase：V3.5-D2

V3.5-D2 的任务是实现 Minimal BFF Smoke，证明业务后端可以通过 Python SDK 代理 harnessOS，而不是绕过 SDK 直连 Core/Gateway。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| Platform-neutral config | `config.example.json` 使用 `reference_app/demo/local`。 | 不硬编码 `meeting` 或 `knowledge`。 |
| Scope binding | 已定义 `identity_scope / route_scope / body_scope`。 | identity scope 是上界，route/body 扩权返回 `SCOPE_MISMATCH`。 |
| Constrained RPC | `/bff/rpc` 只允许 SDK default surface。 | legacy/debug/admin/business facade 返回 `METHOD_FORBIDDEN`。 |
| Structured routes | 已提供 session、turn、approval respond smoke routes。 | 审批只暴露 `approval.respond`。 |
| EventSource proxy | `/bff/events/subscribe` 通过 SDK 获取 descriptor 并代理 upstream SSE。 | Browser 不看到 upstream subscription token，保留 `id/event/data`。 |
| Secret hygiene | error response redacts capability/subscription token。 | token 不进入 response error data。 |
| Import boundary | BFF 不 import GatewayService、RuntimeAdapter、Core Store 或 `apps.gateway.service`。 | 只能通过 `harnessos_client` 调用 harnessOS。 |

V3.5-D2 单阶段完成后可以声明：

```text
Minimal BFF Smoke proves JSON-RPC and EventSource proxy feasibility
```

V3.5-0/A/B/C/D/D2 已全部绿灯，因此 MVP 已声明：

```text
V3.5-MVP dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke
```

仍不能声明：

```text
production-ready external app support
full BFF template complete
external app ready
V3.5 complete
```

### 5.8 MVP E2E Smoke

新增 MVP E2E 的任务是把组件级绿灯升级为真实链路 smoke，而不是实现 V3.5-Full reference app。

| 验证点 | 当前状态 | 说明 |
| --- | --- | --- |
| Minimal BFF + Python SDK | 已通过 `tests/test_v3_5_mvp_e2e.py`。 | BFF 使用真实 `HarnessOSClient`，通过 ASGI/TestClient transport 调 harnessOS。 |
| Session / Turn | 已覆盖。 | `/bff/session/start` 与 `/bff/turn/start` 走 SDK -> `/v1/rpc`。 |
| EventBridge proxy | 已覆盖。 | `/bff/events/subscribe` 通过 SDK 获取 `events.subscribe` descriptor，再代理 upstream `/v1/events/subscribe`。 |
| Approval | 已覆盖。 | BFF 只暴露 `approval.respond`。 |
| Artifact / Job / Pack / Connector | 已覆盖基础查询。 | 不依赖 Meeting、Knowledge 或外部 MCP。 |
| Denylist / Scope isolation | 已覆盖。 | legacy/business facade 与跨 scope 请求被阻断。 |
| Redaction | 已覆盖。 | capability token、subscription token 不进入 BFF response、trace、job failure context。 |

MVP E2E 已完成，可以声明：

```text
V3.5-MVP dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke
```

仍不能声明：

```text
production-ready external app support
full browser app integration ready
V3.5 complete
```

### 5.9 已完成 MVP 开发路线

MVP 的目标是证明 dev/local-first 的适配层链路可用，当前已按下列顺序完成：

```text
V3.5-0 Contract Inventory & Scaffolding
  -> V3.5-A Protocol Schema Registry + Error Registry
  -> V3.5-B Capability Token MVP
  -> V3.5-C Browser Event Bridge
  -> V3.5-D Python SDK MVP
  -> V3.5-D2 Minimal BFF Smoke
```

每一步的核心产物：

- `V3.5-A`：method/event/error schema registry、`approval.respond`、`events.subscribe`、JSON-RPC result/error 互斥合同。
- `V3.5-B`：local capability token、scope/origin/capability 校验、AppProfile auth fields。
- `V3.5-C`：native EventSource / fetch stream、subscription token、replay cursor、channel filter。
- `V3.5-D`：Python thin SDK，覆盖 session/turn/event/artifact/job/approval/connector/pack；已落地。
- `V3.5-D2`：Minimal FastAPI BFF smoke，证明 BFF 代理 JSON-RPC、EventSource 和 denylist 可行；已落地。

MVP 完成后已声明：

```text
dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke
```

MVP 单独不能声明：

```text
V3.5 complete
production-ready external app support
full browser app integration ready
```

### 5.10 已完成 Full Phase：V3.5-E1

V3.5-E1 的任务是实现 TypeScript SDK Core Client。它复用 V3.5-MVP 已冻结的 JSON-RPC、scope、capability token、EventBridge、error registry 合同，不改变 Core，也不实现 React hooks。当前 E1 已完成并通过 TypeScript SDK 测试、V3.5 回归和全量 pytest。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| Package | `sdk/typescript` 已从 scaffold-only 升级为可构建 package。 | `npm test` 已通过。 |
| Runtime boundary | SDK runtime 使用 `protocolSnapshot.ts`。 | 已测试不 import `apps/*`、`core/*`、GatewayService、RuntimeAdapter 或 server `METHOD_SCHEMAS`。 |
| Public API | `index.ts` 只导出 core client、scope、errors、token/subscription、transport。 | 已测试不导出 Meeting/Knowledge client 或业务 wrapper。 |
| JSON-RPC client | 默认走 `/v1/rpc`，支持 injectable transport。 | 已测试 `rpc()` 默认拒绝 unknown、forbidden、legacy/debug/admin/business method。 |
| Scope / token | 自动注入 scope，只接收 capability token。 | 已测试不提供 token issuance/signing；冲突 scope 本地拒绝。 |
| EventSubscription | 只获取 descriptor，不做 reconnect/buffering/React state。 | 已测试 native EventSource 不依赖 Authorization header；fetch stream 可带 bearer。 |
| Browser / Node | Browser 提供 native EventSource URL helper。 | Node 默认只保证 JSON-RPC fetch；复杂 event streaming 留给 E2/F 或用户实现。 |

E1 完成后当前可声明：

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

### 5.11 已完成 Full Phase：V3.5-E2

V3.5-E2 的任务是基于 E1 TypeScript SDK Core Client 实现 React Hooks。E2 只做前端状态模型，不重新定义协议，不绕过 SDK，不引入 Meeting/Knowledge 业务 wrapper。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| Hook package | 已完成。 | 基于 `sdk/typescript`，通过 `@harnessos/client/react` / `sdk/typescript/src/react` 暴露，不直接调用 server internals，core TS SDK import 不强制依赖 React。 |
| Session / Turn hooks | 已完成。 | `useHarnessSession`、`useTurn` 使用 E1 client，默认不 auto-start。 |
| Events hook | 已完成。 | `useEvents` 使用 EventSubscription descriptor，默认不自动打开 EventSource；支持 native EventSource 基础 lifecycle、cursor、dedupe、close on unmount。 |
| Data hooks | 已完成。 | `useArtifacts`、`useJobs` 只消费 SDK default wrappers，不默认 inline read 或 polling。 |
| Approval hook | 已完成。 | `useApprovals` 只调用 `approval.respond`，不暴露 approve/reject 双入口，不默认 approval.list。 |
| State model | 已完成。 | session/turn/artifacts/jobs/approvals 使用 idle/loading/success/error；events 使用 idle/loading/streaming/reconnecting/error。 |
| Boundary | 已完成。 | 不提供业务 hooks，例如 `useMeetingMinutes` 或 `useKnowledgeSearch`。 |

E2 完成后只能声明：

```text
React hooks ready for dev/local UI integration smoke
```

不能声明：

```text
production-ready browser integration
external app ready
AgentTalkWindow ready
Workflow Studio ready
V3.5 complete
```

### 5.12 已完成 Full Phase：V3.5-F

V3.5-F 的任务是把 D2 Minimal BFF Smoke 升级为独立可复制的 Full FastAPI BFF Template。它不是 production-ready BFF，不实现完整用户系统/OAuth/SSO/多租户权限后台，不签发 harnessOS capability token，不向浏览器暴露长期 harnessOS capability token。

| 开发点 | 当前状态 | 出门口径 |
| --- | --- | --- |
| Full FastAPI template | 已完成。 | `templates/bff/fastapi` 独立存在，不依赖 `templates/bff/fastapi_minimal`。 |
| Config safety | 已完成。 | `config.example.json` 无真实 token；`.env.example` 只含 placeholder；wildcard origin + credentials 报错；demo identity 显式开启。 |
| Identity / Scope / CapabilityPolicy | 已完成。 | identity scope 是上界；BFF-side capability 是 structured routes 与 `/bff/rpc` 的上界。 |
| `/bff/rpc` | 已完成。 | 只允许 SDK default safe subset，并默认拒绝 `events.subscribe`。 |
| Structured routes | 已完成。 | 覆盖 sessions、turns、artifacts、jobs、approvals、packs、connectors。 |
| EventSource proxy | 已完成。 | 前端走 `/bff/events/subscribe`，BFF 隐藏 upstream subscription token 并透传 Last-Event-ID/cursor。 |
| Secret hygiene | 已完成。 | capability token、Authorization、subscription token、signed URL query 不进入 response/log/repr。 |

F 完成后只能声明：

```text
Full BFF Template ready for dev/local external app integration smoke
```

不能声明：

```text
production-ready external app support
AgentTalkWindow ready
Workflow Studio ready
Pack/Connector template complete
Reference app complete
V3.5 complete
```

### 5.13 已完成 Full 开发路线

Full 的目标是把 MVP 证明过的能力扩展成完整、可复用的外部 App 接入体系，当前已完成：

```text
V3.5-E1 TypeScript SDK core client
  -> V3.5-E2 React hooks
  -> V3.5-F Full BFF Template
  -> V3.5-G Pack / Connector Template
  -> V3.5-H Embed Contract
  -> V3.5-I Platform-neutral Reference App
```

Full 完成后应具备：

- 后端可以通过 Python SDK 调用 harnessOS。
- 前端可以通过 TS SDK / hooks 发起 turn、订阅 events、展示 jobs/artifacts/approvals。
- 生产业务 UI 默认通过 BFF 安全接入。
- 新业务可以通过 Pack / Connector template 声明能力，不改 Core。
- Embed contract 可以支撑未来 AgentTalkWindow。
- 平台中立 reference app 可以证明新业务不改 Core 接入。

Full 已完成后，当前正式声明：

```text
V3.5 complete at dev/local Application Adaptation Layer level
```

## 6. Completed Capability Matrix

本矩阵不再把 V3.5 dev/local 适配层描述为核心开发差距。当前列出的都是已经落地并通过 evidence bundle 验证的能力；剩余问题统一归入第 8 节的正式外部 App 生产化缺口。

| 能力 | 当前实现状态 | 稳定目标 / 边界 | 主要影响平面 | 阶段 |
| --- | --- | --- | --- | --- |
| Scaffolding | `sdk/`、`templates/`、`examples/reference_app/`、`docs/integration/` 已落地。 | 目录结构、contract inventory、legacy/debug blacklist 已作为后续实现入口。 | Plane-1 | V3.5-0 |
| Method Schema | V3.5-A 已新增 `core/protocol/schemas/methods.py`，default methods 有 schema。 | SDK/BFF 从 schema default surface 对齐。 | Plane-1 / Plane-2 | V3.5-A |
| Event Schema | V3.5-A 已新增 event envelope/channel schema。 | EventBridge、SDK、hooks 和 BFF 复用同一 event schema。 | Plane-1 / Plane-2 / Plane-3 | V3.5-A/C/E/F |
| Error Registry | V3.5-A 已新增 error schema registry 和 `ProtocolError`。 | auth/event/SDK/BFF 复用稳定错误码。 | Plane-1 / Plane-2 | V3.5-A |
| `approval.respond` | V3.5-A 已实现 runtime method。 | SDK/BFF 统一调用 `approval.respond`，legacy approve/reject 仅兼容。 | Plane-1 / Plane-2 / Plane-3 | V3.5-A |
| `events.subscribe` | V3.5-C 已实现 runtime method，`runtime_handler=true`。 | V3.5-D SDK 复用该合同生成事件订阅客户端。 | Plane-1 / Plane-2 | V3.5-C / D |
| Capability Token | V3.5-B 已实现 local HMAC token。 | 后续 BFF/SDK/EventBridge 复用 token contract。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-B |
| AppProfile Auth Fields | V3.5-B 已新增 origin/capability/embed 字段。 | AppProfile 持续作为 token 权限上界。 | Plane-1 / Plane-3 | V3.5-B |
| REST Scope | V3.5-B 已为 run/stream/RPC/session HTTP 入口加 token/scope guard。 | V3.5-C 继续接入 EventBridge token/cursor。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-B / C |
| Browser Event Bridge | V3.5-C 已新增 `GET /v1/events/subscribe`、signed URL、fetch bearer、cursor replay 和 heartbeat。 | SDK、hooks、BFF 和 reference app 已复用；本阶段不扩展为完整 distributed event bus。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-C / D / E / F / I |
| Python SDK | V3.5-D 已实现 thin Python SDK MVP。 | Minimal BFF 与 Full BFF 已复用；生产化 SDK 能力留到后续阶段。 | Plane-1 / Plane-2 | V3.5-D / D2 / F |
| Minimal BFF Smoke | V3.5-D2 已实现 platform-neutral FastAPI minimal smoke。 | 保持为 smoke artifact；V3.5-F Full BFF Template 已独立实现。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-D2 / F |
| TypeScript SDK | V3.5-E1 已实现 browser/Node typed core client 和 EventSource/fetch stream helper。 | React hooks 与 reference app 已复用 TS SDK；direct browser mode 仍限 dev/受限 token。 | Plane-0 / Plane-1 / Plane-2 | V3.5-E1 / E2 / I |
| React Hooks | V3.5-E2 已实现 session、turn、events、artifacts、jobs、approvals hooks。 | Reference app 已使用 hooks；hooks 不承担完整 AgentTalkWindow 状态机。 | Plane-0 / Plane-1 | V3.5-E2 / I |
| BFF Template | V3.5-F 已实现独立可复制 FastAPI template。 | Reference app 已复用 BFF-only 接入；optional Node template 可后置。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-F / I |
| Pack Template | V3.5-G 已落地平台中立模板与 dummy fixture。 | templates 目录只作为可复制模板；实例化 dummy pack 通过 external pack path 显式注入后可发现，含版本兼容字段和 loader-generated warnings。 | Plane-1 / Plane-5 | V3.5-G |
| Connector Template | V3.5-G 已落地 descriptor 模板与 dummy fixture。 | templates 目录只作为可复制模板；实例化 dummy connector 通过 external descriptor path 显式注入后可被 `connector.health` 消费，且 discovery 只读 descriptor.json。 | Plane-1 / Plane-6 | V3.5-G |
| Embed Contract | V3.5-H 已完成嵌入式 Agent 面板前置 contract。 | 静态 `EmbedDefinition`、运行时 `EmbedBootstrap`、allowed actions、event union、UI states 和 BFF bootstrap 示例。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-H |
| Reference App | V3.5-I 已完成平台中立外部 App 示例。 | SDK + BFF + hooks + dummy pack/connector reference app；frontend 默认只走 `/bff/*`，不依赖业务 reference paths。 | Plane-0 through Plane-6 | V3.5-I |
| Completion Evidence | `v3_5_completion_evidence_bundle.md` 已落地。 | 记录 V3.5 专项、全量 Python、TS SDK 和 reference frontend build 结果。 | Plane-0 through Plane-6 | V3.5-I closeout |

## 7. 阶段影响范围

| 阶段 | 目标 | 主要影响平面 | 不应影响 |
| --- | --- | --- | --- |
| V3.5-0 | Contract inventory、目录规划、SDK 默认面、legacy/debug blacklist。 | Plane-1 / Plane-2 | Core runtime behavior |
| V3.5-A | Protocol schema registry、event schema、error registry、`approval.respond` 幂等、`events.subscribe`。 | Plane-1 / Plane-2 | Domain Pack business logic |
| V3.5-B | local capability token、AppProfile auth fields、external transport guard、CORS/token/scope 联动。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | Connector implementation |
| V3.5-C | native EventSource、fetch stream、cursor replay、event channel、scope/token enforcement。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | RuntimeAdapter internals |
| V3.5-D | Python SDK MVP。 | Plane-1 / Plane-2 | Core Store |
| V3.5-D2 | Minimal BFF Smoke。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | Full BFF Template |
| V3.5-E1 | TypeScript SDK core client（已完成）。 | Plane-0 / Plane-1 / Plane-2 | Business pack implementation |
| V3.5-E2 | React hooks（已完成）。 | Plane-0 / Plane-1 | Protocol/EventBridge redesign |
| V3.5-F | BFF template（已完成）。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | Core schema |
| V3.5-G | Pack / Connector template（已完成）。 | Plane-1 / Plane-5 / Plane-6 | Core/Gateway business paths |
| V3.5-H | Embed contract（已完成）。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | Full AgentTalkWindow |
| V3.5-I | Reference app example（已完成）。 | Plane-0 through Plane-6 as validation path | Core modification |

## 8. Remaining P0 Before Formal Production External App Support

以下不是 V3.5 dev/local 完成缺口，而是把当前基线升级为生产级外部 App 支持前必须补的生产化事项：

- 企业级 auth/OAuth/SSO 与真实用户系统接入。
- 生产级 capability token 生命周期管理、轮换、撤销、审计和密钥托管。
- 跨 worker / 分布式 EventBridge 一致性、持久订阅恢复和容量控制。
- 生产级 BFF 部署样板、observability、rate limit、request audit 和 operator runbook。
- 生产级 SDK 发布流程、版本兼容策略和 generated SDK 管线。
- reference app deployment smoke、真实浏览器自动化和跨 origin 安全验收。
- Pack / Connector JSON Schema 发布和模板生成 CLI。
- AgentTalkWindow / Workflow Studio 的产品级 UI 和状态机，这些不属于 V3.5 完成条件。

## 9. P1 Parallel Improvements

- protocol version label 明确化。
- generated SDK strategy（E1 使用 snapshot，后续可演进为生成式 SDK）。
- Pack / Connector JSON Schema。
- `docs/integration/` 外部 App 接入手册。
- reference app deployment smoke。

## 10. Non-Goals

以下不作为 V3.5 gap：

- Core 重构。
- 业务 reference path 重迁移。
- sibling service 内部实现。
- 完整 Workflow Studio。
- 完整 AgentTalkWindow。

## 11. Challenge To Previous Gap Shape

旧 gap 结构的问题：

- 把历史路标放在主叙事里，削弱了 V3.5 当前目标。
- 沿用六大平面，无法表达新增的 Application Adaptation Layer。
- 把 Product UI / external app 与 Gateway 混在一起，导致 SDK/BFF/hooks/EventSource/token 的归属不清。
- 阶段影响范围过多指向 Core/Pack/Connector，容易误导为继续平台重构。

新的 gap 结构应以七层目标架构为主线，以 Plane-1 Application Adaptation Layer 为 V3.5 主工作面。
