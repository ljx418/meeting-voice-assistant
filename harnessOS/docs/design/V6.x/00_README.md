# V6.x Design Index

文档状态：V6-6 complete / ready for review；V6-7 implementation NO-GO / planning refinement only。本文是 V6.x canonical index。

## Current V6 Baseline

```text
V5-8 complete: distributed multi-Agent runtime slice ready for review.
V5 remains bounded dev/local / staging / ready-for-review evidence.
V6-0 planning gate is complete / ready for review.
V6-0 external audit P0 closure is complete.
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
V6-3 complete: production observability and audit export pilot slice ready for review.
V6-4 complete: limited production controlled executor pilot slice ready for review.
V6-5 complete: governed Agent execution intent pilot gate ready for review.
V6-6 complete: production external app onboarding pilot slice ready for review.
V6-7 remains NO-GO for implementation until separate human high-risk proceed decision and detailed contract audit pass.
```

V6 不反向升级 V5 证据。V5-8 只证明 bounded distributed runtime slice ready for review，不证明完整生产级分布式多 Agent 运行时、Agent executor、production controlled executor、production-ready external app support 或 complete Workflow Studio。

## V6 Goal

V6 的目标是把 V5 的 core slice / staging slice / ready-for-review 证据推进到可审计的 production pilot baseline：

```text
Production identity and tenant boundary
Production credential and provider lifecycle
Production observability and audit export
Limited production controlled executor pilot
Governed Agent execution intent pilot gate
Production external app onboarding pilot
Distributed multi-Agent runtime productization pilot
Product Console pilot
Final production pilot acceptance
```

## Canonical Documents

