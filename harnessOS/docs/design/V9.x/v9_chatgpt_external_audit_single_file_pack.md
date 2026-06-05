# V9 ChatGPT External Audit Single File Pack

文档状态：external audit attachment / V9-1 safety gate implementation evidence / not runtime executor evidence。

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
proceed_to_v9_3_runtime_implementation=false
proceed_to_v9_4_runtime_implementation=false
proceed_to_v9_full_runtime_development=false
runtime_executor_route_created=false
runtime_worker_created=false
source_agent_durable_mutation_allowed=false
```

## Included Files
- `docs/design/V9.x/00_README.md` exists=True size=10759
- `docs/design/V9.x/v9_target_prd.md` exists=True size=4329
- `docs/design/V9.x/v9_target_architecture.md` exists=True size=4000
- `docs/design/V9.x/v9_current_gap_analysis.md` exists=True size=2879
- `docs/design/V9.x/v9_front_stage_development_readiness_audit.md` exists=True size=5568
- `docs/design/V9.x/v9_development_and_acceptance_plan.md` exists=True size=7061
- `docs/design/V9.x/v9_acceptance_gate_matrix.md` exists=True size=3778
- `docs/design/V9.x/v9_no_false_green_claim_guard.md` exists=True size=2881
- `docs/design/V9.x/v9_contract_schema_bundle.md` exists=True size=5237
- `docs/design/V9.x/v9_human_authorization_ref_contract.md` exists=True size=3955
- `docs/design/V9.x/v9_api_and_service_boundary_spec.md` exists=True size=3058
- `docs/design/V9.x/v9_evidence_package_schema_and_validator_spec.md` exists=True size=3347
- `docs/design/V9.x/v9_test_fixture_and_ci_matrix.md` exists=True size=2726
- `docs/design/V9.x/v9_high_risk_human_decision_protocol.md` exists=True size=1556
- `docs/design/V9.x/v9_security_threat_model_and_abuse_cases.md` exists=True size=1709
- `docs/design/V9.x/v9_operational_runbook_and_incident_response.md` exists=True size=1325
- `docs/design/V9.x/v9_1_agent_executor_contract_package.md` exists=True size=6402
- `docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md` exists=True size=2790
- `docs/design/V9.x/v9_2_controlled_executor_engineering_design.md` exists=True size=2354
- `docs/design/V9.x/v9_3_orchestration_coordinator_engineering_design.md` exists=True size=1985
- `docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md` exists=True size=1712
- `docs/design/V9.x/v9_5_terminal_sandbox_engineering_design.md` exists=True size=1735
- `docs/design/V9.x/v9_6_workflow_studio_engineering_design.md` exists=True size=1660
- `docs/design/V9.x/v9_7_production_governance_engineering_design.md` exists=True size=1469
- `docs/design/V9.x/v9_8_final_acceptance_validator_engineering_design.md` exists=True size=1811
- `docs/design/V9.x/v9_document_audit_report.md` exists=True size=9666
- `docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json` exists=True size=2004
- `docs/design/V9.x/decisions/v9_2_high_risk_human_decision.json` exists=True size=2390
- `docs/design/V9.x/v9_2_pre_implementation_development_and_acceptance_plan.md` exists=True size=3177
- `docs/design/V9.x/v9_2_pre_implementation_audit_closure.md` exists=True size=7764
- `docs/design/V9.x/reports/v9_1_contract_validation_report.json` exists=True size=8356
- `docs/design/V9.x/reports/v9_1_negative_test_results.json` exists=True size=1502
- `docs/design/V9.x/reports/v9_1_no_false_green_scan.json` exists=True size=1231
- `docs/design/V9.x/reports/v9_1_redaction_scan.json` exists=True size=642
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
- `docs/design/V9.x/../../../core/policies/v9_agent_executor_safety.py` exists=True size=19642
- `docs/design/V9.x/../../../core/policies/v9_controlled_executor_runtime.py` exists=True size=23374
- `docs/design/V9.x/../../../tests/test_v9_2_controlled_executor_runtime.py` exists=True size=10013
- `docs/design/V9.x/../../../tests/test_v9_2_runtime_evidence.py` exists=True size=2327

## Attachments

### `docs/design/V9.x/00_README.md`
```markdown
# V9.x Design Index

