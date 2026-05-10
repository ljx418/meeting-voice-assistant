# harnessOS Target Architecture V3.0

文档状态：V3.0 CLOSEOUT TARGET ARCHITECTURE。V2 目标架构文档已归档到 `docs/history/v2-phase-docs/architecture/harnessos_target_architecture_v2.md`。

## 1. 定位

V3.0 的正式目标架构是：

> Multi-App Harness Core + Pack Assembly + Connector Registry + Governed Runtime Adapter

harnessOS 不再按单一业务应用演进。Meeting、Knowledge、Interview、Investment、Video Studio 都必须通过 AppProfile + Pack + Connector + RuntimeAdapter 复用同一份 Core。Meeting / Knowledge 在 V3.0 中只是 reference packs / validation samples，不代表平台长期内置业务边界。

补充图解说明：

- `docs/design/V3.0/video-flow-plane-call-relations_v3.md`：用 `video_studio` 例子说明六大平面的实际调用关系，以及对 V1/V2/V4 目标的支撑边界。

## 2. 目标分层

V3.0 仍保留全项目六大平面视野，但当前 active overlay 收敛在 multi-app Core、Pack Assembly、Connector Registry、Job/Artifact/Governance、Meeting/Knowledge reference pack validation。已经相对完备或只需小修的平面标为 stable，当前重点硬化标为 active，远期能力标为 deferred。

```text
Plane-1 Client / Gateway Plane [stable]
  CLI / Headless / FastAPI / SSE / JSON-RPC / stdio JSONL
  meeting UI / knowledge UI / future app UI

Plane-2 Protocol App Server Plane [active]
  JSON-RPC / SSE / stdio JSONL / Web Gateway
  protocol version / method registry / event registry / error registry

Plane-3 Harness Core Plane [active]
  AppProfile / AppRegistry / ScopeContext
  app_id / project_id / workspace_id
  Session / Thread / Turn / Item
  Job / Artifact / Trace / Approval / Retry
  Policy / Secret Hygiene / Store / Protocol Registry

Plane-4 Runtime Adapter Plane [active]
  OpenHarness Adapter / SimpleRuntime Adapter / Future Adapter
  Default Governance Injection

Plane-5 Domain Pack Plane [active]
  Pack Manifest / PackAssemblyResult
  Meeting Pack / Knowledge Pack current reference samples
  Interview / Investment / Video Studio deferred

Plane-6 Connector / Tool / Store Plane [active]
  Meeting MCP / Knowledge MCP / FunASR MCP / Data Service MCP
  ConnectorRegistry security descriptor
  SQLite Store / future pluggable stores
```

状态说明：

- stable：已具备可用 MVP，V3.0 只做兼容和回归保护。
- active：V3.0-PhaseA 到 V3.0-PhaseE 的主要改动面。
- deferred：保留目标架构位置，但不进入当前验收。

## 3. 多态运行规则

- AppProfile 决定 app scope、enabled packs、enabled connectors、runtime adapter、policy profile。
- Pack 只声明业务装配，不拥有 Core 状态模型。
- Connector 只提供外部能力边界，不拥有 policy authority。
- RuntimeAdapter 是唯一执行入口，默认注入 scope、policy、approval、trace、secret hygiene。
- Job 和 Artifact 是跨 app 复用的 Core 对象，但必须受 ScopeContext 隔离。
- reference pack 的存在不得要求 Core / Gateway 为其保留长期业务特判。

## 4. V3.0 当前交付边界

包含：

- Multi-app scope 一等化。
- PackAssemblyResult 合同。
- ConnectorRegistry 与 Connector Security Model。
- Job Worker MVP。
- Artifact external asset / metadata-only / large file protection。
- Meeting reference pack validation。
- Knowledge reference pack validation。

不包含：

- Low-Code Workflow Runtime。
- Core Memory System。
- Feedback Optimization Loop。
- Workflow Library。
- Distributed queue / GPU scheduler。
