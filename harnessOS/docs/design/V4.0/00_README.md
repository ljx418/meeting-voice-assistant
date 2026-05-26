# harnessOS V4.0 Design Docs

文档状态：V4.0-Z complete；V4.0 final audit package ready for review。当前基于 V4.0-G governed editing hardening、V4.0-H canvas-to-runtime patch bridge、V4.0-I stateful Agent assistant baseline、V4.0-J AgentTalk governance baseline、V4.0-K Agent action handoff baseline、V4.0-L handoff lifecycle baseline、V4.0-M operation evidence baseline、V4.0-N canvas editing readiness baseline、V4.0-O governed canvas proposal workflow baseline、V4.0-P AgentTalkWindow interaction E2E baseline、V4.0-Q Controlled Executor Design Gate、V4.0-R Production Readiness Preflight、V4.0-S Production Auth / Tenant Boundary Follow-up Design、V4.0-T Token Lifecycle Design、V4.0-U Secret Management Design、V4.0-V Observability / Audit Retention Design、V4.0-W External App Onboarding Design、V4.0-X Production Readiness Consolidation Gate、V4.0-Y Controlled Executor Implementation Gate 和 V4.0-Z Final Audit / Release Gate。V3.6-J Dummy Pipeline E2E / V4.0 Gate 已通过，且 V3.6/V4.0 preflight hardening 已完成。最终允许声明为 `V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.`；这仍不代表完整 Workflow Studio、完整低代码编辑器、complete AgentTalkWindow、controlled executor、Agent executor、autonomous workflow editing、enterprise auth、多租户控制台、OAuth/SSO 或 production-ready external app support 已完成。

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
| `v4_0_workflow_studio_agent_copilot_prd.md` | CURRENT UX ACCEPTANCE BASELINE | Workflow Studio + Agent 工作流助手 v0.2 PRD；后续前端体验以“节点画布 + Agent 自然语言调整 + Patch/Diff 用户确认”为验收基线。 |
| `v4_0_e_reference_console_completion_note.md` | V4.0-E COMPLETION EVIDENCE | Reference Workflow Console E2E 的实现范围、测试证据、浏览器 smoke 降级说明和 No False Green 边界。 |
| `v4_0_f_browser_smoke_plan.md` | V4.0-F PLAN | Browser Smoke Baseline 的开发计划、验收标准、No False Green guard 和后续 G/H/I 路线。 |
| `v4_0_f_browser_smoke_completion_note.md` | V4.0-F COMPLETION EVIDENCE | Browser Smoke Baseline 的完成证据。 |
| `v4_0_g_editing_hardening_plan.md` | V4.0-G PLAN | Governed patch apply/reject/publish editing hardening 的开发计划和边界。 |
| `v4_0_g_editing_hardening_completion_note.md` | V4.0-G COMPLETION EVIDENCE | V4.0-G 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_h_canvas_runtime_bridge_plan.md` | V4.0-H PLAN | Canvas / Inspector intent 到 WorkflowPatch proposal 的桥接计划和边界。 |
| `v4_0_h_canvas_runtime_bridge_completion_note.md` | V4.0-H COMPLETION EVIDENCE | V4.0-H 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_i_agent_talk_window_stateful_plan.md` | V4.0-I PLAN | Governed stateful Agent assistant 的 BFF/UI 边界、action intent、capability profile 和测试计划。 |
| `v4_0_i_agent_talk_window_completion_note.md` | V4.0-I COMPLETION EVIDENCE | V4.0-I 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_j_agent_talk_governance_plan.md` | V4.0-J PLAN | AgentTalk governance / controlled action proposal baseline 的边界、policy class、BFF route 和测试计划。 |
| `v4_0_j_agent_talk_governance_completion_note.md` | V4.0-J COMPLETION EVIDENCE | V4.0-J 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_k_agent_action_handoff_plan.md` | V4.0-K PLAN | Agent action handoff 到用户确认 operation panels 的边界、DTO、BFF route 和测试计划。 |
| `v4_0_k_agent_action_handoff_completion_note.md` | V4.0-K COMPLETION EVIDENCE | V4.0-K 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_l_agent_handoff_lifecycle_plan.md` | V4.0-L PLAN | Agent handoff lifecycle、audit、recovery、stale/expired guard 的边界和测试计划。 |
| `v4_0_l_agent_handoff_lifecycle_completion_note.md` | V4.0-L COMPLETION EVIDENCE | V4.0-L 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_m_operation_evidence_plan.md` | V4.0-M PLAN | User-confirmed operation evidence 与 governance review baseline 的开发计划和边界。 |
| `v4_0_m_operation_evidence_completion_note.md` | V4.0-M COMPLETION EVIDENCE | V4.0-M 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_n_canvas_editing_readiness_plan.md` | V4.0-N PLAN | Canvas editing readiness baseline 的 controlled catalog、projection、node/edge/Inspector proposal 和 layout boundary 计划。 |
| `v4_0_n_canvas_editing_readiness_completion_note.md` | V4.0-N COMPLETION EVIDENCE | V4.0-N 的完成证据、测试结果和 No False Green 边界。 |
| `v4_0_o_governed_canvas_proposal_workflow_plan.md` | V4.0-O PLAN | V4.0-N 后的细化风险登记表，以及 governed canvas proposal workflow 的 patch queue、projection freshness、catalog versioning、Inspector/edge validation、fixture isolation 和文档审计计划。 |
| `v4_0_o_governed_canvas_proposal_workflow_completion_note.md` | V4.0-O COMPLETION EVIDENCE | V4.0-O 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_p_agenttalk_window_interaction_e2e_plan.md` | V4.0-P PLAN | V4.0-O 后的 AgentTalkWindow interaction E2E 计划，覆盖 explain/summarize/suggest/handoff/evidence review、event truth、fixture isolation 和 claim guard。 |
| `v4_0_p_agenttalk_window_interaction_e2e_completion_note.md` | V4.0-P COMPLETION EVIDENCE | V4.0-P 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_q_controlled_executor_design_gate_pre_review.md` | V4.0-Q PRE-REVIEW | V4.0-Q 阶段启动前的一份自包含审查文档，覆盖 P baseline、Q 边界、policy/capability/approval/sandbox/evidence 风险。 |
| `v4_0_q_controlled_executor_design_gate_plan.md` | V4.0-Q PLAN | Controlled Executor Design Gate 的实现计划；只做设计门禁，不实现 executor。 |
| `v4_0_q_controlled_executor_design_gate_contract.json` | V4.0-Q MACHINE-READABLE DESIGN CONTRACT | Q 阶段 policy matrix、capability profile、approval gate、sandbox boundary、rollback / kill switch 和 future evidence contract 的机器可读审计输入；不是运行时配置。 |
| `v4_0_q_controlled_executor_design_gate_completion_note.md` | V4.0-Q COMPLETION EVIDENCE | V4.0-Q 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_r_production_readiness_preflight_plan.md` | V4.0-R PLAN | Production Readiness Preflight 的计划；只登记生产化 gap，不实现 production-ready 能力。 |
| `v4_0_r_production_readiness_preflight_contract.json` | V4.0-R MACHINE-READABLE PREFLIGHT CONTRACT | R 阶段生产化 gap register、身份/租户字段、token lifecycle、secret hygiene、observability/audit 和 external app onboarding gap 的机器可读审计输入；不是运行时配置。 |
| `v4_0_r_production_readiness_preflight_completion_note.md` | V4.0-R COMPLETION EVIDENCE | V4.0-R 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_s_production_auth_tenant_boundary_design_plan.md` | V4.0-S PLAN | Production Auth / Tenant Boundary Follow-up Design 的计划；只做 auth/tenant 设计门禁，不实现 OAuth、SSO 或 tenant control plane。 |
| `v4_0_s_production_auth_tenant_boundary_design_contract.json` | V4.0-S MACHINE-READABLE DESIGN CONTRACT | S 阶段 identity matrix、tenant isolation matrix、service account / agent identity、OAuth / SSO gap 和 capability token binding 的机器可读审计输入；不是运行时配置。 |
| `v4_0_s_production_auth_tenant_boundary_design_completion_note.md` | V4.0-S COMPLETION EVIDENCE | V4.0-S 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_t_production_token_lifecycle_design_plan.md` | V4.0-T PLAN | Production Token Lifecycle Follow-up Design；只做 token lifecycle 设计门禁，不实现 token rotate/revoke/refresh/introspect。 |
| `v4_0_t_production_token_lifecycle_design_contract.json` | V4.0-T MACHINE-READABLE DESIGN CONTRACT | T 阶段 token lifecycle matrix、agent/executor boundary、event truth 和 redaction 的机器可读审计输入。 |
| `v4_0_t_production_token_lifecycle_design_completion_note.md` | V4.0-T COMPLETION EVIDENCE | V4.0-T 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_u_production_secret_management_design_plan.md` | V4.0-U PLAN | Production Secret Management Follow-up Design；只做 secret boundary 设计，不实现 production secret manager。 |
| `v4_0_u_production_secret_management_design_contract.json` | V4.0-U MACHINE-READABLE DESIGN CONTRACT | U 阶段 secret boundary matrix、sandbox boundary 和 event truth 的机器可读审计输入。 |
| `v4_0_u_production_secret_management_design_completion_note.md` | V4.0-U COMPLETION EVIDENCE | V4.0-U 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_v_production_observability_audit_retention_design_plan.md` | V4.0-V PLAN | Production Observability / Audit Retention Follow-up Design；只做 observability/audit gap 设计，不实现 audit export 或 observability platform。 |
| `v4_0_v_production_observability_audit_retention_design_contract.json` | V4.0-V MACHINE-READABLE DESIGN CONTRACT | V 阶段 observability gap matrix 和 evidence boundary 的机器可读审计输入。 |
| `v4_0_v_production_observability_audit_retention_design_completion_note.md` | V4.0-V COMPLETION EVIDENCE | V4.0-V 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_w_external_app_production_onboarding_design_plan.md` | V4.0-W PLAN | External App Production Onboarding Follow-up Design；只做 onboarding gap 设计，不实现 production customer onboarding。 |
| `v4_0_w_external_app_production_onboarding_design_contract.json` | V4.0-W MACHINE-READABLE DESIGN CONTRACT | W 阶段 external app onboarding gap matrix 和 dev/local boundary 的机器可读审计输入。 |
| `v4_0_w_external_app_production_onboarding_design_completion_note.md` | V4.0-W COMPLETION EVIDENCE | V4.0-W 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_x_production_readiness_consolidation_gate_plan.md` | V4.0-X PLAN | Production Readiness Consolidation Gate；聚合 R/S/T/U/V/W 设计门禁，只输出 implementation review gate。 |
| `v4_0_x_production_readiness_consolidation_gate_contract.json` | V4.0-X MACHINE-READABLE GATE CONTRACT | X 阶段 source contracts、blocking categories 和 consolidated result 的机器可读审计输入。 |
| `v4_0_x_production_readiness_consolidation_gate_completion_note.md` | V4.0-X COMPLETION EVIDENCE | V4.0-X 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_y_controlled_executor_implementation_gate_plan.md` | V4.0-Y PLAN | Controlled Executor Implementation Gate；只做 executor implementation 前置门禁，不实现 executor。 |
| `v4_0_y_controlled_executor_implementation_gate_contract.json` | V4.0-Y MACHINE-READABLE GATE CONTRACT | Y 阶段 executor implementation requirements、agent boundary 和 event truth 的机器可读审计输入。 |
| `v4_0_y_controlled_executor_implementation_gate_completion_note.md` | V4.0-Y COMPLETION EVIDENCE | V4.0-Y 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_z_final_audit_release_gate_plan.md` | V4.0-Z PLAN | Final Audit / Release Gate；聚合 V4.0-O 到 V4.0-Z 的最终审计包。 |
| `v4_0_z_final_audit_release_gate_contract.json` | V4.0-Z MACHINE-READABLE FINAL AUDIT CONTRACT | Z 阶段 final allowed claim、forbidden claims、stage claims 和 validation commands 的机器可读审计输入。 |
| `v4_0_z_final_audit_release_gate_completion_note.md` | V4.0-Z COMPLETION EVIDENCE | V4.0-Z 的实现证据、测试结果和 No False Green 边界。 |
| `v4_0_completion_audit_report.md` | CURRENT AUDIT REPORT | 当前 V3.5 / V3.6 / V4.0 完成情况审计报告，包含文档清单、测试证据、架构边界判断和下一步建议。 |

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
- Workflow Studio 页面已按 Stitch + PRD v0.2 方向完成低代码 shell refresh：顶部栏、左侧「节点库」、中央 VideoStudio 多节点画布、右侧默认展开的「Agent 工作流助手」、Patch Proposal / Diff 确认语义、底部运行观察面板；画布支持背景平移、节点拖动、缩放和折叠面板扩展。
- V4.0-A2 Real Data Bridge 已完成：`apps/api/routers/bff.py` 提供 structured BFF read/event routes，`apps/workflow-console` 默认通过 real BFF DTO hook 消费 board/status/output/artifact metadata/lineage；只有显式 `VITE_HARNESSOS_DEMO_MODE=true` 才使用 Demo / Fixture。
- V4.0-D Quality / Approval / Context Panels 已完成：Quality panel 保持 read-only，Approval panel 通过显式用户点击调用 workflow-bound `approval.respond`，Context panel 只允许受控写入 `context.business` 并支持 `business.event.emit`；BFF structured routes 返回 redacted DTO 并校验 instance-scoped resource ownership。
- V4.0-E Reference Workflow Console E2E 已完成 component-level + BFF integration E2E：平台中立 runtime fixture、BusinessEventBinding、后端 seeded patch diff、approval side-effect、context update、EventBridge refresh truth、DTO redaction 和 scope / ownership guard 均有测试覆盖。
- V4.0-F Browser Smoke Baseline 已完成：固定使用 Playwright + build 后 Vite preview，连接同一 test BFF / V3.6 runtime fixture，验证 open console、select instance、render board、approval respond、context update、可控 EventBridge refresh、no direct `/v1/*`、无 Demo / Fixture fallback 和 DOM redaction。
- V4.0-G Editing hardening 已完成：`workflow.patch.apply/reject` 和 `workflow.template.publish` 通过 BFF structured routes 接入，要求用户显式确认；高风险 patch 默认拒绝；Playwright editing smoke 覆盖 apply/publish browser path。
- V4.0-H Canvas-to-runtime bridge 已完成：节点库 click/drag、连线 proposal 和 Inspector 表单会转换为受控 WorkflowPatch proposal；仍不得直接写 Store 或 runtime 对象。
- V4.0-I AgentTalkWindow Stateful Assistant 已完成：Agent state 是 BFF/UI 层对象，deterministic suggestions 不调用外部 LLM，Agent 可以 propose patch 但不能 apply/reject/publish。
- V4.0-J AgentTalk Governance 已完成：Agent action proposal 是 BFF/UI 层对象，action policy guard 将 display/navigation/proposal/forbidden 分类，Agent 仍不是 executor。
- V4.0-K Agent Action Handoff 已完成：Agent action proposal 可以交接到 Editing / Approval / Context panels；handoff route 只创建 DTO，不执行 mutation；最终执行仍要求用户显式确认并复用 V4.0-G / V4.0-D 既有路径。
- V4.0-L Agent Handoff Lifecycle 已完成：handoff 使用 repository/store interface，支持 active/opened/used/dismissed/expired/stale/blocked lifecycle、lazy expiration、URL recovery、audit query 和 stale/blocked UI guard。
- V4.0-M Operation Evidence / Governance Review 已完成：用户确认后的 patch apply/reject、publish、approval.respond、context.update 和 business.event.emit 会生成 append-only operation evidence，Workflow Console 新增只读治理审计面板。
- V4.0-N Canvas Editing Readiness 已完成：controlled node catalog、CanvasDraftProjection、node/edge/Inspector proposal flow、edge validation、Inspector allowlist 和 layout boundary 已完成；Canvas 仍不是 runtime truth。
- V4.0-O Governed Canvas Proposal Workflow 已完成：PatchQueueDTO、projection freshness、catalog versioning、Inspector/edge validation、E2E fixture isolation、redaction/event truth 和声明审计风险已形成验证基线；仍不是完整 Workflow Studio 或 AgentTalkWindow。
- V4.0-P AgentTalkWindow Interaction E2E 已完成：AgentTalkInteractionState、explain/summarize read-only guard、suggest patch to handoff to panel、evidence review read-only、event refresh truth、multi-proposal stale guard、redaction 和 browser smoke 已形成验证基线；仍不引入 Agent executor。
- V4.0-Q Controlled Executor Design Gate 已完成：机器可读 policy matrix、capability profile、approval gate design、sandbox boundary、rollback / kill switch design、future executor evidence contract、event truth guard 和 claim guard 已形成审计门禁；仍不实现 controlled executor。
- V4.0-R Production Readiness Preflight 已完成：机器可读 production readiness gap register、auth/tenant boundary、token lifecycle、secret hygiene、observability/audit、external app production boundary、forbidden route scan 和 claim guard 已形成预检门禁；仍不实现 production-ready external app support。
- V4.0-S Production Auth / Tenant Boundary Follow-up Design 已完成：机器可读 identity matrix、tenant isolation matrix、service account / agent identity design、OAuth / SSO gap contract、capability token binding design、forbidden route scan 和 claim guard 已形成设计门禁；仍不实现 enterprise auth、OAuth、SSO、tenant control plane 或 production-ready external app support。
- V4.0-T/U/V/W 已完成 production follow-up design：token lifecycle、secret management、observability / audit retention、external app onboarding 均形成机器可读设计合同；仍不实现 production runtime。
- V4.0-X/Y/Z 已完成 consolidation / executor implementation gate / final audit：生产化 blocker 已聚合，controlled executor implementation 前置门禁已固化，最终允许声明为 `V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.`。