文档状态：V9 planning package / high-risk execution productization entry。

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
| `v9_no_false_green_claim_guard.md` | V9 禁止声明、误报词和 claim scan 规则。 |
| `v9_planning_audit_for_chatgpt.md` | 给 ChatGPT / 外部审计的审计入口。 |
| `v9_document_audit_report.md` | V9 文档自审报告与进入外部审计建议。 |
| `v9_front_stage_development_readiness_audit.md` | V9-1 到 V9-4 前阶段开发就绪自审。 |
| `v9_1_agent_executor_contract_package.md` | V9-1 Agent executor safety gate 合同包。 |
| `v9_human_authorization_ref_contract.md` | V9 durable mutation 人工授权引用合同。 |
| `v9_2_controlled_executor_implementation_spec.md` | V9-2 controlled executor runtime 实现前规格。 |
| `v9_3_multi_agent_orchestration_implementation_spec.md` | V9-3 multi-Agent orchestration 实现前规格。 |
| `v9_4_autonomous_coding_workflow_implementation_spec.md` | V9-4 autonomous coding workflow 实现前规格。 |
| `v9_5_terminal_worker_boundary_implementation_spec.md` | V9-5 governed terminal worker 实现前规格。 |
| `v9_6_workflow_studio_productization_prd.md` | V9-6 Workflow Studio 独立 PRD。 |
| `v9_7_production_governance_terminal_automation_gate_spec.md` | V9-7 governance/evidence/terminal automation 高风险门禁规格。 |
| `v9_8_final_acceptance_framework.md` | V9-8 最终验收框架。 |
| `v9_contract_schema_bundle.md` | V9 machine-readable schema bundle 计划。 |
| `schemas/` | V9 P0 machine-readable JSON Schema 文件。 |
| `fixtures/` | V9 P0 negative fixture 和 evidence sample。 |
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
| V9-0 documentation planning | GO | This package defines the PRD, architecture, gap, plan, drawio and claim guard. |
| V9-1 contract audit | CONDITIONAL GO | Requires external acceptance of AgentExecutionPolicy, AgentExecutionEnvelope, CapabilityResolver and safety matrix. |
| V9-1 implementation | NO-GO until V9-1 contract audit and P0 implementation package accepted | Agent executor safety gate and schema/fixture package must be externally reviewed first. |
| V9-2 runtime implementation | NO-GO until V9-1 accepted | Controlled executor requires policy, approval, evidence, rollback and kill switch contracts. |
| V9-3 orchestration runtime | NO-GO until V9-2 accepted | Multi-Agent orchestration depends on controlled execution and attempt history. |
| V9-4 autonomous coding | NO-GO until V9-2/V9-3 accepted | Coding workflow requires sandbox, diff, tests, review and human gates. |
| V9-5 terminal expansion | NO-GO until separate high-risk decision | Terminal write capability is high-risk and cannot become unrestricted shell. |
| V9-6 Studio productization | NO-GO until BFF/DTO boundary accepted | Studio must not directly write runtime truth. |
| V9-7 production governance / evidence hardening / terminal automation | NO-GO / design gate first | Production automation requires tenant, credential, audit, incident, evidence and approval boundaries. |
| V9-8 final acceptance | NO-GO until V9-0..V9-7 evidence exists | Final claim cannot be issued from planning docs alone. |

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
V9-1 external implementation-readiness audit: GO
V9-1 runtime implementation: NO-GO
V9-2 runtime implementation: NO-GO until V9-1 PASS
V9-3 runtime implementation: NO-GO until V9-2 PASS
V9-4 runtime implementation: NO-GO until V9-2 and V9-3 PASS
```

```

### `docs/design/V9.x/v9_target_prd.md`
```markdown
# V9 Target PRD

文档状态：V9 target PRD / planning baseline。

## 1. Product Goal

V9 面向 V8 之后的高风险能力补齐：

```text
让 Agent 不只是“在岗解释和产出”，而是在受控边界内具备执行、协作、代码开发、Studio 编辑和终端自动化能力。
```

V9 的产品目标不是一次性宣布完整生产可用，而是建立可审计、可回滚、可人工接管的高风险执行基线。

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

文档状态：V9 target architecture / planning baseline。

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
| ControlledAgentExecutor | Executes only approved actions | not unrestricted executor |
| OrchestrationCoordinator | Coordinates serial, parallel and fan-in/fan-out runs | keeps attempt history |
| CodingWorkflowRuntime | Runs planning, implementation, test, review and fix loops | no auto commit / auto push / auto deploy by default |
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

文档状态：V9 gap analysis / planning baseline。

## 1. Current Baseline

```text
V8 complete: station-agent workflow pilot ready for review.
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

## 2. Gap Table

