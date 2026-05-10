# V3.5 Current Gap Analysis

文档状态：V3.5 gap baseline。  
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

## 2. 当前状态

当前 harnessOS 已具备带约束启动 V3.5 的平台基础，但缺少外部业务 App 接入层。

当前事实：

- Protocol App Server 已有 JSON-RPC / HTTP / stdio 等基础入口。
- Core 已有 scope、job、artifact、trace、approval、pack、connector 等可消费对象。
- Pack / Connector / Job / Artifact / Governance 合同可作为适配层消费对象。
- 但目前没有正式 SDK、BFF template、browser event bridge、local capability token、schema registry、embed contract 和平台中立 reference app。

当前 V3.5 的核心缺口不是“平台能不能跑”，而是：

> 外部业务 App 如何通过稳定、安全、可治理的适配层调用 harnessOS。

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

目标状态必须满足：

- 外部 App 不直接访问 Core Store。
- 外部 App 不调用 legacy/debug API 作为默认路径。
- SDK/BFF 默认携带 scope。
- token 绑定 scope、origin、capabilities。
- browser event bridge 支持 native EventSource、fetch stream 和 replay cursor。
- Pack / Connector template 可以生成 registry 可发现的最小样例。
- 平台中立 reference app 能不改 Core 完成接入。

## 5. 开发计划摘要

### 5.1 当前项目开发到哪了

当前项目处于 **V3.5 Application Adaptation Layer 规划完成、尚未进入代码实施** 的状态。

已完成：

- V3.5 文档入口已建立。
- V3.5 当前 gap 已切换为七层目标架构。
- V3.5 阶段已拆分为 `V3.5-0` 到 `V3.5-I`。
- 已明确 V3.5 不重构 Core、不重迁移业务 reference paths、不实现完整 Workflow Studio、不实现完整 AgentTalkWindow。
- 已明确正式外部 App 接入前的 P0 条件：schema registry、capability token、native EventSource auth、fetch stream auth、`approval.respond` 幂等、`events.subscribe`、REST/BFF scope、legacy/debug denylist。

尚未开始代码实施：

- 未创建 SDK package。
- 未创建 BFF template。
- 未创建 EventSource endpoint。
- 未定义 native EventSource 的 cookie/signed URL 认证实现。
- 未实现 local capability token。
- 未实现 method/event/error schema registry。
- 未创建平台中立 reference app。

### 5.2 下一阶段需要开发什么

下一阶段应优先进入 `V3.5-0 -> V3.5-A -> V3.5-B -> V3.5-C`，原因是 SDK、BFF、hooks、Embed contract 都依赖这四项基础合同。

建议顺序：

1. `V3.5-0 Scaffolding & Contract Inventory`
   - 创建 `sdk/`、`templates/`、`examples/`、`docs/integration/` 基础结构。
   - 固化 SDK default / optional / forbidden method surface。
   - 梳理 event 和 error inventory。

2. `V3.5-A Protocol Schema Registry + Error Registry`
   - 实现 method schema registry。
   - 实现 event schema registry。
   - 实现 error registry。
   - 增加 `approval.respond` 并冻结幂等和错误语义。
   - 增加 `events.subscribe` protocol contract。
   - 确保 schema registry 成为 SDK/BFF 默认面的单一事实源。

3. `V3.5-B Auth / Capability Token MVP`
   - 实现 local capability token。
   - token 绑定 app scope、capabilities、origin。
   - AppProfile 增加 `allowed_origins/default_capabilities/embed_policy`。
   - 明确 dev mode 必须显式开启。

4. `V3.5-C Browser Event Bridge`
   - 实现 `GET /v1/events/subscribe`。
   - 支持 native EventSource mode：same-origin BFF cookie 或 short-lived signed subscription URL。
   - 支持 fetch stream mode：`Authorization: Bearer`。
   - 支持 turn/job/artifact/approval/trace events。
   - 支持 scope/token 校验。
   - 支持 `Last-Event-ID` 或 replay cursor。

这四步完成后，再进入 SDK/BFF/template/embed/reference app：

```text
V3.5-D Python SDK
V3.5-E1 TypeScript SDK core client
V3.5-E2 React hooks
V3.5-F BFF Template
V3.5-G Pack / Connector Template
V3.5-H Embed Contract
V3.5-I Reference App Example
```

### 5.3 最终要开发成什么样

V3.5 最终形态是一个可被外部业务 App 复用的 Application Adaptation Layer：

```text
External Business App
  -> TypeScript SDK / React hooks
  -> BFF template
  -> capability token + scope binding
  -> JSON-RPC / native EventSource / fetch stream
  -> harnessOS Core contracts
```

完成后应具备：

- 后端可以用 Python SDK 调用 harnessOS。
- 前端可以用 TypeScript SDK / React hooks 发起 turn、订阅 events、展示 jobs/artifacts/approvals。
- BFF template 可以作为外部 App 的安全代理层。
- Event bridge 可以让浏览器用 native EventSource 或 fetch stream 订阅事件。
- capability token 可以约束 app scope、origin 和 capabilities。
- Pack / Connector template 可以让新业务不改 Core 被发现。
- Embed contract 可以支撑未来 AgentTalkWindow。
- reference app 可以证明平台中立接入路径可行。

最终出门标准：

- 至少一个平台中立 reference app 不改 Core 完成接入。
- SDK/BFF/hooks/Event Bridge 均通过 contract tests。
- Auth/capability token 区分 dev/local-first 与 formal external app support。
- Pack / Connector template 可生成 registry 可发现的最小样例。
- Embed contract 能支撑未来嵌入式 Agent 面板。
- 默认平台回归保持绿灯。

