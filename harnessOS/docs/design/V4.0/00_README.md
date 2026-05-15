# harnessOS V4.0 Design Docs

文档状态：V4.0 planning entrypoint；V3.6-J Dummy Pipeline E2E / V4.0 Gate 已通过，且 V3.6/V4.0 preflight hardening 已完成。V4.0-0 正式开发在本次 hardening 前被暂停；恢复 V4.0-0 前必须以 V3.6 gap 文档和同名 drawio 的最新实现口径为 baseline。本文仍是设计入口，不代表 Workflow Studio、AgentTalkWindow 或 production external app support 已完成。

## Positioning

V4.0 不是继续堆单一业务，而是把 harnessOS 从 “多 app 共用 Core” 推进成：

> Workflow Descriptor Platform + Studio Console + Nested HarnessOS Runtime

V3.0 解决 Core、Pack、Connector、Governance 的稳定化；V3.5 解决外部 App 接入层；V3.6 负责把 workflow runtime 和 pipeline operating model 变成后端事实源。V4.0 才把这些底座产品化为：

- Studio UI
- Workflow Console
- Agent / Workflow / Skill / Connector Descriptor
- Quality Board
- Embedded / Nested HarnessOS

## Documents

| 文件 | 状态 | 用途 |
| --- | --- | --- |
| `v4_target_architecture_workflow_console.md` | DRAFT TARGET ARCHITECTURE | V4.0 目标架构、控制台、嵌套调用和 descriptor 平台说明。 |
| `v4_target_architecture_workflow_console.drawio` | DRAFT TARGET DIAGRAM | V4.0 目标架构图。 |

V4.0 正式开发必须继续参考以下基线：

| 文件 | 用途 |
| --- | --- |
| `../V3.6/00_README.md` | V3.6 Workflow Runtime Contract 阶段入口。 |
| `../V3.6/v3_6_current_gap_analysis.md` | V3.6 gap、V4.0 gate 和核心维护口径。 |
| `../V3.6/v3_6_acceptance_plan.md` | V3.6 出门标准。 |

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
- 当前下一阶段仍需先确认 V4.0-0 baseline，之后才进入 Workflow Console / Studio / AgentTalkWindow 相关产品层开发计划。

建议 V4.0 阶段拆分为：

| 阶段 | 目标 | 验收口径 |
| --- | --- | --- |
| V4.0-0 Baseline & UI Contract Sync | 以 V3.5/V3.6 completion evidence 作为产品层基线，锁定 UI 只能消费 V3.6 API。 | V4.0 文档、contract map、No False Green 边界同步完成。 |
| V4.0-A Workflow Console Read-only MVP | 使用 `workflow.board.get`、`workflow.instance.status`、`station.output.list` 和 EventBridge 构建只读流水线控制台。 | 不直接读 store，不新增 UI 专用后端旁路，可展示 station/job/artifact/approval/quality/trace summary。 |
| V4.0-B Workflow Editing MVP | 使用 `workflow.patch.propose/diff/apply/reject` 和 `workflow.template.publish` 支撑受控编辑。 | patch 只作用于 draft，agent 只能 propose/diff，published version 不被静默修改。 |
| V4.0-C AgentTalkWindow Preparation | 基于 V3.5 Embed Contract、events、approval/context/patch 能力做 AgentTalkWindow 前置 shell。 | 不声明完整 AgentTalkWindow，不绕过 BFF / SDK / EventBridge。 |
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
