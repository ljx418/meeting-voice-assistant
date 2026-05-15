# harnessOS V3.5 Design Docs

文档状态：V3.5-MVP complete；V3.5-E1 TypeScript SDK Core Client complete；V3.5-E2 React Hooks complete；V3.5-F Full BFF Template complete；V3.5-G Pack / Connector Template complete；V3.5-H Embed Contract complete；V3.5-I Reference App complete。V3.5 complete at dev/local Application Adaptation Layer level。

下一阶段：V3.6 规划位于 `../V3.6/`。V3.6 以 V3.5 为冻结基线，目标是 Workflow Runtime Contract & Pipeline Operating Model，不回写 V3.5 完成口径。

## Positioning

V3.5 的目标是在 Product UI / external business app 与 harnessOS Protocol App Server / Core 之间建立 Application Adaptation Layer。当前文档只描述 V3.5 规划和验收，不展开历史阶段实现细节。

```text
Product UI / External App
  -> V3.5 Application Adaptation Layer
      Python SDK
      TypeScript SDK core client
      React hooks
      App Gateway / BFF template
      Event bridge
      Pack / Connector template
      Embed contract
      Platform-neutral reference app
  -> harnessOS Protocol App Server
  -> Multi-App Core / RuntimeAdapter / Pack / Connector
```

## Documents

| 文件 | 用途 |
| --- | --- |
| `v3_5_starting_baseline.md` | V3.5 起点基线和当前缺失合同。 |
| `v3_5_architecture_baseline.md` | V3.5 在整体架构中的位置、边界和层次关系。 |
| `v3_5_current_gap_analysis.md` | V3.5 当前差距、七层目标架构、阶段影响范围；与同名 drawio 作为核心维护文件。 |
| `v3_5_current_gap_analysis.drawio` | V3.5 当前差距与目标架构图；必须与 `v3_5_current_gap_analysis.md` 同步。 |
| `v3_5_development_plan_application_adaptation_layer.md` | V3.5-0 到 V3.5-I 的阶段计划、PR 切片和排序建议。 |
| `v3_5_project_introduction_baseline.md` | 面向团队沟通的 V3.5 项目介绍基线。 |
| `v3_5_contract_inventory.md` | 当前 methods/events/errors 人类可读摘要；机器可读 source of truth 位于 `core/protocol/contracts/`。 |
| `v3_5_protocol_schema_registry_plan.md` | Protocol schema registry、event schema、error registry、`approval.respond`、`events.subscribe` 计划。 |
| `v3_5_auth_capability_token_plan.md` | local capability token、AppProfile auth fields、CORS/token/scope 联动计划。 |
| `v3_5_event_bridge_plan.md` | Native EventSource / fetch stream、event channel、cursor/replay 计划。 |
| `v3_5_sdk_plan.md` | Python SDK、TypeScript SDK core client、React hooks 的接口和测试计划。 |
| `v3_5_bff_template_plan.md` | FastAPI / optional Node BFF template 计划。 |
| `v3_5_pack_connector_template_plan.md` | Pack / Connector template 计划。 |
| `v3_5_embed_contract_plan.md` | EmbedDefinition 和 AgentTalkWindow 前置 contract 计划。 |
| `v3_5_reference_app_plan.md` | reference app example 计划。 |
| `v3_5_acceptance_plan.md` | V3.5 分阶段验收计划和出门标准。 |
| `v3_5_completion_evidence_bundle.md` | V3.5 dev/local completion 的测试、实现、文档同步证据包。 |
| `diagrams/01_v3_5_application_adaptation_layer_baseline.drawio` | V3.5 应用适配层基线图。 |

## Baseline Rules

- 历史平台能力只作为 V3.5 起点，不再作为 V3.5 完成条件重复验收。
- 业务 reference paths 不能进入 SDK/BFF 默认模板。
- Phase0 机器可读 inventory 是 exposure inventory 和阶段状态 source of truth。
- V3.5-A `core/protocol/schemas/` 是 params/result/event/error schema source of truth。
- V3.5-B `core/protocol/auth/` 与 `apps/api/auth.py` 是 local capability token、method capability resolver 和 external transport auth guard 的实现入口。
- Phase0 scaffold 只允许 README/.gitkeep 和基线文档，不提供可 import 的正式 SDK API。
- V3.5 不能引入新的 Core 重构目标。
- V3.5 若发现必须修改 Core/Gateway 才能接入新 app，应记录为平台缺口，而不是把业务旁路固化为适配层能力。
- V3.5-MVP 已完成：当前已具备 protocol schema registry、`approval.respond` 幂等、local capability token、browser event bridge local runtime、Python SDK MVP、Minimal BFF Smoke，以及 SDK+BFF+EventBridge 端到端 smoke。
- V3.5-E1 TypeScript SDK Core Client 已完成：当前已具备 browser/Node typed core client、native EventSource helper、fetch stream helper、scope、typed errors 和 default wrapper tests。
- V3.5-E2 React Hooks 已完成：当前已具备 session、turn、events、artifacts、jobs、approvals hooks，且 core TS SDK import 不强制依赖 React。
- V3.5-F Full BFF Template 已完成：当前已具备独立可复制 FastAPI BFF template、BFF-side CapabilityPolicy、constrained RPC、structured routes、EventSource proxy、config safety 和 secret hygiene tests。
- V3.5-G Pack / Connector Template 已完成：templates 目录只提供可复制模板，不是 runtime instances；被 registry 发现的只能是显式 external path / descriptor path 注入的实例化 pack/connector。
- V3.5-H Embed Contract 已完成：拆分静态 `EmbedDefinition` 与运行时 `EmbedBootstrap`，定义 allowed actions、event union、UI states、BFF bootstrap 示例和平台中立 fixture。
- V3.5-I Reference App 已完成：reference frontend 默认只调用 `/bff/*`，使用 BFF-local EventSource proxy，不依赖业务 reference pack 或 legacy RPC，并覆盖 approval、artifact、job、trace summary、pack/connector、scope isolation 和 redaction smoke。
- 当前只能声明 `V3.5 complete at dev/local Application Adaptation Layer level`。这不代表 production-ready external app support、完整 AgentTalkWindow、完整 Workflow Studio、enterprise auth/OAuth/SSO ready 或 multi-tenant production control plane ready。