## 6. Gap Matrix

| 缺口 | 当前状态 | 目标状态 | 主要影响平面 | 阶段 |
| --- | --- | --- | --- | --- |
| Scaffolding | 无 `sdk/`、`templates/`、`examples/`、`docs/integration/` 规划目录。 | 明确目录结构、contract inventory、legacy/debug blacklist。 | Plane-1 | V3.5-0 |
| Method Schema | `method.list` 仅返回 method/capability/alias/description。 | method params/result schema registry。 | Plane-1 / Plane-2 | V3.5-A |
| Event Schema | 事件可查询但无统一 schema registry。 | chat/job/artifact/approval/trace/business event schema。 | Plane-1 / Plane-2 / Plane-3 | V3.5-A |
| Error Registry | error code 仍主要由 handler 映射。 | 集中 error registry，供 SDK/BFF/tests 使用。 | Plane-1 / Plane-2 | V3.5-A |
| `approval.respond` | 当前 approve/reject 分离。 | protocol-level `approval.respond`，SDK/BFF 统一调用，幂等和错误码冻结。 | Plane-1 / Plane-2 / Plane-3 | V3.5-A |
| `events.subscribe` | 当前没有独立 subscription method。 | protocol-level subscription contract，返回 `eventsource_url/subscription_token/replay_cursor`。 | Plane-1 / Plane-2 | V3.5-A / C |
| Capability Token | 无 local capability token。 | token 绑定 app scope、capabilities、origin。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-B |
| AppProfile Auth Fields | AppProfile 缺少适配层可消费的 origin/capability/embed 字段。 | `allowed_origins/default_capabilities/embed_policy`。 | Plane-1 / Plane-3 | V3.5-B |
| REST Scope | REST run/stream 未完整暴露 scope。 | `/v1/runs` 与 `/v1/runs/stream` 如保留，必须支持 scope/token；REST 仅为 simple compatibility path。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-B / C |
| Browser Event Bridge | 只有 POST stream / persisted events，缺 native EventSource 认证设计。 | `GET /v1/events/subscribe`，支持 native EventSource cookie/signed URL、fetch bearer、scope/token/cursor/channel。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-C |
| Python SDK | 无 harnessOS Python SDK。 | typed Python client，覆盖 session/turn/events/artifact/job/approval/connector/pack。 | Plane-1 / Plane-2 | V3.5-D |
| TypeScript SDK | 无 TS SDK。 | browser/Node typed core client 和 EventSource/fetch stream helper。 | Plane-0 / Plane-1 / Plane-2 | V3.5-E1 |
| React Hooks | 无通用 hooks。 | session、turn、events、artifacts、jobs、approvals hooks，依赖 EventBridge 和 TS SDK core。 | Plane-0 / Plane-1 | V3.5-E2 |
| BFF Template | 无可复用 BFF template。 | FastAPI template，optional Node template，提供业务 identity 到 scope/capability token 的绑定样例。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-F |
| Pack Template | 有 pack 样例，但无平台中立模板。 | dummy pack template，不改 Core 可发现，含版本兼容字段和 warnings。 | Plane-1 / Plane-5 | V3.5-G |
| Connector Template | connector descriptor 主要由内置代码声明。 | dummy connector template，包含 health/capabilities/security/version compatibility。 | Plane-1 / Plane-6 | V3.5-G |
| Embed Contract | 无嵌入式 Agent 面板前置 contract。 | `EmbedDefinition` 和 event union。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | V3.5-H |
| Reference App | 无平台中立外部 App 示例。 | SDK + BFF + hooks + dummy pack/connector 或 generic workflow 的 reference app，不依赖 Meeting/Knowledge。 | Plane-0 through Plane-6 | V3.5-I |

## 7. 阶段影响范围

| 阶段 | 目标 | 主要影响平面 | 不应影响 |
| --- | --- | --- | --- |
| V3.5-0 | Contract inventory、目录规划、SDK 默认面、legacy/debug blacklist。 | Plane-1 / Plane-2 | Core runtime behavior |
| V3.5-A | Protocol schema registry、event schema、error registry、`approval.respond` 幂等、`events.subscribe`。 | Plane-1 / Plane-2 | Domain Pack business logic |
| V3.5-B | local capability token、AppProfile auth fields、CORS/token/scope 联动。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | Connector implementation |
| V3.5-C | native EventSource、fetch stream、cursor replay、event channel、scope/token enforcement。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | RuntimeAdapter internals |
| V3.5-D | Python SDK MVP。 | Plane-1 / Plane-2 | Core Store |
| V3.5-E1 | TypeScript SDK core client。 | Plane-0 / Plane-1 / Plane-2 | Business pack implementation |
| V3.5-E2 | React hooks。 | Plane-0 / Plane-1 | Protocol/EventBridge redesign |
| V3.5-F | BFF template。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | Core schema |
| V3.5-G | Pack / Connector template。 | Plane-1 / Plane-5 / Plane-6 | Core/Gateway business paths |
| V3.5-H | Embed contract。 | Plane-0 / Plane-1 / Plane-2 / Plane-3 | Full AgentTalkWindow |
| V3.5-I | Reference app example。 | Plane-0 through Plane-6 as validation path | Core modification |

## 8. P0 Before Formal External App Support

- method/event/error schema registry。
- `approval.respond` protocol method。
- `events.subscribe` protocol contract。
- local capability token。
- browser-friendly native EventSource and fetch stream。
- REST/BFF scope support。
- SDK/BFF legacy/debug denylist。

## 9. P1 Parallel Improvements

- protocol version label 明确化。
- generated SDK strategy。
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