建议 V4.0 阶段拆分为：

| 阶段 | 目标 | 验收口径 |
| --- | --- | --- |
| V4.0-0 Baseline & UI Contract Sync | 以 V3.5/V3.6 completion evidence 作为产品层基线，锁定 UI 只能消费 V3.6 API。 | 已完成：V4.0 implementation baseline and UI contract map ready。 |
| V4.0-A Workflow Console Read-only MVP | 使用 `workflow.board.get`、`workflow.instance.status`、`station.output.list` 和 EventBridge 构建只读流水线控制台。 | 已完成：read-only console scaffold、BFF-only client、station/artifact/approval/quality/trace/event panels、redaction tests；已升级为画布优先 Workflow Studio Shell。 |
| V4.0-A2 Real Data Bridge | 补齐 V4.0-A 的真实 BFF read/event data bridge，不再让默认 shell 依赖 demoData。 | 已完成：BFF structured routes、V3.6 dummy fixture integration、EventBridge proxy、frontend real data hook、redaction/source scan tests。 |
| V4.0-B Workflow Editing MVP | 使用 `workflow.patch.propose/diff` 支撑受控建议与 Diff 展示；apply/reject/publish 后移到真实 editing E2E。 | B 阶段完成 preparation；G 阶段已补齐 governed apply/reject/publish。 |
| V4.0-C AgentTalkWindow Preparation | 基于 V3.5 Embed Contract、events、approval/context/patch 能力做 AgentTalkWindow 前置 shell。 | 已完成：fixture-first shell、event source 标识、patch propose/diff 展示、approval notice、只读 context summary；不声明完整 AgentTalkWindow。 |
| V4.0-D Quality / Approval / Context Panels | 产品化 QualityEvaluation、approval.respond、business event 和 workflow context 的查看与操作。 | 已完成：Quality read-only、workflow approval response、business context operation panels ready for dev/local Workflow Studio；不修改 V3.6 board contract，不把 UI state 写回 runtime 内部对象。 |
| V4.0-E Reference Workflow Console E2E | 用平台中立 workflow 验证 UI + BFF + SDK + V3.6 runtime 的端到端链路。 | 已完成 component-level + BFF integration E2E；未完成 browser-level smoke，因此声明为 integration baseline。 |
| V4.0-F Browser Smoke Baseline | 用 Playwright 补真实浏览器 smoke，验证当前 integration baseline 在 build + preview 环境中可打开、可操作、可刷新。 | 已完成：dev/local Workflow Console browser smoke baseline ready。 |
| V4.0-G Editing hardening | 接入 governed patch apply/reject/publish BFF/UI/browser smoke。 | 已完成：governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console。 |
| V4.0-H Canvas-to-runtime bridge | Node / Edge / Inspector intent 转换为 WorkflowPatch proposal，不直接写 draft/store/runtime。 | 已完成：canvas-to-runtime patch bridge ready for dev/local Workflow Console。 |
| V4.0-I AgentTalkWindow Stateful Assistant | BFF/UI 层 Agent session/message/suggestion baseline，非执行型 action intents，source=agent 只允许 propose。 | 已完成：governed stateful Agent assistant baseline ready for dev/local Workflow Console。 |
| V4.0-J AgentTalk Governance | BFF/UI 层 Agent action proposal queue、action policy guard、redacted audit baseline；不实现 executor。 | 已完成：AgentTalk governance and controlled action proposal baseline ready for dev/local Workflow Console。 |
| V4.0-K Agent Action Handoff | AgentActionProposal 安全交接到用户显式确认的 Editing / Approval / Context operation panels；不实现 executor。 | 已完成：Agent action handoff to user-confirmed operation panels ready for dev/local Workflow Console。 |
| V4.0-L Agent Handoff Lifecycle | AgentActionHandoff lifecycle、audit、URL recovery、stale/expired/blocked guard；不实现 executor。 | 已完成：Agent handoff lifecycle, audit, and recovery baseline ready for dev/local Workflow Console。 |
| V4.0-M Operation Evidence / Governance Review | 用户显式确认 operation 的 evidence 与只读治理审计基线。 | 已完成：user-confirmed operation evidence and governance review baseline ready for dev/local Workflow Console。 |
| V4.0-N Canvas Editing Readiness | controlled catalog、CanvasDraftProjection、node/edge/Inspector proposal 和 layout boundary；不实现完整低代码编辑器。 | 已完成：canvas editing readiness baseline ready for dev/local Workflow Console。 |
| V4.0-O Governed Canvas Proposal Workflow | patch queue、projection freshness、catalog versioning、Inspector/edge validation、proposal apply race hardening、fixture isolation 和风险声明审计。 | 已完成：governed canvas proposal workflow ready for expanded dev/local Workflow Console validation；不是完整 Workflow Studio 或 AgentTalkWindow。 |
| V4.0-P AgentTalkWindow Interaction E2E | Agent explain/summarize/suggest/handoff/evidence review 交互 E2E；event refresh truth；DOM redaction；browser smoke。 | 已完成：AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation；不是 complete AgentTalkWindow 或 Agent executor。 |
| V4.0-Q Controlled Executor Design Gate | 只做受控执行器设计门禁：policy、approval、capability、sandbox、audit、rollback、kill switch；不实现真实 executor。 | 已完成：controlled executor design gate ready for review；不声明 controlled executor ready。 |
| V4.0-R Production Readiness Preflight | 只做 production readiness 预检：auth/SSO/multi-tenant/control plane/observability/security hardening 差距清单和验收计划。 | 已完成：production readiness preflight ready for review；不声明 production-ready。 |
| V4.0-S Production Auth / Tenant Boundary Follow-up Design | 基于 R gap register 选择 Auth / Tenant Boundary 方向进入设计；仍不得实现 OAuth、SSO、tenant control plane 或 production-ready。 | 已完成：production auth and tenant boundary follow-up design ready for review；不声明 enterprise auth ready。 |
| V4.0-T Production Token Lifecycle Follow-up Design | 细化 token lifecycle production gaps。 | 已完成：production token lifecycle follow-up design ready for review；不实现 token lifecycle runtime。 |
| V4.0-U Production Secret Management Follow-up Design | 细化 secret boundary 和 future executor sandbox boundary。 | 已完成：production secret management follow-up design ready for review；不实现 production secret manager。 |
| V4.0-V Production Observability / Audit Retention Follow-up Design | 细化 observability、audit retention 和 export gaps。 | 已完成：production observability and audit retention follow-up design ready for review；不实现 observability platform 或 audit export。 |
| V4.0-W External App Production Onboarding Follow-up Design | 细化 app registration、domain verification、tenant provisioning、quota、offboarding 和 support runbook gaps。 | 已完成：external app production onboarding follow-up design ready for review；不实现 production onboarding。 |
| V4.0-X Production Readiness Consolidation Gate | 聚合 R/S/T/U/V/W production readiness blockers。 | 已完成：production readiness consolidation gate ready for implementation review；不声明 production-ready。 |
| V4.0-Y Controlled Executor Implementation Gate | 基于 Q/X 固化 executor implementation 前置门禁。 | 已完成：controlled executor implementation gate ready for review；不实现 controlled executor。 |
| V4.0-Z Final Audit / Release Gate | 聚合 V4.0-O 到 V4.0-Z 的 final audit package。 | 已完成：V4.0 final audit package ready for review；允许 V4.0 complete 的审计口径，但不声明 production-ready 或 executor ready。 |

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
- 在完整编辑器与 AgentTalkWindow 状态机完成前声明 Workflow Studio ready 或 AgentTalkWindow ready
