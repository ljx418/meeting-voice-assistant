# harnessOS V4.0 Design Docs

文档状态：V4.0-C complete + Workflow Studio low-code shell refresh；V3.6-J Dummy Pipeline E2E / V4.0 Gate 已通过，且 V3.6/V4.0 preflight hardening 已完成。当前下一阶段仍是 V4.0-D Quality / Approval / Context Panels。本文仍是设计入口，不代表完整 Workflow Studio、AgentTalkWindow 或 production external app support 已完成。

## Positioning

V4.0 不是继续堆单一业务，而是把 harnessOS 从 “多 app 共用 Core” 推进成：

> Workflow Descriptor Platform + Studio Console + Nested HarnessOS Runtime

V3.0 解决 Core、Pack、Connector、Governance 的稳定化；V3.5 解决外部 App 接入层；V3.6 负责把 workflow runtime 和 pipeline operating model 变成后端事实源。V4.0 才把这些底座产品化为：

- Studio UI
- Workflow Console
- Agent / Workflow / Skill / Connector Descriptor
- Quality Board
- Embedded / Nested HarnessOS

V4.0 的正式目标架构沿用 V3.6 完成后的七平面基线：

```text
Plane-0 Product UI / Workflow Studio / AgentTalkWindow
Plane-1 Application Adaptation Layer
Plane-2 Workflow Runtime Layer
Plane-3 Harness Core
Plane-4 Runtime Adapter & Governance
Plane-5 Domain Pack / Descriptor Plane
Plane-6 Connector / Tool / Store / Asset Plane
```

如果文档或图中为了产品讲解出现“Studio UI / Adaptation / Runtime / Execution / Descriptor / Connector”等六块能力域，必须标注为 aggregated product view，不能替代七平面正式基线。

## Documents

| 文件 | 状态 | 用途 |
| --- | --- | --- |
| `v4_0_current_gap_analysis.md` | CORE MAINTENANCE DOC | V4.0 当前差距、七平面目标架构、阶段路线图、P0/P1、出门标准；与同名 drawio 必须同步更新。 |
| `v4_0_current_gap_analysis.drawio` | CORE MAINTENANCE DIAGRAM | V4.0 gap 可视化图；必须与 `v4_0_current_gap_analysis.md` 保持一致。 |
| `v4_0_ui_contract_map.md` | V4.0-0 CONTRACT MAP | UI 区域、术语、state 分类、allowed RPC/event/BFF route 的分阶段映射。 |
| `v4_0_mock_to_real_contract_checklist.md` | V4.0-0 CHECKLIST | UI mock 字段到 V3.6 API / UI-only transient / future 的固定表结构。 |
| `v4_0_event_contract_map.md` | V4.0-0 EVENT MAP | V4.0 UI 可消费 live events、trace-only events、future events 的边界。 |
| `v4_0_frontend_stack_decision.md` | V4.0-0 DECISION | 冻结 V4.0 Workflow Console 主实现为 React + Vite，新建 `apps/workflow-console/`。 |
| `v4_0_stitch_prototype_mapping.md` | V4.0-0 PROTOTYPE MAP | Stitch 原型区域到 V3.6 API 或 UI-only transient state 的映射。 |
| `v4_target_architecture_workflow_console.md` | DRAFT TARGET ARCHITECTURE | V4.0 目标架构、控制台、嵌套调用和 descriptor 平台说明。 |
| `v4_0_workflow_studio_low_code_baseline.md` | DRAFT DEVELOPMENT BASELINE | 基于 Stitch 原型图的 V4.0 Workflow Studio / low-code UI 开发基线。 |

V4.0 正式开发必须继续参考以下基线：

| 文件 | 用途 |
| --- | --- |
| `../V3.6/00_README.md` | V3.6 Workflow Runtime Contract 阶段入口。 |
| `../V3.6/v3_6_current_gap_analysis.md` | V3.6 gap、V4.0 gate 和核心维护口径。 |
| `../V3.6/v3_6_acceptance_plan.md` | V3.6 出门标准。 |

## Core Maintenance Rule

从 V4.0 起，`v4_0_current_gap_analysis.md` 与 `v4_0_current_gap_analysis.drawio` 是本阶段最高优先级维护文件。每个 V4.0 开发阶段结束后，必须同步更新：

- 当前阶段状态。
- 七平面架构影响范围。
- 核心差距与已关闭差距。
- 下一阶段计划。
- P0/P1 风险。
- 验收证据与 No False Green 边界。

目标架构文档可以解释长期方向，但不能替代 gap 文件对作为项目进展入口。

## Scope

V4.0 主要关注：

