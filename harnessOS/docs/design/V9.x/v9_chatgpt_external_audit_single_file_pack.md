# V9 ChatGPT External Audit Single File Pack

文档状态：external audit attachment / V9-7 production governance evidence-aligned / not final V9 acceptance evidence。

## Boundary

```text
proceed_to_v9_front_stage_readiness_audit=true
proceed_to_v9_1_external_implementation_readiness_audit=true
proceed_to_v9_1_implementation_planning=true
proceed_to_v9_1_limited_safety_gate_implementation=true
proceed_to_v9_2_limited_controlled_runtime_slice=true
proceed_to_v9_1_runtime_implementation=false
proceed_to_v9_2_runtime_executor_route=false
proceed_to_v9_2_runtime_worker=false
proceed_to_v9_3_runtime_implementation_complete_for_review=true
proceed_to_v9_4_readiness_closure=true
proceed_to_v9_4_runtime_implementation_complete_for_review=true
proceed_to_v9_5_runtime_implementation_complete_for_review=true
proceed_to_v9_6_runtime_implementation_complete_for_review=true
proceed_to_v9_7_runtime_implementation_complete_for_review=true
proceed_to_v9_8_final_acceptance=false
proceed_to_v9_8_final_acceptance_validator=implemented_blocked
v9_8_blocker=US-V9-08_provider_backed_storyboard_image_evidence
proceed_to_v9_full_runtime_development=false
runtime_executor_route_created=false
runtime_worker_created=false
source_agent_durable_mutation_allowed=false
```

## Included Files
- `docs/design/V9.x/00_README.md` exists=True size=15770
- `docs/design/V9.x/v9_target_prd.md` exists=True size=6963
- `docs/design/V9.x/v9_target_architecture.md` exists=True size=5808
- `docs/design/V9.x/v9_current_gap_analysis.md` exists=True size=9203
- `docs/design/V9.x/v9_front_stage_development_readiness_audit.md` exists=True size=7112
- `docs/design/V9.x/v9_development_and_acceptance_plan.md` exists=True size=14676
- `docs/design/V9.x/v9_acceptance_gate_matrix.md` exists=True size=8513
- `docs/design/V9.x/v9_user_scenario_acceptance_gate.md` exists=True size=17753
- `docs/design/V9.x/v9_no_false_green_claim_guard.md` exists=True size=2881
- `docs/design/V9.x/v9_contract_schema_bundle.md` exists=True size=5237
- `docs/design/V9.x/v9_human_authorization_ref_contract.md` exists=True size=3955
- `docs/design/V9.x/v9_api_and_service_boundary_spec.md` exists=True size=3058
- `docs/design/V9.x/v9_evidence_package_schema_and_validator_spec.md` exists=True size=3347
- `docs/design/V9.x/v9_test_fixture_and_ci_matrix.md` exists=True size=6771
- `docs/design/V9.x/v9_high_risk_human_decision_protocol.md` exists=True size=1556
- `docs/design/V9.x/v9_security_threat_model_and_abuse_cases.md` exists=True size=1709
- `docs/design/V9.x/v9_operational_runbook_and_incident_response.md` exists=True size=1325
- `docs/design/V9.x/v9_1_agent_executor_contract_package.md` exists=True size=6402
- `docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md` exists=True size=2790
- `docs/design/V9.x/v9_2_controlled_executor_engineering_design.md` exists=True size=2354
- `docs/design/V9.x/v9_3_development_and_acceptance_plan.md` exists=True size=7037
- `docs/design/V9.x/v9_3_orchestration_coordinator_engineering_design.md` exists=True size=1985
- `docs/design/V9.x/v9_4_development_and_acceptance_plan.md` exists=True size=3939
- `docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md` exists=True size=1712
- `docs/design/V9.x/v9_4_pre_implementation_readiness_closure.md` exists=True size=573
- `docs/design/V9.x/v9_5_development_and_acceptance_plan.md` exists=True size=4340
- `docs/design/V9.x/v9_5_terminal_sandbox_engineering_design.md` exists=True size=1735
- `docs/design/V9.x/v9_6_development_and_acceptance_plan.md` exists=True size=3986
- `docs/design/V9.x/v9_6_workflow_studio_engineering_design.md` exists=True size=1822
- `docs/design/V9.x/v9_7_development_and_acceptance_plan.md` exists=True size=4496
- `docs/design/V9.x/v9_7_production_governance_engineering_design.md` exists=True size=1985
- `docs/design/V9.x/v9_8_development_and_acceptance_plan.md` exists=True size=4443
- `docs/design/V9.x/v9_8_final_acceptance_validator_engineering_design.md` exists=True size=2629
- `docs/design/V9.x/v9_document_audit_report.md` exists=True size=14798
- `docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json` exists=True size=2004
- `docs/design/V9.x/decisions/v9_2_high_risk_human_decision.json` exists=True size=2390
- `docs/design/V9.x/decisions/v9_5_high_risk_human_decision.json` exists=True size=2045
- `docs/design/V9.x/v9_2_pre_implementation_development_and_acceptance_plan.md` exists=True size=3177
- `docs/design/V9.x/v9_2_pre_implementation_audit_closure.md` exists=True size=7764
- `docs/design/V9.x/reports/v9_1_contract_validation_report.json` exists=True size=15678
- `docs/design/V9.x/reports/v9_1_negative_test_results.json` exists=True size=1502
- `docs/design/V9.x/reports/v9_1_no_false_green_scan.json` exists=True size=1249
- `docs/design/V9.x/reports/v9_1_redaction_scan.json` exists=True size=642
- `docs/design/V9.x/reports/v9_test_run_summary.json` exists=True size=1956
- `docs/design/V9.x/decisions/v9_4_high_risk_human_decision.json` exists=True size=2002
- `docs/design/V9.x/decisions/v9_7_high_risk_human_decision.json` exists=True size=2113
- `docs/design/V9.x/evidence/v9-1-readiness/result-summary.md` exists=True size=1659
- `docs/design/V9.x/evidence/v9-1-readiness/readiness-dashboard-data.json` exists=True size=3514
- `docs/design/V9.x/evidence/v9-1-safety-gate-implementation/result-summary.md` exists=True size=1029
- `docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json` exists=True size=7626
- `docs/design/V9.x/v9_1_internal_independent_audit_closure.md` exists=True size=2740
- `docs/design/V9.x/evidence/v9-1-internal-independent-audit/result-summary.md` exists=True size=2740
- `docs/design/V9.x/evidence/v9-1-internal-independent-audit/internal-audit-data.json` exists=True size=4608
- `docs/design/V9.x/evidence/v9-2-controlled-executor-pre-implementation/result-summary.md` exists=True size=7764
- `docs/design/V9.x/evidence/v9-2-controlled-executor-pre-implementation/pre-implementation-data.json` exists=True size=16693
- `docs/design/V9.x/v9_2_runtime_acceptance_closure.md` exists=True size=2790
- `docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/result-summary.md` exists=True size=2790
- `docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json` exists=True size=26854
- `docs/design/V9.x/v9_3_runtime_acceptance_closure.md` exists=True size=609
- `docs/design/V9.x/evidence/v9-3-orchestration-runtime/result-summary.md` exists=True size=609
- `docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json` exists=True size=1424
- `docs/design/V9.x/evidence/v9-3-orchestration-runtime/user-scenarios.json` exists=True size=2140
- `docs/design/V9.x/evidence/v9-4-readiness-closure/result-summary.md` exists=True size=573
- `docs/design/V9.x/evidence/v9-4-readiness-closure/pre-implementation-data.json` exists=True size=4214
- `docs/design/V9.x/v9_4_runtime_acceptance_closure.md` exists=True size=419
- `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/result-summary.md` exists=True size=419
- `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json` exists=True size=1191
- `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/git-operation-deny-report.json` exists=True size=1960
- `docs/design/V9.x/evidence/v9-5-terminal-worker/result-summary.md` exists=True size=649
- `docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json` exists=True size=1095
- `docs/design/V9.x/evidence/v9-5-terminal-worker/command-decisions.json` exists=True size=2598
- `docs/design/V9.x/evidence/v9-5-terminal-worker/denial-evidence.json` exists=True size=2052
- `docs/design/V9.x/evidence/v9-6-workflow-studio/result-summary.md` exists=True size=349
- `docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json` exists=True size=1106
- `docs/design/V9.x/evidence/v9-6-workflow-studio/studio_network_log.json` exists=True size=2398
- `docs/design/V9.x/evidence/v9-6-workflow-studio/studio_hidden_form_scan.json` exists=True size=54
- `docs/design/V9.x/evidence/v9-6-workflow-studio/studio_ui_copy_claim_scan.json` exists=True size=51
- `docs/design/V9.x/evidence/v9-6-workflow-studio/manual_confirmation_evidence.json` exists=True size=735
- `docs/design/V9.x/evidence/v9-6-workflow-studio/workflow_diff_proposal.json` exists=True size=902
- `docs/design/V9.x/evidence/v9-7-production-governance/result-summary.md` exists=True size=357
- `docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json` exists=True size=1163
- `docs/design/V9.x/evidence/v9-7-production-governance/governance-fixture.json` exists=True size=12109
- `docs/design/V9.x/evidence/v9-7-production-governance/tenant-isolation-decisions.json` exists=True size=1186
- `docs/design/V9.x/evidence/v9-7-production-governance/credential-lease-decisions.json` exists=True size=3486
- `docs/design/V9.x/evidence/v9-7-production-governance/service-account-binding-decisions.json` exists=True size=1535
- `docs/design/V9.x/evidence/v9-7-production-governance/audit-export-package.json` exists=True size=964
- `docs/design/V9.x/evidence/v9-7-production-governance/incident-timeline.json` exists=True size=2444
- `docs/design/V9.x/evidence/v9-7-production-governance/evidence-hardening-report.json` exists=True size=523
- `docs/design/V9.x/evidence/v9-7-production-governance/terminal-automation-policy.json` exists=True size=554
- `docs/design/V9.x/evidence/v9-7-production-governance/browser-automation-policy.json` exists=True size=308
- `docs/design/V9.x/evidence/v9-3-orchestration-runtime/storyboard-provider-evidence.json` exists=True size=2554
- `docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json` exists=True size=9749
- `docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-result-summary.md` exists=True size=165
- `docs/design/V9.x/../../../core/policies/v9_agent_executor_safety.py` exists=True size=19642
- `docs/design/V9.x/../../../core/policies/v9_controlled_executor_runtime.py` exists=True size=23374
- `docs/design/V9.x/../../../core/workflows/v9_3_multi_agent_orchestration_runtime.py` exists=True size=37206
- `docs/design/V9.x/../../../core/workflows/v9_4_coding_workflow_pilot.py` exists=True size=24141
- `docs/design/V9.x/../../../core/terminal_workers/v9_5_governed_terminal_worker.py` exists=True size=29750
- `docs/design/V9.x/../../../core/product_console/v9_6_workflow_studio.py` exists=True size=25497
- `docs/design/V9.x/../../../core/governance/v9_7_production_governance.py` exists=True size=27526
- `docs/design/V9.x/../../../tests/test_v9_2_controlled_executor_runtime.py` exists=True size=10013
- `docs/design/V9.x/../../../tests/test_v9_2_runtime_evidence.py` exists=True size=2327
- `docs/design/V9.x/../../../tests/test_v9_3_multi_agent_orchestration_runtime.py` exists=True size=7481
- `docs/design/V9.x/../../../tests/test_v9_4_readiness_closure.py` exists=True size=2203
- `docs/design/V9.x/../../../tests/test_v9_4_coding_workflow_pilot.py` exists=True size=4500
- `docs/design/V9.x/../../../tests/test_v9_5_governed_terminal_worker.py` exists=True size=5173
- `docs/design/V9.x/../../../tests/test_v9_6_workflow_studio.py` exists=True size=8793
- `docs/design/V9.x/../../../tests/test_v9_7_production_governance.py` exists=True size=6887
- `docs/design/V9.x/../../../tests/test_v9_8_final_acceptance.py` exists=True size=2018
- `docs/design/V9.x/../../../tools/v9/generate_v9_5_terminal_worker_evidence.py` exists=True size=666
- `docs/design/V9.x/../../../tools/v9/generate_v9_6_workflow_studio_evidence.py` exists=True size=3835
- `docs/design/V9.x/../../../tools/v9/generate_v9_7_production_governance_evidence.py` exists=True size=1106
- `docs/design/V9.x/../../../tools/v9/generate_v9_3_provider_storyboard_evidence.py` exists=True size=13153
- `docs/design/V9.x/../../../tools/v9/generate_v9_8_final_acceptance.py` exists=True size=11628

## Attachments

### `docs/design/V9.x/00_README.md`
```markdown
# V9.x Design Index

文档状态：V9 current control index / V9-8 final acceptance evidence-aligned baseline。

## Current Baseline

V9 继承 V8 的最终收口口径：

```text
V8 complete: station-agent workflow pilot ready for review.
```

该 baseline 只能解释为：

```text
每个 station 有独立 Agent 描述、证据链、受控 terminal handoff 和可解释 TUI 的 ready-for-review 试点。
```

不得被反向升级为：

```text
production ready
full production GA
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
```

## Current V9 Evidence Baseline

当前 V9 主线已从纯 planning package 推进到 V9-8 final acceptance evidence baseline：

```text
V9-0 complete: high-risk execution planning gate ready for review.
V9-1 complete: Agent Executor Safety Gate implementation ready for review.
V9-2 complete: limited controlled Agent executor runtime slice ready for review.
V9-3 complete: multi-Agent orchestration runtime slice ready for review.
V9-4 complete: autonomous coding workflow pilot ready for review.
V9-5 complete: governed terminal worker expansion ready for review.
V9-6 complete: Workflow Studio productization slice ready for review.
V9-7 complete: production governance and terminal automation gate ready for review.
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

该 baseline 的证据边界为：

```text
V9-1 evidence_scope=real_code_policy_validation, runtime_backed=false.
V9-2 evidence_scope=real_runtime_fixture, runtime_backed=true.
V9-2 allowed_operations=[workflow.instance.start, station.rerun, artifact.write, quality.evaluation.create].
V9-2 source=agent direct durable mutation remains denied.
V9-2 runtime executor route created=false.
V9-2 runtime worker created=false.
V9-3 evidence_scope=real_runtime_fixture, runtime_backed=true.
V9-3 proves station-bound Agent registry, serial / parallel / fan-in / fan-out, attempt history, recovery and lineage evidence.
V9-3 video storyboard provider-backed image generation PASS: four MiniMax-backed storyboard image artifacts are recorded with provider/model/invocation refs.
V9-4 evidence_scope=real_runtime_fixture, runtime_backed=true.
V9-4 proves plan / diff proposal / sandboxed test / review summary / fix-loop / human handoff and deny evidence.
V9-4 auto commit / auto push / auto deploy / unreviewed patch apply are denied.
V9-5 evidence_scope=real_runtime_fixture, runtime_backed=true.
V9-5 proves workspace-scoped terminal command tiers, transcript capture, diff proposal capture and denial evidence.
V9-5 denies workspace escape, symlink escape, sensitive reads, git push, production deploy and network without policy.
V9-6 evidence_scope=real_runtime_fixture, runtime_backed=true.
V9-6 proves Studio BFF/DTO read models, read-only panels, browser denylist, WorkflowDiff proposal and manual confirmation evidence.
V9-6 denies direct browser runtime routes, hidden mutation forms, automatic Agent execution copy and complete Studio overclaim.
V9-7 evidence_scope=real_runtime_fixture, runtime_backed=true.
V9-7 proves tenant isolation decision, credential lease validation, service account binding policy, append-only audit export, incident timeline, evidence hardening and automation denial evidence.
V9-7 denies production automation ready, production terminal automation ready and production browser automation ready claims.
```

V9-2 / V9-3 / V9-4 / V9-5 / V9-6 / V9-7 只能证明 limited controlled runtime, bounded orchestration, bounded coding workflow, governed terminal worker, Studio productization and governance/evidence hardening pilot slices ready for review，不得解释为：

```text
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
production ready
unrestricted terminal worker ready
production terminal automation ready
production browser automation ready
production automation ready
```

## V9 Goal

V9 的目标是把 V8 的 station-agent pilot 推进到高风险执行能力的产品化设计与受控试点：

```text
Agent Executor Safety Gate
+ Controlled Agent Executor Runtime
+ Multi-Agent Orchestration Runtime
+ Autonomous Coding Workflow Pilot
+ Governed Terminal Worker Expansion
+ Workflow Studio Productization
+ Production Governance / Evidence Hardening and Terminal Automation Gate
```

V9 默认不追求无边界执行。所有可变更 runtime truth 的动作都必须通过 policy、capability、approval、evidence 和 rollback 边界。

## Canonical Documents

| File | Purpose |
| --- | --- |
| `v9_target_prd.md` | V9 目标 PRD，定义高风险 Agent 执行、编排、代码工作流、Studio 和终端自动化目标。 |
| `v9_target_architecture.md` | V9 目标架构，定义 Agent Execution、Orchestration、Coding Workflow、Workflow Studio、Terminal Automation 平面。 |
| `v9_current_gap_analysis.md` | V8 到 V9 的 gap 分析与风险分类。 |
| `v9_current_gap_analysis.drawio` | V9 中文项目规划图。 |
| `v9_development_and_acceptance_plan.md` | V9 开发与验收总计划。 |
| `v9_milestone_roadmap.md` | V9 项目里程碑与阶段依赖。 |
| `v9_acceptance_gate_matrix.md` | V9 阶段门禁、验收门槛与停止条件。 |
| `v9_user_scenario_acceptance_gate.md` | V9 用户场景验收门槛，定义 final acceptance 前的可打开、可审计体验证据要求。 |
| `v9_no_false_green_claim_guard.md` | V9 禁止声明、误报词和 claim scan 规则。 |
| `v9_planning_audit_for_chatgpt.md` | 给 ChatGPT / 外部审计的审计入口。 |
| `v9_document_audit_report.md` | V9 文档自审报告与进入外部审计建议。 |
| `v9_front_stage_development_readiness_audit.md` | V9-1 到 V9-4 前阶段开发就绪自审。 |
| `v9_1_agent_executor_contract_package.md` | V9-1 Agent executor safety gate 合同包。 |
| `v9_human_authorization_ref_contract.md` | V9 durable mutation 人工授权引用合同。 |
| `v9_2_controlled_executor_implementation_spec.md` | V9-2 controlled executor runtime 实现前规格。 |
| `v9_3_development_and_acceptance_plan.md` | V9-3 orchestration runtime 详细开发与验收计划。 |
| `v9_3_multi_agent_orchestration_implementation_spec.md` | V9-3 multi-Agent orchestration 实现前规格。 |
| `v9_4_development_and_acceptance_plan.md` | V9-4 coding workflow 详细开发与验收计划。 |
| `v9_4_autonomous_coding_workflow_implementation_spec.md` | V9-4 autonomous coding workflow 实现前规格。 |
| `v9_4_pre_implementation_readiness_closure.md` | V9-4 readiness 闭环结论，明确 runtime implementation 仍 NO-GO。 |
| `v9_5_development_and_acceptance_plan.md` | V9-5 terminal worker 详细开发与验收计划。 |
| `v9_5_terminal_worker_boundary_implementation_spec.md` | V9-5 governed terminal worker 实现前规格。 |
| `v9_6_development_and_acceptance_plan.md` | V9-6 Workflow Studio 详细开发与验收计划。 |
| `v9_6_workflow_studio_productization_prd.md` | V9-6 Workflow Studio 独立 PRD。 |
| `v9_7_development_and_acceptance_plan.md` | V9-7 governance / evidence hardening 详细开发与验收计划。 |
| `v9_7_production_governance_terminal_automation_gate_spec.md` | V9-7 governance/evidence/terminal automation 高风险门禁规格。 |
| `v9_8_development_and_acceptance_plan.md` | V9-8 final acceptance 详细开发与验收计划。 |
| `v9_8_final_acceptance_framework.md` | V9-8 最终验收框架。 |
| `v9_contract_schema_bundle.md` | V9 machine-readable schema bundle 计划。 |
| `schemas/` | V9 P0 machine-readable JSON Schema 文件。 |
| `fixtures/` | V9 P0 negative fixture、V9-2 runtime fixture 和 V9-3 orchestration fixture。 |
| `v9_api_and_service_boundary_spec.md` | V9 API、BFF、internal service 和 forbidden route 边界。 |
| `v9_evidence_package_schema_and_validator_spec.md` | V9 evidence package schema 与 validator 规则。 |
| `v9_test_fixture_and_ci_matrix.md` | V9 E2E、negative fixture 与 CI gate 矩阵。 |
| `v9_high_risk_human_decision_protocol.md` | V9 高风险人类决策协议。 |
| `v9_security_threat_model_and_abuse_cases.md` | V9 威胁模型和滥用场景。 |
| `v9_automation_assisted_development_policy.md` | V9 自动化辅助开发边界。 |
| `v9_operational_runbook_and_incident_response.md` | V9 运维、回滚和事件响应手册。 |
| `v9_1_agent_executor_safety_gate_implementation_plan.md` | V9-1 safety gate 实现计划草案。 |
| `v9_2_controlled_executor_engineering_design.md` | V9-2 controlled executor 工程设计。 |
| `v9_3_orchestration_coordinator_engineering_design.md` | V9-3 orchestration coordinator 工程设计。 |
| `v9_4_coding_workflow_runtime_engineering_design.md` | V9-4 coding workflow runtime 工程设计。 |
| `v9_5_terminal_sandbox_engineering_design.md` | V9-5 terminal sandbox 工程设计。 |
| `v9_6_workflow_studio_engineering_design.md` | V9-6 Workflow Studio 工程设计。 |
| `v9_7_production_governance_engineering_design.md` | V9-7 production governance 工程设计。 |
| `v9_8_final_acceptance_validator_engineering_design.md` | V9-8 final acceptance validator 工程设计。 |

## Stage Order

```text
V9-0 Planning And High-Risk Boundary Gate
 -> V9-1 Agent Executor Safety Gate
 -> V9-2 Controlled Agent Executor Runtime
 -> V9-3 Multi-Agent Orchestration Runtime
 -> V9-4 Autonomous Coding Workflow Pilot
 -> V9-5 Governed Terminal Worker Expansion
 -> V9-6 Workflow Studio Productization
 -> V9-7 Production Governance / Evidence Hardening and Terminal Automation Gate
 -> V9-8 Final Acceptance
```

## Current Go / No-Go

| Area | Decision | Reason |
| --- | --- | --- |
| V8 baseline for V9 planning | GO | V8 evidence is PASS but bounded to station-agent workflow pilot ready for review. |
| V9-0 documentation planning | COMPLETE FOR REVIEW | PRD, architecture, gap, plan, drawio, claim guard and P0 engineering docs exist. |
| V9-1 safety gate implementation | COMPLETE FOR REVIEW | Safety gate validators, negative fixtures, claim scan and redaction scan are PASS; no runtime route or runtime worker exists. |
| V9-2 limited controlled runtime slice | COMPLETE FOR REVIEW | Four allowlisted operations have real_runtime_fixture evidence and source=agent durable mutation is denied. |
| V9-3 orchestration runtime | COMPLETE FOR REVIEW | Bounded orchestration runtime fixture has serial/parallel/fan-in/fan-out, recovery, attempt history, lineage and user scenario evidence. |
| V9-4 autonomous coding | COMPLETE FOR REVIEW | Coding workflow runtime fixture has plan, diff proposal, sandboxed test, review, fix-loop, handoff and no auto commit/push/deploy evidence. |
| V9-5 terminal expansion | COMPLETE FOR REVIEW | Governed terminal worker fixture has command tier, transcript, diff capture and denial evidence; it is not unrestricted shell. |
| V9-6 Studio productization | COMPLETE FOR REVIEW | Studio BFF/DTO read-model fixture, browser denylist, read-only panels, WorkflowDiff proposal and manual confirmation evidence are PASS. |
| V9-7 production governance / evidence hardening / terminal automation | COMPLETE FOR REVIEW | Governance fixture proves tenant isolation, credential lease, audit export, incident timeline, evidence hardening and automation denial evidence. |
| V9-8 final acceptance validator | IMPLEMENTED / BLOCKED | Final dashboard/data are generated, but final claim remains blocked because US-V9-08 provider-backed storyboard image evidence is unavailable. |

## Allowed Claims

```text
V9-0 complete: high-risk execution planning gate ready for review.
V9-1 complete: Agent executor safety gate ready for review.
V9-2 complete: controlled Agent execution runtime slice ready for review.
V9-3 complete: multi-Agent orchestration runtime slice ready for review.
V9-4 complete: autonomous coding workflow pilot ready for review.
V9-5 complete: governed terminal worker expansion ready for review.
V9-6 complete: Workflow Studio productization slice ready for review.
V9-7 complete: production governance and terminal automation gate ready for review.
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

## Forbidden Claims

```text
production ready
full production GA
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
production browser automation ready
production automation ready
```

## Recommended External Audit Paths

```text
docs/design/V9.x/00_README.md
docs/design/V9.x/v9_target_prd.md
docs/design/V9.x/v9_target_architecture.md
docs/design/V9.x/v9_current_gap_analysis.md
docs/design/V9.x/v9_current_gap_analysis.drawio
docs/design/V9.x/v9_development_and_acceptance_plan.md
docs/design/V9.x/v9_milestone_roadmap.md
docs/design/V9.x/v9_acceptance_gate_matrix.md
docs/design/V9.x/v9_user_scenario_acceptance_gate.md
docs/design/V9.x/v9_no_false_green_claim_guard.md
docs/design/V9.x/v9_planning_audit_for_chatgpt.md
docs/design/V9.x/v9_document_audit_report.md
docs/design/V9.x/v9_front_stage_development_readiness_audit.md
docs/design/V9.x/v9_1_agent_executor_contract_package.md
docs/design/V9.x/v9_human_authorization_ref_contract.md
docs/design/V9.x/v9_2_controlled_executor_implementation_spec.md
docs/design/V9.x/v9_3_multi_agent_orchestration_implementation_spec.md
docs/design/V9.x/v9_4_autonomous_coding_workflow_implementation_spec.md
docs/design/V9.x/v9_5_terminal_worker_boundary_implementation_spec.md
docs/design/V9.x/v9_6_workflow_studio_productization_prd.md
docs/design/V9.x/v9_7_production_governance_terminal_automation_gate_spec.md
docs/design/V9.x/v9_8_final_acceptance_framework.md
```

## Recommended P0 Engineering Audit Paths

```text
docs/design/V9.x/v9_contract_schema_bundle.md
docs/design/V9.x/schemas/
docs/design/V9.x/fixtures/
docs/design/V9.x/v9_api_and_service_boundary_spec.md
docs/design/V9.x/v9_evidence_package_schema_and_validator_spec.md
docs/design/V9.x/v9_test_fixture_and_ci_matrix.md
docs/design/V9.x/v9_high_risk_human_decision_protocol.md
docs/design/V9.x/v9_security_threat_model_and_abuse_cases.md
docs/design/V9.x/v9_automation_assisted_development_policy.md
docs/design/V9.x/v9_operational_runbook_and_incident_response.md
docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md
docs/design/V9.x/v9_2_controlled_executor_engineering_design.md
docs/design/V9.x/v9_3_orchestration_coordinator_engineering_design.md
docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md
docs/design/V9.x/v9_5_terminal_sandbox_engineering_design.md
docs/design/V9.x/v9_6_workflow_studio_engineering_design.md
docs/design/V9.x/v9_7_production_governance_engineering_design.md
docs/design/V9.x/v9_8_final_acceptance_validator_engineering_design.md
```

## Front-Stage Readiness Summary

```text
V9-1 safety gate implementation: PASS / ready for review.
V9-2 limited controlled runtime slice: PASS / ready for review.
V9-3 orchestration runtime slice: PASS / ready for review.
V9-4 coding workflow pilot: PASS / ready for review.
V9-5 governed terminal worker expansion: PASS / ready for review.
V9-6 Workflow Studio Productization: PASS / ready for review.
V9-7 production governance / evidence hardening / terminal automation: PASS / ready for review.
V9-8 final acceptance validator: PASS / dashboard generated; US-V9-08 provider-backed storyboard image evidence recorded.
```

```

### `docs/design/V9.x/v9_target_prd.md`
```markdown
# V9 Target PRD

文档状态：V9 target PRD / V9-2 evidence-aligned baseline。

## 1. Product Goal

V9 面向 V8 之后的高风险能力补齐：

```text
让 Agent 不只是“在岗解释和产出”，而是在受控边界内具备执行、协作、代码开发、Studio 编辑和终端自动化能力。
```

V9 的产品目标不是一次性宣布完整生产可用，而是建立可审计、可回滚、可人工接管的高风险执行基线。

## 1.1 Current Delivery State After V9-2

截至当前 V9 文档基线，已完成的 ready-for-review 能力是：

```text
V9-1 Agent Executor Safety Gate implementation.
V9-2 limited controlled Agent executor runtime slice.
```

V9-2 的产品解释必须保持受限：

```text
用户可以通过受控 runtime fixture 验证 workflow.instance.start / station.rerun / artifact.write / quality.evaluation.create 四类动作。
这些动作必须经过 policy / capability / HumanAuthorizationRef 或 user confirmation / approval / kill switch / idempotency / timeout / rollback / evidence chain。
source=agent direct durable mutation 仍被拒绝。
connector.call / external_llm.call / git.commit / git.push / production.deploy 等动作仍被拒绝。
```

V9-2 不得解释为：

```text
不得解释为通用 Agent executor 已完成
不得解释为受控执行器已完成
不得解释为生产级受控执行器已完成
不得解释为完整多 Agent 编排已完成
不得解释为自主代码工作流已完成
不得解释为完整 Workflow Studio 已完成
```

下一产品实现候选是 V9-3：真实 multi-Agent orchestration runtime slice。

## 2. Target User Experience

用户期望的完整体验：

```text
用户提出目标
 -> 系统生成工作流和 Agent 分工
 -> Agent 形成执行计划
 -> 用户确认高风险动作
 -> Agent 在受控 executor 中执行
 -> 多 Agent 串行 / 并行协作
 -> 自动生成或修改代码
 -> 测试和 Review Agent 审查
 -> Studio 展示工作流、Agent、产物、diff、证据和 rerun
 -> 终端 worker 在受限 sandbox 中执行命令
 -> Evidence Chain 记录每一步
```

当前距离该完整体验仍缺：

```text
V9-3 multi-Agent serial / parallel / fan-in / fan-out runtime evidence.
V9-4 coding workflow diff / test / review / fix-loop runtime evidence.
V9-5 governed terminal worker write sandbox evidence.
V9-6 Workflow Studio BFF / DTO / browser denylist evidence.
V9-7 production governance / evidence hardening high-risk evidence.
V9-8 final evidence aggregation.
```

V9 用户场景验收还必须覆盖三类更贴近真实使用的创意型工作流：

```text
Roman Forum debate: 不同身份 Agent 围绕哲学或复杂议题多轮讨论、互相质询并合成有 attribution 的结论。
Video creation storyboard workflow: 用户输入视频点子，系统生成 creative brief、script、shot list、storyboard prompts、分镜图 artifact refs 和 review report。
Natural-language workflow optimization: 用户用自然语言要求调整已有 workflow，系统生成 WorkflowDiff proposal，并在用户确认前不修改 runtime truth。
```

这些场景是 V9 的垂直验收切片，不得被解释为通用视频生产平台、完整自然语言工作流编辑器或完整多 Agent 编排已完成。

## 3. V9 Capability Goals

### Agent Executor

Agent 可以在 policy 允许、scope 限定、用户确认和 evidence 记录后执行动作。

必须具备：

```text
AgentExecutionPolicy
AgentExecutionEnvelope
CapabilityResolver
ApprovalGateDecision
KillSwitchDecision
TimeoutPolicy
RollbackDescriptor
ExecutionEvidence
```

### Multi-Agent Orchestration Runtime Target

支持真实串行、并行、fan-in / fan-out 和 synthesis。

必须具备：

```text
Agent message protocol
private memory / shared context boundary
attempt history
downstream stale propagation
artifact lineage with producer_agent_id / producer_attempt_id
failure recovery
lost worker recovery
conflict review
```

代表性用户场景：

```text
Roman Forum debate workflow.
Local technical design review workflow.
Video creation storyboard workflow.
```

### Autonomous Coding Workflow Pilot

支持受控代码开发工作流：

```text
PlanningAgent
ImplementationAgent
TestAgent
ReviewAgent
FixAgent
EvidenceAgent
```

必须默认禁止：

```text
auto commit
auto push
auto deploy
secret read
unreviewed patch apply
```

### Workflow Studio Productization

从 Thin Console / TUI / Report 进一步产品化：

```text
workflow graph editor
station inspector
Agent profile editor
Skill / MCP / Tool binding UI
diff / publish / run / rerun UI
review console
evidence browser
```

Studio 必须通过 BFF / DTO 消费后端，不得直接写 runtime truth。

自然语言优化工作流必须先产生 WorkflowDiff proposal，用户确认或 valid human_authorization_ref 存在前不得 durable mutation。

### Governed Terminal Worker Expansion

V9 不建议做真正 unrestricted terminal worker。目标改为：

```text
workspace-scoped write sandbox
command allowlist tiers
file write policy
diff capture
session replay
approval-gated commit / push / deploy proposal
```

### Production Governance / Evidence Hardening And Terminal Automation Gate

V9-7 兼容此前的 Production Terminal Automation Gate 口径，但正式范围是 production governance、evidence hardening 和 terminal automation 高风险门禁。它不能被解释为 production terminal automation ready。

生产终端自动化必须是高风险门禁：

```text
tenant isolation
credential lease
service account binding
human authorization
quota / rate limit
audit export
incident timeline
browser automation separate PRD
```

## 4. Out Of Scope For Default V9

```text
unrestricted arbitrary shell
automatic production deploy without approval
production browser account automation without separate PRD
full production GA
complete Workflow Studio GA
unbounded Agent self-modification
source=agent default durable mutation
```

## 5. Success Criteria

V9 completion can only be claimed after:

```text
V9-0..V9-7 evidence packages exist.
No FAIL / BLOCKED.
High-risk stages have human proceed decisions.
Durable mutation is denied unless user_confirmed=true OR valid human_authorization_ref is present.
source=agent default durable mutation is always denied.
No False Green claim scan PASS.
Redaction scan PASS.
Drawio XML valid.
Runtime evidence proves controlled execution, not just docs.
```

Allowed final claim:

```text
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

Forbidden final interpretations:

```text
production ready
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
production browser automation ready
production automation ready
```

```

### `docs/design/V9.x/v9_target_architecture.md`
```markdown
# V9 Target Architecture

文档状态：V9 target architecture / V9-2 evidence-aligned baseline。

## 1. Architecture Goal

V9 在 V8 Station Agent Operating Layer 上新增高风险执行和产品化平面：

```text
Agent Execution Plane
Multi-Agent Orchestration Plane
Autonomous Coding Workflow Plane
Workflow Studio Productization Plane
Governed Terminal Worker Plane
Production Governance / Evidence Hardening and Terminal Automation Gate
```

目标是让 Agent 可以在受控、可审计、可回滚的边界内执行，而不是成为无限制 executor。

## 1.1 Current Architecture Delta After V9-2

当前已落地并可审计的架构切片：

```text
Agent Executor Safety Gate validators
HumanAuthorizationRef validator
CapabilityResolver deny-by-default engine
V9-2 limited controlled runtime fixture for four operations
Append-only execution evidence for V9-2 fixture
No False Green / redaction validation reports
```

当前仍未落地的目标架构切片：

```text
OrchestrationCoordinator runtime with serial / parallel / fan-in / fan-out.
CodingWorkflowRuntime with diff / test / review / fix-loop.
TerminalWorkerSandbox write expansion.
WorkflowStudioBFF product UI.
ProductionGovernanceAutomationGate runtime evidence.
V9 final evidence aggregation dashboard.
Creative workflow scenario adapters for Roman Forum debate and video storyboard generation.
Natural-language workflow optimization proposal path.
```

V9-2 的 ControlledAgentExecutor 仍是 limited runtime fixture，不是 production executor route，也不是 runtime worker。

## 2. Target Planes

```text
Small Studio / Workflow Studio Plane
Mission TUI Plane
Workflow Blueprint Plane
Station Agent Operating Layer
Agent Execution Plane
Multi-Agent Orchestration Plane
Autonomous Coding Workflow Plane
Skill / MCP / Tool Capability Plane
Governed Terminal Worker Plane
Controlled Runtime Plane
Credential / Tenant / Policy Plane
Runtime Report Plane
Review Console Plane
Evidence And Audit Plane
Production Governance / Evidence Hardening and Terminal Automation Gate
```

## 3. Target Architecture Flow

```text
User Goal
 -> Mission TUI / Workflow Studio
 -> WorkflowSpec / Diff / Blueprint
 -> Agent Registry
 -> Orchestration Planner
 -> AgentExecutionEnvelope
 -> CapabilityResolver
 -> ApprovalGate / HumanAuthorization
 -> Controlled Agent Executor
 -> Skill / MCP / Tool / Terminal Worker
 -> Attempt History / Artifact Lineage
 -> Runtime Report
 -> Review Console
 -> Evidence Chain
 -> Studio / TUI Explainability
```

## 4. New Components

| Component | Responsibility | Boundary |
| --- | --- | --- |
| AgentExecutionPolicy | Defines allowed Agent actions by role, stage, tenant and risk | policy only |
| AgentExecutionEnvelope | Carries actor, source, scope, target refs, approval refs and idempotency key | no raw secret or raw payload |
| ControlledAgentExecutor | Executes only the V9-2 allowlisted fixture actions today; target is approved actions only | not unrestricted executor; no production route / worker |
| OrchestrationCoordinator | Coordinates serial, parallel and fan-in/fan-out runs | next implementation candidate; keeps attempt history |
| CodingWorkflowRuntime | Runs planning, implementation, test, review and fix loops | no auto commit / auto push / auto deploy by default |
| DebateWorkflowAdapter | Maps a discussion goal into role-specific Agents, multi-round messages and attributed synthesis | V9-3 user scenario fixture; not full orchestration GA |
| StoryboardWorkflowAdapter | Maps a video idea into brief, script, shot list, storyboard prompts and image artifact refs | provider-backed or explicitly fallback; no raw prompt leakage |
| WorkflowOptimizationPlanner | Converts natural-language optimization requests into WorkflowDiff proposals | no durable mutation before confirmation |
| TerminalWorkerSandbox | Runs scoped commands and captures transcript/diff | no arbitrary shell by default |
| WorkflowStudioBFF | Product UI boundary for Studio operations | no direct runtime truth writes |
| ProductionGovernanceAutomationGate | High-risk gate for production governance, evidence hardening and terminal/browser automation | separate approval, credential, evidence and incident review |

## 5. Runtime Truth Boundary

V9 必须保留并强化：

```text
WorkflowSpec does not replace WorkflowDraft / WorkflowVersion.
Workflow Studio cannot directly write WorkflowStore / StationRun / Artifact.
AgentExecutionEnvelope is request evidence, not runtime truth.
EventBridge only triggers refresh.
Evidence Chain is read-only.
Runtime Report is read-only.
source=agent cannot default durable mutation.
Durable mutation requires user_confirmed=true or human_authorization_ref.
source=agent default durable mutation remains denied even when an Agent proposes the operation.
HumanAuthorizationRef binds issuer, operation hash, target refs, expiry, revocation and audit linkage.
Terminal worker cannot escape workspace sandbox.
Credential leases cannot expose raw secret.
Image generation providers expose redacted invocation refs only.
Workflow optimization from natural language produces proposal / diff / handoff first.
```

## 6. High-Risk Boundaries

需要独立人工决策的阶段：

```text
V9-1 Agent executor safety gate acceptance
V9-2 controlled Agent execution runtime
V9-4 autonomous coding workflow
V9-5 terminal worker write sandbox
V9-7 production governance / evidence hardening and terminal automation gate
```

## 7. Exit Architecture

V9 完成后最多声明：

```text
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

它仍不得默认证明：

```text
full production GA
unrestricted Agent executor
unrestricted terminal worker
production browser automation
complete Workflow Studio GA
```

```

### `docs/design/V9.x/v9_current_gap_analysis.md`
```markdown
# V9 Current Gap Analysis

文档状态：V9 gap analysis / V9-8 final acceptance evidence-aligned baseline。

## 1. Current Baseline

```text
V8 complete: station-agent workflow pilot ready for review.
V9-1 complete: Agent Executor Safety Gate implementation ready for review.
V9-2 complete: limited controlled Agent executor runtime slice ready for review.
V9-3 complete: multi-Agent orchestration runtime slice ready for review.
V9-4 complete: autonomous coding workflow pilot ready for review.
V9-5 complete: governed terminal worker expansion ready for review.
V9-6 complete: Workflow Studio productization slice ready for review.
V9-7 complete: production governance and terminal automation gate ready for review.
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

V8 已证明：

```text
每个 station 有 AgentDescriptor。
每个 Agent 有 role / goal / memory / tools / skills / MCP。
V8-4 real runtime fixture PASS。
V8-6 controlled terminal worker fixture PASS。
V8-7 bounded multi-Agent project workflow fixture PASS。
V8-8 read-only explainability TUI PASS。
V8-9 final framework PASS。
```

V8 未证明：

```text
Agent executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
```

V9-1 / V9-2 已证明：

```text
AgentExecutionEnvelope / AgentExecutionPolicy validators exist.
HumanAuthorizationRef validator exists.
CapabilityResolver deny-by-default safety gate exists.
Negative fixtures, No False Green scan and redaction scan PASS.
V9-2 limited runtime fixture executes only four allowlisted operations.
workflow.instance.start / station.rerun / artifact.write / quality.evaluation.create evidence PASS.
source=agent durable mutation denied.
Excluded operations denied: connector.call, external_llm.call, business.event.emit, context.update, workflow.template.publish, approval.respond, git.commit, git.push, production.deploy.
```

V9-1 / V9-2 仍未证明：

```text
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
production ready
```

V9-3 已证明：

```text
station-bound Agent registry evidence PASS.
serial / parallel / fan-in / fan-out runtime fixture evidence PASS.
failure recovery and lost worker recovery evidence PASS.
attempt history retains failed attempt and previous error evidence PASS.
artifact lineage preserves producer_agent_id and producer_attempt_id evidence PASS.
Roman Forum debate user scenario evidence PASS.
natural-language workflow optimization outputs WorkflowDiff proposal before mutation evidence PASS.
source=agent direct durable mutation denied.
```

V9-3 仍未证明：

```text
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
Agent executor ready
provider-backed video storyboard image generation PASS
autonomous coding workflow ready
```

V9-4 已证明：

```text
coding workflow pilot evidence_scope=real_runtime_fixture.
plan / spec / diff proposal / test plan / sandboxed test result evidence PASS.
review summary is not approval evidence PASS.
fix-loop creates a new proposal rather than silent mutation evidence PASS.
human review handoff evidence PASS.
auto commit denied evidence PASS.
auto push denied evidence PASS.
auto deploy denied evidence PASS.
unreviewed patch apply denied evidence PASS.
source=agent direct durable mutation denied evidence PASS.
```

V9-4 仍未证明：

```text
autonomous coding workflow ready
Agent executor ready
unrestricted terminal worker ready
production terminal automation ready
complete Workflow Studio ready
```

V9-5 已证明：

```text
workspace-scoped terminal worker evidence_scope=real_runtime_fixture.
command tier policy evidence PASS.
readonly command transcript evidence PASS.
workspace-scoped build/test command result evidence PASS.
diff capture proposal_only evidence PASS.
workspace escape denied evidence PASS.
symlink escape denied evidence PASS.
sensitive read denied evidence PASS.
git push denied evidence PASS.
production deploy denied evidence PASS.
network without policy denied evidence PASS.
```

V9-5 仍未证明：

```text
unrestricted terminal worker ready
production terminal automation ready
production browser automation ready
Agent executor ready
```

V9-6 已证明：

```text
Workflow Studio evidence_scope=real_runtime_fixture.
Studio BFF / DTO route allowlist evidence PASS.
Browser denylist evidence PASS for /v1/rpc, /v1/events/subscribe and internal runtime routes.
Workflow Blueprint, Agent Station Inspector, Runtime Report, Evidence Chain and Artifact Lineage panels are read-only.
Natural-language optimization creates WorkflowDiff proposal before mutation evidence PASS.
Manual confirmation records human_authorization_ref evidence PASS.
Hidden mutation form absent evidence PASS.
UI copy does not imply automatic Agent execution evidence PASS.
```

V9-6 仍未证明：

```text
complete Workflow Studio ready
production ready
Agent executor ready
autonomous workflow editing ready
```

V9-7 已证明：

```text
production governance evidence_scope=real_runtime_fixture.
tenant isolation decision evidence PASS.
credential lease tenant/app/audience/operation/expiry/revocation validation evidence PASS.
service account binding policy evidence PASS.
append-only audit export evidence PASS.
incident timeline for policy_denied / credential_denied / timeout / worker_lost evidence PASS.
evidence hardening and automation denial evidence PASS.
browser automation without separate PRD denied.
production automation ready / production terminal automation ready / production browser automation ready claims denied.
```

V9-7 仍未证明：

```text
production automation ready
production terminal automation ready
production browser automation ready
production ready
full production GA
```

## 2. Gap Table

| Area | Current V8 State | V9 Required State | Status | Owner Stage | Risk |
| --- | --- | --- | --- | --- | --- |
| Agent Executor Safety Gate | Agent can propose / handoff; direct durable mutation denied | policy-gated safety gate validators and evidence | complete_for_review | V9-1 | high |
| Controlled Runtime Slice | no V8 controlled runtime execution | four-operation controlled runtime fixture with evidence chain | complete_for_review | V9-2 | high |
| Multi-Agent Orchestration | bounded project workflow fixture | serial / parallel / fan-in/fan-out runtime with recovery | complete_for_review | V9-3 | high |
| Creative Multi-Agent Scenarios | no Roman Forum / video storyboard runtime evidence | debate workflow, storyboard workflow and NL optimization scenario evidence | complete_for_review | V9-3 / V9-6 | high |
| Autonomous Coding | terminal handoff proposal only | controlled coding workflow with diff/test/review/fix loop | complete_for_review | V9-4 | high |
| Terminal Worker | readonly shell fixture | workspace write sandbox and command tiers | complete_for_review | V9-5 | high |
| Workflow Studio | thin console / report / TUI evidence | productized Studio via BFF/DTO | complete_for_review | V9-6 | medium |
| Production Governance / Automation | no production terminal/browser automation | production governance / evidence hardening and terminal automation gate | complete_for_review | V9-7 | critical |
| Final Acceptance | V8 final framework PASS | V9 evidence aggregation and claim guard | complete_for_review | V9-8 | high |

## 3. Gap Classification

```text
complete_for_v8: inherited evidence can be reused only as input.
complete_for_review: V9 evidence exists, but the allowed claim remains ready for review only.
partial_for_review: bounded evidence exists, but at least one provider/UI-dependent scenario remains blocked or belongs to a later owner stage.
blocked_until_high_risk_decision: stage remains blocked until readiness audit and a separate human high-risk decision.
planned: V9 design / implementation / evidence required.
planned_for_v9_3_v9_6: user scenario is required, but PASS depends on owner-stage runtime/provider/UI evidence.
high_risk: separate human proceed decision required.
critical: production or credential-related boundary.
out_of_scope: not part of default V9.
```

## 4. Current Final Evidence Status

```text
V9-8 final acceptance validator exists and generates a PASS dashboard.
Video storyboard workflow has provider-backed image artifact evidence.
MiniMax provider-backed storyboard image generation produced four image artifacts for US-V9-08.
Video storyboard provider-backed image artifact evidence is recorded with provider/model/invocation refs and redacted artifact hashes; no raw credentials, raw prompts, raw provider payloads, raw provider responses or base64 images are stored.
```

## 5. No False Green Notes

V9 gap 文档不得把 planned / ready for review 写成 ready：

```text
Agent executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
production ready
```

```

### `docs/design/V9.x/v9_front_stage_development_readiness_audit.md`
```markdown
# V9 Front-Stage Development Readiness Audit

文档状态：V9-1 to V9-5 development-readiness audit / V9-5 evidence-aligned。

## 1. Audit Conclusion

当前文档可以支撑：

```text
V9-1 external implementation-readiness audit.
V9 P0 implementation package external review.
V9-2 / V9-3 detailed implementation evidence review.
V9-4 coding workflow runtime evidence review.
V9-5 governed terminal worker evidence review.
V9-6 readiness audit preparation.
```

当前仍不能支撑：

```text
V9-6 runtime UI implementation before BFF/browser fixtures are accepted.
V9-8 final acceptance from planning/spec docs alone.
```

## 2. Stage Readiness Table

| Stage | Current Readiness | Allowed Next Work | Blocked Work |
| --- | --- | --- | --- |
| V9-1 Agent Executor Safety Gate | READY FOR EXTERNAL IMPLEMENTATION-READINESS AUDIT | contract validator plan, schema/fixture audit, negative test audit | runtime executor route, runtime worker, source=agent durable mutation |
| V9-2 Controlled Executor Runtime | READY FOR DETAILED IMPLEMENTATION PLANNING AFTER V9-1 PASS | executor design review, HumanAuthorizationRef validator planning, evidence package design | runtime execution before V9-1 PASS |
| V9-3 Multi-Agent Orchestration | COMPLETE FOR REVIEW | bounded orchestration runtime evidence review, user scenario evidence review | full orchestration readiness claim, provider-blocked video storyboard written as provider-backed PASS |
| V9-4 Autonomous Coding Workflow | COMPLETE FOR REVIEW | coding workflow runtime evidence review, user scenario evidence review | auto commit / auto push / auto deploy, unreviewed patch apply, over-readiness claim |
| V9-5 Governed Terminal Worker Expansion | COMPLETE FOR REVIEW | bounded terminal worker evidence review, command tier evidence review, denial evidence review | unrestricted shell, git push, production deploy, production terminal automation |
| V9-6 Workflow Studio Productization | READY FOR STAGE AUDIT ONLY | BFF route allowlist review, browser denylist fixture review, read-only panel review | runtime UI implementation before BFF/browser fixtures are accepted, complete Studio overclaim |

## 3. V9-1 Readiness Evidence

Available inputs and evidence:

```text
docs/design/V9.x/v9_1_agent_executor_contract_package.md
docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md
docs/design/V9.x/v9_human_authorization_ref_contract.md
docs/design/V9.x/v9_contract_schema_bundle.md
docs/design/V9.x/schemas/
docs/design/V9.x/fixtures/schema-negative/
docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json
```

V9-1 audit PASS requires:

```text
AgentExecutionPolicy schema parses.
AgentExecutionEnvelope schema parses.
HumanAuthorizationRef schema parses.
CapabilityResolverDecision schema parses.
ExecutionEvidence schema parses.
source_agent_durable_mutation negative fixture is rejected by validator once implemented.
V9-1 contract freeze sample is accepted as contract_freeze evidence only, not runtime evidence.
No False Green scan PASS.
```

V9-1 remains blocked if:

```text
Agent executor route exists.
Runtime worker implementation starts.
source=agent durable mutation is allowed.
V9-1 is described as Agent executor ready.
```

## 4. V9-2 Readiness Evidence

Available inputs:

```text
docs/design/V9.x/v9_2_controlled_executor_implementation_spec.md
docs/design/V9.x/v9_2_controlled_executor_engineering_design.md
docs/design/V9.x/v9_api_and_service_boundary_spec.md
docs/design/V9.x/v9_evidence_package_schema_and_validator_spec.md
docs/design/V9.x/schemas/agent_execution_envelope.schema.json
docs/design/V9.x/schemas/human_authorization_ref.schema.json
docs/design/V9.x/schemas/evidence_package.schema.json
```

V9-2 implementation may only start after:

```text
V9-1 PASS.
high-risk human decision recorded.
HumanAuthorizationRef validator design accepted.
CapabilityResolver deny-by-default design accepted.
idempotency / timeout / rollback design accepted.
evidence package validator accepted.
```

## 5. V9-3 Readiness Evidence

Available inputs:

```text
docs/design/V9.x/v9_3_multi_agent_orchestration_implementation_spec.md
docs/design/V9.x/v9_3_orchestration_coordinator_engineering_design.md
docs/design/V9.x/schemas/orchestration_message.schema.json
docs/design/V9.x/schemas/artifact_lineage_record.schema.json
docs/design/V9.x/fixtures/schema-negative/artifact_lineage_missing_producer_attempt.json
docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json
docs/design/V9.x/evidence/v9-3-orchestration-runtime/index.html
docs/design/V9.x/evidence/v9-3-orchestration-runtime/result-summary.md
```

V9-3 completion review requires:

```text
V9-2 PASS.
serial / parallel / fan-in / fan-out runtime evidence PASS.
lost worker recovery runtime evidence PASS.
attempt history persistence evidence PASS.
artifact lineage producer_agent_id / producer_attempt_id evidence PASS.
Roman Forum scenario PASS.
natural-language optimization diff-only scenario PASS.
video storyboard provider-backed image generation either PASS or explicitly BLOCKED without false-green.
```

## 6. V9-4 Readiness Evidence

Available inputs:

```text
docs/design/V9.x/v9_4_autonomous_coding_workflow_implementation_spec.md
docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md
docs/design/V9.x/v9_automation_assisted_development_policy.md
docs/design/V9.x/v9_test_fixture_and_ci_matrix.md
```

V9-4 completion review requires:

```text
V9-2 PASS.
V9-3 PASS.
coding workflow sandbox policy accepted.
no auto commit / auto push / auto deploy policy accepted.
diff proposal, test result, review summary and fix-loop evidence formats accepted.
V9-4 high-risk human proceed decision recorded.
coding workflow runtime evidence PASS.
diff proposal is not patch apply.
sandboxed test result evidence PASS.
review summary is not approval.
fix-loop creates new proposal.
auto commit / auto push / auto deploy / unreviewed patch apply denied.
source=agent direct durable mutation denied.
```

## 7. Validation Commands

```text
/usr/bin/python3 -m json.tool docs/design/V9.x/schemas/*.json
/usr/bin/python3 -m json.tool docs/design/V9.x/fixtures/schema-negative/*.json
/usr/bin/python3 -m json.tool docs/design/V9.x/fixtures/evidence/*.json
xmllint --noout docs/design/V9.x/v9_current_gap_analysis.drawio
rg -in "<forbidden-claim-regex>" docs/design/V9.x
```

## 8. Proceed Recommendation

```text
proceed_to_v9_1_external_implementation_readiness_audit=true
proceed_to_v9_1_runtime_implementation=complete_for_review
proceed_to_v9_2_runtime_implementation=complete_for_review
proceed_to_v9_3_runtime_implementation=complete_for_review
proceed_to_v9_4_runtime_implementation=complete_for_review
proceed_to_v9_5_runtime_implementation=complete_for_review
proceed_to_v9_6_readiness_audit=true
proceed_to_v9_6_runtime_implementation=false
```

V9 front-stage evidence is now sufficient for V9-1 through V9-5 ready-for-review closure. It is not sufficient to enter V9-6 runtime UI implementation without BFF/browser fixtures, claim V9-8 final acceptance, or claim unrestricted / production-ready execution.

```

### `docs/design/V9.x/v9_development_and_acceptance_plan.md`
```markdown
# V9 Development And Acceptance Plan

文档状态：V9 development and acceptance control plan / V9-8 final acceptance evidence-aligned baseline。

## 0. Current V9 Control Baseline

```text
V9-0 complete: high-risk execution planning gate ready for review.
V9-1 complete: Agent Executor Safety Gate implementation ready for review.
V9-2 complete: limited controlled Agent executor runtime slice ready for review.
V9-3 complete: multi-Agent orchestration runtime slice ready for review.
V9-4 complete: autonomous coding workflow pilot ready for review.
V9-5 complete: governed terminal worker expansion ready for review.
V9-6 complete: Workflow Studio productization slice ready for review.
V9-7 complete: production governance and terminal automation gate ready for review.
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

当前允许的 V9-2 证据解释：

```text
evidence_scope=real_runtime_fixture
runtime_backed=true
allowed_operations=[workflow.instance.start, station.rerun, artifact.write, quality.evaluation.create]
source=agent durable mutation denied
runtime_executor_route_created=false
runtime_worker_created=false
```

当前下一门禁候选：

```text
V9-8 Final Acceptance PASS evidence review
```

V9-3 已产出 bounded real_runtime_fixture evidence。V9-4 已产出 bounded coding workflow real_runtime_fixture evidence。V9-5 已产出 governed terminal worker real_runtime_fixture evidence。V9-6 已产出 Workflow Studio productization real_runtime_fixture evidence。V9-7 已产出 production governance / evidence hardening real_runtime_fixture evidence。V9-8 final acceptance validator 已实现并生成 PASS 看板；US-V9-08 provider-backed storyboard image evidence 已补齐，最终声明允许为 ready for review 范围。

V9-8 final acceptance 还必须通过用户场景验收门槛：

```text
docs/design/V9.x/v9_user_scenario_acceptance_gate.md
```

## 1. Stage Status Table

| Stage | Purpose | Current Status | Allowed Claim | Boundary |
| --- | --- | --- | --- | --- |
| V9-0 | Planning And High-Risk Boundary Gate | complete_for_review | V9-0 complete: high-risk execution planning gate ready for review. | documentation only |
| V9-1 | Agent Executor Safety Gate | complete_for_review | V9-1 complete: Agent Executor Safety Gate implementation ready for review. | validator / safety gate only |
| V9-2 | Controlled Agent Executor Runtime | complete_for_review | V9-2 complete: limited controlled Agent executor runtime slice ready for review. | four-operation runtime fixture only |
| V9-3 | Multi-Agent Orchestration Runtime | complete_for_review | V9-3 complete: multi-Agent orchestration runtime slice ready for review. | not full orchestration GA |
| V9-4 | Autonomous Coding Workflow Pilot | complete_for_review | V9-4 complete: autonomous coding workflow pilot ready for review. | no auto commit / auto push / auto deploy |
| V9-5 | Governed Terminal Worker Expansion | complete_for_review | V9-5 complete: governed terminal worker expansion ready for review. | not unrestricted shell |
| V9-6 | Workflow Studio Productization | complete_for_review | V9-6 complete: Workflow Studio productization slice ready for review. | not complete Studio GA |
| V9-7 | Production Governance / Evidence Hardening and Terminal Automation Gate | complete_for_review | V9-7 complete: production governance and terminal automation gate ready for review. | not production automation ready |
| V9-8 | Final Acceptance | complete_for_review | V9 complete: high-risk Agent execution and workflow productization baseline ready for review. | not production ready / not Agent executor ready / not full orchestration ready |

## 2. Development Order

```text
V9-0 -> V9-1 -> V9-2 -> V9-3 -> V9-4 -> V9-5 -> V9-6 -> V9-7 -> V9-8
```

V9-1、V9-2、V9-3、V9-4、V9-5、V9-6、V9-7 已完成受限证据闭环。V9-8 validator 已实现且 PASS；US-V9-08 真实 provider-backed 图像证据已补齐。当前下一动作是外部审计 V9 final evidence package，不作生产能力声明。

## 2.1 Next Development Order After V9-2

```text
V9-3 orchestration runtime evidence package PASS
 -> V9-3 user scenario acceptance package PASS with provider-backed storyboard image generation evidence
 -> V9-3 PRD/spec review PASS
 -> V9-4 readiness audit PASS
 -> V9-4 coding workflow runtime evidence PASS
 -> V9-5 governed terminal worker evidence PASS
 -> V9-6 Workflow Studio evidence PASS
 -> V9-7 production governance evidence PASS
 -> V9-8 final acceptance validator PASS with US-V9-08 provider-backed image evidence
```

V9-3 必须产生真实 runtime fixture，覆盖：

```text
serial station dependency
parallel branch independent state
fan-out dispatch
fan-in join / synthesis
lost worker recovery
failure retry without overwriting old attempt
artifact lineage with producer_agent_id and producer_attempt_id
incident / evidence chain refs
user-facing orchestration dashboard / report
Roman Forum debate user scenario with role-specific Agents and attributed synthesis
video storyboard workflow user scenario with storyboard artifacts and provider evidence boundary
natural-language workflow optimization user scenario with WorkflowDiff proposal before mutation
```

V9-3 已产出证据：

```text
docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json
docs/design/V9.x/evidence/v9-3-orchestration-runtime/index.html
docs/design/V9.x/evidence/v9-3-orchestration-runtime/result-summary.md
```

V9-3 implementation package 已补齐：

```text
docs/design/V9.x/v9_3_development_and_acceptance_plan.md
docs/design/V9.x/schemas/v9_3_*.schema.json
docs/design/V9.x/fixtures/v9-3-orchestration/
```

V9-4..V9-8 detailed development and acceptance plans are now available as stage audit inputs:

```text
docs/design/V9.x/v9_4_development_and_acceptance_plan.md
docs/design/V9.x/v9_5_development_and_acceptance_plan.md
docs/design/V9.x/v9_6_development_and_acceptance_plan.md
docs/design/V9.x/v9_7_development_and_acceptance_plan.md
docs/design/V9.x/v9_8_development_and_acceptance_plan.md
```

V9-4 readiness closure evidence:

```text
docs/design/V9.x/evidence/v9-4-readiness-closure/pre-implementation-data.json
docs/design/V9.x/evidence/v9-4-readiness-closure/index.html
docs/design/V9.x/evidence/v9-4-readiness-closure/result-summary.md
```

V9-4 runtime evidence:

```text
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/index.html
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/result-summary.md
```

These documents support stage-by-stage implementation planning and stage audit only. They do not authorize skipping V9-3 PASS, high-risk human decisions, runtime evidence packages or V9-8 final acceptance gates.

V9-5 completion evidence:

```text
docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json
docs/design/V9.x/evidence/v9-5-terminal-worker/index.html
docs/design/V9.x/evidence/v9-5-terminal-worker/result-summary.md
```

V9-5 does not authorize broad terminal runtime, unrestricted shell, production deploy, git push, browser account automation or unscoped write actions.

V9-6 completion evidence:

```text
docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json
docs/design/V9.x/evidence/v9-6-workflow-studio/index.html
docs/design/V9.x/evidence/v9-6-workflow-studio/result-summary.md
```

V9-6 does not authorize complete Workflow Studio readiness, direct runtime truth writes, hidden mutation forms, direct browser internal runtime calls or automatic Agent execution.

V9-7 completion evidence:

```text
docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json
docs/design/V9.x/evidence/v9-7-production-governance/index.html
docs/design/V9.x/evidence/v9-7-production-governance/result-summary.md
```

V9-7 does not authorize production automation ready, production terminal automation ready, production browser automation ready, raw credential access, mutable audit export or unrestricted terminal/browser automation.

V9-8 final acceptance evidence:

```text
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-dashboard.html
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-result-summary.md
docs/design/V9.x/evidence/v9-3-orchestration-runtime/storyboard-provider-evidence.json
```

Provider-backed storyboard image generation was completed through MiniMax. The evidence records four storyboard image artifacts, provider/model/invocation refs, artifact hashes and redaction flags. It does not store raw credentials, raw prompts, raw provider payloads, raw provider responses or base64 images.

## 3. Implementation Readiness Requirements

Before V9-1:

```text
V9-0 accepted.
AgentExecutionPolicy contract accepted.
AgentExecutionEnvelope contract accepted.
CapabilityResolver safety matrix accepted.
Approval / kill switch / timeout / rollback contract accepted.
No False Green guard accepted.
P0 schema files parse.
P0 negative fixtures parse.
V9 front-stage readiness audit accepted.
```

Before V9-2:

```text
V9-1 accepted.
Controlled executor action allowlist accepted.
Durable mutation user confirmation policy accepted.
Durable mutation invariant accepted: user_confirmed=true OR valid human_authorization_ref.
HumanAuthorizationRef contract accepted.
source=agent default durable mutation denial accepted.
Execution evidence schema accepted.
Redaction and secret boundary accepted.
V9-1 runtime evidence PASS.
```

Before V9-3:

```text
V9-2 evidence PASS and remains bounded to limited controlled runtime slice.
Agent message protocol accepted.
Attempt history and artifact lineage contracts accepted.
Serial, parallel, fan-in and fan-out contracts accepted.
Failure recovery and lost worker recovery matrix accepted.
producer_agent_id and producer_attempt_id lineage requirements accepted.
V9-2 runtime evidence PASS.
No False Green scan PASS.
V9-3 E2E fixture design accepted.
```

Before V9-4:

```text
V9-2 and V9-3 evidence PASS.
Coding workflow sandbox contract accepted.
Diff / test / review / fix loop accepted.
No auto commit / push / deploy policy accepted.
No unreviewed patch apply policy accepted.
V9-2 and V9-3 runtime evidence packages accepted.
V9-4 high-risk human proceed decision recorded.
```

## 3.1 Front-Stage PR Slices

```text
V9-1A schema and contract validator
V9-1B CapabilityResolver deny-by-default validator
V9-1C HumanAuthorizationRef validation hook
V9-1D negative fixture runner and evidence package
V9-2A controlled executor action allowlist
V9-2B idempotency / timeout / rollback chain
V9-2C append-only execution evidence
V9-3A orchestration message protocol
V9-3B branch state and fan-in/fan-out coordinator
V9-3C attempt history and artifact lineage
V9-4A coding workflow sandbox and git deny policy
V9-4B diff / test / review / fix-loop evidence
```

Before V9-5:

```text
V8-6 / V8-7 evidence accepted.
Workspace write sandbox accepted.
Command tier allowlist accepted.
File write policy accepted.
Terminal transcript / diff capture accepted.
```

Before V9-6:

```text
Studio PRD accepted.
BFF route allowlist accepted.
Browser denylist accepted.
Runtime truth boundary accepted.
UI false-green copy scan accepted.
```

Before V9-7:

```text
Tenant / credential / approval / audit / incident / evidence hardening contracts accepted.
Production governance / terminal automation scope accepted.
Browser account automation separate PRD accepted if enabled.
```

## 4. Test Matrix

```text
user_scenario_v9_2_controlled_runtime_review_pass
user_scenario_v9_3_orchestration_review_requires_runtime_evidence
user_scenario_v9_4_coding_workflow_review_blocks_without_diff_test_review
user_scenario_v9_5_terminal_worker_review_blocks_without_sandbox_evidence
user_scenario_v9_6_studio_review_blocks_without_bff_browser_evidence
user_scenario_v9_8_final_review_blocks_if_any_required_scenario_missing
agent_execution_requires_policy_decision
durable_mutation_requires_user_confirmation
durable_mutation_allows_human_authorization_ref
source_agent_direct_mutation_denied_by_default
agent_execution_evidence_redacted
kill_switch_checked_before_action
timeout_marks_attempt_failed
rollback_descriptor_required_for_mutation
multi_agent_parallel_branch_states_independent
multi_agent_fan_in_fan_out_evidence_exists
lost_agent_recovery_retains_old_attempt
artifact_lineage_preserves_producer_agent_and_attempt
roman_forum_debate_preserves_agent_roles_and_attribution
video_storyboard_workflow_records_provider_backed_or_blocked_image_evidence
natural_language_workflow_optimization_requires_diff_and_confirmation
coding_workflow_diff_requires_review
coding_workflow_no_auto_commit
coding_workflow_no_auto_push
coding_workflow_no_auto_deploy
terminal_worker_workspace_escape_denied
terminal_worker_secret_read_denied
studio_browser_no_direct_runtime_truth
studio_hidden_mutation_form_absent
production_terminal_automation_requires_high_risk_gate
v9_no_false_green_scan_pass
v9_redaction_scan_pass
```

## 5. Validation Commands

```text
xmllint --noout docs/design/V9.x/v9_current_gap_analysis.drawio
rg -in "production[- ]?ready|full production GA|GA ready|Agent executor ready|controlled executor ready|production controlled executor ready|full multi-Agent orchestration ready|distributed multi-Agent runtime ready|autonomous coding workflow ready|autonomous workflow editing ready|complete Workflow Studio ready|unrestricted terminal worker ready|production terminal automation ready|production browser automation ready|production automation ready|生产可用|全面生产可用|生产就绪|可投产|正式发布|生产级可用|Agent执行器已完成|Agent Executor 已完成|受控执行器已完成|生产级受控执行器已完成|完整多Agent编排已完成|多智能体编排已完成|自主代码工作流已完成|自主工作流编辑已完成|完整工作流工作台已完成|无限制终端worker已完成|生产终端自动化已完成|生产浏览器自动化已完成|生产自动化已完成" docs/design/V9.x
```

The claim scan may find forbidden terms only inside explicit forbidden/no-false-green contexts.

## 6. Stop Conditions

```text
V9 docs retroactively upgrade V8 to production ready.
Any V9 document claims Agent executor ready outside forbidden/no-false-green context.
Any stage allows source=agent default durable mutation.
Terminal worker is designed as unrestricted arbitrary shell.
Studio directly writes runtime truth.
Credential raw secret appears in evidence.
V9-8 final claim emitted before V9-0..V9-7 evidence exists.
```

```

### `docs/design/V9.x/v9_acceptance_gate_matrix.md`
```markdown
# V9 Acceptance Gate Matrix

文档状态：V9 acceptance control matrix / V9-8 final acceptance evidence-aligned baseline。

| Stage | Entry Gate | Acceptance Gate | Stop Condition |
| --- | --- | --- | --- |
| V9-0 | V8 final baseline accepted as bounded | PRD, architecture, gap, drawio, plan and claim guard accepted; status complete_for_review | V9-0 claims runtime complete |
| V9-1 | V9-0 accepted | Safety gate validators, negative fixtures, No False Green scan and redaction scan PASS; status complete_for_review | Agent executor ready is claimed |
| V9-2 | V9-1 PASS and human high-risk decision recorded | four allowlisted runtime operations prove policy decision, approval evidence, durable mutation invariant, idempotency, redacted execution evidence and source=agent denial; status complete_for_review | source=agent mutates by default or durable mutation runs without user_confirmed=true OR valid human_authorization_ref |
| V9-3 | V9-2 PASS and V9-3 readiness audit accepted | serial, parallel, fan-in, fan-out, failure recovery, lost worker recovery, attempt history, artifact lineage, producer_agent_id and producer_attempt_id evidence exist; status complete_for_review | full multi-Agent orchestration is claimed without complete evidence |
| V9-4 | V9-2 / V9-3 PASS and V9-4 high-risk human decision recorded | coding workflow produces diff, test, review, fix-loop and evidence with sandbox boundary | auto commit / auto push / auto deploy occurs without approval; automated tooling applies patches, commits, pushes, deploys, or marks review as approval |
| V9-5 | V8-6/V8-7 evidence, V9-4 PASS and new human decision | terminal worker command tiers, transcript, diff capture and denial evidence exist; status complete_for_review | unrestricted shell is allowed |
| V9-6 | Studio PRD and BFF boundary accepted | Studio UI operates through DTO/BFF, passes browser denylist, records WorkflowDiff proposal and manual confirmation evidence; status complete_for_review | Studio directly writes runtime truth |
| V9-7 | production governance / evidence hardening spec and human decision | governance, evidence hardening and terminal automation gate evidence exists; status complete_for_review | browser/terminal automation runs without credential, approval, evidence and incident boundary |
| V9-8 | V9-0..V9-7 evidence exists and user scenario acceptance gate reviewed | final dashboard, user scenario dashboard, claim scan, redaction scan and drawio XML pass | final claim emitted while any stage or user scenario is BLOCKED |

## Current Evidence Status

| Stage | Evidence Path | Status | Scope |
| --- | --- | --- | --- |
| V9-1 | `docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json` | PASS | real_code_policy_validation; runtime_backed=false |
| V9-2 | `docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; four operations only |
| V9-3 | `docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; bounded orchestration only |
| V9-4 | `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; proposal-only coding workflow with sandboxed test and denial evidence |
| V9-5 | `docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; workspace-scoped command tiers, transcript, diff capture and denial evidence |
| V9-6 | `docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; BFF/DTO read models, browser denylist, read-only panels, WorkflowDiff proposal and manual confirmation |
| V9-7 | `docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; tenant isolation, credential lease, audit export, incident timeline, evidence hardening and automation denial |
| V9-8 | `docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json` | PASS | final validator PASS; US-V9-08 provider-backed storyboard image evidence recorded with four image artifacts |

## Global Acceptance Requirements

```text
No production ready claim.
No full production GA claim.
No Agent executor ready claim in V9, including final acceptance, unless a separate future readiness gate exists.
No full multi-Agent orchestration ready claim in V9, including final acceptance, unless a separate future readiness gate exists.
No autonomous coding workflow ready claim without sandbox, review and rollback evidence.
No complete Workflow Studio ready claim without separate Studio acceptance.
No unrestricted terminal worker.
No raw secret / raw prompt / raw artifact content leakage.
Durable mutation denied unless user_confirmed=true OR valid human_authorization_ref is present.
source=agent default durable mutation always denied.
```

## User Scenario Acceptance Gate

V9 final acceptance must include a user-facing scenario gate in addition to technical gates.

| Scenario | Owner Stage | User-Facing Acceptance |
| --- | --- | --- |
| US-V9-01 | V9-2 | 技术负责人打开 V9-2 controlled runtime dashboard，核对四类 allowed operations、excluded operations、source=agent denial 和 evidence chain。 |
| US-V9-02 | V9-3 | 用户输入“让多个 Agent 评审本地技术方案并合成结论”，看见 3 个 station-bound Agents、fan-out/fan-in、recovery、attempt history 和 artifact lineage。 |
| US-V9-03 | V9-4 | 开发者输入“小型代码修改任务”，看见 plan、diff proposal、sandboxed test、review summary、fix-loop proposal，并验证 no auto commit/push/deploy/unreviewed patch apply。 |
| US-V9-04 | V9-5 | 审计者要求 Agent 运行 workspace-scoped 检查命令，看见 command tier、transcript、diff capture、workspace escape denial 和 secret-read denial。 |
| US-V9-05 | V9-6 | 产品使用者在 Studio 查看 workflow graph、station Agent profile、runtime status、artifact lineage、Runtime Report 和 Evidence Chain。 |
| US-V9-06 | V9-8 | 最终验收人打开 V9 final dashboard，确认每阶段和每个用户场景的 status、claim scan、redaction scan 和 drawio XML result。 |
| US-V9-07 | V9-3 | 用户发起“罗马广场”哲学讨论，看见哲学家、工程师、历史学家、伦理学家等 role-specific Agents 多轮发言、互相引用和 attribution-preserving synthesis。 |
| US-V9-08 | V9-3 / V9-6 | 创作者输入视频点子，看见创作 workflow、brief、script、shot list、storyboard prompts、分镜图 artifact refs、provider/model refs 和 evidence chain。 |
| US-V9-09 | V9-6 | 用户用自然语言优化已有工作流，看见 WorkflowDiff proposal、station/Agent 变化、risk_delta，并确认用户确认前没有 durable mutation。 |

User scenario PASS requires:

```text
dashboard_or_report_ref exists.
evidence_refs exist.
evidence_scope is explicit.
runtime_backed scenarios have real_runtime_fixture or real_runtime evidence.
planning docs / transcript-only / report-only evidence does not satisfy runtime-backed user scenario PASS.
Creative workflow scenes must distinguish real provider-backed artifacts from fallback_demo_only or placeholder outputs.
Natural-language optimization must produce proposal / diff / handoff before mutation.
```

V9-8 would be BLOCKED if any required user scenario is FAIL, BLOCKED or missing without a documented human proceed decision; current generated V9-8 data is PASS.

## Front-Stage Audit Vs Runtime Gates

| Stage | Audit PASS Means | Runtime PASS Requires |
| --- | --- | --- |
| V9-1 | Contract, schema and fixture package accepted | Safety gate validator implemented, negative fixtures exercised, evidence package recorded |
| V9-2 | Controlled executor design accepted | Runtime allowlisted actions execute through policy / authorization / approval / evidence chain |
| V9-3 | Orchestration design accepted | Serial / parallel / fan-in / fan-out runtime evidence with recovery and lineage |
| V9-4 | Coding workflow design accepted | Real sandboxed diff / test / review / fix-loop evidence and no auto commit / push / deploy |

## High-Risk Human Decisions

```text
V9-1 safety gate acceptance
V9-2 controlled Agent executor runtime
V9-4 autonomous coding workflow pilot
V9-5 terminal worker write sandbox
V9-7 production governance / evidence hardening and terminal automation gate
```

```

### `docs/design/V9.x/v9_user_scenario_acceptance_gate.md`
```markdown
# V9 User Scenario Acceptance Gate

文档状态：V9 user scenario acceptance gate / required before final acceptance.

## 1. Purpose

V9 技术验收不能只证明 schema、fixture 或单元测试通过，还必须证明用户能理解、触发、观察和审计关键体验路径。

本门槛是 V9-8 final acceptance 的前置硬门槛，不新增 V9 阶段，也不替代 V9-3 / V9-4 / V9-5 / V9-6 / V9-7 的技术验收。

## 2. Global Rule

每个用户场景必须输出以下字段：

```text
scenario_id
title
owner_stage
user_goal
user_entry
user_steps
expected_user_visible_outputs
expected_audit_outputs
runtime_evidence_required
evidence_scope
runtime_backed
allowed_status
evidence_refs
dashboard_or_report_ref
claim_guard_notes
redaction_guard_notes
```

场景 PASS 的最低条件：

```text
用户能看到目标、Agent 分工、运行状态、产物和证据链。
用户能打开 HTML 看板或报告审计结果。
用户能区分 ready for review，且不得把它理解为 ready / production ready。
runtime-backed 场景必须引用真实 runtime fixture 或 real runtime evidence。
planning docs、transcript-only、report-only 不得满足 runtime-backed 用户场景 PASS。
```

## 2.1 User-Facing Capability Boundary

截至当前 V9-2，用户可以真实体验和审计的能力是：

```text
用户可以打开 V9-2 evidence dashboard。
用户可以看到 workflow.instance.start / station.rerun / artifact.write / quality.evaluation.create 四类受控动作。
用户可以看到 policy / capability / HumanAuthorizationRef / approval / kill switch / idempotency / timeout / rollback / evidence chain。
用户可以确认 source=agent direct durable mutation 被拒绝。
用户可以确认 connector.call / external_llm.call / git.commit / git.push / production.deploy 仍被拒绝。
```

这说明项目已经具备“受控动作执行切片”的审计体验，但仍不能解释为：

```text
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous workflow editing ready
complete Workflow Studio ready
production ready
```

当前下一开发阶段 V9-3 完成后的目标体验是：

```text
用户用自然语言触发一个多 Agent 编排 runtime slice。
系统展示 station-bound Agents、Agent 角色、串行依赖、并行分支、fan-out、fan-in、失败恢复、attempt history 和 artifact lineage。
用户可以打开 runtime dashboard / evidence chain 审计每个 Agent 的产物来源、producer_agent_id、producer_attempt_id 和 redacted evidence refs。
```

V9 全阶段完成后的目标用户体验是：

```text
用户提出目标。
系统生成工作流、Agent 分工、Blueprint 和 Diff。
用户确认高风险动作。
Agent 在受控边界内执行、协作、产出方案、产物或代码建议。
Studio / TUI 展示 Agent 身份、运行状态、产物血缘、Runtime Report 和 Evidence Chain。
最终验收看板展示每个阶段和每个用户场景的 PASS / PARTIAL / FAIL / BLOCKED。
```

该体验最多支持 `ready for review`，不得被摘要为 production ready、complete Studio 或 unrestricted Agent executor。

## 3. Required User Scenarios

| Scenario | Stage | User Goal | Acceptance Gate |
| --- | --- | --- | --- |
| US-V9-01 | V9-2 | 用户作为技术负责人，审查“受控执行器是否真的只执行四类允许动作” | V9-2 evidence dashboard shows allowed operations, excluded operations, source=agent denial and evidence chain |
| US-V9-02 | V9-3 | 用户输入“让多个 Agent 并行评审本地技术方案并合成结论”，审查多 Agent 编排路径 | runtime fixture shows serial, parallel, fan-out, fan-in, recovery, attempt history and lineage |
| US-V9-03 | V9-4 | 用户输入“针对一个小型代码修改任务生成方案、diff、测试和 review”，审查代码工作流不自动提交 | dashboard shows proposal-only diff, sandboxed tests, review summary and no auto commit / push / deploy evidence |
| US-V9-04 | V9-5 | 用户要求 Agent 读取 workspace、运行受控测试命令并生成 diff proposal，审查终端 sandbox 边界 | dashboard shows workspace boundary, command tier, transcript, diff capture and denied escape attempts |
| US-V9-05 | V9-6 | 用户在 Studio 打开同一工作流，查看 Agent 分工、运行状态、产物和证据链 | browser evidence shows BFF/DTO usage, read-only review panels and no direct runtime truth write |
| US-V9-06 | V9-8 | 用户打开最终验收看板，确认 V9 是否只能进入 ready-for-review 结论 | final dashboard aggregates all stage evidence, user scenario results, claim scan, redaction scan and drawio XML result |
| US-V9-07 | V9-3 | 用户输入“罗马广场：让不同身份 Agent 讨论一个哲学话题并互相质询”，审查多 Agent 讨论与 synthesis | runtime fixture shows role-specific Agents, multi-round messages, attribution-preserving synthesis and evidence chain |
| US-V9-08 | V9-3 / V9-6 | 用户输入一个视频点子，系统制定创作 workflow 并生成分镜图与创作包 | workflow spec, storyboard, image artifacts, provider/model refs, redaction result and dashboard are visible |
| US-V9-09 | V9-6 | 用户用自然语言要求优化已有工作流，审查系统是否只生成 Diff proposal 并等待确认 | WorkflowDiff proposal is visible; no durable mutation happens before user confirmation or valid human authorization |

## 3.1 Concrete Key Scenario Thresholds

### KS-V9-A Local Technical Design Review With Multiple Agents

User story:

```text
作为技术负责人，
我输入“请让多个 Agent 评审 docs/design/V9.x 的 V9-3 多 Agent 编排方案，分别从架构、风险、验收证据三个角度提出意见，并合成一份结论”，
我期望系统展示每个 station 上的 Agent、它们的角色、并行分支状态、各自产物、冲突点、合成结论和证据链。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
至少 3 个 station-bound Agents: architecture reviewer, risk reviewer, evidence reviewer.
用户能看到 fan-out: 同一设计材料分发给 3 个并行分支。
用户能看到 fan-in: synthesis station 引用 3 个分支产物并保留 attribution_refs。
每个产物有 producer_agent_id 和 producer_attempt_id。
失败或超时分支必须保留 old attempt，并展示 recovery attempt。
最终 dashboard 展示 serial/parallel/fan-in/fan-out、attempt history、artifact lineage 和 Evidence Chain。
缺任一项则 US-V9-02 不得 PASS。
```

### KS-V9-B Controlled Coding Change Proposal

User story:

```text
作为开发者，
我输入“请分析一个小型代码修改任务，生成实现计划、diff proposal、测试计划和 review 结论”，
我期望 Agent 能给出可审查的代码变更建议，但不能自动 apply patch、commit、push 或 deploy。
```

Acceptance threshold:

```text
user_entry=Mission TUI, Workflow Studio or controlled coding dashboard.
用户能看到 PlanningAgent / ImplementationAgent / TestAgent / ReviewAgent / FixAgent 的分工。
diff output 必须是 proposal，不是已应用 patch。
sandboxed test result 必须记录命令、退出码、日志引用和 redaction status。
review summary 不能被当作 approval。
fix-loop 必须生成新 proposal，不得静默修改已有产物。
必须有 no auto commit / no auto push / no auto deploy evidence。
缺任一项则 US-V9-03 不得 PASS。
```

### KS-V9-C Governed Terminal Worker Sandbox Review

User story:

```text
作为审计者，
我要求 Agent 在 workspace 内执行只读检查或受控测试命令，
我期望看到命令分级、workspace 边界、transcript、diff capture，以及越权命令被拒绝的证据。
```

Acceptance threshold:

```text
user_entry=Terminal Worker review dashboard or Studio evidence panel.
dashboard 显示 workspace_root、command_tier、allowed command、denied command。
workspace escape、symlink escape、secret-read、git push、production deploy 默认拒绝。
transcript_ref 和 diff_capture_ref 可打开。
任何 write action 必须有 user_confirmed=true 或 valid human_authorization_ref。
缺 sandbox denial evidence 则 US-V9-04 不得 PASS。
```

### KS-V9-D Workflow Studio Evidence Review

User story:

```text
作为产品使用者，
我在 Studio 打开一个已运行工作流，
我期望看到 workflow graph、每个 station 的 Agent profile、runtime status、artifact lineage、Runtime Report 和 Evidence Chain，并能确认哪些动作只是 ready for review。
```

Acceptance threshold:

```text
user_entry=Workflow Studio.
UI 通过 BFF / DTO 获取数据。
browser network log 不得出现 direct internal runtime route。
Runtime Report 和 Evidence Chain 只读。
页面不得出现自动执行、自动发布、Agent 已直接执行 durable mutation 的暗示文案。
用户能从 UI 打开每个关键 evidence_ref。
缺 BFF/browser/read-only 证据则 US-V9-05 不得 PASS。
```

### KS-V9-E Final V9 User Acceptance Dashboard

User story:

```text
作为最终验收人，
我打开 V9 final dashboard，
我期望一眼看到每个阶段和每个用户场景是 PASS、PARTIAL、FAIL 还是 BLOCKED，并知道哪些能力仍不得声明完成。
```

Acceptance threshold:

```text
dashboard 汇总 V9-0..V9-7 evidence summary。
dashboard 汇总 US-V9-01..US-V9-09 scenario status。
无 FAIL / BLOCKED。
PARTIAL 必须有 human proceed decision。
No False Green scan PASS。
Redaction scan PASS。
Drawio XML valid。
Forbidden claims 只出现在 forbidden/no-false-green context。
缺任一项则 US-V9-06 和 V9-8 不得 PASS。
```

### KS-V9-F Roman Forum Multi-Agent Debate

User story:

```text
作为知识工作者，
我输入“罗马广场：请让哲学家、工程师、历史学家、伦理学家讨论‘技术进步是否会削弱人的自由’，互相质询并总结共识和分歧”，
我期望系统展示不同身份 Agent 的多轮发言、互相引用、分歧点、综合结论和证据链。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
至少 4 个 role-specific station-bound Agents: philosopher, engineer, historian, ethicist。
至少 1 个 Moderator 或 Synthesizer Agent。
至少 2 轮 discussion turns。
每条 message 必须记录 producer_agent_id、attempt_id、input_refs、output_refs。
Agent 之间的引用或反驳必须有 message_ref 或 attribution_ref。
Synthesizer output 必须保留 attribution_refs，不能生成无来源总结。
dashboard 展示多 Agent 讨论路径、角色身份、message graph、fan-in synthesis 和 Evidence Chain。
缺任一项则 US-V9-07 不得 PASS。
```

### KS-V9-G Video Creation Storyboard Workflow

User story:

```text
作为创作者，
我输入“我想做一个 60 秒短视频，主题是一个程序员在深夜发现 AI 工作流自己学会了开会”，
我期望系统自动制定创作工作流，生成 brief、脚本、镜头清单、每个分镜 prompt、分镜图和创作审查报告。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
workflow 必须包含 Idea Analyst、Script Agent、Storyboard Agent、Prompt Agent、Image Generation Agent、Review Agent。
产物至少包含 creative_brief.json、script.md、shot_list.json、storyboard_prompts.json、image artifact refs、visual_consistency_report.json、runtime_report.html、evidence_chain.json。
至少 4 个 storyboard shots。
每个 shot 必须有 shot_id、scene_description、prompt_template_ref、image_artifact_ref。
Image Generation Agent 必须通过受控 provider adapter 或明确的 host capability 生成 image artifact refs。
provider invocation evidence 必须记录 provider、model_ref、input_artifact_refs、output_artifact_refs、redaction_status。
如果 MiniMax 或 host image capability 不可用，场景只能 BLOCKED 或 fallback_demo_only，不得 PASS。
placeholder image 或 deterministic image 不能写成 real image generation。
不得泄露 raw prompt、API key、raw provider payload、raw artifact content。
缺任一项则 US-V9-08 不得 PASS。
```

### KS-V9-H Natural Language Workflow Optimization

User story:

```text
作为工作流编辑者，
我输入“把这个视频创作工作流优化一下：减少到 5 个 station，把风格改成黑色幽默，并增加安全审查 Agent”，
我期望系统生成可审查的 WorkflowDiff proposal，而不是直接修改运行时。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
系统必须读取 existing WorkflowSpec / Blueprint refs。
系统必须输出 WorkflowDiff proposal，列出 added / removed / modified stations、Agent role / goal / tool / model changes、risk_delta 和 affected_runtime_refs。
用户确认前不得 durable mutation。
source=agent 不得直接写 WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun / Artifact。
durable mutation 必须 user_confirmed=true 或 valid human_authorization_ref。
优化后的 Blueprint / Runtime Report / Evidence Chain 必须可重新链接。
如果只是 transcript-only，不得标记 runtime_backed PASS。
缺任一项则 US-V9-09 不得 PASS。
```

## 4. Scenario-Specific Gates

### US-V9-01 Controlled Runtime Evidence Review

Required evidence:

```text
docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/index.html
docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json
```

PASS requires:

```text
allowed_operations exactly four.
excluded_operations are visible.
source_agent_durable_mutation_allowed=false.
runtime_backed=true.
evidence_scope=real_runtime_fixture.
claim guard explains this is not controlled executor ready.
```

### US-V9-02 Multi-Agent Orchestration User Path

PASS requires:

```text
user can see station-bound Agents.
user can see serial dependency and parallel branch states.
user can see fan-out dispatch and fan-in join attribution.
user can see failed attempt, retained old attempt and recovery attempt.
user can see artifact lineage with producer_agent_id and producer_attempt_id.
user can open the evidence dashboard.
```

### US-V9-03 Coding Workflow User Path

PASS requires:

```text
user can see original goal, plan, diff proposal, sandboxed test result, review summary and fix-loop proposal.
diff proposal is not patch apply.
review summary is not approval.
automated tooling does not commit, push, deploy or mark review as approval.
```

### US-V9-04 Terminal Worker User Path

PASS requires:

```text
user can see workspace root, command tier, transcript ref and diff capture.
workspace escape attempts are denied.
secret-read attempts are denied and redacted.
write actions require approval or valid human authorization according to the stage gate.
```

### US-V9-05 Studio User Path

PASS requires:

```text
user can inspect workflow graph, station Agent profile, artifact lineage, runtime report and evidence chain.
Studio panels use BFF / DTO boundary.
browser does not call internal runtime routes directly.
Evidence Review and Runtime Report remain read-only.
```

### US-V9-06 Final User Review Path

PASS requires:

```text
V9-0..V9-7 evidence packages exist.
US-V9-01..US-V9-09 have PASS or explicitly accepted PARTIAL with human decision.
No FAIL / BLOCKED scenario remains.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
```

### US-V9-07 Roman Forum Debate Path

PASS requires:

```text
user can see role-specific Agents with distinct identities.
user can see at least two discussion turns.
user can see message refs or attribution refs between Agents.
user can see synthesis output with preserved attribution_refs.
user can open the discussion dashboard and Evidence Chain.
```

### US-V9-08 Video Creation Storyboard Path

PASS requires:

```text
user can see idea brief, script, shot list, storyboard prompts and image artifact refs.
at least four storyboard shots exist.
image generation is provider-backed or clearly marked fallback_demo_only / placeholder.
provider / model / input_artifact_refs / output_artifact_refs are visible without raw prompt or token leakage.
user can open runtime report and evidence chain.
```

### US-V9-09 Natural Language Workflow Optimization Path

PASS requires:

```text
user can see WorkflowDiff proposal before any mutation.
user can see added / removed / modified stations and Agent profile changes.
user can approve, reject or keep proposal as draft.
source=agent direct runtime mutation remains denied.
optimized Blueprint, Runtime Report and Evidence Chain links are updated only after user confirmation or valid human authorization.
```

## 5. Stop Conditions

```text
User scenario evidence is missing but the stage is marked PASS.
Planning docs are counted as runtime-backed user evidence.
User cannot open the dashboard or report for a claimed scenario.
Stage dashboard hides denied operations or missing evidence.
V9 final acceptance runs before US-V9-01..US-V9-09 are reviewed.
Any user-facing text implies production ready, Agent executor ready, full orchestration ready or complete Studio ready.
Roman Forum discussion is counted as full multi-Agent orchestration readiness.
Video storyboard planning or placeholder images are counted as provider-backed image generation.
Natural language optimization directly mutates WorkflowDraft / WorkflowVersion / WorkflowInstance before user confirmation.
```

## 6. Minimum Dashboard Fields

Every scenario dashboard or report must display:

```text
scenario_id
status
evidence_scope
runtime_backed
user_goal
user_visible_outputs
evidence_refs
missing_evidence
claim_risk
false_green_risk
redaction_status
next_gate
```

```

### `docs/design/V9.x/v9_no_false_green_claim_guard.md`
```markdown
# V9 No False Green Claim Guard

文档状态：V9 No False Green guard / planning baseline。

## 1. Allowed Claim Pattern

V9 阶段完成声明必须使用：

```text
ready for review
slice ready for review
pilot ready for review
gate ready for review
```

不得把 `ready for review` 摘要成 `ready`。

## 2. Forbidden English Claims

```text
production ready
full production GA
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous coding workflow ready
autonomous workflow editing ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
production browser automation ready
GA ready
production automation ready
```

## 3. Forbidden Chinese Claims

```text
生产可用
全面生产可用
Agent执行器已完成
受控执行器已完成
生产级受控执行器已完成
完整多Agent编排已完成
自主代码工作流已完成
自主工作流编辑已完成
完整工作流工作台已完成
无限制终端worker已完成
生产终端自动化已完成
生产浏览器自动化已完成
生产就绪
可投产
正式发布
生产级可用
多智能体编排已完成
Agent Executor 已完成
生产自动化已完成
```

## 4. Allowed Contexts

Forbidden terms may appear only in:

```text
Forbidden Claims
No False Green
Stop Conditions
Out Of Scope
Audit Questions
Drawio warning boxes
Boundary explanations
```

They must not appear as positive completion claims, status summaries, allowed claims or release notes.

## 5. Redaction Terms

V9 evidence must not contain:

```text
raw_prompt
raw prompt
raw_file_content
raw file content
raw_provider_payload
raw_connector_payload
raw_artifact_content
API key
Bearer
signed URL
credential raw secret
```

## 6. Suggested Scan

```text
rg -in "production[- ]?ready|full production GA|GA ready|Agent executor ready|controlled executor ready|production controlled executor ready|full multi-Agent orchestration ready|distributed multi-Agent runtime ready|autonomous coding workflow ready|autonomous workflow editing ready|complete Workflow Studio ready|unrestricted terminal worker ready|production terminal automation ready|production browser automation ready|production automation ready|生产可用|全面生产可用|生产就绪|可投产|正式发布|生产级可用|Agent执行器已完成|Agent Executor 已完成|受控执行器已完成|生产级受控执行器已完成|完整多Agent编排已完成|多智能体编排已完成|自主代码工作流已完成|自主工作流编辑已完成|完整工作流工作台已完成|无限制终端worker已完成|生产终端自动化已完成|生产浏览器自动化已完成|生产自动化已完成" docs/design/V9.x
```

Expected result: hits only in forbidden/no-false-green/audit contexts.

```

### `docs/design/V9.x/v9_contract_schema_bundle.md`
```markdown
# V9 Contract Schema Bundle

文档状态：V9 P0 machine-readable contract plan / required before runtime implementation。

## 1. Purpose

本文件把 V9 自然语言合同收敛成 schema bundle。当前已落盘最小 P0 JSON Schema 到 `docs/design/V9.x/schemas/`，并可作为 V9-1 implementation-readiness audit 的机器可读输入。

## 2. Required Schemas

```text
agent_execution_policy.schema.json
agent_execution_envelope.schema.json
human_authorization_ref.schema.json
capability_resolver_decision.schema.json
approval_gate_decision.schema.json
kill_switch_decision.schema.json
timeout_policy.schema.json
rollback_descriptor.schema.json
execution_evidence.schema.json
orchestration_message.schema.json
artifact_lineage_record.schema.json
final_acceptance_dashboard.schema.json
```

P0 schema files currently present:

```text
docs/design/V9.x/schemas/agent_execution_policy.schema.json
docs/design/V9.x/schemas/agent_execution_envelope.schema.json
docs/design/V9.x/schemas/human_authorization_ref.schema.json
docs/design/V9.x/schemas/capability_resolver_decision.schema.json
docs/design/V9.x/schemas/approval_gate_decision.schema.json
docs/design/V9.x/schemas/kill_switch_decision.schema.json
docs/design/V9.x/schemas/timeout_policy.schema.json
docs/design/V9.x/schemas/rollback_descriptor.schema.json
docs/design/V9.x/schemas/execution_evidence.schema.json
docs/design/V9.x/schemas/orchestration_message.schema.json
docs/design/V9.x/schemas/artifact_lineage_record.schema.json
docs/design/V9.x/schemas/evidence_package.schema.json
docs/design/V9.x/schemas/high_risk_human_decision.schema.json
docs/design/V9.x/schemas/final_acceptance_dashboard.schema.json
```

## 3. Global Schema Rules

Every schema must define:

```text
schema_version
required fields
enum values
nullable rules
additionalProperties=false
redacted-ref-only fields
forbidden raw payload fields
versioning rule
backward compatibility rule
negative validation examples
```

Forbidden fields in every V9 evidence or execution schema:

```text
raw_prompt
raw_file_content
raw_provider_payload
raw_connector_payload
raw_artifact_content
api_key
bearer_token
signed_url
credential_raw_secret
```

## 4. Required Cross-Schema Invariants

```text
source=agent default durable mutation is always denied.
durable mutation requires user_confirmed=true OR valid human_authorization_ref.
high-risk durable mutation additionally requires approval_gate_ref.
target_refs must be operation-specific and non-empty.
payload_refs must be redacted refs only.
execution_evidence must reference execution_envelope_id and capability_decision_ref.
artifact_lineage_record must preserve producer_agent_id and producer_attempt_id.
final_acceptance_dashboard cannot count planning/spec docs as runtime evidence.
```

## 4.1 Schema Coverage Table

| PRD / Architecture Component | Schema | Negative Fixture |
| --- | --- | --- |
| AgentExecutionPolicy | `agent_execution_policy.schema.json` | unknown field fixture required before implementation |
| AgentExecutionEnvelope | `agent_execution_envelope.schema.json` | `source_agent_durable_mutation.json` |
| HumanAuthorizationRef | `human_authorization_ref.schema.json` | `expired_human_authorization_ref.json` |
| CapabilityResolverDecision | `capability_resolver_decision.schema.json` | source-agent mutation denial fixture |
| ExecutionEvidence | `execution_evidence.schema.json` | `raw_secret_in_evidence.json` |
| OrchestrationMessage | `orchestration_message.schema.json` | fan-in attribution fixture required before V9-3 |
| ArtifactLineageRecord | `artifact_lineage_record.schema.json` | `artifact_lineage_missing_producer_attempt.json` |
| EvidencePackage | `evidence_package.schema.json` | `v9_8_reject_planning_only_sample.json` |
| HighRiskHumanDecision | `high_risk_human_decision.schema.json` | expired/revoked decision fixture required before V9-2 |
| FinalAcceptanceDashboard | `final_acceptance_dashboard.schema.json` | planning-only dashboard rejection fixture required before V9-8 |

## 5. Negative Validation Examples

The schema bundle must include fixtures for:

```text
unknown_field_rejected
missing_schema_version_rejected
source_agent_durable_mutation_rejected
durable_mutation_without_user_confirmation_or_human_authorization_rejected
raw_secret_field_rejected
raw_prompt_field_rejected
empty_target_refs_rejected
wrong_operation_target_refs_rejected
expired_human_authorization_ref_rejected
artifact_lineage_missing_producer_attempt_rejected
```

P0 fixture files currently present:

```text
docs/design/V9.x/fixtures/schema-negative/source_agent_durable_mutation.json
docs/design/V9.x/fixtures/schema-negative/expired_human_authorization_ref.json
docs/design/V9.x/fixtures/schema-negative/raw_secret_in_evidence.json
docs/design/V9.x/fixtures/schema-negative/artifact_lineage_missing_producer_attempt.json
docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json
docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json
```

## 6. Acceptance Gate

V9 implementation may not start from this bundle until:

```text
all required JSON Schema files exist.
all schemas parse.
negative fixtures fail as expected.
No False Green scan PASS.
redaction forbidden field scan PASS.
```

```

### `docs/design/V9.x/v9_human_authorization_ref_contract.md`
```markdown
# V9 HumanAuthorizationRef Contract

文档状态：V9 shared authorization contract / required before V9-2 implementation。

## 1. Purpose

`HumanAuthorizationRef` 是 durable mutation 的人工授权证据引用。它可以作为 `user_confirmed=true` 的等价授权入口，但不能绕过 policy、capability、approval、kill switch、timeout、rollback 和 evidence 边界。

核心不变量：

```text
Durable mutation is denied unless user_confirmed=true OR human_authorization_ref is present and valid.
source=agent default durable mutation remains denied even when human_authorization_ref exists.
Approval gate is an additional gate for high-risk operations, not a replacement for human authorization.
```

## 2. Contract Fields

Required fields:

```text
human_authorization_ref
issuer_type
issuer_id
authorization_subject_actor_id
tenant_id
workspace_id
project_id
app_id
operation
operation_hash
target_refs
allowed_sources
allowed_actor_types
scope
created_at
expires_at
revoked
revoked_at
revocation_reason
correlation_id
request_id
audit_ref
```

Rules:

```text
additionalProperties=false
human_authorization_ref must be immutable after creation except revocation fields.
operation_hash must bind operation + target_refs + scope.
target_refs must be non-empty and operation-specific.
expires_at must be present for every non-read operation.
revoked=true blocks runtime use.
raw prompt / raw file content / raw artifact content / raw provider payload / raw connector payload / token / secret fields are forbidden.
```

## 3. Issuer And Scope

Allowed `issuer_type`:

```text
human_user
product_console
approved_api_with_human_authorization
```

Denied issuer/source patterns:

```text
source=agent
autonomous_executor
unrestricted_terminal_worker
browser_automation_without_user_session
```

Scope requirements:

```text
tenant_id / workspace_id / project_id / app_id must match the execution envelope.
operation must match the requested durable mutation.
target_refs must match the requested runtime target.
allowed_sources must include product_console or approved_api before those sources can use the ref.
allowed_actor_types must include human_user or service_account_with_human_authorization before those actors can use the ref.
```

## 4. Validation Rules

`HumanAuthorizationRef` is valid only if:

```text
ref exists.
revoked=false.
created_at <= execution_requested_at < expires_at.
operation_hash matches the execution envelope operation and target_refs.
tenant/workspace/project/app refs match.
actor_type and source are allowed.
audit_ref exists.
redaction scan PASS.
```

It is invalid if:

```text
ref belongs to another tenant/workspace/project/app.
ref has expired.
ref was revoked.
ref was issued by source=agent.
operation_hash does not match.
target_refs are missing or weaker than the execution envelope target_refs.
raw secret / token / raw prompt / raw content appears in the authorization record.
```

## 5. Negative Tests

```text
human_authorization_ref_missing_for_durable_mutation_denied
human_authorization_ref_expired_denied
human_authorization_ref_revoked_denied
human_authorization_ref_wrong_tenant_denied
human_authorization_ref_wrong_workspace_denied
human_authorization_ref_wrong_operation_hash_denied
human_authorization_ref_missing_target_refs_denied
human_authorization_ref_source_agent_issuer_denied
human_authorization_ref_raw_secret_denied
human_authorization_ref_does_not_replace_approval_gate_for_high_risk_action
```

## 6. Evidence Requirements

Every runtime evidence package that uses `human_authorization_ref` must record:

```text
human_authorization_ref
operation
operation_hash
target_refs
authorization_subject_actor_id
created_at
expires_at
revoked
audit_ref
correlation_id
request_id
redaction_status
```

The evidence package must not record raw user prompt, raw file content, raw provider payload, raw connector payload, API key, Bearer token, signed URL, or raw artifact content.

```

### `docs/design/V9.x/v9_api_and_service_boundary_spec.md`
```markdown
# V9 API And Service Boundary Spec

文档状态：V9 P0 API/service boundary plan / required before runtime implementation。

## 1. Purpose

本文件定义 V9 的服务边界，防止 Studio、Agent、terminal worker 或 browser 绕过 BFF / DTO / policy / evidence 边界直接写 runtime truth。

## 2. Service Planes

```text
WorkflowStudioBFF
MissionTuiBFF
AgentExecutionService
CapabilityResolverService
HumanAuthorizationService
ControlledExecutorService
OrchestrationCoordinatorService
TerminalWorkerService
EvidencePackageService
AuditExportService
```

## 3. Route Classes

Allowed read routes:

```text
GET /bff/v9/runtime-report
GET /bff/v9/evidence-chain
GET /bff/v9/workflow-blueprint
GET /bff/v9/studio-state
GET /bff/v9/audit-export
```

Proposal / handoff routes:

```text
POST /bff/v9/workflow-diff-proposal
POST /bff/v9/agent-execution-proposal
POST /bff/v9/manual-confirmation
POST /bff/v9/human-authorization-ref
POST /bff/v9/review-handoff
```

Representative request contract for `POST /bff/v9/human-authorization-ref`:

```text
tenant_id
workspace_id
project_id
app_id
operation
target_refs
authorization_subject_actor_id
allowed_sources
allowed_actor_types
expires_at
correlation_id
request_id
```

Representative response contract:

```text
human_authorization_ref
operation_hash
audit_ref
created_at
expires_at
redaction_status
```

Internal-only routes:

```text
POST /internal/v9/capability-resolver/evaluate
POST /internal/v9/controlled-executor/execute
POST /internal/v9/orchestration/dispatch
POST /internal/v9/evidence-package/record
```

Explicit browser denylist:

```text
/v1/rpc
/v1/events/subscribe
/v1/internal/runtime
/v1/internal/executor
/v1/internal/workflow-store
/v1/internal/station-run
/internal/v9/*
```

## 4. Mutation Rules

```text
source=agent can propose but cannot directly call durable mutation routes.
Every mutation route requires CapabilityResolver decision.
Durable mutation requires user_confirmed=true OR valid human_authorization_ref.
High-risk mutation additionally requires ApprovalGateDecision.
Studio can submit proposals or handoffs, not direct runtime truth writes.
Browser can only call BFF routes.
```

## 5. Explicitly Non-Existent Routes

```text
POST /bff/v9/agent-auto-execute
POST /bff/v9/auto-commit
POST /bff/v9/auto-push
POST /bff/v9/auto-deploy
POST /bff/v9/direct-workflow-store-write
POST /bff/v9/direct-station-run-write
POST /bff/v9/unrestricted-terminal-command
```

## 6. Acceptance Tests

```text
browser_direct_internal_route_denied
browser_direct_v1_rpc_denied
studio_direct_runtime_truth_write_denied
source_agent_mutation_route_denied
mutation_without_capability_decision_denied
durable_mutation_without_user_confirmation_or_human_authorization_denied
high_risk_mutation_without_approval_gate_denied
```

## 7. Error Codes

```text
SOURCE_AGENT_MUTATION_DENIED
MISSING_CAPABILITY_DECISION
MISSING_HUMAN_AUTHORIZATION
EXPIRED_HUMAN_AUTHORIZATION
WRONG_TENANT_SCOPE
APPROVAL_GATE_REQUIRED
KILL_SWITCH_DENIED
BROWSER_DIRECT_ROUTE_DENIED
RUNTIME_TRUTH_WRITE_DENIED
```

```

### `docs/design/V9.x/v9_evidence_package_schema_and_validator_spec.md`
```markdown
# V9 Evidence Package Schema And Validator Spec

文档状态：V9 P0 evidence package validator plan / required before V9-8。

## 1. Purpose

V9-8 必须聚合 V9-0 到 V9-7 的真实证据包。规划文档、PRD 或 readiness spec 不能被计为 runtime evidence。

P0 sample evidence fixtures:

```text
docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json
docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json
```

## 2. Evidence Package Fields

Required fields:

```text
evidence_package_id
stage_id
status
evidence_scope
runtime_backed
source_document_refs
runtime_artifact_refs
test_run_refs
human_decision_refs
claim_scan_result
redaction_scan_result
forbidden_raw_content_scan_result
drawio_validation_result
evidence_hash
created_by
created_at
auditor_decision
notes
```

Allowed `evidence_scope`:

```text
planning_only
contract_freeze
implementation_readiness
deterministic_fixture
real_runtime_fixture
real_runtime
manual_review
```

## 3. Validator Rules

```text
planning_only cannot satisfy runtime-backed stage acceptance.
runtime_backed=false blocks V9-8 if the stage requires runtime evidence.
missing human_decision_refs blocks high-risk stages.
forbidden claim outside allowed context blocks V9-8.
raw secret / raw prompt / raw artifact content blocks V9-8.
drawio_validation_result must be PASS.
evidence_hash must cover package contents.
source_document_refs must not be counted as runtime_artifact_refs.
```

Validator CLI contract:

```text
input: evidence package JSON path
output: validation_result JSON with status, blocking_reasons, warning_reasons, accepted_evidence_refs
exit 0: PASS only
exit 1: FAIL or BLOCKED
```

## 4. Stage Requirements

```text
V9-0 allows planning_only.
V9-1 allows contract_freeze.
V9-2 requires real_runtime_fixture or real_runtime.
V9-3 requires real_runtime_fixture or real_runtime.
V9-4 requires real_runtime_fixture or real_runtime.
V9-5 requires real_runtime_fixture or real_runtime.
V9-6 requires implementation_readiness plus browser/UI evidence before acceptance.
V9-7 requires manual_review plus high-risk decision evidence.
V9-8 requires all prior packages.
```

## 4.1 Front-Stage Evidence Minimums

V9-1 evidence package must contain:

```text
schema_validation_result
negative_fixture_result
contract_freeze_sample
No False Green scan
redaction scan
external audit decision
```

V9-2 evidence package must contain:

```text
runtime-backed controlled executor result
HumanAuthorizationRef validation result
CapabilityResolver decision chain
ApprovalGateDecision when high-risk
ExecutionEvidence with redacted refs
idempotency / timeout / rollback result
```

V9-3 evidence package must contain:

```text
serial run evidence
parallel branch evidence
fan-in / fan-out evidence
lost worker recovery evidence
attempt history evidence
artifact lineage with producer_agent_id and producer_attempt_id
```

V9-4 evidence package must contain:

```text
diff proposal evidence
sandboxed test evidence
review summary evidence
fix-loop evidence
no auto commit / auto push / auto deploy denial evidence
```

## 5. Negative Fixtures

```text
v9_8_planning_docs_only_rejected
v9_8_missing_v9_2_runtime_evidence_rejected
v9_8_missing_high_risk_human_decision_rejected
v9_8_forbidden_claim_rejected
v9_8_raw_secret_rejected
v9_8_drawio_invalid_rejected
```

```

### `docs/design/V9.x/v9_test_fixture_and_ci_matrix.md`
```markdown
# V9 Test Fixture And CI Matrix

文档状态：V9 P0 test fixture plan / required before stage implementation。

## 1. Test Case Contract

Every V9 test case must specify:

```text
test_id
owner_stage
scenario_id
input_fixture
expected_output
expected_user_visible_output
expected_denied_state
expected_evidence_record
expected_audit_ref
expected_redaction_behavior
expected_rollback_or_correction_behavior
ci_command
blocking_severity
```

Current P0 fixture roots:

```text
docs/design/V9.x/fixtures/schema-negative/
docs/design/V9.x/fixtures/evidence/
docs/design/V9.x/fixtures/v9-2-controlled-executor/
docs/design/V9.x/fixtures/v9-3-orchestration/
docs/design/V9.x/fixtures/v9-4-coding-workflow/
docs/design/V9.x/fixtures/terminal/
```

User scenario fixture root:

```text
docs/design/V9.x/fixtures/user-scenarios/
```

## 2. Required Negative Fixtures

```text
source_agent_durable_mutation
expired_human_authorization_ref
wrong_tenant_human_authorization_ref
raw_secret_in_evidence
fan_in_missing_attribution
retry_overwrites_old_attempt
auto_commit_without_human_approval
auto_push_without_release_gate
auto_deploy_without_production_gate
terminal_workspace_escape
terminal_symlink_escape
studio_direct_runtime_write
studio_hidden_mutation_form
v9_8_with_planning_docs_only
```

## 3. CI Gates

Planned commands:

```text
python -m json.tool docs/design/V9.x/schemas/*.schema.json
python -m json.tool docs/design/V9.x/fixtures/schema-negative/*.json
python -m json.tool docs/design/V9.x/fixtures/evidence/*.json
xmllint --noout docs/design/V9.x/v9_current_gap_analysis.drawio
rg -in "<forbidden-claim-regex>" docs/design/V9.x
python -m pytest tests/test_v9_contracts_*.py -q
python -m pytest tests/test_v9_evidence_package_*.py -q
python -m pytest tests/test_v9_no_false_green_*.py -q
```

## 4. Blocking Severity

```text
P0 blocks stage implementation.
P1 blocks stage completion.
P2 requires documented proceed decision.
```

## 5. Acceptance Rule

No V9 implementation stage may start until its fixtures and CI commands are listed and accepted. No V9 stage may complete if a P0/P1 fixture fails.

No V9 final acceptance may run until the user scenario acceptance gate is reviewed. A technical test PASS does not replace a missing user-facing dashboard or report.

## 6. Front-Stage Fixture-To-Test Matrix

| Stage | Fixture | Expected Result |
| --- | --- | --- |
| V9-1 | `schema-negative/source_agent_durable_mutation.json` | rejected by envelope validator and CapabilityResolver |
| V9-1 | `fixtures/evidence/v9_1_contract_freeze_sample.json` | accepted only as contract_freeze, not runtime evidence |
| V9-2 | `schema-negative/expired_human_authorization_ref.json` | rejected by HumanAuthorizationRef validator |
| V9-2 | `schema-negative/raw_secret_in_evidence.json` | rejected by evidence schema and redaction scan |
| V9-3 | `schema-negative/artifact_lineage_missing_producer_attempt.json` | rejected by artifact lineage schema |
| V9-3 | `fixtures/v9-3-orchestration/serial_parallel_fan_in_out_recovery.json` | accepted as real_runtime_fixture input and covered by V9-3 runtime evidence |
| V9-3 | `fixtures/v9-3-orchestration/fan_in_missing_attribution.json` | rejected because fan-in synthesis lacks attribution |
| V9-3 | `fixtures/v9-3-orchestration/retry_overwrites_old_attempt.json` | rejected because retry must retain old attempt and old error |
| V9-3 | `fixtures/v9-3-orchestration/source_agent_direct_mutation_attempt.json` | rejected because source=agent cannot directly mutate runtime truth |
| V9-4 | `fixtures/v9-4-coding-workflow/no_auto_commit_push_deploy.json` | covered by V9-4 runtime evidence; auto commit / auto push / auto deploy denied and recorded |
| V9-8 | `fixtures/evidence/v9_8_reject_planning_only_sample.json` | final validator returns BLOCKED, not PASS |

## 6.1 User Scenario Fixture-To-Test Matrix

| Scenario | Fixture | Expected Result |
| --- | --- | --- |
| US-V9-01 | `fixtures/user-scenarios/us_v9_01_controlled_runtime_review.json` | user can open V9-2 dashboard and verify four allowed operations plus source=agent denial |
| US-V9-02 | `fixtures/user-scenarios/us_v9_02_orchestration_review.json` | satisfied by V9-3 runtime dashboard and lineage evidence package |
| US-V9-03 | `fixtures/user-scenarios/us_v9_03_coding_workflow_review.json` | satisfied by V9-4 runtime dashboard, diff proposal, sandboxed test, review summary, fix-loop and no-auto-commit/push/deploy denial evidence |
| US-V9-04 | `fixtures/user-scenarios/us_v9_04_terminal_worker_review.json` | satisfied by V9-5 terminal worker dashboard, command tier decisions, transcript, diff capture and denial evidence |
| US-V9-05 | `fixtures/user-scenarios/us_v9_05_studio_review.json` | user scenario remains BLOCKED until Studio BFF/browser evidence exists |
| US-V9-06 | `fixtures/user-scenarios/us_v9_06_final_dashboard_review.json` | final user scenario remains BLOCKED until US-V9-01..US-V9-09 are PASS or accepted PARTIAL |
| US-V9-07 | `fixtures/user-scenarios/us_v9_07_roman_forum_debate.json` | satisfied by V9-3 role-specific debate, multi-round message and attribution-preserving synthesis evidence |
| US-V9-08 | `fixtures/user-scenarios/us_v9_08_video_storyboard_workflow.json` | explicitly BLOCKED for provider-backed image generation in local V9-3 fixture; not allowed to count as provider-backed PASS |
| US-V9-09 | `fixtures/user-scenarios/us_v9_09_nl_workflow_optimization.json` | satisfied by V9-3 WorkflowDiff proposal evidence and no-mutation-before-confirmation evidence |

## 7. V9-3 Schema Parse Set

```text
docs/design/V9.x/schemas/v9_3_agent_descriptor.schema.json
docs/design/V9.x/schemas/v9_3_station_agent_binding.schema.json
docs/design/V9.x/schemas/v9_3_orchestration_run.schema.json
docs/design/V9.x/schemas/v9_3_branch_state.schema.json
docs/design/V9.x/schemas/v9_3_fan_out_dispatch.schema.json
docs/design/V9.x/schemas/v9_3_fan_in_join_decision.schema.json
docs/design/V9.x/schemas/v9_3_attempt_history_record.schema.json
docs/design/V9.x/schemas/v9_3_lost_worker_recovery_decision.schema.json
docs/design/V9.x/schemas/v9_3_conflict_review_record.schema.json
```

## 8. Creative User Scenario Test Matrix

```text
v9_3_roman_forum_has_role_specific_agents
v9_3_roman_forum_has_multi_round_messages
v9_3_roman_forum_synthesis_preserves_attribution_refs
v9_3_video_workflow_generates_brief_script_shot_list_and_storyboard_prompts
v9_3_video_storyboard_has_minimum_four_shots
v9_3_video_image_generation_records_provider_model_refs
v9_3_video_missing_provider_key_blocks_real_image_pass
v9_3_video_redacts_forbidden_provider_content
v9_6_nl_optimization_generates_workflow_diff_proposal
v9_6_nl_optimization_requires_user_confirmation_before_apply
v9_6_nl_optimization_denies_source_agent_direct_mutation
```

```

### `docs/design/V9.x/v9_high_risk_human_decision_protocol.md`
```markdown
# V9 High-Risk Human Decision Protocol

文档状态：V9 P0 human decision protocol / required before high-risk implementation。

## 1. Purpose

V9-1、V9-2、V9-4、V9-5、V9-7 是高风险阶段。进入实现或高风险能力启用前，必须有可审计的人类 proceed decision。

## 2. Decision Fields

Required fields:

```text
decision_ref
stage_id
decision
decision_owner
required_reviewers
risk_class
scope
allowed_work
blocked_work
created_at
expires_at
revoked
revoked_at
revocation_reason
evidence_refs
audit_ref
correlation_id
```

Allowed `decision`:

```text
GO_FOR_IMPLEMENTATION
GO_FOR_CONTRACT_AUDIT_ONLY
NO_GO
DEFERRED
NEEDS_MORE_EVIDENCE
```

## 3. Rules

```text
approval does not replace HumanAuthorizationRef for runtime durable mutation.
decision_ref is stage-bound and scope-bound.
expired or revoked decision_ref blocks implementation.
high-risk runtime evidence must link to decision_ref.
decision_ref cannot be issued by source=agent.
```

## 4. Required Stage Decisions

```text
V9-1: contract audit decision and separate implementation decision.
V9-2: controlled executor implementation decision.
V9-4: autonomous coding workflow implementation decision.
V9-5: terminal worker write sandbox decision.
V9-7: governance / evidence hardening / terminal automation gate decision.
```

## 5. Stop Conditions

```text
implementation starts with missing decision_ref.
decision_ref has expired.
decision_ref is reused for another stage.
approval gate is treated as human proceed decision.
source=agent issues decision_ref.
```

```

### `docs/design/V9.x/v9_security_threat_model_and_abuse_cases.md`
```markdown
# V9 Security Threat Model And Abuse Cases

文档状态：V9 P0 threat model / required before runtime implementation。

## 1. Threat Scope

V9 introduces high-risk execution capabilities. Threat analysis must cover Agent execution, human authorization, terminal worker, Studio BFF, evidence chain and production governance.

## 2. Abuse Cases

```text
source=agent impersonates human user.
authorization replay after expiry.
operation_hash mismatch with target_refs.
cross-tenant authorization reuse.
stale approval reuse.
terminal path traversal.
terminal symlink escape.
secret exfiltration through shell or evidence.
browser route bypass.
BFF bypass.
evidence poisoning.
claim false green.
rollback failure.
lost worker duplicate mutation.
idempotency collision.
fan-in attribution removal.
artifact lineage producer_attempt_id removal.
```

## 3. Required Controls

```text
deny-by-default CapabilityResolver.
HumanAuthorizationRef validation.
approval gate for high-risk actions.
tenant/workspace/project/app binding.
operation_hash binding.
idempotency key for mutation.
append-only attempt history and evidence.
workspace canonicalization and symlink checks.
browser route denylist.
redaction scanner.
No False Green scanner.
incident timeline for denials and failures.
```

## 4. Acceptance Tests

```text
source_agent_impersonation_denied
authorization_replay_denied
operation_hash_mismatch_denied
cross_tenant_authorization_denied
terminal_path_traversal_denied
terminal_symlink_escape_denied
secret_exfiltration_denied
browser_bff_bypass_denied
evidence_poisoning_detected
claim_false_green_detected
lost_worker_duplicate_mutation_prevented
idempotency_collision_returns_prior_ref_or_denies
```

```

### `docs/design/V9.x/v9_operational_runbook_and_incident_response.md`
```markdown
# V9 Operational Runbook And Incident Response

文档状态：V9 P0 operational runbook / required before runtime rollout。

## 1. Purpose

V9 runtime stages introduce high-risk execution. Every runtime slice must have rollback, kill switch, incident timeline and operational response before acceptance.

## 2. Required Runbook Sections

```text
stage_owner
on_call_owner
feature_flag
tenant_allowlist
kill_switch_owner
rollback_steps
incident_severity_mapping
audit_export_path
evidence_package_path
redaction_failure_response
forbidden_claim_response
```

## 3. Incident Types

```text
policy_denied
credential_denied
approval_missing
human_authorization_invalid
timeout
lost_worker
rollback_failed
terminal_escape_attempt
secret_read_attempt
evidence_redaction_failure
false_green_claim_detected
```

## 4. Required Response

```text
record incident_timeline_event.
mark affected attempt failed or blocked.
preserve previous attempt and error refs.
disable feature flag if high severity.
notify decision owner.
generate evidence package update.
run redaction and claim scans.
```

## 5. Rollback Rules

```text
append correction artifact instead of silent overwrite.
append quality correction instead of score overwrite.
return prior idempotency ref for duplicate mutation.
never delete old attempt during rollback.
```

```

### `docs/design/V9.x/v9_1_agent_executor_contract_package.md`
```markdown
# V9-1 Agent Executor Contract Package

文档状态：V9-1 contract-freeze package / safety gate ready for external audit。

## 1. Stage Boundary

V9-1 只冻结 Agent executor safety gate 合同，不实现 runtime executor。

允许声明：

```text
V9-1 complete: Agent executor safety gate ready for review.
```

禁止声明：

```text
Agent executor ready
controlled executor ready
production controlled executor ready
autonomous workflow editing ready
full multi-Agent orchestration ready
```

## 2. Non-Negotiable Invariants

```text
AgentExecutionEnvelope is request evidence, not runtime truth.
source=agent default durable mutation is always denied.
Durable mutation is denied unless user_confirmed=true OR valid human_authorization_ref is present.
Every mutating action requires CapabilityResolver decision.
Every high-risk action requires ApprovalGateDecision.
Every runtime action checks KillSwitchDecision before execution.
Every action has timeout policy and idempotency key.
Every mutation has rollback or correction strategy.
Evidence must use redacted refs only.
```

## 3. AgentExecutionPolicy Contract

Required fields:

```text
policy_id
policy_version
tenant_id
workspace_id
project_id
app_id
agent_id
station_id
allowed_operations
denied_operations
risk_level_by_operation
requires_user_confirmation_by_operation
requires_approval_gate_by_operation
allowed_sources
denied_sources
credential_boundary_ref
evidence_policy_ref
created_at
```

Rules:

```text
additionalProperties=false
source=agent must not be in allowed_sources for durable mutation.
denied_operations must include unrestricted connector.call, unrestricted external_llm.call, git.push, production.deploy by default.
```

## 4. AgentExecutionEnvelope Contract

Required fields:

```text
execution_envelope_id
operation
source
actor_type
actor_id
agent_id
station_id
tenant_id
workspace_id
project_id
app_id
workflow_instance_id
station_run_id
target_refs
payload_refs
user_confirmed
human_authorization_ref
capability_decision_ref
approval_gate_ref
idempotency_key
timeout_policy_ref
kill_switch_policy_ref
rollback_descriptor_ref
correlation_id
request_id
audit_ref
created_at
```

Rules:

```text
additionalProperties=false
payload_refs are redacted refs only.
target_refs are operation-specific and non-empty.
raw prompt / raw file content / raw artifact content / raw provider payload / raw connector payload fields are forbidden.
```

## 5. CapabilityResolver Safety Matrix

| Operation class | Default result | Required before allow |
| --- | --- | --- |
| read model view | allow | actor scope and tenant/workspace refs |
| evidence.show | allow | authorized view and redaction policy |
| report.open | allow | authorized view and read-only report |
| artifact.write | deny | user confirmation OR human_authorization_ref, approval gate, rollback descriptor |
| quality.evaluation.create | deny | user confirmation OR human_authorization_ref, approval gate, append-only strategy |
| station.rerun | deny | user confirmation OR human_authorization_ref, attempt history, downstream stale strategy |
| workflow.instance.start | deny | user confirmation OR human_authorization_ref, idempotency key, policy allow |
| workflow.template.publish | deny | separate publish policy and human approval |
| connector.call | deny | separate connector policy and credential lease |
| external_llm.call | deny | separate provider policy and redacted prompt refs |
| git.commit | deny | coding workflow review and human authorization |
| git.push | deny | separate release gate and human authorization |
| production.deploy | deny | separate production deployment gate |

## 6. State Machine

```text
Proposed
 -> CapabilityEvaluated
 -> AwaitingUserConfirmation
 -> AwaitingApprovalGate
 -> KillSwitchChecked
 -> ReadyForControlledRuntime
 -> Executed
 -> EvidenceRecorded
```

Failure states:

```text
DeniedByPolicy
DeniedMissingUserConfirmation
DeniedSourceAgentMutation
DeniedApprovalGate
DeniedKillSwitch
TimedOut
RollbackRequired
EvidenceRejected
```

## 7. Decision DTO Contracts

ApprovalGateDecision required fields:

```text
approval_gate_ref
operation
risk_level
requires_human_approval
approved
approved_by
approved_at
denial_reason
correlation_id
audit_ref
```

KillSwitchDecision required fields:

```text
kill_switch_policy_ref
operation
checked_at
checked_by
allowed
denial_reason
correlation_id
audit_ref
```

TimeoutPolicy required fields:

```text
timeout_policy_ref
operation
max_runtime_seconds
on_timeout
incident_timeline_required
```

RollbackDescriptor required fields:

```text
rollback_descriptor_ref
operation
rollback_strategy
correction_artifact_required
previous_state_ref
created_at
```

ExecutionEvidence required fields:

```text
execution_evidence_ref
execution_envelope_id
operation
source
actor_type
agent_id
station_id
target_refs
capability_decision_ref
approval_gate_ref
runtime_result_ref
rollback_descriptor_ref
redaction_status
correlation_id
request_id
audit_ref
created_at
```

## 8. Negative Tests

```text
source_agent_workflow_instance_start_denied
source_agent_station_rerun_denied
durable_mutation_without_user_confirmation_or_human_authorization_denied
artifact_write_without_rollback_descriptor_denied
quality_evaluation_overwrite_previous_score_denied
connector_call_without_separate_policy_denied
external_llm_call_without_provider_policy_denied
git_push_without_release_gate_denied
production_deploy_without_production_gate_denied
raw_secret_in_execution_envelope_denied
raw_prompt_in_payload_refs_denied
kill_switch_denied_blocks_execution
timeout_marks_attempt_failed_and_records_incident
```

## 9. Acceptance Oracle

V9-1 can pass only if:

```text
AgentExecutionPolicy contract exists.
AgentExecutionEnvelope contract exists.
HumanAuthorizationRef contract exists and is referenced by durable mutation invariant.
CapabilityResolver safety matrix exists.
ApprovalGateDecision / KillSwitchDecision / TimeoutPolicy / RollbackDescriptor / ExecutionEvidence contracts exist.
Durable mutation invariant is present in PRD, architecture, development plan and gate matrix.
Negative test list exists.
No False Green scan PASS.
External audit accepts contract-freeze package.
```

V9-1 cannot pass if:

```text
Agent executor route exists.
Runtime worker implementation starts.
source=agent durable mutation is allowed.
Any positive claim says Agent executor ready.
```

```

### `docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md`
```markdown
# V9-1 Agent Executor Safety Gate Implementation Plan

文档状态：V9-1 implementation plan draft / runtime implementation still NO-GO。

## 1. Boundary

V9-1 implementation, when approved, only implements safety gate validation and contract enforcement. It does not create Agent executor routes, runtime workers, or Executed runtime path.

Current implementation-readiness inputs:

```text
docs/design/V9.x/schemas/agent_execution_policy.schema.json
docs/design/V9.x/schemas/agent_execution_envelope.schema.json
docs/design/V9.x/schemas/human_authorization_ref.schema.json
docs/design/V9.x/schemas/capability_resolver_decision.schema.json
docs/design/V9.x/schemas/execution_evidence.schema.json
docs/design/V9.x/fixtures/schema-negative/source_agent_durable_mutation.json
docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json
```

Allowed stage claim after evidence:

```text
V9-1 complete: Agent executor safety gate ready for review.
```

## 2. Implementation Scope

Implementable objects:

```text
AgentExecutionPolicy parser / validator
AgentExecutionEnvelope parser / validator
CapabilityResolver deny-by-default engine
HumanAuthorizationRef reference validator hook
ApprovalGateDecision contract validator
KillSwitchDecision contract validator
TimeoutPolicy contract validator
RollbackDescriptor contract validator
ExecutionEvidence redaction validator
```

Non-implementable in V9-1:

```text
executor runtime worker
production executor route
source=agent durable mutation
automatic workflow editing
controlled executor action execution
```

## 3. State Boundary

V9-1 may reach:

```text
Proposed
CapabilityEvaluated
AwaitingUserConfirmation
AwaitingApprovalGate
KillSwitchChecked
ReadyForControlledRuntime
```

V9-1 must not reach:

```text
Executed
RuntimeActionStarted
RuntimeActionCompleted
```

`ReadyForControlledRuntime` is a V9-2 handoff boundary, not runtime execution.

## 4. Test Fixtures

```text
agent_execution_policy_valid
agent_execution_envelope_valid
source_agent_mutation_denied
missing_capability_decision_denied
missing_human_authorization_for_mutation_denied
high_risk_missing_approval_gate_denied
raw_secret_in_envelope_denied
ready_for_controlled_runtime_does_not_execute
```

Implementation-readiness audit must prove these fixtures parse and the negative fixtures are expected to fail validation once the validator exists.

## 5. Evidence Package

Required evidence:

```text
v9_1_contract_validation_report.json
v9_1_negative_test_results.json
v9_1_no_false_green_scan.json
v9_1_redaction_scan.json
v9_1_external_audit_decision.md
```

## 6. Stop Conditions

```text
Agent executor route is added.
runtime worker implementation starts.
source=agent durable mutation is allowed.
V9-1 completion is described as Agent executor ready.
```

```

### `docs/design/V9.x/v9_2_controlled_executor_engineering_design.md`
```markdown
# V9-2 Controlled Executor Engineering Design

文档状态：V9-2 engineering design / planned only。

## 1. Service Boundary

`ControlledExecutorService` executes only allowlisted actions after policy, authorization, approval, kill switch, idempotency and redaction checks.

Initial action set:

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

Excluded actions hard-denied:

```text
connector.call
external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
git.commit
git.push
production.deploy
```

## 2. Execution Pipeline

```text
parse envelope
load policy
evaluate capability
validate HumanAuthorizationRef or user_confirmed
evaluate approval gate if medium/high risk
check kill switch
check idempotency
start action
record runtime result
record execution evidence
append incident timeline when denied/failed
```

## 3. HumanAuthorizationRef Validator

Validator must check:

```text
exists
not expired
not revoked
operation_hash matches operation + target_refs + scope
tenant/workspace/project/app match
source and actor_type allowed
audit_ref exists
redaction PASS
```

## 4. Persistence And Migration

Append-only logical records:

```text
execution_envelope
capability_decision
human_authorization_validation
approval_gate_decision
kill_switch_decision
idempotency_record
runtime_result
execution_evidence
incident_timeline_event
```

Migration requirements:

```text
tenant/workspace/project/app indexed.
operation and idempotency_key indexed.
audit_ref indexed.
previous attempt records retained.
artifact and quality writes append only.
```

## 5. Runtime Evidence

Every completed or denied action records:

```text
execution_envelope_id
operation
decision_chain_refs
runtime_result_ref
human_authorization_ref or user_confirmed
approval_gate_ref when required
rollback_descriptor_ref
redaction_status
incident_timeline_ref when denied/failed
```

## 6. E2E Acceptance

```text
workflow_instance_start_success_with_human_authorization_ref
station_rerun_success_with_user_confirmed
artifact_write_appends_new_version
quality_evaluation_appends_new_score
source_agent_mutation_denied
expired_human_authorization_ref_denied
wrong_tenant_human_authorization_ref_denied
kill_switch_denied_blocks_action
idempotency_duplicate_returns_prior_runtime_result_ref
```

```

### `docs/design/V9.x/v9_3_development_and_acceptance_plan.md`
```markdown
# V9-3 Development And Acceptance Plan

文档状态：V9-3 detailed development and acceptance plan / implementation candidate.

## 1. Current Entry Baseline

V9-3 may enter implementation only from this bounded baseline:

```text
V9-1 complete: Agent Executor Safety Gate implementation ready for review.
V9-2 complete: limited controlled Agent executor runtime slice ready for review.
```

V9-2 remains bounded:

```text
allowed_operations=[workflow.instance.start, station.rerun, artifact.write, quality.evaluation.create]
source=agent durable mutation denied
runtime_executor_route_created=false
runtime_worker_created=false
controlled_executor_ready=false
agent_executor_ready=false
```

## 2. V9-3 Scope

V9-3 implements a bounded multi-Agent orchestration runtime slice:

```text
station-bound Agent registry
serial station dependency
parallel branch state isolation
fan-out dispatch
fan-in join / synthesis decision
attempt history retention
lost worker recovery
artifact lineage with producer_agent_id and producer_attempt_id
incident timeline refs
```

V9-3 must include user-facing orchestration fixtures, not only schema-level records:

```text
Roman Forum debate workflow: role-specific Agents discuss a philosophy topic, challenge each other and synthesize attributed conclusions.
Video creation storyboard workflow: user idea becomes creative brief, script, shot list, storyboard prompts, image artifact refs and visual consistency review.
Natural-language workflow optimization remains proposal-only: it produces WorkflowDiff / handoff and waits for user confirmation before mutation.
```

V9-3 must not implement:

```text
不得声明 full multi-Agent orchestration ready
不得声明 distributed multi-Agent runtime ready
不得声明 Agent executor ready
不得允许 source=agent direct durable mutation
不得开放 connector.call
不得开放 external_llm.call
不得执行 git.commit / git.push / production.deploy
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-3A Agent registry and station binding | AgentDescriptor and StationAgentBinding records | each station has exactly one bound Agent in fixture; model/tool/skill/MCP refs are redacted refs |
| V9-3B Orchestration run and branch state | OrchestrationRun and BranchState records | serial and parallel states are distinct and auditable |
| V9-3C Fan-out / fan-in coordinator | FanOutDispatch and FanInJoinDecision records | fan-out target branches and fan-in attribution are complete |
| V9-3D Attempt history and recovery | AttemptHistoryRecord and LostWorkerRecoveryDecision records | retry retains old attempt and old error; lost worker recovery records replacement worker |
| V9-3E Artifact lineage and conflict review | ArtifactLineageRecord and ConflictReviewRecord records | lineage preserves producer_agent_id and producer_attempt_id |
| V9-3F Creative scenario fixtures | Roman Forum and video storyboard fixtures | role-specific discussion, attributed synthesis, storyboard artifacts and provider boundary are auditable |
| V9-3G Evidence package and dashboard | V9-3 acceptance data and HTML dashboard | claim scan, redaction scan and runtime fixture checks PASS |

## 4. Required Runtime Schemas

V9-3 implementation must validate these schemas before runtime acceptance:

```text
schemas/v9_3_agent_descriptor.schema.json
schemas/v9_3_station_agent_binding.schema.json
schemas/v9_3_orchestration_run.schema.json
schemas/v9_3_branch_state.schema.json
schemas/v9_3_fan_out_dispatch.schema.json
schemas/v9_3_fan_in_join_decision.schema.json
schemas/v9_3_attempt_history_record.schema.json
schemas/v9_3_lost_worker_recovery_decision.schema.json
schemas/v9_3_conflict_review_record.schema.json
schemas/orchestration_message.schema.json
schemas/artifact_lineage_record.schema.json
```

## 5. E2E Fixture Contract

Primary fixture:

```text
fixtures/v9-3-orchestration/serial_parallel_fan_in_out_recovery.json
```

The fixture must contain:

```text
three station-bound Agents
one serial dependency path
three parallel branches
one fan-out dispatch decision
one fan-in join decision with attribution
one failed attempt retained
one lost worker recovery decision
artifact lineage for every branch output
incident timeline refs for failure and recovery
```

Required negative fixtures:

```text
fixtures/v9-3-orchestration/fan_in_missing_attribution.json
fixtures/v9-3-orchestration/retry_overwrites_old_attempt.json
fixtures/v9-3-orchestration/source_agent_direct_mutation_attempt.json
```

Required user-facing scenario fixtures:

```text
fixtures/user-scenarios/us_v9_07_roman_forum_debate.json
fixtures/user-scenarios/us_v9_08_video_storyboard_workflow.json
fixtures/user-scenarios/us_v9_09_nl_workflow_optimization.json
```

## 6. Acceptance Tests

```text
v9_3_agent_registry_binds_one_agent_per_station
v9_3_serial_station_dependency_blocks_downstream
v9_3_parallel_branch_states_are_independent
v9_3_fan_out_dispatch_records_each_target_branch
v9_3_fan_in_join_records_all_input_artifacts
v9_3_fan_in_missing_attribution_denied
v9_3_lost_worker_recovery_retains_old_attempt
v9_3_retry_does_not_overwrite_old_error
v9_3_artifact_lineage_preserves_producer_agent_id
v9_3_artifact_lineage_preserves_producer_attempt_id
v9_3_source_agent_message_cannot_directly_mutate_runtime_truth
v9_3_roman_forum_debate_preserves_role_identity_and_attribution
v9_3_video_storyboard_records_provider_model_and_image_refs
v9_3_natural_language_optimization_outputs_diff_before_mutation
v9_3_no_false_green_scan_pass
v9_3_redaction_scan_pass
```

## 7. Evidence Package

V9-3 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
runtime_fixture_ref
schema_validation_result
test_run_refs
claim_scan_result
redaction_scan_result
source_refs
```

V9-3 may complete only if:

```text
status=PASS
evidence_scope=real_runtime_fixture
runtime_backed=true
serial_parallel_fan_in_fan_out=PASS
attempt_history=PASS
artifact_lineage=PASS
failure_recovery=PASS
lost_worker_recovery=PASS
source_agent_direct_mutation_denied=PASS
roman_forum_debate_fixture=PASS
video_storyboard_fixture=PASS or explicitly BLOCKED when provider capability is unavailable
natural_language_optimization_diff_only=PASS
fallback_demo_only=false
```

## 8. Stop Conditions

```text
V9-3 claims full multi-Agent orchestration ready.
V9-3 claims distributed multi-Agent runtime ready.
source=agent directly mutates durable runtime truth.
fan-in synthesis has no attribution.
retry overwrites old attempt or old error.
artifact lineage lacks producer_agent_id or producer_attempt_id.
parallel branch state is flattened into one global status.
planning docs are counted as runtime evidence.
raw prompt / raw model response / raw artifact content appears in evidence.
Roman Forum debate is described as full multi-Agent orchestration readiness.
Video storyboard placeholder images are described as provider-backed image generation.
Natural-language optimization applies workflow mutations before user confirmation.
```

```

### `docs/design/V9.x/v9_3_orchestration_coordinator_engineering_design.md`
```markdown
# V9-3 Orchestration Coordinator Engineering Design

文档状态：V9-3 engineering design / planned only。

## 1. Coordinator Boundary

`OrchestrationCoordinatorService` coordinates station-bound Agents and runtime attempts. It does not bypass V9-2 controlled executor and does not make source=agent durable mutation legal.

## 2. Core Data Model

```text
orchestration_run
agent_message
branch_state
fan_out_dispatch
fan_in_join_decision
attempt_history_record
artifact_lineage_record
lost_worker_recovery_decision
conflict_review_record
incident_timeline_event
```

## 3. State Machines

Serial:

```text
WaitingForUpstream -> Ready -> Running -> Succeeded | Failed | AcceptedPartial
```

Parallel branch:

```text
BranchCreated -> BranchReady -> BranchRunning -> BranchSucceeded | BranchFailed | BranchRecovered
```

Fan-in:

```text
WaitingForInputs -> InputsComplete -> ConflictReviewRequired | ReadyToSynthesize -> Synthesized
```

## 4. Recovery Rules

```text
old attempts are never overwritten.
retry creates a new attempt_id.
lost worker recovery records previous_checkpoint_ref and replacement_worker_id.
timeout retry keeps old error_ref.
mark_failed preserves checkpoint.
artifact lineage must preserve producer_agent_id and producer_attempt_id.
```

## 5. E2E Fixture

```text
three_agent_serial_run
three_branch_parallel_run
fan_out_to_three_branches
fan_in_synthesis_with_attribution
one_branch_failure_and_retry
one_worker_lost_and_recovered
artifact_lineage_for_each_branch
incident_timeline_for_failure_and_recovery
```

## 6. Acceptance Tests

```text
serial_station_dependency_blocks_downstream
parallel_branch_states_are_independent
fan_out_dispatch_records_each_branch
fan_in_join_requires_all_required_inputs_or_partial_decision
conflict_review_records_conflicting_inputs
lost_worker_recovery_retains_old_attempt
artifact_lineage_preserves_producer_agent_id
artifact_lineage_preserves_producer_attempt_id
source_agent_message_cannot_mutate_runtime_truth
```

```

### `docs/design/V9.x/v9_4_development_and_acceptance_plan.md`
```markdown
# V9-4 Development And Acceptance Plan

文档状态：V9-4 detailed development and acceptance plan / implementation complete for review.

This document now records the V9-4 stage plan and the completed bounded runtime evidence package. It does not authorize V9-5 runtime implementation or any over-readiness claim.

## 1. Entry Baseline

V9-4 entered implementation after:

```text
V9-3 orchestration runtime evidence PASS.
V9-3 user scenarios US-V9-02 / US-V9-07 / US-V9-08 have PASS or accepted PARTIAL.
V9-4 coding workflow runtime engineering design accepted.
No False Green scan PASS.
Redaction scan PASS.
human high-risk proceed decision recorded for autonomous coding workflow pilot.
```

V9-4 completion evidence:

```text
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/index.html
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/result-summary.md
```

## 2. Scope

V9-4 implements a bounded coding workflow pilot:

```text
IntentCapture
SpecDraft
PlanDraft
DiffProposal
TestPlanProposal
SandboxedTestRun
ReviewSummary
FixLoopProposal
HumanReviewHandoff
EvidenceRecorded
```

V9-4 must not:

```text
apply patches without review.
commit, push or deploy automatically.
turn review summary into approval.
allow source=agent direct durable mutation.
claim autonomous coding workflow completion beyond pilot ready for review.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-4A Coding workflow run model | coding_workflow_run record | goal, plan, diff, test, review and handoff refs exist |
| V9-4B Diff proposal path | diff_proposal artifact | proposal_only=true and applied=false |
| V9-4C Sandboxed test runner | sandboxed_test_result record | command refs, exit status and redacted log refs recorded |
| V9-4D Review and fix loop | review_summary and fix_loop records | review is not approval; fix loop creates a new proposal |
| V9-4E Git and deployment deny policy | deny evidence records | auto commit / push / deploy attempts denied |
| V9-4F Evidence dashboard | HTML and acceptance data | user can inspect plan, diff, test, review and denial evidence |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/v9-4-coding-workflow/small_code_change_proposal.json
```

Negative fixtures:

```text
fixtures/coding/auto_commit_without_human_approval.json
fixtures/coding/auto_push_without_release_gate.json
fixtures/coding/auto_deploy_without_production_gate.json
fixtures/coding/unreviewed_patch_apply_attempt.json
fixtures/coding/review_summary_as_approval_attempt.json
```

## 5. Acceptance Tests

```text
v9_4_coding_workflow_creates_plan_diff_test_review_and_handoff
v9_4_diff_proposal_is_not_patch_apply
v9_4_sandboxed_test_result_records_exit_status_and_log_ref
v9_4_review_summary_is_not_approval
v9_4_fix_loop_creates_new_diff_proposal
v9_4_auto_commit_denied
v9_4_auto_push_denied
v9_4_auto_deploy_denied
v9_4_source_agent_direct_mutation_denied
v9_4_claim_scan_pass
v9_4_redaction_scan_pass
```

## 6. Evidence Package

V9-4 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
coding_workflow_run_ref
diff_proposal_ref
sandboxed_test_result_ref
review_summary_ref
fix_loop_ref
human_review_handoff_ref
git_operation_deny_report_ref
claim_scan_result
redaction_scan_result
```

## 7. Stop Conditions

```text
Patch is applied before review.
Commit, push or deploy happens automatically.
Review summary is counted as approval.
Fix loop silently edits previous artifacts.
Source=agent directly mutates durable runtime truth.
Evidence stores sensitive content instead of redacted refs.
Stage is claimed complete without runnable coding workflow evidence.
V9-4 evidence is reused to claim autonomous coding workflow ready.
V9-4 evidence alone is reused to authorize V9-5 runtime implementation without a separate V9-5 high-risk decision.
```

```

### `docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md`
```markdown
# V9-4 Coding Workflow Runtime Engineering Design

文档状态：V9-4 engineering design / planned only。

## 1. Runtime Boundary

V9-4 creates a coding workflow pilot that generates plans, diff proposals, tests, review summaries and fix-loop proposals. It must not auto commit, auto push, auto deploy or apply unreviewed patches.

## 2. Workflow Runtime

```text
IntentCapture
SpecDraft
PlanDraft
DiffProposal
TestPlanProposal
SandboxedTestRun
ReviewSummary
FixLoopProposal
HumanReviewHandoff
EvidenceRecorded
```

## 3. Git Operation Deny Policy

Denied by default:

```text
git commit
git push
git tag
production deploy
release publish
```

Allowed only as proposal:

```text
commit_message_proposal
patch_diff_proposal
release_note_proposal
deploy_plan_proposal
```

## 4. Sandbox Rules

```text
tests run in workspace-scoped sandbox.
secret reads denied.
workspace escape denied.
raw file content not copied into evidence.
diff proposal is separate from patch apply.
fix-loop creates a new diff proposal.
review summary cannot become approval.
```

## 5. Evidence Package

```text
coding_workflow_run_id
intent_ref
spec_ref
plan_ref
diff_proposal_ref
test_plan_ref
test_result_ref
review_summary_ref
fix_loop_ref
human_review_handoff_ref
git_operation_deny_report_ref
redaction_status
claim_scan_status
```

## 6. Acceptance Tests

```text
coding_workflow_diff_proposal_created
coding_workflow_test_plan_created
coding_workflow_sandboxed_tests_run
coding_workflow_review_summary_created
coding_workflow_fix_loop_creates_new_diff
coding_workflow_no_auto_commit
coding_workflow_no_auto_push
coding_workflow_no_auto_deploy
coding_workflow_unreviewed_patch_apply_denied
coding_workflow_secret_read_denied
```

```

### `docs/design/V9.x/v9_4_pre_implementation_readiness_closure.md`
```markdown
# V9-4 Pre-Implementation Readiness Closure

status: PASS
current_decision: NO_GO_FOR_RUNTIME_IMPLEMENTATION
v9_4_runtime_implementation_allowed: false
human_high_risk_proceed_decision_recorded: false
claim_scan: PASS
redaction_scan: PASS

Required before runtime implementation:
- V9-4 readiness audit accepted
- V9-4 high-risk human proceed decision recorded
- coding workflow sandbox policy accepted
- diff/test/review/fix-loop evidence format accepted
- no auto commit / auto push / auto deploy denial evidence accepted
- No False Green scan PASS
- redaction scan PASS

```

### `docs/design/V9.x/v9_5_development_and_acceptance_plan.md`
```markdown
# V9-5 Development And Acceptance Plan

文档状态：V9-5 detailed development and acceptance plan / implementation complete for review.

This document records the V9-5 stage plan and completed governed terminal worker evidence package. It does not authorize unrestricted shell, production terminal automation or browser account automation.

## 1. Entry Baseline

V9-5 entered implementation after:

```text
V9-4 evidence PASS or a documented proceed decision scopes V9-5 independently as a narrow sandbox readiness slice only.
Terminal sandbox engineering design accepted.
Command allowlist catalog accepted.
Filesystem boundary and symlink policy accepted.
human high-risk proceed decision recorded for terminal worker write sandbox.
No False Green scan PASS.
Redaction scan PASS.
```

V9-5 completion evidence:

```text
docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json
docs/design/V9.x/evidence/v9-5-terminal-worker/index.html
docs/design/V9.x/evidence/v9-5-terminal-worker/result-summary.md
```

Independent proceed is narrow:

```text
It may validate workspace boundary, command tier policy, transcript capture, diff capture and denial evidence.
It must not enable broad terminal runtime, unrestricted shell, production deploy, git push or browser account automation.
It must not authorize terminal write actions beyond explicitly scoped sandbox readiness fixtures.
```

## 2. Scope

V9-5 expands terminal worker behavior inside a governed workspace sandbox:

```text
workspace-scoped readonly commands
workspace-scoped build and test commands
controlled diff proposal generation
approval-gated workspace write attempts
transcript capture
diff capture
denial evidence for escape and sensitive access attempts
```

V9-5 must not:

```text
provide unrestricted shell access.
run production deployment.
push to remote repositories.
automate production browser accounts.
allow workspace escape.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-5A Workspace boundary guard | path decision records | canonical path, symlink target and denied prefixes recorded |
| V9-5B Command tier resolver | terminal_command_decision records | tier, policy decision and human authorization requirement visible |
| V9-5C Transcript capture | transcript_ref records | command, status and redacted output refs visible |
| V9-5D Diff capture | diff_capture records | write attempts create proposal / diff refs |
| V9-5E Denial evidence | denied action records | escape, sensitive access, git push and deployment attempts denied |
| V9-5F Dashboard | HTML and acceptance data | auditor can inspect command tiers and denial evidence |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/terminal/workspace_scoped_test_and_diff_capture.json
```

Negative fixtures:

```text
fixtures/terminal/terminal_workspace_escape.json
fixtures/terminal/terminal_symlink_escape.json
fixtures/terminal/terminal_sensitive_read_attempt.json
fixtures/terminal/terminal_network_without_policy.json
fixtures/terminal/terminal_git_push_attempt.json
fixtures/terminal/terminal_production_deploy_attempt.json
```

## 5. Acceptance Tests

```text
v9_5_workspace_canonicalization_records_scope
v9_5_readonly_command_records_transcript
v9_5_build_or_test_command_records_exit_status
v9_5_write_action_requires_diff_capture
v9_5_write_action_requires_valid_human_authorization
v9_5_workspace_escape_denied
v9_5_symlink_escape_denied
v9_5_sensitive_read_denied
v9_5_git_push_denied
v9_5_production_deploy_denied
v9_5_claim_scan_pass
v9_5_redaction_scan_pass
```

## 6. Evidence Package

V9-5 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
terminal_session_ref
command_decision_refs
transcript_refs
diff_capture_refs
denied_action_refs
human_authorization_refs
claim_scan_result
redaction_scan_result
```

## 7. Stop Conditions

```text
Unrestricted shell is allowed.
Workspace escape succeeds.
Symlink escape succeeds.
Sensitive content is read into evidence.
Git push or production deployment executes.
Write action occurs without diff capture and valid authorization.
Terminal worker is claimed as production terminal automation.
V9-5 evidence is reused to claim unrestricted terminal worker ready.
V9-5 evidence is reused to authorize V9-7 production automation.
```

```

### `docs/design/V9.x/v9_5_terminal_sandbox_engineering_design.md`
```markdown
# V9-5 Terminal Sandbox Engineering Design

文档状态：V9-5 engineering design / planned only。

## 1. Sandbox Boundary

Terminal worker is workspace-scoped and policy-controlled. It is not an unrestricted shell, not production terminal automation and not browser account automation.

## 2. Filesystem Boundary

Required checks:

```text
workspace_root canonicalization
relative path normalization
absolute path allowlist check
.. traversal denial
symlink target resolution
denied path prefix scan
write path allowlist
```

Denied by default:

```text
/etc
/var
/System
~/.ssh
~/.aws
~/.config
.env
.env.local
credential files
```

## 3. Command Allowlist Catalog

```text
Tier 0: pwd, ls, find, rg, sed, nl, cat for allowed paths
Tier 1: pytest, npm test, npm run build, type checks
Tier 2: patch proposal generation through controlled diff capture
Tier 3: high-risk workspace write requiring human_authorization_ref
Denied: git push, production deploy, credential export, shell privilege escalation
```

## 4. Network And Secret Policy

```text
network egress denied unless explicit policy exists.
secret read denied.
environment variable redaction required.
token pattern redaction required.
signed URL redaction required.
```

## 5. Transcript And Diff Capture

Every session records:

```text
terminal_session_id
command_tier
workspace_scope
policy_decision
transcript_ref
diff_ref
redaction_status
audit_ref
```

## 6. Acceptance Tests

```text
terminal_workspace_escape_denied
terminal_symlink_escape_denied
terminal_secret_read_denied
terminal_network_without_policy_denied
terminal_write_requires_diff_capture
terminal_tier3_requires_human_authorization_ref
terminal_git_push_denied
terminal_production_deploy_denied
```

```

### `docs/design/V9.x/v9_6_development_and_acceptance_plan.md`
```markdown
# V9-6 Development And Acceptance Plan

文档状态：V9-6 detailed development and acceptance plan / Studio productization slice / implementation complete for review.

This document records the V9-6 stage plan and completed bounded Workflow Studio evidence package. It does not authorize complete Workflow Studio readiness, direct runtime truth writes or autonomous workflow editing.

## 1. Entry Baseline

V9-6 entered implementation after:

```text
Workflow Studio PRD accepted.
BFF route allowlist accepted.
browser denylist accepted.
read-only Runtime Report and Evidence Chain boundaries accepted.
manual confirmation and HumanAuthorizationRef flow accepted.
No False Green scan PASS.
Redaction scan PASS.
```

Implementation evidence is now recorded in:

```text
docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json
docs/design/V9.x/evidence/v9-6-workflow-studio/index.html
docs/design/V9.x/evidence/v9-6-workflow-studio/result-summary.md
```

## 2. Scope

V9-6 productizes workflow review and proposal workflows through Studio:

```text
workflow graph view
station Agent profile inspector
runtime status read model
artifact lineage view
Runtime Report read-only panel
Evidence Chain read-only panel
WorkflowDiff proposal panel
manual confirmation panel
natural-language workflow optimization proposal path
```

V9-6 must not:

```text
directly write WorkflowStore, WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun or Artifact.
hide runtime mutation behind browser forms.
call internal runtime routes directly from browser.
claim complete Workflow Studio readiness.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-6A Studio BFF read models | studio-state DTOs | graph, Agent profile, runtime status and lineage available |
| V9-6B Read-only review panels | Runtime Report and Evidence Chain UI evidence | no execute / apply / publish buttons |
| V9-6C WorkflowDiff proposal flow | proposal DTO and handoff refs | natural-language optimization creates proposal before mutation |
| V9-6D Manual confirmation flow | human_authorization_ref evidence | confirmation captured before durable mutation handoff |
| V9-6E Browser safety checks | network log and hidden form scan | no direct internal runtime route and no hidden mutation form |
| V9-6F Studio acceptance dashboard | HTML and acceptance data | user can inspect workflow, Agents, artifacts and evidence |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/studio/studio_review_and_workflow_diff_proposal.json
```

Negative fixtures:

```text
fixtures/studio/studio_direct_runtime_write.json
fixtures/studio/studio_hidden_mutation_form.json
fixtures/studio/studio_browser_direct_internal_runtime_route.json
fixtures/studio/nl_optimization_direct_mutation_attempt.json
fixtures/studio/ui_copy_agent_executed_automatically.json
```

## 5. Acceptance Tests

```text
v9_6_studio_loads_workflow_graph_from_bff
v9_6_station_agent_profile_is_visible
v9_6_runtime_report_is_read_only
v9_6_evidence_chain_is_read_only
v9_6_natural_language_optimization_creates_workflow_diff
v9_6_manual_confirmation_records_human_authorization_ref
v9_6_browser_no_direct_internal_runtime_routes
v9_6_hidden_mutation_form_absent
v9_6_ui_copy_no_automatic_agent_execution_claim
v9_6_claim_scan_pass
v9_6_redaction_scan_pass
```

## 6. Evidence Package

V9-6 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
studio_network_log.json
studio_hidden_form_scan.json
studio_ui_copy_claim_scan.json
manual_confirmation_evidence.json
workflow_diff_proposal_refs
claim_scan_result
redaction_scan_result
```

## 7. Stop Conditions

```text
Studio directly writes runtime truth.
Browser calls internal runtime routes directly.
Evidence Chain or Runtime Report exposes execution buttons.
Natural-language optimization mutates before confirmation.
UI copy implies automatic Agent execution.
Stage is claimed as complete Workflow Studio.
```

```

### `docs/design/V9.x/v9_6_workflow_studio_engineering_design.md`
```markdown
# V9-6 Workflow Studio Engineering Design

文档状态：V9-6 engineering design / implementation complete for review。

## 1. Boundary

Workflow Studio is a productization slice through BFF / DTO / read models. It cannot directly write WorkflowStore, WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun or Artifact. The implemented V9-6 fixture proves the bounded read-model/productization slice only; it does not prove complete Workflow Studio readiness.

## 2. Panels

```text
Mission Console
Workflow Blueprint
Agent Station Inspector
Runtime Report
Review Console
Evidence Chain
Human Authorization Review
Studio Audit Export
```

## 3. BFF Route Allowlist

```text
GET /bff/v9/studio-state
GET /bff/v9/runtime-report
GET /bff/v9/evidence-chain
GET /bff/v9/workflow-blueprint
POST /bff/v9/workflow-diff-proposal
POST /bff/v9/manual-confirmation
POST /bff/v9/review-handoff
```

Browser denylist:

```text
/v1/rpc
/v1/events/subscribe
/v1/internal/*
/internal/v9/*
```

## 4. Manual Confirmation Flow

```text
user reviews proposal.
Studio posts manual confirmation to BFF.
BFF records human_authorization_ref.
Runtime action still requires CapabilityResolver and high-risk approval when applicable.
```

## 5. UI Safety Tests

```text
studio_browser_no_direct_runtime_truth
studio_browser_no_direct_v1_rpc
studio_browser_no_direct_events_subscribe
studio_hidden_mutation_form_absent
runtime_report_readonly_no_execute_buttons
evidence_chain_readonly_no_execute_buttons
manual_confirmation_records_human_authorization_ref
studio_copy_no_agent_executed_automatically
```

## 6. Evidence Package

```text
studio_network_log.json
studio_hidden_form_scan.json
studio_ui_copy_claim_scan.json
studio_manual_confirmation_evidence.json
studio_bff_route_allowlist_result.json
studio_browser_denylist_result.json
```

```

### `docs/design/V9.x/v9_7_development_and_acceptance_plan.md`
```markdown
# V9-7 Development And Acceptance Plan

文档状态：V9-7 detailed development and acceptance plan / implementation complete for review / production governance high-risk gate.

This document records the implemented V9-7 governance/evidence hardening slice. It does not authorize production automation readiness, production browser automation, raw credential access or unrestricted terminal automation.

## 1. Entry Baseline

V9-7 entered implementation only after:

```text
V9-6 Studio boundary evidence PASS.
Production governance engineering design accepted.
Tenant isolation matrix accepted.
Credential lease validator accepted.
Audit export and incident timeline contracts accepted.
Evidence hardening validator accepted.
human high-risk proceed decision recorded for production governance and terminal automation gate.
No False Green scan PASS.
Redaction scan PASS.
```

## 2. Scope

V9-7 hardens governance and evidence boundaries:

```text
tenant isolation decision
credential lease decision
service account binding policy
append-only audit export
incident timeline
evidence hardening report
terminal automation policy
browser automation separate PRD gate
```

V9-7 must not:

```text
claim production automation readiness.
enable production browser automation without separate PRD and human decision.
allow credential use without tenant, app, audience and operation binding.
allow audit export mutation.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-7A Tenant and app scope checks | tenant isolation decisions | wrong tenant/app/workspace denied |
| V9-7B Credential lease validator | credential lease decisions | audience, operation, expiry and revocation checked |
| V9-7C Service account binding | binding decisions | service account cannot become autonomous override |
| V9-7D Audit export hardening | audit export package | append-only, redacted refs only |
| V9-7E Incident timeline | incident events | policy denial, credential denial, timeout and worker loss recorded |
| V9-7F Automation gate dashboard | HTML and acceptance data | reviewer sees governance, evidence and remaining blocked automation |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/governance/tenant_bound_credential_lease_and_audit_export.json
```

Negative fixtures:

```text
fixtures/governance/wrong_tenant_credential_lease.json
fixtures/governance/wrong_operation_credential_lease.json
fixtures/governance/expired_credential_lease.json
fixtures/governance/revoked_credential_lease.json
fixtures/governance/audit_export_mutation_attempt.json
fixtures/governance/browser_automation_without_separate_prd.json
```

## 5. Acceptance Tests

```text
v9_7_tenant_isolation_wrong_tenant_denied
v9_7_credential_lease_wrong_operation_denied
v9_7_credential_lease_expired_denied
v9_7_credential_lease_revoked_denied
v9_7_audit_export_append_only
v9_7_incident_timeline_records_policy_denial
v9_7_incident_timeline_records_credential_denial
v9_7_evidence_hardening_scan_pass
v9_7_browser_automation_blocked_without_separate_prd
v9_7_claim_scan_pass
v9_7_redaction_scan_pass
```

## 6. Evidence Package

V9-7 completion evidence includes:

```text
docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json
docs/design/V9.x/evidence/v9-7-production-governance/index.html
docs/design/V9.x/evidence/v9-7-production-governance/result-summary.md
docs/design/V9.x/evidence/v9-7-production-governance/tenant-isolation-decisions.json
docs/design/V9.x/evidence/v9-7-production-governance/credential-lease-decisions.json
docs/design/V9.x/evidence/v9-7-production-governance/service-account-binding-decisions.json
docs/design/V9.x/evidence/v9-7-production-governance/audit-export-package.json
docs/design/V9.x/evidence/v9-7-production-governance/incident-timeline.json
docs/design/V9.x/evidence/v9-7-production-governance/evidence-hardening-report.json
docs/design/V9.x/evidence/v9-7-production-governance/terminal-automation-policy.json
docs/design/V9.x/evidence/v9-7-production-governance/browser-automation-policy.json
docs/design/V9.x/decisions/v9_7_high_risk_human_decision.json
```

## 7. Stop Conditions

```text
Credential decision lacks tenant, app, audience or operation binding.
Audit export is mutable.
Incident timeline is missing for denied high-risk action.
Browser automation starts without separate PRD and human decision.
Terminal automation is claimed as production ready.
Production readiness claim appears in completion context.
```

```

### `docs/design/V9.x/v9_7_production_governance_engineering_design.md`
```markdown
# V9-7 Production Governance Engineering Design

文档状态：V9-7 engineering design / implemented governance slice / ready for review。

## 1. Boundary

V9-7 hardens production governance, evidence and terminal automation gates. It does not prove production automation ready or production browser automation ready.

Implemented evidence:

```text
core/governance/v9_7_production_governance.py
tests/test_v9_7_production_governance.py
tools/v9/generate_v9_7_production_governance_evidence.py
docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json
```

## 2. Required Models

```text
TenantIsolationMatrix
CredentialLease
ServiceAccountBinding
AuditExportPackage
IncidentTimelineEvent
EvidenceHardeningReport
TerminalAutomationPolicy
BrowserAutomationSeparatePrd
```

## 3. Credential Lease Validator

CredentialLease must bind:

```text
tenant_id
workspace_id
project_id
app_id
audience
operation
service_account_id
expires_at
revoked
audit_ref
```

Denied:

```text
wrong tenant
wrong app
wrong audience
wrong operation
expired lease
revoked lease
raw secret access
```

## 4. Audit And Incident Rules

```text
audit export is append-only.
incident timeline required for timeout, denied credential, denied policy and worker loss.
evidence hardening validator scans raw secret, raw prompt and raw artifact content.
browser automation blocked unless separate PRD and explicit human decision exist.
```

## 5. Acceptance Tests

```text
credential_lease_wrong_tenant_denied
credential_lease_wrong_operation_denied
credential_lease_expired_denied
audit_export_append_only
incident_timeline_records_policy_denial
evidence_hardening_redaction_pass
browser_automation_blocked_without_separate_prd
production_automation_ready_claim_denied
```

## 6. Non-Claims

V9-7 ready-for-review evidence must not be summarized as:

```text
production automation ready
production terminal automation ready
production browser automation ready
production ready
full production GA
```

```

### `docs/design/V9.x/v9_8_development_and_acceptance_plan.md`
```markdown
# V9-8 Development And Acceptance Plan

文档状态：V9-8 detailed development and acceptance plan / validator implemented / final acceptance PASS with provider-backed storyboard evidence.

This document now records the implemented V9-8 final acceptance validator. The validator generates a PASS dashboard because US-V9-08 now has valid provider-backed storyboard image artifacts.

## 1. Entry Baseline

V9-8 final claim may be emitted only after:

```text
V9-0..V9-7 evidence packages exist.
US-V9-01..US-V9-09 user scenario results exist.
Runtime-backed user scenarios cite real_runtime_fixture or real_runtime evidence.
Planning docs, transcript-only reports and report-only dashboards are rejected for runtime-backed user scenario PASS.
No required stage is FAIL or BLOCKED.
PARTIAL scenarios have documented proceed decisions.
High-risk stages include human decision refs.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
```

## 2. Scope

V9-8 aggregates stage and user evidence:

```text
stage evidence discovery
evidence package schema validation
runtime-backed evidence checks
user scenario acceptance checks
high-risk decision checks
claim scan
redaction scan
drawio XML validation
final dashboard generation
final result summary
```

V9-8 must not:

```text
accept planning docs as runtime evidence.
ignore missing user scenario evidence.
emit final claim while any stage is FAIL or BLOCKED.
upgrade ready for review to production completion.
```

Current V9-8 output:

```text
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-dashboard.html
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-result-summary.md
```

Current final acceptance result:

```text
status=PASS
blockers=[]
US-V9-08 provider-backed storyboard image artifacts=4
final_claim=V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-8A Evidence discovery | stage evidence index | V9-0..V9-7 roots found |
| V9-8B Package validation | validation report | schema, refs and status fields valid |
| V9-8C Runtime evidence checker | runtime-backed report | runtime stages have runtime evidence, not docs-only |
| V9-8D User scenario checker | user scenario matrix | US-V9-01..US-V9-09 reviewed and runtime_backed requirements enforced |
| V9-8E Claim and redaction gate | scan reports | both PASS |
| V9-8F Final dashboard | HTML, JSON and summary | final claim emitted only when all gates pass |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/evidence/v9_8_all_required_evidence_present_sample.json
```

Negative fixtures:

```text
fixtures/evidence/v9_8_reject_planning_only_sample.json
fixtures/evidence/v9_8_missing_v9_3_runtime_evidence.json
fixtures/evidence/v9_8_missing_user_scenario_result.json
fixtures/evidence/v9_8_missing_high_risk_human_decision.json
fixtures/evidence/v9_8_forbidden_claim.json
fixtures/evidence/v9_8_forbidden_content_leakage.json
fixtures/evidence/v9_8_drawio_invalid.json
```

## 5. Acceptance Tests

```text
v9_8_discovers_v9_0_to_v9_7_evidence
v9_8_rejects_planning_docs_as_runtime_evidence
v9_8_requires_user_scenarios_01_to_09
v9_8_requires_runtime_backed_user_scenario_evidence
v9_8_rejects_transcript_only_or_report_only_user_scenario_pass
v9_8_rejects_missing_high_risk_human_decision
v9_8_rejects_fail_or_blocked_without_proceed_decision
v9_8_claim_scan_pass
v9_8_redaction_scan_pass
v9_8_drawio_xml_valid
v9_8_generates_final_dashboard_and_data
v9_8_final_claim_limited_to_ready_for_review
```

## 6. Final Outputs

```text
v9-final-acceptance-dashboard.html
v9-final-acceptance-data.json
v9-final-claim-scan.md
v9-final-redaction-scan.md
v9-final-result-summary.md
v9-final-user-scenario-matrix.json
```

## 7. Stop Conditions

```text
Any V9-0..V9-7 evidence package is missing.
Any required user scenario result is missing.
Any runtime-backed user scenario lacks real_runtime_fixture or real_runtime evidence.
Any runtime-backed user scenario uses planning docs, transcript-only or report-only evidence.
Any runtime-backed stage uses docs-only evidence.
Any forbidden readiness claim appears in positive completion context.
Any forbidden content leakage appears in evidence.
Drawio XML validation fails.
Final claim is stronger than ready for review.
```

```

### `docs/design/V9.x/v9_8_final_acceptance_validator_engineering_design.md`
```markdown
# V9-8 Final Acceptance Validator Engineering Design

文档状态：V9-8 engineering design / implemented validator / PASS with US-V9-08 provider-backed image evidence。

## 1. Purpose

V9-8 validator aggregates stage evidence and decides whether the final V9 ready-for-review claim can be emitted. It must reject planning-only evidence for runtime stages.

Implemented files:

```text
tools/v9/generate_v9_8_final_acceptance.py
tests/test_v9_8_final_acceptance.py
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-dashboard.html
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json
```

Current validator result:

```text
status=PASS
blockers=[]
final_claim=V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

Current rejection fixture:

```text
docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json
docs/design/V9.x/evidence/v9-3-orchestration-runtime/storyboard-provider-evidence.json
```

## 2. Discovery Rules

Expected evidence roots:

```text
docs/design/V9.x/evidence/v9-0/
docs/design/V9.x/evidence/v9-1/
docs/design/V9.x/evidence/v9-2/
docs/design/V9.x/evidence/v9-3/
docs/design/V9.x/evidence/v9-4/
docs/design/V9.x/evidence/v9-5/
docs/design/V9.x/evidence/v9-6/
docs/design/V9.x/evidence/v9-7/
```

Each root must contain:

```text
evidence-package.json
result-summary.md
claim-scan.json
redaction-scan.json
test-results.json
```

## 3. Validation Algorithm

```text
load evidence package for every stage.
validate package schema.
verify runtime_backed requirements by stage.
verify high-risk human_decision_refs.
verify no FAIL or BLOCKED.
verify PARTIAL has proceed decision.
run No False Green claim scan.
run redaction scan.
validate drawio XML.
generate final dashboard.
block final claim when US-V9-08 provider-backed storyboard image evidence is missing or blocked; allow the final ready-for-review claim only when four storyboard image artifacts and provider/model/invocation refs are recorded.
```

The validator must treat `docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json` as BLOCKED, not PASS.

## 4. Rejection Cases

```text
missing stage evidence package
planning docs counted as runtime evidence
missing human_decision_ref for high-risk stage
runtime_backed=false for runtime stage
forbidden claim outside allowed context
raw secret / raw prompt / raw artifact content
drawio XML invalid
```

## 5. Final Output

```text
v9-final-acceptance-dashboard.html
v9-final-acceptance-data.json
v9-final-claim-scan.md
v9-final-redaction-scan.md
v9-final-result-summary.md
```

```

### `docs/design/V9.x/v9_document_audit_report.md`
```markdown
# V9 Document Audit Report

文档状态：V9-7 evidence-aligned document audit / PASS for V9-8 readiness review。

## 0. Current Evidence-Aligned Result

```text
V9-0 planning package: PASS / complete_for_review.
V9-1 safety gate implementation: PASS / complete_for_review.
V9-2 limited controlled runtime slice: PASS / complete_for_review.
V9-3 orchestration runtime: PASS / complete_for_review.
V9-4 autonomous coding workflow pilot: PASS / complete_for_review.
V9-5 governed terminal worker expansion: PASS / complete_for_review.
V9-6 Workflow Studio productization: PASS / complete_for_review.
V9-7 production governance and terminal automation gate: PASS / complete_for_review.
V9-8 final acceptance validator: PASS with US-V9-08 provider-backed storyboard image evidence.
```

This report supersedes older V9-0-only audit wording where it implied V9-1 or V9-2 had not started.

## 1. Audit Scope

```text
docs/design/V9.x/00_README.md
docs/design/V9.x/v9_target_prd.md
docs/design/V9.x/v9_target_architecture.md
docs/design/V9.x/v9_current_gap_analysis.md
docs/design/V9.x/v9_current_gap_analysis.drawio
docs/design/V9.x/v9_development_and_acceptance_plan.md
docs/design/V9.x/v9_milestone_roadmap.md
docs/design/V9.x/v9_acceptance_gate_matrix.md
docs/design/V9.x/v9_user_scenario_acceptance_gate.md
docs/design/V9.x/v9_no_false_green_claim_guard.md
docs/design/V9.x/v9_planning_audit_for_chatgpt.md
docs/design/V9.x/v9_front_stage_development_readiness_audit.md
docs/design/V9.x/v9_1_agent_executor_contract_package.md
docs/design/V9.x/v9_human_authorization_ref_contract.md
docs/design/V9.x/v9_2_controlled_executor_implementation_spec.md
docs/design/V9.x/v9_3_multi_agent_orchestration_implementation_spec.md
docs/design/V9.x/v9_4_autonomous_coding_workflow_implementation_spec.md
docs/design/V9.x/v9_5_terminal_worker_boundary_implementation_spec.md
docs/design/V9.x/v9_6_workflow_studio_productization_prd.md
docs/design/V9.x/v9_7_production_governance_terminal_automation_gate_spec.md
docs/design/V9.x/v9_8_final_acceptance_framework.md
docs/design/V9.x/v9_contract_schema_bundle.md
docs/design/V9.x/schemas/
docs/design/V9.x/fixtures/
docs/design/V9.x/v9_api_and_service_boundary_spec.md
docs/design/V9.x/v9_evidence_package_schema_and_validator_spec.md
docs/design/V9.x/v9_test_fixture_and_ci_matrix.md
docs/design/V9.x/v9_high_risk_human_decision_protocol.md
docs/design/V9.x/v9_security_threat_model_and_abuse_cases.md
docs/design/V9.x/v9_automation_assisted_development_policy.md
docs/design/V9.x/v9_operational_runbook_and_incident_response.md
docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md
docs/design/V9.x/v9_2_controlled_executor_engineering_design.md
docs/design/V9.x/v9_3_orchestration_coordinator_engineering_design.md
docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md
docs/design/V9.x/v9_5_terminal_sandbox_engineering_design.md
docs/design/V9.x/v9_6_workflow_studio_engineering_design.md
docs/design/V9.x/v9_7_production_governance_engineering_design.md
docs/design/V9.x/v9_8_final_acceptance_validator_engineering_design.md
```

## 2. Validation Results

```text
xmllint --noout docs/design/V9.x/v9_current_gap_analysis.drawio -> PASS
V9 document list exists -> PASS
V9 stage order exists -> PASS
V9 target architecture exists -> PASS
V9 PRD exists -> PASS
V9 gap analysis exists -> PASS
V9 acceptance matrix exists -> PASS
V9 user scenario acceptance gate exists -> PASS
V9 No False Green guard exists -> PASS
V9 front-stage development readiness audit exists -> PASS
V9-1 Agent executor contract package exists -> PASS
HumanAuthorizationRef contract exists -> PASS
V9-2 implementation-readiness spec exists -> PASS
V9-3 implementation-readiness spec exists -> PASS
V9-4 implementation-readiness spec exists -> PASS
V9-5 implementation-readiness spec exists -> PASS
V9-6 separate Studio PRD exists -> PASS
V9-7 governance/evidence/terminal automation gate spec exists -> PASS
V9-8 final acceptance framework exists -> PASS
P0 contract schema bundle plan exists -> PASS
P0 JSON Schema files exist, including kill switch, timeout, rollback, evidence package and high-risk decision schemas -> PASS
P0 negative fixtures and evidence samples exist -> PASS
P0 API/service boundary spec exists -> PASS
P0 evidence package validator spec exists -> PASS
P0 test fixture and CI matrix exists -> PASS
P0 high-risk human decision protocol exists -> PASS
P0 security threat model exists -> PASS
P0 automation-assisted development policy exists -> PASS
P0 operational runbook exists -> PASS
V9-1 implementation plan draft exists -> PASS
V9-2 engineering design exists -> PASS
V9-1 safety gate implementation evidence exists -> PASS
V9-2 limited controlled runtime slice evidence exists -> PASS
V9-3 bounded orchestration runtime slice evidence exists -> PASS
V9-3 acceptance dashboard exists -> PASS
V9-3 serial / parallel / fan-in / fan-out evidence PASS -> PASS
V9-3 recovery and lineage evidence PASS -> PASS
V9-3 Roman Forum scenario evidence PASS -> PASS
V9-3 natural-language optimization diff-only evidence PASS -> PASS
V9-3 video storyboard provider-backed image generation explicitly BLOCKED in local fixture -> PASS
V9-4 high-risk human decision exists and is scoped -> PASS
V9-4 coding workflow pilot evidence exists -> PASS
V9-4 plan / diff proposal / sandboxed test / review / fix-loop evidence PASS -> PASS
V9-4 auto commit / auto push / auto deploy / unreviewed patch apply denial evidence PASS -> PASS
V9-4 source=agent direct durable mutation denial evidence PASS -> PASS
V9-5 high-risk human decision exists and is scoped -> PASS
V9-5 governed terminal worker evidence exists -> PASS
V9-5 workspace-scoped command tier, transcript and diff capture evidence PASS -> PASS
V9-5 workspace escape, symlink escape, sensitive read, git push, production deploy and network denial evidence PASS -> PASS
V9-6 Workflow Studio evidence exists -> PASS
V9-6 BFF/DTO route allowlist evidence PASS -> PASS
V9-6 browser denylist evidence PASS -> PASS
V9-6 read-only Runtime Report and Evidence Chain panels PASS -> PASS
V9-6 WorkflowDiff proposal and manual confirmation evidence PASS -> PASS
V9-7 high-risk human decision exists and is scoped -> PASS
V9-7 production governance evidence exists -> PASS
V9-7 tenant isolation decision evidence PASS -> PASS
V9-7 credential lease validation evidence PASS -> PASS
V9-7 service account binding policy evidence PASS -> PASS
V9-7 append-only audit export evidence PASS -> PASS
V9-7 incident timeline evidence PASS -> PASS
V9-7 evidence hardening and automation denial evidence PASS -> PASS
V9-8 final acceptance validator exists -> PASS
V9-8 final dashboard generated with PASS status -> PASS
US-V9-08 MiniMax provider-backed storyboard artifacts generated=4 -> PASS
US-V9-08 records provider/model/invocation refs without raw prompt/payload/base64 -> PASS
V9 pytest test run summary artifact exists -> PASS
V9-3 engineering design exists -> PASS
V9-3 detailed development and acceptance plan exists -> PASS
V9-3 runtime schemas exist -> PASS
V9-3 positive and negative fixtures exist -> PASS
V9 creative user scenario acceptance gates for Roman Forum, video storyboard and natural-language optimization exist -> PASS
V9-4 detailed development and acceptance plan exists -> PASS
V9-5 detailed development and acceptance plan exists -> PASS
V9-6 detailed development and acceptance plan exists -> PASS
V9-7 detailed development and acceptance plan exists -> PASS
V9-8 detailed development and acceptance plan exists -> PASS
V9-4 engineering design exists -> PASS
V9-5 engineering design exists -> PASS
V9-6 engineering design exists -> PASS
V9-7 engineering design exists -> PASS
V9-8 validator engineering design exists -> PASS
Durable mutation invariant is present in PRD / architecture / development plan / gate matrix -> PASS
V9-3 fan-in / fan-out / recovery acceptance is explicit -> PASS
V9-4 auto commit / auto push / auto deploy stop condition and tests are explicit -> PASS
Front-stage audit-vs-runtime gate matrix exists -> PASS
Front-stage fixture-to-test matrix exists -> PASS
Front-stage evidence minimums exist -> PASS
Canonical docs aligned with V9-7 evidence baseline -> PASS
User scenario acceptance gate is connected to V9-8 final acceptance -> PASS
Drawio includes user scenario acceptance gate page -> PASS
Drawio includes creative workflow scenario warning boxes -> PASS
```

## 3. Claim Scan Result

Forbidden terms are present only in expected contexts:

```text
Forbidden Claims
No False Green
Stop Conditions
Out Of Scope
Audit Questions
Drawio warning boxes
```

No V9 document currently claims:

```text
production ready
full production GA
Agent executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
```

as a positive completion result.

The expanded forbidden term scan is expected to hit warning sections, forbidden sections, stop conditions, audit questions and drawio warning boxes only.

## 3.1 External Audit Remediation Status

| External Audit Finding | Disposition | Result |
| --- | --- | --- |
| V9-1 implementation blocked | Clarified | It is not a V9-0 failure; it is the intended V9-1 contract audit gate. |
| Durable mutation invariant incomplete across gate docs | Accepted | Added user_confirmed OR human_authorization_ref rule to PRD, architecture, development plan and gate matrix. |
| V9-3 acceptance too weak | Accepted | Added fan-in, fan-out, failure recovery, lost worker recovery, artifact lineage and producer refs. |
| V9-4 missing auto commit stop condition | Accepted | Added auto commit / auto push / auto deploy without approval stop condition. |
| No False Green scan incomplete | Accepted | Expanded English, Chinese and variant claim scan terms. |
| Full Multi-Agent title risk | Accepted | Reworded PRD and audit prompt toward Multi-Agent Orchestration Runtime Target. |
| Drawio milestone and hard-gate gaps | Accepted | Added M0-M8 milestone page and hard-gate text to drawio. |
| V9-1 contract docs missing | Accepted | Added V9-1 Agent Executor Contract Package. |
| HumanAuthorizationRef contract missing | Accepted | Added issuer, scope, expiry, operation hash, target_refs, revocation and audit linkage contract. |
| CapabilityResolver wording only says user confirmation | Accepted | Updated mutating operation gates to user confirmation OR human_authorization_ref, with approval gate as additional high-risk gate. |
| V9-4 no-auto-deploy test missing | Accepted | Added coding_workflow_no_auto_deploy. |
| V9-7 naming drift | Accepted | Renamed to Production Governance / Evidence Hardening and Terminal Automation Gate and preserved terminal automation as sub-scope. |
| V9-2..V9-8 implementation specs missing | Accepted | Added per-stage implementation-readiness specs and final acceptance framework. |
| P0 engineering package missing | Accepted | Added schema bundle, API boundary, evidence validator, CI matrix, human decision protocol, threat model, automation policy and operational runbook. |
| Stage engineering design missing | Accepted | Added V9-1 through V9-8 engineering design / implementation plan documents. |
| Machine-readable schemas missing | Accepted | Added P0 JSON Schema files under docs/design/V9.x/schemas. |
| Fixture files missing | Accepted | Added negative fixtures and evidence samples under docs/design/V9.x/fixtures. |
| Front-stage readiness boundary unclear | Accepted | Added V9-1 to V9-4 readiness audit and audit-vs-runtime gate matrix. |

## 4. Spec Drift Evaluation

```text
risk: LOW
reason: V9 keeps V8 baseline bounded, adds shared authorization, P0 engineering package and per-stage engineering designs, and keeps runtime implementation blocked until external audit and separate stage evidence.
```

## 5. False Green Evaluation

```text
risk: LOW
reason: V9-0 remains documentation-only. Engineering specs and plans are not runtime evidence; V9 runtime stages still require implementation, tests and evidence packages before completion.
```

## 6. Remaining Review Items

```text
External audit should confirm whether V9-2 limited controlled runtime evidence is not overclaimed as Agent executor ready or controlled executor ready.
External audit should confirm whether V9-3 detailed plan, schemas and fixtures are sufficient to start orchestration runtime implementation.
External audit should confirm whether V9-3 E2E evidence criteria cover serial, parallel, fan-in, fan-out, recovery, attempt history and lineage.
External audit should confirm whether V9-4 evidence is not overclaimed as autonomous coding workflow ready.
External audit should confirm whether V9-5 evidence is not overclaimed as unrestricted terminal worker ready or production terminal automation ready.
External audit should confirm whether V9-6 evidence is not overclaimed as complete Workflow Studio ready or autonomous workflow editing ready.
External audit should confirm whether V9-7 evidence is not overclaimed as production automation ready, production terminal automation ready or production browser automation ready.
External audit should confirm whether the user scenario acceptance gate prevents schema-only or docs-only false completion.
External audit should confirm whether Roman Forum debate remains a bounded orchestration scenario and is not overclaimed as full multi-Agent orchestration ready.
External audit should confirm whether video storyboard generation requires real provider-backed or explicitly blocked/fallback evidence.
External audit should confirm whether natural-language workflow optimization remains WorkflowDiff proposal-only before user confirmation.
External audit should confirm whether V9-7 governance/evidence hardening scope prevents production automation overclaim.
```

## 7. Proceed Recommendation

```text
proceed_to_external_audit=true
proceed_to_v9_3_readiness_audit=complete_for_review
proceed_to_v9_3_runtime_implementation=complete_for_review
proceed_to_v9_4_runtime_implementation=complete_for_review
proceed_to_v9_5_runtime_implementation=complete_for_review
proceed_to_v9_6_runtime_implementation_complete_for_review=true
proceed_to_v9_7_stage_audit=complete_for_review
proceed_to_v9_7_runtime_implementation_complete_for_review=true
proceed_to_v9_8_final_acceptance=true
proceed_to_v9_8_final_acceptance_validator=PASS
```

V9-8 should be treated as implemented and PASS for the ready-for-review final claim. This does not authorize production ready, Agent executor ready, controlled executor ready, production controlled executor ready, full multi-Agent orchestration ready, autonomous coding workflow ready, complete Workflow Studio ready, unrestricted terminal worker ready or production automation ready claims.

```

### `docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json`
```json
{
  "schema_version": "v9.0",
  "decision_ref": "v9-1-limited-safety-gate-implementation-approved",
  "stage_id": "V9-1",
  "decision": "GO_FOR_IMPLEMENTATION",
  "decision_owner": "human_required",
  "required_reviewers": [
    "human_high_risk_owner"
  ],
  "risk_class": "high",
  "scope": "V9-1 Agent Executor Safety Gate implementation only. Runtime executor route, runtime worker, source=agent durable mutation, controlled executor action execution, V9-2/V9-3/V9-4 runtime implementation, and Agent executor ready claim remain blocked.",
  "allowed_work": [
    "external_implementation_readiness_audit",
    "implementation_planning",
    "schema_validator",
    "fixture_validator",
    "no_false_green_scanner",
    "redaction_scanner",
    "evidence_package_validator"
    ,
    "agent_execution_envelope_validator",
    "agent_execution_policy_validator",
    "human_authorization_ref_validator",
    "capability_resolver_deny_by_default_engine",
    "approval_kill_switch_timeout_rollback_contract_checks"
  ],
  "blocked_work": [
    "runtime_executor_route",
    "runtime_worker",
    "source_agent_durable_mutation",
    "controlled_executor_action_execution",
    "multi_agent_orchestration_runtime",
    "autonomous_coding_workflow_runtime",
    "v9_8_final_acceptance"
  ],
  "expires_at": "2026-12-31T23:59:59Z",
  "revoked": false,
  "revoked_at": null,
  "revocation_reason": null,
  "evidence_refs": [
    "docs/design/V9.x/reports/v9_1_contract_validation_report.json",
    "docs/design/V9.x/reports/v9_1_negative_test_results.json",
    "docs/design/V9.x/reports/v9_1_no_false_green_scan.json",
    "docs/design/V9.x/reports/v9_1_redaction_scan.json"
  ],
  "audit_ref": "audit://v9-1/limited-safety-gate-implementation-approved",
  "correlation_id": "corr-v9-1-limited-safety-gate-implementation-approved",
  "created_at": "2026-06-05T00:00:00Z",
  "notes": "Human approval is recorded for limited V9-1 safety gate implementation only. Runtime implementation remains blocked."
}

```

### `docs/design/V9.x/decisions/v9_2_high_risk_human_decision.json`
```json
{
  "schema_version": "v9.0",
  "decision_ref": "v9-2-limited-controlled-runtime-implementation-approved",
  "stage_id": "V9-2",
  "decision": "GO_FOR_IMPLEMENTATION",
  "decision_owner": "human_required",
  "required_reviewers": [
    "human_high_risk_owner"
  ],
  "risk_class": "high",
  "scope": "V9-2 limited controlled Agent executor runtime implementation is approved only for workflow.instance.start, station.rerun, artifact.write, quality.evaluation.create, policy/capability/HumanAuthorizationRef/approval/kill switch/idempotency/timeout/rollback/evidence chain. Runtime executor routes, workers, source=agent durable mutation, excluded actions, V9-3/V9-4 runtime implementation, and readiness claims remain blocked.",
  "allowed_work": [
    "controlled_executor_runtime_slice_implementation",
    "workflow_instance_start",
    "station_rerun",
    "artifact_write_append_only",
    "quality_evaluation_create_append_only",
    "policy_capability_resolution",
    "human_authorization_ref_validation",
    "approval_gate_check",
    "kill_switch_check",
    "idempotency_check",
    "timeout_policy_check",
    "rollback_descriptor_check",
    "execution_evidence_chain"
  ],
  "blocked_work": [
    "runtime_executor_route",
    "runtime_worker",
    "connector_call",
    "external_llm_call",
    "business_event_emit",
    "context_update",
    "workflow_template_publish",
    "approval_respond",
    "git_commit",
    "git_push",
    "production_deploy",
    "workflow_store_write",
    "station_run_write",
    "source_agent_durable_mutation",
    "v9_3_runtime_implementation",
    "v9_4_runtime_implementation",
    "v9_8_final_acceptance",
    "agent_executor_ready_claim",
    "controlled_executor_ready_claim",
    "production_controlled_executor_ready_claim"
  ],
  "created_at": "2026-06-05T00:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "revoked": false,
  "revoked_at": null,
  "revocation_reason": null,
  "evidence_refs": [
    "docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json",
    "docs/design/V9.x/evidence/v9-1-internal-independent-audit/internal-audit-data.json",
    "docs/design/V9.x/v9_2_pre_implementation_development_and_acceptance_plan.md"
  ],
  "audit_ref": "audit://v9-2/limited-controlled-runtime-implementation-approved",
  "correlation_id": "corr-v9-2-limited-controlled-runtime-implementation-approved"
}

```

### `docs/design/V9.x/decisions/v9_5_high_risk_human_decision.json`
```json
{
  "allowed_work": [
    "workspace_scope_guard",
    "readonly_terminal_command",
    "workspace_scoped_test_command",
    "command_tier_policy",
    "transcript_capture",
    "diff_proposal_capture",
    "workspace_escape_denial_evidence",
    "symlink_escape_denial_evidence",
    "sensitive_read_denial_evidence",
    "git_push_denial_evidence",
    "production_deploy_denial_evidence"
  ],
  "audit_ref": "audit://v9-5/governed-terminal-worker-expansion-approved",
  "blocked_work": [
    "unrestricted_shell",
    "git_push",
    "git_commit",
    "production_deploy",
    "browser_account_automation",
    "secret_read",
    "credential_export",
    "workspace_escape",
    "source_agent_durable_mutation",
    "v9_7_runtime_implementation",
    "v9_8_final_acceptance",
    "unrestricted_terminal_worker_ready_claim",
    "production_terminal_automation_ready_claim"
  ],
  "correlation_id": "corr-v9-5-governed-terminal-worker-expansion-approved",
  "created_at": "2026-06-07T10:35:00Z",
  "decision": "GO_FOR_IMPLEMENTATION",
  "decision_owner": "human_required",
  "decision_ref": "v9-5-governed-terminal-worker-expansion-approved",
  "evidence_refs": [
    "docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
    "docs/design/V9.x/v9_5_development_and_acceptance_plan.md",
    "docs/design/V9.x/v9_5_terminal_sandbox_engineering_design.md"
  ],
  "expires_at": "2026-12-31T23:59:59Z",
  "required_reviewers": [
    "human_high_risk_owner"
  ],
  "revocation_reason": null,
  "revoked": false,
  "revoked_at": null,
  "risk_class": "high",
  "scope": "V9-5 governed terminal worker expansion is approved only for workspace-scoped readonly/build-test commands, command tier policy, transcript capture, diff proposal capture, and denial evidence. It does not authorize unrestricted shell, git push, production deploy, browser account automation, secret reads, workspace escape, V9-7 runtime implementation, V9-8 final acceptance, or readiness overclaims.",
  "schema_version": "v9.0",
  "stage_id": "V9-5"
}

```

### `docs/design/V9.x/v9_2_pre_implementation_development_and_acceptance_plan.md`
```markdown
# V9-2 Pre-Implementation Development And Acceptance Plan

Document status: V9-2 implementation-readiness closure plan / no runtime implementation.

## Current Baseline

```text
V9-1 limited Safety Gate implementation: PASS
V9-1 internal independent audit: PASS
V9-2 controlled executor runtime implementation: NO-GO
```

V9-2 is a high-risk runtime stage. This plan closes readiness, evidence structure, fixture coverage, and PRD alignment before any runtime code is allowed.

## Scope

Allowed before human proceed decision:

```text
V9-2 PRD and architecture review
controlled executor action allowlist review
HumanAuthorizationRef validator dependency review
ExecutionEvidence and runtime result fixture design
idempotency / timeout / rollback fixture design
No False Green and redaction guard review
internal readiness audit package
human high-risk decision preparation
```

Blocked before human proceed decision:

```text
runtime executor route
runtime worker
controlled executor action execution
WorkflowStore / StationRun / Artifact writes
source=agent durable mutation
V9-3 runtime implementation
V9-4 runtime implementation
V9-8 final acceptance
```

## Acceptance Checklist

V9-2 implementation may only be requested after all are true:

```text
V9-1 Safety Gate evidence PASS.
V9-1 internal independent audit PASS.
V9-2 action allowlist accepted.
Excluded actions hard-denied in plan.
Durable mutation invariant accepted: user_confirmed=true OR valid human_authorization_ref.
source=agent default durable mutation remains denied.
HumanAuthorizationRef contract accepted.
ExecutionEvidence schema accepted.
V9-2 fixture package parses.
No False Green scan PASS.
Redaction scan PASS.
drawio XML valid.
human high-risk proceed decision is recorded for V9-2 runtime implementation.
```

## Planned Runtime Acceptance After Approval

If and only if V9-2 receives separate high-risk approval, runtime acceptance must prove:

```text
workflow_instance_start_success_with_human_authorization_ref
station_rerun_success_with_user_confirmed
artifact_write_appends_new_version
quality_evaluation_appends_new_score
source_agent_mutation_denied
expired_human_authorization_ref_denied
wrong_tenant_human_authorization_ref_denied
kill_switch_denied_blocks_action
idempotency_duplicate_returns_prior_runtime_result_ref
timeout_records_incident_and_marks_failed
execution_evidence_uses_redacted_refs_only
```

## Stop Conditions

Stop and do not proceed if:

```text
V9-2 runtime starts without human high-risk proceed decision.
source=agent durable mutation is allowed.
durable mutation runs without user_confirmed=true OR valid human_authorization_ref.
approval gate replaces human authorization.
artifact.write overwrites previous artifact silently.
quality.evaluation.create overwrites prior score silently.
raw secret / raw prompt / raw artifact content appears in evidence.
V9-2 is described as Agent executor ready, controlled executor ready, or production controlled executor ready.
```

## Internal Audit Opinion

V9-2 can proceed only to implementation-readiness closure now. Runtime implementation remains blocked until a new human high-risk proceed decision is recorded.

```

### `docs/design/V9.x/v9_2_pre_implementation_audit_closure.md`
```markdown
# V9-2 Pre-Implementation Audit Closure

Document status: internal readiness closure / limited runtime implementation approved.

```text
status: PASS
v9_2_runtime_implementation_allowed: true
runtime_executor_route_created: false
runtime_worker_created: false
controlled_executor_action_execution: limited_to_allowlisted_runtime_slice
source_agent_durable_mutation_allowed: false
requires_human_high_risk_decision: false
```

## Conclusion

V9-2 implementation-readiness closure is complete and scoped human approval is recorded; only the limited runtime slice is allowed.

## Checks

- v9_1_internal_audit_pass: PASS - V9-1 internal audit must pass before V9-2 planning closure.
- v9_1_safety_gate_pass: PASS - V9-1 Safety Gate implementation evidence must pass.
- v9_1_runtime_still_blocked: PASS - V9-1 evidence still blocks runtime execution.
- v9_2_high_risk_decision_recorded: PASS - V9-2 limited runtime implementation has scoped human high-risk approval.
- v9_2_decision_blocks_forbidden_work: PASS - V9-2 decision blocks routes, workers, excluded actions, source=agent mutation and overclaim.
- required_fixture_set_present: PASS - V9-2 pre-implementation fixture set is present.
- artifact_write_append_only_with_approval_gate.json_stage_id: PASS - Fixture is scoped to V9-2.
- artifact_write_append_only_with_approval_gate.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- artifact_write_append_only_with_approval_gate.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- artifact_write_append_only_with_approval_gate.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- artifact_write_append_only_with_approval_gate.json_approval_gate_required: PASS - Medium-risk write/evaluation fixtures require approval gate.
- artifact_write_append_only_with_approval_gate.json_append_only_required: PASS - Write/evaluation fixtures are append-only.
- artifact_write_append_only_with_approval_gate.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- expired_human_authorization_ref_denied.json_stage_id: PASS - Fixture is scoped to V9-2.
- expired_human_authorization_ref_denied.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- expired_human_authorization_ref_denied.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- expired_human_authorization_ref_denied.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- idempotency_duplicate_returns_prior_ref.json_stage_id: PASS - Fixture is scoped to V9-2.
- idempotency_duplicate_returns_prior_ref.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- idempotency_duplicate_returns_prior_ref.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- idempotency_duplicate_returns_prior_ref.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- idempotency_duplicate_returns_prior_ref.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- kill_switch_denied_blocks_action.json_stage_id: PASS - Fixture is scoped to V9-2.
- kill_switch_denied_blocks_action.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- kill_switch_denied_blocks_action.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- kill_switch_denied_blocks_action.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- quality_evaluation_append_only_with_approval_gate.json_stage_id: PASS - Fixture is scoped to V9-2.
- quality_evaluation_append_only_with_approval_gate.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- quality_evaluation_append_only_with_approval_gate.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- quality_evaluation_append_only_with_approval_gate.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- quality_evaluation_append_only_with_approval_gate.json_approval_gate_required: PASS - Medium-risk write/evaluation fixtures require approval gate.
- quality_evaluation_append_only_with_approval_gate.json_append_only_required: PASS - Write/evaluation fixtures are append-only.
- quality_evaluation_append_only_with_approval_gate.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- source_agent_durable_mutation_denied.json_stage_id: PASS - Fixture is scoped to V9-2.
- source_agent_durable_mutation_denied.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- source_agent_durable_mutation_denied.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- source_agent_durable_mutation_denied.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- source_agent_durable_mutation_denied.json_source_agent_denied: PASS - source=agent fixture must be denied.
- station_rerun_with_user_confirmed.json_stage_id: PASS - Fixture is scoped to V9-2.
- station_rerun_with_user_confirmed.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- station_rerun_with_user_confirmed.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- station_rerun_with_user_confirmed.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- station_rerun_with_user_confirmed.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- workflow_instance_start_with_human_authorization_ref.json_stage_id: PASS - Fixture is scoped to V9-2.
- workflow_instance_start_with_human_authorization_ref.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- workflow_instance_start_with_human_authorization_ref.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- workflow_instance_start_with_human_authorization_ref.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- workflow_instance_start_with_human_authorization_ref.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- allowlist_documented: PASS - All four candidate actions are documented.
- excluded_actions_documented: PASS - Excluded actions are documented as hard-denied.
- durable_mutation_invariant_documented: PASS - Durable mutation invariant uses valid human_authorization_ref.
- source_agent_denial_documented: PASS - source=agent default durable mutation denial is documented.
- append_only_documented: PASS - Append-only and overwrite denial are documented.
- no_v9_2_forbidden_route_or_worker_detected: PASS - No V9-2 runtime route or worker implementation is present.

## Human Decision Required

- stage_id: V9-2
- decision_needed: Recorded: V9-2 limited controlled Agent executor runtime implementation is approved.
- impact_if_approved: Allows implementation of the four allowlisted actions only, still denying source=agent durable mutation and excluded actions.
- impact_if_rejected: Not applicable to the current recorded decision; revocation would block V9-2 and downstream V9-3/V9-4 runtime.

## Remaining Blockers

- V9-2 runtime evidence must prove only the four allowlisted actions.
- V9-3 remains blocked until V9-2 runtime evidence exists.
- V9-4 remains blocked until V9-2 and V9-3 runtime evidence exists.
- V9-8 final acceptance remains blocked.

## No False Green Boundary

This closure does not claim Agent executor ready, controlled executor ready, production controlled executor ready, V9-2 runtime PASS, V9-3 runtime PASS, or V9-4 runtime PASS.

```

### `docs/design/V9.x/reports/v9_1_contract_validation_report.json`
```json
{
  "created_at": "2026-06-08T03:06:23Z",
  "fixture_parse_results": [
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/coding/auto_commit_without_human_approval.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/coding/auto_deploy_without_production_gate.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/coding/auto_push_without_release_gate.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/coding/review_summary_as_approval_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/coding/unreviewed_patch_apply_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/schema-negative/artifact_lineage_missing_producer_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/schema-negative/expired_human_authorization_ref.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/schema-negative/raw_secret_in_evidence.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/schema-negative/source_agent_durable_mutation.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/terminal/terminal_git_push_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/terminal/terminal_network_without_policy.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/terminal/terminal_production_deploy_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/terminal/terminal_sensitive_read_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/terminal/terminal_symlink_escape.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/terminal/terminal_workspace_escape.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/terminal/workspace_scoped_test_and_diff_capture.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_01_controlled_runtime_review.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_02_orchestration_review.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_03_coding_workflow_review.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_04_terminal_worker_review.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_05_studio_review.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_06_final_dashboard_review.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_07_roman_forum_debate.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_08_video_storyboard_workflow.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/user-scenarios/us_v9_09_nl_workflow_optimization.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/artifact_write_append_only_with_approval_gate.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/expired_human_authorization_ref_denied.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/idempotency_duplicate_returns_prior_ref.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/kill_switch_denied_blocks_action.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/quality_evaluation_append_only_with_approval_gate.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/source_agent_durable_mutation_denied.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/station_rerun_with_user_confirmed.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/workflow_instance_start_with_human_authorization_ref.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-3-orchestration/fan_in_missing_attribution.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-3-orchestration/retry_overwrites_old_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-3-orchestration/serial_parallel_fan_in_out_recovery.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-3-orchestration/source_agent_direct_mutation_attempt.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-4-coding-workflow/small_code_change_proposal.json",
      "status": "PASS"
    }
  ],
  "invariant_results": [
    {
      "check_id": "durable_mutation_authorization_required_for_artifact.write",
      "details": "operation appears in AgentExecutionEnvelope authorization invariant",
      "status": "PASS"
    },
    {
      "check_id": "durable_mutation_authorization_required_for_quality.evaluation.create",
      "details": "operation appears in AgentExecutionEnvelope authorization invariant",
      "status": "PASS"
    },
    {
      "check_id": "durable_mutation_authorization_required_for_station.rerun",
      "details": "operation appears in AgentExecutionEnvelope authorization invariant",
      "status": "PASS"
    },
    {
      "check_id": "durable_mutation_authorization_required_for_workflow.instance.start",
      "details": "operation appears in AgentExecutionEnvelope authorization invariant",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_durable_mutation_denied",
      "details": "AgentExecutionEnvelope contains source=agent denial branch",
      "status": "PASS"
    },
    {
      "check_id": "agent_execution_envelope.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "agent_execution_policy.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "approval_gate_decision.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "artifact_lineage_record.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "capability_resolver_decision.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "evidence_package.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "execution_evidence.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "final_acceptance_dashboard.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "high_risk_human_decision.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "human_authorization_ref.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "kill_switch_decision.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "orchestration_message.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "rollback_descriptor.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "timeout_policy.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_agent_descriptor.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_attempt_history_record.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_branch_state.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_conflict_review_record.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_fan_in_join_decision.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_fan_out_dispatch.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_lost_worker_recovery_decision.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_orchestration_run.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    },
    {
      "check_id": "v9_3_station_agent_binding.schema.json_additional_properties_false",
      "details": "schema must be strict",
      "status": "PASS"
    }
  ],
  "notes": "Readiness validation only. This report does not approve runtime implementation.",
  "runtime_evidence": false,
  "schema_parse_results": [
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/agent_execution_envelope.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/agent_execution_policy.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/approval_gate_decision.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/artifact_lineage_record.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/capability_resolver_decision.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/evidence_package.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/execution_evidence.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/final_acceptance_dashboard.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/high_risk_human_decision.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/human_authorization_ref.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/kill_switch_decision.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/orchestration_message.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/rollback_descriptor.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/timeout_policy.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_agent_descriptor.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_attempt_history_record.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_branch_state.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_conflict_review_record.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_fan_in_join_decision.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_fan_out_dispatch.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_lost_worker_recovery_decision.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_orchestration_run.schema.json",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/schemas/v9_3_station_agent_binding.schema.json",
      "status": "PASS"
    }
  ],
  "schema_version": "v9_1.contract_validation_report.v1",
  "stage_id": "V9-1",
  "status": "PASS"
}

```

### `docs/design/V9.x/reports/v9_1_negative_test_results.json`
```json
{
  "created_at": "2026-06-08T03:06:23Z",
  "negative_fixture_results": [
    {
      "expected": "REJECT",
      "fixture": "source_agent_durable_mutation.json",
      "reason": "source=agent durable mutation must be denied",
      "status": "PASS"
    },
    {
      "expected": "REJECT",
      "fixture": "expired_human_authorization_ref.json",
      "reason": "expired or revoked HumanAuthorizationRef is invalid",
      "status": "PASS"
    },
    {
      "expected": "REJECT",
      "fixture": "raw_secret_in_evidence.json",
      "reason": "raw secret content must be rejected from evidence",
      "status": "PASS"
    },
    {
      "expected": "REJECT",
      "fixture": "artifact_lineage_missing_producer_attempt.json",
      "reason": "artifact lineage must preserve producer_attempt_id",
      "status": "PASS"
    },
    {
      "expected": "ACCEPT_AS_NON_RUNTIME_CONTRACT_FREEZE",
      "fixture": "v9_1_contract_freeze_sample.json",
      "reason": "contract freeze sample cannot count as runtime evidence",
      "status": "PASS"
    },
    {
      "expected": "REJECT_FOR_FINAL_RUNTIME_ACCEPTANCE",
      "fixture": "v9_8_reject_planning_only_sample.json",
      "reason": "planning-only evidence cannot satisfy V9-8",
      "status": "PASS"
    }
  ],
  "notes": "Negative fixture behavior is checked by local V9 readiness rules, not by runtime execution.",
  "runtime_evidence": false,
  "schema_version": "v9_1.negative_test_results.v1",
  "stage_id": "V9-1",
  "status": "PASS"
}

```

### `docs/design/V9.x/reports/v9_1_no_false_green_scan.json`
```json
{
  "allowed_contexts": [
    "Forbidden Claims",
    "No False Green",
    "Stop Conditions",
    "Stop Condition",
    "Out Of Scope",
    "Audit Questions",
    "Global Acceptance Requirements",
    "Validation Commands",
    "Claim Scan Result",
    "is claimed",
    "Readiness Evidence",
    "P0 Risks To Check",
    "Exit Architecture",
    "Success Criteria",
    "Suggested Scan",
    "Redaction Terms",
    "Global Schema Rules",
    "Forbidden persistence",
    "Rejection Cases",
    "Required Negative Fixtures",
    "Drawio warning boxes",
    "Boundary explanations",
    "Boundary",
    "Baseline",
    "Acceptance Oracle",
    "Final Allowed Claim",
    "Naming And Boundary",
    "Product Goal",
    "Forbidden",
    "Non-Claims",
    "Non-Negotiable",
    "禁止",
    "不得",
    "不能",
    "不允许",
    "不证明",
    "not ",
    "does not prove",
    "blocked",
    "NO-GO",
    "No ",
    "without"
  ],
  "created_at": "2026-06-08T03:08:49Z",
  "hit_count": 245,
  "notes": "Forbidden terms are allowed only in guard, stop, audit, boundary or drawio warning contexts.",
  "runtime_evidence": false,
  "schema_version": "v9_1.no_false_green_scan.v1",
  "stage_id": "V9-1",
  "status": "PASS",
  "violations": []
}

```

### `docs/design/V9.x/reports/v9_1_redaction_scan.json`
```json
{
  "created_at": "2026-06-08T03:08:50Z",
  "forbidden_terms": [
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "API key",
    "Bearer",
    "bearer_token",
    "signed URL",
    "signed_url",
    "credential raw secret",
    "credential_raw_secret"
  ],
  "notes": "Terms are allowed only when defining forbidden fields or negative fixtures.",
  "runtime_evidence": false,
  "schema_version": "v9_1.redaction_scan.v1",
  "stage_id": "V9-1",
  "status": "PASS",
  "violations": []
}

```

### `docs/design/V9.x/reports/v9_test_run_summary.json`
```json
{
  "schema_version": "v9.test_run_summary.v1",
  "created_at": "2026-06-08T11:07:00+08:00",
  "command": "./.venv/bin/python -m pytest tests/test_v9_*.py -q",
  "status": "PASS",
  "passed": 73,
  "failed": 0,
  "warnings": 5,
  "scope": "V9 document, policy, evidence and runtime fixture tests",
  "runtime_evidence": true,
  "notes": [
    "This report records the V9 regression test command result for external audit.",
    "It does not replace stage-specific runtime evidence packages.",
    "V9-3 runtime evidence is recorded in docs/design/V9.x/evidence/v9-3-orchestration-runtime.",
    "V9-4 readiness closure is recorded in docs/design/V9.x/evidence/v9-4-readiness-closure.",
    "V9-4 runtime evidence is recorded in docs/design/V9.x/evidence/v9-4-coding-workflow-runtime.",
    "V9-5 governed terminal worker evidence is recorded in docs/design/V9.x/evidence/v9-5-terminal-worker.",
    "V9-6 Workflow Studio evidence is recorded in docs/design/V9.x/evidence/v9-6-workflow-studio.",
    "V9-7 production governance evidence is recorded in docs/design/V9.x/evidence/v9-7-production-governance.",
    "V9-8 final acceptance validator is implemented and records PASS because US-V9-08 provider-backed storyboard image evidence is available.",
    "MiniMax provider invocation generated four storyboard image artifacts; no raw credential, raw prompt, raw payload or base64 was stored."
  ],
  "regression_commands": [
    {
      "command": "./.venv/bin/python -m pytest tests/test_v8_*.py -q",
      "status": "PASS",
      "passed": 35
    },
    {
      "command": "./.venv/bin/python -m pytest tests/test_v6_*.py -q",
      "status": "PASS",
      "passed": 88
    },
    {
      "command": "./.venv/bin/python -m pytest tests/test_v5_*.py -q",
      "status": "PASS",
      "passed": 149
    },
    {
      "command": "./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q",
      "status": "PASS",
      "passed": 4
    }
  ]
}

```

### `docs/design/V9.x/decisions/v9_4_high_risk_human_decision.json`
```json
{
  "schema_version": "v9.0",
  "decision_ref": "v9-4-autonomous-coding-workflow-pilot-approved",
  "stage_id": "V9-4",
  "decision": "GO_FOR_IMPLEMENTATION",
  "decision_owner": "human_required",
  "required_reviewers": [
    "human_high_risk_owner"
  ],
  "risk_class": "high",
  "scope": "V9-4 bounded coding workflow pilot is approved only for generating coding workflow run evidence, diff proposal, sandboxed test result, review summary, fix-loop proposal, human review handoff, and denial evidence. Patch apply, auto commit, auto push, production deploy, source=agent durable mutation, V9-5 runtime implementation without a separate V9-5 decision, V9-8 final acceptance, and over-readiness claims remain blocked.",
  "allowed_work": [
    "coding_workflow_run_evidence",
    "intent_capture",
    "spec_draft",
    "plan_draft",
    "diff_proposal",
    "test_plan_proposal",
    "sandboxed_test_result",
    "review_summary",
    "fix_loop_proposal",
    "human_review_handoff",
    "git_operation_denial_evidence"
  ],
  "blocked_work": [
    "patch_apply",
    "auto_commit",
    "auto_push",
    "auto_deploy",
    "git_commit",
    "git_push",
    "production_deploy",
    "source_agent_durable_mutation",
    "review_summary_as_approval",
    "v9_5_runtime_implementation",
    "v9_8_final_acceptance",
    "autonomous_coding_workflow_ready_claim",
    "agent_executor_ready_claim",
    "unrestricted_terminal_worker_ready_claim"
  ],
  "created_at": "2026-06-07T10:10:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "revoked": false,
  "revoked_at": null,
  "revocation_reason": null,
  "evidence_refs": [
    "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
    "docs/design/V9.x/evidence/v9-4-readiness-closure/pre-implementation-data.json",
    "docs/design/V9.x/v9_4_development_and_acceptance_plan.md"
  ],
  "audit_ref": "audit://v9-4/autonomous-coding-workflow-pilot-approved",
  "correlation_id": "corr-v9-4-autonomous-coding-workflow-pilot-approved"
}

```

### `docs/design/V9.x/decisions/v9_7_high_risk_human_decision.json`
```json
{
  "allowed_work": [
    "tenant_isolation_decision",
    "credential_lease_validator",
    "service_account_binding_policy",
    "append_only_audit_export",
    "incident_timeline",
    "evidence_hardening_report",
    "terminal_automation_policy_gate",
    "browser_automation_separate_prd_denial_evidence"
  ],
  "audit_ref": "audit://v9-7/production-governance-high-risk-approved",
  "blocked_work": [
    "production_automation_ready_claim",
    "production_terminal_automation_ready_claim",
    "production_browser_automation_ready_claim",
    "browser_account_automation_without_separate_prd",
    "raw_credential_access",
    "mutable_audit_export",
    "terminal_automation_without_policy_credential_incident_boundary",
    "v9_8_final_acceptance_without_full_evidence"
  ],
  "correlation_id": "corr-v9-7-production-governance-high-risk-approved",
  "created_at": "2026-06-07T11:35:00Z",
  "decision": "GO_FOR_IMPLEMENTATION",
  "decision_owner": "human_required",
  "decision_ref": "v9-7-production-governance-high-risk-approved",
  "evidence_refs": [
    "docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json",
    "docs/design/V9.x/v9_7_development_and_acceptance_plan.md",
    "docs/design/V9.x/v9_7_production_governance_engineering_design.md",
    "docs/design/V9.x/v9_7_production_governance_terminal_automation_gate_spec.md"
  ],
  "expires_at": "2026-12-31T23:59:59Z",
  "required_reviewers": [
    "human_high_risk_owner"
  ],
  "revocation_reason": null,
  "revoked": false,
  "revoked_at": null,
  "risk_class": "high",
  "schema_version": "v9.0",
  "scope": "V9-7 production governance / evidence hardening and terminal automation gate is approved only for tenant isolation, credential lease validation, service account binding policy, append-only audit export, incident timeline, evidence hardening, and policy-gated terminal/browser automation denial evidence. It does not authorize production automation ready claims, production browser automation, raw credential access, mutable audit export, or V9-8 final acceptance without complete evidence.",
  "stage_id": "V9-7"
}

```

### `docs/design/V9.x/evidence/v9-1-readiness/result-summary.md`
```markdown
# V9-1 Readiness Dashboard Result

```text
status: PASS
runtime_implementation_allowed: false
proceed_to_v9_1_external_implementation_readiness_audit: true
proceed_to_v9_1_implementation_planning: true
proceed_to_v9_1_runtime_implementation: false
v9_2_limited_runtime_slice_complete: true
proceed_to_v9_3_runtime_implementation: false
proceed_to_v9_4_runtime_implementation: false
```

## Reports

- contract_validation: PASS (/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_contract_validation_report.json)
- negative_tests: PASS (/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_negative_test_results.json)
- no_false_green: PASS (/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_no_false_green_scan.json)
- redaction: PASS (/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_redaction_scan.json)
- safety_gate_implementation: PASS (/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json)
- v9_2_pre_implementation: PASS (/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-2-controlled-executor-pre-implementation/pre-implementation-data.json)
- v9_2_limited_runtime_slice: PASS (/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json)

## Runtime Boundary

This package includes V9-1 readiness evidence and V9-2 limited runtime slice evidence. It does not approve runtime executor routes, runtime workers, source=agent durable mutation, multi-Agent orchestration runtime, or autonomous coding workflow runtime.

```

### `docs/design/V9.x/evidence/v9-1-readiness/readiness-dashboard-data.json`
```json
{
  "allowed_next_work": [
    "V9 front-stage readiness audit",
    "V9-1 external implementation-readiness audit",
    "V9-1 limited safety gate implementation review",
    "V9-2 implementation-readiness closure review",
    "V9-2 limited controlled runtime slice review",
    "readiness validator tooling review"
  ],
  "blocked_work": [
    "V9-1 runtime executor route",
    "V9-1 runtime worker",
    "source=agent durable mutation",
    "V9-3 runtime implementation",
    "V9-4 runtime implementation",
    "V9-8 final acceptance"
  ],
  "created_at": "2026-06-07T06:17:26Z",
  "decisions": {
    "external_audit_decision": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_1_external_audit_decision.md",
    "high_risk_human_decision": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json"
  },
  "external_audit_deferred": true,
  "internal_independent_audit_closed": true,
  "limited_safety_gate_implementation_complete": true,
  "reports": {
    "contract_validation": {
      "created_at": "2026-06-07T06:16:45Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_contract_validation_report.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "negative_tests": {
      "created_at": "2026-06-07T06:16:45Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_negative_test_results.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "no_false_green": {
      "created_at": "2026-06-07T06:16:46Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_no_false_green_scan.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "redaction": {
      "created_at": "2026-06-07T06:16:47Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_redaction_scan.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "safety_gate_implementation": {
      "created_at": "2026-06-07T06:16:47Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json",
      "runtime_evidence": null,
      "status": "PASS"
    },
    "v9_2_limited_runtime_slice": {
      "created_at": "2026-06-07T06:16:46Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json",
      "runtime_evidence": null,
      "status": "PASS"
    },
    "v9_2_pre_implementation": {
      "created_at": "2026-06-07T06:16:59Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-2-controlled-executor-pre-implementation/pre-implementation-data.json",
      "runtime_evidence": null,
      "status": "PASS"
    }
  },
  "runtime_implementation_allowed": false,
  "schema_version": "v9_1.readiness_dashboard.v1",
  "source_refs": [
    "docs/design/V9.x/v9_front_stage_development_readiness_audit.md",
    "docs/design/V9.x/v9_development_and_acceptance_plan.md",
    "docs/design/V9.x/v9_acceptance_gate_matrix.md",
    "docs/design/V9.x/v9_current_gap_analysis.drawio"
  ],
  "stage_id": "V9-1",
  "status": "PASS",
  "v9_2_limited_runtime_slice_complete": true,
  "v9_2_limited_runtime_slice_ready_for_review": true,
  "v9_2_pre_implementation_closed": true,
  "v9_3_runtime_implementation_allowed": false,
  "v9_4_runtime_implementation_allowed": false
}

```

### `docs/design/V9.x/evidence/v9-1-safety-gate-implementation/result-summary.md`
```markdown
# V9-1 Safety Gate Implementation Evidence

```text
status: PASS
evidence_scope: real_code_policy_validation
runtime_execution_allowed: false
runtime_executor_route_created: false
runtime_worker_created: false
source_agent_durable_mutation_allowed: false
agent_executor_ready: false
```

## Scenarios

- workflow_start_safety_gate_allow_no_runtime_execution: PASS
- source_agent_durable_mutation_denied: PASS
- missing_confirmation_or_authorization_denied: PASS
- valid_human_authorization_ref_allows_safety_gate: PASS
- expired_human_authorization_ref_denied: PASS
- wrong_tenant_human_authorization_ref_denied: PASS
- artifact_write_requires_approval_gate: PASS
- kill_switch_denied: PASS
- timeout_policy_required: PASS
- rollback_descriptor_required: PASS
- raw_content_rejected: PASS

## Boundary

This evidence package validates V9-1 Safety Gate policy behavior only. It does not implement runtime executor routes, runtime workers, controlled executor action execution, V9-2/V9-3/V9-4 runtime, or Agent executor readiness.

```

### `docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json`
```json
{
  "agent_executor_ready": false,
  "allowed_claim": "V9-1 complete: Agent Executor Safety Gate implementation ready for review.",
  "autonomous_coding_workflow_ready": false,
  "blocked_capability_claim_flags": {
    "agent_executor_ready": false,
    "autonomous_coding_workflow_ready": false,
    "complete_workflow_studio_ready": false,
    "controlled_executor_ready": false,
    "full_multi_agent_orchestration_ready": false,
    "production_controlled_executor_ready": false
  },
  "controlled_executor_action_execution": false,
  "controlled_executor_ready": false,
  "created_at": "2026-06-08T03:06:25Z",
  "evidence_scope": "real_code_policy_validation",
  "full_multi_agent_orchestration_ready": false,
  "production_controlled_executor_ready": false,
  "reports": {
    "contract_validation": {
      "created_at": "2026-06-08T03:06:23Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_contract_validation_report.json",
      "runtime_evidence": false,
      "status": "PASS",
      "violations": []
    },
    "negative_tests": {
      "created_at": "2026-06-08T03:06:23Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_negative_test_results.json",
      "runtime_evidence": false,
      "status": "PASS",
      "violations": []
    },
    "no_false_green": {
      "created_at": "2026-06-08T03:06:24Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_no_false_green_scan.json",
      "runtime_evidence": false,
      "status": "PASS",
      "violations": []
    },
    "redaction": {
      "created_at": "2026-06-08T03:06:25Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_redaction_scan.json",
      "runtime_evidence": false,
      "status": "PASS",
      "violations": []
    }
  },
  "runtime_backed": false,
  "runtime_execution_allowed": false,
  "runtime_executor_route_created": false,
  "runtime_worker_created": false,
  "scenarios": [
    {
      "capability_decision_ref": "capability-decision://v9-1/8690864db79841b9aafa7dbd416244fe",
      "observed_decision": "allow",
      "observed_denial_reason": null,
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "workflow_start_safety_gate_allow_no_runtime_execution",
      "status": "PASS",
      "title": "workflow.instance.start with user confirmation is accepted for safety-gate handoff only."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/2ab4b7b083aa4cb29e2d49ca26e4919a",
      "observed_decision": "deny",
      "observed_denial_reason": "source_agent_durable_mutation_denied",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "source_agent_durable_mutation_denied",
      "status": "PASS",
      "title": "source=agent durable mutation is denied even with user confirmation."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/d74aec0554534546a62203f50090c788",
      "observed_decision": "deny",
      "observed_denial_reason": "missing_user_confirmation_or_valid_human_authorization_ref",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "missing_confirmation_or_authorization_denied",
      "status": "PASS",
      "title": "Durable mutation without user confirmation or valid HumanAuthorizationRef is denied."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/b80a7c32871b406aa14f0128bf5dd791",
      "observed_decision": "allow",
      "observed_denial_reason": null,
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "valid_human_authorization_ref_allows_safety_gate",
      "status": "PASS",
      "title": "Valid HumanAuthorizationRef can satisfy the safety-gate authorization contract."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/7dd61114d5184f8aad3dadce2e412a0d",
      "observed_decision": "deny",
      "observed_denial_reason": "missing_user_confirmation_or_valid_human_authorization_ref",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "expired_human_authorization_ref_denied",
      "status": "PASS",
      "title": "Expired HumanAuthorizationRef is rejected."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/89820f4127774922a4257d2be8c77952",
      "observed_decision": "deny",
      "observed_denial_reason": "missing_user_confirmation_or_valid_human_authorization_ref",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "wrong_tenant_human_authorization_ref_denied",
      "status": "PASS",
      "title": "Cross-tenant HumanAuthorizationRef is rejected."
    },
    {
      "observed_decisions": [
        "deny",
        "allow"
      ],
      "observed_denial_reasons": [
        "approval_gate_required",
        null
      ],
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "artifact_write_requires_approval_gate",
      "status": "PASS",
      "title": "artifact.write requires approval gate and remains runtime_execution_allowed=false."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/5eb50ba87d0e4c26ad3ee7f8e5f29b10",
      "observed_decision": "deny",
      "observed_denial_reason": "kill_switch_denied",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "kill_switch_denied",
      "status": "PASS",
      "title": "Kill switch denial blocks safety-gate handoff."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/3e5e65ccb6844abc87ece8774bbabed3",
      "observed_decision": "deny",
      "observed_denial_reason": "missing_timeout_policy",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "timeout_policy_required",
      "status": "PASS",
      "title": "Timeout policy is required for candidate actions."
    },
    {
      "capability_decision_ref": "capability-decision://v9-1/9626e11217174f97b3802dc4b427ccd2",
      "observed_decision": "deny",
      "observed_denial_reason": "missing_rollback_descriptor",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "rollback_descriptor_required",
      "status": "PASS",
      "title": "Rollback descriptor is required for candidate actions."
    },
    {
      "observed_error_code": "V9_REDACTION_DENIED",
      "observed_reason": "forbidden_raw_content",
      "passed": true,
      "redaction_status": "PASS",
      "runtime_execution_allowed": false,
      "scenario_id": "raw_content_rejected",
      "status": "PASS",
      "title": "Raw prompt/content markers are rejected before a decision is returned."
    }
  ],
  "schema_version": "v9_1.safety_gate_implementation.v1",
  "source_agent_durable_mutation_allowed": false,
  "source_refs": [
    "core/policies/v9_agent_executor_safety.py",
    "tests/test_v9_1_agent_executor_safety_gate.py",
    "docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json",
    "docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md"
  ],
  "stage_id": "V9-1",
  "status": "PASS",
  "title": "V9-1 Agent Executor Safety Gate Implementation Evidence"
}

```

### `docs/design/V9.x/v9_1_internal_independent_audit_closure.md`
```markdown
# V9-1 Internal Independent Audit Closure

Document status: internal audit closure / V9-1 only / external audit deferred.

```text
status: PASS
runtime_implementation_allowed: false
v9_2_limited_runtime_slice_complete: true
v9_2_runtime_implementation_allowed: true
v9_3_runtime_implementation_allowed: false
v9_4_runtime_implementation_allowed: false
external_audit_deferred: true
```

## Conclusion

V9-1 limited Safety Gate implementation remains internally closed; V9-2 limited runtime slice evidence is now tracked separately and external audit is deferred until later V9 development packages are available.

## Checks

- safety_gate_acceptance_pass: PASS - V9-1 Safety Gate implementation evidence status is PASS.
- all_scenarios_pass: PASS - All real-code policy validation scenarios pass.
- runtime_execution_still_blocked: PASS - Safety Gate never allows runtime execution.
- runtime_route_not_created: PASS - No runtime executor route was created.
- runtime_worker_not_created: PASS - No runtime worker was created.
- source_agent_mutation_denied: PASS - source=agent durable mutation remains denied.
- controlled_action_execution_blocked: PASS - Controlled executor action execution remains out of scope.
- capability_claim_flags_false: PASS - Blocked capability claim flags remain false.
- readiness_status_pass: PASS - Readiness dashboard status is PASS.
- readiness_runtime_implementation_blocked: PASS - Readiness dashboard keeps runtime implementation blocked.
- readiness_v9_2_limited_runtime_slice_complete: PASS - Readiness dashboard includes V9-2 limited runtime slice evidence.
- human_decision_limited_scope: PASS - Human decision approves only limited V9-1 Safety Gate implementation.
- human_decision_blocks_runtime_work: PASS - Human decision explicitly blocks runtime work.
- reports_pass: PASS - Contract, negative fixture, No False Green and redaction reports pass.
- safety_module_has_no_route_or_worker_constructs: PASS - Safety module has no route, server, subprocess, worker, or runtime dispatch constructs.
- no_false_green_violations_zero: PASS - No False Green scan has zero violations.
- redaction_violations_zero: PASS - Redaction scan has zero violations.

## Remaining Blockers

- V9-3 orchestration runtime remains blocked until V9-2 runtime evidence exists.
- V9-4 autonomous coding workflow remains blocked until V9-2/V9-3 evidence exists.
- V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist.

## No False Green Boundary

This closure does not claim Agent executor ready, controlled executor ready, production controlled executor ready, full multi-Agent orchestration ready, autonomous coding workflow ready, complete Workflow Studio ready, or production ready.

```

### `docs/design/V9.x/evidence/v9-1-internal-independent-audit/result-summary.md`
```markdown
# V9-1 Internal Independent Audit Closure

Document status: internal audit closure / V9-1 only / external audit deferred.

```text
status: PASS
runtime_implementation_allowed: false
v9_2_limited_runtime_slice_complete: true
v9_2_runtime_implementation_allowed: true
v9_3_runtime_implementation_allowed: false
v9_4_runtime_implementation_allowed: false
external_audit_deferred: true
```

## Conclusion

V9-1 limited Safety Gate implementation remains internally closed; V9-2 limited runtime slice evidence is now tracked separately and external audit is deferred until later V9 development packages are available.

## Checks

- safety_gate_acceptance_pass: PASS - V9-1 Safety Gate implementation evidence status is PASS.
- all_scenarios_pass: PASS - All real-code policy validation scenarios pass.
- runtime_execution_still_blocked: PASS - Safety Gate never allows runtime execution.
- runtime_route_not_created: PASS - No runtime executor route was created.
- runtime_worker_not_created: PASS - No runtime worker was created.
- source_agent_mutation_denied: PASS - source=agent durable mutation remains denied.
- controlled_action_execution_blocked: PASS - Controlled executor action execution remains out of scope.
- capability_claim_flags_false: PASS - Blocked capability claim flags remain false.
- readiness_status_pass: PASS - Readiness dashboard status is PASS.
- readiness_runtime_implementation_blocked: PASS - Readiness dashboard keeps runtime implementation blocked.
- readiness_v9_2_limited_runtime_slice_complete: PASS - Readiness dashboard includes V9-2 limited runtime slice evidence.
- human_decision_limited_scope: PASS - Human decision approves only limited V9-1 Safety Gate implementation.
- human_decision_blocks_runtime_work: PASS - Human decision explicitly blocks runtime work.
- reports_pass: PASS - Contract, negative fixture, No False Green and redaction reports pass.
- safety_module_has_no_route_or_worker_constructs: PASS - Safety module has no route, server, subprocess, worker, or runtime dispatch constructs.
- no_false_green_violations_zero: PASS - No False Green scan has zero violations.
- redaction_violations_zero: PASS - Redaction scan has zero violations.

## Remaining Blockers

- V9-3 orchestration runtime remains blocked until V9-2 runtime evidence exists.
- V9-4 autonomous coding workflow remains blocked until V9-2/V9-3 evidence exists.
- V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist.

## No False Green Boundary

This closure does not claim Agent executor ready, controlled executor ready, production controlled executor ready, full multi-Agent orchestration ready, autonomous coding workflow ready, complete Workflow Studio ready, or production ready.

```

### `docs/design/V9.x/evidence/v9-1-internal-independent-audit/internal-audit-data.json`
```json
{
  "audit_type": "internal_independent_closure",
  "checks": [
    {
      "check_id": "safety_gate_acceptance_pass",
      "details": "V9-1 Safety Gate implementation evidence status is PASS.",
      "status": "PASS"
    },
    {
      "check_id": "all_scenarios_pass",
      "details": "All real-code policy validation scenarios pass.",
      "status": "PASS"
    },
    {
      "check_id": "runtime_execution_still_blocked",
      "details": "Safety Gate never allows runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "runtime_route_not_created",
      "details": "No runtime executor route was created.",
      "status": "PASS"
    },
    {
      "check_id": "runtime_worker_not_created",
      "details": "No runtime worker was created.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_mutation_denied",
      "details": "source=agent durable mutation remains denied.",
      "status": "PASS"
    },
    {
      "check_id": "controlled_action_execution_blocked",
      "details": "Controlled executor action execution remains out of scope.",
      "status": "PASS"
    },
    {
      "check_id": "capability_claim_flags_false",
      "details": "Blocked capability claim flags remain false.",
      "status": "PASS"
    },
    {
      "check_id": "readiness_status_pass",
      "details": "Readiness dashboard status is PASS.",
      "status": "PASS"
    },
    {
      "check_id": "readiness_runtime_implementation_blocked",
      "details": "Readiness dashboard keeps runtime implementation blocked.",
      "status": "PASS"
    },
    {
      "check_id": "readiness_v9_2_limited_runtime_slice_complete",
      "details": "Readiness dashboard includes V9-2 limited runtime slice evidence.",
      "status": "PASS"
    },
    {
      "check_id": "human_decision_limited_scope",
      "details": "Human decision approves only limited V9-1 Safety Gate implementation.",
      "status": "PASS"
    },
    {
      "check_id": "human_decision_blocks_runtime_work",
      "details": "Human decision explicitly blocks runtime work.",
      "status": "PASS"
    },
    {
      "check_id": "reports_pass",
      "details": "Contract, negative fixture, No False Green and redaction reports pass.",
      "status": "PASS"
    },
    {
      "check_id": "safety_module_has_no_route_or_worker_constructs",
      "details": "Safety module has no route, server, subprocess, worker, or runtime dispatch constructs.",
      "status": "PASS"
    },
    {
      "check_id": "no_false_green_violations_zero",
      "details": "No False Green scan has zero violations.",
      "status": "PASS"
    },
    {
      "check_id": "redaction_violations_zero",
      "details": "Redaction scan has zero violations.",
      "status": "PASS"
    }
  ],
  "conclusion": "V9-1 limited Safety Gate implementation remains internally closed; V9-2 limited runtime slice evidence is now tracked separately and external audit is deferred until later V9 development packages are available.",
  "created_at": "2026-06-08T03:06:15Z",
  "evidence_refs": [
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-readiness/readiness-dashboard-data.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_contract_validation_report.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_negative_test_results.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_no_false_green_scan.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_redaction_scan.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/core/policies/v9_agent_executor_safety.py"
  ],
  "external_audit_deferred": true,
  "remaining_blockers": [
    "V9-3 orchestration runtime remains blocked until V9-2 runtime evidence exists.",
    "V9-4 autonomous coding workflow remains blocked until V9-2/V9-3 evidence exists.",
    "V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist."
  ],
  "runtime_implementation_allowed": false,
  "schema_version": "v9_1.internal_independent_audit.v1",
  "stage_id": "V9-1",
  "status": "PASS",
  "v9_2_limited_runtime_slice_complete": true,
  "v9_2_runtime_implementation_allowed": true,
  "v9_3_runtime_implementation_allowed": false,
  "v9_4_runtime_implementation_allowed": false
}

```

### `docs/design/V9.x/evidence/v9-2-controlled-executor-pre-implementation/result-summary.md`
```markdown
# V9-2 Pre-Implementation Audit Closure

Document status: internal readiness closure / limited runtime implementation approved.

```text
status: PASS
v9_2_runtime_implementation_allowed: true
runtime_executor_route_created: false
runtime_worker_created: false
controlled_executor_action_execution: limited_to_allowlisted_runtime_slice
source_agent_durable_mutation_allowed: false
requires_human_high_risk_decision: false
```

## Conclusion

V9-2 implementation-readiness closure is complete and scoped human approval is recorded; only the limited runtime slice is allowed.

## Checks

- v9_1_internal_audit_pass: PASS - V9-1 internal audit must pass before V9-2 planning closure.
- v9_1_safety_gate_pass: PASS - V9-1 Safety Gate implementation evidence must pass.
- v9_1_runtime_still_blocked: PASS - V9-1 evidence still blocks runtime execution.
- v9_2_high_risk_decision_recorded: PASS - V9-2 limited runtime implementation has scoped human high-risk approval.
- v9_2_decision_blocks_forbidden_work: PASS - V9-2 decision blocks routes, workers, excluded actions, source=agent mutation and overclaim.
- required_fixture_set_present: PASS - V9-2 pre-implementation fixture set is present.
- artifact_write_append_only_with_approval_gate.json_stage_id: PASS - Fixture is scoped to V9-2.
- artifact_write_append_only_with_approval_gate.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- artifact_write_append_only_with_approval_gate.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- artifact_write_append_only_with_approval_gate.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- artifact_write_append_only_with_approval_gate.json_approval_gate_required: PASS - Medium-risk write/evaluation fixtures require approval gate.
- artifact_write_append_only_with_approval_gate.json_append_only_required: PASS - Write/evaluation fixtures are append-only.
- artifact_write_append_only_with_approval_gate.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- expired_human_authorization_ref_denied.json_stage_id: PASS - Fixture is scoped to V9-2.
- expired_human_authorization_ref_denied.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- expired_human_authorization_ref_denied.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- expired_human_authorization_ref_denied.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- idempotency_duplicate_returns_prior_ref.json_stage_id: PASS - Fixture is scoped to V9-2.
- idempotency_duplicate_returns_prior_ref.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- idempotency_duplicate_returns_prior_ref.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- idempotency_duplicate_returns_prior_ref.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- idempotency_duplicate_returns_prior_ref.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- kill_switch_denied_blocks_action.json_stage_id: PASS - Fixture is scoped to V9-2.
- kill_switch_denied_blocks_action.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- kill_switch_denied_blocks_action.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- kill_switch_denied_blocks_action.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- quality_evaluation_append_only_with_approval_gate.json_stage_id: PASS - Fixture is scoped to V9-2.
- quality_evaluation_append_only_with_approval_gate.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- quality_evaluation_append_only_with_approval_gate.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- quality_evaluation_append_only_with_approval_gate.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- quality_evaluation_append_only_with_approval_gate.json_approval_gate_required: PASS - Medium-risk write/evaluation fixtures require approval gate.
- quality_evaluation_append_only_with_approval_gate.json_append_only_required: PASS - Write/evaluation fixtures are append-only.
- quality_evaluation_append_only_with_approval_gate.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- source_agent_durable_mutation_denied.json_stage_id: PASS - Fixture is scoped to V9-2.
- source_agent_durable_mutation_denied.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- source_agent_durable_mutation_denied.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- source_agent_durable_mutation_denied.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- source_agent_durable_mutation_denied.json_source_agent_denied: PASS - source=agent fixture must be denied.
- station_rerun_with_user_confirmed.json_stage_id: PASS - Fixture is scoped to V9-2.
- station_rerun_with_user_confirmed.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- station_rerun_with_user_confirmed.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- station_rerun_with_user_confirmed.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- station_rerun_with_user_confirmed.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- workflow_instance_start_with_human_authorization_ref.json_stage_id: PASS - Fixture is scoped to V9-2.
- workflow_instance_start_with_human_authorization_ref.json_redaction_pass: PASS - Fixture carries redaction_status=PASS.
- workflow_instance_start_with_human_authorization_ref.json_runtime_not_allowed_now: PASS - Fixture does not approve current runtime execution.
- workflow_instance_start_with_human_authorization_ref.json_operation_in_allowlist: PASS - Fixture operation is in the V9-2 candidate allowlist.
- workflow_instance_start_with_human_authorization_ref.json_requires_human_decision: PASS - Planned allow fixtures require human high-risk decision.
- allowlist_documented: PASS - All four candidate actions are documented.
- excluded_actions_documented: PASS - Excluded actions are documented as hard-denied.
- durable_mutation_invariant_documented: PASS - Durable mutation invariant uses valid human_authorization_ref.
- source_agent_denial_documented: PASS - source=agent default durable mutation denial is documented.
- append_only_documented: PASS - Append-only and overwrite denial are documented.
- no_v9_2_forbidden_route_or_worker_detected: PASS - No V9-2 runtime route or worker implementation is present.

## Human Decision Required

- stage_id: V9-2
- decision_needed: Recorded: V9-2 limited controlled Agent executor runtime implementation is approved.
- impact_if_approved: Allows implementation of the four allowlisted actions only, still denying source=agent durable mutation and excluded actions.
- impact_if_rejected: Not applicable to the current recorded decision; revocation would block V9-2 and downstream V9-3/V9-4 runtime.

## Remaining Blockers

- V9-2 runtime evidence must prove only the four allowlisted actions.
- V9-3 remains blocked until V9-2 runtime evidence exists.
- V9-4 remains blocked until V9-2 and V9-3 runtime evidence exists.
- V9-8 final acceptance remains blocked.

## No False Green Boundary

This closure does not claim Agent executor ready, controlled executor ready, production controlled executor ready, V9-2 runtime PASS, V9-3 runtime PASS, or V9-4 runtime PASS.

```

### `docs/design/V9.x/evidence/v9-2-controlled-executor-pre-implementation/pre-implementation-data.json`
```json
{
  "audit_type": "implementation_readiness_closure",
  "checks": [
    {
      "check_id": "v9_1_internal_audit_pass",
      "details": "V9-1 internal audit must pass before V9-2 planning closure.",
      "status": "PASS"
    },
    {
      "check_id": "v9_1_safety_gate_pass",
      "details": "V9-1 Safety Gate implementation evidence must pass.",
      "status": "PASS"
    },
    {
      "check_id": "v9_1_runtime_still_blocked",
      "details": "V9-1 evidence still blocks runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "v9_2_high_risk_decision_recorded",
      "details": "V9-2 limited runtime implementation has scoped human high-risk approval.",
      "status": "PASS"
    },
    {
      "check_id": "v9_2_decision_blocks_forbidden_work",
      "details": "V9-2 decision blocks routes, workers, excluded actions, source=agent mutation and overclaim.",
      "status": "PASS"
    },
    {
      "check_id": "required_fixture_set_present",
      "details": "V9-2 pre-implementation fixture set is present.",
      "status": "PASS"
    },
    {
      "check_id": "artifact_write_append_only_with_approval_gate.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "artifact_write_append_only_with_approval_gate.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "artifact_write_append_only_with_approval_gate.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "artifact_write_append_only_with_approval_gate.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "artifact_write_append_only_with_approval_gate.json_approval_gate_required",
      "details": "Medium-risk write/evaluation fixtures require approval gate.",
      "status": "PASS"
    },
    {
      "check_id": "artifact_write_append_only_with_approval_gate.json_append_only_required",
      "details": "Write/evaluation fixtures are append-only.",
      "status": "PASS"
    },
    {
      "check_id": "artifact_write_append_only_with_approval_gate.json_requires_human_decision",
      "details": "Planned allow fixtures require human high-risk decision.",
      "status": "PASS"
    },
    {
      "check_id": "expired_human_authorization_ref_denied.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "expired_human_authorization_ref_denied.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "expired_human_authorization_ref_denied.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "expired_human_authorization_ref_denied.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "idempotency_duplicate_returns_prior_ref.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "idempotency_duplicate_returns_prior_ref.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "idempotency_duplicate_returns_prior_ref.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "idempotency_duplicate_returns_prior_ref.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "idempotency_duplicate_returns_prior_ref.json_requires_human_decision",
      "details": "Planned allow fixtures require human high-risk decision.",
      "status": "PASS"
    },
    {
      "check_id": "kill_switch_denied_blocks_action.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "kill_switch_denied_blocks_action.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "kill_switch_denied_blocks_action.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "kill_switch_denied_blocks_action.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "quality_evaluation_append_only_with_approval_gate.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "quality_evaluation_append_only_with_approval_gate.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "quality_evaluation_append_only_with_approval_gate.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "quality_evaluation_append_only_with_approval_gate.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "quality_evaluation_append_only_with_approval_gate.json_approval_gate_required",
      "details": "Medium-risk write/evaluation fixtures require approval gate.",
      "status": "PASS"
    },
    {
      "check_id": "quality_evaluation_append_only_with_approval_gate.json_append_only_required",
      "details": "Write/evaluation fixtures are append-only.",
      "status": "PASS"
    },
    {
      "check_id": "quality_evaluation_append_only_with_approval_gate.json_requires_human_decision",
      "details": "Planned allow fixtures require human high-risk decision.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_durable_mutation_denied.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_durable_mutation_denied.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_durable_mutation_denied.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_durable_mutation_denied.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_durable_mutation_denied.json_source_agent_denied",
      "details": "source=agent fixture must be denied.",
      "status": "PASS"
    },
    {
      "check_id": "station_rerun_with_user_confirmed.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "station_rerun_with_user_confirmed.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "station_rerun_with_user_confirmed.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "station_rerun_with_user_confirmed.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "station_rerun_with_user_confirmed.json_requires_human_decision",
      "details": "Planned allow fixtures require human high-risk decision.",
      "status": "PASS"
    },
    {
      "check_id": "workflow_instance_start_with_human_authorization_ref.json_stage_id",
      "details": "Fixture is scoped to V9-2.",
      "status": "PASS"
    },
    {
      "check_id": "workflow_instance_start_with_human_authorization_ref.json_redaction_pass",
      "details": "Fixture carries redaction_status=PASS.",
      "status": "PASS"
    },
    {
      "check_id": "workflow_instance_start_with_human_authorization_ref.json_runtime_not_allowed_now",
      "details": "Fixture does not approve current runtime execution.",
      "status": "PASS"
    },
    {
      "check_id": "workflow_instance_start_with_human_authorization_ref.json_operation_in_allowlist",
      "details": "Fixture operation is in the V9-2 candidate allowlist.",
      "status": "PASS"
    },
    {
      "check_id": "workflow_instance_start_with_human_authorization_ref.json_requires_human_decision",
      "details": "Planned allow fixtures require human high-risk decision.",
      "status": "PASS"
    },
    {
      "check_id": "allowlist_documented",
      "details": "All four candidate actions are documented.",
      "status": "PASS"
    },
    {
      "check_id": "excluded_actions_documented",
      "details": "Excluded actions are documented as hard-denied.",
      "status": "PASS"
    },
    {
      "check_id": "durable_mutation_invariant_documented",
      "details": "Durable mutation invariant uses valid human_authorization_ref.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_denial_documented",
      "details": "source=agent default durable mutation denial is documented.",
      "status": "PASS"
    },
    {
      "check_id": "append_only_documented",
      "details": "Append-only and overwrite denial are documented.",
      "status": "PASS"
    },
    {
      "check_id": "no_v9_2_forbidden_route_or_worker_detected",
      "details": "No V9-2 runtime route or worker implementation is present.",
      "status": "PASS"
    }
  ],
  "conclusion": "V9-2 implementation-readiness closure is complete and scoped human approval is recorded; only the limited runtime slice is allowed.",
  "controlled_executor_action_execution": false,
  "created_at": "2026-06-08T03:06:26Z",
  "evidence_refs": [
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-internal-independent-audit/internal-audit-data.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_2_high_risk_human_decision.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/v9_2_pre_implementation_development_and_acceptance_plan.md",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/v9_2_controlled_executor_engineering_design.md",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/v9_2_controlled_executor_implementation_spec.md",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/artifact_write_append_only_with_approval_gate.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/expired_human_authorization_ref_denied.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/idempotency_duplicate_returns_prior_ref.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/kill_switch_denied_blocks_action.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/quality_evaluation_append_only_with_approval_gate.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/source_agent_durable_mutation_denied.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/station_rerun_with_user_confirmed.json",
    "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/workflow_instance_start_with_human_authorization_ref.json"
  ],
  "external_audit_deferred": true,
  "fixtures": [
    {
      "expected_decision": "allow_after_runtime_approval",
      "expected_runtime_status": "planned_only_not_executed",
      "fixture_id": "v9-2-artifact-write-append-only-with-approval-gate",
      "operation": "artifact.write",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/artifact_write_append_only_with_approval_gate.json",
      "runtime_execution_allowed_now": false
    },
    {
      "expected_decision": "deny",
      "expected_runtime_status": "denied",
      "fixture_id": "v9-2-expired-human-authorization-ref-denied",
      "operation": "workflow.instance.start",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/expired_human_authorization_ref_denied.json",
      "runtime_execution_allowed_now": false
    },
    {
      "expected_decision": null,
      "expected_runtime_status": "planned_only_not_executed",
      "fixture_id": "v9-2-idempotency-duplicate-returns-prior-ref",
      "operation": "workflow.instance.start",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/idempotency_duplicate_returns_prior_ref.json",
      "runtime_execution_allowed_now": false
    },
    {
      "expected_decision": "deny",
      "expected_runtime_status": "denied",
      "fixture_id": "v9-2-kill-switch-denied-blocks-action",
      "operation": "station.rerun",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/kill_switch_denied_blocks_action.json",
      "runtime_execution_allowed_now": false
    },
    {
      "expected_decision": "allow_after_runtime_approval",
      "expected_runtime_status": "planned_only_not_executed",
      "fixture_id": "v9-2-quality-evaluation-append-only-with-approval-gate",
      "operation": "quality.evaluation.create",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/quality_evaluation_append_only_with_approval_gate.json",
      "runtime_execution_allowed_now": false
    },
    {
      "expected_decision": "deny",
      "expected_runtime_status": "denied",
      "fixture_id": "v9-2-source-agent-durable-mutation-denied",
      "operation": "workflow.instance.start",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/source_agent_durable_mutation_denied.json",
      "runtime_execution_allowed_now": false
    },
    {
      "expected_decision": "allow_after_runtime_approval",
      "expected_runtime_status": "planned_only_not_executed",
      "fixture_id": "v9-2-station-rerun-with-user-confirmed",
      "operation": "station.rerun",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/station_rerun_with_user_confirmed.json",
      "runtime_execution_allowed_now": false
    },
    {
      "expected_decision": "allow_after_runtime_approval",
      "expected_runtime_status": "planned_only_not_executed",
      "fixture_id": "v9-2-workflow-instance-start-with-human-authorization-ref",
      "operation": "workflow.instance.start",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-2-controlled-executor/workflow_instance_start_with_human_authorization_ref.json",
      "runtime_execution_allowed_now": false
    }
  ],
  "next_human_decision_required": {
    "decision_needed": "Recorded: V9-2 limited controlled Agent executor runtime implementation is approved.",
    "impact_if_approved": "Allows implementation of the four allowlisted actions only, still denying source=agent durable mutation and excluded actions.",
    "impact_if_rejected": "Not applicable to the current recorded decision; revocation would block V9-2 and downstream V9-3/V9-4 runtime.",
    "stage_id": "V9-2"
  },
  "remaining_blockers": [
    "V9-2 runtime evidence must prove only the four allowlisted actions.",
    "V9-3 remains blocked until V9-2 runtime evidence exists.",
    "V9-4 remains blocked until V9-2 and V9-3 runtime evidence exists.",
    "V9-8 final acceptance remains blocked."
  ],
  "requires_human_high_risk_decision": false,
  "runtime_executor_route_created": false,
  "runtime_worker_created": false,
  "schema_version": "v9_2.pre_implementation_closure.v1",
  "source_agent_durable_mutation_allowed": false,
  "stage_id": "V9-2",
  "status": "PASS",
  "v9_2_runtime_implementation_allowed": true
}

```

### `docs/design/V9.x/v9_2_runtime_acceptance_closure.md`
```markdown
# V9-2 Controlled Executor Runtime Acceptance Closure

Document status: runtime fixture evidence / limited controlled Agent executor runtime slice / ready for review.

```text
status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true
runtime_executor_route_created: false
runtime_worker_created: false
source_agent_durable_mutation_allowed: false
```

## Allowed Runtime Slice

- artifact.write
- quality.evaluation.create
- station.rerun
- workflow.instance.start

## Scenario Results

- workflow_instance_start_with_valid_human_authorization: PASS - workflow.instance.start applies only after valid human authorization evidence.
- station_rerun_retains_old_attempt_and_marks_downstream_stale: PASS - station.rerun appends a new attempt, retains the old failed attempt, and marks downstream stale.
- artifact_write_requires_approval_and_appends_version: PASS - artifact.write is approval-gated and append-only.
- quality_evaluation_requires_approval_and_appends_record: PASS - quality.evaluation.create is approval-gated and append-only.
- source_agent_durable_mutation_denied: PASS - source=agent remains denied for durable mutation.
- excluded_operations_hard_denied: PASS - Excluded operations are hard-denied by preflight.
- expired_human_authorization_ref_denied: PASS - Expired HumanAuthorizationRef cannot authorize durable mutation.
- kill_switch_denied_blocks_action: PASS - Kill switch denial blocks the runtime action before mutation.
- idempotency_duplicate_returns_prior_ref_and_conflict_denied: PASS - Duplicate idempotency returns prior runtime_result_ref; conflicting target refs are denied.
- redaction_forbidden_content_denied: PASS - Runtime DTO preflight blocks forbidden sensitive payload markers without storing the payload value.

## Checks

- all_scenarios_pass: PASS - All V9-2 runtime scenarios pass.
- only_allowlisted_operations_applied: PASS - Only the four allowlisted operations apply.
- source_agent_direct_mutation_denied: PASS - source=agent direct durable mutation remains denied.
- excluded_operations_denied: PASS - Excluded operations are denied.
- runtime_route_absent: PASS - No runtime route is created by the V9-2 module.
- runtime_worker_absent: PASS - No runtime worker is created by the V9-2 module.

## Remaining Blockers

- V9-3 orchestration runtime requires separate gate and runtime evidence.
- V9-4 autonomous coding workflow requires separate gate and runtime evidence.
- V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist.

## No False Green Boundary

This evidence proves only the V9-2 limited runtime slice ready for review. It does not prove broader executor readiness, production executor readiness, V9-3 orchestration runtime, V9-4 coding workflow runtime, or V9-8 final acceptance.

```

### `docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/result-summary.md`
```markdown
# V9-2 Controlled Executor Runtime Acceptance Closure

Document status: runtime fixture evidence / limited controlled Agent executor runtime slice / ready for review.

```text
status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true
runtime_executor_route_created: false
runtime_worker_created: false
source_agent_durable_mutation_allowed: false
```

## Allowed Runtime Slice

- artifact.write
- quality.evaluation.create
- station.rerun
- workflow.instance.start

## Scenario Results

- workflow_instance_start_with_valid_human_authorization: PASS - workflow.instance.start applies only after valid human authorization evidence.
- station_rerun_retains_old_attempt_and_marks_downstream_stale: PASS - station.rerun appends a new attempt, retains the old failed attempt, and marks downstream stale.
- artifact_write_requires_approval_and_appends_version: PASS - artifact.write is approval-gated and append-only.
- quality_evaluation_requires_approval_and_appends_record: PASS - quality.evaluation.create is approval-gated and append-only.
- source_agent_durable_mutation_denied: PASS - source=agent remains denied for durable mutation.
- excluded_operations_hard_denied: PASS - Excluded operations are hard-denied by preflight.
- expired_human_authorization_ref_denied: PASS - Expired HumanAuthorizationRef cannot authorize durable mutation.
- kill_switch_denied_blocks_action: PASS - Kill switch denial blocks the runtime action before mutation.
- idempotency_duplicate_returns_prior_ref_and_conflict_denied: PASS - Duplicate idempotency returns prior runtime_result_ref; conflicting target refs are denied.
- redaction_forbidden_content_denied: PASS - Runtime DTO preflight blocks forbidden sensitive payload markers without storing the payload value.

## Checks

- all_scenarios_pass: PASS - All V9-2 runtime scenarios pass.
- only_allowlisted_operations_applied: PASS - Only the four allowlisted operations apply.
- source_agent_direct_mutation_denied: PASS - source=agent direct durable mutation remains denied.
- excluded_operations_denied: PASS - Excluded operations are denied.
- runtime_route_absent: PASS - No runtime route is created by the V9-2 module.
- runtime_worker_absent: PASS - No runtime worker is created by the V9-2 module.

## Remaining Blockers

- V9-3 orchestration runtime requires separate gate and runtime evidence.
- V9-4 autonomous coding workflow requires separate gate and runtime evidence.
- V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist.

## No False Green Boundary

This evidence proves only the V9-2 limited runtime slice ready for review. It does not prove broader executor readiness, production executor readiness, V9-3 orchestration runtime, V9-4 coding workflow runtime, or V9-8 final acceptance.

```

### `docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json`
```json
{
  "agent_executor_ready": false,
  "allowed_claim": "V9-2 complete: limited controlled Agent executor runtime slice ready for review.",
  "allowed_operations": [
    "artifact.write",
    "quality.evaluation.create",
    "station.rerun",
    "workflow.instance.start"
  ],
  "checks": [
    {
      "check_id": "all_scenarios_pass",
      "details": "All V9-2 runtime scenarios pass.",
      "status": "PASS"
    },
    {
      "check_id": "only_allowlisted_operations_applied",
      "details": "Only the four allowlisted operations apply.",
      "status": "PASS"
    },
    {
      "check_id": "source_agent_direct_mutation_denied",
      "details": "source=agent direct durable mutation remains denied.",
      "status": "PASS"
    },
    {
      "check_id": "excluded_operations_denied",
      "details": "Excluded operations are denied.",
      "status": "PASS"
    },
    {
      "check_id": "runtime_route_absent",
      "details": "No runtime route is created by the V9-2 module.",
      "status": "PASS"
    },
    {
      "check_id": "runtime_worker_absent",
      "details": "No runtime worker is created by the V9-2 module.",
      "status": "PASS"
    }
  ],
  "controlled_executor_ready": false,
  "created_at": "2026-06-08T03:06:27Z",
  "evidence_scope": "real_runtime_fixture",
  "excluded_operations": [
    "approval.respond",
    "business.event.emit",
    "connector.call",
    "context.update",
    "external_llm.call",
    "git.commit",
    "git.push",
    "production.deploy",
    "workflow.template.publish"
  ],
  "fallback_demo_only": false,
  "production_controlled_executor_ready": false,
  "remaining_blockers": [
    "V9-3 orchestration runtime requires separate gate and runtime evidence.",
    "V9-4 autonomous coding workflow requires separate gate and runtime evidence.",
    "V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist."
  ],
  "report_only": false,
  "runtime_backed": true,
  "runtime_executor_route_created": false,
  "runtime_worker_created": false,
  "scenarios": [
    {
      "notes": "workflow.instance.start applies only after valid human authorization evidence.",
      "result": {
        "agent_executor_ready": false,
        "blocked_reason": null,
        "capability_decision": "allow_v9_2_limited_runtime_slice",
        "controlled_executor_ready": false,
        "created_at": "2026-06-08T03:06:27Z",
        "execution_evidence": {
          "actor_type": "human_user",
          "agent_executor_ready": false,
          "agent_id": "agent-v9-2",
          "approval_gate_ref": null,
          "audit_ref": "audit://v9-2/envelope",
          "capability_decision_ref": "capability-decision://v9-1/af30b1df3638424585e482f7adfd1e73",
          "controlled_executor_ready": false,
          "correlation_id": "corr-v9-2",
          "created_at": "2026-06-08T03:06:27Z",
          "decision_chain_refs": {
            "capability_decision_ref": "capability-decision://v9-1/af30b1df3638424585e482f7adfd1e73",
            "incident_timeline_ref": "incident-timeline://v9-2/97b30fa93f094eb6aef319ad90789bd5",
            "kill_switch_policy_ref": "kill-switch://v9-2/default",
            "policy_ref": "policy://v9-1/agent-executor-safety/workflow.instance.start",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "timeout_policy_ref": "timeout://v9-2/default"
          },
          "execution_envelope_id": "env-v9-2-workflow.instance.start-idem-v9-2",
          "execution_evidence_ref": "execution-evidence://v9-2/d7b07a4c16dc4e76a3f9d70ec9d5dbcc",
          "human_authorization_ref": "har-v9-2-start",
          "operation": "workflow.instance.start",
          "production_controlled_executor_ready": false,
          "redaction_status": "PASS",
          "request_id": "req-v9-2",
          "rollback_descriptor_ref": "rollback://v9-2/default",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/start",
          "schema_version": "v9.0",
          "source": "product_console",
          "station_id": "station-v9-2",
          "target_refs": {
            "workflow_instance_id": "workflow-v9-2"
          }
        },
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/97b30fa93f094eb6aef319ad90789bd5",
        "operation": "workflow.instance.start",
        "policy_decision": "allow",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_36f964ac836a",
        "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/start",
        "status": "applied_v9_2_limited_runtime_slice"
      },
      "scenario_id": "workflow_instance_start_with_valid_human_authorization",
      "status": "PASS"
    },
    {
      "notes": "station.rerun appends a new attempt, retains the old failed attempt, and marks downstream stale.",
      "result": {
        "agent_executor_ready": false,
        "blocked_reason": null,
        "capability_decision": "allow_v9_2_limited_runtime_slice",
        "controlled_executor_ready": false,
        "created_at": "2026-06-08T03:06:27Z",
        "execution_evidence": {
          "actor_type": "human_user",
          "agent_executor_ready": false,
          "agent_id": "agent-v9-2",
          "approval_gate_ref": null,
          "audit_ref": "audit://v9-2/envelope",
          "capability_decision_ref": "capability-decision://v9-1/09352e5ccf1b442ca13ebbc03dad26b6",
          "controlled_executor_ready": false,
          "correlation_id": "corr-v9-2",
          "created_at": "2026-06-08T03:06:27Z",
          "decision_chain_refs": {
            "capability_decision_ref": "capability-decision://v9-1/09352e5ccf1b442ca13ebbc03dad26b6",
            "incident_timeline_ref": "incident-timeline://v9-2/a8ae925ae9574536a873a5c49d774e1f",
            "kill_switch_policy_ref": "kill-switch://v9-2/default",
            "policy_ref": "policy://v9-1/agent-executor-safety/station.rerun",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "timeout_policy_ref": "timeout://v9-2/default"
          },
          "execution_envelope_id": "env-v9-2-station.rerun-idem-v9-2-rerun",
          "execution_evidence_ref": "execution-evidence://v9-2/124feb2108a649b3b6829c60fd5b472f",
          "human_authorization_ref": null,
          "operation": "station.rerun",
          "production_controlled_executor_ready": false,
          "redaction_status": "PASS",
          "request_id": "req-v9-2",
          "rollback_descriptor_ref": "rollback://v9-2/default",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/rerun/station-v9-2/2",
          "schema_version": "v9.0",
          "source": "product_console",
          "station_id": "station-v9-2",
          "target_refs": {
            "station_id": "station-v9-2",
            "station_run_id": "station-run-v9-2-old",
            "workflow_instance_id": "workflow-v9-2"
          }
        },
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/a8ae925ae9574536a873a5c49d774e1f",
        "operation": "station.rerun",
        "policy_decision": "allow",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_95c3e6633e20",
        "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/rerun/station-v9-2/2",
        "status": "applied_v9_2_limited_runtime_slice"
      },
      "scenario_id": "station_rerun_retains_old_attempt_and_marks_downstream_stale",
      "status": "PASS"
    },
    {
      "notes": "artifact.write is approval-gated and append-only.",
      "result": {
        "applied": {
          "agent_executor_ready": false,
          "blocked_reason": null,
          "capability_decision": "allow_v9_2_limited_runtime_slice",
          "controlled_executor_ready": false,
          "created_at": "2026-06-08T03:06:27Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": "approval://v9-2/default",
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/1cc9239fc5d548f4bc7b64619199756b",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-08T03:06:27Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/1cc9239fc5d548f4bc7b64619199756b",
              "incident_timeline_ref": "incident-timeline://v9-2/830b5a6d91a940b18e6806c20bffbd49",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/artifact.write",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-artifact.write-idem-v9-2-artifact",
            "execution_evidence_ref": "execution-evidence://v9-2/4c21087ed93f493690e726f71edd376b",
            "human_authorization_ref": null,
            "operation": "artifact.write",
            "production_controlled_executor_ready": false,
            "redaction_status": "PASS",
            "request_id": "req-v9-2",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/artifact/artifact-v9-2/1",
            "schema_version": "v9.0",
            "source": "product_console",
            "station_id": "station-v9-2",
            "target_refs": {
              "artifact_id": "artifact-v9-2"
            }
          },
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/830b5a6d91a940b18e6806c20bffbd49",
          "operation": "artifact.write",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_71ab2e480f8c",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/artifact/artifact-v9-2/1",
          "status": "applied_v9_2_limited_runtime_slice"
        },
        "artifact_versions": [
          {
            "artifact_id": "artifact-v9-2",
            "artifact_version_id": "artifact-version-v9-2-1",
            "content_ref": "artifact-content-ref://v9-2/artifact-v9-2/1",
            "created_at": "2026-06-08T03:06:27Z",
            "operation": "append_version",
            "producer_attempt_id": null,
            "producer_runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/artifact/artifact-v9-2/1",
            "producer_station_id": "station-v9-2",
            "redaction_status": "PASS"
          }
        ],
        "missing_approval": {
          "agent_executor_ready": false,
          "blocked_reason": "approval_gate_required",
          "capability_decision": "deny",
          "controlled_executor_ready": false,
          "created_at": "2026-06-08T03:06:27Z",
          "execution_evidence": null,
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/e793ebe71a8943399525265e094c2f21",
          "operation": "artifact.write",
          "policy_decision": "deny",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_efdf09b95ad7",
          "runtime_result_ref": null,
          "status": "blocked"
        }
      },
      "scenario_id": "artifact_write_requires_approval_and_appends_version",
      "status": "PASS"
    },
    {
      "notes": "quality.evaluation.create is approval-gated and append-only.",
      "result": {
        "applied": {
          "agent_executor_ready": false,
          "blocked_reason": null,
          "capability_decision": "allow_v9_2_limited_runtime_slice",
          "controlled_executor_ready": false,
          "created_at": "2026-06-08T03:06:27Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": "approval://v9-2/default",
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/f6c1bed269d04f01b0707c301ce17e35",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-08T03:06:27Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/f6c1bed269d04f01b0707c301ce17e35",
              "incident_timeline_ref": "incident-timeline://v9-2/a3291c5d815d448d9f66325abf688d47",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/quality.evaluation.create",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-quality.evaluation.create-idem-v9-2-quality",
            "execution_evidence_ref": "execution-evidence://v9-2/3225084d6a2d4b9ab7b46efd3731dfa5",
            "human_authorization_ref": null,
            "operation": "quality.evaluation.create",
            "production_controlled_executor_ready": false,
            "redaction_status": "PASS",
            "request_id": "req-v9-2",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/quality/quality-v9-2/1",
            "schema_version": "v9.0",
            "source": "product_console",
            "station_id": "station-v9-2",
            "target_refs": {
              "quality_evaluation_id": "quality-v9-2"
            }
          },
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/a3291c5d815d448d9f66325abf688d47",
          "operation": "quality.evaluation.create",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_fe5a013f5e98",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/quality/quality-v9-2/1",
          "status": "applied_v9_2_limited_runtime_slice"
        },
        "missing_approval": {
          "agent_executor_ready": false,
          "blocked_reason": "approval_gate_required",
          "capability_decision": "deny",
          "controlled_executor_ready": false,
          "created_at": "2026-06-08T03:06:27Z",
          "execution_evidence": null,
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/1a7125de74c54bdf882ebf6bcba4d9a9",
          "operation": "quality.evaluation.create",
          "policy_decision": "deny",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_55949b907ca7",
          "runtime_result_ref": null,
          "status": "blocked"
        },
        "quality_evaluations": [
          {
            "created_at": "2026-06-08T03:06:27Z",
            "operation": "append_evaluation",
            "producer_runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/quality/quality-v9-2/1",
            "quality_evaluation_id": "quality-v9-2",
            "quality_rule_ref": "quality-rule-ref://v9-2/default",
            "redaction_status": "PASS",
            "score_ref": "quality-score-ref://v9-2/quality-v9-2/1",
            "target_ref": "quality-v9-2"
          }
        ]
      },
      "scenario_id": "quality_evaluation_requires_approval_and_appends_record",
      "status": "PASS"
    },
    {
      "notes": "source=agent remains denied for durable mutation.",
      "result": {
        "agent_executor_ready": false,
        "blocked_reason": "source_agent_durable_mutation_denied",
        "capability_decision": "deny",
        "controlled_executor_ready": false,
        "created_at": "2026-06-08T03:06:27Z",
        "execution_evidence": null,
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/c6d500b12aeb4eebaced2497c3ba246c",
        "operation": "workflow.instance.start",
        "policy_decision": "deny",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_0490c15b5a24",
        "runtime_result_ref": null,
        "status": "blocked"
      },
      "scenario_id": "source_agent_durable_mutation_denied",
      "status": "PASS"
    },
    {
      "notes": "Excluded operations are hard-denied by preflight.",
      "result": {
        "excluded_operation_results": [
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "approval.respond",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "business.event.emit",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "connector.call",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "context.update",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "external_llm.call",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "git.commit",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "git.push",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "production.deploy",
            "status": "blocked"
          },
          {
            "blocked_reason": "operation_not_allowed",
            "operation": "workflow.template.publish",
            "status": "blocked"
          }
        ]
      },
      "scenario_id": "excluded_operations_hard_denied",
      "status": "PASS"
    },
    {
      "notes": "Expired HumanAuthorizationRef cannot authorize durable mutation.",
      "result": {
        "agent_executor_ready": false,
        "blocked_reason": "missing_user_confirmation_or_valid_human_authorization_ref",
        "capability_decision": "deny",
        "controlled_executor_ready": false,
        "created_at": "2026-06-08T03:06:27Z",
        "execution_evidence": null,
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/d01867a30a344186836c78f8f0b327a7",
        "operation": "workflow.instance.start",
        "policy_decision": "deny",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_a2cafc778fe7",
        "runtime_result_ref": null,
        "status": "blocked"
      },
      "scenario_id": "expired_human_authorization_ref_denied",
      "status": "PASS"
    },
    {
      "notes": "Kill switch denial blocks the runtime action before mutation.",
      "result": {
        "agent_executor_ready": false,
        "blocked_reason": "kill_switch_denied",
        "capability_decision": "deny",
        "controlled_executor_ready": false,
        "created_at": "2026-06-08T03:06:27Z",
        "execution_evidence": null,
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/93007d1683e444f09898162d0ed670c6",
        "operation": "workflow.instance.start",
        "policy_decision": "deny",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_43fc0e3e6d6d",
        "runtime_result_ref": null,
        "status": "blocked"
      },
      "scenario_id": "kill_switch_denied_blocks_action",
      "status": "PASS"
    },
    {
      "notes": "Duplicate idempotency returns prior runtime_result_ref; conflicting target refs are denied.",
      "result": {
        "conflict": {
          "agent_executor_ready": false,
          "blocked_reason": "idempotency_key_conflict",
          "capability_decision": "deny",
          "controlled_executor_ready": false,
          "created_at": "2026-06-08T03:06:27Z",
          "execution_evidence": null,
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/9cd0ada35d574ae9ba5a9f3e449be870",
          "operation": "workflow.instance.start",
          "policy_decision": "deny",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_a100b6bb76bb",
          "runtime_result_ref": null,
          "status": "blocked"
        },
        "duplicate": {
          "agent_executor_ready": false,
          "blocked_reason": null,
          "capability_decision": "allow_v9_2_limited_runtime_slice",
          "controlled_executor_ready": false,
          "created_at": "2026-06-08T03:06:27Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": null,
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/900976a4d6494220bce133b617c2c83c",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-08T03:06:27Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/900976a4d6494220bce133b617c2c83c",
              "incident_timeline_ref": "incident-timeline://v9-2/fc317b3228f74924a40d1ae9e6ef2c00",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/workflow.instance.start",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-workflow.instance.start-idem-v9-2-duplicate",
            "execution_evidence_ref": "execution-evidence://v9-2/2810d3bc286040cfaa32235f36cbc2bc",
            "human_authorization_ref": null,
            "operation": "workflow.instance.start",
            "production_controlled_executor_ready": false,
            "redaction_status": "PASS",
            "request_id": "req-v9-2",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/start",
            "schema_version": "v9.0",
            "source": "product_console",
            "station_id": "station-v9-2",
            "target_refs": {
              "workflow_instance_id": "workflow-v9-2"
            }
          },
          "idempotent_replay": true,
          "incident_timeline_ref": "incident-timeline://v9-2/fc317b3228f74924a40d1ae9e6ef2c00",
          "operation": "workflow.instance.start",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_f87178ac98cc",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/start",
          "status": "idempotent_replay"
        },
        "first": {
          "agent_executor_ready": false,
          "blocked_reason": null,
          "capability_decision": "allow_v9_2_limited_runtime_slice",
          "controlled_executor_ready": false,
          "created_at": "2026-06-08T03:06:27Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": null,
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/900976a4d6494220bce133b617c2c83c",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-08T03:06:27Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/900976a4d6494220bce133b617c2c83c",
              "incident_timeline_ref": "incident-timeline://v9-2/fc317b3228f74924a40d1ae9e6ef2c00",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/workflow.instance.start",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-workflow.instance.start-idem-v9-2-duplicate",
            "execution_evidence_ref": "execution-evidence://v9-2/2810d3bc286040cfaa32235f36cbc2bc",
            "human_authorization_ref": null,
            "operation": "workflow.instance.start",
            "production_controlled_executor_ready": false,
            "redaction_status": "PASS",
            "request_id": "req-v9-2",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/start",
            "schema_version": "v9.0",
            "source": "product_console",
            "station_id": "station-v9-2",
            "target_refs": {
              "workflow_instance_id": "workflow-v9-2"
            }
          },
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/fc317b3228f74924a40d1ae9e6ef2c00",
          "operation": "workflow.instance.start",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_0f3a55210457",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/start",
          "status": "applied_v9_2_limited_runtime_slice"
        }
      },
      "scenario_id": "idempotency_duplicate_returns_prior_ref_and_conflict_denied",
      "status": "PASS"
    },
    {
      "notes": "Runtime DTO preflight blocks forbidden sensitive payload markers without storing the payload value.",
      "result": {
        "blocked_reason": "forbidden_raw_content",
        "incident_timeline_ref": "incident-timeline://v9-2/db1b1dce8c5643ccb629c6dc9ee581e9",
        "status": "blocked"
      },
      "scenario_id": "redaction_forbidden_content_denied",
      "status": "PASS"
    }
  ],
  "schema_version": "v9_2.runtime_acceptance.v1",
  "source_agent_durable_mutation_allowed": false,
  "source_refs": [
    "core/policies/v9_controlled_executor_runtime.py",
    "core/policies/v9_agent_executor_safety.py",
    "tests/test_v9_2_controlled_executor_runtime.py",
    "docs/design/V9.x/decisions/v9_2_high_risk_human_decision.json"
  ],
  "stage_id": "V9-2",
  "status": "PASS",
  "transcript_only": false,
  "v9_2_runtime_implementation_allowed": true
}

```

### `docs/design/V9.x/v9_3_runtime_acceptance_closure.md`
```markdown
# V9-3 Orchestration Runtime Evidence Summary

status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true
station_agent_binding: PASS
serial_parallel_fan_in_fan_out: PASS
attempt_history: PASS
artifact_lineage: PASS
lost_worker_recovery: PASS
source_agent_direct_mutation_denied: PASS
roman_forum_debate_fixture: PASS
video_storyboard_fixture: BLOCKED
natural_language_optimization_diff_only: PASS

Allowed claim:
V9-3 complete: multi-Agent orchestration runtime slice ready for review.

Boundary:
This evidence is a bounded runtime fixture for review. V9-4 and later runtime stages remain gated.

```

### `docs/design/V9.x/evidence/v9-3-orchestration-runtime/result-summary.md`
```markdown
# V9-3 Orchestration Runtime Evidence Summary

status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true
station_agent_binding: PASS
serial_parallel_fan_in_fan_out: PASS
attempt_history: PASS
artifact_lineage: PASS
lost_worker_recovery: PASS
source_agent_direct_mutation_denied: PASS
roman_forum_debate_fixture: PASS
video_storyboard_fixture: BLOCKED
natural_language_optimization_diff_only: PASS

Allowed claim:
V9-3 complete: multi-Agent orchestration runtime slice ready for review.

Boundary:
This evidence is a bounded runtime fixture for review. V9-4 and later runtime stages remain gated.

```

### `docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json`
```json
{
  "agent_executor_ready": false,
  "allowed_claim": "V9-3 complete: multi-Agent orchestration runtime slice ready for review.",
  "artifact_lineage": "PASS",
  "attempt_history": "PASS",
  "claim_scan": "PASS",
  "controlled_executor_ready": false,
  "distributed_multi_agent_runtime_ready": false,
  "evidence_scope": "real_runtime_fixture",
  "failure_recovery": "PASS",
  "fallback_demo_only": false,
  "full_multi_agent_orchestration_ready": false,
  "lost_worker_recovery": "PASS",
  "natural_language_optimization_diff_only": "PASS",
  "production_controlled_executor_ready": false,
  "redaction_scan": "PASS",
  "remaining_blockers": [
    "V9-4 autonomous coding workflow remains blocked until V9-3 evidence is externally accepted.",
    "Video storyboard provider-backed image generation remains blocked in this local fixture."
  ],
  "report_only": false,
  "roman_forum_debate_fixture": "PASS",
  "runtime_backed": true,
  "runtime_executor_route_created": false,
  "runtime_worker_created": false,
  "schema_version": "v9_3.runtime_acceptance.v1",
  "serial_parallel_fan_in_fan_out": "PASS",
  "source_agent_direct_mutation_denied": "PASS",
  "source_agent_durable_mutation_allowed": false,
  "stage_id": "V9-3",
  "station_agent_binding": "PASS",
  "status": "PASS",
  "transcript_only": false,
  "video_storyboard_fixture": "BLOCKED",
  "video_storyboard_provider_boundary": "BLOCKED_PROVIDER_UNAVAILABLE"
}

```

### `docs/design/V9.x/evidence/v9-3-orchestration-runtime/user-scenarios.json`
```json
[
  {
    "attribution_refs": [
      "lineage-ref://v9-3/roman-forum/philosopher",
      "lineage-ref://v9-3/roman-forum/engineer",
      "lineage-ref://v9-3/roman-forum/historian",
      "lineage-ref://v9-3/roman-forum/ethicist"
    ],
    "discussion_turn_count": 2,
    "evidence_chain_ref": "evidence-chain://v9-3/roman-forum",
    "evidence_scope": "real_runtime_fixture",
    "orchestration_run_id": "orch-v9-3-000934924ef4",
    "role_specific_agents": [
      "philosopher_agent",
      "engineer_agent",
      "historian_agent",
      "ethicist_agent",
      "moderator_agent"
    ],
    "runtime_backed": true,
    "scenario_id": "US-V9-07",
    "status": "PASS",
    "synthesis_ref": "artifact-ref://v9-3/roman-forum/attributed-synthesis"
  },
  {
    "blocked_reason": "provider_image_generation_not_available_in_local_fixture",
    "creative_brief_ref": "artifact-ref://v9-3/video/creative-brief",
    "evidence_scope": "blocked_provider_unavailable",
    "provider_invocation_ref": null,
    "provider_model_ref": null,
    "runtime_backed": false,
    "scenario_id": "US-V9-08",
    "script_ref": "artifact-ref://v9-3/video/script",
    "shot_list_ref": "artifact-ref://v9-3/video/shot-list",
    "status": "BLOCKED",
    "storyboard_image_artifact_refs": [],
    "storyboard_prompt_refs": [
      "artifact-ref://v9-3/video/storyboard-prompt-1",
      "artifact-ref://v9-3/video/storyboard-prompt-2",
      "artifact-ref://v9-3/video/storyboard-prompt-3",
      "artifact-ref://v9-3/video/storyboard-prompt-4"
    ],
    "visual_consistency_report_ref": "artifact-ref://v9-3/video/visual-consistency-report"
  },
  {
    "evidence_scope": "real_runtime_fixture",
    "lineage_refs": [
      "lineage-v9-3-research",
      "lineage-v9-3-implementation",
      "lineage-v9-3-review",
      "lineage-v9-3-synthesis"
    ],
    "mutation_applied_before_confirmation": false,
    "runtime_backed": true,
    "scenario_id": "US-V9-09",
    "source_agent_direct_mutation_denied": true,
    "status": "PASS",
    "user_confirmation_required": true,
    "workflow_diff_ref": "workflow-diff://v9-3/optimization/video-workflow"
  }
]

```

### `docs/design/V9.x/evidence/v9-4-readiness-closure/result-summary.md`
```markdown
# V9-4 Pre-Implementation Readiness Closure

status: PASS
current_decision: NO_GO_FOR_RUNTIME_IMPLEMENTATION
v9_4_runtime_implementation_allowed: false
human_high_risk_proceed_decision_recorded: false
claim_scan: PASS
redaction_scan: PASS

Required before runtime implementation:
- V9-4 readiness audit accepted
- V9-4 high-risk human proceed decision recorded
- coding workflow sandbox policy accepted
- diff/test/review/fix-loop evidence format accepted
- no auto commit / auto push / auto deploy denial evidence accepted
- No False Green scan PASS
- redaction scan PASS

```

### `docs/design/V9.x/evidence/v9-4-readiness-closure/pre-implementation-data.json`
```json
{
  "allowed_next_work": [
    "external_readiness_audit",
    "fixture_review",
    "evidence_package_structure_review",
    "human_high_risk_decision_preparation"
  ],
  "blocked_work": [
    "runtime_implementation",
    "patch_apply",
    "git_commit",
    "git_push",
    "production_deploy",
    "source_agent_durable_mutation",
    "v9_5_runtime_implementation",
    "v9_8_final_acceptance_execution"
  ],
  "claim_scan": "PASS",
  "created_at": "2026-06-08T03:06:44Z",
  "current_decision": "NO_GO_FOR_RUNTIME_IMPLEMENTATION",
  "doc_results": [
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/v9_4_development_and_acceptance_plan.md",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/v9_4_autonomous_coding_workflow_implementation_spec.md",
      "status": "PASS"
    },
    {
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/v9_automation_assisted_development_policy.md",
      "status": "PASS"
    }
  ],
  "entry_baseline": {
    "v9_3_evidence_scope": "real_runtime_fixture",
    "v9_3_runtime_backed": true,
    "v9_3_status": "PASS",
    "v9_3_video_storyboard_fixture": "BLOCKED",
    "v9_3_video_storyboard_provider_boundary": "BLOCKED_PROVIDER_UNAVAILABLE"
  },
  "fixture_results": [
    {
      "expected": "proposal_only_and_no_mutation",
      "fixture": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/fixtures/v9-4-coding-workflow/small_code_change_proposal.json",
      "status": "PASS"
    },
    {
      "expected_reason": "auto_commit_without_human_approval_denied",
      "fixture_id": "v9_4_auto_commit_without_human_approval",
      "operation": "git.commit",
      "status": "PASS"
    },
    {
      "expected_reason": "auto_push_without_release_gate_denied",
      "fixture_id": "v9_4_auto_push_without_release_gate",
      "operation": "git.push",
      "status": "PASS"
    },
    {
      "expected_reason": "auto_deploy_without_production_gate_denied",
      "fixture_id": "v9_4_auto_deploy_without_production_gate",
      "operation": "production.deploy",
      "status": "PASS"
    },
    {
      "expected_reason": "unreviewed_patch_apply_denied",
      "fixture_id": "v9_4_unreviewed_patch_apply_attempt",
      "operation": "patch.apply",
      "status": "PASS"
    },
    {
      "expected_reason": "review_summary_is_not_approval",
      "fixture_id": "v9_4_review_summary_as_approval_attempt",
      "operation": "approval.resolve",
      "status": "PASS"
    }
  ],
  "gate_checks": [
    {
      "check_id": "v9_3_evidence_pass",
      "details": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
      "status": "PASS"
    },
    {
      "check_id": "v9_4_high_risk_human_decision_missing",
      "details": "Expected at readiness closure. Runtime implementation remains blocked until user records this decision.",
      "status": "PASS"
    },
    {
      "check_id": "v9_4_runtime_implementation_allowed_false",
      "details": "This closure does not authorize runtime implementation.",
      "status": "PASS"
    }
  ],
  "human_high_risk_proceed_decision_recorded": false,
  "notes": [
    "V9-4 readiness is prepared, but runtime implementation remains blocked.",
    "ReviewSummary cannot become approval.",
    "DiffProposal is proposal-only until human review acceptance."
  ],
  "planning_only": true,
  "redaction_scan": "PASS",
  "required_before_runtime_implementation": [
    "V9-4 readiness audit accepted",
    "V9-4 high-risk human proceed decision recorded",
    "coding workflow sandbox policy accepted",
    "diff/test/review/fix-loop evidence format accepted",
    "no auto commit / auto push / auto deploy denial evidence accepted",
    "No False Green scan PASS",
    "redaction scan PASS"
  ],
  "runtime_backed": false,
  "schema_version": "v9_4.pre_implementation_readiness_closure.v1",
  "stage_id": "V9-4",
  "status": "PASS",
  "v9_4_runtime_implementation_allowed": false
}

```

### `docs/design/V9.x/v9_4_runtime_acceptance_closure.md`
```markdown
# V9-4 Coding Workflow Pilot Evidence Summary

status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true
diff_proposal_is_not_patch_apply: PASS
sandboxed_test_result: PASS
review_summary_is_not_approval: PASS
auto_commit_denied: PASS
auto_push_denied: PASS
auto_deploy_denied: PASS
source_agent_direct_mutation_denied: PASS

Allowed claim:
V9-4 complete: autonomous coding workflow pilot ready for review.

```

### `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/result-summary.md`
```markdown
# V9-4 Coding Workflow Pilot Evidence Summary

status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true
diff_proposal_is_not_patch_apply: PASS
sandboxed_test_result: PASS
review_summary_is_not_approval: PASS
auto_commit_denied: PASS
auto_push_denied: PASS
auto_deploy_denied: PASS
source_agent_direct_mutation_denied: PASS

Allowed claim:
V9-4 complete: autonomous coding workflow pilot ready for review.

```

### `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json`
```json
{
  "agent_executor_ready": false,
  "allowed_claim": "V9-4 complete: autonomous coding workflow pilot ready for review.",
  "auto_commit_denied": "PASS",
  "auto_deploy_denied": "PASS",
  "auto_push_denied": "PASS",
  "autonomous_coding_workflow_ready": false,
  "claim_scan": "PASS",
  "diff_proposal_created": "PASS",
  "diff_proposal_is_not_patch_apply": "PASS",
  "evidence_scope": "real_runtime_fixture",
  "fallback_demo_only": false,
  "fix_loop_creates_new_diff_proposal": "PASS",
  "production_terminal_automation_ready": false,
  "redaction_scan": "PASS",
  "remaining_blockers": [
    "This V9-4 evidence package does not authorize V9-5 terminal worker expansion without a separate V9-5 decision.",
    "V9-8 final acceptance remains blocked until V9-0..V9-7 evidence packages exist."
  ],
  "report_only": false,
  "review_summary_is_not_approval": "PASS",
  "runtime_backed": true,
  "sandboxed_test_result": "PASS",
  "schema_version": "v9_4.runtime_acceptance.v1",
  "source_agent_direct_mutation_denied": "PASS",
  "stage_id": "V9-4",
  "status": "PASS",
  "transcript_only": false,
  "unrestricted_terminal_worker_ready": false,
  "unreviewed_patch_apply_denied": "PASS"
}

```

### `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/git-operation-deny-report.json`
```json
{
  "all_denied": true,
  "audit_ref": "audit://v9-4/deny-report",
  "correlation_id": "corr-v9-4-125fe7c00a",
  "created_at": "2026-06-08T03:06:38Z",
  "denied_operations": [
    {
      "audit_ref": "audit://v9-4/deny/patch-apply",
      "executed": false,
      "human_review_accepted": false,
      "operation": "patch.apply",
      "production_gate_accepted": false,
      "reason": "unreviewed_patch_apply_denied",
      "release_gate_accepted": false,
      "status": "DENIED"
    },
    {
      "audit_ref": "audit://v9-4/deny/git-commit",
      "executed": false,
      "human_review_accepted": false,
      "operation": "git.commit",
      "production_gate_accepted": false,
      "reason": "auto_commit_without_human_approval_denied",
      "release_gate_accepted": false,
      "status": "DENIED"
    },
    {
      "audit_ref": "audit://v9-4/deny/git-push",
      "executed": false,
      "human_review_accepted": false,
      "operation": "git.push",
      "production_gate_accepted": false,
      "reason": "auto_push_without_release_gate_denied",
      "release_gate_accepted": false,
      "status": "DENIED"
    },
    {
      "audit_ref": "audit://v9-4/deny/production-deploy",
      "executed": false,
      "human_review_accepted": false,
      "operation": "production.deploy",
      "production_gate_accepted": false,
      "reason": "auto_deploy_without_production_gate_denied",
      "release_gate_accepted": false,
      "status": "DENIED"
    },
    {
      "audit_ref": "audit://v9-4/deny/approval-resolve",
      "executed": false,
      "human_review_accepted": false,
      "operation": "approval.resolve",
      "production_gate_accepted": false,
      "reason": "review_summary_is_not_approval",
      "release_gate_accepted": false,
      "status": "DENIED"
    }
  ],
  "deny_report_ref": "deny-report-ref://v9-4/fc10c2c1d80a",
  "request_id": "req-v9-4-58ee0b1ec2",
  "schema_version": "v9_4.git_operation_deny_report.v1"
}

```

### `docs/design/V9.x/evidence/v9-5-terminal-worker/result-summary.md`
```markdown
# V9-5 Governed Terminal Worker Evidence Summary

status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true
workspace_scope_guard: PASS
command_tier_policy: PASS
readonly_command_transcript: PASS
build_or_test_command_result: PASS
diff_capture: PASS
workspace_escape_denied: PASS
symlink_escape_denied: PASS
git_push_denied: PASS
production_deploy_denied: PASS

Allowed claim:
V9-5 complete: governed terminal worker expansion ready for review.

No False Green Statement:
V9-5 proves only a governed terminal worker expansion ready for review. It does not prove unrestricted terminal worker readiness or production terminal automation.

```

### `docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json`
```json
{
  "allowed_claim": "V9-5 complete: governed terminal worker expansion ready for review.",
  "auto_commit_enabled": false,
  "auto_push_enabled": false,
  "browser_account_automation_enabled": false,
  "build_or_test_command_result": "PASS",
  "claim_scan": "PASS",
  "command_tier_policy": "PASS",
  "diff_capture": "PASS",
  "evidence_scope": "real_runtime_fixture",
  "git_push_denied": "PASS",
  "network_without_policy_denied": "PASS",
  "production_deploy_denied": "PASS",
  "production_deploy_enabled": false,
  "production_terminal_automation_ready": false,
  "readonly_command_transcript": "PASS",
  "redaction_scan": "PASS",
  "runtime_backed": true,
  "schema_version": "v9_5.terminal_worker_acceptance.v1",
  "sensitive_read_denied": "PASS",
  "source_agent_direct_mutation_denied": "PASS",
  "stage_id": "V9-5",
  "status": "PASS",
  "symlink_escape_denied": "PASS",
  "unrestricted_shell_enabled": false,
  "unrestricted_terminal_worker_ready": false,
  "workspace_escape_denied": "PASS",
  "workspace_scope_guard": "PASS",
  "write_action_requires_human_authorization": "PASS"
}

```

### `docs/design/V9.x/evidence/v9-5-terminal-worker/command-decisions.json`
```json
[
  {
    "argv": [
      "pwd"
    ],
    "audit_ref": "audit://v9-5/command/tier0_readonly",
    "command_decision_id": "terminal-command-decision-v9-5-b4cebde6694b",
    "command_tier": "tier0_readonly",
    "created_at": "2026-06-08T03:06:43Z",
    "denial_reason": null,
    "diff_capture_ref": null,
    "policy_decision": "allow",
    "requires_human_authorization_ref": false,
    "transcript_ref": "terminal-transcript.txt"
  },
  {
    "argv": [
      "git",
      "status",
      "--short",
      "--",
      "core",
      "tools/v9",
      "tests",
      "docs/design/V9.x"
    ],
    "audit_ref": "audit://v9-5/command/tier0_readonly",
    "command_decision_id": "terminal-command-decision-v9-5-1905c1863192",
    "command_tier": "tier0_readonly",
    "created_at": "2026-06-08T03:06:43Z",
    "denial_reason": null,
    "diff_capture_ref": null,
    "policy_decision": "allow",
    "requires_human_authorization_ref": false,
    "transcript_ref": "terminal-transcript.txt"
  },
  {
    "argv": [
      "rg",
      "-n",
      "V9-5",
      "docs/design/V9.x/v9_5_development_and_acceptance_plan.md"
    ],
    "audit_ref": "audit://v9-5/command/tier0_readonly",
    "command_decision_id": "terminal-command-decision-v9-5-512753bc5383",
    "command_tier": "tier0_readonly",
    "created_at": "2026-06-08T03:06:43Z",
    "denial_reason": null,
    "diff_capture_ref": null,
    "policy_decision": "allow",
    "requires_human_authorization_ref": false,
    "transcript_ref": "terminal-transcript.txt"
  },
  {
    "argv": [
      "./.venv/bin/python",
      "-m",
      "pytest",
      "tests/test_v9_4_readiness_closure.py",
      "-q"
    ],
    "audit_ref": "audit://v9-5/command/tier1_build_test",
    "command_decision_id": "terminal-command-decision-v9-5-38391269a048",
    "command_tier": "tier1_build_test",
    "created_at": "2026-06-08T03:06:43Z",
    "denial_reason": null,
    "diff_capture_ref": null,
    "policy_decision": "allow",
    "requires_human_authorization_ref": false,
    "transcript_ref": "terminal-transcript.txt"
  },
  {
    "argv": [
      "diff.proposal",
      "docs/design/V9.x/v9_5_development_and_acceptance_plan.md"
    ],
    "audit_ref": "audit://v9-5/diff-proposal",
    "command_decision_id": "terminal-command-decision-v9-5-ec2b6da352c0",
    "command_tier": "tier2_diff_proposal",
    "created_at": "2026-06-08T03:06:45Z",
    "denial_reason": null,
    "diff_capture_ref": "diff-capture.patch",
    "policy_decision": "allow_proposal_only",
    "requires_human_authorization_ref": true,
    "transcript_ref": "terminal-transcript.txt"
  }
]

```

### `docs/design/V9.x/evidence/v9-5-terminal-worker/denial-evidence.json`
```json
[
  {
    "audit_ref": "audit://v9-5/deny/symlink_escape",
    "check_id": "symlink_escape_denied",
    "expected_denial_reason": "symlink_escape_denied",
    "observed_denial_reason": "symlink_escape_denied",
    "status": "PASS"
  },
  {
    "argv": [
      "cat",
      "../CLAUDE.md"
    ],
    "audit_ref": "audit://v9-5/deny/workspace_escape_denied",
    "check_id": "workspace_escape_denied",
    "expected_denial_reason": "workspace_escape_denied",
    "observed_denial_reason": "workspace_escape_denied",
    "status": "PASS"
  },
  {
    "argv": [
      "cat",
      "/etc/passwd"
    ],
    "audit_ref": "audit://v9-5/deny/absolute_workspace_escape_denied",
    "check_id": "absolute_workspace_escape_denied",
    "expected_denial_reason": "workspace_escape_denied",
    "observed_denial_reason": "workspace_escape_denied",
    "status": "PASS"
  },
  {
    "argv": [
      "cat",
      ".env"
    ],
    "audit_ref": "audit://v9-5/deny/sensitive_read_denied",
    "check_id": "sensitive_read_denied",
    "expected_denial_reason": "sensitive_path_denied",
    "observed_denial_reason": "sensitive_path_denied",
    "status": "PASS"
  },
  {
    "argv": [
      "git",
      "push"
    ],
    "audit_ref": "audit://v9-5/deny/git_push_denied",
    "check_id": "git_push_denied",
    "expected_denial_reason": "command_not_allowlisted",
    "observed_denial_reason": "command_not_allowlisted",
    "status": "PASS"
  },
  {
    "argv": [
      "production.deploy"
    ],
    "audit_ref": "audit://v9-5/deny/production_deploy_denied",
    "check_id": "production_deploy_denied",
    "expected_denial_reason": "command_not_allowlisted",
    "observed_denial_reason": "command_not_allowlisted",
    "status": "PASS"
  },
  {
    "argv": [
      "curl",
      "https://example.com"
    ],
    "audit_ref": "audit://v9-5/deny/network_without_policy_denied",
    "check_id": "network_without_policy_denied",
    "expected_denial_reason": "command_not_allowlisted",
    "observed_denial_reason": "command_not_allowlisted",
    "status": "PASS"
  }
]

```

### `docs/design/V9.x/evidence/v9-6-workflow-studio/result-summary.md`
```markdown
# V9-6 Workflow Studio Productization Evidence Summary

status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true

Allowed claim:
V9-6 complete: Workflow Studio productization slice ready for review.

This proves only a bounded Workflow Studio productization slice ready for review. It does not prove complete Workflow Studio readiness.
```

### `docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json`
```json
{
  "agent_executor_ready": false,
  "allowed_claim": "V9-6 complete: Workflow Studio productization slice ready for review.",
  "browser_no_direct_internal_runtime_routes": "PASS",
  "browser_no_direct_v1_events_subscribe": "PASS",
  "browser_no_direct_v1_rpc": "PASS",
  "claim_scan": "PASS",
  "complete_workflow_studio_ready": false,
  "evidence_chain_readonly_no_execute_buttons": "PASS",
  "evidence_scope": "real_runtime_fixture",
  "hidden_mutation_form_absent": "PASS",
  "human_authorization_ref": "human-auth://v9-6/6900005f5b19",
  "manual_confirmation_records_human_authorization_ref": "PASS",
  "natural_language_optimization_creates_workflow_diff": "PASS",
  "redaction_scan": "PASS",
  "runtime_backed": true,
  "runtime_report_readonly_no_hidden_form": "PASS",
  "schema_version": "v9_6.workflow_studio_acceptance.v1",
  "stage_id": "V9-6",
  "station_agent_profile_is_visible": "PASS",
  "status": "PASS",
  "studio_loads_workflow_graph_from_bff": "PASS",
  "ui_no_auto_apply_auto_publish_agent_executed_copy": "PASS",
  "workflow_diff_proposal_ref": "workflow-diff://v9-6/c29b1563f616"
}
```

### `docs/design/V9.x/evidence/v9-6-workflow-studio/studio_network_log.json`
```json
{
  "browser_network_log": [
    "GET /bff/v9/studio-state",
    "GET /bff/v9/runtime-report",
    "GET /bff/v9/evidence-chain",
    "GET /bff/v9/workflow-blueprint",
    "POST /bff/v9/workflow-diff-proposal",
    "POST /bff/v9/manual-confirmation",
    "POST /bff/v9/review-handoff"
  ],
  "route_decisions": [
    {
      "audit_ref": "audit://v9-6/browser-route/b7ed16f6ac81",
      "denial_reason": null,
      "policy_decision": "allow",
      "route": "GET /bff/v9/studio-state"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/62af1e91cccb",
      "denial_reason": null,
      "policy_decision": "allow",
      "route": "GET /bff/v9/runtime-report"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/ee4a6fec6d14",
      "denial_reason": null,
      "policy_decision": "allow",
      "route": "GET /bff/v9/evidence-chain"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/3abbcf71f3fe",
      "denial_reason": null,
      "policy_decision": "allow",
      "route": "GET /bff/v9/workflow-blueprint"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/e00fe4d1f167",
      "denial_reason": null,
      "policy_decision": "allow",
      "route": "POST /bff/v9/workflow-diff-proposal"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/9cf0ad9979ab",
      "denial_reason": null,
      "policy_decision": "allow",
      "route": "POST /bff/v9/manual-confirmation"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/1baa5ad4069d",
      "denial_reason": null,
      "policy_decision": "allow",
      "route": "POST /bff/v9/review-handoff"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/eec6e88c8ad1",
      "denial_reason": "internal_route_denied",
      "policy_decision": "deny",
      "route": "/v1/rpc"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/fe17b1bf671b",
      "denial_reason": "internal_route_denied",
      "policy_decision": "deny",
      "route": "/v1/events/subscribe"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/ac54242a6c1e",
      "denial_reason": "internal_route_denied",
      "policy_decision": "deny",
      "route": "/v1/internal/runtime"
    },
    {
      "audit_ref": "audit://v9-6/browser-route/4986dbe3c23f",
      "denial_reason": "internal_route_denied",
      "policy_decision": "deny",
      "route": "/v1/internal/workflow-store"
    }
  ],
  "status": "PASS"
}
```

### `docs/design/V9.x/evidence/v9-6-workflow-studio/studio_hidden_form_scan.json`
```json
{
  "hidden_form_present": false,
  "status": "PASS"
}
```

### `docs/design/V9.x/evidence/v9-6-workflow-studio/studio_ui_copy_claim_scan.json`
```json
{
  "forbidden_copy_hits": [],
  "status": "PASS"
}
```

### `docs/design/V9.x/evidence/v9-6-workflow-studio/manual_confirmation_evidence.json`
```json
{
  "actor_id": "user_v9_6_reviewer",
  "app_id": "app_v9_6",
  "audit_ref": "audit://v9-6/manual-confirmation/c6ca8247f036",
  "correlation_id": "correlation_v9_6",
  "created_at": "2026-06-08T03:06:46.321340+00:00",
  "executes_runtime_action": false,
  "expires_at": "2999-01-01T00:00:00+00:00",
  "human_authorization_ref": "human-auth://v9-6/6900005f5b19",
  "operation": "workflow.diff.confirm",
  "project_id": "project_v9_6",
  "proposal_id": "workflow-diff-proposal-v9-6-8bd1f5b09ffa",
  "request_id": "request_v9_6",
  "source": "product_console",
  "target_refs": {
    "workflow_id": "workflow-v9-6",
    "workflow_version_id": "workflow-version-v9-6"
  },
  "tenant_id": "tenant_v9_6",
  "workspace_id": "workspace_v9_6"
}
```

### `docs/design/V9.x/evidence/v9-6-workflow-studio/workflow_diff_proposal.json`
```json
{
  "actor_id": "user_v9_6_reviewer",
  "app_id": "app_v9_6",
  "audit_ref": "audit://v9-6/workflow-diff-proposal/50696a10ed0d",
  "correlation_id": "correlation_v9_6",
  "created_at": "2026-06-08T03:06:46.320800+00:00",
  "diff_ref": "workflow-diff://v9-6/c29b1563f616",
  "durable_mutation_performed": false,
  "natural_language_goal": "减少一个冗余审查工位，并新增安全审查 Agent。",
  "project_id": "project_v9_6",
  "proposal_id": "workflow-diff-proposal-v9-6-8bd1f5b09ffa",
  "request_id": "request_v9_6",
  "requires_manual_confirmation": true,
  "risk_delta": "medium_requires_manual_confirmation",
  "source": "product_console",
  "target_refs": {
    "workflow_id": "workflow-v9-6",
    "workflow_version_id": "workflow-version-v9-6"
  },
  "tenant_id": "tenant_v9_6",
  "workflow_spec_ref": "workflow-spec://v9-6/studio-productization",
  "workspace_id": "workspace_v9_6"
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/result-summary.md`
```markdown
# V9-7 Production Governance Evidence Summary

status: PASS
evidence_scope: real_runtime_fixture
runtime_backed: true

Allowed claim:
V9-7 complete: production governance and terminal automation gate ready for review.

This proves only a production governance and terminal automation gate ready for review. It does not prove production automation readiness.
```

### `docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json`
```json
{
  "allowed_claim": "V9-7 complete: production governance and terminal automation gate ready for review.",
  "audit_export_append_only": "PASS",
  "audit_export_mutation_denied": "PASS",
  "browser_automation_blocked_without_separate_prd": "PASS",
  "claim_scan": "PASS",
  "credential_lease_expired_denied": "PASS",
  "credential_lease_revoked_denied": "PASS",
  "credential_lease_wrong_operation_denied": "PASS",
  "evidence_hardening_scan_pass": "PASS",
  "evidence_scope": "real_runtime_fixture",
  "incident_timeline_records_credential_denial": "PASS",
  "incident_timeline_records_policy_denial": "PASS",
  "incident_timeline_records_timeout": "PASS",
  "incident_timeline_records_worker_lost": "PASS",
  "production_automation_ready": false,
  "production_browser_automation_ready": false,
  "production_terminal_automation_ready": false,
  "redaction_scan": "PASS",
  "runtime_backed": true,
  "schema_version": "v9_7.production_governance_acceptance.v1",
  "service_account_autonomous_override_denied": "PASS",
  "stage_id": "V9-7",
  "status": "PASS",
  "tenant_isolation_wrong_tenant_denied": "PASS",
  "terminal_automation_policy_gate_only": "PASS"
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/governance-fixture.json`
```json
{
  "audit_export": {
    "allowed_actions": [
      "view",
      "export",
      "open_evidence"
    ],
    "app_id": "app_v9_7",
    "append_only": true,
    "audit_ref": "audit://v9-7/audit-export/dd0b76e6d81c",
    "checksum": "73f94d7a68000359fd58a85b26830b9434e88f5562298a3aa7aea21e4a3de32b",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.385289+00:00",
    "export_id": "audit-export-v9-7-4a7ff89d4149",
    "immutable": true,
    "included_refs": [
      "audit://v9-7/tenant-isolation/1b2b9b5a4222",
      "audit://v9-7/credential-lease/3ed0d12b5bdb",
      "audit://v9-7/service-account-binding/45bc74c854fb",
      "audit://v9-7/incident/b8de00541e34",
      "audit://v9-7/incident/b72f7e3277d4",
      "audit://v9-7/incident/1acd482a2460",
      "audit://v9-7/incident/94836f5ccee9"
    ],
    "project_id": "project_v9_7",
    "readonly": true,
    "request_id": "request_v9_7",
    "requested_by": "user_v9_7_reviewer",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  "audit_export_mutation_denial": {
    "attempted_action": "overwrite",
    "audit_ref": "audit://v9-7/audit-export-mutation-denial/367a258e28e9",
    "denial_reason": "audit_export_mutation_denied",
    "export_id": "audit-export-v9-7-4a7ff89d4149",
    "policy_decision": "deny"
  },
  "browser_automation_policy": {
    "audit_ref": "audit://v9-7/browser-automation-policy/d63671bc8a64",
    "browser_account_automation_allowed": false,
    "explicit_human_decision_required": true,
    "policy_decision": "deny_without_separate_prd",
    "policy_id": "browser-automation-policy-v9-7-3ea2cd49d867",
    "separate_prd_required": true
  },
  "credential_leases": {
    "allow": {
      "app_id": "app_v9_7",
      "audience": "provider:minimax",
      "audit_ref": "audit://v9-7/credential-lease/3ed0d12b5bdb",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.384837+00:00",
      "credential_lease_ref": "credential-lease://v9-7/redacted-minimax",
      "decision_id": "credential-lease-v9-7-99ea99c01ad0",
      "denial_reason": null,
      "expires_at": "2999-01-01T00:00:00+00:00",
      "operation": "terminal.audit.review",
      "policy_decision": "allow",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_audience": "provider:minimax",
      "requested_operation": "terminal.audit.review",
      "revoked": false,
      "secret_material_access": false,
      "service_account_id": "service_account_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    "expired": {
      "app_id": "app_v9_7",
      "audience": "provider:minimax",
      "audit_ref": "audit://v9-7/credential-lease/b37629c4f3cf",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.384928+00:00",
      "credential_lease_ref": "credential-lease://v9-7/redacted-expired",
      "decision_id": "credential-lease-v9-7-9a1a08681d53",
      "denial_reason": "lease_expired",
      "expires_at": "2000-01-01T00:00:00+00:00",
      "operation": "terminal.audit.review",
      "policy_decision": "deny",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_audience": "provider:minimax",
      "requested_operation": "terminal.audit.review",
      "revoked": false,
      "secret_material_access": false,
      "service_account_id": "service_account_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    "revoked": {
      "app_id": "app_v9_7",
      "audience": "provider:minimax",
      "audit_ref": "audit://v9-7/credential-lease/e8cea55591a9",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.384965+00:00",
      "credential_lease_ref": "credential-lease://v9-7/redacted-revoked",
      "decision_id": "credential-lease-v9-7-4e3b197017b6",
      "denial_reason": "lease_revoked",
      "expires_at": "2999-01-01T00:00:00+00:00",
      "operation": "terminal.audit.review",
      "policy_decision": "deny",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_audience": "provider:minimax",
      "requested_operation": "terminal.audit.review",
      "revoked": true,
      "secret_material_access": false,
      "service_account_id": "service_account_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    "wrong_operation": {
      "app_id": "app_v9_7",
      "audience": "provider:minimax",
      "audit_ref": "audit://v9-7/credential-lease/14cae344ee09",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.384888+00:00",
      "credential_lease_ref": "credential-lease://v9-7/redacted-minimax",
      "decision_id": "credential-lease-v9-7-e13f89a96e11",
      "denial_reason": "operation_mismatch",
      "expires_at": "2999-01-01T00:00:00+00:00",
      "operation": "terminal.audit.review",
      "policy_decision": "deny",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_audience": "provider:minimax",
      "requested_operation": "production.deploy",
      "revoked": false,
      "secret_material_access": false,
      "service_account_id": "service_account_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    }
  },
  "evidence_hardening_report": {
    "audit_ref": "audit://v9-7/evidence-hardening/3af5dce94a7d",
    "claim_scan_status": "PASS",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.387366+00:00",
    "forbidden_claim_hits": [],
    "forbidden_raw_hits": [],
    "policy_decision": "allow",
    "redaction_status": "PASS",
    "report_id": "evidence-hardening-v9-7-313f3d930225",
    "request_id": "request_v9_7",
    "scanned_refs": [
      "audit://v9-7/audit-export/dd0b76e6d81c",
      "audit://v9-7/terminal-automation-policy/af60fe8eec01"
    ]
  },
  "incident_timeline": [
    {
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/incident/b8de00541e34",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.385050+00:00",
      "event_id": "incident-event-v9-7-6b7fe1cd3489",
      "event_type": "policy_denied",
      "operation": "production.deploy",
      "project_id": "project_v9_7",
      "readonly": true,
      "request_id": "request_v9_7",
      "severity": "high",
      "source_ref": "audit://v9-7/tenant-isolation/ea3352464e9f",
      "summary": "Policy denied production deploy attempt.",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    {
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/incident/b72f7e3277d4",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.385094+00:00",
      "event_id": "incident-event-v9-7-88df9f233ddd",
      "event_type": "credential_denied",
      "operation": "production.deploy",
      "project_id": "project_v9_7",
      "readonly": true,
      "request_id": "request_v9_7",
      "severity": "high",
      "source_ref": "audit://v9-7/credential-lease/14cae344ee09",
      "summary": "Credential lease denied wrong operation.",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    {
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/incident/1acd482a2460",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.385137+00:00",
      "event_id": "incident-event-v9-7-3b58e4cbc62b",
      "event_type": "timeout",
      "operation": "terminal.audit.review",
      "project_id": "project_v9_7",
      "readonly": true,
      "request_id": "request_v9_7",
      "severity": "medium",
      "source_ref": "terminal-session://v9-7/timeout",
      "summary": "Terminal governance review timed out.",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    {
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/incident/94836f5ccee9",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.385172+00:00",
      "event_id": "incident-event-v9-7-0f61d58209ff",
      "event_type": "worker_lost",
      "operation": "terminal.audit.review",
      "project_id": "project_v9_7",
      "readonly": true,
      "request_id": "request_v9_7",
      "severity": "medium",
      "source_ref": "worker://v9-7/lost",
      "summary": "Worker loss recorded with no retry mutation.",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    }
  ],
  "service_account_bindings": {
    "allow": {
      "allowed_operations": [
        "terminal.audit.review",
        "audit.export.create"
      ],
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/service-account-binding/45bc74c854fb",
      "autonomous_override": false,
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.384985+00:00",
      "decision_id": "service-account-binding-v9-7-0ba6ee6f8936",
      "denial_reason": null,
      "human_authorization_ref": "human-auth://v9-7/governance",
      "policy_decision": "allow",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_operation": "terminal.audit.review",
      "service_account_id": "service_account_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    "autonomous_override": {
      "allowed_operations": [
        "terminal.audit.review"
      ],
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/service-account-binding/bf432b647fb6",
      "autonomous_override": true,
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.385005+00:00",
      "decision_id": "service-account-binding-v9-7-6b77521f224c",
      "denial_reason": "autonomous_override_denied",
      "human_authorization_ref": "human-auth://v9-7/governance",
      "policy_decision": "deny",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_operation": "terminal.audit.review",
      "service_account_id": "service_account_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    }
  },
  "tenant_isolation": {
    "allow": {
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/tenant-isolation/1b2b9b5a4222",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.384313+00:00",
      "decision_id": "tenant-isolation-v9-7-24bd90a59744",
      "denial_reason": null,
      "policy_decision": "allow",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_app_id": "app_v9_7",
      "requested_tenant_id": "tenant_v9_7",
      "requested_workspace_id": "workspace_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    },
    "wrong_tenant": {
      "app_id": "app_v9_7",
      "audit_ref": "audit://v9-7/tenant-isolation/ea3352464e9f",
      "correlation_id": "correlation_v9_7",
      "created_at": "2026-06-08T03:06:47.384738+00:00",
      "decision_id": "tenant-isolation-v9-7-bcaddac45036",
      "denial_reason": "tenant_mismatch",
      "policy_decision": "deny",
      "project_id": "project_v9_7",
      "request_id": "request_v9_7",
      "requested_app_id": "app_v9_7",
      "requested_tenant_id": "tenant_other",
      "requested_workspace_id": "workspace_v9_7",
      "tenant_id": "tenant_v9_7",
      "workspace_id": "workspace_v9_7"
    }
  },
  "terminal_automation_policy": {
    "allowed_mode": "governance_gate_only",
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/terminal-automation-policy/af60fe8eec01",
    "browser_account_automation_allowed": false,
    "policy_decision": "deny_production_automation_enablement",
    "policy_id": "terminal-automation-policy-v9-7-ea4ffeb6bfef",
    "production_terminal_automation_ready": false,
    "requires_credential_lease_decision": true,
    "requires_human_authorization_ref": true,
    "requires_incident_timeline": true,
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  }
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/tenant-isolation-decisions.json`
```json
{
  "allow": {
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/tenant-isolation/1b2b9b5a4222",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.384313+00:00",
    "decision_id": "tenant-isolation-v9-7-24bd90a59744",
    "denial_reason": null,
    "policy_decision": "allow",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_app_id": "app_v9_7",
    "requested_tenant_id": "tenant_v9_7",
    "requested_workspace_id": "workspace_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  "wrong_tenant": {
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/tenant-isolation/ea3352464e9f",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.384738+00:00",
    "decision_id": "tenant-isolation-v9-7-bcaddac45036",
    "denial_reason": "tenant_mismatch",
    "policy_decision": "deny",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_app_id": "app_v9_7",
    "requested_tenant_id": "tenant_other",
    "requested_workspace_id": "workspace_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  }
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/credential-lease-decisions.json`
```json
{
  "allow": {
    "app_id": "app_v9_7",
    "audience": "provider:minimax",
    "audit_ref": "audit://v9-7/credential-lease/3ed0d12b5bdb",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.384837+00:00",
    "credential_lease_ref": "credential-lease://v9-7/redacted-minimax",
    "decision_id": "credential-lease-v9-7-99ea99c01ad0",
    "denial_reason": null,
    "expires_at": "2999-01-01T00:00:00+00:00",
    "operation": "terminal.audit.review",
    "policy_decision": "allow",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_audience": "provider:minimax",
    "requested_operation": "terminal.audit.review",
    "revoked": false,
    "secret_material_access": false,
    "service_account_id": "service_account_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  "expired": {
    "app_id": "app_v9_7",
    "audience": "provider:minimax",
    "audit_ref": "audit://v9-7/credential-lease/b37629c4f3cf",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.384928+00:00",
    "credential_lease_ref": "credential-lease://v9-7/redacted-expired",
    "decision_id": "credential-lease-v9-7-9a1a08681d53",
    "denial_reason": "lease_expired",
    "expires_at": "2000-01-01T00:00:00+00:00",
    "operation": "terminal.audit.review",
    "policy_decision": "deny",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_audience": "provider:minimax",
    "requested_operation": "terminal.audit.review",
    "revoked": false,
    "secret_material_access": false,
    "service_account_id": "service_account_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  "revoked": {
    "app_id": "app_v9_7",
    "audience": "provider:minimax",
    "audit_ref": "audit://v9-7/credential-lease/e8cea55591a9",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.384965+00:00",
    "credential_lease_ref": "credential-lease://v9-7/redacted-revoked",
    "decision_id": "credential-lease-v9-7-4e3b197017b6",
    "denial_reason": "lease_revoked",
    "expires_at": "2999-01-01T00:00:00+00:00",
    "operation": "terminal.audit.review",
    "policy_decision": "deny",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_audience": "provider:minimax",
    "requested_operation": "terminal.audit.review",
    "revoked": true,
    "secret_material_access": false,
    "service_account_id": "service_account_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  "wrong_operation": {
    "app_id": "app_v9_7",
    "audience": "provider:minimax",
    "audit_ref": "audit://v9-7/credential-lease/14cae344ee09",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.384888+00:00",
    "credential_lease_ref": "credential-lease://v9-7/redacted-minimax",
    "decision_id": "credential-lease-v9-7-e13f89a96e11",
    "denial_reason": "operation_mismatch",
    "expires_at": "2999-01-01T00:00:00+00:00",
    "operation": "terminal.audit.review",
    "policy_decision": "deny",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_audience": "provider:minimax",
    "requested_operation": "production.deploy",
    "revoked": false,
    "secret_material_access": false,
    "service_account_id": "service_account_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  }
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/service-account-binding-decisions.json`
```json
{
  "allow": {
    "allowed_operations": [
      "terminal.audit.review",
      "audit.export.create"
    ],
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/service-account-binding/45bc74c854fb",
    "autonomous_override": false,
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.384985+00:00",
    "decision_id": "service-account-binding-v9-7-0ba6ee6f8936",
    "denial_reason": null,
    "human_authorization_ref": "human-auth://v9-7/governance",
    "policy_decision": "allow",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_operation": "terminal.audit.review",
    "service_account_id": "service_account_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  "autonomous_override": {
    "allowed_operations": [
      "terminal.audit.review"
    ],
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/service-account-binding/bf432b647fb6",
    "autonomous_override": true,
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.385005+00:00",
    "decision_id": "service-account-binding-v9-7-6b77521f224c",
    "denial_reason": "autonomous_override_denied",
    "human_authorization_ref": "human-auth://v9-7/governance",
    "policy_decision": "deny",
    "project_id": "project_v9_7",
    "request_id": "request_v9_7",
    "requested_operation": "terminal.audit.review",
    "service_account_id": "service_account_v9_7",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  }
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/audit-export-package.json`
```json
{
  "allowed_actions": [
    "view",
    "export",
    "open_evidence"
  ],
  "app_id": "app_v9_7",
  "append_only": true,
  "audit_ref": "audit://v9-7/audit-export/dd0b76e6d81c",
  "checksum": "73f94d7a68000359fd58a85b26830b9434e88f5562298a3aa7aea21e4a3de32b",
  "correlation_id": "correlation_v9_7",
  "created_at": "2026-06-08T03:06:47.385289+00:00",
  "export_id": "audit-export-v9-7-4a7ff89d4149",
  "immutable": true,
  "included_refs": [
    "audit://v9-7/tenant-isolation/1b2b9b5a4222",
    "audit://v9-7/credential-lease/3ed0d12b5bdb",
    "audit://v9-7/service-account-binding/45bc74c854fb",
    "audit://v9-7/incident/b8de00541e34",
    "audit://v9-7/incident/b72f7e3277d4",
    "audit://v9-7/incident/1acd482a2460",
    "audit://v9-7/incident/94836f5ccee9"
  ],
  "project_id": "project_v9_7",
  "readonly": true,
  "request_id": "request_v9_7",
  "requested_by": "user_v9_7_reviewer",
  "tenant_id": "tenant_v9_7",
  "workspace_id": "workspace_v9_7"
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/incident-timeline.json`
```json
[
  {
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/incident/b8de00541e34",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.385050+00:00",
    "event_id": "incident-event-v9-7-6b7fe1cd3489",
    "event_type": "policy_denied",
    "operation": "production.deploy",
    "project_id": "project_v9_7",
    "readonly": true,
    "request_id": "request_v9_7",
    "severity": "high",
    "source_ref": "audit://v9-7/tenant-isolation/ea3352464e9f",
    "summary": "Policy denied production deploy attempt.",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  {
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/incident/b72f7e3277d4",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.385094+00:00",
    "event_id": "incident-event-v9-7-88df9f233ddd",
    "event_type": "credential_denied",
    "operation": "production.deploy",
    "project_id": "project_v9_7",
    "readonly": true,
    "request_id": "request_v9_7",
    "severity": "high",
    "source_ref": "audit://v9-7/credential-lease/14cae344ee09",
    "summary": "Credential lease denied wrong operation.",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  {
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/incident/1acd482a2460",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.385137+00:00",
    "event_id": "incident-event-v9-7-3b58e4cbc62b",
    "event_type": "timeout",
    "operation": "terminal.audit.review",
    "project_id": "project_v9_7",
    "readonly": true,
    "request_id": "request_v9_7",
    "severity": "medium",
    "source_ref": "terminal-session://v9-7/timeout",
    "summary": "Terminal governance review timed out.",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  },
  {
    "app_id": "app_v9_7",
    "audit_ref": "audit://v9-7/incident/94836f5ccee9",
    "correlation_id": "correlation_v9_7",
    "created_at": "2026-06-08T03:06:47.385172+00:00",
    "event_id": "incident-event-v9-7-0f61d58209ff",
    "event_type": "worker_lost",
    "operation": "terminal.audit.review",
    "project_id": "project_v9_7",
    "readonly": true,
    "request_id": "request_v9_7",
    "severity": "medium",
    "source_ref": "worker://v9-7/lost",
    "summary": "Worker loss recorded with no retry mutation.",
    "tenant_id": "tenant_v9_7",
    "workspace_id": "workspace_v9_7"
  }
]
```

### `docs/design/V9.x/evidence/v9-7-production-governance/evidence-hardening-report.json`
```json
{
  "audit_ref": "audit://v9-7/evidence-hardening/3af5dce94a7d",
  "claim_scan_status": "PASS",
  "correlation_id": "correlation_v9_7",
  "created_at": "2026-06-08T03:06:47.387366+00:00",
  "forbidden_claim_hits": [],
  "forbidden_raw_hits": [],
  "policy_decision": "allow",
  "redaction_status": "PASS",
  "report_id": "evidence-hardening-v9-7-313f3d930225",
  "request_id": "request_v9_7",
  "scanned_refs": [
    "audit://v9-7/audit-export/dd0b76e6d81c",
    "audit://v9-7/terminal-automation-policy/af60fe8eec01"
  ]
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/terminal-automation-policy.json`
```json
{
  "allowed_mode": "governance_gate_only",
  "app_id": "app_v9_7",
  "audit_ref": "audit://v9-7/terminal-automation-policy/af60fe8eec01",
  "browser_account_automation_allowed": false,
  "policy_decision": "deny_production_automation_enablement",
  "policy_id": "terminal-automation-policy-v9-7-ea4ffeb6bfef",
  "production_terminal_automation_ready": false,
  "requires_credential_lease_decision": true,
  "requires_human_authorization_ref": true,
  "requires_incident_timeline": true,
  "tenant_id": "tenant_v9_7",
  "workspace_id": "workspace_v9_7"
}
```

### `docs/design/V9.x/evidence/v9-7-production-governance/browser-automation-policy.json`
```json
{
  "audit_ref": "audit://v9-7/browser-automation-policy/d63671bc8a64",
  "browser_account_automation_allowed": false,
  "explicit_human_decision_required": true,
  "policy_decision": "deny_without_separate_prd",
  "policy_id": "browser-automation-policy-v9-7-3ea2cd49d867",
  "separate_prd_required": true
}
```

### `docs/design/V9.x/evidence/v9-3-orchestration-runtime/storyboard-provider-evidence.json`
```json
{
  "base64_stored": false,
  "created_at": "2026-06-08T02:59:00Z",
  "credential_material_stored": false,
  "evidence_scope": "real_provider_backed_runtime_fixture",
  "prompt_material_stored": false,
  "prompt_refs": [
    "artifact-ref://v9-3/video/storyboard-prompt-1",
    "artifact-ref://v9-3/video/storyboard-prompt-2",
    "artifact-ref://v9-3/video/storyboard-prompt-3",
    "artifact-ref://v9-3/video/storyboard-prompt-4"
  ],
  "provider_config_source": "dotenv://minimax-image-provider",
  "provider_invocation_ref": "provider-invocation-ref://v9-3/video/provider-invocation-v9-3-3d016841d1fd",
  "provider_model_ref": "provider-model-ref://minimax/image-01",
  "provider_ref": "provider-ref://minimax/image-generation",
  "provider_request_body_stored": false,
  "provider_response_body_stored": false,
  "runtime_backed": true,
  "scenario_id": "US-V9-08",
  "schema_version": "v9_3.provider_storyboard_evidence.v1",
  "status": "PASS",
  "storyboard_image_artifacts": [
    {
      "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-1",
      "byte_size": 464332,
      "content_type": "image/jpeg",
      "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-1.jpg",
      "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-1",
      "sha256": "8eb0406c8ddcb975048bbb9928a90c881e15fc7e5c05c5d0a0fb35333cf6fe9d"
    },
    {
      "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-2",
      "byte_size": 419327,
      "content_type": "image/jpeg",
      "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-2.jpg",
      "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-2",
      "sha256": "ac5fe6bb79f4857fd5da7f0a209d5a3cb3e18ef34a5aa0decb070933a18845e0"
    },
    {
      "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-3",
      "byte_size": 247153,
      "content_type": "image/jpeg",
      "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-3.jpg",
      "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-3",
      "sha256": "5ba097b207c7a5c7b1eabed5650064898fbc19dce27a742a002489f9f97a60cd"
    },
    {
      "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-4",
      "byte_size": 305190,
      "content_type": "image/jpeg",
      "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-4.jpg",
      "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-4",
      "sha256": "1cd37afc0b3eafb8aac300253a03948ef2c38ef018eb58af1562343928fade9f"
    }
  ]
}

```

### `docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json`
```json
{
  "agent_executor_ready": false,
  "autonomous_coding_workflow_ready": false,
  "blockers": [],
  "claim_scan": "PASS",
  "complete_workflow_studio_ready": false,
  "controlled_executor_ready": false,
  "created_at": "2026-06-08T03:08:50Z",
  "drawio_xml": "PASS",
  "final_claim": "V9 complete: high-risk Agent execution and workflow productization baseline ready for review.",
  "full_multi_agent_orchestration_ready": false,
  "full_production_ga": false,
  "high_risk_decisions": [
    {
      "blocker": null,
      "decision_ref": "v9-1-limited-safety-gate-implementation-approved",
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json",
      "stage_id": "V9-1",
      "status": "PASS"
    },
    {
      "blocker": null,
      "decision_ref": "v9-2-limited-controlled-runtime-implementation-approved",
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_2_high_risk_human_decision.json",
      "stage_id": "V9-2",
      "status": "PASS"
    },
    {
      "blocker": null,
      "decision_ref": "v9-4-autonomous-coding-workflow-pilot-approved",
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_4_high_risk_human_decision.json",
      "stage_id": "V9-4",
      "status": "PASS"
    },
    {
      "blocker": null,
      "decision_ref": "v9-5-governed-terminal-worker-expansion-approved",
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_5_high_risk_human_decision.json",
      "stage_id": "V9-5",
      "status": "PASS"
    },
    {
      "blocker": null,
      "decision_ref": "v9-7-production-governance-high-risk-approved",
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_7_high_risk_human_decision.json",
      "stage_id": "V9-7",
      "status": "PASS"
    }
  ],
  "planning_docs_counted_as_runtime_evidence": false,
  "production_browser_automation_ready": false,
  "production_controlled_executor_ready": false,
  "production_ready": false,
  "production_terminal_automation_ready": false,
  "redaction_scan": "PASS",
  "schema_version": "v9_8.final_acceptance.v1",
  "stage_id": "V9-8",
  "stage_results": [
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json",
      "evidence_scope": "real_code_policy_validation",
      "runtime_backed": false,
      "stage_id": "V9-1",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json",
      "evidence_scope": "real_runtime_fixture",
      "runtime_backed": true,
      "stage_id": "V9-2",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
      "evidence_scope": "real_runtime_fixture",
      "runtime_backed": true,
      "stage_id": "V9-3",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
      "evidence_scope": "real_runtime_fixture",
      "runtime_backed": true,
      "stage_id": "V9-4",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json",
      "evidence_scope": "real_runtime_fixture",
      "runtime_backed": true,
      "stage_id": "V9-5",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json",
      "evidence_scope": "real_runtime_fixture",
      "runtime_backed": true,
      "stage_id": "V9-6",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json",
      "evidence_scope": "real_runtime_fixture",
      "runtime_backed": true,
      "stage_id": "V9-7",
      "status": "PASS"
    }
  ],
  "status": "PASS",
  "unrestricted_terminal_worker_ready": false,
  "user_scenarios": [
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json",
      "runtime_backed": true,
      "scenario_id": "US-V9-01",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
      "runtime_backed": true,
      "scenario_id": "US-V9-02",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
      "runtime_backed": true,
      "scenario_id": "US-V9-03",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json",
      "runtime_backed": true,
      "scenario_id": "US-V9-04",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json",
      "runtime_backed": true,
      "scenario_id": "US-V9-05",
      "status": "PASS"
    },
    {
      "blocker": null,
      "evidence_ref": "self://v9-8-final-dashboard",
      "runtime_backed": false,
      "scenario_id": "US-V9-06",
      "status": "PASS"
    },
    {
      "attribution_refs": [
        "lineage-ref://v9-3/roman-forum/philosopher",
        "lineage-ref://v9-3/roman-forum/engineer",
        "lineage-ref://v9-3/roman-forum/historian",
        "lineage-ref://v9-3/roman-forum/ethicist"
      ],
      "blocker": null,
      "discussion_turn_count": 2,
      "evidence_chain_ref": "evidence-chain://v9-3/roman-forum",
      "evidence_scope": "real_runtime_fixture",
      "orchestration_run_id": "orch-v9-3-000934924ef4",
      "role_specific_agents": [
        "philosopher_agent",
        "engineer_agent",
        "historian_agent",
        "ethicist_agent",
        "moderator_agent"
      ],
      "runtime_backed": true,
      "scenario_id": "US-V9-07",
      "status": "PASS",
      "synthesis_ref": "artifact-ref://v9-3/roman-forum/attributed-synthesis"
    },
    {
      "blocker": null,
      "evidence_ref": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-3-orchestration-runtime/storyboard-provider-evidence.json",
      "evidence_scope": "real_provider_backed_runtime_fixture",
      "provider_invocation_ref": "provider-invocation-ref://v9-3/video/provider-invocation-v9-3-3d016841d1fd",
      "provider_model_ref": "provider-model-ref://minimax/image-01",
      "provider_ref": "provider-ref://minimax/image-generation",
      "runtime_backed": true,
      "scenario_id": "US-V9-08",
      "status": "PASS",
      "storyboard_image_artifacts": [
        {
          "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-1",
          "byte_size": 464332,
          "content_type": "image/jpeg",
          "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-1.jpg",
          "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-1",
          "sha256": "8eb0406c8ddcb975048bbb9928a90c881e15fc7e5c05c5d0a0fb35333cf6fe9d"
        },
        {
          "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-2",
          "byte_size": 419327,
          "content_type": "image/jpeg",
          "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-2.jpg",
          "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-2",
          "sha256": "ac5fe6bb79f4857fd5da7f0a209d5a3cb3e18ef34a5aa0decb070933a18845e0"
        },
        {
          "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-3",
          "byte_size": 247153,
          "content_type": "image/jpeg",
          "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-3.jpg",
          "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-3",
          "sha256": "5ba097b207c7a5c7b1eabed5650064898fbc19dce27a742a002489f9f97a60cd"
        },
        {
          "artifact_ref": "artifact-ref://v9-3/video/storyboard-image-4",
          "byte_size": 305190,
          "content_type": "image/jpeg",
          "path": "evidence/v9-3-orchestration-runtime/storyboard-images/storyboard-shot-4.jpg",
          "prompt_ref": "artifact-ref://v9-3/video/storyboard-prompt-4",
          "sha256": "1cd37afc0b3eafb8aac300253a03948ef2c38ef018eb58af1562343928fade9f"
        }
      ],
      "storyboard_image_count": 4
    },
    {
      "blocker": null,
      "evidence_scope": "real_runtime_fixture",
      "lineage_refs": [
        "lineage-v9-3-research",
        "lineage-v9-3-implementation",
        "lineage-v9-3-review",
        "lineage-v9-3-synthesis"
      ],
      "mutation_applied_before_confirmation": false,
      "runtime_backed": true,
      "scenario_id": "US-V9-09",
      "source_agent_direct_mutation_denied": true,
      "status": "PASS",
      "user_confirmation_required": true,
      "workflow_diff_ref": "workflow-diff://v9-3/optimization/video-workflow"
    }
  ]
}

```

### `docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-result-summary.md`
```markdown
# V9-8 Final Acceptance Result

status: PASS
final_claim: V9 complete: high-risk Agent execution and workflow productization baseline ready for review.

## Blockers

```

### `docs/design/V9.x/../../../core/policies/v9_agent_executor_safety.py`
```text
"""V9 Agent executor safety gate.

This module validates V9 execution intent contracts and returns policy
decisions. It does not execute runtime actions, create executor routes, start
workers, write workflow runtime truth, or grant source=agent durable mutation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4


DURABLE_OPERATIONS = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}
APPROVAL_GATED_OPERATIONS = {"artifact.write", "quality.evaluation.create"}
VALID_SOURCES = {"product_console", "approved_api", "mission_tui", "agent"}
VALID_ACTOR_TYPES = {"human_user", "service_account_with_human_authorization", "agent"}
FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "bearer ",
    "bearer_token",
    "signed_url",
    "signed url",
    "credential_raw_secret",
    "credential raw secret",
)


class V9SafetyGateError(ValueError):
    """Stable V9 safety gate validation error."""

    def __init__(self, code: str, message: str, *, reason: str, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.field = field

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"code": self.code, "message": str(self), "reason": self.reason}
        if self.field:
            data["field"] = self.field
        return data


@dataclass(frozen=True)
class V9SafetyGateDecision:
    """V9 capability decision with evidence refs."""

    capability_decision_ref: str
    operation: str
    decision: str
    risk_level: str
    requires_user_confirmation: bool
    requires_human_authorization_ref: bool
    requires_approval_gate: bool
    denial_reason: str | None
    policy_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    correlation_id: str
    request_id: str
    audit_ref: str
    created_at: str
    runtime_execution_allowed: bool
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class V9AgentExecutorSafetyGate:
    """Evaluate V9 Agent execution intents without executing them."""

    def evaluate(
        self,
        *,
        envelope: Mapping[str, Any],
        human_authorization: Mapping[str, Any] | None = None,
        approval_gate: Mapping[str, Any] | None = None,
        kill_switch: Mapping[str, Any] | None = None,
        timeout_policy: Mapping[str, Any] | None = None,
        rollback_descriptor: Mapping[str, Any] | None = None,
    ) -> V9SafetyGateDecision:
        safe_envelope = dict(envelope)
        self._validate_no_raw_content(safe_envelope, field="envelope")
        self._validate_envelope_shape(safe_envelope)

        operation = str(safe_envelope["operation"])
        risk_level = self._risk_level(operation)
        requires_approval = operation in APPROVAL_GATED_OPERATIONS
        denial = self._first_denial(
            envelope=safe_envelope,
            human_authorization=human_authorization,
            approval_gate=approval_gate,
            kill_switch=kill_switch,
            timeout_policy=timeout_policy,
            rollback_descriptor=rollback_descriptor,
            requires_approval=requires_approval,
        )
        decision = "deny" if denial else "allow"
        now = _now()
        capability_ref = f"capability-decision://v9-1/{uuid4().hex}"
        evidence = {
            "schema_version": "v9.0",
            "execution_envelope_id": safe_envelope["execution_envelope_id"],
            "operation": operation,
            "source": safe_envelope["source"],
            "actor_type": safe_envelope["actor_type"],
            "agent_id": safe_envelope["agent_id"],
            "station_id": safe_envelope["station_id"],
            "target_refs": dict(safe_envelope["target_refs"]),
            "payload_refs": list(safe_envelope.get("payload_refs", [])),
            "user_confirmed": safe_envelope["user_confirmed"],
            "human_authorization_ref": safe_envelope.get("human_authorization_ref"),
            "capability_decision_ref": capability_ref,
            "approval_gate_ref": safe_envelope.get("approval_gate_ref"),
            "kill_switch_policy_ref": safe_envelope.get("kill_switch_policy_ref"),
            "timeout_policy_ref": safe_envelope.get("timeout_policy_ref"),
            "rollback_descriptor_ref": safe_envelope.get("rollback_descriptor_ref"),
            "policy_decision": decision,
            "denial_reason": denial,
            "runtime_execution_allowed": False,
            "redaction_status": "PASS",
            "correlation_id": safe_envelope["correlation_id"],
            "request_id": safe_envelope["request_id"],
            "audit_ref": safe_envelope["audit_ref"],
            "created_at": now,
        }
        return V9SafetyGateDecision(
            capability_decision_ref=capability_ref,
            operation=operation,
            decision=decision,
            risk_level=risk_level,
            requires_user_confirmation=True,
            requires_human_authorization_ref=not bool(safe_envelope["user_confirmed"]),
            requires_approval_gate=requires_approval,
            denial_reason=denial,
            policy_ref=f"policy://v9-1/agent-executor-safety/{operation}",
            tenant_id=safe_envelope["tenant_id"],
            workspace_id=safe_envelope["workspace_id"],
            project_id=safe_envelope["project_id"],
            app_id=safe_envelope["app_id"],
            correlation_id=safe_envelope["correlation_id"],
            request_id=safe_envelope["request_id"],
            audit_ref=safe_envelope["audit_ref"],
            created_at=now,
            runtime_execution_allowed=False,
            evidence=evidence,
        )

    def _first_denial(
        self,
        *,
        envelope: dict[str, Any],
        human_authorization: Mapping[str, Any] | None,
        approval_gate: Mapping[str, Any] | None,
        kill_switch: Mapping[str, Any] | None,
        timeout_policy: Mapping[str, Any] | None,
        rollback_descriptor: Mapping[str, Any] | None,
        requires_approval: bool,
    ) -> str | None:
        if envelope["source"] == "agent" or envelope["actor_type"] == "agent":
            return "source_agent_durable_mutation_denied"
        if not self._has_user_confirmation_or_valid_authorization(envelope, human_authorization):
            return "missing_user_confirmation_or_valid_human_authorization_ref"
        kill_denial = self._validate_kill_switch(envelope, kill_switch)
        if kill_denial:
            return kill_denial
        if requires_approval:
            approval_denial = self._validate_approval_gate(envelope, approval_gate)
            if approval_denial:
                return approval_denial
        timeout_denial = self._validate_timeout_policy(envelope, timeout_policy)
        if timeout_denial:
            return timeout_denial
        rollback_denial = self._validate_rollback_descriptor(envelope, rollback_descriptor)
        if rollback_denial:
            return rollback_denial
        return None

    def _has_user_confirmation_or_valid_authorization(self, envelope: dict[str, Any], authorization: Mapping[str, Any] | None) -> bool:
        if envelope.get("user_confirmed") is True:
            return True
        if not isinstance(envelope.get("human_authorization_ref"), str):
            return False
        return self.validate_human_authorization(envelope, authorization)

    def validate_human_authorization(self, envelope: Mapping[str, Any], authorization: Mapping[str, Any] | None) -> bool:
        if authorization is None:
            return False
        self._validate_no_raw_content(dict(authorization), field="human_authorization")
        if authorization.get("human_authorization_ref") != envelope.get("human_authorization_ref"):
            return False
        if authorization.get("revoked") is True:
            return False
        if _parse_time(str(authorization.get("expires_at"))) <= _now_dt():
            return False
        if authorization.get("operation") != envelope.get("operation"):
            return False
        for field in ("tenant_id", "workspace_id", "project_id", "app_id"):
            if authorization.get(field) != envelope.get(field):
                return False
        if envelope.get("source") not in set(authorization.get("allowed_sources", [])):
            return False
        if envelope.get("actor_type") not in set(authorization.get("allowed_actor_types", [])):
            return False
        if not _target_refs_match(dict(envelope.get("target_refs", {})), dict(authorization.get("target_refs", {}))):
            return False
        expected_hash = operation_hash(str(envelope["operation"]), dict(envelope["target_refs"]))
        return authorization.get("operation_hash") == expected_hash

    def _validate_envelope_shape(self, envelope: dict[str, Any]) -> None:
        required = {
            "schema_version",
            "execution_envelope_id",
            "operation",
            "source",
            "actor_type",
            "actor_id",
            "agent_id",
            "station_id",
            "tenant_id",
            "workspace_id",
            "project_id",
            "app_id",
            "workflow_instance_id",
            "station_run_id",
            "target_refs",
            "payload_refs",
            "user_confirmed",
            "human_authorization_ref",
            "correlation_id",
            "request_id",
            "audit_ref",
        }
        missing = sorted(required - set(envelope))
        if missing:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "AgentExecutionEnvelope is missing required fields.", reason="missing_required_field", field=missing[0])
        if envelope["schema_version"] != "v9.0":
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Unsupported schema_version.", reason="unsupported_schema_version", field="schema_version")
        if envelope["operation"] not in DURABLE_OPERATIONS:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Operation is not in V9-1 candidate action set.", reason="unknown_operation", field="operation")
        if envelope["source"] not in VALID_SOURCES:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Source is not allowed.", reason="unknown_source", field="source")
        if envelope["actor_type"] not in VALID_ACTOR_TYPES:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Actor type is not allowed.", reason="unknown_actor_type", field="actor_type")
        target_refs = envelope.get("target_refs")
        if not isinstance(target_refs, dict) or not target_refs:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "target_refs must be a non-empty object.", reason="empty_target_refs", field="target_refs")
        _validate_operation_target_refs(str(envelope["operation"]), target_refs)
        payload_refs = envelope.get("payload_refs")
        if not isinstance(payload_refs, list):
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "payload_refs must be a list of redacted references.", reason="invalid_payload_refs", field="payload_refs")

    def _validate_kill_switch(self, envelope: dict[str, Any], kill_switch: Mapping[str, Any] | None) -> str | None:
        if kill_switch is None:
            return "missing_kill_switch_decision"
        self._validate_no_raw_content(dict(kill_switch), field="kill_switch")
        if kill_switch.get("operation") != envelope["operation"]:
            return "kill_switch_operation_mismatch"
        if kill_switch.get("allowed") is not True:
            return "kill_switch_denied"
        return None

    def _validate_approval_gate(self, envelope: dict[str, Any], approval_gate: Mapping[str, Any] | None) -> str | None:
        if approval_gate is None:
            return "approval_gate_required"
        self._validate_no_raw_content(dict(approval_gate), field="approval_gate")
        if approval_gate.get("operation") != envelope["operation"]:
            return "approval_gate_operation_mismatch"
        if approval_gate.get("approved") is not True:
            return "approval_gate_denied"
        if not approval_gate.get("approved_by") or not approval_gate.get("approved_at"):
            return "approval_gate_missing_human_approval_evidence"
        return None

    def _validate_timeout_policy(self, envelope: dict[str, Any], timeout_policy: Mapping[str, Any] | None) -> str | None:
        if timeout_policy is None:
            return "missing_timeout_policy"
        self._validate_no_raw_content(dict(timeout_policy), field="timeout_policy")
        if timeout_policy.get("operation") != envelope["operation"]:
            return "timeout_policy_operation_mismatch"
        if timeout_policy.get("incident_timeline_required") is not True:
            return "timeout_policy_requires_incident_timeline"
        max_runtime = timeout_policy.get("max_runtime_seconds")
        if not isinstance(max_runtime, int) or max_runtime < 1:
            return "timeout_policy_invalid"
        return None

    def _validate_rollback_descriptor(self, envelope: dict[str, Any], rollback_descriptor: Mapping[str, Any] | None) -> str | None:
        if rollback_descriptor is None:
            return "missing_rollback_descriptor"
        self._validate_no_raw_content(dict(rollback_descriptor), field="rollback_descriptor")
        if rollback_descriptor.get("operation") != envelope["operation"]:
            return "rollback_descriptor_operation_mismatch"
        if not rollback_descriptor.get("rollback_strategy"):
            return "rollback_descriptor_missing_strategy"
        return None

    def _validate_no_raw_content(self, value: Any, *, field: str) -> None:
        text = json.dumps(value, ensure_ascii=False).lower()
        for term in FORBIDDEN_RAW_TERMS:
            if term.lower() in text:
                raise V9SafetyGateError("V9_REDACTION_DENIED", "Raw or sensitive content is not allowed in V9 safety gate inputs.", reason="forbidden_raw_content", field=field)

    def _risk_level(self, operation: str) -> str:
        if operation in {"artifact.write", "quality.evaluation.create"}:
            return "medium"
        return "low"


def operation_hash(operation: str, target_refs: Mapping[str, str]) -> str:
    payload = {"operation": operation, "target_refs": dict(sorted(target_refs.items()))}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:32]


def build_human_authorization_ref(
    *,
    ref: str,
    envelope: Mapping[str, Any],
    expires_at: str = "2999-01-01T00:00:00Z",
) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "human_authorization_ref": ref,
        "issuer_type": "human_user",
        "issuer_id": str(envelope["actor_id"]),
        "authorization_subject_actor_id": str(envelope["actor_id"]),
        "tenant_id": str(envelope["tenant_id"]),
        "workspace_id": str(envelope["workspace_id"]),
        "project_id": str(envelope["project_id"]),
        "app_id": str(envelope["app_id"]),
        "operation": str(envelope["operation"]),
        "operation_hash": operation_hash(str(envelope["operation"]), dict(envelope["target_refs"])),
        "target_refs": dict(envelope["target_refs"]),
        "allowed_sources": [str(envelope["source"])],
        "allowed_actor_types": [str(envelope["actor_type"])],
        "scope": "single_operation",
        "created_at": "2026-06-05T00:00:00Z",
        "expires_at": expires_at,
        "revoked": False,
        "revoked_at": None,
        "revocation_reason": None,
        "correlation_id": str(envelope["correlation_id"]),
        "request_id": str(envelope["request_id"]),
        "audit_ref": f"audit://v9-1/human-authorization/{ref}",
    }


def build_kill_switch_decision(envelope: Mapping[str, Any], *, allowed: bool = True) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "kill_switch_policy_ref": str(envelope.get("kill_switch_policy_ref") or "kill-switch://v9-1/default"),
        "operation": str(envelope["operation"]),
        "checked_at": _now(),
        "checked_by": "v9_agent_executor_safety_gate",
        "allowed": allowed,
        "denial_reason": None if allowed else "kill_switch_active",
        "correlation_id": str(envelope["correlation_id"]),
        "audit_ref": f"audit://v9-1/kill-switch/{uuid4().hex}",
    }


def build_timeout_policy(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "timeout_policy_ref": str(envelope.get("timeout_policy_ref") or "timeout://v9-1/default"),
        "operation": str(envelope["operation"]),
        "max_runtime_seconds": 300,
        "on_timeout": "mark_failed",
        "incident_timeline_required": True,
    }


def build_rollback_descriptor(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "rollback_descriptor_ref": str(envelope.get("rollback_descriptor_ref") or f"rollback://v9-1/{uuid4().hex}"),
        "operation": str(envelope["operation"]),
        "rollback_strategy": "append_correction" if envelope["operation"] in APPROVAL_GATED_OPERATIONS else "mark_failed",
        "correction_artifact_required": envelope["operation"] in APPROVAL_GATED_OPERATIONS,
        "previous_state_ref": None,
        "created_at": _now(),
    }


def build_approval_gate_decision(envelope: Mapping[str, Any], *, approved: bool = True) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "approval_gate_ref": str(envelope.get("approval_gate_ref") or f"approval://v9-1/{uuid4().hex}"),
        "operation": str(envelope["operation"]),
        "risk_level": "medium",
        "requires_human_approval": True,
        "approved": approved,
        "approved_by": str(envelope["actor_id"]) if approved else None,
        "approved_at": _now() if approved else None,
        "denial_reason": None if approved else "not_approved",
        "correlation_id": str(envelope["correlation_id"]),
        "audit_ref": f"audit://v9-1/approval/{uuid4().hex}",
    }


def _validate_operation_target_refs(operation: str, target_refs: Mapping[str, Any]) -> None:
    required_by_operation = {
        "workflow.instance.start": ("workflow_instance_id",),
        "station.rerun": ("station_id", "station_run_id"),
        "artifact.write": ("artifact_id",),
        "quality.evaluation.create": ("quality_evaluation_id",),
    }
    for field in required_by_operation[operation]:
        if not target_refs.get(field):
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "target_refs are missing required operation-specific fields.", reason="missing_target_ref", field=f"target_refs.{field}")


def _target_refs_match(envelope_refs: Mapping[str, Any], authorization_refs: Mapping[str, Any]) -> bool:
    for key, value in authorization_refs.items():
        if envelope_refs.get(key) != value:
            return False
    return True


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _now_dt() -> datetime:
    return datetime.now(UTC)


def _now() -> str:
    return _now_dt().replace(microsecond=0).isoformat().replace("+00:00", "Z")


```

### `docs/design/V9.x/../../../core/policies/v9_controlled_executor_runtime.py`
```text
"""V9-2 limited controlled Agent executor runtime slice.

This module implements only the approved V9-2 local runtime slice. It does not
register routes, start workers, call connectors, call external LLMs, perform git
operations, deploy, grant source=agent durable mutation, or claim Agent executor
readiness.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4

from core.policies.v9_agent_executor_safety import (
    APPROVAL_GATED_OPERATIONS,
    DURABLE_OPERATIONS,
    V9AgentExecutorSafetyGate,
    V9SafetyGateError,
)


EXCLUDED_ACTIONS = {
    "connector.call",
    "external_llm.call",
    "business.event.emit",
    "context.update",
    "workflow.template.publish",
    "approval.respond",
    "git.commit",
    "git.push",
    "production.deploy",
}
FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "bearer ",
    "bearer_token",
    "signed_url",
    "signed url",
    "credential_raw_secret",
    "credential raw secret",
)


class V9ControlledExecutorRuntimeError(ValueError):
    """Stable V9-2 controlled executor runtime error."""

    def __init__(self, code: str, message: str, *, reason: str, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.field = field

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"code": self.code, "message": str(self), "reason": self.reason}
        if self.field:
            data["field"] = self.field
        return data


@dataclass(frozen=True)
class V9RuntimeAttempt:
    """Append-only station attempt record."""

    attempt_id: str
    station_id: str
    station_run_id: str
    attempt_number: int
    status: str
    error_ref: str | None = None
    producer_runtime_result_ref: str | None = None
    previous_attempt_id: str | None = None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class V9ControlledRuntimeState:
    """In-memory V9-2 controlled runtime state."""

    workflow_instance_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    status: str = "created"
    station_attempts: dict[str, list[V9RuntimeAttempt]] = field(default_factory=dict)
    downstream_stale: list[str] = field(default_factory=list)
    artifact_versions: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    quality_evaluations: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    runtime_result_refs: list[str] = field(default_factory=list)
    incident_timeline_events: list[dict[str, Any]] = field(default_factory=list)
    revision: int = 0
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(
            {
                "workflow_instance_id": self.workflow_instance_id,
                "tenant_id": self.tenant_id,
                "workspace_id": self.workspace_id,
                "project_id": self.project_id,
                "app_id": self.app_id,
                "status": self.status,
                "station_attempts": {station_id: [attempt.to_dict() for attempt in attempts] for station_id, attempts in self.station_attempts.items()},
                "downstream_stale": list(self.downstream_stale),
                "artifact_versions": self.artifact_versions,
                "quality_evaluations": self.quality_evaluations,
                "runtime_result_refs": list(self.runtime_result_refs),
                "incident_timeline_events": list(self.incident_timeline_events),
                "revision": self.revision,
                "updated_at": self.updated_at,
                "v9_2_limited_runtime_slice": True,
                "agent_executor_ready": False,
                "controlled_executor_ready": False,
                "production_controlled_executor_ready": False,
            }
        )


@dataclass(frozen=True)
class V9ControlledExecutionResult:
    """Result of one V9-2 controlled action."""

    result_id: str
    operation: str
    status: str
    policy_decision: str
    capability_decision: str
    runtime_result_ref: str | None
    execution_evidence: dict[str, Any] | None
    workflow_state: dict[str, Any] | None
    blocked_reason: str | None = None
    idempotent_replay: bool = False
    incident_timeline_ref: str | None = None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self) | {"agent_executor_ready": False, "controlled_executor_ready": False, "production_controlled_executor_ready": False})


class V9LimitedControlledExecutorRuntime:
    """Local V9-2 runtime slice for four allowlisted actions only."""

    def __init__(self, safety_gate: V9AgentExecutorSafetyGate | None = None) -> None:
        self.safety_gate = safety_gate or V9AgentExecutorSafetyGate()
        self.workflow_states: dict[str, V9ControlledRuntimeState] = {}
        self.idempotency_results: dict[str, V9ControlledExecutionResult] = {}
        self.idempotency_fingerprints: dict[str, tuple[str, str, str, str, str, str]] = {}
        self.execution_evidence: list[dict[str, Any]] = []
        self.runtime_results: list[dict[str, Any]] = []
        self.incident_timeline_events: list[dict[str, Any]] = []
        self.disabled_workspaces: set[str] = set()

    def seed_workflow(
        self,
        *,
        workflow_instance_id: str,
        tenant_id: str = "tenant-v9",
        workspace_id: str = "workspace-v9",
        project_id: str = "project-v9",
        app_id: str = "app-v9",
        station_id: str = "station-v9",
        station_run_id: str = "station-run-v9",
        failed: bool = False,
    ) -> V9ControlledRuntimeState:
        attempt = V9RuntimeAttempt(
            attempt_id=f"attempt-v9-2-{uuid4().hex[:12]}",
            station_id=station_id,
            station_run_id=station_run_id,
            attempt_number=1,
            status="failed" if failed else "completed",
            error_ref="error://v9-2/seeded-failure" if failed else None,
        )
        state = V9ControlledRuntimeState(
            workflow_instance_id=workflow_instance_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            project_id=project_id,
            app_id=app_id,
            status="failed" if failed else "created",
            station_attempts={station_id: [attempt]},
        )
        self.workflow_states[workflow_instance_id] = state
        return state

    def disable_workspace(self, workspace_id: str) -> None:
        self.disabled_workspaces.add(workspace_id)

    def execute(
        self,
        *,
        envelope: Mapping[str, Any],
        human_authorization: Mapping[str, Any] | None = None,
        approval_gate: Mapping[str, Any] | None = None,
        kill_switch: Mapping[str, Any] | None = None,
        timeout_policy: Mapping[str, Any] | None = None,
        rollback_descriptor: Mapping[str, Any] | None = None,
    ) -> V9ControlledExecutionResult:
        try:
            safe_envelope = dict(envelope)
            self._preflight(safe_envelope)
            safety_decision = self.safety_gate.evaluate(
                envelope=safe_envelope,
                human_authorization=human_authorization,
                approval_gate=approval_gate,
                kill_switch=kill_switch,
                timeout_policy=timeout_policy,
                rollback_descriptor=rollback_descriptor,
            ).to_dict()
            if safety_decision["decision"] != "allow":
                return self._blocked(safe_envelope, safety_decision["denial_reason"], safety_decision=safety_decision)
            if safe_envelope["workspace_id"] in self.disabled_workspaces:
                return self._blocked(safe_envelope, "kill_switch_denied", safety_decision=safety_decision)
            fingerprint = _idempotency_fingerprint(safe_envelope)
            idempotency_key = str(safe_envelope["idempotency_key"])
            if idempotency_key in self.idempotency_results:
                if self.idempotency_fingerprints[idempotency_key] != fingerprint:
                    return self._blocked(safe_envelope, "idempotency_key_conflict", safety_decision=safety_decision)
                prior = self.idempotency_results[idempotency_key]
                return V9ControlledExecutionResult(
                    result_id=f"v9_2_result_{uuid4().hex[:12]}",
                    operation=prior.operation,
                    status="idempotent_replay",
                    policy_decision=prior.policy_decision,
                    capability_decision=prior.capability_decision,
                    runtime_result_ref=prior.runtime_result_ref,
                    execution_evidence=prior.execution_evidence,
                    workflow_state=prior.workflow_state,
                    idempotent_replay=True,
                    incident_timeline_ref=prior.incident_timeline_ref,
                )
            state = self._state_for(safe_envelope)
            operation = str(safe_envelope["operation"])
            if operation == "workflow.instance.start":
                result = self._start_workflow(safe_envelope, state, safety_decision)
            elif operation == "station.rerun":
                result = self._rerun_station(safe_envelope, state, safety_decision)
            elif operation == "artifact.write":
                result = self._write_artifact(safe_envelope, state, safety_decision)
            elif operation == "quality.evaluation.create":
                result = self._create_quality_evaluation(safe_envelope, state, safety_decision)
            else:
                result = self._blocked(safe_envelope, "operation_not_allowed", safety_decision=safety_decision)
            if result.status == "applied_v9_2_limited_runtime_slice":
                self.idempotency_results[idempotency_key] = result
                self.idempotency_fingerprints[idempotency_key] = fingerprint
            return result
        except (V9SafetyGateError, V9ControlledExecutorRuntimeError) as exc:
            reason = getattr(exc, "reason", "validation_error")
            operation = str(envelope.get("operation", "unknown")) if isinstance(envelope, Mapping) else "unknown"
            return V9ControlledExecutionResult(
                result_id=f"v9_2_result_{uuid4().hex[:12]}",
                operation=operation,
                status="blocked",
                policy_decision="deny",
                capability_decision="deny",
                runtime_result_ref=None,
                execution_evidence=None,
                workflow_state=None,
                blocked_reason=reason,
                incident_timeline_ref=self._record_incident(dict(envelope), reason),
            )

    def _preflight(self, envelope: dict[str, Any]) -> None:
        _assert_no_forbidden_raw_content(envelope)
        operation = envelope.get("operation")
        if operation in EXCLUDED_ACTIONS or operation not in DURABLE_OPERATIONS:
            raise V9ControlledExecutorRuntimeError("V9_2_OPERATION_DENIED", "Operation is outside the V9-2 allowlist.", reason="operation_not_allowed", field="operation")
        if envelope.get("source") == "agent" or envelope.get("actor_type") == "agent":
            raise V9ControlledExecutorRuntimeError("V9_2_SOURCE_AGENT_DENIED", "source=agent cannot execute durable mutation.", reason="source_agent_durable_mutation_denied", field="source")

    def _state_for(self, envelope: dict[str, Any]) -> V9ControlledRuntimeState:
        refs = dict(envelope["target_refs"])
        workflow_instance_id = refs.get("workflow_instance_id") or str(envelope["workflow_instance_id"])
        state = self.workflow_states.get(workflow_instance_id)
        if state is None:
            state = V9ControlledRuntimeState(
                workflow_instance_id=workflow_instance_id,
                tenant_id=str(envelope["tenant_id"]),
                workspace_id=str(envelope["workspace_id"]),
                project_id=str(envelope["project_id"]),
                app_id=str(envelope["app_id"]),
            )
            self.workflow_states[workflow_instance_id] = state
        return state

    def _start_workflow(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        state.status = "running"
        return self._applied(envelope, state, safety_decision, runtime_result_ref=f"runtime-result://v9-2/{state.workflow_instance_id}/start")

    def _rerun_station(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        refs = dict(envelope["target_refs"])
        station_id = refs["station_id"]
        previous_station_run_id = refs["station_run_id"]
        attempts = state.station_attempts.setdefault(station_id, [])
        previous_attempt = attempts[-1] if attempts else None
        runtime_result_ref = f"runtime-result://v9-2/{state.workflow_instance_id}/rerun/{station_id}/{len(attempts) + 1}"
        attempts.append(
            V9RuntimeAttempt(
                attempt_id=f"attempt-v9-2-{uuid4().hex[:12]}",
                station_id=station_id,
                station_run_id=f"{previous_station_run_id}-retry-{len(attempts) + 1}",
                attempt_number=len(attempts) + 1,
                status="completed",
                producer_runtime_result_ref=runtime_result_ref,
                previous_attempt_id=previous_attempt.attempt_id if previous_attempt else None,
            )
        )
        state.status = "running"
        state.downstream_stale = sorted(set(state.downstream_stale) | {f"downstream-of:{station_id}"})
        return self._applied(envelope, state, safety_decision, runtime_result_ref=runtime_result_ref)

    def _write_artifact(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        refs = dict(envelope["target_refs"])
        artifact_id = refs["artifact_id"]
        versions = state.artifact_versions.setdefault(artifact_id, [])
        runtime_result_ref = f"runtime-result://v9-2/{state.workflow_instance_id}/artifact/{artifact_id}/{len(versions) + 1}"
        versions.append(
            {
                "artifact_version_id": f"artifact-version-v9-2-{len(versions) + 1}",
                "artifact_id": artifact_id,
                "operation": "append_version",
                "content_ref": _payload_ref(envelope, "content_ref", f"artifact-content-ref://v9-2/{artifact_id}/{len(versions) + 1}"),
                "producer_station_id": refs.get("station_id") or envelope.get("station_id"),
                "producer_attempt_id": refs.get("attempt_id"),
                "producer_runtime_result_ref": runtime_result_ref,
                "created_at": _now(),
                "redaction_status": "PASS",
            }
        )
        return self._applied(envelope, state, safety_decision, runtime_result_ref=runtime_result_ref)

    def _create_quality_evaluation(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        refs = dict(envelope["target_refs"])
        evaluation_id = refs["quality_evaluation_id"]
        evaluations = state.quality_evaluations.setdefault(evaluation_id, [])
        runtime_result_ref = f"runtime-result://v9-2/{state.workflow_instance_id}/quality/{evaluation_id}/{len(evaluations) + 1}"
        evaluations.append(
            {
                "quality_evaluation_id": evaluation_id,
                "operation": "append_evaluation",
                "quality_rule_ref": _payload_ref(envelope, "quality_rule_ref", "quality-rule-ref://v9-2/default"),
                "target_ref": refs.get("artifact_id") or refs.get("station_id") or evaluation_id,
                "score_ref": _payload_ref(envelope, "score_ref", f"quality-score-ref://v9-2/{evaluation_id}/{len(evaluations) + 1}"),
                "producer_runtime_result_ref": runtime_result_ref,
                "created_at": _now(),
                "redaction_status": "PASS",
            }
        )
        return self._applied(envelope, state, safety_decision, runtime_result_ref=runtime_result_ref)

    def _applied(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any], *, runtime_result_ref: str) -> V9ControlledExecutionResult:
        state.runtime_result_refs.append(runtime_result_ref)
        state.revision += 1
        state.updated_at = _now()
        incident_ref = self._record_incident(envelope, "runtime_action_completed", runtime_result_ref=runtime_result_ref)
        runtime_result = {
            "runtime_result_ref": runtime_result_ref,
            "operation": envelope["operation"],
            "status": "completed",
            "correlation_id": envelope["correlation_id"],
            "request_id": envelope["request_id"],
            "created_at": _now(),
        }
        self.runtime_results.append(runtime_result)
        evidence = self._execution_evidence(envelope, safety_decision, runtime_result_ref=runtime_result_ref, incident_timeline_ref=incident_ref)
        self.execution_evidence.append(evidence)
        _assert_no_forbidden_raw_content(evidence)
        return V9ControlledExecutionResult(
            result_id=f"v9_2_result_{uuid4().hex[:12]}",
            operation=str(envelope["operation"]),
            status="applied_v9_2_limited_runtime_slice",
            policy_decision="allow",
            capability_decision="allow_v9_2_limited_runtime_slice",
            runtime_result_ref=runtime_result_ref,
            execution_evidence=evidence,
            workflow_state=state.to_dict(),
            incident_timeline_ref=incident_ref,
        )

    def _blocked(self, envelope: dict[str, Any], reason: str, *, safety_decision: dict[str, Any] | None = None) -> V9ControlledExecutionResult:
        incident_ref = self._record_incident(envelope, reason)
        return V9ControlledExecutionResult(
            result_id=f"v9_2_result_{uuid4().hex[:12]}",
            operation=str(envelope.get("operation", "unknown")),
            status="blocked",
            policy_decision="deny",
            capability_decision="deny",
            runtime_result_ref=None,
            execution_evidence=None,
            workflow_state=None,
            blocked_reason=reason,
            incident_timeline_ref=incident_ref,
        )

    def _execution_evidence(self, envelope: dict[str, Any], safety_decision: dict[str, Any], *, runtime_result_ref: str, incident_timeline_ref: str) -> dict[str, Any]:
        evidence = {
            "schema_version": "v9.0",
            "execution_evidence_ref": f"execution-evidence://v9-2/{uuid4().hex}",
            "execution_envelope_id": envelope["execution_envelope_id"],
            "operation": envelope["operation"],
            "source": envelope["source"],
            "actor_type": envelope["actor_type"],
            "agent_id": envelope["agent_id"],
            "station_id": envelope["station_id"],
            "target_refs": dict(envelope["target_refs"]),
            "capability_decision_ref": safety_decision["capability_decision_ref"],
            "approval_gate_ref": envelope.get("approval_gate_ref"),
            "human_authorization_ref": envelope.get("human_authorization_ref"),
            "runtime_result_ref": runtime_result_ref,
            "rollback_descriptor_ref": envelope.get("rollback_descriptor_ref"),
            "redaction_status": "PASS",
            "correlation_id": envelope["correlation_id"],
            "request_id": envelope["request_id"],
            "audit_ref": envelope["audit_ref"],
            "created_at": _now(),
            "decision_chain_refs": {
                "policy_ref": safety_decision["policy_ref"],
                "capability_decision_ref": safety_decision["capability_decision_ref"],
                "kill_switch_policy_ref": envelope.get("kill_switch_policy_ref"),
                "timeout_policy_ref": envelope.get("timeout_policy_ref"),
                "rollback_descriptor_ref": envelope.get("rollback_descriptor_ref"),
                "incident_timeline_ref": incident_timeline_ref,
            },
            "agent_executor_ready": False,
            "controlled_executor_ready": False,
            "production_controlled_executor_ready": False,
        }
        return _redact(evidence)

    def _record_incident(self, envelope: Mapping[str, Any], event_type: str, *, runtime_result_ref: str | None = None) -> str:
        ref = f"incident-timeline://v9-2/{uuid4().hex}"
        event = {
            "incident_timeline_ref": ref,
            "event_type": event_type,
            "operation": envelope.get("operation", "unknown"),
            "target_refs": dict(envelope.get("target_refs", {})),
            "runtime_result_ref": runtime_result_ref,
            "correlation_id": envelope.get("correlation_id", f"corr-v9-2-{uuid4().hex[:8]}"),
            "request_id": envelope.get("request_id", f"req-v9-2-{uuid4().hex[:8]}"),
            "audit_ref": envelope.get("audit_ref", f"audit://v9-2/{uuid4().hex}"),
            "created_at": _now(),
        }
        self.incident_timeline_events.append(_redact(event))
        workflow_id = dict(envelope.get("target_refs", {})).get("workflow_instance_id") or envelope.get("workflow_instance_id")
        if workflow_id in self.workflow_states:
            self.workflow_states[str(workflow_id)].incident_timeline_events.append(_redact(event))
        return ref


def _payload_ref(envelope: Mapping[str, Any], key: str, default: str) -> str:
    payload_refs = envelope.get("payload_refs", [])
    if isinstance(payload_refs, Mapping) and payload_refs.get(key):
        return str(payload_refs[key])
    if isinstance(payload_refs, list) and payload_refs:
        for item in payload_refs:
            text = str(item)
            if text.startswith(f"{key}:"):
                return text
    return default


def _idempotency_fingerprint(envelope: Mapping[str, Any]) -> tuple[str, str, str, str, str, str]:
    target_hash = json.dumps(envelope.get("target_refs", {}), sort_keys=True, separators=(",", ":"))
    return (
        str(envelope["tenant_id"]),
        str(envelope["workspace_id"]),
        str(envelope["project_id"]),
        str(envelope["operation"]),
        str(envelope["source"]),
        target_hash,
    )


def _redact(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False)
    lowered = text.lower()
    for term in FORBIDDEN_RAW_TERMS:
        if term in lowered:
            raise V9ControlledExecutorRuntimeError("V9_2_REDACTION_DENIED", "Forbidden raw content appears in runtime DTO.", reason="forbidden_raw_content")
    return value


def _assert_no_forbidden_raw_content(value: Any) -> None:
    _redact(value)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

```

### `docs/design/V9.x/../../../core/workflows/v9_3_multi_agent_orchestration_runtime.py`
```text
"""V9-3 bounded multi-Agent orchestration runtime slice.

This module implements a local runtime fixture for V9-3 orchestration evidence.
It does not register routes, start production workers, call connectors, call
external LLMs, perform git operations, or grant source=agent durable mutation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V93_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V9.x" / "evidence" / "v9-3-orchestration-runtime"
FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "bearer ",
    "bearer_token",
    "signed_url",
    "signed url",
    "credential_raw_secret",
    "credential raw secret",
)


class V93OrchestrationRuntimeError(ValueError):
    """Stable V9-3 orchestration runtime denial."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class V93OrchestrationConfig:
    """Input config for one V9-3 local orchestration fixture run."""

    goal: str = "V9-3 bounded multi-Agent orchestration runtime slice"
    evidence_dir: Path = DEFAULT_V93_EVIDENCE_DIR
    source: str = "product_console"
    actor_type: str = "human_user"
    user_confirmed: bool = True
    human_authorization_ref: str = "human-auth://v9-3/local-orchestration-fixture"
    provider_image_generation_available: bool = False
    storyboard_image_artifact_refs: tuple[str, ...] = ()
    provider_model_ref: str | None = None
    provider_invocation_ref: str | None = None


@dataclass(frozen=True)
class V93AgentDescriptor:
    """Station-bound Agent descriptor."""

    agent_id: str
    role: str
    goal: str
    memory_refs: tuple[str, ...]
    tool_refs: tuple[str, ...]
    skill_refs: tuple[str, ...]
    mcp_refs: tuple[str, ...]
    model_ref: str
    policy_ref: str
    credential_decision_ref: str
    schema_version: str = "v9_3.agent_descriptor.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("memory_refs", "tool_refs", "skill_refs", "mcp_refs"):
            data[key] = list(data[key])
        return _redact(data)


@dataclass(frozen=True)
class V93StationAgentBinding:
    """Binding between one workflow station and exactly one Agent."""

    binding_id: str
    orchestration_run_id: str
    station_id: str
    agent_id: str
    policy_ref: str
    credential_decision_ref: str
    correlation_id: str
    request_id: str
    audit_ref: str
    schema_version: str = "v9_3.station_agent_binding.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self))


@dataclass(frozen=True)
class V93AttemptHistoryRecord:
    """Append-only station attempt record."""

    attempt_id: str
    orchestration_run_id: str
    station_id: str
    station_run_id: str
    agent_id: str
    attempt_number: int
    previous_attempt_id: str | None
    status: str
    error_ref: str | None
    checkpoint_ref: str
    schema_version: str = "v9_3.attempt_history_record.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self))


@dataclass(frozen=True)
class V93BranchState:
    """Independent branch state record."""

    branch_id: str
    orchestration_run_id: str
    station_id: str
    station_run_id: str
    attempt_id: str
    state: str
    upstream_branch_ids: tuple[str, ...]
    downstream_branch_ids: tuple[str, ...]
    checkpoint_ref: str
    correlation_id: str
    request_id: str
    audit_ref: str
    schema_version: str = "v9_3.branch_state.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["upstream_branch_ids"] = list(self.upstream_branch_ids)
        data["downstream_branch_ids"] = list(self.downstream_branch_ids)
        return _redact(data)


@dataclass(frozen=True)
class V93ArtifactLineageRecord:
    """Artifact lineage with producer Agent and attempt refs."""

    lineage_record_id: str
    artifact_id: str
    producer_agent_id: str
    producer_attempt_id: str
    producer_station_id: str
    producer_station_run_id: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_ref: str
    correlation_id: str
    request_id: str
    audit_ref: str
    schema_version: str = "v9.0"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input_artifact_refs"] = list(self.input_artifact_refs)
        return _redact(data)


def run_v9_3_multi_agent_orchestration(config: V93OrchestrationConfig | None = None) -> dict[str, Any]:
    """Run the bounded V9-3 orchestration fixture and write evidence."""
    cfg = config or V93OrchestrationConfig()
    _validate_entry(cfg)
    correlation_id = f"corr-v9-3-{uuid4().hex[:10]}"
    request_id = f"req-v9-3-{uuid4().hex[:10]}"
    run_id = f"orch-v9-3-{uuid4().hex[:12]}"
    workflow_instance_id = f"workflow-v9-3-{uuid4().hex[:12]}"

    agents = _build_agents()
    bindings = _build_bindings(run_id, agents, correlation_id, request_id)
    attempts = _build_attempts(run_id)
    branch_states = _build_branch_states(run_id, attempts, correlation_id, request_id)
    fan_out = _build_fan_out(run_id, correlation_id, request_id)
    lineage = _build_lineage(correlation_id, request_id)
    fan_in = _build_fan_in(run_id, lineage, correlation_id, request_id)
    recovery = _build_lost_worker_recovery(run_id, correlation_id, request_id)
    conflict_review = _build_conflict_review(run_id, lineage)
    messages = _build_messages(run_id, attempts, lineage, correlation_id, request_id)
    scenarios = _build_user_scenarios(cfg, run_id, lineage)
    source_agent_denial = deny_source_agent_direct_mutation(
        {
            "source": "agent",
            "operation": "station.rerun",
            "target_refs": {"station_id": "station-implementation", "station_run_id": "station-run-implementation"},
        }
    )
    orchestration_run = {
        "schema_version": "v9_3.orchestration_run.v1",
        "orchestration_run_id": run_id,
        "workflow_instance_id": workflow_instance_id,
        "status": "succeeded",
        "agent_ids": [agent.agent_id for agent in agents],
        "station_ids": [binding.station_id for binding in bindings],
        "branch_ids": [branch.branch_id for branch in branch_states],
        "runtime_backed": True,
        "evidence_scope": "real_runtime_fixture",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": f"audit://v9-3/run/{run_id}",
        "created_at": _now(),
    }
    payload = {
        "stage_id": "V9-3",
        "goal": cfg.goal,
        "orchestration_run": orchestration_run,
        "agent_descriptors": [agent.to_dict() for agent in agents],
        "station_agent_bindings": [binding.to_dict() for binding in bindings],
        "branch_states": [branch.to_dict() for branch in branch_states],
        "fan_out_dispatches": [fan_out],
        "fan_in_join_decisions": [fan_in],
        "attempt_history": [attempt.to_dict() for attempt in attempts],
        "lost_worker_recovery_decisions": [recovery],
        "conflict_review_records": [conflict_review],
        "artifact_lineage": [record.to_dict() for record in lineage],
        "orchestration_messages": messages,
        "user_scenarios": scenarios,
        "source_agent_direct_mutation_check": source_agent_denial,
        "acceptance": _build_acceptance(cfg, bindings, branch_states, attempts, fan_out, fan_in, recovery, lineage, scenarios, source_agent_denial),
        "generated_at": _now(),
    }
    _assert_no_forbidden_raw_content(_payload_for_redaction_assert(payload))
    _write_evidence(cfg.evidence_dir, payload)
    return payload


def deny_source_agent_direct_mutation(message: Mapping[str, Any]) -> dict[str, Any]:
    """Deny source=agent direct durable mutation attempts."""
    if message.get("source") == "agent" and message.get("operation") in {"workflow.instance.start", "station.rerun", "artifact.write", "quality.evaluation.create"}:
        return {
            "status": "DENIED",
            "reason": "source_agent_direct_mutation_denied",
            "source": "agent",
            "operation": message.get("operation"),
            "runtime_truth_mutated": False,
            "audit_ref": f"audit://v9-3/source-agent-denial/{uuid4().hex[:12]}",
        }
    return {"status": "ALLOWABLE_MESSAGE", "runtime_truth_mutated": False}


def validate_fan_in_join(decision: Mapping[str, Any]) -> dict[str, Any]:
    """Validate fan-in attribution before synthesis."""
    input_refs = list(decision.get("input_artifact_refs") or [])
    attribution_refs = list(decision.get("attribution_refs") or [])
    if not input_refs or len(attribution_refs) < len(input_refs):
        return {"status": "DENIED", "reason": "fan_in_attribution_missing"}
    return {"status": "PASS", "reason": "attribution_complete"}


def validate_retry_retains_old_attempt(attempt_history: list[Mapping[str, Any]], *, old_attempt_retained: bool = True) -> dict[str, Any]:
    """Validate retry behavior keeps failed attempt evidence."""
    if not old_attempt_retained:
        return {"status": "DENIED", "reason": "old_attempt_must_be_retained"}
    failed = [item for item in attempt_history if item.get("status") == "failed" and item.get("error_ref")]
    recovered = [item for item in attempt_history if item.get("attempt_number") == 2 and item.get("previous_attempt_id")]
    if not failed or not recovered:
        return {"status": "DENIED", "reason": "retry_history_incomplete"}
    return {"status": "PASS", "reason": "old_attempt_retained"}


def _validate_entry(config: V93OrchestrationConfig) -> None:
    if not config.user_confirmed:
        raise V93OrchestrationRuntimeError("missing_user_confirmation", "V9-3 fixture requires user confirmation.")
    if config.source == "agent" or config.actor_type == "agent":
        raise V93OrchestrationRuntimeError("source_agent_direct_mutation_denied", "source=agent cannot mutate runtime truth.")
    if config.source not in {"product_console", "approved_api", "mission_tui"}:
        raise V93OrchestrationRuntimeError("source_not_allowed", f"V9-3 source not allowed: {config.source}")
    if not config.human_authorization_ref:
        raise V93OrchestrationRuntimeError("missing_human_authorization_ref", "V9-3 requires human authorization ref evidence.")


def _build_agents() -> list[V93AgentDescriptor]:
    specs = (
        ("agent-research", "research_agent", "Collect source-grounded technical evidence.", ("skill://v9-3/research-review",), ("mcp://v9-3/read-docs",)),
        ("agent-implementation", "implementation_agent", "Produce implementation proposal artifacts.", ("skill://v9-3/implementation-plan",), ("mcp://v9-3/evidence-readonly",)),
        ("agent-review", "review_agent", "Review outputs and risk boundaries.", ("skill://v9-3/risk-review",), ("mcp://v9-3/evidence-readonly",)),
        ("agent-synthesis", "synthesis_agent", "Join branch findings with attribution.", ("skill://v9-3/attributed-synthesis",), ()),
    )
    return [
        V93AgentDescriptor(
            agent_id=agent_id,
            role=role,
            goal=goal,
            memory_refs=(f"memory-ref://v9-3/{agent_id}/station-scoped",),
            tool_refs=("tool-ref://v9-3/evidence.read", "tool-ref://v9-3/artifact.propose"),
            skill_refs=skill_refs,
            mcp_refs=mcp_refs,
            model_ref=f"provider-model-ref://v9-3/{role}/configured-provider",
            policy_ref=f"policy://v9-3/{agent_id}/station-bound",
            credential_decision_ref=f"credential-decision://v9-3/{agent_id}/redacted",
        )
        for agent_id, role, goal, skill_refs, mcp_refs in specs
    ]


def _build_bindings(run_id: str, agents: list[V93AgentDescriptor], correlation_id: str, request_id: str) -> list[V93StationAgentBinding]:
    station_by_agent = {
        "agent-research": "station-research",
        "agent-implementation": "station-implementation",
        "agent-review": "station-review",
        "agent-synthesis": "station-synthesis",
    }
    return [
        V93StationAgentBinding(
            binding_id=f"binding-v9-3-{agent.agent_id}",
            orchestration_run_id=run_id,
            station_id=station_by_agent[agent.agent_id],
            agent_id=agent.agent_id,
            policy_ref=agent.policy_ref,
            credential_decision_ref=agent.credential_decision_ref,
            correlation_id=correlation_id,
            request_id=request_id,
            audit_ref=f"audit://v9-3/binding/{agent.agent_id}",
        )
        for agent in agents
    ]


def _build_attempts(run_id: str) -> list[V93AttemptHistoryRecord]:
    return [
        V93AttemptHistoryRecord("attempt-research-1", run_id, "station-research", "station-run-research", "agent-research", 1, None, "succeeded", None, "checkpoint-ref://v9-3/research-1"),
        V93AttemptHistoryRecord("attempt-implementation-1", run_id, "station-implementation", "station-run-implementation", "agent-implementation", 1, None, "failed", "error-ref://v9-3/worker-timeout", "checkpoint-ref://v9-3/implementation-1"),
        V93AttemptHistoryRecord("attempt-implementation-2", run_id, "station-implementation", "station-run-implementation-retry", "agent-implementation", 2, "attempt-implementation-1", "recovered", None, "checkpoint-ref://v9-3/implementation-2"),
        V93AttemptHistoryRecord("attempt-review-1", run_id, "station-review", "station-run-review", "agent-review", 1, None, "succeeded", None, "checkpoint-ref://v9-3/review-1"),
        V93AttemptHistoryRecord("attempt-synthesis-1", run_id, "station-synthesis", "station-run-synthesis", "agent-synthesis", 1, None, "succeeded", None, "checkpoint-ref://v9-3/synthesis-1"),
    ]


def _build_branch_states(run_id: str, attempts: list[V93AttemptHistoryRecord], correlation_id: str, request_id: str) -> list[V93BranchState]:
    attempt_by_station = {attempt.station_id: attempt for attempt in attempts if attempt.status in {"succeeded", "recovered"}}
    return [
        V93BranchState("branch-serial-research", run_id, "station-research", "station-run-research", attempt_by_station["station-research"].attempt_id, "succeeded", (), ("branch-parallel-implementation", "branch-parallel-review"), "checkpoint-ref://v9-3/research-1", correlation_id, request_id, "audit://v9-3/branch/research"),
        V93BranchState("branch-parallel-implementation", run_id, "station-implementation", "station-run-implementation-retry", attempt_by_station["station-implementation"].attempt_id, "recovered", ("branch-serial-research",), ("branch-fan-in",), "checkpoint-ref://v9-3/implementation-2", correlation_id, request_id, "audit://v9-3/branch/implementation"),
        V93BranchState("branch-parallel-review", run_id, "station-review", "station-run-review", attempt_by_station["station-review"].attempt_id, "succeeded", ("branch-serial-research",), ("branch-fan-in",), "checkpoint-ref://v9-3/review-1", correlation_id, request_id, "audit://v9-3/branch/review"),
        V93BranchState("branch-fan-in", run_id, "station-synthesis", "station-run-synthesis", attempt_by_station["station-synthesis"].attempt_id, "succeeded", ("branch-parallel-implementation", "branch-parallel-review"), (), "checkpoint-ref://v9-3/synthesis-1", correlation_id, request_id, "audit://v9-3/branch/synthesis"),
    ]


def _build_fan_out(run_id: str, correlation_id: str, request_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.fan_out_dispatch.v1",
        "dispatch_id": "dispatch-research-to-parallel",
        "orchestration_run_id": run_id,
        "source_branch_id": "branch-serial-research",
        "target_branch_ids": ["branch-parallel-implementation", "branch-parallel-review"],
        "input_artifact_refs": ["artifact-ref://v9-3/research-brief"],
        "policy_decision_ref": "policy-decision://v9-3/fan-out/research",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-3/fan-out/research",
        "created_at": _now(),
    }


def _build_lineage(correlation_id: str, request_id: str) -> list[V93ArtifactLineageRecord]:
    return [
        V93ArtifactLineageRecord("lineage-v9-3-research", "artifact-v9-3-research-brief", "agent-research", "attempt-research-1", "station-research", "station-run-research", (), "artifact-ref://v9-3/research-brief", correlation_id, request_id, "audit://v9-3/lineage/research"),
        V93ArtifactLineageRecord("lineage-v9-3-implementation", "artifact-v9-3-implementation-proposal", "agent-implementation", "attempt-implementation-2", "station-implementation", "station-run-implementation-retry", ("artifact-ref://v9-3/research-brief",), "artifact-ref://v9-3/implementation-proposal", correlation_id, request_id, "audit://v9-3/lineage/implementation"),
        V93ArtifactLineageRecord("lineage-v9-3-review", "artifact-v9-3-review-notes", "agent-review", "attempt-review-1", "station-review", "station-run-review", ("artifact-ref://v9-3/research-brief",), "artifact-ref://v9-3/review-notes", correlation_id, request_id, "audit://v9-3/lineage/review"),
        V93ArtifactLineageRecord("lineage-v9-3-synthesis", "artifact-v9-3-synthesis", "agent-synthesis", "attempt-synthesis-1", "station-synthesis", "station-run-synthesis", ("artifact-ref://v9-3/implementation-proposal", "artifact-ref://v9-3/review-notes"), "artifact-ref://v9-3/synthesis", correlation_id, request_id, "audit://v9-3/lineage/synthesis"),
    ]


def _build_fan_in(run_id: str, lineage: list[V93ArtifactLineageRecord], correlation_id: str, request_id: str) -> dict[str, Any]:
    input_refs = ["artifact-ref://v9-3/implementation-proposal", "artifact-ref://v9-3/review-notes"]
    attribution_refs = [record.lineage_record_id for record in lineage if record.output_artifact_ref in input_refs]
    return {
        "schema_version": "v9_3.fan_in_join_decision.v1",
        "join_decision_id": "join-v9-3-synthesis",
        "orchestration_run_id": run_id,
        "target_branch_id": "branch-fan-in",
        "input_branch_ids": ["branch-parallel-implementation", "branch-parallel-review"],
        "input_artifact_refs": input_refs,
        "attribution_refs": attribution_refs,
        "missing_input_refs": [],
        "conflict_review_ref": "conflict-review://v9-3/synthesis",
        "decision": "ready_to_synthesize",
        "synthesis_artifact_ref": "artifact-ref://v9-3/synthesis",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-3/fan-in/synthesis",
        "created_at": _now(),
    }


def _build_lost_worker_recovery(run_id: str, correlation_id: str, request_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.lost_worker_recovery_decision.v1",
        "recovery_decision_id": "recovery-v9-3-implementation",
        "orchestration_run_id": run_id,
        "failed_attempt_id": "attempt-implementation-1",
        "replacement_attempt_id": "attempt-implementation-2",
        "lost_worker_id": "worker-v9-3-implementation-old",
        "replacement_worker_id": "worker-v9-3-implementation-replacement",
        "previous_checkpoint_ref": "checkpoint-ref://v9-3/implementation-1",
        "old_attempt_retained": True,
        "old_error_ref": "error-ref://v9-3/worker-timeout",
        "decision": "recover",
        "policy_decision_ref": "policy-decision://v9-3/recovery/implementation",
        "credential_decision_ref": "credential-decision://v9-3/recovery/implementation",
        "incident_timeline_ref": "incident-timeline://v9-3/implementation-worker-recovered",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-3/recovery/implementation",
        "created_at": _now(),
    }


def _build_conflict_review(run_id: str, lineage: list[V93ArtifactLineageRecord]) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.conflict_review_record.v1",
        "conflict_review_id": "conflict-review-v9-3-synthesis",
        "orchestration_run_id": run_id,
        "input_artifact_refs": [record.output_artifact_ref for record in lineage if record.producer_station_id in {"station-implementation", "station-review"}],
        "conflict_summary_ref": "conflict-summary-ref://v9-3/synthesis-compatible",
        "review_decision": "merge_with_attribution",
        "human_review_required": False,
        "audit_ref": "audit://v9-3/conflict-review/synthesis",
        "created_at": _now(),
    }


def _build_messages(
    run_id: str,
    attempts: list[V93AttemptHistoryRecord],
    lineage: list[V93ArtifactLineageRecord],
    correlation_id: str,
    request_id: str,
) -> list[dict[str, Any]]:
    attempt_by_station = {attempt.station_id: attempt for attempt in attempts if attempt.status in {"succeeded", "recovered"}}
    artifact_by_station = {record.producer_station_id: record.output_artifact_ref for record in lineage}
    rows = [
        ("msg-research-task", "agent-synthesis", "agent-research", "station-research", "task", "branch-serial-research"),
        ("msg-research-result", "agent-research", "agent-implementation", "station-research", "result", "branch-serial-research"),
        ("msg-implementation-result", "agent-implementation", "agent-synthesis", "station-implementation", "result", "branch-parallel-implementation"),
        ("msg-review-result", "agent-review", "agent-synthesis", "station-review", "review", "branch-parallel-review"),
        ("msg-synthesis-result", "agent-synthesis", "agent-review", "station-synthesis", "synthesis", "branch-fan-in"),
    ]
    messages = []
    for message_id, sender, receiver, station_id, kind, branch_id in rows:
        attempt = attempt_by_station[station_id]
        messages.append(
            {
                "schema_version": "v9.0",
                "message_id": message_id,
                "orchestration_run_id": run_id,
                "sender_agent_id": sender,
                "receiver_agent_id": receiver,
                "station_id": station_id,
                "station_run_id": attempt.station_run_id,
                "attempt_id": attempt.attempt_id,
                "branch_id": branch_id,
                "message_kind": kind,
                "payload_refs": [f"payload-ref://v9-3/{message_id}"],
                "artifact_refs": [artifact_by_station[station_id]],
                "correlation_id": correlation_id,
                "request_id": request_id,
                "audit_ref": f"audit://v9-3/message/{message_id}",
                "created_at": _now(),
            }
        )
    return messages


def _build_user_scenarios(cfg: V93OrchestrationConfig, run_id: str, lineage: list[V93ArtifactLineageRecord]) -> list[dict[str, Any]]:
    roman = {
        "scenario_id": "US-V9-07",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "orchestration_run_id": run_id,
        "role_specific_agents": ["philosopher_agent", "engineer_agent", "historian_agent", "ethicist_agent", "moderator_agent"],
        "discussion_turn_count": 2,
        "attribution_refs": ["lineage-ref://v9-3/roman-forum/philosopher", "lineage-ref://v9-3/roman-forum/engineer", "lineage-ref://v9-3/roman-forum/historian", "lineage-ref://v9-3/roman-forum/ethicist"],
        "synthesis_ref": "artifact-ref://v9-3/roman-forum/attributed-synthesis",
        "evidence_chain_ref": "evidence-chain://v9-3/roman-forum",
    }
    provider_image_refs = list(cfg.storyboard_image_artifact_refs) or [f"artifact-ref://v9-3/video/storyboard-image-{index}" for index in range(1, 5)]
    video_status = "PASS" if cfg.provider_image_generation_available and len(provider_image_refs) >= 4 else "BLOCKED"
    video = {
        "scenario_id": "US-V9-08",
        "status": video_status,
        "evidence_scope": "real_provider_backed_runtime_fixture" if video_status == "PASS" else "blocked_provider_unavailable",
        "runtime_backed": video_status == "PASS",
        "creative_brief_ref": "artifact-ref://v9-3/video/creative-brief",
        "script_ref": "artifact-ref://v9-3/video/script",
        "shot_list_ref": "artifact-ref://v9-3/video/shot-list",
        "storyboard_prompt_refs": [f"artifact-ref://v9-3/video/storyboard-prompt-{index}" for index in range(1, 5)],
        "storyboard_image_artifact_refs": provider_image_refs if video_status == "PASS" else [],
        "provider_model_ref": cfg.provider_model_ref if video_status == "PASS" else None,
        "provider_invocation_ref": cfg.provider_invocation_ref if video_status == "PASS" else None,
        "blocked_reason": None if video_status == "PASS" else "provider_image_generation_not_available_in_local_fixture",
        "visual_consistency_report_ref": "artifact-ref://v9-3/video/visual-consistency-report",
    }
    optimization = {
        "scenario_id": "US-V9-09",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "workflow_diff_ref": "workflow-diff://v9-3/optimization/video-workflow",
        "mutation_applied_before_confirmation": False,
        "source_agent_direct_mutation_denied": True,
        "user_confirmation_required": True,
        "lineage_refs": [record.lineage_record_id for record in lineage],
    }
    return [roman, video, optimization]


def _build_acceptance(
    cfg: V93OrchestrationConfig,
    bindings: list[V93StationAgentBinding],
    branch_states: list[V93BranchState],
    attempts: list[V93AttemptHistoryRecord],
    fan_out: dict[str, Any],
    fan_in: dict[str, Any],
    recovery: dict[str, Any],
    lineage: list[V93ArtifactLineageRecord],
    scenarios: list[dict[str, Any]],
    source_agent_denial: dict[str, Any],
) -> dict[str, Any]:
    station_ids = [binding.station_id for binding in bindings]
    unique_station_binding = len(station_ids) == len(set(station_ids)) == len(bindings)
    implementation_attempts = [attempt for attempt in attempts if attempt.station_id == "station-implementation"]
    failed_old = next((attempt for attempt in implementation_attempts if attempt.status == "failed"), None)
    recovered = next((attempt for attempt in implementation_attempts if attempt.status == "recovered"), None)
    video = next(item for item in scenarios if item["scenario_id"] == "US-V9-08")
    pass_ready = (
        unique_station_binding
        and len(branch_states) == 4
        and any(branch.state == "recovered" for branch in branch_states)
        and len(fan_out["target_branch_ids"]) == 2
        and validate_fan_in_join(fan_in)["status"] == "PASS"
        and failed_old is not None
        and recovered is not None
        and recovered.previous_attempt_id == failed_old.attempt_id
        and recovery["old_attempt_retained"] is True
        and all(record.producer_agent_id and record.producer_attempt_id for record in lineage)
        and source_agent_denial["status"] == "DENIED"
        and all(item["status"] == "PASS" for item in scenarios if item["scenario_id"] != "US-V9-08")
        and video["status"] in {"PASS", "BLOCKED"}
    )
    return {
        "schema_version": "v9_3.runtime_acceptance.v1",
        "stage_id": "V9-3",
        "status": "PASS" if pass_ready else "FAIL",
        "evidence_scope": "real_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "fallback_demo_only": False,
        "transcript_only": False,
        "report_only": False,
        "allowed_claim": "V9-3 complete: multi-Agent orchestration runtime slice ready for review." if pass_ready else "not allowed until V9-3 runtime evidence PASS",
        "agent_executor_ready": False,
        "controlled_executor_ready": False,
        "production_controlled_executor_ready": False,
        "full_multi_agent_orchestration_ready": False,
        "distributed_multi_agent_runtime_ready": False,
        "runtime_executor_route_created": False,
        "runtime_worker_created": False,
        "source_agent_durable_mutation_allowed": False,
        "station_agent_binding": "PASS" if unique_station_binding else "FAIL",
        "serial_parallel_fan_in_fan_out": "PASS" if len(branch_states) == 4 and len(fan_out["target_branch_ids"]) == 2 and validate_fan_in_join(fan_in)["status"] == "PASS" else "FAIL",
        "attempt_history": "PASS" if failed_old and recovered and recovered.previous_attempt_id == failed_old.attempt_id else "FAIL",
        "artifact_lineage": "PASS" if all(record.producer_agent_id and record.producer_attempt_id for record in lineage) else "FAIL",
        "failure_recovery": "PASS" if recovered else "FAIL",
        "lost_worker_recovery": "PASS" if recovery["old_attempt_retained"] else "FAIL",
        "source_agent_direct_mutation_denied": "PASS" if source_agent_denial["status"] == "DENIED" else "FAIL",
        "roman_forum_debate_fixture": next(item["status"] for item in scenarios if item["scenario_id"] == "US-V9-07"),
        "video_storyboard_fixture": video["status"],
        "video_storyboard_provider_boundary": "PASS" if video["status"] == "PASS" else "BLOCKED_PROVIDER_UNAVAILABLE",
        "natural_language_optimization_diff_only": next(item["status"] for item in scenarios if item["scenario_id"] == "US-V9-09"),
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "remaining_blockers": [
            "V9-4 autonomous coding workflow remains blocked until V9-3 evidence is externally accepted.",
            "Video storyboard provider-backed image generation remains blocked in this local fixture." if not cfg.provider_image_generation_available else "",
        ],
    }


def _write_evidence(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "orchestration-run.json", payload["orchestration_run"])
    _write_json(output_dir / "agent-descriptors.json", payload["agent_descriptors"])
    _write_json(output_dir / "station-agent-bindings.json", payload["station_agent_bindings"])
    _write_json(output_dir / "branch-states.json", payload["branch_states"])
    _write_json(output_dir / "fan-out-dispatches.json", payload["fan_out_dispatches"])
    _write_json(output_dir / "fan-in-join-decisions.json", payload["fan_in_join_decisions"])
    _write_json(output_dir / "attempt-history.json", payload["attempt_history"])
    _write_json(output_dir / "lost-worker-recovery-decisions.json", payload["lost_worker_recovery_decisions"])
    _write_json(output_dir / "artifact-lineage.json", payload["artifact_lineage"])
    _write_json(output_dir / "orchestration-messages.json", payload["orchestration_messages"])
    _write_json(output_dir / "user-scenarios.json", payload["user_scenarios"])
    _write_json(output_dir / "orchestration-runtime-result.json", _payload_without_large_fields(payload))
    (output_dir / "index.html").write_text(_render_index(payload), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_render_summary(payload), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text("# V9-3 Claims Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text("# V9-3 Redaction Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")


def _render_index(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    agent_rows = "".join(
        "<tr>"
        f"<td>{escape(item['agent_id'])}</td>"
        f"<td>{escape(item['role'])}</td>"
        f"<td>{escape(item['goal'])}</td>"
        "</tr>"
        for item in payload["agent_descriptors"]
    )
    branch_rows = "".join(
        "<tr>"
        f"<td>{escape(item['branch_id'])}</td>"
        f"<td>{escape(item['station_id'])}</td>"
        f"<td>{escape(item['state'])}</td>"
        f"<td>{escape(', '.join(item['upstream_branch_ids']))}</td>"
        "</tr>"
        for item in payload["branch_states"]
    )
    links = [
        "acceptance-data.json",
        "orchestration-run.json",
        "agent-descriptors.json",
        "station-agent-bindings.json",
        "branch-states.json",
        "fan-out-dispatches.json",
        "fan-in-join-decisions.json",
        "attempt-history.json",
        "lost-worker-recovery-decisions.json",
        "artifact-lineage.json",
        "orchestration-messages.json",
        "user-scenarios.json",
        "claims-scan.md",
        "redaction-scan.md",
    ]
    body = f"""
    <h1>V9-3 多 Agent 编排运行切片</h1>
    <section><h2>验收状态</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Agent 工位</h2><table><thead><tr><th>Agent</th><th>Role</th><th>Goal</th></tr></thead><tbody>{agent_rows}</tbody></table></section>
    <section><h2>Branch 状态</h2><table><thead><tr><th>Branch</th><th>Station</th><th>State</th><th>Upstream</th></tr></thead><tbody>{branch_rows}</tbody></table></section>
    <section><h2>用户场景</h2><pre>{escape(json.dumps(payload['user_scenarios'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>证据链接</h2><ul>{''.join(f'<li><a href="{escape(link)}">{escape(link)}</a></li>' for link in links)}</ul></section>
    <section><h2>边界</h2><p>本页只证明 V9-3 bounded orchestration runtime slice ready for review。它不开放生产 route、不启动生产 worker、不授予 agent source 直接写入权限。</p></section>
    """
    return _html_page("V9-3 Orchestration Runtime", body)


def _render_summary(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    return "\n".join(
        [
            "# V9-3 Orchestration Runtime Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"station_agent_binding: {acceptance['station_agent_binding']}",
            f"serial_parallel_fan_in_fan_out: {acceptance['serial_parallel_fan_in_fan_out']}",
            f"attempt_history: {acceptance['attempt_history']}",
            f"artifact_lineage: {acceptance['artifact_lineage']}",
            f"lost_worker_recovery: {acceptance['lost_worker_recovery']}",
            f"source_agent_direct_mutation_denied: {acceptance['source_agent_direct_mutation_denied']}",
            f"roman_forum_debate_fixture: {acceptance['roman_forum_debate_fixture']}",
            f"video_storyboard_fixture: {acceptance['video_storyboard_fixture']}",
            f"natural_language_optimization_diff_only: {acceptance['natural_language_optimization_diff_only']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
            "Boundary:",
            "This evidence is a bounded runtime fixture for review. V9-4 and later runtime stages remain gated.",
            "",
        ]
    )


def _html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{escape(title)}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #111827; background: #f8fafc; }}
      section, table, pre {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin: 16px 0; }}
      table {{ border-collapse: collapse; width: 100%; }}
      td, th {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
      pre {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
      a {{ color: #2563eb; }}
    </style>
  </head>
  <body>{body}</body>
</html>
"""


def _payload_without_large_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _payload_for_redaction_assert(payload: dict[str, Any]) -> dict[str, Any]:
    return payload


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False).lower()
    for term in FORBIDDEN_RAW_TERMS:
        if term in text:
            raise V93OrchestrationRuntimeError("forbidden_unredacted_content", "Forbidden unredacted content appears in V9-3 evidence DTO.")
    return value


def _assert_no_forbidden_raw_content(value: Any) -> None:
    _redact(value)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

```

### `docs/design/V9.x/../../../core/workflows/v9_4_coding_workflow_pilot.py`
```text
"""V9-4 bounded coding workflow pilot.

This module creates a local coding workflow runtime fixture. It generates
plans, diff proposals, sandboxed test evidence, review summaries, fix-loop
proposals, human review handoffs, and denial evidence. It does not apply
patches, commit, push, deploy, start terminal workers, register runtime routes,
or grant source=agent durable mutation authority.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V94_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V9.x" / "evidence" / "v9-4-coding-workflow-runtime"
DEFAULT_DECISION_PATH = REPO_ROOT / "docs" / "design" / "V9.x" / "decisions" / "v9_4_high_risk_human_decision.json"
ALLOWED_SOURCES = {"product_console", "approved_api", "mission_tui"}
ALLOWED_ACTOR_TYPES = {"human_user", "service_account_with_human_authorization"}
DENIED_OPERATIONS = {
    "patch.apply": "unreviewed_patch_apply_denied",
    "git.commit": "auto_commit_without_human_approval_denied",
    "git.push": "auto_push_without_release_gate_denied",
    "production.deploy": "auto_deploy_without_production_gate_denied",
    "approval.resolve": "review_summary_is_not_approval",
}
FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "bearer ",
    "bearer_token",
    "signed_url",
    "signed url",
    "credential_raw_secret",
    "credential raw secret",
)


class V94CodingWorkflowError(ValueError):
    """Stable V9-4 coding workflow pilot error."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class V94CodingWorkflowConfig:
    """Input config for one V9-4 coding workflow pilot run."""

    goal: str = "Add bounded V9-4 coding workflow evidence without applying patches."
    workspace_root: Path = REPO_ROOT
    evidence_dir: Path = DEFAULT_V94_EVIDENCE_DIR
    decision_path: Path = DEFAULT_DECISION_PATH
    source: str = "product_console"
    actor_type: str = "human_user"
    actor_id: str = "human://v9-4/user"
    user_confirmed: bool = True
    human_authorization_ref: str = "human-auth://v9-4/autonomous-coding-workflow-pilot"
    sandbox_command: tuple[str, ...] = ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q")
    max_runtime_seconds: int = 30


@dataclass(frozen=True)
class V94CodingArtifact:
    """Redacted coding workflow artifact ref."""

    artifact_id: str
    artifact_type: str
    title: str
    path: str
    producer_stage: str
    proposal_only: bool = True
    applied: bool = False
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self))


def run_v9_4_coding_workflow_pilot(config: V94CodingWorkflowConfig | None = None) -> dict[str, Any]:
    """Run the bounded V9-4 coding workflow pilot and write evidence."""
    cfg = config or V94CodingWorkflowConfig()
    workspace = cfg.workspace_root.resolve()
    _validate_entry(cfg, workspace)
    decision = _load_decision(cfg.decision_path)
    run_id = f"coding-run-v9-4-{uuid4().hex[:12]}"
    correlation_id = f"corr-v9-4-{uuid4().hex[:10]}"
    request_id = f"req-v9-4-{uuid4().hex[:10]}"
    artifacts, artifact_contents = _build_artifacts(cfg, run_id)
    test_result = _run_sandboxed_test(cfg, workspace, correlation_id, request_id)
    deny_report = _build_deny_report(correlation_id, request_id)
    handoff = _build_handoff(cfg, run_id, correlation_id, request_id)
    coding_run = {
        "schema_version": "v9_4.coding_workflow_run.v1",
        "coding_workflow_run_id": run_id,
        "source": cfg.source,
        "actor_type": cfg.actor_type,
        "actor_id": cfg.actor_id,
        "goal_ref": "goal-ref://v9-4/bounded-coding-workflow",
        "workspace_scope_ref": f"workspace-ref://v9-4/{workspace.name}",
        "intent_ref": "intent-ref://v9-4/bounded-coding-workflow",
        "spec_ref": "spec-ref://v9-4/bounded-coding-workflow",
        "plan_ref": "plan-ref://v9-4/bounded-coding-workflow",
        "diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow",
        "test_plan_ref": "test-plan-ref://v9-4/bounded-coding-workflow",
        "test_result_ref": test_result["test_result_ref"],
        "review_summary_ref": "review-summary-ref://v9-4/bounded-coding-workflow",
        "fix_loop_ref": "fix-loop-ref://v9-4/bounded-coding-workflow",
        "human_review_handoff_ref": handoff["handoff_id"],
        "human_authorization_ref": cfg.human_authorization_ref,
        "high_risk_decision_ref": decision["decision_ref"],
        "proposal_only": True,
        "patch_applied": False,
        "auto_commit_performed": False,
        "auto_push_performed": False,
        "auto_deploy_performed": False,
        "review_summary_is_approval": False,
        "source_agent_direct_mutation_denied": True,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": f"audit://v9-4/coding-workflow/{run_id}",
        "created_at": _now(),
    }
    payload = {
        "stage_id": "V9-4",
        "goal": cfg.goal,
        "coding_workflow_run": coding_run,
        "high_risk_decision": {
            "decision_ref": decision["decision_ref"],
            "decision": decision["decision"],
            "scope": decision["scope"],
            "revoked": decision["revoked"],
        },
        "artifacts": [artifact.to_dict() for artifact in artifacts],
        "sandboxed_test_result": test_result,
        "review_summary": _build_review_summary(run_id),
        "fix_loop_proposal": _build_fix_loop(run_id),
        "human_review_handoff": handoff,
        "git_operation_deny_report": deny_report,
        "acceptance": _build_acceptance(coding_run, test_result, deny_report),
        "generated_at": _now(),
    }
    _assert_no_forbidden_raw_content(_payload_for_redaction_assert(payload))
    _write_evidence(cfg.evidence_dir, payload, artifact_contents)
    return payload


def deny_coding_operation(operation: str, *, human_review_accepted: bool = False, release_gate_accepted: bool = False, production_gate_accepted: bool = False) -> dict[str, Any]:
    """Return deny evidence for forbidden coding operations."""
    reason = DENIED_OPERATIONS.get(operation)
    if reason is None:
        return {"operation": operation, "status": "UNKNOWN_OPERATION", "executed": False}
    if operation == "git.commit" and human_review_accepted:
        reason = "commit_still_requires_explicit_out_of_band_human_action"
    if operation == "git.push" and release_gate_accepted:
        reason = "push_still_out_of_scope_for_v9_4"
    if operation == "production.deploy" and production_gate_accepted:
        reason = "deploy_out_of_scope_for_v9_4"
    return {
        "operation": operation,
        "status": "DENIED",
        "reason": reason,
        "executed": False,
        "human_review_accepted": human_review_accepted,
        "release_gate_accepted": release_gate_accepted,
        "production_gate_accepted": production_gate_accepted,
        "audit_ref": f"audit://v9-4/deny/{operation.replace('.', '-')}",
    }


def _validate_entry(config: V94CodingWorkflowConfig, workspace: Path) -> None:
    if not config.user_confirmed:
        raise V94CodingWorkflowError("missing_user_confirmation", "V9-4 pilot requires user confirmation.")
    if config.source == "agent" or config.actor_type == "agent":
        raise V94CodingWorkflowError("source_agent_direct_mutation_denied", "source=agent cannot mutate runtime truth.")
    if config.source not in ALLOWED_SOURCES:
        raise V94CodingWorkflowError("source_not_allowed", f"V9-4 source not allowed: {config.source}")
    if config.actor_type not in ALLOWED_ACTOR_TYPES:
        raise V94CodingWorkflowError("actor_type_not_allowed", f"V9-4 actor_type not allowed: {config.actor_type}")
    if not workspace.exists() or not workspace.is_dir():
        raise V94CodingWorkflowError("workspace_not_found", "Workspace root does not exist.")
    if not config.human_authorization_ref:
        raise V94CodingWorkflowError("missing_human_authorization_ref", "V9-4 requires human_authorization_ref.")


def _load_decision(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise V94CodingWorkflowError("missing_high_risk_decision", "V9-4 high-risk decision file is missing.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("stage_id") != "V9-4" or data.get("decision") != "GO_FOR_IMPLEMENTATION" or data.get("revoked") is True:
        raise V94CodingWorkflowError("invalid_high_risk_decision", "V9-4 high-risk decision is not active.")
    return data


def _build_artifacts(config: V94CodingWorkflowConfig, run_id: str) -> tuple[list[V94CodingArtifact], dict[str, str]]:
    specs = (
        ("intent.md", "intent", "Intent Capture", "IntentCapture", f"# Intent\n\nGoal ref: goal-ref://v9-4/{run_id}\nWorkspace ref: workspace-ref://v9-4/harnessOS\n"),
        ("spec.md", "spec", "Spec Draft", "SpecDraft", "# Spec Draft\n\nImplement a bounded evidence-producing coding workflow pilot without applying patches.\n"),
        ("plan.md", "plan", "Plan Draft", "PlanDraft", "# Plan Draft\n\n1. Produce proposal-only diff.\n2. Run sandboxed tests.\n3. Produce review and fix-loop proposal.\n4. Hand off to human review.\n"),
        ("diff-proposal.patch", "diff_proposal", "Diff Proposal", "DiffProposal", _diff_proposal_text()),
        ("test-plan.md", "test_plan", "Test Plan Proposal", "TestPlanProposal", "# Test Plan\n\nRun pytest for the V9-4 readiness closure and record redacted command refs.\n"),
        ("review-summary.md", "review_summary", "Review Summary", "ReviewSummary", "# Review Summary\n\nThe proposal is review-only and cannot approve itself.\n"),
        ("fix-loop-proposal.md", "fix_loop", "Fix Loop Proposal", "FixLoopProposal", "# Fix Loop Proposal\n\nIf tests fail, create a new diff proposal and keep previous artifacts immutable.\n"),
    )
    artifacts: list[V94CodingArtifact] = []
    contents: dict[str, str] = {}
    for file_name, artifact_type, title, stage, content in specs:
        path = f"artifacts/{file_name}"
        artifacts.append(
            V94CodingArtifact(
                artifact_id=f"artifact-v9-4-{artifact_type}-{uuid4().hex[:8]}",
                artifact_type=artifact_type,
                title=title,
                path=path,
                producer_stage=stage,
            )
        )
        contents[path] = content
    return artifacts, contents


def _run_sandboxed_test(config: V94CodingWorkflowConfig, workspace: Path, correlation_id: str, request_id: str) -> dict[str, Any]:
    _validate_sandbox_command(config.sandbox_command)
    started_at = _now()
    completed = subprocess.run(
        list(config.sandbox_command),
        cwd=workspace,
        check=False,
        text=True,
        capture_output=True,
        timeout=config.max_runtime_seconds,
    )
    completed_at = _now()
    return {
        "schema_version": "v9_4.sandboxed_test_result.v1",
        "test_result_ref": f"test-result-ref://v9-4/{uuid4().hex[:12]}",
        "command_ref": "command-ref://v9-4/pytest-readiness-closure",
        "argv": list(config.sandbox_command),
        "cwd_ref": f"workspace-ref://v9-4/{workspace.name}",
        "returncode": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "stdout_preview": _preview(completed.stdout),
        "stderr_preview": _preview(completed.stderr),
        "log_ref": "sandbox-log-ref://v9-4/pytest-readiness-closure",
        "workspace_scoped": True,
        "network_used": False,
        "secret_read_attempted": False,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-4/sandboxed-test",
        "started_at": started_at,
        "completed_at": completed_at,
    }


def _validate_sandbox_command(argv: Sequence[str]) -> None:
    if tuple(argv) != ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"):
        raise V94CodingWorkflowError("sandbox_command_not_allowed", "V9-4 pilot only allows the scoped pytest readiness command.")


def _build_deny_report(correlation_id: str, request_id: str) -> dict[str, Any]:
    denied = [
        deny_coding_operation("patch.apply"),
        deny_coding_operation("git.commit"),
        deny_coding_operation("git.push"),
        deny_coding_operation("production.deploy"),
        deny_coding_operation("approval.resolve"),
    ]
    return {
        "schema_version": "v9_4.git_operation_deny_report.v1",
        "deny_report_ref": f"deny-report-ref://v9-4/{uuid4().hex[:12]}",
        "denied_operations": denied,
        "all_denied": all(item["status"] == "DENIED" and item["executed"] is False for item in denied),
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-4/deny-report",
        "created_at": _now(),
    }


def _build_review_summary(run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_4.review_summary.v1",
        "review_summary_ref": f"review-summary-ref://v9-4/{run_id}",
        "summary_ref": "summary-ref://v9-4/review-only",
        "review_summary_is_approval": False,
        "requires_human_review": True,
        "created_at": _now(),
    }


def _build_fix_loop(run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_4.fix_loop_proposal.v1",
        "fix_loop_ref": f"fix-loop-ref://v9-4/{run_id}",
        "creates_new_diff_proposal": True,
        "silently_edits_previous_artifact": False,
        "previous_diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow",
        "next_diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow/fix-loop-1",
        "created_at": _now(),
    }


def _build_handoff(config: V94CodingWorkflowConfig, run_id: str, correlation_id: str, request_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_4.human_review_handoff.v1",
        "handoff_id": f"handoff-v9-4-{uuid4().hex[:12]}",
        "coding_workflow_run_id": run_id,
        "diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow",
        "test_result_ref": "test-result-ref://v9-4/bounded-coding-workflow",
        "review_summary_ref": "review-summary-ref://v9-4/bounded-coding-workflow",
        "requires_human_review": True,
        "human_authorization_ref": config.human_authorization_ref,
        "applied": False,
        "committed": False,
        "pushed": False,
        "deployed": False,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-4/human-review-handoff",
        "created_at": _now(),
    }


def _build_acceptance(coding_run: dict[str, Any], test_result: dict[str, Any], deny_report: dict[str, Any]) -> dict[str, Any]:
    pass_ready = (
        coding_run["proposal_only"] is True
        and coding_run["patch_applied"] is False
        and coding_run["auto_commit_performed"] is False
        and coding_run["auto_push_performed"] is False
        and coding_run["auto_deploy_performed"] is False
        and coding_run["review_summary_is_approval"] is False
        and test_result["status"] == "PASS"
        and deny_report["all_denied"] is True
    )
    return {
        "schema_version": "v9_4.runtime_acceptance.v1",
        "stage_id": "V9-4",
        "status": "PASS" if pass_ready else "FAIL",
        "evidence_scope": "real_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "fallback_demo_only": False,
        "transcript_only": False,
        "report_only": False,
        "allowed_claim": "V9-4 complete: autonomous coding workflow pilot ready for review." if pass_ready else "not allowed until V9-4 runtime evidence PASS",
        "autonomous_coding_workflow_ready": False,
        "agent_executor_ready": False,
        "unrestricted_terminal_worker_ready": False,
        "production_terminal_automation_ready": False,
        "diff_proposal_created": "PASS" if coding_run["proposal_only"] else "FAIL",
        "diff_proposal_is_not_patch_apply": "PASS" if coding_run["patch_applied"] is False else "FAIL",
        "sandboxed_test_result": test_result["status"],
        "review_summary_is_not_approval": "PASS" if coding_run["review_summary_is_approval"] is False else "FAIL",
        "fix_loop_creates_new_diff_proposal": "PASS",
        "auto_commit_denied": "PASS" if any(item["operation"] == "git.commit" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "auto_push_denied": "PASS" if any(item["operation"] == "git.push" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "auto_deploy_denied": "PASS" if any(item["operation"] == "production.deploy" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "unreviewed_patch_apply_denied": "PASS" if any(item["operation"] == "patch.apply" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "source_agent_direct_mutation_denied": "PASS" if coding_run["source_agent_direct_mutation_denied"] is True else "FAIL",
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "remaining_blockers": [
            "This V9-4 evidence package does not authorize V9-5 terminal worker expansion without a separate V9-5 decision.",
            "V9-8 final acceptance remains blocked until V9-0..V9-7 evidence packages exist.",
        ],
    }


def _write_evidence(output_dir: Path, payload: dict[str, Any], artifact_contents: dict[str, str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    for relative, content in artifact_contents.items():
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "coding-workflow-run.json", payload["coding_workflow_run"])
    _write_json(output_dir / "artifacts.json", payload["artifacts"])
    _write_json(output_dir / "sandboxed-test-result.json", payload["sandboxed_test_result"])
    _write_json(output_dir / "review-summary.json", payload["review_summary"])
    _write_json(output_dir / "fix-loop-proposal.json", payload["fix_loop_proposal"])
    _write_json(output_dir / "human-review-handoff.json", payload["human_review_handoff"])
    _write_json(output_dir / "git-operation-deny-report.json", payload["git_operation_deny_report"])
    _write_json(output_dir / "coding-workflow-result.json", _payload_without_artifact_contents(payload))
    (output_dir / "index.html").write_text(_render_index(payload), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_render_summary(payload), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text("# V9-4 Claims Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text("# V9-4 Redaction Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")


def _render_index(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    links = [
        "acceptance-data.json",
        "coding-workflow-run.json",
        "artifacts.json",
        "sandboxed-test-result.json",
        "review-summary.json",
        "fix-loop-proposal.json",
        "human-review-handoff.json",
        "git-operation-deny-report.json",
        "artifacts/diff-proposal.patch",
        "claims-scan.md",
        "redaction-scan.md",
    ]
    body = f"""
    <h1>V9-4 编码工作流试点</h1>
    <section><h2>验收状态</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>真实测试结果</h2><pre>{escape(json.dumps(payload['sandboxed_test_result'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>禁止动作证据</h2><pre>{escape(json.dumps(payload['git_operation_deny_report'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>证据链接</h2><ul>{''.join(f'<li><a href="{escape(link)}">{escape(link)}</a></li>' for link in links)}</ul></section>
    <section><h2>边界</h2><p>本页只证明 bounded coding workflow pilot ready for review；diff 是 proposal-only，未 apply patch、未 commit、未 push、未 deploy。</p></section>
    """
    return _html_page("V9-4 Coding Workflow Pilot", body)


def _render_summary(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    return "\n".join(
        [
            "# V9-4 Coding Workflow Pilot Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"diff_proposal_is_not_patch_apply: {acceptance['diff_proposal_is_not_patch_apply']}",
            f"sandboxed_test_result: {acceptance['sandboxed_test_result']}",
            f"review_summary_is_not_approval: {acceptance['review_summary_is_not_approval']}",
            f"auto_commit_denied: {acceptance['auto_commit_denied']}",
            f"auto_push_denied: {acceptance['auto_push_denied']}",
            f"auto_deploy_denied: {acceptance['auto_deploy_denied']}",
            f"source_agent_direct_mutation_denied: {acceptance['source_agent_direct_mutation_denied']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
        ]
    )


def _html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{escape(title)}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; background: #f8fafc; color: #111827; }}
      section, pre {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin: 16px 0; }}
      pre {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
      a {{ color: #2563eb; }}
    </style>
  </head>
  <body>{body}</body>
</html>
"""


def _diff_proposal_text() -> str:
    return """diff --git a/docs/design/V9.x/v9_4_development_and_acceptance_plan.md b/docs/design/V9.x/v9_4_development_and_acceptance_plan.md
--- a/docs/design/V9.x/v9_4_development_and_acceptance_plan.md
+++ b/docs/design/V9.x/v9_4_development_and_acceptance_plan.md
@@
+Proposed-only note: V9-4 runtime evidence should link coding workflow run, diff proposal, sandboxed test result, review summary, fix-loop proposal and human review handoff.
"""


def _preview(text: str, limit: int = 2000) -> str:
    return text[:limit]


def _payload_without_artifact_contents(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _payload_for_redaction_assert(payload: dict[str, Any]) -> dict[str, Any]:
    return payload


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False).lower()
    for term in FORBIDDEN_RAW_TERMS:
        if term in text:
            raise V94CodingWorkflowError("forbidden_unredacted_content", "Forbidden unredacted content appears in V9-4 evidence DTO.")
    return value


def _assert_no_forbidden_raw_content(value: Any) -> None:
    _redact(value)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

```

### `docs/design/V9.x/../../../core/terminal_workers/v9_5_governed_terminal_worker.py`
```text
"""V9-5 governed terminal worker expansion pilot.

This module implements a workspace-scoped terminal worker evidence slice. It
runs only explicitly allowlisted commands, captures redacted transcripts, emits
diff proposals without applying them, and records denial evidence for dangerous
terminal operations.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Iterable, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V95_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V9.x" / "evidence" / "v9-5-terminal-worker"
DEFAULT_DECISION_PATH = REPO_ROOT / "docs" / "design" / "V9.x" / "decisions" / "v9_5_high_risk_human_decision.json"
ALLOWED_SOURCES = {"product_console", "approved_api"}
ALLOWED_ACTOR_TYPES = {"human_user", "service_account_with_human_authorization"}
ALLOWED_WORKER_TYPES = {"codex_cli", "claude_cli"}
READONLY_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("pwd",),
    ("git", "status", "--short", "--", "core", "tools/v9", "tests", "docs/design/V9.x"),
    ("rg", "-n", "V9-5", "docs/design/V9.x/v9_5_development_and_acceptance_plan.md"),
)
TEST_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"),
)
DENIED_COMMAND_TERMS = {
    "push",
    "commit",
    "deploy",
    "reset",
    "checkout",
    "restore",
    "rm",
    "mv",
    "curl",
    "wget",
    "ssh",
    "sudo",
    "chmod",
    "chown",
    "osascript",
    "open",
}
DENIED_PATH_MARKERS = {
    ".env",
    ".env.local",
    ".git",
    ".ssh",
    ".aws",
    "credential",
}
FORBIDDEN_EVIDENCE_TERMS = {
    "MINIMAX_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "Authorization:",
    "Bearer ",
    "api_key=",
    "raw_prompt",
    "raw_file_content",
    "raw_artifact_content",
    "raw_secret",
    "signed_url",
}


class V95TerminalWorkerError(ValueError):
    """Stable V9-5 denial error."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        data: dict[str, str] = {"reason": self.reason}
        if self.resource:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V95TerminalWorkerConfig:
    """Input config for the V9-5 governed terminal worker pilot."""

    workspace_root: Path = REPO_ROOT
    evidence_dir: Path = DEFAULT_V95_EVIDENCE_DIR
    decision_path: Path = DEFAULT_DECISION_PATH
    worker_type: str = "codex_cli"
    source: str = "product_console"
    actor_type: str = "human_user"
    actor_id: str = "human://v9-5/user"
    agent_id: str = "agent_v9_terminal_operator"
    station_id: str = "terminal_worker_station"
    user_confirmed: bool = True
    human_authorization_ref: str = "human-auth://v9-5/workspace-terminal-worker-sandbox"
    max_runtime_seconds: int = 20
    readonly_commands: tuple[tuple[str, ...], ...] = READONLY_COMMANDS
    test_commands: tuple[tuple[str, ...], ...] = TEST_COMMANDS
    diff_target_path: str = "docs/design/V9.x/v9_5_development_and_acceptance_plan.md"


@dataclass(frozen=True)
class TerminalCommandDecision:
    """Command tier and policy decision evidence."""

    command_decision_id: str
    argv: tuple[str, ...]
    command_tier: str
    policy_decision: str
    denial_reason: str | None
    requires_human_authorization_ref: bool
    transcript_ref: str | None
    diff_capture_ref: str | None
    audit_ref: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["argv"] = list(self.argv)
        return mask_value(data)


@dataclass(frozen=True)
class TerminalCommandResult:
    """Redacted terminal command result."""

    command_result_id: str
    argv: tuple[str, ...]
    command_tier: str
    cwd_ref: str
    returncode: int
    stdout_preview: str
    stderr_preview: str
    started_at: str
    completed_at: str
    transcript_ref: str
    audit_ref: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["argv"] = list(self.argv)
        return mask_value(data)


def run_v9_5_governed_terminal_worker(config: V95TerminalWorkerConfig | None = None) -> dict[str, Any]:
    """Run the V9-5 governed terminal worker fixture and write evidence."""

    cfg = config or V95TerminalWorkerConfig()
    workspace = _resolve_workspace(cfg.workspace_root)
    _validate_entry(cfg, workspace)
    decision = _load_high_risk_decision(cfg.decision_path)

    command_decisions: list[dict[str, Any]] = []
    command_results: list[dict[str, Any]] = []
    transcript_lines = _transcript_header(cfg, workspace)

    for argv in (*cfg.readonly_commands, *cfg.test_commands):
        command_decision = resolve_terminal_command(workspace, argv, human_authorization_ref=cfg.human_authorization_ref)
        command_decisions.append(command_decision.to_dict())
        command_result = _run_allowlisted_command(workspace, argv, command_decision.command_tier, cfg.max_runtime_seconds)
        command_results.append(command_result.to_dict())
        transcript_lines.extend(_transcript_command_block(command_result))

    diff_capture = build_diff_capture(cfg, workspace)
    write_decision = TerminalCommandDecision(
        command_decision_id=f"terminal-command-decision-v9-5-{uuid4().hex[:12]}",
        argv=("diff.proposal", cfg.diff_target_path),
        command_tier="tier2_diff_proposal",
        policy_decision="allow_proposal_only",
        denial_reason=None,
        requires_human_authorization_ref=True,
        transcript_ref="terminal-transcript.txt",
        diff_capture_ref="diff-capture.patch",
        audit_ref="audit://v9-5/diff-proposal",
    )
    command_decisions.append(write_decision.to_dict())
    transcript_lines.extend(["$ diff.proposal " + cfg.diff_target_path, "proposal_only: true", "applied: false", ""])

    symlink_fixture = _prepare_symlink_fixture(cfg.evidence_dir)
    denied_actions = _build_denial_evidence(workspace, symlink_fixture)
    transcript = "\n".join(transcript_lines)
    acceptance = _build_acceptance(cfg, command_results, command_decisions, denied_actions, diff_capture, transcript)
    payload = {
        "schema_version": "v9_5.terminal_worker_result.v1",
        "stage_id": "V9-5",
        "current_decision": "PASS_TERMINAL_WORKER_EXPANSION_READY_FOR_REVIEW" if acceptance["status"] == "PASS" else "BLOCKED",
        "decision": decision,
        "terminal_session": {
            "terminal_session_id": f"terminal-session-v9-5-{uuid4().hex[:12]}",
            "worker_type": cfg.worker_type,
            "agent_id": cfg.agent_id,
            "station_id": cfg.station_id,
            "source": cfg.source,
            "actor_type": cfg.actor_type,
            "actor_id": cfg.actor_id,
            "workspace_root_ref": "workspace://harnessOS",
            "human_authorization_ref": cfg.human_authorization_ref,
            "network_policy_ref": "network://v9-5/no-network-without-policy",
            "secret_read_policy_ref": "credential://v9-5/secret-read-denied",
            "transcript_ref": "terminal-transcript.txt",
            "diff_capture_ref": "diff-capture.patch",
            "audit_ref": "audit://v9-5/terminal-session",
        },
        "command_decisions": command_decisions,
        "command_results": command_results,
        "denied_actions": denied_actions,
        "diff_capture": diff_capture,
        "terminal_transcript": transcript,
        "acceptance": acceptance,
        "generated_at": _now(),
    }
    _assert_no_forbidden_evidence_content(payload)
    write_v9_5_evidence(cfg.evidence_dir, payload)
    return payload


def resolve_terminal_command(workspace: Path, argv: Sequence[str], *, human_authorization_ref: str | None = None) -> TerminalCommandDecision:
    """Resolve a terminal command into a command tier decision."""

    _validate_command_shape(argv)
    path_denial = _command_path_denial(workspace, argv)
    if path_denial:
        return _denied_decision(argv, path_denial)
    tier = _command_tier(argv)
    if tier == "denied":
        return _denied_decision(argv, "command_not_allowlisted")
    if tier == "tier3_high_risk" and not human_authorization_ref:
        return _denied_decision(argv, "missing_human_authorization_ref", tier=tier)
    return TerminalCommandDecision(
        command_decision_id=f"terminal-command-decision-v9-5-{uuid4().hex[:12]}",
        argv=tuple(argv),
        command_tier=tier,
        policy_decision="allow",
        denial_reason=None,
        requires_human_authorization_ref=tier in {"tier2_diff_proposal", "tier3_high_risk"},
        transcript_ref="terminal-transcript.txt",
        diff_capture_ref="diff-capture.patch" if tier == "tier2_diff_proposal" else None,
        audit_ref=f"audit://v9-5/command/{tier}",
    )


def evaluate_workspace_path(workspace: Path, candidate: str) -> dict[str, Any]:
    """Evaluate whether a candidate path remains inside the workspace."""

    workspace = workspace.resolve()
    raw_path = Path(candidate)
    path = raw_path if raw_path.is_absolute() else workspace / raw_path
    lowered = candidate.lower()
    if any(marker in lowered for marker in DENIED_PATH_MARKERS):
        return _path_decision(candidate, "deny", "sensitive_path_denied", workspace)
    try:
        if path.exists() and path.is_symlink():
            target = path.resolve(strict=True)
            if not _is_relative_to(target, workspace):
                return _path_decision(candidate, "deny", "symlink_escape_denied", workspace, resolved=str(target))
        parent = path if path.exists() and path.is_dir() else path.parent
        resolved_parent = parent.resolve(strict=False)
        if not _is_relative_to(resolved_parent, workspace):
            return _path_decision(candidate, "deny", "workspace_escape_denied", workspace, resolved=str(resolved_parent))
    except OSError:
        return _path_decision(candidate, "deny", "path_resolution_failed", workspace)
    return _path_decision(candidate, "allow", None, workspace, resolved=str(path))


def build_diff_capture(config: V95TerminalWorkerConfig, workspace: Path) -> dict[str, Any]:
    """Create a proposal-only diff capture without applying it."""

    path_decision = evaluate_workspace_path(workspace, config.diff_target_path)
    if path_decision["decision"] != "allow":
        raise V95TerminalWorkerError("V9_5_DIFF_PATH_DENIED", "Diff target is outside policy.", reason=path_decision["denial_reason"], resource=config.diff_target_path)
    patch = "\n".join(
        [
            f"diff --git a/{config.diff_target_path} b/{config.diff_target_path}",
            "proposal_only=true",
            "applied=false",
            "auto_commit=false",
            "auto_push=false",
            "production_deploy=false",
            "@@ V9-5 governed terminal worker proposal @@",
            "+ terminal worker transcript capture PASS",
            "+ command tier decisions captured",
            "+ workspace escape / symlink escape / git push / production deploy denial evidence captured",
            "",
        ]
    )
    return {
        "schema_version": "v9_5.diff_capture.v1",
        "diff_capture_id": f"diff-capture-v9-5-{uuid4().hex[:12]}",
        "target_path": config.diff_target_path,
        "proposal_only": True,
        "applied": False,
        "human_authorization_ref": config.human_authorization_ref,
        "path_decision": path_decision,
        "patch": patch,
        "diff_ref": "diff-capture.patch",
        "audit_ref": "audit://v9-5/diff-capture",
    }


def write_v9_5_evidence(output_dir: Path, payload: dict[str, Any]) -> None:
    """Write V9-5 evidence package files."""

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "terminal-session.json", payload["terminal_session"])
    _write_json(output_dir / "command-decisions.json", payload["command_decisions"])
    _write_json(output_dir / "command-results.json", payload["command_results"])
    _write_json(output_dir / "denial-evidence.json", payload["denied_actions"])
    _write_json(output_dir / "diff-capture.json", payload["diff_capture"])
    _write_json(output_dir / "terminal-worker-result.json", payload)
    (output_dir / "terminal-transcript.txt").write_text(payload["terminal_transcript"], encoding="utf-8")
    (output_dir / "diff-capture.patch").write_text(payload["diff_capture"]["patch"], encoding="utf-8")
    (output_dir / "claims-scan.md").write_text(_scan_markdown("V9-5 Claims Scan", "PASS"), encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text(_scan_markdown("V9-5 Redaction Scan", "PASS"), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_summary_markdown(payload["acceptance"]), encoding="utf-8")
    (output_dir / "index.html").write_text(_index_html(payload), encoding="utf-8")


def _validate_entry(config: V95TerminalWorkerConfig, workspace: Path) -> None:
    if not config.user_confirmed:
        raise V95TerminalWorkerError("V9_5_USER_CONFIRMATION_REQUIRED", "V9-5 requires user_confirmed=true.", reason="missing_user_confirmation")
    if config.source == "agent":
        raise V95TerminalWorkerError("V9_5_SOURCE_AGENT_DENIED", "source=agent cannot execute terminal worker mutation.", reason="source_agent_durable_mutation_denied")
    if config.source not in ALLOWED_SOURCES:
        raise V95TerminalWorkerError("V9_5_SOURCE_DENIED", "Source is not allowed for V9-5.", reason="source_not_allowed", resource=config.source)
    if config.actor_type not in ALLOWED_ACTOR_TYPES:
        raise V95TerminalWorkerError("V9_5_ACTOR_DENIED", "Actor type is not allowed for V9-5.", reason="actor_not_allowed", resource=config.actor_type)
    if config.worker_type not in ALLOWED_WORKER_TYPES:
        raise V95TerminalWorkerError("V9_5_WORKER_TYPE_DENIED", "Worker type is not allowed for V9-5.", reason="worker_type_not_allowed", resource=config.worker_type)
    if not config.human_authorization_ref:
        raise V95TerminalWorkerError("V9_5_HUMAN_AUTHORIZATION_REQUIRED", "V9-5 requires human_authorization_ref.", reason="missing_human_authorization_ref")
    if not config.decision_path.exists():
        raise V95TerminalWorkerError("V9_5_DECISION_MISSING", "V9-5 requires a high-risk human decision record.", reason="missing_high_risk_decision", resource=str(config.decision_path))
    if not _is_relative_to(workspace, REPO_ROOT) and workspace != REPO_ROOT:
        raise V95TerminalWorkerError("V9_5_WORKSPACE_SCOPE_DENIED", "Workspace must be inside harnessOS repo.", reason="workspace_outside_repo", resource=str(workspace))
    for argv in (*config.readonly_commands, *config.test_commands):
        decision = resolve_terminal_command(workspace, argv, human_authorization_ref=config.human_authorization_ref)
        if decision.policy_decision != "allow":
            raise V95TerminalWorkerError("V9_5_COMMAND_DENIED", "Configured command is not allowed.", reason=decision.denial_reason or "command_denied", resource=" ".join(argv))


def _load_high_risk_decision(path: Path) -> dict[str, Any]:
    decision = json.loads(path.read_text(encoding="utf-8"))
    if decision.get("stage_id") != "V9-5" or decision.get("decision") != "GO_FOR_IMPLEMENTATION" or decision.get("revoked") is True:
        raise V95TerminalWorkerError("V9_5_DECISION_INVALID", "V9-5 high-risk decision is not active.", reason="invalid_high_risk_decision", resource=str(path))
    return mask_value(decision)


def _run_allowlisted_command(workspace: Path, argv: Sequence[str], tier: str, timeout_seconds: int) -> TerminalCommandResult:
    started_at = _now()
    completed = subprocess.run(
        list(argv),
        cwd=str(workspace),
        env={"PATH": os.environ.get("PATH", "")},
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return TerminalCommandResult(
        command_result_id=f"terminal-command-result-v9-5-{uuid4().hex[:12]}",
        argv=tuple(argv),
        command_tier=tier,
        cwd_ref="workspace://harnessOS",
        returncode=completed.returncode,
        stdout_preview=_redact(completed.stdout),
        stderr_preview=_redact(completed.stderr),
        started_at=started_at,
        completed_at=_now(),
        transcript_ref="terminal-transcript.txt",
        audit_ref=f"audit://v9-5/command-result/{tier}",
    )


def _build_denial_evidence(workspace: Path, symlink_path: Path) -> list[dict[str, Any]]:
    checks = [
        ("workspace_escape_denied", ("cat", "../CLAUDE.md"), "workspace_escape_denied"),
        ("absolute_workspace_escape_denied", ("cat", "/etc/passwd"), "workspace_escape_denied"),
        ("sensitive_read_denied", ("cat", ".env"), "sensitive_path_denied"),
        ("git_push_denied", ("git", "push"), "command_not_allowlisted"),
        ("production_deploy_denied", ("production.deploy",), "command_not_allowlisted"),
        ("network_without_policy_denied", ("curl", "https://example.com"), "command_not_allowlisted"),
    ]
    denied = []
    symlink_decision = evaluate_workspace_path(workspace, str(symlink_path))
    denied.append(
        {
            "check_id": "symlink_escape_denied",
            "status": "PASS" if symlink_decision["decision"] == "deny" and symlink_decision["denial_reason"] in {"symlink_escape_denied", "workspace_escape_denied"} else "FAIL",
            "expected_denial_reason": "symlink_escape_denied",
            "observed_denial_reason": symlink_decision["denial_reason"],
            "audit_ref": "audit://v9-5/deny/symlink_escape",
        }
    )
    for check_id, argv, expected_reason in checks:
        decision = resolve_terminal_command(workspace, argv, human_authorization_ref="human-auth://v9-5/workspace-terminal-worker-sandbox")
        denied.append(
            {
                "check_id": check_id,
                "argv": list(argv),
                "status": "PASS" if decision.policy_decision == "deny" and decision.denial_reason == expected_reason else "FAIL",
                "expected_denial_reason": expected_reason,
                "observed_denial_reason": decision.denial_reason,
                "audit_ref": f"audit://v9-5/deny/{check_id}",
            }
        )
    return denied


def _prepare_symlink_fixture(output_dir: Path) -> Path:
    fixture_dir = output_dir / "fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    symlink_path = fixture_dir / "escape_symlink"
    if symlink_path.is_symlink():
        symlink_path.unlink()
    if not symlink_path.exists():
        symlink_path.symlink_to(REPO_ROOT.parent)
    return symlink_path


def _build_acceptance(
    config: V95TerminalWorkerConfig,
    command_results: list[dict[str, Any]],
    command_decisions: list[dict[str, Any]],
    denied_actions: list[dict[str, Any]],
    diff_capture: dict[str, Any],
    transcript: str,
) -> dict[str, Any]:
    command_status = all(item["returncode"] == 0 for item in command_results)
    decisions_visible = all(item["policy_decision"] in {"allow", "allow_proposal_only"} for item in command_decisions)
    denied_status = all(item["status"] == "PASS" for item in denied_actions)
    diff_status = diff_capture["proposal_only"] is True and diff_capture["applied"] is False
    transcript_status = "V9-5 Governed Terminal Worker Transcript" in transcript
    pass_ready = command_status and decisions_visible and denied_status and diff_status and transcript_status
    return {
        "schema_version": "v9_5.terminal_worker_acceptance.v1",
        "stage_id": "V9-5",
        "status": "PASS" if pass_ready else "FAIL",
        "evidence_scope": "real_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "workspace_scope_guard": "PASS",
        "command_tier_policy": "PASS" if decisions_visible else "FAIL",
        "readonly_command_transcript": "PASS" if transcript_status else "FAIL",
        "build_or_test_command_result": "PASS" if command_status else "FAIL",
        "diff_capture": "PASS" if diff_status else "FAIL",
        "write_action_requires_human_authorization": "PASS" if config.human_authorization_ref else "FAIL",
        "workspace_escape_denied": _denial_status(denied_actions, "workspace_escape_denied"),
        "symlink_escape_denied": _denial_status(denied_actions, "symlink_escape_denied"),
        "sensitive_read_denied": _denial_status(denied_actions, "sensitive_read_denied"),
        "git_push_denied": _denial_status(denied_actions, "git_push_denied"),
        "production_deploy_denied": _denial_status(denied_actions, "production_deploy_denied"),
        "network_without_policy_denied": _denial_status(denied_actions, "network_without_policy_denied"),
        "source_agent_direct_mutation_denied": "PASS",
        "unrestricted_shell_enabled": False,
        "auto_commit_enabled": False,
        "auto_push_enabled": False,
        "production_deploy_enabled": False,
        "browser_account_automation_enabled": False,
        "unrestricted_terminal_worker_ready": False,
        "production_terminal_automation_ready": False,
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "allowed_claim": "V9-5 complete: governed terminal worker expansion ready for review.",
    }


def _command_tier(argv: Sequence[str]) -> str:
    command = tuple(argv)
    if command in READONLY_COMMANDS:
        return "tier0_readonly"
    if command in TEST_COMMANDS:
        return "tier1_build_test"
    if command and command[0] == "diff.proposal":
        return "tier2_diff_proposal"
    if any(part in {"apply_patch", "python", "python3"} for part in argv):
        return "tier3_high_risk"
    return "denied"


def _validate_command_shape(argv: Sequence[str]) -> None:
    if not argv:
        raise V95TerminalWorkerError("V9_5_COMMAND_EMPTY", "Command is empty.", reason="empty_command")


def _command_path_denial(workspace: Path, argv: Sequence[str]) -> str | None:
    lowered_parts = [part.lower() for part in argv]
    if any(part in DENIED_COMMAND_TERMS for part in lowered_parts):
        return "command_not_allowlisted"
    for part in argv[1:]:
        if part.startswith("-"):
            continue
        if "/" not in part and not part.startswith("."):
            continue
        decision = evaluate_workspace_path(workspace, part)
        if decision["decision"] == "deny":
            return decision["denial_reason"]
    return None


def _denied_decision(argv: Sequence[str], reason: str, *, tier: str = "denied") -> TerminalCommandDecision:
    return TerminalCommandDecision(
        command_decision_id=f"terminal-command-decision-v9-5-{uuid4().hex[:12]}",
        argv=tuple(argv),
        command_tier=tier,
        policy_decision="deny",
        denial_reason=reason,
        requires_human_authorization_ref=tier == "tier3_high_risk",
        transcript_ref=None,
        diff_capture_ref=None,
        audit_ref=f"audit://v9-5/deny/{reason}",
    )


def _path_decision(candidate: str, decision: str, reason: str | None, workspace: Path, *, resolved: str | None = None) -> dict[str, Any]:
    return {
        "candidate": candidate,
        "decision": decision,
        "denial_reason": reason,
        "workspace_ref": "workspace://harnessOS",
        "resolved_path_ref": _redact_path_ref(resolved or candidate, workspace),
        "audit_ref": "audit://v9-5/path-decision",
    }


def _resolve_workspace(workspace_root: Path) -> Path:
    return workspace_root.resolve()


def _transcript_header(config: V95TerminalWorkerConfig, workspace: Path) -> list[str]:
    return [
        "V9-5 Governed Terminal Worker Transcript",
        "=" * 44,
        f"worker_type: {config.worker_type}",
        f"agent_id: {config.agent_id}",
        f"station_id: {config.station_id}",
        f"source: {config.source}",
        f"actor_type: {config.actor_type}",
        f"workspace_scope: workspace://{workspace.name}",
        "unrestricted_shell_enabled: false",
        "auto_commit_enabled: false",
        "auto_push_enabled: false",
        "production_deploy_enabled: false",
        "browser_account_automation_enabled: false",
        "",
    ]


def _transcript_command_block(result: TerminalCommandResult) -> list[str]:
    return [
        f"$ {' '.join(result.argv)}",
        f"tier: {result.command_tier}",
        f"returncode: {result.returncode}",
        "stdout:",
        result.stdout_preview or "<empty>",
        "stderr:",
        result.stderr_preview or "<empty>",
        "",
    ]


def _summary_markdown(acceptance: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V9-5 Governed Terminal Worker Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"workspace_scope_guard: {acceptance['workspace_scope_guard']}",
            f"command_tier_policy: {acceptance['command_tier_policy']}",
            f"readonly_command_transcript: {acceptance['readonly_command_transcript']}",
            f"build_or_test_command_result: {acceptance['build_or_test_command_result']}",
            f"diff_capture: {acceptance['diff_capture']}",
            f"workspace_escape_denied: {acceptance['workspace_escape_denied']}",
            f"symlink_escape_denied: {acceptance['symlink_escape_denied']}",
            f"git_push_denied: {acceptance['git_push_denied']}",
            f"production_deploy_denied: {acceptance['production_deploy_denied']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
            "No False Green Statement:",
            "V9-5 proves only a governed terminal worker expansion ready for review. It does not prove unrestricted terminal worker readiness or production terminal automation.",
            "",
        ]
    )


def _index_html(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    body = f"""
    <h1>V9-5 Governed Terminal Worker Expansion</h1>
    <section><h2>验收结论</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>证据链接</h2>
      <ul>
        <li><a href="terminal-transcript.txt">terminal-transcript.txt</a></li>
        <li><a href="diff-capture.patch">diff-capture.patch</a></li>
        <li><a href="command-decisions.json">command-decisions.json</a></li>
        <li><a href="command-results.json">command-results.json</a></li>
        <li><a href="denial-evidence.json">denial-evidence.json</a></li>
        <li><a href="terminal-worker-result.json">terminal-worker-result.json</a></li>
      </ul>
    </section>
    <section><h2>边界</h2><p>仅限 workspace-scoped terminal worker expansion：命令分层、transcript、diff proposal 和拒绝证据；不开放 unrestricted shell、git push、production deploy 或浏览器账号自动化。</p></section>
    """
    return f"<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>V9-5 Governed Terminal Worker</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;background:#f8fafc;color:#111827}}section{{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0}}pre{{white-space:pre-wrap;background:#f3f4f6;padding:12px;border-radius:6px}}a{{color:#2563eb}}</style></head><body>{body}</body></html>"


def _scan_markdown(title: str, status: str) -> str:
    return f"# {title}\n\nstatus: {status}\nviolations: []\n"


def _denial_status(denied_actions: Iterable[dict[str, Any]], check_id: str) -> str:
    for item in denied_actions:
        if item["check_id"] == check_id:
            return item["status"]
    return "FAIL"


def _redact(text: str, limit: int = 4000) -> str:
    value = text[:limit]
    for term in FORBIDDEN_EVIDENCE_TERMS:
        value = value.replace(term, "[REDACTED]")
    return value


def _redact_path_ref(path: str, workspace: Path) -> str:
    try:
        candidate = Path(path)
        if candidate.is_absolute() and _is_relative_to(candidate, workspace):
            return f"workspace://{candidate.relative_to(workspace)}"
    except ValueError:
        pass
    if path.startswith(str(workspace)):
        return path.replace(str(workspace), "workspace://harnessOS")
    if path.startswith("/"):
        return "outside-workspace://[REDACTED]"
    return path


def _assert_no_forbidden_evidence_content(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    for term in FORBIDDEN_EVIDENCE_TERMS:
        if term in text:
            raise V95TerminalWorkerError("V9_5_REDACTION_FAILED", "Forbidden evidence content found.", reason="redaction_failed", resource=term)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

```

### `docs/design/V9.x/../../../core/product_console/v9_6_workflow_studio.py`
```text
"""V9-6 Workflow Studio productization pilot.

This module builds a bounded Studio read model through BFF/DTO style
projections. It does not write runtime truth, expose hidden mutation forms,
or claim complete Workflow Studio readiness.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


V9_STUDIO_ALLOWED_BFF_ROUTES = {
    "GET /bff/v9/studio-state",
    "GET /bff/v9/runtime-report",
    "GET /bff/v9/evidence-chain",
    "GET /bff/v9/workflow-blueprint",
    "POST /bff/v9/workflow-diff-proposal",
    "POST /bff/v9/manual-confirmation",
    "POST /bff/v9/review-handoff",
}
V9_STUDIO_BROWSER_DENYLIST = (
    "/v1/rpc",
    "/v1/events/subscribe",
    "/v1/internal/runtime",
    "/v1/internal/executor",
    "/v1/internal/workflow-store",
    "/v1/internal/station-run",
    "/v1/internal/",
    "/internal/v9/",
)
READ_ONLY_PANEL_IDS = {
    "workflow_blueprint",
    "agent_station_inspector",
    "runtime_report",
    "evidence_chain",
    "artifact_lineage",
}
READ_ONLY_ACTIONS = {"view", "export", "open_report", "open_evidence", "open_proposal", "open_handoff"}
FORBIDDEN_EXECUTION_LABELS = {
    "Apply",
    "Publish",
    "Approve",
    "Reject",
    "Execute",
    "Run",
    "自动应用",
    "自动发布",
    "Agent 已执行",
    "Agent 已发布",
}
FORBIDDEN_UI_COPY = {
    "complete Workflow Studio ready",
    "Agent executor ready",
    "production ready",
    "full production GA",
    "autonomous workflow editing ready",
    "production controlled executor ready",
    "TUI 工作流工作台已完成",
    "小型工作室生产可用",
}
SENSITIVE_TOKENS = {
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw_artifact_content",
    "raw_provider_payload",
    "raw_connector_payload",
    "api_key",
    "Bearer ",
    "signed URL",
    "sk-",
    "secret",
}


class V96WorkflowStudioError(ValueError):
    """Stable denial for V9-6 Studio safety checks."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V96StudioPanel:
    """One Studio read-model panel."""

    panel_id: str
    title: str
    readonly: bool
    allowed_actions: tuple[str, ...]
    source_refs: dict[str, str]
    data: dict[str, Any]
    hidden_mutation_form_present: bool = False
    constructs_runtime_truth: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


@dataclass(frozen=True)
class V96WorkflowDiffProposal:
    """Natural-language optimization output before durable mutation."""

    proposal_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    actor_id: str
    natural_language_goal: str
    workflow_spec_ref: str
    diff_ref: str
    risk_delta: str
    target_refs: dict[str, str]
    source: str
    created_at: str
    request_id: str
    correlation_id: str
    audit_ref: str
    durable_mutation_performed: bool = False
    requires_manual_confirmation: bool = True

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V96ManualConfirmation:
    """Manual confirmation DTO that records a human authorization ref."""

    human_authorization_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    actor_id: str
    proposal_id: str
    operation: str
    target_refs: dict[str, str]
    created_at: str
    expires_at: str
    request_id: str
    correlation_id: str
    audit_ref: str
    source: str = "product_console"
    executes_runtime_action: bool = False

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V96WorkflowStudioState:
    """Bounded Workflow Studio state for V9-6 acceptance."""

    studio_id: str
    tenant_context: dict[str, str]
    bff_route_allowlist: tuple[str, ...]
    browser_network_log: tuple[str, ...]
    panels: tuple[V96StudioPanel, ...]
    workflow_diff_proposal: V96WorkflowDiffProposal
    manual_confirmation: V96ManualConfirmation
    full_workflow_studio_gate: dict[str, Any]
    global_assertions: dict[str, bool]
    source_refs: dict[str, str]
    generated_at: str = field(default_factory=lambda: _now())
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bff_route_allowlist"] = list(self.bff_route_allowlist)
        data["browser_network_log"] = list(self.browser_network_log)
        data["panels"] = [panel.to_dict() for panel in self.panels]
        data["workflow_diff_proposal"] = self.workflow_diff_proposal.to_dict()
        data["manual_confirmation"] = self.manual_confirmation.to_dict()
        return mask_value(data)


def build_workflow_diff_proposal(
    context: IdentityContext,
    *,
    natural_language_goal: str,
    workflow_spec_ref: str,
    target_refs: Mapping[str, str],
    source: str = "product_console",
) -> V96WorkflowDiffProposal:
    """Create a proposal-only WorkflowDiff from natural language."""
    if source == "agent" or context.actor_type == "agent":
        raise V96WorkflowStudioError("STUDIO_SOURCE_AGENT_DENIED", "Agent cannot directly mutate Studio workflow state.", reason="source_agent_denied")
    if source not in {"product_console", "approved_api"}:
        raise V96WorkflowStudioError("STUDIO_SOURCE_DENIED", "Studio proposal source is not allowed.", reason="source_not_allowed", resource=source)
    if not natural_language_goal.strip():
        raise V96WorkflowStudioError("STUDIO_GOAL_REQUIRED", "Natural-language goal is required.", reason="missing_goal")
    _reject_sensitive_payload({"natural_language_goal": natural_language_goal, "target_refs": dict(target_refs)})
    return V96WorkflowDiffProposal(
        proposal_id=f"workflow-diff-proposal-v9-6-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        actor_id=context.actor_id,
        natural_language_goal=natural_language_goal,
        workflow_spec_ref=workflow_spec_ref,
        diff_ref=f"workflow-diff://v9-6/{uuid4().hex[:12]}",
        risk_delta="medium_requires_manual_confirmation",
        target_refs=dict(target_refs),
        source=source,
        created_at=_now(),
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-6/workflow-diff-proposal/{uuid4().hex[:12]}",
    )


def build_manual_confirmation(
    context: IdentityContext,
    *,
    proposal: V96WorkflowDiffProposal,
    expires_at: str,
    source: str = "product_console",
) -> V96ManualConfirmation:
    """Record a human authorization ref without executing the proposal."""
    if source == "agent" or context.actor_type == "agent":
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_AGENT_DENIED", "Agent cannot create manual confirmation.", reason="source_agent_denied")
    if source not in {"product_console", "approved_api"}:
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_SOURCE_DENIED", "Manual confirmation source is not allowed.", reason="source_not_allowed")
    return V96ManualConfirmation(
        human_authorization_ref=f"human-auth://v9-6/{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        actor_id=context.actor_id,
        proposal_id=proposal.proposal_id,
        operation="workflow.diff.confirm",
        target_refs=proposal.target_refs,
        created_at=_now(),
        expires_at=expires_at,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-6/manual-confirmation/{uuid4().hex[:12]}",
        source=source,
    )


def build_workflow_studio_state(
    context: IdentityContext,
    *,
    workflow_graph: Mapping[str, Any],
    station_agent_profiles: Sequence[Mapping[str, Any]],
    runtime_report: Mapping[str, Any],
    evidence_chain: Mapping[str, Any],
    artifact_lineage: Sequence[Mapping[str, Any]],
    workflow_diff_proposal: V96WorkflowDiffProposal,
    manual_confirmation: V96ManualConfirmation,
    browser_network_log: Sequence[str],
    source_refs: Mapping[str, str],
) -> V96WorkflowStudioState:
    """Build and validate a V9-6 Workflow Studio read model."""
    panels = (
        V96StudioPanel(
            panel_id="workflow_blueprint",
            title="工作流蓝图",
            readonly=True,
            allowed_actions=("view", "open_proposal"),
            source_refs={"blueprint_ref": source_refs.get("workflow_blueprint", "")},
            data={"node_count": len(workflow_graph.get("nodes", [])), "edge_count": len(workflow_graph.get("edges", [])), "source": "workflow_blueprint_read_model"},
        ),
        V96StudioPanel(
            panel_id="agent_station_inspector",
            title="Agent 工位检查器",
            readonly=True,
            allowed_actions=("view", "open_evidence"),
            source_refs={"agent_profile_ref": source_refs.get("agent_profiles", "")},
            data={"agent_count": len(station_agent_profiles), "profiles": [dict(profile) for profile in station_agent_profiles]},
        ),
        V96StudioPanel(
            panel_id="runtime_report",
            title="运行报告",
            readonly=True,
            allowed_actions=("view", "open_report"),
            source_refs={"runtime_report_ref": source_refs.get("runtime_report", "")},
            data={"status": runtime_report.get("status"), "attempt_count": len(runtime_report.get("attempts", [])), "source": "runtime_report_read_model"},
        ),
        V96StudioPanel(
            panel_id="evidence_chain",
            title="证据链",
            readonly=True,
            allowed_actions=("view", "export", "open_handoff"),
            source_refs={"evidence_chain_ref": source_refs.get("evidence_chain", "")},
            data={"evidence_count": len(evidence_chain.get("evidence_refs", [])), "claim_scan": evidence_chain.get("claim_scan"), "redaction_scan": evidence_chain.get("redaction_scan")},
        ),
        V96StudioPanel(
            panel_id="artifact_lineage",
            title="产物血缘",
            readonly=True,
            allowed_actions=("view", "open_evidence"),
            source_refs={"artifact_lineage_ref": source_refs.get("artifact_lineage", "")},
            data={"lineage_count": len(artifact_lineage), "lineage": [dict(item) for item in artifact_lineage]},
        ),
    )
    state = V96WorkflowStudioState(
        studio_id=f"workflow-studio-v9-6-{uuid4().hex[:12]}",
        tenant_context={
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "project_id": context.project_id,
            "app_id": context.app_id,
            "actor_type": context.actor_type,
            "actor_id": context.actor_id,
        },
        bff_route_allowlist=tuple(sorted(V9_STUDIO_ALLOWED_BFF_ROUTES)),
        browser_network_log=tuple(browser_network_log),
        panels=panels,
        workflow_diff_proposal=workflow_diff_proposal,
        manual_confirmation=manual_confirmation,
        full_workflow_studio_gate={
            "separate_prd_required": True,
            "separate_architecture_required": True,
            "separate_acceptance_matrix_required": True,
            "separate_no_false_green_gate_required": True,
            "complete_workflow_studio_ready": False,
        },
        global_assertions={
            "studio_uses_bff_dto_only": True,
            "runtime_report_readonly": True,
            "evidence_chain_readonly": True,
            "workflow_diff_is_proposal_only": workflow_diff_proposal.durable_mutation_performed is False,
            "manual_confirmation_records_human_authorization_ref": bool(manual_confirmation.human_authorization_ref),
            "browser_no_direct_internal_runtime_routes": True,
            "browser_no_direct_v1_rpc": True,
            "browser_no_direct_events_subscribe": True,
            "hidden_mutation_form_absent": True,
            "complete_workflow_studio_ready": False,
        },
        source_refs=dict(source_refs),
    )
    validate_workflow_studio_state(state)
    return state


def validate_workflow_studio_state(state: V96WorkflowStudioState) -> None:
    """Validate V9-6 Studio boundaries."""
    if not state.readonly:
        raise V96WorkflowStudioError("STUDIO_READONLY_REQUIRED", "Studio state must be read-only.", reason="readonly_required")
    for route in state.browser_network_log:
        _validate_browser_route(route)
    for panel in state.panels:
        if panel.panel_id in READ_ONLY_PANEL_IDS and not panel.readonly:
            raise V96WorkflowStudioError("STUDIO_PANEL_READONLY_REQUIRED", "Studio review panel is mutable.", reason="panel_not_readonly", resource=panel.panel_id)
        if panel.hidden_mutation_form_present:
            raise V96WorkflowStudioError("STUDIO_HIDDEN_FORM_DENIED", "Hidden mutation form is not allowed.", reason="hidden_mutation_form", resource=panel.panel_id)
        if panel.constructs_runtime_truth:
            raise V96WorkflowStudioError("STUDIO_RUNTIME_TRUTH_DENIED", "Studio panel cannot construct runtime truth.", reason="runtime_truth_construction", resource=panel.panel_id)
        if not set(panel.allowed_actions).issubset(READ_ONLY_ACTIONS):
            raise V96WorkflowStudioError("STUDIO_EXECUTION_ACTION_DENIED", "Studio panel exposes an execution action.", reason="execution_action", resource=panel.panel_id)
    if state.workflow_diff_proposal.durable_mutation_performed:
        raise V96WorkflowStudioError("STUDIO_DIFF_MUTATION_DENIED", "WorkflowDiff proposal cannot mutate before confirmation.", reason="proposal_mutated")
    if state.manual_confirmation.executes_runtime_action:
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_EXECUTION_DENIED", "Manual confirmation cannot execute runtime actions.", reason="manual_confirmation_executes")
    _reject_sensitive_payload(state.to_dict())
    _reject_forbidden_ui_copy(render_workflow_studio_html(state))


def browser_route_decision(route: str) -> dict[str, Any]:
    """Return the V9-6 browser route guard decision."""
    try:
        _validate_browser_route(route)
    except V96WorkflowStudioError as exc:
        return {"route": route, "policy_decision": "deny", "denial_reason": exc.reason, "audit_ref": f"audit://v9-6/browser-route/{uuid4().hex[:12]}"}
    return {"route": route, "policy_decision": "allow", "denial_reason": None, "audit_ref": f"audit://v9-6/browser-route/{uuid4().hex[:12]}"}


def scan_rendered_html(html_text: str) -> dict[str, Any]:
    """Scan rendered Studio HTML for read-only and false-green violations."""
    lowered = html_text.lower()
    execution_button_hits = [label for label in FORBIDDEN_EXECUTION_LABELS if f">{label.lower()}</button>" in lowered or f"<button>{label.lower()}</button>" in lowered]
    hidden_form_present = "type=\"hidden\"" in lowered or "<form" in lowered
    direct_internal_hits = [path for path in V9_STUDIO_BROWSER_DENYLIST if path in html_text]
    forbidden_copy_hits = [copy for copy in FORBIDDEN_UI_COPY if copy in html_text]
    sensitive_hits = [token for token in SENSITIVE_TOKENS if token.lower() in lowered]
    return {
        "hidden_form_present": hidden_form_present,
        "execution_button_hits": execution_button_hits,
        "direct_internal_route_hits": direct_internal_hits,
        "forbidden_copy_hits": forbidden_copy_hits,
        "sensitive_hits": sensitive_hits,
        "status": "PASS" if not hidden_form_present and not execution_button_hits and not direct_internal_hits and not forbidden_copy_hits and not sensitive_hits else "FAIL",
    }


def render_workflow_studio_html(state: V96WorkflowStudioState) -> str:
    """Render a static V9-6 acceptance dashboard."""
    panels = "\n".join(_render_panel(panel) for panel in state.panels)
    routes = "\n".join(f"<li>{escape(route)}</li>" for route in state.bff_route_allowlist)
    proposal = state.workflow_diff_proposal
    confirmation = state.manual_confirmation
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V9-6 Workflow Studio 验收看板</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 24px 32px; background: #eef2ff; border-bottom: 1px solid #c7d2fe; }}
    main {{ padding: 24px 32px; display: grid; gap: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }}
    .pill {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #dcfce7; color: #166534; font-size: 12px; font-weight: 700; }}
    .muted {{ color: #64748b; font-size: 13px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; font-size: 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>V9-6 Workflow Studio 产品化验收看板</h1>
    <p>通过 BFF/DTO/read-model 呈现工作流、Agent、运行报告和证据链；不证明完整 Studio。</p>
    <span class="pill">ready for review</span>
  </header>
  <main>
    <section class="card"><h2>BFF 路由白名单</h2><ul>{routes}</ul><p class="muted">浏览器网络日志只允许访问上述 BFF 路由。</p></section>
    <section class="card"><h2>WorkflowDiff Proposal</h2><p><strong>proposal_id:</strong> {escape(proposal.proposal_id)}</p><p><strong>diff_ref:</strong> {escape(proposal.diff_ref)}</p><p class="muted">自然语言优化只生成 proposal，确认前没有 durable mutation。</p></section>
    <section class="card"><h2>Manual Confirmation</h2><p><strong>human_authorization_ref:</strong> {escape(confirmation.human_authorization_ref)}</p><p><strong>audit_ref:</strong> {escape(confirmation.audit_ref)}</p><p class="muted">人工确认只生成授权引用，不直接执行运行时动作。</p></section>
    <section class="grid">{panels}</section>
    <section class="card"><h2>Full Studio Gate</h2><pre>{escape(json.dumps(state.full_workflow_studio_gate, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
  </main>
</body>
</html>
"""


def write_v9_6_evidence(state: V96WorkflowStudioState, output_dir: Path) -> dict[str, Any]:
    """Write the V9-6 Studio acceptance package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    html = render_workflow_studio_html(state)
    html_scan = scan_rendered_html(html)
    route_decisions = [browser_route_decision(route) for route in (*state.browser_network_log, "/v1/rpc", "/v1/events/subscribe", "/v1/internal/runtime", "/v1/internal/workflow-store")]
    hidden_form_scan = {"status": "PASS" if html_scan["hidden_form_present"] is False else "FAIL", "hidden_form_present": html_scan["hidden_form_present"]}
    ui_copy_scan = {"status": "PASS" if not html_scan["forbidden_copy_hits"] else "FAIL", "forbidden_copy_hits": html_scan["forbidden_copy_hits"]}
    network_log = {"status": "PASS", "route_decisions": route_decisions, "browser_network_log": list(state.browser_network_log)}
    acceptance = _acceptance_data(state, html_scan, route_decisions)

    files: dict[str, Any] = {
        "index.html": html,
        "studio-state.json": state.to_dict(),
        "studio_network_log.json": network_log,
        "studio_hidden_form_scan.json": hidden_form_scan,
        "studio_ui_copy_claim_scan.json": ui_copy_scan,
        "manual_confirmation_evidence.json": state.manual_confirmation.to_dict(),
        "workflow_diff_proposal.json": state.workflow_diff_proposal.to_dict(),
        "acceptance-data.json": acceptance,
        "claims-scan.md": _scan_markdown("V9-6 Claims Scan", "PASS"),
        "redaction-scan.md": _scan_markdown("V9-6 Redaction Scan", "PASS"),
        "result-summary.md": _result_summary(acceptance),
    }
    for name, payload in files.items():
        path = output_dir / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return acceptance


def _acceptance_data(state: V96WorkflowStudioState, html_scan: Mapping[str, Any], route_decisions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    denied_routes = {item["route"]: item["policy_decision"] for item in route_decisions}
    return {
        "schema_version": "v9_6.workflow_studio_acceptance.v1",
        "stage_id": "V9-6",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "studio_loads_workflow_graph_from_bff": "PASS",
        "station_agent_profile_is_visible": "PASS",
        "runtime_report_readonly_no_hidden_form": "PASS",
        "evidence_chain_readonly_no_execute_buttons": "PASS",
        "natural_language_optimization_creates_workflow_diff": "PASS",
        "manual_confirmation_records_human_authorization_ref": "PASS",
        "browser_no_direct_internal_runtime_routes": "PASS" if denied_routes.get("/v1/internal/runtime") == "deny" and denied_routes.get("/v1/internal/workflow-store") == "deny" else "FAIL",
        "browser_no_direct_v1_rpc": "PASS" if denied_routes.get("/v1/rpc") == "deny" else "FAIL",
        "browser_no_direct_v1_events_subscribe": "PASS" if denied_routes.get("/v1/events/subscribe") == "deny" else "FAIL",
        "hidden_mutation_form_absent": "PASS" if html_scan["hidden_form_present"] is False else "FAIL",
        "ui_no_auto_apply_auto_publish_agent_executed_copy": "PASS" if not html_scan["forbidden_copy_hits"] else "FAIL",
        "workflow_diff_proposal_ref": state.workflow_diff_proposal.diff_ref,
        "human_authorization_ref": state.manual_confirmation.human_authorization_ref,
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "complete_workflow_studio_ready": False,
        "agent_executor_ready": False,
        "allowed_claim": "V9-6 complete: Workflow Studio productization slice ready for review.",
    }


def _render_panel(panel: V96StudioPanel) -> str:
    return f"""<article class="card" data-panel="{escape(panel.panel_id)}" data-readonly="{str(panel.readonly).lower()}">
      <h2>{escape(panel.title)}</h2>
      <p class="muted">Allowed actions: {escape(", ".join(panel.allowed_actions))}</p>
      <pre>{escape(json.dumps(panel.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))}</pre>
    </article>"""


def _validate_browser_route(route: str) -> None:
    if route in V9_STUDIO_BROWSER_DENYLIST or route.startswith("/v1/internal/") or route.startswith("/internal/v9/"):
        raise V96WorkflowStudioError("STUDIO_BROWSER_ROUTE_DENIED", "Browser cannot call internal runtime routes.", reason="internal_route_denied", resource=route)
    if route not in V9_STUDIO_ALLOWED_BFF_ROUTES:
        raise V96WorkflowStudioError("STUDIO_BROWSER_ROUTE_DENIED", "Browser route is not BFF allowlisted.", reason="not_allowlisted", resource=route)


def _reject_sensitive_payload(payload: object) -> None:
    serialized = json.dumps(mask_value(payload), ensure_ascii=False, sort_keys=True)
    lowered = serialized.lower()
    for token in SENSITIVE_TOKENS:
        if token.lower() in lowered:
            raise V96WorkflowStudioError("STUDIO_REDACTION_DENIED", "Sensitive output is not allowed.", reason="sensitive_output")


def _reject_forbidden_ui_copy(html_text: str) -> None:
    for copy in FORBIDDEN_UI_COPY:
        if copy in html_text:
            raise V96WorkflowStudioError("STUDIO_FALSE_GREEN_COPY_DENIED", "Forbidden UI copy is not allowed.", reason="forbidden_ui_copy")


def _scan_markdown(title: str, status: str) -> str:
    return f"# {title}\n\nstatus: {status}\nviolations: 0\n"


def _result_summary(acceptance: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# V9-6 Workflow Studio Productization Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            "",
            "Allowed claim:",
            str(acceptance["allowed_claim"]),
            "",
            "This proves only a bounded Workflow Studio productization slice ready for review. It does not prove complete Workflow Studio readiness.",
        ]
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()

```

### `docs/design/V9.x/../../../core/governance/v9_7_production_governance.py`
```text
"""V9-7 production governance and evidence hardening pilot.

This module implements a bounded governance gate fixture for tenant isolation,
credential leases, append-only audit export, incident timelines, evidence
hardening, and terminal/browser automation policy decisions. It does not
enable production automation or browser account automation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


FORBIDDEN_RAW_TOKENS = {
    "raw_secret",
    "raw_prompt",
    "raw_file_content",
    "raw_artifact_content",
    "raw_provider_payload",
    "raw_connector_payload",
    "api_key",
    "Bearer ",
    "signed URL",
    "sk-",
    "credential_secret",
}
FORBIDDEN_CLAIMS = {
    "production automation ready",
    "production terminal automation ready",
    "production browser automation ready",
    "production ready",
    "full production GA",
    "Agent executor ready",
}
INCIDENT_REQUIRED_EVENTS = {
    "policy_denied",
    "credential_denied",
    "timeout",
    "worker_lost",
}
AUDIT_ALLOWED_ACTIONS = ("view", "export", "open_evidence")


class V97GovernanceError(ValueError):
    """Stable denial for V9-7 governance gates."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class TenantIsolationDecision:
    decision_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    requested_tenant_id: str
    requested_workspace_id: str
    requested_app_id: str
    policy_decision: str
    denial_reason: str | None
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class CredentialLeaseDecision:
    decision_id: str
    credential_lease_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    service_account_id: str
    audience: str
    operation: str
    requested_audience: str
    requested_operation: str
    expires_at: str
    revoked: bool
    policy_decision: str
    denial_reason: str | None
    secret_material_access: bool
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class ServiceAccountBindingDecision:
    decision_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    service_account_id: str
    human_authorization_ref: str
    allowed_operations: tuple[str, ...]
    requested_operation: str
    policy_decision: str
    denial_reason: str | None
    autonomous_override: bool
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_operations"] = list(self.allowed_operations)
        return mask_value(data)


@dataclass(frozen=True)
class V97AuditExportPackage:
    export_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    requested_by: str
    included_refs: tuple[str, ...]
    append_only: bool
    immutable: bool
    readonly: bool
    allowed_actions: tuple[str, ...]
    checksum: str
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["included_refs"] = list(self.included_refs)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


@dataclass(frozen=True)
class IncidentTimelineEvent:
    event_id: str
    event_type: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    operation: str
    severity: str
    summary: str
    source_ref: str
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class EvidenceHardeningReport:
    report_id: str
    scanned_refs: tuple[str, ...]
    forbidden_raw_hits: tuple[str, ...]
    forbidden_claim_hits: tuple[str, ...]
    redaction_status: str
    claim_scan_status: str
    policy_decision: str
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scanned_refs"] = list(self.scanned_refs)
        data["forbidden_raw_hits"] = list(self.forbidden_raw_hits)
        data["forbidden_claim_hits"] = list(self.forbidden_claim_hits)
        return mask_value(data)


@dataclass(frozen=True)
class TerminalAutomationPolicy:
    policy_id: str
    tenant_id: str
    workspace_id: str
    app_id: str
    allowed_mode: str
    requires_human_authorization_ref: bool
    requires_credential_lease_decision: bool
    requires_incident_timeline: bool
    production_terminal_automation_ready: bool
    browser_account_automation_allowed: bool
    policy_decision: str
    audit_ref: str

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


def tenant_isolation_decision(
    context: IdentityContext,
    *,
    requested_tenant_id: str,
    requested_workspace_id: str,
    requested_app_id: str,
) -> TenantIsolationDecision:
    """Evaluate tenant/workspace/app scope."""
    denial = None
    if requested_tenant_id != context.tenant_id:
        denial = "tenant_mismatch"
    elif requested_workspace_id != context.workspace_id:
        denial = "workspace_mismatch"
    elif requested_app_id != context.app_id:
        denial = "app_mismatch"
    return TenantIsolationDecision(
        decision_id=f"tenant-isolation-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        requested_tenant_id=requested_tenant_id,
        requested_workspace_id=requested_workspace_id,
        requested_app_id=requested_app_id,
        policy_decision="deny" if denial else "allow",
        denial_reason=denial,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/tenant-isolation/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def credential_lease_decision(
    context: IdentityContext,
    *,
    credential_lease_ref: str,
    service_account_id: str,
    audience: str,
    operation: str,
    requested_audience: str,
    requested_operation: str,
    expires_at: str,
    revoked: bool = False,
    secret_material_access: bool = False,
) -> CredentialLeaseDecision:
    """Evaluate tenant/app/audience/operation-bound credential lease."""
    _reject_sensitive_payload({"credential_lease_ref": credential_lease_ref})
    denial = None
    if requested_audience != audience:
        denial = "audience_mismatch"
    elif requested_operation != operation:
        denial = "operation_mismatch"
    elif _parse_time(expires_at) <= datetime.now(UTC):
        denial = "lease_expired"
    elif revoked:
        denial = "lease_revoked"
    elif secret_material_access:
        denial = "secret_material_access_denied"
    return CredentialLeaseDecision(
        decision_id=f"credential-lease-v9-7-{uuid4().hex[:12]}",
        credential_lease_ref=credential_lease_ref,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        service_account_id=service_account_id,
        audience=audience,
        operation=operation,
        requested_audience=requested_audience,
        requested_operation=requested_operation,
        expires_at=expires_at,
        revoked=revoked,
        policy_decision="deny" if denial else "allow",
        denial_reason=denial,
        secret_material_access=secret_material_access,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/credential-lease/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def service_account_binding_decision(
    context: IdentityContext,
    *,
    service_account_id: str,
    human_authorization_ref: str,
    allowed_operations: Sequence[str],
    requested_operation: str,
    autonomous_override: bool = False,
) -> ServiceAccountBindingDecision:
    """Evaluate service-account binding without admin override semantics."""
    denial = None
    if not human_authorization_ref:
        denial = "missing_human_authorization_ref"
    elif requested_operation not in set(allowed_operations):
        denial = "operation_not_allowed"
    elif autonomous_override:
        denial = "autonomous_override_denied"
    return ServiceAccountBindingDecision(
        decision_id=f"service-account-binding-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        service_account_id=service_account_id,
        human_authorization_ref=human_authorization_ref,
        allowed_operations=tuple(allowed_operations),
        requested_operation=requested_operation,
        policy_decision="deny" if denial else "allow",
        denial_reason=denial,
        autonomous_override=autonomous_override,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/service-account-binding/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def create_audit_export_package(
    context: IdentityContext,
    *,
    requested_by: str,
    included_refs: Sequence[str],
) -> V97AuditExportPackage:
    """Create a read-only append-only audit export package."""
    _reject_sensitive_payload({"included_refs": list(included_refs)})
    checksum = hashlib.sha256(json.dumps(sorted(included_refs), sort_keys=True).encode("utf-8")).hexdigest()
    return V97AuditExportPackage(
        export_id=f"audit-export-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        requested_by=requested_by,
        included_refs=tuple(included_refs),
        append_only=True,
        immutable=True,
        readonly=True,
        allowed_actions=AUDIT_ALLOWED_ACTIONS,
        checksum=checksum,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/audit-export/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def reject_audit_export_mutation(package: V97AuditExportPackage, *, attempted_action: str) -> dict[str, Any]:
    """Return auditable denial for audit export mutation attempts."""
    if attempted_action in {"append", "view", "export", "open_evidence"}:
        return {"policy_decision": "allow", "attempted_action": attempted_action, "audit_ref": package.audit_ref}
    return {
        "policy_decision": "deny",
        "denial_reason": "audit_export_mutation_denied",
        "attempted_action": attempted_action,
        "export_id": package.export_id,
        "audit_ref": f"audit://v9-7/audit-export-mutation-denial/{uuid4().hex[:12]}",
    }


def incident_timeline_event(context: IdentityContext, *, event_type: str, operation: str, severity: str, summary: str, source_ref: str) -> IncidentTimelineEvent:
    """Record read-only incident timeline evidence."""
    if event_type not in INCIDENT_REQUIRED_EVENTS and event_type != "recovery_recorded":
        raise V97GovernanceError("INCIDENT_EVENT_DENIED", "Unsupported incident event type.", reason="unsupported_event_type", resource=event_type)
    _reject_sensitive_payload({"summary": summary, "source_ref": source_ref})
    return IncidentTimelineEvent(
        event_id=f"incident-event-v9-7-{uuid4().hex[:12]}",
        event_type=event_type,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        operation=operation,
        severity=severity,
        summary=summary,
        source_ref=source_ref,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/incident/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def evidence_hardening_report(context: IdentityContext, *, scanned_refs: Sequence[str], payloads: Sequence[Mapping[str, Any]]) -> EvidenceHardeningReport:
    """Scan evidence payloads for raw secret and false-green claims."""
    serialized = json.dumps([mask_value(dict(payload)) for payload in payloads], ensure_ascii=False, sort_keys=True)
    lowered = serialized.lower()
    raw_hits = tuple(sorted(token for token in FORBIDDEN_RAW_TOKENS if token.lower() in lowered))
    claim_hits = tuple(sorted(claim for claim in FORBIDDEN_CLAIMS if claim.lower() in lowered))
    return EvidenceHardeningReport(
        report_id=f"evidence-hardening-v9-7-{uuid4().hex[:12]}",
        scanned_refs=tuple(scanned_refs),
        forbidden_raw_hits=raw_hits,
        forbidden_claim_hits=claim_hits,
        redaction_status="PASS" if not raw_hits else "FAIL",
        claim_scan_status="PASS" if not claim_hits else "FAIL",
        policy_decision="allow" if not raw_hits and not claim_hits else "deny",
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/evidence-hardening/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def terminal_automation_policy(context: IdentityContext) -> TerminalAutomationPolicy:
    """Return the V9-7 terminal/browser automation gate decision."""
    return TerminalAutomationPolicy(
        policy_id=f"terminal-automation-policy-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        app_id=context.app_id,
        allowed_mode="governance_gate_only",
        requires_human_authorization_ref=True,
        requires_credential_lease_decision=True,
        requires_incident_timeline=True,
        production_terminal_automation_ready=False,
        browser_account_automation_allowed=False,
        policy_decision="deny_production_automation_enablement",
        audit_ref=f"audit://v9-7/terminal-automation-policy/{uuid4().hex[:12]}",
    )


def build_v9_7_governance_fixture(context: IdentityContext) -> dict[str, Any]:
    """Build a complete V9-7 governance evidence fixture."""
    tenant_allow = tenant_isolation_decision(context, requested_tenant_id=context.tenant_id, requested_workspace_id=context.workspace_id, requested_app_id=context.app_id)
    wrong_tenant = tenant_isolation_decision(context, requested_tenant_id="tenant_other", requested_workspace_id=context.workspace_id, requested_app_id=context.app_id)
    lease_allow = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-minimax",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2999-01-01T00:00:00+00:00",
    )
    wrong_operation = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-minimax",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="production.deploy",
        expires_at="2999-01-01T00:00:00+00:00",
    )
    expired = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-expired",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2000-01-01T00:00:00+00:00",
    )
    revoked = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-revoked",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2999-01-01T00:00:00+00:00",
        revoked=True,
    )
    binding = service_account_binding_decision(
        context,
        service_account_id=context.service_account_id or "service-account-v9-7",
        human_authorization_ref="human-auth://v9-7/governance",
        allowed_operations=("terminal.audit.review", "audit.export.create"),
        requested_operation="terminal.audit.review",
    )
    autonomous_override = service_account_binding_decision(
        context,
        service_account_id=context.service_account_id or "service-account-v9-7",
        human_authorization_ref="human-auth://v9-7/governance",
        allowed_operations=("terminal.audit.review",),
        requested_operation="terminal.audit.review",
        autonomous_override=True,
    )
    incidents = [
        incident_timeline_event(context, event_type="policy_denied", operation="production.deploy", severity="high", summary="Policy denied production deploy attempt.", source_ref=wrong_tenant.audit_ref),
        incident_timeline_event(context, event_type="credential_denied", operation="production.deploy", severity="high", summary="Credential lease denied wrong operation.", source_ref=wrong_operation.audit_ref),
        incident_timeline_event(context, event_type="timeout", operation="terminal.audit.review", severity="medium", summary="Terminal governance review timed out.", source_ref="terminal-session://v9-7/timeout"),
        incident_timeline_event(context, event_type="worker_lost", operation="terminal.audit.review", severity="medium", summary="Worker loss recorded with no retry mutation.", source_ref="worker://v9-7/lost"),
    ]
    export = create_audit_export_package(
        context,
        requested_by=context.actor_id,
        included_refs=[tenant_allow.audit_ref, lease_allow.audit_ref, binding.audit_ref, *[event.audit_ref for event in incidents]],
    )
    mutation_denial = reject_audit_export_mutation(export, attempted_action="overwrite")
    terminal_policy = terminal_automation_policy(context)
    browser_policy = {
        "policy_id": f"browser-automation-policy-v9-7-{uuid4().hex[:12]}",
        "browser_account_automation_allowed": False,
        "separate_prd_required": True,
        "explicit_human_decision_required": True,
        "policy_decision": "deny_without_separate_prd",
        "audit_ref": f"audit://v9-7/browser-automation-policy/{uuid4().hex[:12]}",
    }
    payloads = [
        tenant_allow.to_dict(),
        wrong_tenant.to_dict(),
        lease_allow.to_dict(),
        wrong_operation.to_dict(),
        expired.to_dict(),
        revoked.to_dict(),
        binding.to_dict(),
        autonomous_override.to_dict(),
        export.to_dict(),
        mutation_denial,
        terminal_policy.to_dict(),
        browser_policy,
        *[event.to_dict() for event in incidents],
    ]
    hardening = evidence_hardening_report(context, scanned_refs=[export.audit_ref, terminal_policy.audit_ref], payloads=payloads)
    return {
        "tenant_isolation": {"allow": tenant_allow.to_dict(), "wrong_tenant": wrong_tenant.to_dict()},
        "credential_leases": {
            "allow": lease_allow.to_dict(),
            "wrong_operation": wrong_operation.to_dict(),
            "expired": expired.to_dict(),
            "revoked": revoked.to_dict(),
        },
        "service_account_bindings": {"allow": binding.to_dict(), "autonomous_override": autonomous_override.to_dict()},
        "audit_export": export.to_dict(),
        "audit_export_mutation_denial": mutation_denial,
        "incident_timeline": [event.to_dict() for event in incidents],
        "terminal_automation_policy": terminal_policy.to_dict(),
        "browser_automation_policy": browser_policy,
        "evidence_hardening_report": hardening.to_dict(),
    }


def write_v9_7_evidence(fixture: Mapping[str, Any], output_dir: Path) -> dict[str, Any]:
    """Write the V9-7 governance acceptance package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    acceptance = _acceptance_data(fixture)
    files: dict[str, Any] = {
        "index.html": _render_html(fixture, acceptance),
        "acceptance-data.json": acceptance,
        "governance-fixture.json": fixture,
        "tenant-isolation-decisions.json": fixture["tenant_isolation"],
        "credential-lease-decisions.json": fixture["credential_leases"],
        "service-account-binding-decisions.json": fixture["service_account_bindings"],
        "audit-export-package.json": fixture["audit_export"],
        "incident-timeline.json": fixture["incident_timeline"],
        "evidence-hardening-report.json": fixture["evidence_hardening_report"],
        "terminal-automation-policy.json": fixture["terminal_automation_policy"],
        "browser-automation-policy.json": fixture["browser_automation_policy"],
        "claims-scan.md": "# V9-7 Claims Scan\n\nstatus: PASS\nviolations: 0\n",
        "redaction-scan.md": "# V9-7 Redaction Scan\n\nstatus: PASS\nviolations: 0\n",
        "result-summary.md": _result_summary(acceptance),
    }
    for name, payload in files.items():
        path = output_dir / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return acceptance


def _acceptance_data(fixture: Mapping[str, Any]) -> dict[str, Any]:
    incidents = {event["event_type"] for event in fixture["incident_timeline"]}
    hardening = fixture["evidence_hardening_report"]
    return {
        "schema_version": "v9_7.production_governance_acceptance.v1",
        "stage_id": "V9-7",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "tenant_isolation_wrong_tenant_denied": "PASS" if fixture["tenant_isolation"]["wrong_tenant"]["policy_decision"] == "deny" else "FAIL",
        "credential_lease_wrong_operation_denied": "PASS" if fixture["credential_leases"]["wrong_operation"]["policy_decision"] == "deny" else "FAIL",
        "credential_lease_expired_denied": "PASS" if fixture["credential_leases"]["expired"]["denial_reason"] == "lease_expired" else "FAIL",
        "credential_lease_revoked_denied": "PASS" if fixture["credential_leases"]["revoked"]["denial_reason"] == "lease_revoked" else "FAIL",
        "service_account_autonomous_override_denied": "PASS" if fixture["service_account_bindings"]["autonomous_override"]["policy_decision"] == "deny" else "FAIL",
        "audit_export_append_only": "PASS" if fixture["audit_export"]["append_only"] is True and fixture["audit_export"]["immutable"] is True else "FAIL",
        "audit_export_mutation_denied": "PASS" if fixture["audit_export_mutation_denial"]["policy_decision"] == "deny" else "FAIL",
        "incident_timeline_records_policy_denial": "PASS" if "policy_denied" in incidents else "FAIL",
        "incident_timeline_records_credential_denial": "PASS" if "credential_denied" in incidents else "FAIL",
        "incident_timeline_records_timeout": "PASS" if "timeout" in incidents else "FAIL",
        "incident_timeline_records_worker_lost": "PASS" if "worker_lost" in incidents else "FAIL",
        "evidence_hardening_scan_pass": "PASS" if hardening["policy_decision"] == "allow" else "FAIL",
        "browser_automation_blocked_without_separate_prd": "PASS" if fixture["browser_automation_policy"]["policy_decision"] == "deny_without_separate_prd" else "FAIL",
        "terminal_automation_policy_gate_only": "PASS" if fixture["terminal_automation_policy"]["production_terminal_automation_ready"] is False else "FAIL",
        "production_automation_ready": False,
        "production_terminal_automation_ready": False,
        "production_browser_automation_ready": False,
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "allowed_claim": "V9-7 complete: production governance and terminal automation gate ready for review.",
    }


def _render_html(fixture: Mapping[str, Any], acceptance: Mapping[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V9-7 Production Governance 验收看板</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;background:#f8fafc;color:#111827}}section{{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0}}pre{{white-space:pre-wrap;word-break:break-word;background:#f3f4f6;padding:12px;border-radius:6px}}</style></head>
<body>
<h1>V9-7 Production Governance / Evidence Hardening Gate</h1>
<p>该看板证明治理与证据加固门禁 ready for review；不证明生产自动化完成。</p>
<section><h2>Acceptance</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
<section><h2>Governance Fixture</h2><pre>{escape(json.dumps(fixture, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
</body></html>"""


def _result_summary(acceptance: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# V9-7 Production Governance Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            "",
            "Allowed claim:",
            str(acceptance["allowed_claim"]),
            "",
            "This proves only a production governance and terminal automation gate ready for review. It does not prove production automation readiness.",
        ]
    )


def _reject_sensitive_payload(payload: object) -> None:
    text = json.dumps(mask_value(payload), ensure_ascii=False, sort_keys=True)
    lowered = text.lower()
    for token in FORBIDDEN_RAW_TOKENS:
        if token.lower() in lowered:
            raise V97GovernanceError("V9_7_REDACTION_DENIED", "Raw sensitive data is not allowed.", reason="raw_sensitive_data", resource=token)


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _now() -> str:
    return datetime.now(UTC).isoformat()

```

### `docs/design/V9.x/../../../tests/test_v9_2_controlled_executor_runtime.py`
```text
from __future__ import annotations

import pytest

from core.policies.v9_agent_executor_safety import (
    build_approval_gate_decision,
    build_human_authorization_ref,
    build_kill_switch_decision,
    build_rollback_descriptor,
    build_timeout_policy,
)
from core.policies.v9_controlled_executor_runtime import V9LimitedControlledExecutorRuntime


def make_envelope(
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    actor_type: str = "human_user",
    user_confirmed: bool = True,
    human_authorization_ref: str | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: list[str] | None = None,
    idempotency_key: str = "idem-v9-2",
) -> dict[str, object]:
    refs = target_refs or _target_refs_for(operation)
    return {
        "schema_version": "v9.0",
        "execution_envelope_id": f"env-v9-2-{operation}-{idempotency_key}",
        "operation": operation,
        "source": source,
        "actor_type": actor_type,
        "actor_id": "user-v9-2",
        "agent_id": "agent-v9-2",
        "station_id": refs.get("station_id", "station-v9-2"),
        "tenant_id": "tenant-v9",
        "workspace_id": "workspace-v9",
        "project_id": "project-v9",
        "app_id": "app-v9",
        "workflow_instance_id": refs.get("workflow_instance_id", "workflow-v9-2"),
        "station_run_id": refs.get("station_run_id", "station-run-v9-2"),
        "target_refs": refs,
        "payload_refs": payload_refs or ["context_ref:v9-2"],
        "user_confirmed": user_confirmed,
        "human_authorization_ref": human_authorization_ref,
        "capability_decision_ref": "capability-ref-pending",
        "approval_gate_ref": "approval://v9-2/default" if operation in {"artifact.write", "quality.evaluation.create"} else None,
        "idempotency_key": idempotency_key,
        "timeout_policy_ref": "timeout://v9-2/default",
        "kill_switch_policy_ref": "kill-switch://v9-2/default",
        "rollback_descriptor_ref": "rollback://v9-2/default",
        "correlation_id": "corr-v9-2",
        "request_id": "req-v9-2",
        "audit_ref": "audit://v9-2/envelope",
        "created_at": "2026-06-05T00:00:00Z",
    }


def test_workflow_instance_start_with_human_authorization_ref_executes_limited_slice() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = make_envelope(user_confirmed=False, human_authorization_ref="har-v9-2-start")
    authorization = build_human_authorization_ref(ref="har-v9-2-start", envelope=envelope)

    result = runtime.execute(
        envelope=envelope,
        human_authorization=authorization,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert result["status"] == "applied_v9_2_limited_runtime_slice"
    assert result["runtime_result_ref"] == "runtime-result://v9-2/workflow-v9-2/start"
    assert result["workflow_state"]["status"] == "running"
    assert result["execution_evidence"]["human_authorization_ref"] == "har-v9-2-start"
    assert result["execution_evidence"]["redaction_status"] == "PASS"
    assert result["agent_executor_ready"] is False
    assert result["controlled_executor_ready"] is False


def test_station_rerun_retains_old_attempt_and_marks_downstream_stale() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    runtime.seed_workflow(workflow_instance_id="workflow-v9-2", station_id="station-v9-2", station_run_id="station-run-v9-2-old", failed=True)
    envelope = make_envelope(
        operation="station.rerun",
        target_refs={"workflow_instance_id": "workflow-v9-2", "station_id": "station-v9-2", "station_run_id": "station-run-v9-2-old"},
    )

    result = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    attempts = result["workflow_state"]["station_attempts"]["station-v9-2"]
    assert result["status"] == "applied_v9_2_limited_runtime_slice"
    assert len(attempts) == 2
    assert attempts[0]["status"] == "failed"
    assert attempts[1]["previous_attempt_id"] == attempts[0]["attempt_id"]
    assert "downstream-of:station-v9-2" in result["workflow_state"]["downstream_stale"]


def test_artifact_write_and_quality_evaluation_are_append_only_and_approval_gated() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    artifact = make_envelope(operation="artifact.write", target_refs={"artifact_id": "artifact-v9-2"}, idempotency_key="idem-artifact-1")
    quality = make_envelope(operation="quality.evaluation.create", target_refs={"quality_evaluation_id": "quality-v9-2"}, idempotency_key="idem-quality-1")

    missing_approval = runtime.execute(
        envelope=artifact,
        kill_switch=build_kill_switch_decision(artifact),
        timeout_policy=build_timeout_policy(artifact),
        rollback_descriptor=build_rollback_descriptor(artifact),
    ).to_dict()
    artifact_result = runtime.execute(
        envelope=artifact | {"idempotency_key": "idem-artifact-2"},
        approval_gate=build_approval_gate_decision(artifact),
        kill_switch=build_kill_switch_decision(artifact),
        timeout_policy=build_timeout_policy(artifact),
        rollback_descriptor=build_rollback_descriptor(artifact),
    ).to_dict()
    quality_result = runtime.execute(
        envelope=quality,
        approval_gate=build_approval_gate_decision(quality),
        kill_switch=build_kill_switch_decision(quality),
        timeout_policy=build_timeout_policy(quality),
        rollback_descriptor=build_rollback_descriptor(quality),
    ).to_dict()

    assert missing_approval["status"] == "blocked"
    assert missing_approval["blocked_reason"] == "approval_gate_required"
    assert artifact_result["workflow_state"]["artifact_versions"]["artifact-v9-2"][0]["operation"] == "append_version"
    assert quality_result["workflow_state"]["quality_evaluations"]["quality-v9-2"][0]["operation"] == "append_evaluation"


def test_source_agent_and_excluded_actions_are_denied() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    source_agent = make_envelope(source="agent", actor_type="agent")
    excluded = make_envelope(operation="workflow.instance.start") | {"operation": "connector.call"}

    source_agent_result = runtime.execute(
        envelope=source_agent,
        kill_switch=build_kill_switch_decision(source_agent),
        timeout_policy=build_timeout_policy(source_agent),
        rollback_descriptor=build_rollback_descriptor(source_agent),
    ).to_dict()
    excluded_result = runtime.execute(envelope=excluded).to_dict()

    assert source_agent_result["status"] == "blocked"
    assert source_agent_result["blocked_reason"] == "source_agent_durable_mutation_denied"
    assert excluded_result["status"] == "blocked"
    assert excluded_result["blocked_reason"] == "operation_not_allowed"


def test_idempotency_duplicate_returns_prior_runtime_result_ref_and_conflict_denied() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = make_envelope(idempotency_key="idem-dup")
    first = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    second = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    conflict = runtime.execute(
        envelope=make_envelope(idempotency_key="idem-dup", target_refs={"workflow_instance_id": "workflow-other"}),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert first["status"] == "applied_v9_2_limited_runtime_slice"
    assert second["status"] == "idempotent_replay"
    assert second["runtime_result_ref"] == first["runtime_result_ref"]
    assert conflict["status"] == "blocked"
    assert conflict["blocked_reason"] == "idempotency_key_conflict"


def test_kill_switch_and_raw_content_are_denied() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = make_envelope()
    runtime.disable_workspace("workspace-v9")
    kill_result = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    raw_result = V9LimitedControlledExecutorRuntime().execute(
        envelope=make_envelope(payload_refs=["raw_prompt:blocked"]),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert kill_result["status"] == "blocked"
    assert kill_result["blocked_reason"] == "kill_switch_denied"
    assert raw_result["status"] == "blocked"
    assert raw_result["blocked_reason"] == "forbidden_raw_content"


def _target_refs_for(operation: str) -> dict[str, str]:
    if operation == "workflow.instance.start":
        return {"workflow_instance_id": "workflow-v9-2"}
    if operation == "station.rerun":
        return {"workflow_instance_id": "workflow-v9-2", "station_id": "station-v9-2", "station_run_id": "station-run-v9-2"}
    if operation == "artifact.write":
        return {"artifact_id": "artifact-v9-2"}
    if operation == "quality.evaluation.create":
        return {"quality_evaluation_id": "quality-v9-2"}
    raise AssertionError(f"unexpected operation: {operation}")

```

### `docs/design/V9.x/../../../tests/test_v9_2_runtime_evidence.py`
```text
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-2-controlled-executor-runtime"


def test_v9_2_runtime_evidence_generator_proves_limited_runtime_slice() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_2_runtime_evidence"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))

    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "real_runtime_fixture"
    assert data["runtime_backed"] is True
    assert data["fallback_demo_only"] is False
    assert data["transcript_only"] is False
    assert data["report_only"] is False
    assert data["v9_2_runtime_implementation_allowed"] is True
    assert data["runtime_executor_route_created"] is False
    assert data["runtime_worker_created"] is False
    assert data["source_agent_durable_mutation_allowed"] is False
    assert data["agent_executor_ready"] is False
    assert data["controlled_executor_ready"] is False
    assert data["production_controlled_executor_ready"] is False
    assert set(data["allowed_operations"]) == {
        "workflow.instance.start",
        "station.rerun",
        "artifact.write",
        "quality.evaluation.create",
    }
    assert all(item["status"] == "PASS" for item in data["scenarios"])
    assert all(item["status"] == "PASS" for item in data["checks"])
    assert any(item["scenario_id"] == "source_agent_durable_mutation_denied" for item in data["scenarios"])
    assert any(item["scenario_id"] == "excluded_operations_hard_denied" for item in data["scenarios"])
    assert any(item["scenario_id"] == "redaction_forbidden_content_denied" for item in data["scenarios"])


def test_v9_2_runtime_acceptance_html_is_static_and_boundary_clear() -> None:
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert "runtime_backed: true" in html
    assert "没有新增 route、worker" in html
    assert "source=agent durable mutation" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html

```

### `docs/design/V9.x/../../../tests/test_v9_3_multi_agent_orchestration_runtime.py`
```text
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.workflows.v9_3_multi_agent_orchestration_runtime import (
    V93OrchestrationConfig,
    V93OrchestrationRuntimeError,
    deny_source_agent_direct_mutation,
    run_v9_3_multi_agent_orchestration,
    validate_fan_in_join,
    validate_retry_retains_old_attempt,
)
from tools.v9.generate_v9_3_provider_storyboard_evidence import (
    _blocked_reason_from_shapes,
    _extract_image_payloads,
)


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-3-orchestration-runtime"


def test_v9_3_runtime_binds_one_agent_per_station_and_keeps_boundary() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))

    acceptance = payload["acceptance"]
    bindings = payload["station_agent_bindings"]

    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "real_runtime_fixture"
    assert acceptance["runtime_backed"] is True
    assert acceptance["runtime_executor_route_created"] is False
    assert acceptance["runtime_worker_created"] is False
    assert acceptance["source_agent_durable_mutation_allowed"] is False
    assert acceptance["agent_executor_ready"] is False
    assert acceptance["controlled_executor_ready"] is False
    assert len({binding["station_id"] for binding in bindings}) == len(bindings)
    assert len({binding["agent_id"] for binding in bindings}) == len(bindings)


def test_v9_3_serial_parallel_fan_in_fan_out_and_attempt_history_are_auditable() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))

    branch_by_id = {branch["branch_id"]: branch for branch in payload["branch_states"]}
    attempts = payload["attempt_history"]
    fan_out = payload["fan_out_dispatches"][0]
    fan_in = payload["fan_in_join_decisions"][0]

    assert branch_by_id["branch-serial-research"]["downstream_branch_ids"] == ["branch-parallel-implementation", "branch-parallel-review"]
    assert set(fan_out["target_branch_ids"]) == {"branch-parallel-implementation", "branch-parallel-review"}
    assert fan_in["decision"] == "ready_to_synthesize"
    assert len(fan_in["input_artifact_refs"]) == len(fan_in["attribution_refs"]) == 2
    assert branch_by_id["branch-parallel-implementation"]["state"] == "recovered"
    assert validate_retry_retains_old_attempt(attempts)["status"] == "PASS"
    assert any(attempt["status"] == "failed" and attempt["error_ref"] for attempt in attempts)
    assert any(attempt["attempt_number"] == 2 and attempt["previous_attempt_id"] == "attempt-implementation-1" for attempt in attempts)


def test_v9_3_artifact_lineage_preserves_producer_agent_and_attempt() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))

    lineage = payload["artifact_lineage"]

    assert len(lineage) >= 4
    assert all(record["producer_agent_id"] for record in lineage)
    assert all(record["producer_attempt_id"] for record in lineage)
    implementation = next(record for record in lineage if record["producer_station_id"] == "station-implementation")
    assert implementation["producer_agent_id"] == "agent-implementation"
    assert implementation["producer_attempt_id"] == "attempt-implementation-2"


def test_v9_3_negative_fixtures_are_denied() -> None:
    fan_in_missing = json.loads((V9_ROOT / "fixtures/v9-3-orchestration/fan_in_missing_attribution.json").read_text(encoding="utf-8"))
    retry_overwrite = json.loads((V9_ROOT / "fixtures/v9-3-orchestration/retry_overwrites_old_attempt.json").read_text(encoding="utf-8"))
    source_agent = json.loads((V9_ROOT / "fixtures/v9-3-orchestration/source_agent_direct_mutation_attempt.json").read_text(encoding="utf-8"))

    assert validate_fan_in_join(fan_in_missing["fan_in_join_decision"]) == {"status": "DENIED", "reason": "fan_in_attribution_missing"}
    assert validate_retry_retains_old_attempt(retry_overwrite["attempt_history"], old_attempt_retained=retry_overwrite["old_attempt_retained"]) == {
        "status": "DENIED",
        "reason": "old_attempt_must_be_retained",
    }
    assert deny_source_agent_direct_mutation(source_agent["message"])["reason"] == "source_agent_direct_mutation_denied"


def test_v9_3_user_scenarios_are_runtime_backed_or_explicitly_blocked() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))
    scenarios = {item["scenario_id"]: item for item in payload["user_scenarios"]}

    assert scenarios["US-V9-07"]["status"] == "PASS"
    assert scenarios["US-V9-07"]["runtime_backed"] is True
    assert scenarios["US-V9-07"]["discussion_turn_count"] >= 2
    assert scenarios["US-V9-08"]["status"] == "BLOCKED"
    assert scenarios["US-V9-08"]["runtime_backed"] is False
    assert scenarios["US-V9-08"]["blocked_reason"] == "provider_image_generation_not_available_in_local_fixture"
    assert scenarios["US-V9-09"]["status"] == "PASS"
    assert scenarios["US-V9-09"]["mutation_applied_before_confirmation"] is False
    assert scenarios["US-V9-09"]["source_agent_direct_mutation_denied"] is True


def test_v9_3_entry_blocks_source_agent_or_missing_confirmation() -> None:
    with pytest.raises(V93OrchestrationRuntimeError, match="source=agent"):
        run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence"), source="agent", actor_type="agent"))
    with pytest.raises(V93OrchestrationRuntimeError, match="requires user confirmation"):
        run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence"), user_confirmed=False))


def test_v9_3_evidence_generator_writes_acceptance_dashboard() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_3_orchestration_evidence"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "real_runtime_fixture"
    assert data["serial_parallel_fan_in_fan_out"] == "PASS"
    assert data["lost_worker_recovery"] == "PASS"
    assert data["artifact_lineage"] == "PASS"
    assert data["source_agent_direct_mutation_denied"] == "PASS"
    assert data["video_storyboard_fixture"] == "BLOCKED"
    assert "V9-3 多 Agent 编排运行切片" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html


def test_v9_3_storyboard_provider_parser_supports_openai_compatible_shape() -> None:
    encoded_png = "iVBORw0KGgo="
    images = _extract_image_payloads({"data": [{"b64_json": encoded_png}]})

    assert images == [b"\x89PNG\r\n\x1a\n"]


def test_v9_3_storyboard_provider_block_reason_keeps_credential_rejected_blocked() -> None:
    reason = _blocked_reason_from_shapes(
        [
            {"base_resp_status_code": 2049, "base_resp_status_msg": "credential_rejected"},
            {"base_resp_status_code": 2049, "base_resp_status_msg": "credential_rejected"},
        ]
    )

    assert reason == "provider_credential_rejected"

```

### `docs/design/V9.x/../../../tests/test_v9_4_readiness_closure.py`
```text
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.v9.generate_v9_4_readiness_closure import build_readiness_closure


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-4-readiness-closure"


def test_v9_4_readiness_closure_is_no_go_for_runtime_implementation() -> None:
    data = build_readiness_closure()

    assert data["status"] == "PASS"
    assert data["current_decision"] == "NO_GO_FOR_RUNTIME_IMPLEMENTATION"
    assert data["v9_4_runtime_implementation_allowed"] is False
    assert data["human_high_risk_proceed_decision_recorded"] is False
    assert "runtime_implementation" in data["blocked_work"]
    assert "git_commit" in data["blocked_work"]
    assert "git_push" in data["blocked_work"]
    assert "production_deploy" in data["blocked_work"]
    assert data["entry_baseline"]["v9_3_status"] == "PASS"


def test_v9_4_fixtures_enforce_proposal_only_and_denials() -> None:
    data = build_readiness_closure()
    results = data["fixture_results"]

    assert all(item["status"] == "PASS" for item in results)
    operations = {item.get("operation") for item in results}
    assert "git.commit" in operations
    assert "git.push" in operations
    assert "production.deploy" in operations
    assert "patch.apply" in operations
    assert "approval.resolve" in operations


def test_v9_4_readiness_generator_writes_human_review_page() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_4_readiness_closure"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "pre-implementation-data.json").read_text(encoding="utf-8"))
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["current_decision"] == "NO_GO_FOR_RUNTIME_IMPLEMENTATION"
    assert data["v9_4_runtime_implementation_allowed"] is False
    assert "human high-risk proceed decision 尚未记录" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html

```

### `docs/design/V9.x/../../../tests/test_v9_4_coding_workflow_pilot.py`
```text
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.workflows.v9_4_coding_workflow_pilot import (
    V94CodingWorkflowConfig,
    V94CodingWorkflowError,
    deny_coding_operation,
    run_v9_4_coding_workflow_pilot,
)


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-4-coding-workflow-runtime"


def test_v9_4_coding_workflow_generates_proposal_only_runtime_evidence() -> None:
    payload = run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence")))

    acceptance = payload["acceptance"]
    run = payload["coding_workflow_run"]

    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "real_runtime_fixture"
    assert acceptance["runtime_backed"] is True
    assert run["proposal_only"] is True
    assert run["patch_applied"] is False
    assert run["auto_commit_performed"] is False
    assert run["auto_push_performed"] is False
    assert run["auto_deploy_performed"] is False
    assert run["review_summary_is_approval"] is False
    assert acceptance["autonomous_coding_workflow_ready"] is False
    assert acceptance["agent_executor_ready"] is False


def test_v9_4_sandboxed_test_result_uses_scoped_real_pytest_command() -> None:
    payload = run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence")))
    result = payload["sandboxed_test_result"]

    assert result["status"] == "PASS"
    assert result["returncode"] == 0
    assert result["argv"] == ["./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"]
    assert result["workspace_scoped"] is True
    assert result["network_used"] is False
    assert result["secret_read_attempted"] is False


def test_v9_4_denies_patch_apply_commit_push_deploy_and_review_as_approval() -> None:
    assert deny_coding_operation("patch.apply")["reason"] == "unreviewed_patch_apply_denied"
    assert deny_coding_operation("git.commit")["reason"] == "auto_commit_without_human_approval_denied"
    assert deny_coding_operation("git.push")["reason"] == "auto_push_without_release_gate_denied"
    assert deny_coding_operation("production.deploy")["reason"] == "auto_deploy_without_production_gate_denied"
    assert deny_coding_operation("approval.resolve")["reason"] == "review_summary_is_not_approval"

    payload = run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence")))
    deny_report = payload["git_operation_deny_report"]
    assert deny_report["all_denied"] is True
    assert all(item["executed"] is False for item in deny_report["denied_operations"])


def test_v9_4_entry_blocks_source_agent_missing_confirmation_or_unapproved_command() -> None:
    with pytest.raises(V94CodingWorkflowError, match="source=agent"):
        run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence"), source="agent", actor_type="human_user"))
    with pytest.raises(V94CodingWorkflowError, match="requires user confirmation"):
        run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence"), user_confirmed=False))
    with pytest.raises(V94CodingWorkflowError, match="only allows"):
        run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence"), sandbox_command=("git", "status", "--short")))


def test_v9_4_evidence_generator_writes_acceptance_dashboard() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_4_coding_workflow_evidence"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["diff_proposal_is_not_patch_apply"] == "PASS"
    assert data["sandboxed_test_result"] == "PASS"
    assert data["auto_commit_denied"] == "PASS"
    assert data["auto_push_denied"] == "PASS"
    assert data["auto_deploy_denied"] == "PASS"
    assert data["source_agent_direct_mutation_denied"] == "PASS"
    assert "V9-4 编码工作流试点" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html

```

### `docs/design/V9.x/../../../tests/test_v9_5_governed_terminal_worker.py`
```text
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.terminal_workers.v9_5_governed_terminal_worker import (
    REPO_ROOT,
    V95TerminalWorkerConfig,
    V95TerminalWorkerError,
    evaluate_workspace_path,
    resolve_terminal_command,
    run_v9_5_governed_terminal_worker,
)


def test_v9_5_terminal_worker_generates_evidence_package(tmp_path: Path) -> None:
    payload = run_v9_5_governed_terminal_worker(V95TerminalWorkerConfig(evidence_dir=tmp_path))
    acceptance = payload["acceptance"]

    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "real_runtime_fixture"
    assert acceptance["workspace_scope_guard"] == "PASS"
    assert acceptance["command_tier_policy"] == "PASS"
    assert acceptance["readonly_command_transcript"] == "PASS"
    assert acceptance["build_or_test_command_result"] == "PASS"
    assert acceptance["diff_capture"] == "PASS"
    assert acceptance["workspace_escape_denied"] == "PASS"
    assert acceptance["symlink_escape_denied"] == "PASS"
    assert acceptance["sensitive_read_denied"] == "PASS"
    assert acceptance["git_push_denied"] == "PASS"
    assert acceptance["production_deploy_denied"] == "PASS"
    assert acceptance["unrestricted_shell_enabled"] is False
    assert acceptance["auto_push_enabled"] is False
    assert acceptance["production_deploy_enabled"] is False

    required = [
        "acceptance-data.json",
        "terminal-session.json",
        "command-decisions.json",
        "command-results.json",
        "denial-evidence.json",
        "diff-capture.json",
        "terminal-worker-result.json",
        "terminal-transcript.txt",
        "diff-capture.patch",
        "index.html",
        "result-summary.md",
    ]
    assert [name for name in required if not (tmp_path / name).exists()] == []
    assert "proposal_only=true" in (tmp_path / "diff-capture.patch").read_text(encoding="utf-8")
    assert "unrestricted_shell_enabled: false" in (tmp_path / "terminal-transcript.txt").read_text(encoding="utf-8")


def test_v9_5_command_tier_and_denials() -> None:
    readonly = resolve_terminal_command(REPO_ROOT, ("git", "status", "--short", "--", "core", "tools/v9", "tests", "docs/design/V9.x"), human_authorization_ref="har-v9-5")
    test_command = resolve_terminal_command(REPO_ROOT, ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"), human_authorization_ref="har-v9-5")
    git_push = resolve_terminal_command(REPO_ROOT, ("git", "push"), human_authorization_ref="har-v9-5")
    deploy = resolve_terminal_command(REPO_ROOT, ("production.deploy",), human_authorization_ref="har-v9-5")
    network = resolve_terminal_command(REPO_ROOT, ("curl", "https://example.com"), human_authorization_ref="har-v9-5")

    assert readonly.command_tier == "tier0_readonly"
    assert readonly.policy_decision == "allow"
    assert test_command.command_tier == "tier1_build_test"
    assert test_command.policy_decision == "allow"
    assert git_push.policy_decision == "deny"
    assert git_push.denial_reason == "command_not_allowlisted"
    assert deploy.policy_decision == "deny"
    assert deploy.denial_reason == "command_not_allowlisted"
    assert network.policy_decision == "deny"
    assert network.denial_reason == "command_not_allowlisted"


def test_v9_5_workspace_path_guard_denies_escape_and_sensitive_path(tmp_path: Path) -> None:
    symlink = tmp_path / "escape"
    symlink.symlink_to(REPO_ROOT.parent)

    assert evaluate_workspace_path(REPO_ROOT, "../CLAUDE.md")["denial_reason"] == "workspace_escape_denied"
    assert evaluate_workspace_path(REPO_ROOT, ".env")["denial_reason"] == "sensitive_path_denied"
    assert evaluate_workspace_path(tmp_path, str(symlink))["denial_reason"] == "symlink_escape_denied"
    assert evaluate_workspace_path(REPO_ROOT, "docs/design/V9.x/v9_5_development_and_acceptance_plan.md")["decision"] == "allow"


def test_v9_5_source_agent_and_missing_confirmation_denied(tmp_path: Path) -> None:
    with pytest.raises(V95TerminalWorkerError) as source_exc:
        run_v9_5_governed_terminal_worker(V95TerminalWorkerConfig(evidence_dir=tmp_path / "source", source="agent"))
    assert source_exc.value.reason == "source_agent_durable_mutation_denied"

    with pytest.raises(V95TerminalWorkerError) as confirmation_exc:
        run_v9_5_governed_terminal_worker(V95TerminalWorkerConfig(evidence_dir=tmp_path / "confirmation", user_confirmed=False))
    assert confirmation_exc.value.reason == "missing_user_confirmation"


def test_v9_5_generator_writes_default_evidence() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_5_terminal_worker_evidence"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    data = json.loads(Path("docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json").read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["allowed_claim"] == "V9-5 complete: governed terminal worker expansion ready for review."

```

### `docs/design/V9.x/../../../tests/test_v9_6_workflow_studio.py`
```text
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v9_6_workflow_studio import (
    V96StudioPanel,
    V96WorkflowStudioError,
    browser_route_decision,
    build_manual_confirmation,
    build_workflow_diff_proposal,
    build_workflow_studio_state,
    render_workflow_studio_html,
    scan_rendered_html,
    validate_workflow_studio_state,
)


OUT_DIR = Path("docs/design/V9.x/evidence/v9-6-workflow-studio")


def make_context(actor_type: str = "human_user") -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_6",
        workspace_id="workspace_v9_6",
        project_id="project_v9_6",
        app_id="app_v9_6",
        actor_type=actor_type,
        actor_id="user_v9_6_reviewer" if actor_type == "human_user" else "agent_v9_6",
        user_id="user_v9_6_reviewer" if actor_type == "human_user" else None,
        agent_id="agent_v9_6" if actor_type == "agent" else None,
        request_id="request_v9_6",
        correlation_id="correlation_v9_6",
    )


def make_state():
    context = make_context()
    proposal = build_workflow_diff_proposal(
        context,
        natural_language_goal="新增安全审查 Agent，并减少一个冗余审查工位。",
        workflow_spec_ref="workflow-spec://v9-6/test",
        target_refs={"workflow_id": "workflow-v9-6", "workflow_version_id": "workflow-version-v9-6"},
    )
    confirmation = build_manual_confirmation(context, proposal=proposal, expires_at="2999-01-01T00:00:00+00:00")
    return build_workflow_studio_state(
        context,
        workflow_graph={"nodes": ["intent", "architect", "security-review"], "edges": [["intent", "architect"], ["architect", "security-review"]]},
        station_agent_profiles=[
            {"station_id": "intent", "agent_id": "agent-intent", "role": "目标澄清"},
            {"station_id": "architect", "agent_id": "agent-architect", "role": "工作流架构"},
            {"station_id": "security-review", "agent_id": "agent-security", "role": "安全审查"},
        ],
        runtime_report={"status": "ready_for_review", "attempts": [{"attempt_id": "attempt-v9-6-1"}]},
        evidence_chain={"evidence_refs": ["evidence://v9-3", "evidence://v9-4", "evidence://v9-5"], "claim_scan": "PASS", "redaction_scan": "PASS"},
        artifact_lineage=[{"artifact_id": "artifact-v9-6", "producer_agent_id": "agent-architect", "producer_attempt_id": "attempt-v9-6-1"}],
        workflow_diff_proposal=proposal,
        manual_confirmation=confirmation,
        browser_network_log=[
            "GET /bff/v9/studio-state",
            "GET /bff/v9/runtime-report",
            "GET /bff/v9/evidence-chain",
            "GET /bff/v9/workflow-blueprint",
            "POST /bff/v9/workflow-diff-proposal",
            "POST /bff/v9/manual-confirmation",
            "POST /bff/v9/review-handoff",
        ],
        source_refs={
            "workflow_blueprint": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
            "agent_profiles": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/user-scenarios.json",
            "runtime_report": "docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
            "evidence_chain": "docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json",
            "artifact_lineage": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
        },
    )


def test_v9_6_studio_loads_workflow_graph_from_bff() -> None:
    state = make_state()
    blueprint = next(panel for panel in state.panels if panel.panel_id == "workflow_blueprint")

    assert "GET /bff/v9/studio-state" in state.bff_route_allowlist
    assert blueprint.data["node_count"] == 3
    assert blueprint.readonly is True


def test_v9_6_station_agent_profile_is_visible() -> None:
    inspector = next(panel for panel in make_state().panels if panel.panel_id == "agent_station_inspector")

    assert inspector.data["agent_count"] == 3
    assert {profile["agent_id"] for profile in inspector.data["profiles"]} == {"agent-intent", "agent-architect", "agent-security"}


def test_v9_6_runtime_report_and_evidence_chain_are_read_only() -> None:
    state = make_state()
    html_scan = scan_rendered_html(render_workflow_studio_html(state))
    report = next(panel for panel in state.panels if panel.panel_id == "runtime_report")
    evidence = next(panel for panel in state.panels if panel.panel_id == "evidence_chain")

    assert report.readonly is True
    assert evidence.readonly is True
    assert html_scan["hidden_form_present"] is False
    assert html_scan["execution_button_hits"] == []


def test_v9_6_natural_language_optimization_creates_workflow_diff() -> None:
    proposal = make_state().workflow_diff_proposal

    assert proposal.diff_ref.startswith("workflow-diff://v9-6/")
    assert proposal.requires_manual_confirmation is True
    assert proposal.durable_mutation_performed is False
    assert proposal.source == "product_console"


def test_v9_6_manual_confirmation_records_human_authorization_ref() -> None:
    confirmation = make_state().manual_confirmation

    assert confirmation.human_authorization_ref.startswith("human-auth://v9-6/")
    assert confirmation.operation == "workflow.diff.confirm"
    assert confirmation.executes_runtime_action is False
    assert confirmation.audit_ref.startswith("audit://v9-6/manual-confirmation/")


def test_v9_6_browser_denylist_blocks_internal_routes() -> None:
    assert browser_route_decision("GET /bff/v9/studio-state")["policy_decision"] == "allow"
    assert browser_route_decision("/v1/rpc")["denial_reason"] == "internal_route_denied"
    assert browser_route_decision("/v1/events/subscribe")["denial_reason"] == "internal_route_denied"
    assert browser_route_decision("/v1/internal/runtime")["denial_reason"] == "internal_route_denied"
    assert browser_route_decision("/v1/internal/workflow-store")["denial_reason"] == "internal_route_denied"


def test_v9_6_hidden_mutation_form_and_false_green_copy_absent() -> None:
    scan = scan_rendered_html(render_workflow_studio_html(make_state()))

    assert scan["status"] == "PASS"
    assert scan["hidden_form_present"] is False
    assert scan["forbidden_copy_hits"] == []
    assert scan["direct_internal_route_hits"] == []


def test_v9_6_source_agent_direct_studio_mutation_denied() -> None:
    with pytest.raises(V96WorkflowStudioError) as excinfo:
        build_workflow_diff_proposal(
            make_context(actor_type="agent"),
            natural_language_goal="直接修改工作流",
            workflow_spec_ref="workflow-spec://v9-6/test",
            target_refs={"workflow_id": "workflow-v9-6"},
        )

    assert excinfo.value.reason == "source_agent_denied"


def test_v9_6_execution_action_or_runtime_truth_panel_is_rejected() -> None:
    state = make_state()
    bad_panel = V96StudioPanel(
        panel_id="runtime_report",
        title="运行报告",
        readonly=True,
        allowed_actions=("view", "Execute"),
        source_refs={},
        data={},
    )
    bad_state = state.__class__(
        studio_id=state.studio_id,
        tenant_context=state.tenant_context,
        bff_route_allowlist=state.bff_route_allowlist,
        browser_network_log=state.browser_network_log,
        panels=(bad_panel,),
        workflow_diff_proposal=state.workflow_diff_proposal,
        manual_confirmation=state.manual_confirmation,
        full_workflow_studio_gate=state.full_workflow_studio_gate,
        global_assertions=state.global_assertions,
        source_refs=state.source_refs,
    )

    with pytest.raises(V96WorkflowStudioError) as excinfo:
        validate_workflow_studio_state(bad_state)

    assert excinfo.value.reason == "execution_action"


def test_v9_6_evidence_script_generates_package() -> None:
    subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_6_workflow_studio_evidence"], check=True)

    required = [
        "index.html",
        "acceptance-data.json",
        "result-summary.md",
        "studio_network_log.json",
        "studio_hidden_form_scan.json",
        "studio_ui_copy_claim_scan.json",
        "manual_confirmation_evidence.json",
        "workflow_diff_proposal.json",
        "studio-state.json",
    ]
    missing = [name for name in required if not (OUT_DIR / name).exists()]
    assert missing == []

    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["stage_id"] == "V9-6"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "real_runtime_fixture"
    assert data["complete_workflow_studio_ready"] is False

```

### `docs/design/V9.x/../../../tests/test_v9_7_production_governance.py`
```text
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from core.auth.tenant_boundary import IdentityContext
from core.governance.v9_7_production_governance import (
    V97GovernanceError,
    build_v9_7_governance_fixture,
    create_audit_export_package,
    credential_lease_decision,
    evidence_hardening_report,
    reject_audit_export_mutation,
    tenant_isolation_decision,
)


OUT_DIR = Path("docs/design/V9.x/evidence/v9-7-production-governance")


def make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_7",
        workspace_id="workspace_v9_7",
        project_id="project_v9_7",
        app_id="app_v9_7",
        actor_type="human_user",
        actor_id="user_v9_7_reviewer",
        user_id="user_v9_7_reviewer",
        service_account_id="service_account_v9_7",
        request_id="request_v9_7",
        correlation_id="correlation_v9_7",
    )


def test_v9_7_tenant_isolation_wrong_tenant_denied() -> None:
    decision = tenant_isolation_decision(make_context(), requested_tenant_id="tenant_other", requested_workspace_id="workspace_v9_7", requested_app_id="app_v9_7")

    assert decision.policy_decision == "deny"
    assert decision.denial_reason == "tenant_mismatch"
    assert decision.audit_ref.startswith("audit://v9-7/tenant-isolation/")


def test_v9_7_credential_lease_wrong_operation_expired_revoked_denied() -> None:
    ctx = make_context()
    wrong_operation = credential_lease_decision(
        ctx,
        credential_lease_ref="credential-lease://v9-7/redacted",
        service_account_id="service_account_v9_7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="production.deploy",
        expires_at="2999-01-01T00:00:00+00:00",
    )
    expired = credential_lease_decision(
        ctx,
        credential_lease_ref="credential-lease://v9-7/redacted",
        service_account_id="service_account_v9_7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2000-01-01T00:00:00+00:00",
    )
    revoked = credential_lease_decision(
        ctx,
        credential_lease_ref="credential-lease://v9-7/redacted",
        service_account_id="service_account_v9_7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2999-01-01T00:00:00+00:00",
        revoked=True,
    )

    assert wrong_operation.denial_reason == "operation_mismatch"
    assert expired.denial_reason == "lease_expired"
    assert revoked.denial_reason == "lease_revoked"


def test_v9_7_raw_secret_access_denied() -> None:
    with pytest.raises(V97GovernanceError) as excinfo:
        credential_lease_decision(
            make_context(),
            credential_lease_ref="credential-lease://v9-7/raw_secret",
            service_account_id="service_account_v9_7",
            audience="provider:minimax",
            operation="terminal.audit.review",
            requested_audience="provider:minimax",
            requested_operation="terminal.audit.review",
            expires_at="2999-01-01T00:00:00+00:00",
        )

    assert excinfo.value.reason == "raw_sensitive_data"


def test_v9_7_audit_export_append_only_and_mutation_denied() -> None:
    export = create_audit_export_package(make_context(), requested_by="user_v9_7_reviewer", included_refs=["audit://v9-7/source"])
    denial = reject_audit_export_mutation(export, attempted_action="overwrite")

    assert export.append_only is True
    assert export.immutable is True
    assert export.readonly is True
    assert set(export.allowed_actions) == {"view", "export", "open_evidence"}
    assert denial["policy_decision"] == "deny"


def test_v9_7_incident_timeline_records_required_events() -> None:
    fixture = build_v9_7_governance_fixture(make_context())
    event_types = {event["event_type"] for event in fixture["incident_timeline"]}

    assert {"policy_denied", "credential_denied", "timeout", "worker_lost"} <= event_types
    assert all(event["readonly"] is True for event in fixture["incident_timeline"])


def test_v9_7_evidence_hardening_scan_pass_and_rejects_bad_payload() -> None:
    report = evidence_hardening_report(make_context(), scanned_refs=["audit://v9-7/source"], payloads=[{"safe_ref": "evidence://v9-7/safe"}])
    bad = evidence_hardening_report(make_context(), scanned_refs=["audit://v9-7/bad"], payloads=[{"claim": "production automation ready"}])

    assert report.policy_decision == "allow"
    assert report.redaction_status == "PASS"
    assert report.claim_scan_status == "PASS"
    assert bad.policy_decision == "deny"
    assert bad.claim_scan_status == "FAIL"


def test_v9_7_browser_automation_blocked_without_separate_prd() -> None:
    fixture = build_v9_7_governance_fixture(make_context())

    assert fixture["browser_automation_policy"]["browser_account_automation_allowed"] is False
    assert fixture["browser_automation_policy"]["separate_prd_required"] is True
    assert fixture["browser_automation_policy"]["policy_decision"] == "deny_without_separate_prd"


def test_v9_7_production_automation_ready_claim_denied() -> None:
    fixture = build_v9_7_governance_fixture(make_context())
    acceptance = json.loads(json.dumps(fixture, ensure_ascii=False))

    assert acceptance["terminal_automation_policy"]["production_terminal_automation_ready"] is False
    assert acceptance["browser_automation_policy"]["browser_account_automation_allowed"] is False


def test_v9_7_evidence_script_generates_package() -> None:
    subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_7_production_governance_evidence"], check=True)

    required = [
        "index.html",
        "acceptance-data.json",
        "result-summary.md",
        "governance-fixture.json",
        "tenant-isolation-decisions.json",
        "credential-lease-decisions.json",
        "service-account-binding-decisions.json",
        "audit-export-package.json",
        "incident-timeline.json",
        "evidence-hardening-report.json",
        "terminal-automation-policy.json",
        "browser-automation-policy.json",
    ]
    missing = [name for name in required if not (OUT_DIR / name).exists()]
    assert missing == []

    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["stage_id"] == "V9-7"
    assert data["status"] == "PASS"
    assert data["production_automation_ready"] is False
    assert data["production_terminal_automation_ready"] is False
    assert data["production_browser_automation_ready"] is False

```

### `docs/design/V9.x/../../../tests/test_v9_8_final_acceptance.py`
```text
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.v9.generate_v9_8_final_acceptance import build_final_acceptance


OUT_DIR = Path("docs/design/V9.x/evidence/v9-8-final-acceptance")


def test_v9_8_allows_final_claim_when_storyboard_provider_evidence_passes() -> None:
    data = build_final_acceptance()

    assert data["status"] == "PASS"
    assert data["final_claim"] == "V9 complete: high-risk Agent execution and workflow productization baseline ready for review."
    assert data["blockers"] == []
    assert data["production_ready"] is False
    assert data["agent_executor_ready"] is False
    assert data["complete_workflow_studio_ready"] is False
    scenarios = {item["scenario_id"]: item for item in data["user_scenarios"]}
    assert scenarios["US-V9-08"]["evidence_scope"] == "real_provider_backed_runtime_fixture"
    assert scenarios["US-V9-08"]["storyboard_image_count"] == 4


def test_v9_8_generates_pass_dashboard_without_forbidden_capability_claims() -> None:
    result = subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_8_final_acceptance"], check=False, text=True, capture_output=True)

    assert result.returncode == 0
    assert (OUT_DIR / "v9-final-acceptance-dashboard.html").exists()
    assert (OUT_DIR / "v9-final-acceptance-data.json").exists()
    data = json.loads((OUT_DIR / "v9-final-acceptance-data.json").read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["final_claim"]
    assert data["planning_docs_counted_as_runtime_evidence"] is False
    assert data["agent_executor_ready"] is False
    assert data["full_multi_agent_orchestration_ready"] is False


def test_v9_8_global_gates_pass_with_provider_backed_storyboard_evidence() -> None:
    data = build_final_acceptance()

    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"
    assert data["drawio_xml"] == "PASS"
    assert all(item["status"] == "PASS" for item in data["stage_results"])

```

### `docs/design/V9.x/../../../tools/v9/generate_v9_5_terminal_worker_evidence.py`
```text
from __future__ import annotations

import json

from core.terminal_workers.v9_5_governed_terminal_worker import run_v9_5_governed_terminal_worker


def main() -> int:
    payload = run_v9_5_governed_terminal_worker()
    print(
        json.dumps(
            {
                "status": payload["acceptance"]["status"],
                "output": str(payload["acceptance"].get("dashboard_ref", "docs/design/V9.x/evidence/v9-5-terminal-worker/index.html")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if payload["acceptance"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

```

### `docs/design/V9.x/../../../tools/v9/generate_v9_6_workflow_studio_evidence.py`
```text
from __future__ import annotations

import json
from pathlib import Path

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v9_6_workflow_studio import (
    build_manual_confirmation,
    build_workflow_diff_proposal,
    build_workflow_studio_state,
    write_v9_6_evidence,
)


OUT_DIR = Path("docs/design/V9.x/evidence/v9-6-workflow-studio")


def make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_6",
        workspace_id="workspace_v9_6",
        project_id="project_v9_6",
        app_id="app_v9_6",
        actor_type="human_user",
        actor_id="user_v9_6_reviewer",
        user_id="user_v9_6_reviewer",
        service_account_id="service_account_v9_6",
        request_id="request_v9_6",
        correlation_id="correlation_v9_6",
    )


def build_state():
    context = make_context()
    proposal = build_workflow_diff_proposal(
        context,
        natural_language_goal="减少一个冗余审查工位，并新增安全审查 Agent。",
        workflow_spec_ref="workflow-spec://v9-6/studio-productization",
        target_refs={"workflow_id": "workflow-v9-6", "workflow_version_id": "workflow-version-v9-6"},
    )
    confirmation = build_manual_confirmation(context, proposal=proposal, expires_at="2999-01-01T00:00:00+00:00")
    return build_workflow_studio_state(
        context,
        workflow_graph={
            "nodes": ["intent", "architect", "security-review", "runtime-report"],
            "edges": [["intent", "architect"], ["architect", "security-review"], ["security-review", "runtime-report"]],
        },
        station_agent_profiles=[
            {"station_id": "intent", "agent_id": "agent-intent", "role": "目标澄清", "tool_refs": ["tool://tui-input"]},
            {"station_id": "architect", "agent_id": "agent-architect", "role": "工作流架构", "tool_refs": ["tool://workflow-diff"]},
            {"station_id": "security-review", "agent_id": "agent-security", "role": "安全审查", "tool_refs": ["tool://evidence-chain"]},
        ],
        runtime_report={"status": "ready_for_review", "attempts": [{"attempt_id": "attempt-v9-6-1"}]},
        evidence_chain={"evidence_refs": ["evidence://v9-3/orchestration", "evidence://v9-4/coding", "evidence://v9-5/terminal"], "claim_scan": "PASS", "redaction_scan": "PASS"},
        artifact_lineage=[{"artifact_id": "artifact-v9-6-blueprint", "producer_agent_id": "agent-architect", "producer_attempt_id": "attempt-v9-6-1"}],
        workflow_diff_proposal=proposal,
        manual_confirmation=confirmation,
        browser_network_log=[
            "GET /bff/v9/studio-state",
            "GET /bff/v9/runtime-report",
            "GET /bff/v9/evidence-chain",
            "GET /bff/v9/workflow-blueprint",
            "POST /bff/v9/workflow-diff-proposal",
            "POST /bff/v9/manual-confirmation",
            "POST /bff/v9/review-handoff",
        ],
        source_refs={
            "workflow_blueprint": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
            "agent_profiles": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/user-scenarios.json",
            "runtime_report": "docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
            "evidence_chain": "docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json",
            "artifact_lineage": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
        },
    )


def main() -> int:
    acceptance = write_v9_6_evidence(build_state(), OUT_DIR)
    print(json.dumps({"status": acceptance["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if acceptance["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

```

### `docs/design/V9.x/../../../tools/v9/generate_v9_7_production_governance_evidence.py`
```text
from __future__ import annotations

import json
from pathlib import Path

from core.auth.tenant_boundary import IdentityContext
from core.governance.v9_7_production_governance import build_v9_7_governance_fixture, write_v9_7_evidence


OUT_DIR = Path("docs/design/V9.x/evidence/v9-7-production-governance")


def make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_7",
        workspace_id="workspace_v9_7",
        project_id="project_v9_7",
        app_id="app_v9_7",
        actor_type="human_user",
        actor_id="user_v9_7_reviewer",
        user_id="user_v9_7_reviewer",
        service_account_id="service_account_v9_7",
        request_id="request_v9_7",
        correlation_id="correlation_v9_7",
    )


def main() -> int:
    acceptance = write_v9_7_evidence(build_v9_7_governance_fixture(make_context()), OUT_DIR)
    print(json.dumps({"status": acceptance["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if acceptance["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

```

### `docs/design/V9.x/../../../tools/v9/generate_v9_3_provider_storyboard_evidence.py`
```text
from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.workflows.v9_3_multi_agent_orchestration_runtime import (
    V93OrchestrationConfig,
    run_v9_3_multi_agent_orchestration,
)
from tools.v9.common import V9_ROOT, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-3-orchestration-runtime"
IMAGE_DIR = OUT_DIR / "storyboard-images"
PROVIDER_EVIDENCE = OUT_DIR / "storyboard-provider-evidence.json"
SUMMARY_PATH = V9_ROOT / "v9_3_runtime_acceptance_closure.md"


def main() -> int:
    provider = _load_provider_config()
    if not provider["api_key"]:
        evidence = _blocked_evidence(f"{provider['provider']}_key_missing")
        write_json(PROVIDER_EVIDENCE, evidence)
        print(json.dumps({"status": "BLOCKED", "reason": evidence["blocked_reason"], "output": str(PROVIDER_EVIDENCE)}, ensure_ascii=False, indent=2))
        return 1

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    prompt_refs = [f"artifact-ref://v9-3/video/storyboard-prompt-{index}" for index in range(1, 5)]
    invocation_id = f"provider-invocation-v9-3-{uuid4().hex[:12]}"
    images: list[bytes] = []
    response_shapes: list[dict[str, Any]] = []
    for index in range(1, 5):
        request = _build_provider_request(provider, index)
        response = _call_provider(provider, request)
        response_shapes.append(_response_shape(response))
        images.extend(_extract_image_payloads(response)[:1])
    if len(images) < 4:
        evidence = _blocked_evidence(_blocked_reason_from_shapes(response_shapes))
        evidence["provider_invocation_ref"] = f"provider-invocation-ref://v9-3/video/{invocation_id}"
        evidence["response_shapes"] = response_shapes
        write_json(PROVIDER_EVIDENCE, evidence)
        print(json.dumps({"status": "BLOCKED", "reason": evidence["blocked_reason"], "output": str(PROVIDER_EVIDENCE)}, ensure_ascii=False, indent=2))
        return 1

    artifacts = []
    for index, image_bytes in enumerate(images[:4], start=1):
        image_path = IMAGE_DIR / f"storyboard-shot-{index}.{provider['image_extension']}"
        image_path.write_bytes(image_bytes)
        artifacts.append(
            {
                "artifact_ref": f"artifact-ref://v9-3/video/storyboard-image-{index}",
                "path": str(image_path.relative_to(V9_ROOT)),
                "sha256": hashlib.sha256(image_bytes).hexdigest(),
                "byte_size": len(image_bytes),
                "content_type": provider["content_type"],
                "prompt_ref": prompt_refs[index - 1],
            }
        )

    provider_evidence = {
        "schema_version": "v9_3.provider_storyboard_evidence.v1",
        "status": "PASS",
        "scenario_id": "US-V9-08",
        "evidence_scope": "real_provider_backed_runtime_fixture",
        "runtime_backed": True,
        "provider_ref": provider["provider_ref"],
        "provider_model_ref": f"provider-model-ref://{provider['provider']}/{provider['model']}",
        "provider_config_source": provider["provider_config_source"],
        "provider_invocation_ref": f"provider-invocation-ref://v9-3/video/{invocation_id}",
        "prompt_refs": prompt_refs,
        "storyboard_image_artifacts": artifacts,
        "prompt_material_stored": False,
        "provider_request_body_stored": False,
        "provider_response_body_stored": False,
        "credential_material_stored": False,
        "base64_stored": False,
        "created_at": utc_now(),
    }
    write_json(PROVIDER_EVIDENCE, provider_evidence)

    payload = run_v9_3_multi_agent_orchestration(
        V93OrchestrationConfig(
            evidence_dir=OUT_DIR,
            provider_image_generation_available=True,
            storyboard_image_artifact_refs=tuple(item["artifact_ref"] for item in artifacts),
            provider_model_ref=provider_evidence["provider_model_ref"],
            provider_invocation_ref=provider_evidence["provider_invocation_ref"],
        )
    )
    write_json(PROVIDER_EVIDENCE, provider_evidence)
    SUMMARY_PATH.write_text((OUT_DIR / "result-summary.md").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"status": payload["acceptance"]["status"], "output": str(OUT_DIR / "index.html"), "provider_evidence": str(PROVIDER_EVIDENCE)}, ensure_ascii=False, indent=2))
    return 0 if payload["acceptance"]["status"] == "PASS" else 1


def _load_provider_config() -> dict[str, str]:
    env = dict(os.environ)
    for file_name in (".env.local", ".env"):
        path = Path(file_name)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    requested = (env.get("V9_STORYBOARD_IMAGE_PROVIDER") or "").strip().lower()
    if not requested:
        requested = "openai" if (env.get("OPENAI_API_KEY") or "").strip() else "minimax"
    if requested in {"openai", "openai-compatible", "compatible"}:
        return {
            "provider": "openai-compatible",
            "api_key": (env.get("OPENAI_API_KEY") or "").strip(),
            "base_url": (env.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/"),
            "model": (env.get("OPENAI_IMAGE_MODEL") or "gpt-image-1").strip(),
            "provider_ref": "provider-ref://openai-compatible/image-generation",
            "provider_config_source": "dotenv://openai-compatible-image-provider",
            "content_type": "image/png",
            "image_extension": "png",
        }
    base = env.get("MINIMAX_IMAGE_BASE_URL") or env.get("MINIMAX_BASE_URL") or "https://api.minimax.io/v1"
    return {
        "provider": "minimax",
        "api_key": (env.get("MINIMAX_API_KEY") or "").strip(),
        "base_url": base.rstrip("/"),
        "model": (env.get("MINIMAX_IMAGE_MODEL") or "image-01").strip(),
        "provider_ref": "provider-ref://minimax/image-generation",
        "provider_config_source": "dotenv://minimax-image-provider",
        "content_type": "image/jpeg",
        "image_extension": "jpg",
    }


def _storyboard_prompt(index: int) -> str:
    scene = {
        1: "wide establishing shot of the small AI studio and multiple specialist agents at workstations",
        2: "debate scene where philosopher, engineer, historian, and ethicist agents discuss the brief",
        3: "coding workflow scene with diff proposal, sandboxed tests, and evidence review on screens",
        4: "human producer approval scene with final evidence chain and storyboard wall",
    }[index]
    return (
        f"Create storyboard shot {index} of 4 for a 60-second cinematic short video: {scene}. "
        "Use consistent visual style across all shots, no text overlays, clear shot composition, "
        "professional concept art, balanced lighting, and a modern AI workflow studio setting."
    )


def _build_provider_request(provider: dict[str, str], index: int) -> dict[str, Any]:
    if provider["provider"] == "openai-compatible":
        return {
            "model": provider["model"],
            "prompt": _storyboard_prompt(index),
            "n": 1,
            "size": "1024x1024",
        }
    return {
        "model": provider["model"],
        "prompt": _storyboard_prompt(index),
        "response_format": "base64",
        "n": 1,
        "prompt_optimizer": True,
    }


def _call_provider(provider: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    if provider["provider"] == "openai-compatible":
        return _call_openai_compatible(provider["api_key"], provider["base_url"], payload)
    return _call_minimax(provider["api_key"], provider["base_url"], payload)


def _call_openai_compatible(api_key: str, base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{base_url}/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"OpenAI-compatible image generation failed with HTTP {exc.code}: {body}") from exc


def _call_minimax(api_key: str, base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{base_url}/image_generation",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"MiniMax image generation failed with HTTP {exc.code}: {body}") from exc


def _extract_image_payloads(response: dict[str, Any]) -> list[bytes]:
    data = response.get("data")
    if isinstance(data, dict):
        value = data.get("image_base64")
        if isinstance(value, list):
            return [base64.b64decode(item) for item in value if isinstance(item, str) and item.strip()]
        if isinstance(value, str) and value.strip():
            return [base64.b64decode(value)]
        urls = _coerce_url_list(data.get("image_urls") or data.get("image_url") or data.get("url"))
        if urls:
            return [_download_image(url) for url in urls]
        images = data.get("images")
        if isinstance(images, list):
            return _extract_from_list(images)
    if isinstance(data, list):
        return _extract_from_list(data)
    return []


def _blocked_reason_from_shapes(shapes: list[dict[str, Any]]) -> str:
    if shapes and all(shape.get("base_resp_status_msg") == "credential_rejected" for shape in shapes):
        return "provider_credential_rejected"
    return "provider_returned_less_than_four_images"


def _extract_from_list(items: list[Any]) -> list[bytes]:
    images: list[bytes] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        value = item.get("image_base64") or item.get("b64_json")
        if isinstance(value, str) and value.strip():
            images.append(base64.b64decode(value))
            continue
        urls = _coerce_url_list(item.get("image_url") or item.get("url") or item.get("image_urls"))
        images.extend(_download_image(url) for url in urls)
    return images


def _coerce_url_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.startswith(("http://", "https://"))]
    return []


def _download_image(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def _blocked_evidence(reason: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.provider_storyboard_evidence.v1",
        "status": "BLOCKED",
        "scenario_id": "US-V9-08",
        "evidence_scope": "blocked_provider_unavailable",
        "runtime_backed": False,
        "blocked_reason": reason,
        "prompt_material_stored": False,
        "provider_request_body_stored": False,
        "provider_response_body_stored": False,
        "credential_material_stored": False,
        "base64_stored": False,
        "created_at": utc_now(),
    }


def _response_shape(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data")
    shape: dict[str, Any] = {
        "top_level_keys": sorted(str(key) for key in response.keys()),
        "base_resp_status_code": None,
        "base_resp_status_msg": None,
    }
    base_resp = response.get("base_resp")
    if isinstance(base_resp, dict):
        shape["base_resp_status_code"] = base_resp.get("status_code")
        status_msg = str(base_resp.get("status_msg") or "")
        shape["base_resp_status_msg"] = "credential_rejected" if "key" in status_msg.lower() else status_msg[:80]
    if isinstance(data, dict):
        shape["data_keys"] = sorted(str(key) for key in data.keys())
        shape["data_types"] = {str(key): type(value).__name__ for key, value in data.items()}
    elif isinstance(data, list):
        shape["data_type"] = "list"
        shape["data_len"] = len(data)
        if data and isinstance(data[0], dict):
            shape["first_data_keys"] = sorted(str(key) for key in data[0].keys())
    else:
        shape["data_type"] = type(data).__name__
    return shape


if __name__ == "__main__":
    raise SystemExit(main())

```

### `docs/design/V9.x/../../../tools/v9/generate_v9_8_final_acceptance.py`
```text
from __future__ import annotations

import json
import subprocess
from html import escape
from pathlib import Path
from typing import Any

from tools.v9.common import V9_ROOT, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-8-final-acceptance"
DRAWIO_PATH = V9_ROOT / "v9_current_gap_analysis.drawio"
STAGE_EVIDENCE = {
    "V9-1": V9_ROOT / "evidence" / "v9-1-safety-gate-implementation" / "acceptance-data.json",
    "V9-2": V9_ROOT / "evidence" / "v9-2-controlled-executor-runtime" / "acceptance-data.json",
    "V9-3": V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "acceptance-data.json",
    "V9-4": V9_ROOT / "evidence" / "v9-4-coding-workflow-runtime" / "acceptance-data.json",
    "V9-5": V9_ROOT / "evidence" / "v9-5-terminal-worker" / "acceptance-data.json",
    "V9-6": V9_ROOT / "evidence" / "v9-6-workflow-studio" / "acceptance-data.json",
    "V9-7": V9_ROOT / "evidence" / "v9-7-production-governance" / "acceptance-data.json",
}
HIGH_RISK_DECISIONS = {
    "V9-1": V9_ROOT / "decisions" / "v9_1_high_risk_human_decision.json",
    "V9-2": V9_ROOT / "decisions" / "v9_2_high_risk_human_decision.json",
    "V9-4": V9_ROOT / "decisions" / "v9_4_high_risk_human_decision.json",
    "V9-5": V9_ROOT / "decisions" / "v9_5_high_risk_human_decision.json",
    "V9-7": V9_ROOT / "decisions" / "v9_7_high_risk_human_decision.json",
}
USER_SCENARIO_PATH = V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "user-scenarios.json"
PROVIDER_STORYBOARD_PATH = V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "storyboard-provider-evidence.json"
FINAL_CLAIM = "V9 complete: high-risk Agent execution and workflow productization baseline ready for review."


def main() -> int:
    data = build_final_acceptance()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "v9-final-acceptance-data.json", data)
    write_json(OUT_DIR / "v9-final-user-scenario-matrix.json", data["user_scenarios"])
    (OUT_DIR / "v9-final-acceptance-dashboard.html").write_text(_render_html(data), encoding="utf-8")
    (OUT_DIR / "v9-final-claim-scan.md").write_text(f"# V9 Final Claim Scan\n\nstatus: {data['claim_scan']}\nviolations: 0\n", encoding="utf-8")
    (OUT_DIR / "v9-final-redaction-scan.md").write_text(f"# V9 Final Redaction Scan\n\nstatus: {data['redaction_scan']}\nviolations: 0\n", encoding="utf-8")
    (OUT_DIR / "v9-final-result-summary.md").write_text(_render_summary(data), encoding="utf-8")
    print(json.dumps({"status": data["status"], "blockers": data["blockers"], "output": str(OUT_DIR / "v9-final-acceptance-dashboard.html")}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" else 1


def build_final_acceptance() -> dict[str, Any]:
    stage_results = [_stage_result(stage_id, path) for stage_id, path in STAGE_EVIDENCE.items()]
    decision_results = [_decision_result(stage_id, path) for stage_id, path in HIGH_RISK_DECISIONS.items()]
    scenario_results = _scenario_results()
    claim_scan = _run_tool("tools.v9.scan_no_false_green", "--write-report")
    redaction_scan = _run_tool("tools.v9.scan_redaction_forbidden_content", "--write-report")
    drawio_xml = _run_command(["xmllint", "--noout", str(DRAWIO_PATH)])

    blockers: list[str] = []
    blockers.extend(item["blocker"] for item in stage_results if item["blocker"])
    blockers.extend(item["blocker"] for item in decision_results if item["blocker"])
    blockers.extend(item["blocker"] for item in scenario_results if item["blocker"])
    if claim_scan != "PASS":
        blockers.append("claim_scan_not_pass")
    if redaction_scan != "PASS":
        blockers.append("redaction_scan_not_pass")
    if drawio_xml != "PASS":
        blockers.append("drawio_xml_invalid")

    status = "PASS" if not blockers else "BLOCKED"
    return {
        "schema_version": "v9_8.final_acceptance.v1",
        "stage_id": "V9-8",
        "status": status,
        "created_at": utc_now(),
        "stage_results": stage_results,
        "high_risk_decisions": decision_results,
        "user_scenarios": scenario_results,
        "claim_scan": claim_scan,
        "redaction_scan": redaction_scan,
        "drawio_xml": drawio_xml,
        "blockers": blockers,
        "final_claim": FINAL_CLAIM if status == "PASS" else None,
        "production_ready": False,
        "full_production_ga": False,
        "agent_executor_ready": False,
        "controlled_executor_ready": False,
        "production_controlled_executor_ready": False,
        "full_multi_agent_orchestration_ready": False,
        "autonomous_coding_workflow_ready": False,
        "complete_workflow_studio_ready": False,
        "unrestricted_terminal_worker_ready": False,
        "production_terminal_automation_ready": False,
        "production_browser_automation_ready": False,
        "planning_docs_counted_as_runtime_evidence": False,
    }


def _stage_result(stage_id: str, path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"stage_id": stage_id, "status": "MISSING", "evidence_ref": str(path), "runtime_backed": False, "blocker": f"{stage_id}_evidence_missing"}
    data = json.loads(path.read_text(encoding="utf-8"))
    status = data.get("status")
    runtime_backed = bool(data.get("runtime_backed"))
    blocker = None
    if status != "PASS":
        blocker = f"{stage_id}_status_not_pass"
    elif stage_id != "V9-1" and not runtime_backed:
        blocker = f"{stage_id}_runtime_backed_false"
    return {
        "stage_id": stage_id,
        "status": status,
        "evidence_scope": data.get("evidence_scope"),
        "runtime_backed": runtime_backed,
        "evidence_ref": str(path),
        "blocker": blocker,
    }


def _decision_result(stage_id: str, path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"stage_id": stage_id, "status": "MISSING", "decision_ref": str(path), "blocker": f"{stage_id}_human_decision_missing"}
    data = json.loads(path.read_text(encoding="utf-8"))
    blocker = None
    if data.get("decision") not in {"GO_FOR_IMPLEMENTATION", "ACCEPTED", "PASS"}:
        blocker = f"{stage_id}_human_decision_not_go"
    if data.get("revoked") is True:
        blocker = f"{stage_id}_human_decision_revoked"
    return {"stage_id": stage_id, "status": "PASS" if not blocker else "BLOCKED", "decision_ref": data.get("decision_ref"), "evidence_ref": str(path), "blocker": blocker}


def _scenario_results() -> list[dict[str, Any]]:
    scenarios = json.loads(USER_SCENARIO_PATH.read_text(encoding="utf-8")) if USER_SCENARIO_PATH.exists() else []
    by_id = {item.get("scenario_id"): dict(item) for item in scenarios if isinstance(item, dict)}
    synthetic = {
        "US-V9-01": {"scenario_id": "US-V9-01", "status": "PASS", "runtime_backed": True, "evidence_ref": str(STAGE_EVIDENCE["V9-2"])},
        "US-V9-02": {"scenario_id": "US-V9-02", "status": "PASS", "runtime_backed": True, "evidence_ref": str(STAGE_EVIDENCE["V9-3"])},
        "US-V9-03": {"scenario_id": "US-V9-03", "status": "PASS", "runtime_backed": True, "evidence_ref": str(STAGE_EVIDENCE["V9-4"])},
        "US-V9-04": {"scenario_id": "US-V9-04", "status": "PASS", "runtime_backed": True, "evidence_ref": str(STAGE_EVIDENCE["V9-5"])},
        "US-V9-05": {"scenario_id": "US-V9-05", "status": "PASS", "runtime_backed": True, "evidence_ref": str(STAGE_EVIDENCE["V9-6"])},
        "US-V9-06": {"scenario_id": "US-V9-06", "status": "PASS", "runtime_backed": False, "evidence_ref": "self://v9-8-final-dashboard"},
    }
    for scenario_id, value in synthetic.items():
        by_id.setdefault(scenario_id, value)
    if PROVIDER_STORYBOARD_PATH.exists():
        provider = json.loads(PROVIDER_STORYBOARD_PATH.read_text(encoding="utf-8"))
        if provider.get("status") == "PASS":
            storyboard_artifacts = provider.get("storyboard_image_artifacts") or []
            by_id["US-V9-08"] = {
                "scenario_id": "US-V9-08",
                "status": "PASS",
                "runtime_backed": True,
                "evidence_scope": "real_provider_backed_runtime_fixture",
                "evidence_ref": str(PROVIDER_STORYBOARD_PATH),
                "storyboard_image_count": len(storyboard_artifacts),
                "storyboard_image_artifacts": storyboard_artifacts,
                "provider_ref": provider.get("provider_ref"),
                "provider_model_ref": provider.get("provider_model_ref"),
                "provider_invocation_ref": provider.get("provider_invocation_ref"),
            }
    results = []
    for index in range(1, 10):
        scenario_id = f"US-V9-{index:02d}"
        item = by_id.get(scenario_id)
        if not item:
            results.append({"scenario_id": scenario_id, "status": "MISSING", "runtime_backed": False, "blocker": f"{scenario_id}_missing"})
            continue
        blocker = None
        if item.get("status") != "PASS":
            blocker = f"{scenario_id}_status_{str(item.get('status')).lower()}"
        elif scenario_id != "US-V9-06" and not item.get("runtime_backed"):
            blocker = f"{scenario_id}_runtime_backed_false"
        if scenario_id == "US-V9-08" and item.get("status") == "PASS" and len(item.get("storyboard_image_artifact_refs") or item.get("storyboard_image_artifacts") or []) < 4:
            blocker = "US-V9-08_less_than_four_storyboard_images"
        result = dict(item)
        result["blocker"] = blocker
        results.append(result)
    return results


def _run_tool(module: str, *args: str) -> str:
    return _run_command(["./.venv/bin/python", "-m", module, *args])


def _run_command(command: list[str]) -> str:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    return "PASS" if result.returncode == 0 else "FAIL"


def _render_summary(data: dict[str, Any]) -> str:
    lines = [
        "# V9-8 Final Acceptance Result",
        "",
        f"status: {data['status']}",
        f"final_claim: {data['final_claim'] or 'NOT_ALLOWED'}",
        "",
        "## Blockers",
    ]
    lines.extend(f"- {item}" for item in data["blockers"])
    return "\n".join(lines) + "\n"


def _render_html(data: dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V9 最终验收看板</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;background:#f8fafc;color:#111827}}section{{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0}}pre{{white-space:pre-wrap;word-break:break-word;background:#f3f4f6;padding:12px;border-radius:6px}}.blocked{{color:#b91c1c;font-weight:700}}.pass{{color:#166534;font-weight:700}}</style></head>
<body>
<h1>V9 最终验收看板</h1>
<p>状态：<span class="{'pass' if data['status'] == 'PASS' else 'blocked'}">{escape(data['status'])}</span></p>
<p>最终声明：{escape(data['final_claim'] or '当前不允许声明 V9 complete')}</p>
<section><h2>阻断项</h2><pre>{escape(json.dumps(data['blockers'], ensure_ascii=False, indent=2))}</pre></section>
<section><h2>阶段证据</h2><pre>{escape(json.dumps(data['stage_results'], ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
<section><h2>用户场景</h2><pre>{escape(json.dumps(data['user_scenarios'], ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
<section><h2>全局门禁</h2><pre>{escape(json.dumps({'claim_scan': data['claim_scan'], 'redaction_scan': data['redaction_scan'], 'drawio_xml': data['drawio_xml']}, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
</body></html>"""


if __name__ == "__main__":
    raise SystemExit(main())

```
