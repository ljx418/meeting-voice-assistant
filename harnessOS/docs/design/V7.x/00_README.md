# V7.x Design Index

文档状态：V7 planning package / document-only stage。本文是 V7.x canonical index。

## Current Baseline

V7 继承 V6 的最终收口口径：

```text
V6 complete: production pilot baseline ready for review.
```

V6 不是 production ready、full production GA、complete Workflow Studio、Agent executor、production controlled executor、production-ready external app support 或 full multi-Agent orchestration ready。

该 baseline 已被接受用于 V7 planning，但只能解释为：

```text
V6 生产试点基线 ready for review。
```

## Audit Opinion Reconciliation

外部审计曾要求：V7-0 只有在 Small Studio DTO/schema、Mission TUI command contract、Experience State Line、TUI screen layout、WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain link contract、Evidence package schema、test matrix、claim scan 和 redaction scan 全部完成并验收后，才允许声明：

```text
V7-0 complete: V7 small studio and explainable TUI planning gate ready for review.
```

当前仓库已经具备对应合同、schema、证据包和测试覆盖，因此 V7-0 可以保持 `complete / ready for review`。该声明仍只代表 planning gate 完成，不代表 V7-1 / V7-2 / V7-3 自动完成，也不代表 production ready。

V7 文档必须继续保留以下 V6 baseline evidence facts：

```text
V6 final acceptance status=PASS
stage_count=9
claim_scan=PASS
redaction_scan=PASS
drawio_xml=PASS
blockers=0
production_ready=false
full_production_ga=false
agent_executor_ready=false
production_controlled_executor_ready=false
complete_workflow_studio_ready=false
production_ready_external_app_support=false
full_multi_agent_orchestration_ready=false
distributed_multi_agent_runtime_ready=false
autonomous_workflow_editing_ready=false
```

Baseline evidence is summarized in:

```text
docs/design/V7.x/v7_v6_baseline_evidence.md
```

Canonical source evidence is:

```text
docs/design/V6.x/evidence/v6-9-final-acceptance/final-acceptance-data.json
docs/design/V6.x/evidence/v6-9-final-acceptance/result-summary.md
docs/design/V6.x/evidence/v6-9-final-acceptance/claims-scan.md
docs/design/V6.x/evidence/v6-9-final-acceptance/redaction-scan.md
docs/design/V6.x/v6_final_completion_note.md
```

## V7 Goal

V7 的目标是把 V6 的 production pilot baseline 推进为两个协同方向：

```text
Small Studio Production Pilot
+ Explainable Mission TUI / Product Console Experience
```

也就是：

```text
小型工作室可用的生产试点控制面
+ 可解释的自然语言工作流创建、确认、运行、审计体验
```

## Canonical Documents

| File | Purpose |
| --- | --- |
| `v7_target_prd.md` | V7 总 PRD，定义小型工作室和可解释 TUI 体验目标。 |
| `v7_target_architecture.md` | V7 目标架构，定义控制面、TUI、运行时、报告和审计关系。 |
| `v7_current_gap_analysis.md` | V6 到 V7 的 gap 分析。 |
| `v7_current_gap_analysis.drawio` | V7 中文项目规划图。 |
| `v7_development_and_acceptance_plan.md` | V7 开发与验收总计划。 |
| `v7_acceptance_gate_matrix.md` | V7 阶段验收门槛矩阵。 |
| `v7_milestone_roadmap.md` | V7 项目里程碑、剩余 blocker 和出门条件。 |
| `v7_no_false_green_claim_guard.md` | V7 禁止声明与误报扫描规则。 |
| `v7_planning_audit_for_chatgpt.md` | 给 ChatGPT / 外部审计的审计入口。 |
| `v7_v6_baseline_evidence.md` | V6 baseline 证据索引，回应 V7 基线质疑。 |
| `v7_0_planning_gate.md` | V7-0 文档冻结与实现前门禁。 |
| `v7_1_small_studio_control_plane_prd.md` | V7-1 小型工作室控制面 PRD。 |
| `v7_1_small_studio_architecture_delta.md` | V7-1 架构增量。 |
| `v7_1_small_studio_development_and_acceptance_plan.md` | V7-1 开发及验收计划。 |
| `v7_2_explainable_mission_tui_prd.md` | V7-2 可解释 Mission TUI PRD。 |
| `v7_2_explainable_mission_tui_architecture_delta.md` | V7-2 TUI 架构增量。 |
| `v7_2_explainable_mission_tui_development_and_acceptance_plan.md` | V7-2 开发及验收计划。 |
| `v7_2_explainable_mission_tui_completion_note.md` | V7-2 完成声明和证据索引。 |
| `v7_3_pre_implementation_review.md` | V7-3 实现前 PRD/spec 审计与 Go/No-Go 口径。 |
| `v7_3_io_contracts_and_schemas.md` | V7-3 自然语言、WorkflowSpec、Diff、Blueprint、handoff、report、evidence I/O 合同。 |
| `v7_3_real_data_acceptance_plan.md` | V7-3 真实数据验收、provider-backed 证据、fallback/BLOCKED 规则。 |
| `v7_3_schema_manifest_and_examples.md` | V7-3 schema manifest、生成物文件合同和 PASS/BLOCKED/fallback 示例。 |
| `v7_3_workflow_creation_run_experience_plan.md` | V7-3 自然语言创建和运行体验计划。 |
| `v7_3_workflow_creation_run_completion_note.md` | V7-3 完成声明、真实运行证据和 No False Green 口径。 |
| `v7_4_final_acceptance_data_contract.md` | V7-4 最终验收数据合同和 HTML 看板字段。 |
| `v7_4_final_small_studio_acceptance_plan.md` | V7-4 最终小型工作室验收计划。 |
| `v7_4_final_acceptance_completion_note.md` | V7-4 最终验收完成声明和 V7 收口口径。 |

