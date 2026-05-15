# V3.6 Architecture Baseline

文档状态：V3.6 complete architecture baseline with Dummy Pipeline E2E / V4.0 Gate。  
配套图：`v3_6_current_gap_analysis.drawio`。

## 1. Architecture Position

V3.6 的架构位置是 **Workflow Runtime Layer**，位于 V3.5 Application Adaptation Layer 与 harnessOS Core 之间：

```text
V4.0 Future UI / Workflow Studio / AgentTalkWindow
  -> V3.5 Application Adaptation Layer
  -> V3.6 Workflow Runtime Layer
  -> harnessOS Core
  -> Domain Packs / Connectors
```

V3.6 不替代 Core。它把 Core 已有的 Session、Turn、Job、Artifact、Approval、Trace、Policy 组织成“流水线工作流”。

## 2. Architecture Evolution

| 阶段 | 核心问题 | 结果 |
| --- | --- | --- |
| V3.5 | 外部业务 App 如何接入 harnessOS Core。 | SDK、BFF、hooks、EventBridge、templates、Embed、Reference App。 |
| V3.6 | 外部 App 接入后，如何定义、运行、追踪、重跑、评价和修改业务流水线。 | Workflow Runtime Contract 与 Pipeline Operating Model。 |
| V4.0 | 用户如何通过 UI 生成、编辑、观察和嵌入工作流。 | Workflow Studio、AgentTalkWindow、Station Board、Quality Board。 |

## 3. Target Planes

```text
Plane-0 V4.0 Future UI
  Workflow Studio / AgentTalkWindow / Station Board / Quality Panel

Plane-1 V3.5 Application Adaptation Layer
  SDK / BFF / React Hooks / EventBridge / Embed Contract

Plane-2 V3.6 Workflow Runtime Layer
  Template / Version / Instance / Station / StationRun / Board / Patch / Quality / Context

Plane-3 Harness Core
  Session / Turn / Job / Artifact / Approval / Trace / Policy / Scope

Plane-4 Runtime Adapter & Governance
  execution boundary / policy / approval / secret hygiene / trace

Plane-5 Domain Packs
  domain workflows / skills / artifact kinds / policy bundles

Plane-6 Connectors / Tools / Stores
  MCP / stdio / HTTP connectors / local stores / external services
```

V3.6 的主工作面是 Plane-2。它消费 Plane-3 到 Plane-6，并通过 Plane-1 向 Plane-0 提供稳定数据。

## 4. Runtime Responsibilities

| 组件 | 职责 | 不负责 |
| --- | --- | --- |
| WorkflowTemplate / Version | 描述可发布、可归档、可追踪版本的 workflow 合同。 | 不承载 UI 画布布局细节。 |
| WorkflowInstance | 表示一次 workflow 运行。 | 不替代 session/job storage。 |
| Station / StationRun | 表示流水线工位与单次工位执行。 | 不直接绕过 RuntimeAdapter 执行工具。 |
| ArtifactContract | 约束 station input/output artifacts。 | 不改变 artifact registry 主合同。 |
| QualityEvaluation | 绑定 station output 的质量评估结果。 | 不实现复杂 LLM 评审系统。 |
| Pipeline Board API | 给 UI 返回 station/job/artifact/approval/quality/trace summary。 | 不返回 raw token 或敏感 trace payload。 |
| WorkflowPatch | 支持 Agent propose patch、diff、apply to draft、publish version。 | 不允许 Agent 静默修改 published workflow。 |

当前 V3.6-J 已完成 Template / Draft / Version Service、deterministic dummy workflow runtime MVP、workflow-bound approval point、Station artifact contract / lineage binding、QualityEvaluation MVP、Pipeline Board Data API、Business Event Bridge / Workflow Context、Safe Workflow Patch Contract 和 platform-neutral Dummy Pipeline E2E。WorkflowInstance / StationRun 已可通过 RPC 创建和查询，StationRun 已绑定真实 JobRecord、ArtifactRecord、QualityEvaluation 和 trace；approval-required station 可进入 `waiting_approval` 并通过 `approval.respond` 推进或阻断；artifact lineage、board reconstruction、business context update、patch apply/publish V2、scope isolation、external auth smoke 和 redaction 已由 J 阶段端到端验证。

## 5. V4.0 Gate

V3.6-J 已完成，V4.0 可以进入正式 UI 主开发计划。正式 V4.0 UI 主开发必须继续消费以下后端事实源：

- WorkflowTemplate / WorkflowVersion
- WorkflowInstance / Station / StationRun
- ArtifactContract / QualityEvaluation
- Pipeline Board API
- Business Event / Workflow Context
- WorkflowPatch
- Dummy Pipeline E2E
