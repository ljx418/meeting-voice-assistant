# harnessOS V4.0 Target Architecture: Workflow Console Platform

文档状态：V4.0 target architecture planning baseline；V3.6-J Dummy Pipeline E2E / V4.0 Gate 已通过，V4.0-Z Final Audit / Release Gate 已完成。本文定义 Workflow Console / Studio / AgentTalkWindow 目标架构，不代表 complete Workflow Studio、complete AgentTalkWindow、controlled executor ready、Agent executor ready、enterprise auth ready、OAuth ready、SSO ready、multi-tenant control plane ready 或 production-ready external app support。

当前进展、核心差距、阶段路线图和验收状态以 `v4_0_current_gap_analysis.md` 与 `v4_0_current_gap_analysis.drawio` 为最高优先级维护入口。本文只保留目标架构解释，不替代 gap 文件对。

## 1. 目标定义

V4.0 的目标不是单一新增一个视频产品，而是把 harnessOS 演进为：

> 可生成、可微调、可执行、可评估、可嵌套的 AI 工作流平台

平台需要同时支撑：

- Video Flow V2.0
- 个人应聘助手 V2.0
- 后续 Interview / Investment / Video / Knowledge 等 app
- 外部项目嵌入 harnessOS 工作流

V4.0 正式 UI 主开发不能直接从 mock schema 起步。它必须消费已经通过 V3.6-J gate 的 Workflow Runtime Contract、Pipeline Board API、WorkflowPatch、QualityEvaluation、Business Event 和 Dummy Pipeline E2E 结果。

截至 V4.0-Z，Workflow Console 已具备 read/event bridge、operation panels、browser smoke、governed editing hardening、canvas/Inspector patch proposal bridge、stateful Agent assistant baseline、Agent action proposal governance、AgentActionHandoff 到用户确认 operation panels 的安全交接、handoff lifecycle / audit / URL recovery / stale guard、operation evidence / governance review、canvas proposal workflow、AgentTalk interaction E2E、controlled executor design gate、production readiness preflight、production auth / tenant boundary follow-up design、token lifecycle design、secret management design、observability / audit retention design、external app onboarding design、production readiness consolidation gate、controlled executor implementation gate 和 final audit package。Agent 仍只是 proposal / handoff generator，不是 executor；Z 也不是 production auth、OAuth/SSO、tenant control plane、controlled executor 或 production-ready implementation。

## 2. 目标能力

### 2.1 Workflow Generation

用户输入自然语言目标，例如：

> 生成一个 AI 文生视频工作流，至少包含导演、脚本、分镜、剪辑工位，可生产 100s / 10 个镜头 / 多角色剧情一致的短剧。

系统自动生成：

- workflow descriptor
- agent descriptors
- skill / connector descriptors
- artifact contracts
- quality rules
- review board schema

### 2.2 Workflow Editing

用户在 Studio UI 中微调：

- 工位
- agent goal
- tool / skill / connector 绑定
- 产出合同
- 质量规则
- 审批与 review 流程

### 2.3 Workflow Execution

服务侧将编辑后的 workflow 编译为可执行图，并通过 harnessOS Runtime 执行：

- session / turn / job / trace / artifact
- connector submit / poll / collect
- governance / approval / retry

### 2.4 Quality Board

每个 workflow 都有质量看板，汇总：

- artifact completeness
- lineage completeness
- connector failures
- review scores
- policy violations
- cost / latency / token / media metrics

### 2.5 Nested HarnessOS

外部项目可以把某条 workflow 作为内嵌子系统使用：

- 自己的 UI 调用 harnessOS workflow
- 在自身产品界面嵌入工作流面板
- 把 harnessOS 当作 workflow engine / governance plane

## 3. V4 正式七平面基线

V4.0 的正式目标架构必须继承 V3.6 完成后的七平面基线。此前“六大平面”写法只是产品能力聚合视图，会把 V3.5 Application Adaptation Layer、V3.6 Workflow Runtime Layer、Harness Core、RuntimeAdapter / Governance 等边界压扁，不适合作为 gap 文档或正式架构主口径。

正式基线如下：