| Area | Current V8 State | V9 Required State | Status | Owner Stage | Risk |
| --- | --- | --- | --- | --- | --- |
| Agent Executor | Agent can propose / handoff; direct durable mutation denied | policy-gated controlled Agent execution | planned | V9-1 / V9-2 | high |
| Multi-Agent Orchestration | bounded project workflow fixture | serial / parallel / fan-in/fan-out runtime with recovery | planned | V9-3 | high |
| Autonomous Coding | terminal handoff proposal only | controlled coding workflow with diff/test/review/fix loop | planned | V9-4 | high |
| Terminal Worker | readonly shell fixture | workspace write sandbox and command tiers | planned | V9-5 | high |
| Workflow Studio | thin console / report / TUI evidence | productized Studio via BFF/DTO | planned | V9-6 | medium |
| Production Governance / Automation | no production terminal/browser automation | production governance / evidence hardening and terminal automation gate | planned | V9-7 | critical |
| Final Acceptance | V8 final framework PASS | V9 evidence aggregation and claim guard | planned | V9-8 | high |

## 3. Gap Classification

```text
complete_for_v8: inherited evidence can be reused only as input.
planned: V9 design / implementation / evidence required.
high_risk: separate human proceed decision required.
critical: production or credential-related boundary.
out_of_scope: not part of default V9.
```

## 4. Current Blockers

```text
No AgentExecutionEnvelope schema accepted.
No controlled Agent executor runtime evidence.
No V9-1 contract package external audit acceptance.
No full orchestration recovery evidence.
No coding workflow sandbox and review loop evidence.
No terminal write sandbox evidence.
No complete Studio BFF/UI acceptance.
No production terminal automation high-risk gate evidence.
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

文档状态：V9-1 to V9-4 development-readiness audit / documentation only。

## 1. Audit Conclusion

当前文档可以支撑：

```text
V9-1 external implementation-readiness audit.
V9 P0 implementation package external review.
V9-2 / V9-3 / V9-4 detailed implementation planning after prior gates pass.
```

当前仍不能支撑：

```text
V9-1 runtime implementation without external audit acceptance.
V9-2 runtime implementation before V9-1 PASS.
V9-3 orchestration runtime before V9-2 PASS.
V9-4 coding workflow runtime before V9-2 and V9-3 PASS.
V9-8 final acceptance from planning/spec docs alone.
```

## 2. Stage Readiness Table

| Stage | Current Readiness | Allowed Next Work | Blocked Work |
| --- | --- | --- | --- |
| V9-1 Agent Executor Safety Gate | READY FOR EXTERNAL IMPLEMENTATION-READINESS AUDIT | contract validator plan, schema/fixture audit, negative test audit | runtime executor route, runtime worker, source=agent durable mutation |
| V9-2 Controlled Executor Runtime | READY FOR DETAILED IMPLEMENTATION PLANNING AFTER V9-1 PASS | executor design review, HumanAuthorizationRef validator planning, evidence package design | runtime execution before V9-1 PASS |
| V9-3 Multi-Agent Orchestration | READY FOR DETAILED IMPLEMENTATION PLANNING AFTER V9-2 PASS | message protocol review, branch state machine review, lineage fixture design | orchestration runtime before V9-2 PASS |
| V9-4 Autonomous Coding Workflow | READY FOR DETAILED IMPLEMENTATION PLANNING AFTER V9-2/V9-3 PASS | sandbox policy review, diff/test/review fixture design | auto commit / auto push / auto deploy, coding runtime before prior gates |

## 3. V9-1 Readiness Evidence

Available inputs:

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
```

V9-3 implementation may only start after:

```text
V9-2 PASS.
serial / parallel / fan-in / fan-out semantics accepted.
lost worker recovery design accepted.
attempt history persistence accepted.
artifact lineage producer_agent_id / producer_attempt_id requirement accepted.
```

## 6. V9-4 Readiness Evidence

Available inputs:

```text
docs/design/V9.x/v9_4_autonomous_coding_workflow_implementation_spec.md
docs/design/V9.x/v9_4_coding_workflow_runtime_engineering_design.md
docs/design/V9.x/v9_automation_assisted_development_policy.md
docs/design/V9.x/v9_test_fixture_and_ci_matrix.md
```

V9-4 implementation may only start after:

```text
V9-2 PASS.
V9-3 PASS.
coding workflow sandbox policy accepted.
no auto commit / auto push / auto deploy policy accepted.
diff proposal, test result, review summary and fix-loop evidence formats accepted.
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
proceed_to_v9_1_runtime_implementation=false
proceed_to_v9_2_runtime_implementation=false
proceed_to_v9_3_runtime_implementation=false
proceed_to_v9_4_runtime_implementation=false
```