- 用户自然语言生成工作流
- 用户可视化微调 workflow / agent / skill / quality rules
- 业务方把生成出的工作流嵌入自己的项目
- HarnessOS 作为工作流平台而不只是单一助手后端

## Current Plan

当前项目状态：

- V3.5 已冻结为 `V3.5 complete at dev/local Application Adaptation Layer level`。
- V3.6 已冻结为 `V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development`。
- V3.6/V4.0 preflight hardening 已完成：scope/capability/governance guard、platform startup neutrality、Reference App BFF structured path 和 V4.0 protocol naming 已完成收口。
- V4.0-0 Baseline & UI Contract Sync 已完成。
- V4.0-A Workflow Console Read-only MVP 已完成，新增 `apps/workflow-console/` React/Vite read-only console。
- V4.0-B Workflow Editing MVP 已重新收窄为 preparation shell：新增受控 patch diff / risk display，不暴露 apply / reject / publish 执行动作。
- V4.0-C AgentTalkWindow Preparation 已完成，新增 fixture-first AgentTalk preparation shell、事件时间线、patch 建议卡片、审批提醒、只读 context summary 和 embed boundary tests。
- Workflow Studio 页面已按 Stitch 方向完成低代码 shell refresh：顶部栏、左侧「节点库」、中央无限拖拽画布、右侧「节点配置 / Agent 助手」、底部运行观察面板；画布支持背景平移、节点拖动、缩放和折叠面板扩展。
- 当前下一阶段是 V4.0-D Quality / Approval / Context Panels。

建议 V4.0 阶段拆分为：

| 阶段 | 目标 | 验收口径 |
| --- | --- | --- |
| V4.0-0 Baseline & UI Contract Sync | 以 V3.5/V3.6 completion evidence 作为产品层基线，锁定 UI 只能消费 V3.6 API。 | 已完成：V4.0 implementation baseline and UI contract map ready。 |
| V4.0-A Workflow Console Read-only MVP | 使用 `workflow.board.get`、`workflow.instance.status`、`station.output.list` 和 EventBridge 构建只读流水线控制台。 | 已完成：read-only console scaffold、BFF-only client、station/artifact/approval/quality/trace/event panels、redaction tests；已升级为画布优先 Workflow Studio Shell。 |
| V4.0-B Workflow Editing MVP | 使用 `workflow.patch.propose/diff` 支撑受控建议与 Diff 展示；apply/reject/publish 后移到真实 editing E2E。 | 当前完成：patch diff panel、BFF structured propose/diff routes、高风险 patch 风险展示；不暴露 apply/reject/publish。 |
| V4.0-C AgentTalkWindow Preparation | 基于 V3.5 Embed Contract、events、approval/context/patch 能力做 AgentTalkWindow 前置 shell。 | 已完成：fixture-first shell、event source 标识、patch propose/diff 展示、approval notice、只读 context summary；不声明完整 AgentTalkWindow。 |
| V4.0-D Quality / Approval / Context Panels | 产品化 QualityEvaluation、approval.respond、business event 和 workflow context 的查看与操作。 | 不修改 V3.6 board contract，不把 UI state 写回 runtime 内部对象。 |
| V4.0-E Reference Workflow Console E2E | 用平台中立 workflow 验证 UI + BFF + SDK + V3.6 runtime 的端到端链路。 | 不依赖 Meeting / Knowledge / Video / external MCP，不声明 production-ready。 |

## V3.6 Gate

V3.6-J Dummy Pipeline E2E / V4.0 Gate 已通过。Gate 已验证：

- WorkflowTemplate / WorkflowVersion schema 冻结。
- WorkflowInstance / Station / StationRun 可运行和查询。
- StationRun 可绑定 Job / Artifact / Trace。
- Approval point 可触发 `approval.required` 并通过 `approval.respond` 继续。
- QualityEvaluation 可绑定 artifact / station_run。
- Pipeline Board API 可返回 station、job、artifact、approval、quality、trace summary。
- WorkflowPatch 只能 apply 到 draft，publish 生成新 version。
- 平台中立 dummy pipeline E2E 通过。

V4.0 仍可以做 UI Spike，但 Spike 不能替代正式 V3.6 API，不能固化 mock schema，不能新增 UI 专用后端旁路，不能绕过 V3.6 API。

## Non-Goals

以下内容不应在 V4 文档中被误写为“已实现”：

- 任意外部模型 / 视频引擎即插即用
- 全自动高质量剧情视频生成
- 完整多租户商业化权限系统
- 完整分布式调度 / GPU 资源编排
- 在 V4.0-E reference workflow console E2E 之前声明 Workflow Studio ready 或 AgentTalkWindow ready