```text
Plane-0 Product UI / Workflow Studio / AgentTalkWindow
  Workflow Canvas / Quality Board / Project Console / Embedded Surface

Plane-1 Application Adaptation Layer
  V3.5 SDK / BFF / hooks / EventBridge / Embed Contract

Plane-2 Workflow Runtime Layer
  V3.6 workflow runtime RPC / board / patch / quality / context APIs
  WorkflowTemplate / WorkflowInstance / Station / StationRun / Board / Patch / Quality / Context

Plane-3 Harness Core
  Session / Turn / Job / Artifact / Approval / Trace / Policy / Scope / Memory / Retry

Plane-4 Runtime Adapter & Governance
  runtime adapters / agent runners / planner-executor / governed execution / secret hygiene

Plane-5 Domain Pack / Descriptor Plane
  app descriptors / workflow descriptors / agent descriptors / skill descriptors / quality descriptors
  domain packs / policy bundles / artifact kinds / versioning + compiler

Plane-6 Connector / Tool / Store / Asset Plane
  MCP / stdio / HTTP connectors / model APIs / media engines / search / storage / external asset services
```

六块能力域仍可用于产品讲解，但必须标注为 aggregated product view：

```text
Studio UI
Application Adaptation
Workflow Runtime
Execution / Governance
Descriptor / Pack
Connector / Asset
```

该聚合视图不能替代七平面作为正式目标架构，也不能用于新增绕过 V3.6 API 的 UI 专用后端通道。

## 4. 新增关键对象

### 4.1 Workflow Descriptor

最小字段建议：

- `workflow_id`
- `app_id`
- `version`
- `entry_nodes`
- `nodes`
- `edges`
- `artifact_contracts`
- `quality_rules`
- `execution_policy`
- `embedded_surface`

V3.6 将其中可执行的后端合同优先落成 WorkflowTemplate / WorkflowVersion / WorkflowInstance / Station / StationRun / ArtifactContract / QualityEvaluation / WorkflowPatch。V4.0 Studio UI 在正式开发时应消费这些合同，而不是引入 UI-only descriptor。

### 4.2 Agent Descriptor

最小字段建议：

- `agent_id`
- `role`
- `goal`
- `tool_refs`
- `skill_refs`
- `memory_scope`
- `handoff_targets`
- `quality_requirements`

### 4.3 Quality Board Descriptor

最小字段建议：

- `board_id`
- `artifact_checks`
- `review_checks`
- `connector_checks`
- `policy_checks`
- `score_model`
- `blocking_rules`

## 5. 典型调用链

### 5.1 用户生成工作流

```text
User Prompt
  -> Workflow Generator
  -> Workflow Descriptor Draft
  -> Agent / Skill / Connector Drafts
  -> Studio Console Review
  -> Saved Workflow Version
```

### 5.2 用户执行工作流

```text
Studio UI / Embedded UI
  -> V3.5 SDK / BFF / Hooks
  -> V3.6 Workflow Runtime APIs
  -> WorkflowInstance / StationRun / Board API
  -> Runtime adapters
  -> Connectors / models / asset services
  -> jobs / artifacts / traces / quality board
```

### 5.3 外部项目嵌套使用

```text
External Project UI / BFF
  -> V3.5 SDK / embedding API
  -> V3.6 workflow instance / board / patch APIs
  -> harnessOS execution + governance + quality board
  -> embedded result surface
```

## 6. 对业务目标的支撑

### 6.1 Video Flow V2.0

V4 应该正式支撑：

- Studio UI
- 视频 workflow 控制台
- 多工位 AI 角色
- 远端模型 / 渲染 connector 编排
- 视频资产 / 预览 / 输出管理
- 发布前 QA 看板

### 6.2 个人应聘助手 V2.0

V4 应该正式支撑：

- 简历分析 / JD 匹配 / 模拟面试 / 反馈建议等多 workflow
- 面试流程可编辑
- 面试评估质量看板
- 外部站点 / App 嵌入 interview workflow

### 6.3 自然语言生成工作流

V4 的核心能力之一就是：

- 用户说目标
- 平台生成 workflow / agents / skills / connectors / outputs / quality board
- 用户只需要微调

