# V6 Development And Acceptance Plan

文档状态：V6 complete / ready for review。本文定义 V6 开发和验收门禁。

## 1. Stage Status Table

| Stage | Purpose | Implementation Status | Allowed Claim | Boundary |
| --- | --- | --- | --- | --- |
| V6-0 | Production Pilot Planning Gate | complete / ready for review | V6-0 complete: production pilot planning gate ready for review. | planning only |
| V6-1 | Identity And Tenant Control Plane | complete / ready for review | V6-1 complete: production identity and tenant boundary pilot slice ready for review. | not enterprise auth ready |
| V6-2 | Credential And Provider Lifecycle | complete / ready for review | V6-2 complete: production credential and provider lifecycle pilot slice ready for review. | not production secret lifecycle ready |
| V6-3 | Observability And Audit Export | complete / ready for review | V6-3 complete: production observability and audit export pilot slice ready for review. | not production audit export ready |
| V6-4 | Production Controlled Executor Runtime | complete / ready for review | V6-4 complete: limited production controlled executor pilot slice ready for review. | not production controlled executor ready |
| V6-5 | Governed Agent Execution Intent Pilot | complete / ready for review | V6-5 complete: governed Agent execution intent pilot gate ready for review. | not Agent executor ready |
| V6-6 | Production External App Onboarding | complete / ready for review | V6-6 complete: production external app onboarding pilot slice ready for review. | not production-ready external app support |
| V6-7 | Distributed Runtime Productization | complete / ready for review | V6-7 complete: distributed multi-Agent runtime productization pilot slice ready for review. | not full multi-Agent orchestration ready |
| V6-8 | Product Console And Studio Gate | complete / ready for review | V6-8 complete: product console pilot slice ready for review. | not complete Workflow Studio ready |
| V6-9 | Final Production Pilot Acceptance | complete / ready for review | V6 complete: production pilot baseline ready for review. | not full production GA |

## 2. Development Order

```text
V6-0 -> V6-1 -> V6-2 -> V6-3 -> V6-4 -> V6-5 -> V6-6 -> V6-7 -> V6-8 -> V6-9
```

V6-5 已在人工 high-risk proceed decision 后完成。V6-6 已完成外部应用接入 pilot slice。V6-7 已在单独人工 high-risk proceed decision 后完成分布式运行时产品化 pilot slice。V6-8 已完成 Product Console / Thin Web Console pilot slice。

当前文档开发结论：

```text
V6 canonical PRD / architecture / milestone / acceptance / gap drawio must reflect V6 complete / ready for review.
V6-8 remains Product Console / Thin Web Console scope unless separate Full Workflow Studio PRD passes.
Document updates may refine wording, evidence links, diagrams, milestones and acceptance gates.
V6-9 final acceptance has passed with V6-0 through V6-8 evidence packages present and No False Green / redaction / drawio validation pass.
```

## 2.1 Stage Detail Plans

```text
V6-1: v6_1_identity_tenant_development_and_acceptance_plan.md
  detail docs: v6_1_identity_tenant_prd.md, v6_1_identity_tenant_architecture_delta.md, v6_1_identity_tenant_ownership_model.md, v6_1_api_bff_route_design.md, v6_1_audit_fields.md, v6_1_test_matrix.md, v6_1_pre_implementation_audit.md
V6-2: v6_2_credential_provider_development_and_acceptance_plan.md
  detail docs: v6_2_credential_provider_prd.md, v6_2_credential_provider_architecture_delta.md, v6_2_credential_lease_model.md, v6_2_audit_fields.md, v6_2_test_matrix.md, v6_2_pre_implementation_audit.md
V6-3: v6_3_observability_audit_development_and_acceptance_plan.md
  detail docs: v6_3_observability_audit_prd.md, v6_3_observability_architecture_delta.md, v6_3_audit_export_model.md, v6_3_incident_timeline_model.md, v6_3_test_matrix.md, v6_3_pre_implementation_audit.md
V6-4: v6_4_controlled_executor_development_and_acceptance_plan.md
  detail docs: v6_4_controlled_executor_prd.md, v6_4_controlled_executor_architecture_delta.md, v6_4_execution_contract_model.md, v6_4_runtime_state_model.md, v6_4_action_allowlist_and_policy_matrix.md, v6_4_test_matrix.md, v6_4_pre_implementation_audit.md
V6-5: v6_5_agent_governance_development_and_acceptance_plan.md
V6-6: v6_6_external_app_onboarding_development_and_acceptance_plan.md
  detail docs: v6_6_external_app_onboarding_dto_contract.md, v6_6_external_app_onboarding_completion_note.md, schemas/v6_6_*.schema.json, evidence/v6-6-external-app-onboarding/
V6-7: v6_7_distributed_runtime_development_and_acceptance_plan.md
  detail docs: v6_7_distributed_runtime_prd.md, v6_7_target_architecture_delta.md, v6_7_pre_implementation_closure_plan.md, v6_7_distributed_run_coordinator_contract.md, v6_7_runtime_io_contract.md, v6_7_distributed_runtime_state_machine.md, v6_7_worker_lifecycle_model.md, v6_7_worker_assignment_policy.md, v6_7_failure_recovery_acceptance_matrix.md, v6_7_incident_timeline_contract.md, v6_7_no_false_green_guard.md, v6_7_distributed_runtime_completion_note.md, schemas/v6_7_*.json, evidence/v6-7-distributed-runtime/
V6-8: v6_8_product_console_development_and_acceptance_plan.md
  detail docs: v6_8_ui_bff_browser_safety_plan.md, v6_8_product_console_bff_contract.md, v6_8_browser_safety_test_matrix.md, v6_8_manual_confirmation_ux_contract.md, v6_8_product_console_completion_note.md, evidence/v6-8-product-console/
V6-9: v6_9_final_acceptance_development_and_acceptance_plan.md
  detail docs: v6_9_final_acceptance_evidence_inventory_plan.md, v6_9_no_false_green_and_redaction_scan_plan.md, v6_final_completion_note.md, evidence/v6-9-final-acceptance/
```

V6-5 到 V6-9 的统一剩余开发控制计划：

```text
v6_remaining_development_and_acceptance_plan.md
```

## 3. Stage Acceptance Rules

每个阶段必须：

```text
run focused V6 tests
run V5 regression
run V4-U9 regression
validate V6 gap drawio XML
produce evidence package
run claim scan
run redaction scan when sensitive fields are involved
perform PRD spec review
perform False Green evaluation
record next stage audit
```

## 4. Evidence Package Layout

```text
docs/design/V6.x/evidence/v6-N-stage-name/
  index.html
  result-summary.md
  acceptance-data.json
  claims-scan.md
  logs/
  screenshots/
  raw/
```

## 5. Global Validation Commands

```text
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V6.x/v6_current_gap_analysis.drawio
```

Frontend-related stages also run:

```text
cd apps/workflow-console && npm test -- --runInBand
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
```

## 6. Stop Conditions

停止并回到规划审计：

```text
V6 docs upgrade V5 evidence to production-ready
V6-0 P0 closure evidence is missing
V5-8 handoff evidence is missing or only a document claim
source=agent receives direct durable mutation
raw secret / raw prompt / raw artifact content leaks
controlled executor bypasses confirmation / approval / kill switch
external app bypasses tenant / credential / quota boundary
distributed worker bypasses tenant / credential / policy boundary
Evidence Chain or Runtime Report constructs runtime truth
Full Web Studio becomes default V6 prerequisite
No False Green claim scan fails
```