## Stage Order

```text
V7-0 Planning Hardening Gate
 -> V7-1 Small Studio Production Pilot Control Plane
 -> V7-2 Explainable Mission TUI
 -> V7-3 Workflow Creation And Run Experience
 -> V7-4 Final Small Studio Acceptance
```

## Current Go / No-Go

| Area | Decision | Reason |
| --- | --- | --- |
| V6 baseline for V7 planning | GO | V6-9 evidence supports `production pilot baseline ready for review` only. |
| V7-0 | COMPLETE / READY FOR REVIEW | Planning contracts, schemas, test matrix and evidence package passed local audit. |
| V7-1 | COMPLETE / READY FOR REVIEW | Small Studio repo-backed control-plane projection and evidence package passed local audit. |
| V7-2 | COMPLETE / READY FOR REVIEW | Explainable Mission TUI transcript-only pilot and evidence package passed local audit. |
| V7-3 | COMPLETE / READY FOR REVIEW | Natural-language local Markdown workflow creation and controlled run evidence passed with real_runtime_fixture scope. |
| V7-4 | COMPLETE / READY FOR REVIEW | Final acceptance package passed; V7 complete claim is allowed with bounded ready-for-review wording. |

## Allowed Claims

```text
V7-0 complete: V7 small studio and explainable TUI planning gate ready for review.
V7-1 complete: small studio production pilot control plane ready for review.
V7-2 complete: explainable Mission TUI pilot ready for review.
V7-3 complete: natural-language workflow creation and controlled run experience ready for review.
V7 complete: small studio production pilot and explainable TUI baseline ready for review.
```

## Forbidden Claims

```text
production ready
full production GA
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous workflow editing ready
```

## Recommended External Audit Paths

```text
docs/design/V7.x/00_README.md
docs/design/V7.x/v7_target_prd.md
docs/design/V7.x/v7_target_architecture.md
docs/design/V7.x/v7_current_gap_analysis.md
docs/design/V7.x/v7_current_gap_analysis.drawio
docs/design/V7.x/v7_development_and_acceptance_plan.md
docs/design/V7.x/v7_acceptance_gate_matrix.md
docs/design/V7.x/v7_milestone_roadmap.md
docs/design/V7.x/v7_no_false_green_claim_guard.md
docs/design/V7.x/v7_planning_audit_for_chatgpt.md
docs/design/V7.x/v7_v6_baseline_evidence.md
docs/design/V7.x/v7_3_pre_implementation_review.md
docs/design/V7.x/v7_3_io_contracts_and_schemas.md
docs/design/V7.x/v7_3_real_data_acceptance_plan.md
docs/design/V7.x/v7_3_schema_manifest_and_examples.md
docs/design/V7.x/v7_3_workflow_creation_run_experience_plan.md
docs/design/V7.x/v7_4_final_acceptance_data_contract.md
docs/design/V7.x/v7_4_final_small_studio_acceptance_plan.md
```

## Current Documentation Readiness

```text
ready_for_external_planning_audit: true
ready_for_direct_full_v7_implementation: false
current_stage: V7-2 complete / ready for review
v7_0_complete: true
v7_1_complete: true
v7_2_complete: true
required_next_step: external audit of V7-3/V7-4 remaining contracts and V7-3 implementation readiness
```

V7-0 已补齐 DTO/schema、CLI/TUI 命令合同、证据包数据结构、测试矩阵和 claim/redaction scan 规则。V7-1 已完成 repo-backed Small Studio 投影。V7-2 已完成 transcript-only Explainable Mission TUI。V7-3 可进入 external implementation-readiness audit；当前已补齐实现前审计、I/O 合同、schema files 和真实数据验收计划，但进入实质开发前仍必须通过外部审计且无新增 P0/P1 规格偏差。