这要求 Studio Console 继续以 V3.6 Workflow Runtime Contract 作为后端事实源。

## 7. V4 相对 V3 的关键新增

V3 已有但尚未全部冻结为平台合同：

- multi-app Core 基础
- Pack / Connector / Runtime / Governance 基础能力
- meeting / knowledge / video_studio 业务样板与规划型 workflow

V4 必须新增：

- Workflow Descriptor Platform
- Agent Descriptor Platform
- Quality Board
- Workflow Generator
- Visual Workflow Console
- Nested HarnessOS Embedding APIs
- 更稳定的 SDK / schema registry

V4.0 正式实现建立在已经通过的 V3.6-J gate 之上。V3.6-J gate 包括 WorkflowTemplate / WorkflowInstance / Station / StationRun / Board API / Patch / Business Event / Quality Evaluation / Approval Point / Dummy Pipeline E2E。

## 8. 建议实施顺序

1. 以 V3.5 complete baseline 作为接入层基线。
2. 以 V3.6 complete baseline 作为 workflow runtime / pipeline operating model 后端基线。
3. V4.0-0 Baseline & UI Contract Sync：建立 UI contract map、No False Green 边界和 mock-to-real 对齐检查。
4. V4.0-A Workflow Console Read-only MVP：消费 Board / status / station output / EventBridge，先做只读流水线控制台。
5. V4.0-B Workflow Editing MVP：消费 WorkflowPatch / draft / publish 合同，支持受控编辑和 diff。
6. V4.0-C AgentTalkWindow Preparation：基于 Embed Contract、EventBridge、approval/context/patch 做前置 shell。
7. V4.0-D Quality / Approval / Context Panels：产品化质量、审批和上下文面板。
8. V4.0-E Reference Workflow Console E2E：用平台中立 workflow 验证 UI + BFF + SDK + V3.6 runtime。
9. V4.0-F Browser Smoke Baseline：用 Playwright + build 后 Vite preview 验证真实浏览器 open/select/render/approve/context/event refresh，且不直接调用 `/v1/rpc` 或 `/v1/events/subscribe`。
10. V4.0-G/H/I/J/K：完成 editing hardening、canvas-to-runtime bridge、AgentTalkWindow stateful assistant baseline、AgentTalk governance baseline 和 Agent action handoff baseline。
11. 后续如进入 controlled executor、完整 AgentTalkWindow 或 Video Flow V2.0 / Interview V2.0，必须单独立项并继续保持 No False Green。

## 9. V3.6 Baseline For Formal V4.0

V3.6-J 已通过，V4.0 可以进入正式开发计划。V4.0 UI Spike 仍允许存在，但只能用于探索交互，不得替代正式 V3.6 API：

- Workflow Studio wireframe。
- AgentTalkWindow shell。
- Station Board mock。
- Artifact Board mock。
- Quality Panel mock。
- Business Event mock。

Spike 禁止：

- 固化 mock schema 为正式协议。
- 新增 UI 专用后端旁路。
- 绕过 V3.6 API。
- 声明 Workflow Studio ready 或 AgentTalkWindow ready。

V4.0 当前可以声明：

```text
V4.0-L complete: Agent handoff lifecycle, audit, and recovery baseline ready for dev/local Workflow Console.
```

V4.0 当前仍不能声明：

```text
Workflow Studio ready
AgentTalkWindow ready
controlled executor ready
autonomous workflow editing ready
production workflow automation ready
distributed workflow engine ready
```
## V4.0-Z Final Audit Update

V4.0-Z closes the current V4.0 audit package at the design-gate level:

```text
V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.
```

This target architecture remains an implementation review input, not a production implementation claim. Production auth, tenant control plane, token lifecycle runtime, production secret manager, observability platform, audit export, external app production onboarding, controlled executor, Agent executor, complete Workflow Studio, and complete AgentTalkWindow remain future work.

No False Green: V4.0-Z 不能声明 production-ready external app support, enterprise auth ready, multi-tenant control plane ready, OAuth ready, SSO ready, controlled executor ready, Agent executor ready, autonomous workflow editing ready, complete Workflow Studio ready, complete AgentTalkWindow ready, or full low-code canvas editing ready.