V9 front-stage documents are now sufficient for external readiness audit, but not sufficient to claim runtime completion.

```

### `docs/design/V9.x/v9_development_and_acceptance_plan.md`
```markdown
# V9 Development And Acceptance Plan

文档状态：V9 development and acceptance control plan / planning baseline。

## 1. Stage Status Table

| Stage | Purpose | Current Status | Allowed Claim | Boundary |
| --- | --- | --- | --- | --- |
| V9-0 | Planning And High-Risk Boundary Gate | planning | V9-0 complete: high-risk execution planning gate ready for review. | documentation only |
| V9-1 | Agent Executor Safety Gate | planned | V9-1 complete: Agent executor safety gate ready for review. | design / safety gate |
| V9-2 | Controlled Agent Executor Runtime | planned | V9-2 complete: controlled Agent execution runtime slice ready for review. | controlled runtime slice only |
| V9-3 | Multi-Agent Orchestration Runtime | planned | V9-3 complete: multi-Agent orchestration runtime slice ready for review. | not full orchestration GA |
| V9-4 | Autonomous Coding Workflow Pilot | planned | V9-4 complete: autonomous coding workflow pilot ready for review. | no auto commit / auto push / auto deploy |
| V9-5 | Governed Terminal Worker Expansion | planned | V9-5 complete: governed terminal worker expansion ready for review. | not unrestricted shell |
| V9-6 | Workflow Studio Productization | planned | V9-6 complete: Workflow Studio productization slice ready for review. | not complete Studio GA |
| V9-7 | Production Governance / Evidence Hardening and Terminal Automation Gate | planned | V9-7 complete: production governance and terminal automation gate ready for review. | design/high-risk gate first |
| V9-8 | Final Acceptance | planned | V9 complete: high-risk Agent execution and workflow productization baseline ready for review. | not production ready |

## 2. Development Order

```text
V9-0 -> V9-1 -> V9-2 -> V9-3 -> V9-4 -> V9-5 -> V9-6 -> V9-7 -> V9-8
```

V9-1、V9-2、V9-4、V9-5、V9-7 是高风险阶段。每个阶段实现前必须有独立审计和人工 high-risk proceed decision。

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
V9-2 evidence PASS.
Agent message protocol accepted.
Attempt history and artifact lineage contracts accepted.
Serial, parallel, fan-in and fan-out contracts accepted.
Failure recovery and lost worker recovery matrix accepted.
producer_agent_id and producer_attempt_id lineage requirements accepted.
V9-2 runtime evidence PASS.
```

Before V9-4:

```text
V9-2 and V9-3 evidence PASS.
Coding workflow sandbox contract accepted.
Diff / test / review / fix loop accepted.
No auto commit / push / deploy policy accepted.
No unreviewed patch apply policy accepted.
V9-2 and V9-3 runtime evidence packages accepted.
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

文档状态：V9 acceptance control matrix / planning baseline。

| Stage | Entry Gate | Acceptance Gate | Stop Condition |
| --- | --- | --- | --- |
| V9-0 | V8 final baseline accepted as bounded | PRD, architecture, gap, drawio, plan and claim guard accepted | V9-0 claims runtime complete |
| V9-1 | V9-0 accepted | AgentExecutionPolicy, AgentExecutionEnvelope, CapabilityResolver, approval, kill switch, timeout, rollback and evidence contracts accepted | Agent executor ready is claimed |
| V9-2 | V9-1 contract audit accepted, HumanAuthorizationRef contract accepted and human decision recorded | controlled executor slice proves policy decision, approval evidence, durable mutation invariant and redacted execution evidence | source=agent mutates by default or durable mutation runs without user_confirmed=true OR valid human_authorization_ref |
| V9-3 | V9-2 PASS | serial, parallel, fan-in, fan-out, failure recovery, lost worker recovery, attempt history, artifact lineage, producer_agent_id and producer_attempt_id evidence exist | full multi-Agent orchestration is claimed without complete evidence |
| V9-4 | V9-2 / V9-3 PASS | coding workflow produces diff, test, review, fix-loop and evidence with sandbox boundary | auto commit / auto push / auto deploy occurs without approval; automated tooling applies patches, commits, pushes, deploys, or marks review as approval |
| V9-5 | V8-6/V8-7 evidence and new human decision | terminal worker sandbox evidence exists | unrestricted shell is allowed |
| V9-6 | Studio PRD and BFF boundary accepted | Studio UI operates through DTO/BFF and passes browser denylist | Studio directly writes runtime truth |
| V9-7 | production governance / evidence hardening spec and human decision | governance, evidence hardening and terminal automation gate evidence exists | browser/terminal automation runs without credential, approval, evidence and incident boundary |
| V9-8 | V9-0..V9-7 evidence exists | final dashboard, claim scan, redaction scan and drawio XML pass | final claim emitted while any stage is BLOCKED |

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
input_fixture
expected_output
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

