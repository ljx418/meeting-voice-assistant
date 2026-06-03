# V4.x 设计文档索引

文档状态：V4-U9 最终人工验收与 V5 移交包完成后的 Headless-first 路线索引。UX-01 到 UX-12 全部有可审计证据，最终人工验收入口和 V5 planning brief 已生成。

V4.x 不再把完整 Web 低代码 Workflow Studio 作为当前主线。新的前向路线已从“多 Head 输出”进一步收敛为统一体验：

```text
Headless Workflow Core
+ Interaction Orchestrator
+ Experience State Machine
+ Agent Policy Layer
+ Runtime Capability Matrix
+ Report Schema
+ Mission Console
+ Workflow Blueprint
+ Runtime Report
+ Review Console
+ Evidence Chain
```

## 当前前向 Gap 文档

| File | Purpose |
| --- | --- |
| `v4_x_headless_current_gap_analysis.md` | 当前 V4.x gap 分析、过度设计审计、虚假验收风险、V4.2-A 修正范围。 |
| `v4_x_headless_current_gap_analysis.drawio` | 当前 V4.x 图形版 gap 文档。V4.1 之后以前向规划应使用这张图。 |
| `v4_x_headless_first_roadmap.md` | V4.1 到 V4.6 的 Headless-first 路线图。 |
| `v4_x_headless_api_surface_map.md` | Headless command / spec / report surface 与 runtime truth boundary。 |
| `v4_x_tui_drawio_html_report_plan.md` | TUI、Drawio、HTML Report、Thin Web Console 的规划合同。 |
| `v4_x_unified_experience_prd.md` | V4.6 之后的统一体验 PRD。 |
| `v4_x_unified_development_plan.md` | V4-U0 到 V4-U6 的统一体验开发与验收计划。 |
| `v4_x_experience_state_machine.md` | Mission Console、Blueprint、Report、Review、Evidence 共享状态机。 |
| `v4_x_interaction_orchestrator_contract.md` | 多 Head 用户意图与可用动作合同。 |
| `v4_x_report_schema.md` | Drawio、HTML、TUI、Thin Web 共享报告投影合同。 |
| `v4_x_mission_console_prd.md` | Mission Console 主体验入口 PRD。 |
| `v4_x_unified_experience_acceptance.md` | 当前 canonical 验收矩阵，必须包含 UX-01 到 UX-12，且 UX-12 不得被旧 UX-01 到 UX-11 文档绕过。 |
| `v4_x_schema_audit_pack.md` | V4.x schema 严格性审计包。 |
| `v4_x_runtime_capability_matrix.md` | V4.x runtime capability 状态、证据和 false-green 风险矩阵。 |
| `v4_x_workflow_spec_registry.md` | WorkflowSpec Registry 边界说明，不替代 runtime truth。 |
| `v4_u5c_mission_console_closed_loop_plan.md` | Mission Console 闭环阶段计划。 |
| `v4_u5d_review_console_evidence_chain_plan.md` | Review Console 与 Evidence Chain 阶段计划。 |
| `v4_u5e_real_llm_local_document_workflow_plan.md` | 真实 LLM 本地技术文档工作流阶段计划。 |
| `v4_u5_scenario_path_acceptance_plan.md` | 场景路径验收包阶段计划。 |
| `v4_u5_scenario_path_acceptance_completion_note.md` | 场景路径验收包完成说明，记录 U6 暂停和 PARTIAL 风险。 |
| `v4_u6_unified_experience_gate_plan.md` | V4 统一体验收口门禁计划。 |
| `v4_u6_unified_experience_gate_completion_note.md` | V4-U6 完成说明，记录人工接受 PARTIAL 风险和最终门禁结果。 |
| `v4_u7_real_multi_agent_runtime_evidence_plan.md` | V4-U7 真实 provider-backed 多 Agent 场景证据计划。 |
| `v4_u7_real_multi_agent_runtime_evidence_completion_note.md` | V4-U7 完成说明，记录 UX-08/09/10 real_runtime 证据和 No False Green 结果。 |
| `v4_u8_v4_closure_manual_acceptance_plan.md` | V4-U8 收口与人工验收包计划。 |
| `v4_u8_v4_closure_manual_acceptance_completion_note.md` | V4-U8 完成说明，记录人工验收代理报告和收口边界。 |
| `v4_u9_final_human_acceptance_and_v5_handoff_plan.md` | V4-U9 最终人工验收与 V5 移交计划。 |
| `v4_u9_final_human_acceptance_and_v5_handoff_completion_note.md` | V4-U9 完成说明，记录最终人工验收报告、PRD 规格复核、false-green 审计和 V5 planning-only 交接。 |
| `v4_remaining_development_and_acceptance_plan.md` | V4-U9 后的剩余开发与验收计划；明确 V4 不再新增功能，只保留文档审计、人工验收、勘误修复和 V5 进入前门禁。 |
| `v4_remaining_development_audit_for_chatgpt.md` | 可交给 ChatGPT 复核的剩余开发审计包。 |
| `v4_r0_document_audit_freeze_completion_note.md` | V4-R0 文档审计与口径冻结完成说明。 |
| `v4_r1_human_acceptance_review_completion_note.md` | V4-R1 人工验收复核完成说明。 |
| `v4_r2_errata_fix_completion_note.md` | V4-R2 勘误修复门禁完成说明。 |
| `v4_r3_v5_entry_gate_completion_note.md` | V4-R3 V5 进入前门禁完成说明。 |
| `v4_final_human_acceptance_confirmation.md` | V4 最终人工验收确认，记录人工复核接受结论、R0/R1/R2/R3 closure gates 接受状态和 V5 planning-only 前提。 |
| `v4_target_architecture_after_u9.md` | V4-U9 后的目标架构冻结版；描述 Headless-first dev/local 架构与 runtime truth 边界。 |
| `v4_target_spec_prd_after_u9.md` | V4-U9 后的目标规格 PRD 冻结版；描述 UX-01 到 UX-12、产品规则、非目标和验收标准。 |
| `v4_target_acceptance_plan_after_u9.md` | V4-U9 后的目标验收计划冻结版；描述人工验收、自动验收命令和停止条件。 |
| `v4_document_review_for_chatgpt_after_u9.md` | 给 ChatGPT 的 V4-U9 后文档检视包。 |
| `../V5.x/v5_0_production_productization_planning_brief.md` | V5 production productization 前置规划 brief；不改变 V4 dev/local closure 边界。 |

