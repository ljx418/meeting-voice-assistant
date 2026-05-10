# harnessOS V3.5 Design Docs

文档状态：V3.5 planning entrypoint。本文档集用于指导 Application Adaptation Layer 的 dev/local-first 实施。

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
| `v3_5_contract_inventory.md` | 当前 methods/events/errors 盘点、SDK 默认面和 legacy/debug blacklist。 |
| `v3_5_protocol_schema_registry_plan.md` | Protocol schema registry、event schema、error registry、`approval.respond`、`events.subscribe` 计划。 |
| `v3_5_auth_capability_token_plan.md` | local capability token、AppProfile auth fields、CORS/token/scope 联动计划。 |
| `v3_5_event_bridge_plan.md` | Native EventSource / fetch stream、event channel、cursor/replay 计划。 |
| `v3_5_sdk_plan.md` | Python SDK、TypeScript SDK core client、React hooks 的接口和测试计划。 |
| `v3_5_bff_template_plan.md` | FastAPI / optional Node BFF template 计划。 |
| `v3_5_pack_connector_template_plan.md` | Pack / Connector template 计划。 |
| `v3_5_embed_contract_plan.md` | EmbedDefinition 和 AgentTalkWindow 前置 contract 计划。 |
| `v3_5_reference_app_plan.md` | reference app example 计划。 |
| `v3_5_acceptance_plan.md` | V3.5 分阶段验收计划和出门标准。 |
| `diagrams/01_v3_5_application_adaptation_layer_baseline.drawio` | V3.5 应用适配层基线图。 |

## Baseline Rules

- 历史平台能力只作为 V3.5 起点，不再作为 V3.5 完成条件重复验收。
- 业务 reference paths 不能进入 SDK/BFF 默认模板。
- V3.5 不能引入新的 Core 重构目标。
- V3.5 若发现必须修改 Core/Gateway 才能接入新 app，应记录为平台缺口，而不是把业务旁路固化为适配层能力。
- V3.5 早期是 dev/local-first；正式外部 App 接入前必须补齐 protocol schema registry、auth/capability token、native EventSource / fetch stream、`approval.respond` 幂等、REST scope 支持。

## Implementation Order

1. `V3.5-0` Contract inventory and scaffolding plan.
2. `V3.5-A` Protocol schema registry and error registry.
3. `V3.5-B` Auth / local capability token.
4. `V3.5-C` Browser Event Bridge.
5. `V3.5-D` Python SDK.
6. `V3.5-E1` TypeScript SDK core client.
7. `V3.5-E2` React hooks.
8. `V3.5-F` App Gateway / BFF template.
9. `V3.5-G/H` Pack / Connector template and Embed contract.
10. `V3.5-I` Reference app example.