| File | Purpose |
| --- | --- |
| `v6_target_prd.md` | V6 目标 PRD，定义生产试点体验、能力组和非目标。 |
| `v6_target_architecture.md` | V6 目标架构，定义生产平面和 runtime truth 边界。 |
| `v6_current_gap_analysis.md` | V6 当前 gap 分析，区分 V5 inherited、V6 planned、production blocker。 |
| `v6_current_gap_analysis.drawio` | V6 gap 图形版。 |
| `v6_development_and_acceptance_plan.md` | V6 开发与验收计划。 |
| `v6_acceptance_gate_matrix.md` | V6 阶段验收门槛矩阵。 |
| `v6_milestone_roadmap.md` | V6 里程碑路线图。 |
| `v6_no_false_green_claim_guard.md` | V6 禁止声明和 claim guard。 |
| `v6_planning_audit_for_chatgpt.md` | V6 规划审计包，供外部复核。 |
| `v6_1_identity_tenant_development_and_acceptance_plan.md` | V6-1 身份与租户控制面开发及验收计划。 |
| `v6_1_identity_tenant_prd.md` | V6-1 身份与租户控制面详细 PRD。 |
| `v6_1_identity_tenant_architecture_delta.md` | V6-1 架构增量设计。 |
| `v6_1_identity_tenant_ownership_model.md` | V6-1 ownership model。 |
| `v6_1_api_bff_route_design.md` | V6-1 API / BFF route design。 |
| `v6_1_audit_fields.md` | V6-1 审计字段合同。 |
| `v6_1_test_matrix.md` | V6-1 测试矩阵。 |
| `v6_1_pre_implementation_audit.md` | V6-1 实现前审计报告。 |
| `v6_2_credential_provider_development_and_acceptance_plan.md` | V6-2 凭证与模型供应商生命周期开发及验收计划。 |
| `v6_2_credential_provider_prd.md` | V6-2 凭证与供应商生命周期详细 PRD。 |
| `v6_2_credential_provider_architecture_delta.md` | V6-2 架构增量设计。 |
| `v6_2_credential_lease_model.md` | V6-2 CredentialLease 模型。 |
| `v6_2_audit_fields.md` | V6-2 审计字段合同。 |
| `v6_2_test_matrix.md` | V6-2 测试矩阵。 |
| `v6_2_pre_implementation_audit.md` | V6-2 实现前审计报告。 |
| `v6_3_observability_audit_development_and_acceptance_plan.md` | V6-3 观测与审计导出开发及验收计划。 |
| `v6_3_observability_audit_prd.md` | V6-3 观测与审计导出详细 PRD。 |
| `v6_3_observability_architecture_delta.md` | V6-3 架构增量设计。 |
| `v6_3_audit_export_model.md` | V6-3 审计导出模型。 |
| `v6_3_incident_timeline_model.md` | V6-3 incident timeline 模型。 |
| `v6_3_test_matrix.md` | V6-3 测试矩阵。 |
| `v6_3_pre_implementation_audit.md` | V6-3 实现前审计报告。 |
| `v6_3_observability_audit_completion_note.md` | V6-3 historical completion note；不是当前控制入口。 |
| `evidence/v6-3-observability-audit/` | V6-3 端到端验收证据包。 |
| `v6_4_controlled_executor_development_and_acceptance_plan.md` | V6-4 生产受控执行器开发及验收计划。 |
| `v6_4_controlled_executor_prd.md` | V6-4 生产受控执行器详细 PRD。 |
| `v6_4_controlled_executor_architecture_delta.md` | V6-4 架构增量设计。 |
| `v6_4_execution_contract_model.md` | V6-4 执行 envelope、result、evidence 合同。 |
| `v6_4_runtime_state_model.md` | V6-4 pilot runtime state 模型。 |
| `v6_4_action_allowlist_and_policy_matrix.md` | V6-4 action allowlist 和 policy matrix。 |
| `v6_4_test_matrix.md` | V6-4 测试矩阵。 |
| `v6_4_pre_implementation_audit.md` | V6-4 实现前审计报告。 |
| `v6_4_external_design_audit_closure.md` | V6-4 外部设计审计闭环说明。 |
| `evidence/v6-4-controlled-executor/pre-implementation-closure.json` | V6-4 NO-GO 闭环证据。 |
| `v6_4_controlled_executor_completion_note.md` | V6-4 completion note。 |
| `evidence/v6-4-controlled-executor/` | V6-4 端到端验收证据包。 |
| `v6_5_agent_governance_development_and_acceptance_plan.md` | V6-5 Agent 执行意图试点开发及验收计划。 |
| `v6_5_agent_governance_prd.md` | V6-5 Agent 执行意图详细 PRD。 |
| `v6_5_agent_governance_architecture_delta.md` | V6-5 Agent Governance 架构增量。 |
| `v6_5_agent_execution_intent_contract.md` | V6-5 AgentExecutionIntent / decision / handoff 合同。 |
| `v6_5_agent_policy_matrix.md` | V6-5 Agent intent 策略矩阵。 |
| `v6_5_minimax_intent_invocation_model.md` | V6-5 MiniMax intent 调用模型。 |
| `v6_5_test_matrix.md` | V6-5 测试矩阵。 |
| `v6_5_pre_implementation_audit.md` | V6-5 实现前审计；historical gate，已由 completion note 和 evidence package 闭环。 |
| `v6_5_agent_governance_completion_note.md` | V6-5 completion note。 |
| `evidence/v6-5-agent-governance/` | V6-5 端到端验收证据包。 |
| `v6_6_external_app_onboarding_development_and_acceptance_plan.md` | V6-6 生产外部应用接入开发及验收计划。 |
| `v6_6_external_app_onboarding_dto_contract.md` | V6-6 外部应用接入 DTO / schema 合同。 |
| `v6_6_external_app_onboarding_completion_note.md` | V6-6 completion note。 |
| `evidence/v6-6-external-app-onboarding/` | V6-6 端到端验收证据包。 |
| `v6_7_distributed_runtime_development_and_acceptance_plan.md` | V6-7 分布式多 Agent 运行时产品化开发及验收计划。 |
| `v6_7_distributed_runtime_prd.md` | V6-7 分布式运行时详细 PRD；当前 implementation NO-GO。 |
| `v6_7_target_architecture_delta.md` | V6-7 架构增量设计。 |
| `v6_7_distributed_run_coordinator_contract.md` | V6-7 DistributedRunCoordinator 合同。 |
| `v6_7_worker_assignment_policy.md` | V6-7 worker assignment policy。 |
| `v6_7_incident_timeline_contract.md` | V6-7 incident timeline 合同。 |
| `v6_7_no_false_green_guard.md` | V6-7 No False Green guard。 |
| `v6_8_product_console_development_and_acceptance_plan.md` | V6-8 产品控制台开发及验收计划。 |
| `v6_8_ui_bff_browser_safety_plan.md` | V6-8 UI / BFF / browser safety 计划。 |
| `v6_9_final_acceptance_development_and_acceptance_plan.md` | V6-9 最终生产试点验收计划。 |
| `v6_document_audit_report.md` | V6 文档审计报告。 |