旧的 `docs/design/V4.0/v4_0_current_gap_analysis.drawio` 现在只作为 V4.0 历史参考。后续 V4.x 规划应使用上面的 V4.x gap 文档对。

## 标记规则

```text
灰色【旧有不用改】：已经存在，并且当前 V4.x 阶段不需要改动。
黄色【旧有需改】：已经存在，但为了 V4.x 目标体验需要扩展、收敛或重构。
绿色【新增】：V4.x Headless-first 路线新增的组件、输出物或交互入口。
红色【禁止误报】：不得声明完成的能力或禁止路径。
```

黄色和绿色模块必须在标题下方标明负责阶段，例如 `【V4.2-A】`、`【V4.2-B/C】`、`【V4.3】`。每个阶段结束后同步更新 gap 文档时必须重新应用该涂色规则。

## 当前允许基线

```text
V4-U5A complete: scenario evidence archive ready for review.
V4-U5B complete: experience state projection read-model ready for shared workflow heads.
V4-U5C complete: Mission Console closed loop ready for dev/local validation.
V4-U5D complete: Review Console and Evidence Chain baseline ready for review.
V4-U5E complete: real LLM-backed local technical document workflow ready for dev/local validation.
V4-U5 complete: unified scenario path acceptance package ready for V4-U6 gate review.
V4-U6 complete: V4 unified dev/local experience baseline ready for review.
V4-U7 complete: real provider-backed multi-agent scenario evidence ready for review.
V4-U8 complete: V4 dev/local closure package ready for human acceptance.
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
V4-R0 complete: V4 documentation boundary frozen for human audit.
V4-R1 complete: V4 final human acceptance reviewed.
V4-R2 complete: V4 acceptance errata resolved without scope expansion.
V4-R3 complete: V4 closed and V5 entry gate ready for planning.
V4 final human acceptance confirmed: V4 feature development closed; V5 planning may proceed.
```

## 下一阶段

```text
V4-U9 is complete with final human acceptance and V5 handoff package. V4-R0/R1/R2/R3 closure gates are complete. 下一阶段建议进入 V5 planning，而不是继续把 production hardening 塞入 V4。禁止把 full multi-Agent orchestration, Agent executor, controlled executor, or production-ready external app support 视为已证明。
```

Unified Experience Rebaseline 只统一体验、合同、状态机、报告投影和验收证据；不新增 Agent executor、production controlled executor、production auth 或完整 Web Studio。

## No False Green

以下声明仍然禁止：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```