## 6. Front-Stage Fixture-To-Test Matrix

| Stage | Fixture | Expected Result |
| --- | --- | --- |
| V9-1 | `schema-negative/source_agent_durable_mutation.json` | rejected by envelope validator and CapabilityResolver |
| V9-1 | `fixtures/evidence/v9_1_contract_freeze_sample.json` | accepted only as contract_freeze, not runtime evidence |
| V9-2 | `schema-negative/expired_human_authorization_ref.json` | rejected by HumanAuthorizationRef validator |
| V9-2 | `schema-negative/raw_secret_in_evidence.json` | rejected by evidence schema and redaction scan |
| V9-3 | `schema-negative/artifact_lineage_missing_producer_attempt.json` | rejected by artifact lineage schema |
| V9-4 | coding workflow no-auto-deploy fixture | must deny deploy and record evidence; fixture still required before implementation |
| V9-8 | `fixtures/evidence/v9_8_reject_planning_only_sample.json` | final validator returns BLOCKED, not PASS |

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

### `docs/design/V9.x/v9_6_workflow_studio_engineering_design.md`
```markdown
# V9-6 Workflow Studio Engineering Design

文档状态：V9-6 engineering design / planned only。

## 1. Boundary

Workflow Studio is a productization slice through BFF / DTO / read models. It cannot directly write WorkflowStore, WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun or Artifact.

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

### `docs/design/V9.x/v9_7_production_governance_engineering_design.md`
```markdown
# V9-7 Production Governance Engineering Design

文档状态：V9-7 engineering design / planned only。

## 1. Boundary

V9-7 hardens production governance, evidence and terminal automation gates. It does not prove production automation ready or production browser automation ready.

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

```

### `docs/design/V9.x/v9_8_final_acceptance_validator_engineering_design.md`
```markdown
# V9-8 Final Acceptance Validator Engineering Design

文档状态：V9-8 engineering design / planned only。

## 1. Purpose

V9-8 validator aggregates stage evidence and decides whether the final V9 ready-for-review claim can be emitted. It must reject planning-only evidence for runtime stages.

Current rejection fixture:

```text
docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json
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

文档状态：V9-0 remediation self-audit / PASS for contract audit entry。

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
V9-3 engineering design exists -> PASS
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
External audit should confirm whether V9-1 Agent executor safety contracts are detailed enough for implementation planning.
External audit should confirm whether HumanAuthorizationRef can serve as equivalent durable mutation authorization to user_confirmed=true.
External audit should confirm whether V9 P0 engineering package is sufficient to start V9-1 implementation-readiness audit.
External audit should confirm whether V9 front-stage readiness package is sufficient to start V9-1 implementation planning after human approval.
External audit should confirm whether V9-2..V9-8 engineering designs are sufficient to start stage-by-stage detailed implementation planning after prior gates pass.
External audit should confirm whether V9-7 governance/evidence hardening scope prevents production automation overclaim.
```

## 7. Proceed Recommendation

```text
proceed_to_external_audit=true
proceed_to_v9_front_stage_readiness_audit=true
proceed_to_v9_1_contract_audit=true
v9_runtime_specs_ready_for_external_review=true
v9_p0_engineering_package_ready_for_external_review=true
v9_p0_implementation_package_ready_for_external_review=true
proceed_to_v9_1_implementation=false
```