## Historical Stage Notes

以下文档只记录旧阶段完成证据，不是当前控制入口：

```text
docs/design/V6.x/v6_0_production_pilot_planning_completion_note.md
docs/design/V6.x/v6_3_observability_audit_completion_note.md
```

## Allowed V6-0 Claim

```text
V6-0 complete: production pilot planning gate ready for review.
```

## Allowed V6-1 Claim

```text
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
```

## Allowed V6-2 Claim

```text
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
```

## Allowed V6-3 Claim

```text
V6-3 complete: production observability and audit export pilot slice ready for review.
```

## Allowed V6-4 Claim

```text
V6-4 complete: limited production controlled executor pilot slice ready for review.
```

## Allowed V6-5 Claim

```text
V6-5 complete: governed Agent execution intent pilot gate ready for review.
```

## Allowed V6-6 Claim

```text
V6-6 complete: production external app onboarding pilot slice ready for review.
```

## Forbidden Claims

```text
production-ready external app support
enterprise auth ready
multi-tenant control plane ready
Agent executor ready
controlled executor ready
production controlled executor ready
complete Workflow Studio ready
complete AgentTalkWindow ready
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous workflow editing ready
```

## Recommended Next Step

```text
Review V6-6 completion package and evidence package.
Continue V6-7 planning refinement only.
Do not enter V6-7 runtime implementation until a separate human high-risk proceed decision is recorded.
```

## Top 19 External Audit Paths

```text
docs/design/V6.x/00_README.md
docs/design/V6.x/v6_target_prd.md
docs/design/V6.x/v6_target_architecture.md
docs/design/V6.x/v6_current_gap_analysis.md
docs/design/V6.x/v6_current_gap_analysis.drawio
docs/design/V6.x/v6_development_and_acceptance_plan.md
docs/design/V6.x/v6_remaining_development_and_acceptance_plan.md
docs/design/V6.x/v6_no_false_green_claim_guard.md
docs/design/V6.x/v6_planning_audit_for_chatgpt.md
docs/design/V6.x/v6_6_external_app_onboarding_development_and_acceptance_plan.md
docs/design/V6.x/v6_6_external_app_onboarding_dto_contract.md
docs/design/V6.x/v6_7_distributed_runtime_development_and_acceptance_plan.md
docs/design/V6.x/v6_7_distributed_runtime_prd.md
docs/design/V6.x/v6_7_distributed_run_coordinator_contract.md
docs/design/V6.x/v6_7_no_false_green_guard.md
docs/design/V6.x/v6_8_product_console_development_and_acceptance_plan.md
docs/design/V6.x/v6_8_ui_bff_browser_safety_plan.md
docs/design/V6.x/v6_9_final_acceptance_development_and_acceptance_plan.md
docs/design/V6.x/evidence/v6-5-agent-governance/acceptance-data.json
```
