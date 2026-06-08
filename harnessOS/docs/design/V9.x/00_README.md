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
| V9-8 final acceptance validator | PASS / COMPLETE FOR REVIEW | Final dashboard/data are generated; US-V9-08 provider-backed storyboard image evidence is available and final claim is limited to ready for review. |

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