V9-1 implementation should not start until V9-1 contract package and P0 engineering package are externally accepted and a separate implementation plan is approved. V9-2..V9-8 implementation should not start from this document package alone; each stage still needs prior gate PASS, PRD review, E2E fixture and evidence package before coding.

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
  "created_at": "2026-06-05T09:17:12Z",
  "fixture_parse_results": [
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
  "created_at": "2026-06-05T09:17:12Z",
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
  "created_at": "2026-06-05T09:17:30Z",
  "hit_count": 155,
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
  "created_at": "2026-06-05T09:17:30Z",
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
  "created_at": "2026-06-05T09:17:50Z",
  "decisions": {
    "external_audit_decision": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_1_external_audit_decision.md",
    "high_risk_human_decision": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json"
  },
  "external_audit_deferred": true,
  "internal_independent_audit_closed": true,
  "limited_safety_gate_implementation_complete": true,
  "reports": {
    "contract_validation": {
      "created_at": "2026-06-05T09:17:12Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_contract_validation_report.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "negative_tests": {
      "created_at": "2026-06-05T09:17:12Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_negative_test_results.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "no_false_green": {
      "created_at": "2026-06-05T09:17:30Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_no_false_green_scan.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "redaction": {
      "created_at": "2026-06-05T09:17:30Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_redaction_scan.json",
      "runtime_evidence": false,
      "status": "PASS"
    },
    "safety_gate_implementation": {
      "created_at": "2026-06-05T09:17:14Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json",
      "runtime_evidence": null,
      "status": "PASS"
    },
    "v9_2_limited_runtime_slice": {
      "created_at": "2026-06-05T09:17:15Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json",
      "runtime_evidence": null,
      "status": "PASS"
    },
    "v9_2_pre_implementation": {
      "created_at": "2026-06-05T09:17:15Z",
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
  "created_at": "2026-06-05T09:17:14Z",
  "evidence_scope": "real_code_policy_validation",
  "full_multi_agent_orchestration_ready": false,
  "production_controlled_executor_ready": false,
  "reports": {
    "contract_validation": {
      "created_at": "2026-06-05T09:17:12Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_contract_validation_report.json",
      "runtime_evidence": false,
      "status": "PASS",
      "violations": []
    },
    "negative_tests": {
      "created_at": "2026-06-05T09:17:12Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_negative_test_results.json",
      "runtime_evidence": false,
      "status": "PASS",
      "violations": []
    },
    "no_false_green": {
      "created_at": "2026-06-05T09:17:13Z",
      "path": "/Users/Zhuanz/Desktop/workspace/harnessOS/docs/design/V9.x/reports/v9_1_no_false_green_scan.json",
      "runtime_evidence": false,
      "status": "PASS",
      "violations": []
    },
    "redaction": {
      "created_at": "2026-06-05T09:17:14Z",
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
      "capability_decision_ref": "capability-decision://v9-1/4627ab8ae9214e35b52b9673fa3e50cf",
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
      "capability_decision_ref": "capability-decision://v9-1/ed0f85c0e3cc465cbdebcee326ce054e",
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
      "capability_decision_ref": "capability-decision://v9-1/0b1f8a491ad64a3482d55c640e42ccd9",
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
      "capability_decision_ref": "capability-decision://v9-1/79f42ee989f647449a03cb8064fd66f2",
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
      "capability_decision_ref": "capability-decision://v9-1/3de225c63ff54c5c9addb4b48d850f86",
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
      "capability_decision_ref": "capability-decision://v9-1/1bb6ac236c1044b4810b475dd9fa606e",
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
      "capability_decision_ref": "capability-decision://v9-1/06987543897141d8817c788a25ce29c6",
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
      "capability_decision_ref": "capability-decision://v9-1/a96ed4fe542646348bedd27068aa8ce5",
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
      "capability_decision_ref": "capability-decision://v9-1/38bacf1e9d304a3ea6f0c42162be696f",
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
  "created_at": "2026-06-05T09:18:01Z",
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
  "created_at": "2026-06-05T09:17:15Z",
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
  "created_at": "2026-06-05T09:17:15Z",
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
        "created_at": "2026-06-05T09:17:15Z",
        "execution_evidence": {
          "actor_type": "human_user",
          "agent_executor_ready": false,
          "agent_id": "agent-v9-2",
          "approval_gate_ref": null,
          "audit_ref": "audit://v9-2/envelope",
          "capability_decision_ref": "capability-decision://v9-1/ebca56e82f8c4d6795c1f495bd593032",
          "controlled_executor_ready": false,
          "correlation_id": "corr-v9-2",
          "created_at": "2026-06-05T09:17:15Z",
          "decision_chain_refs": {
            "capability_decision_ref": "capability-decision://v9-1/ebca56e82f8c4d6795c1f495bd593032",
            "incident_timeline_ref": "incident-timeline://v9-2/d4c10da4d61f49289f35fd0db88e5810",
            "kill_switch_policy_ref": "kill-switch://v9-2/default",
            "policy_ref": "policy://v9-1/agent-executor-safety/workflow.instance.start",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "timeout_policy_ref": "timeout://v9-2/default"
          },
          "execution_envelope_id": "env-v9-2-workflow.instance.start-idem-v9-2",
          "execution_evidence_ref": "execution-evidence://v9-2/8647859683d64ebb88043b31cdb4f54f",
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
        "incident_timeline_ref": "incident-timeline://v9-2/d4c10da4d61f49289f35fd0db88e5810",
        "operation": "workflow.instance.start",
        "policy_decision": "allow",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_30b6612aa43e",
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
        "created_at": "2026-06-05T09:17:15Z",
        "execution_evidence": {
          "actor_type": "human_user",
          "agent_executor_ready": false,
          "agent_id": "agent-v9-2",
          "approval_gate_ref": null,
          "audit_ref": "audit://v9-2/envelope",
          "capability_decision_ref": "capability-decision://v9-1/3b7469a3c98944a8baf3ee27632e57d8",
          "controlled_executor_ready": false,
          "correlation_id": "corr-v9-2",
          "created_at": "2026-06-05T09:17:15Z",
          "decision_chain_refs": {
            "capability_decision_ref": "capability-decision://v9-1/3b7469a3c98944a8baf3ee27632e57d8",
            "incident_timeline_ref": "incident-timeline://v9-2/d7bec3e611f74439a94dc5565f887f5b",
            "kill_switch_policy_ref": "kill-switch://v9-2/default",
            "policy_ref": "policy://v9-1/agent-executor-safety/station.rerun",
            "rollback_descriptor_ref": "rollback://v9-2/default",
            "timeout_policy_ref": "timeout://v9-2/default"
          },
          "execution_envelope_id": "env-v9-2-station.rerun-idem-v9-2-rerun",
          "execution_evidence_ref": "execution-evidence://v9-2/6a37fb201fb04470832ed31f5f48cde0",
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
        "incident_timeline_ref": "incident-timeline://v9-2/d7bec3e611f74439a94dc5565f887f5b",
        "operation": "station.rerun",
        "policy_decision": "allow",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_7a81ec4a1001",
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
          "created_at": "2026-06-05T09:17:15Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": "approval://v9-2/default",
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/c9f636fca21c4396b2d63caa8d16b5a2",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-05T09:17:15Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/c9f636fca21c4396b2d63caa8d16b5a2",
              "incident_timeline_ref": "incident-timeline://v9-2/df94fc23754d45e89e2d3582de8df933",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/artifact.write",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-artifact.write-idem-v9-2-artifact",
            "execution_evidence_ref": "execution-evidence://v9-2/4dda3a59f5ca4ed08b1108aaa1ca09ab",
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
          "incident_timeline_ref": "incident-timeline://v9-2/df94fc23754d45e89e2d3582de8df933",
          "operation": "artifact.write",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_8059788b02be",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/artifact/artifact-v9-2/1",
          "status": "applied_v9_2_limited_runtime_slice"
        },
        "artifact_versions": [
          {
            "artifact_id": "artifact-v9-2",
            "artifact_version_id": "artifact-version-v9-2-1",
            "content_ref": "artifact-content-ref://v9-2/artifact-v9-2/1",
            "created_at": "2026-06-05T09:17:15Z",
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
          "created_at": "2026-06-05T09:17:15Z",
          "execution_evidence": null,
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/5fee267d222141f09648dc0d5852feec",
          "operation": "artifact.write",
          "policy_decision": "deny",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_09476b999fc3",
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
          "created_at": "2026-06-05T09:17:15Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": "approval://v9-2/default",
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/79b2732635c14b2c906f905f46d33919",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-05T09:17:15Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/79b2732635c14b2c906f905f46d33919",
              "incident_timeline_ref": "incident-timeline://v9-2/d02e84d618ed489e82dbbca66cf04749",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/quality.evaluation.create",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-quality.evaluation.create-idem-v9-2-quality",
            "execution_evidence_ref": "execution-evidence://v9-2/441787954e0a442a85f5233bd7e63997",
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
          "incident_timeline_ref": "incident-timeline://v9-2/d02e84d618ed489e82dbbca66cf04749",
          "operation": "quality.evaluation.create",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_374f5d08ff90",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/quality/quality-v9-2/1",
          "status": "applied_v9_2_limited_runtime_slice"
        },
        "missing_approval": {
          "agent_executor_ready": false,
          "blocked_reason": "approval_gate_required",
          "capability_decision": "deny",
          "controlled_executor_ready": false,
          "created_at": "2026-06-05T09:17:15Z",
          "execution_evidence": null,
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/d20755311d5b483d8ed3282324b09645",
          "operation": "quality.evaluation.create",
          "policy_decision": "deny",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_b13154c5a0f4",
          "runtime_result_ref": null,
          "status": "blocked"
        },
        "quality_evaluations": [
          {
            "created_at": "2026-06-05T09:17:15Z",
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
        "created_at": "2026-06-05T09:17:15Z",
        "execution_evidence": null,
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/1b2df91e8f584a7baf5337030faa32bc",
        "operation": "workflow.instance.start",
        "policy_decision": "deny",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_34827451bdbc",
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
        "created_at": "2026-06-05T09:17:15Z",
        "execution_evidence": null,
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/0c5b0b3506e04860b728e6d6735ffd2a",
        "operation": "workflow.instance.start",
        "policy_decision": "deny",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_6aaea1f3190c",
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
        "created_at": "2026-06-05T09:17:15Z",
        "execution_evidence": null,
        "idempotent_replay": false,
        "incident_timeline_ref": "incident-timeline://v9-2/322ce5f35e17421ca741c322056e6a4a",
        "operation": "workflow.instance.start",
        "policy_decision": "deny",
        "production_controlled_executor_ready": false,
        "result_id": "v9_2_result_331dd399cff5",
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
          "created_at": "2026-06-05T09:17:15Z",
          "execution_evidence": null,
          "idempotent_replay": false,
          "incident_timeline_ref": "incident-timeline://v9-2/c69fb1fc33a04e799db1a86287f62ef0",
          "operation": "workflow.instance.start",
          "policy_decision": "deny",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_82317eef85c2",
          "runtime_result_ref": null,
          "status": "blocked"
        },
        "duplicate": {
          "agent_executor_ready": false,
          "blocked_reason": null,
          "capability_decision": "allow_v9_2_limited_runtime_slice",
          "controlled_executor_ready": false,
          "created_at": "2026-06-05T09:17:15Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": null,
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/a9490ac5dd8347b6acadf79367fce528",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-05T09:17:15Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/a9490ac5dd8347b6acadf79367fce528",
              "incident_timeline_ref": "incident-timeline://v9-2/a1f29ac98d3c4bd7b843bda05ae48407",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/workflow.instance.start",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-workflow.instance.start-idem-v9-2-duplicate",
            "execution_evidence_ref": "execution-evidence://v9-2/290e5d4bf7cb409982d6ea51bc102a60",
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
          "incident_timeline_ref": "incident-timeline://v9-2/a1f29ac98d3c4bd7b843bda05ae48407",
          "operation": "workflow.instance.start",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_fd512904abcd",
          "runtime_result_ref": "runtime-result://v9-2/workflow-v9-2/start",
          "status": "idempotent_replay"
        },
        "first": {
          "agent_executor_ready": false,
          "blocked_reason": null,
          "capability_decision": "allow_v9_2_limited_runtime_slice",
          "controlled_executor_ready": false,
          "created_at": "2026-06-05T09:17:15Z",
          "execution_evidence": {
            "actor_type": "human_user",
            "agent_executor_ready": false,
            "agent_id": "agent-v9-2",
            "approval_gate_ref": null,
            "audit_ref": "audit://v9-2/envelope",
            "capability_decision_ref": "capability-decision://v9-1/a9490ac5dd8347b6acadf79367fce528",
            "controlled_executor_ready": false,
            "correlation_id": "corr-v9-2",
            "created_at": "2026-06-05T09:17:15Z",
            "decision_chain_refs": {
              "capability_decision_ref": "capability-decision://v9-1/a9490ac5dd8347b6acadf79367fce528",
              "incident_timeline_ref": "incident-timeline://v9-2/a1f29ac98d3c4bd7b843bda05ae48407",
              "kill_switch_policy_ref": "kill-switch://v9-2/default",
              "policy_ref": "policy://v9-1/agent-executor-safety/workflow.instance.start",
              "rollback_descriptor_ref": "rollback://v9-2/default",
              "timeout_policy_ref": "timeout://v9-2/default"
            },
            "execution_envelope_id": "env-v9-2-workflow.instance.start-idem-v9-2-duplicate",
            "execution_evidence_ref": "execution-evidence://v9-2/290e5d4bf7cb409982d6ea51bc102a60",
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
          "incident_timeline_ref": "incident-timeline://v9-2/a1f29ac98d3c4bd7b843bda05ae48407",
          "operation": "workflow.instance.start",
          "policy_decision": "allow",
          "production_controlled_executor_ready": false,
          "result_id": "v9_2_result_decacccbc4d7",
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
        "incident_timeline_ref": "incident-timeline://v9-2/2de695b20a884a12890c940c772ad408",
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