## Implementation Order

V3.5 分为 MVP 和 Full 两段推进。

V3.5-MVP：

1. `V3.5-0` Contract inventory and scaffolding.
2. `V3.5-A` Protocol schema registry and error registry.
3. `V3.5-B` Auth / local capability token.
4. `V3.5-C` Browser Event Bridge.
5. `V3.5-D` Python SDK.
6. `V3.5-D2` Minimal BFF Smoke.

V3.5-Full：

7. `V3.5-E1` TypeScript SDK core client.
8. `V3.5-E2` React hooks.
9. `V3.5-F` Full App Gateway / BFF template.
10. `V3.5-G` Pack / Connector template.
11. `V3.5-H` Embed contract.
12. `V3.5-I` Reference app example.

MVP 当前可声明 `V3.5-MVP dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke`。Full 已完成 reference app、TS SDK/hooks、Full BFF template、templates 和 embed contract，因此当前可声明 `V3.5 complete at dev/local Application Adaptation Layer level`。

Phase0 完成后只能声明 `V3.5 implementation ready`。Phase0 不改变 supported public API，不让 SDK 可用，也不让 external app ready。

V3.5-A 完成后只能声明 `protocol schema and approval response contract ready`。V3.5-A 不代表 MVP complete、SDK usable、external app ready，也不代表 `events.subscribe` runtime ready。

V3.5-B 完成后只能声明 `local capability token and external auth contract ready`。V3.5-B 不代表 MVP complete、SDK usable、external app ready 或 production-ready auth。

V3.5-C 完成后只能声明 `browser event bridge contract and local runtime ready`。V3.5-C 不实现完整 event bus，不保证多 worker / 分布式实时事件一致性，也不代表 SDK usable、external app ready 或 V3.5-MVP complete。

V3.5-D 完成后只能声明 `Python SDK MVP usable for local/backend integration smoke`。V3.5-D 的 SDK runtime 不 import server internals，不代表 SDK production-ready、external app ready 或 V3.5-MVP complete。

V3.5-D2 完成后可以声明 `Minimal BFF Smoke proves JSON-RPC and EventSource proxy feasibility`。当前新增 MVP E2E 覆盖真实 Minimal BFF + 真实 Python SDK + harnessOS ASGI/TestClient transport 后，可以声明 `V3.5-MVP dev/local adaptation layer ready with end-to-end SDK+BFF+EventBridge smoke`。这仍不代表 production-ready external app support、Full BFF Template complete、external app ready 或 V3.5 complete。

V3.5-E1 完成后只能声明 `TypeScript SDK core client ready for dev/local protocol integration smoke`。E1 不代表 React hooks ready、external app ready、production-ready browser integration 或 V3.5 complete。

V3.5-E2 完成后只能声明 `React hooks ready for dev/local UI integration smoke`。E2 不代表 external app ready、production-ready browser integration、AgentTalkWindow ready、Workflow Studio ready 或 V3.5 complete。

V3.5-F 完成时只能声明 `Full BFF Template ready for dev/local external app integration smoke`。F 当时不代表 production-ready external app support、AgentTalkWindow ready、Workflow Studio ready、Pack/Connector template complete、Reference app complete 或 V3.5 complete。

V3.5-G 完成时只能声明 `Pack / Connector templates ready for dev/local external app integration scaffolding`。G 当时不代表 Reference App complete、Embed Contract complete、production-ready external app support 或 V3.5 complete。

V3.5-H 完成后只能声明 `Embed contract ready for dev/local AgentTalkWindow preparation`。H 不代表 AgentTalkWindow ready、Workflow Studio ready、external app ready 或 V3.5 complete。

V3.5-I 完成后，如果 V3.5-0 到 H 的回归保持绿灯，可以声明 `V3.5 complete at dev/local Application Adaptation Layer level`。I 仍不能声明 production-ready external app support、complete AgentTalkWindow、complete Workflow Studio、enterprise auth/OAuth/SSO ready 或 multi-tenant production control plane ready。
