# V5 Development And Acceptance Plan

文档状态：V5 baseline frozen for planning audit。本文定义 V5 后续开发和验收门禁，不执行实现。

## 0. Current V5 Baseline

```text
No False Green Current V5 baseline:
- V4-U9 closure is accepted; V4 feature development is closed.
- V5-0 planning gate is complete / ready for review.
- V5-1 core tenant boundary slice is ready for review, not enterprise auth ready.
- V5-2 core credential/provider lifecycle slice is ready for review, not production secret lifecycle ready.
- V5-3 core observability/audit export slice is ready for review, not production audit export ready.
- V5-4A Agent executor safety gate core slice is ready for review, not Agent executor ready.
- V5-4B synthetic controlled executor dev/local trial is ready for review, not controlled executor ready.
- V5-4C existing V4 local runtime controlled trial is ready for review after bounded dev/local bridge validation.
- V5-5 external app onboarding boundary core slice is ready for review, not production-ready external app support.
- V5-6 Thin Web Console productization slice is ready for review, not complete Workflow Studio ready.
- V5-7A production controlled executor design gate is ready for review, not production controlled executor ready.
- V5-7B limited staging runtime slice is accepted for V5-8 planning entry after external review closure; it remains not production controlled executor ready.
- V5-8A distributed runtime planning gate is ready for review, backed by the existing UX-12 real local Markdown + MiniMax provider evidence.
- V5-8B minimal distributed run coordination slice is ready for review, backed by existing V4 UX-08/09/10 MiniMax provider-backed evidence plus in-memory coordination validation.
- V5-8C artifact lineage and attempt recovery slice is ready for review, backed by existing V4 UX-10 MiniMax provider-backed evidence plus read-only lineage projection.
- V5-8D policy / credential / observability slice is ready for review, backed by existing V4 UX-09 MiniMax provider-backed evidence plus read-only audit projection.
- V5-8E distributed runtime acceptance package is complete and ready for review.
- V5-8 complete: distributed multi-Agent runtime slice ready for review. This is still not full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.
```

## 1. Stage Status Table

| Stage | Current Status | Implementation Status | Allowed Claim | No False Green Boundary |
| --- | --- | --- | --- | --- |
| V5-0 | planning gate complete / ready for review | closed | V5-0 complete: production productization planning gate ready for review. | not production-ready |
| V5-1 | core tenant boundary slice ready for review | core slice implemented | V5-1 complete: production auth and tenant boundary slice ready for review. | not enterprise auth ready |
| V5-2 | core credential/provider lifecycle slice ready for review | core slice implemented | V5-2 complete: credential and provider lifecycle core slice ready for review. | not production secret lifecycle ready |
| V5-3 | core observability/audit export slice ready for review | core slice implemented | V5-3 complete: observability and audit export core slice ready for review. | not production audit export ready |
| V5-4A | safety gate core slice ready for review | core slice implemented | V5-4A complete: Agent executor safety gate core slice ready for review. | not Agent executor ready |
| V5-4B | synthetic controlled executor trial ready for review | synthetic core slice implemented | V5-4B complete: synthetic controlled executor dev/local trial ready for review. | not controlled executor ready |
| V5-4C | existing V4 local runtime trial ready for review | core slice implemented | V5-4C complete: existing V4 local workflow controlled trial ready for review. | not controlled executor ready |
| V5-5 | external app onboarding boundary core slice ready for review | core slice implemented | V5-5 complete: external app onboarding boundary core slice ready for review. | not production-ready external app support |
| V5-6 | Thin Web Console productization slice ready for review | core slice implemented | V5-6 complete: Thin Web Console productization slice ready for review. | not complete Workflow Studio ready |
| V5-7A | production controlled executor design gate ready for review | design gate completed | V5-7A complete: production controlled executor design gate ready for review. | not production controlled executor ready |
| V5-7B | limited staging runtime slice ready for review | isolated staging runtime code implemented, no route / no worker | V5-7B complete: limited production controlled executor runtime slice ready for review. | not production controlled executor ready |
| V5-8A | distributed runtime planning gate ready for review | planning gate evidence generated; runtime implementation not started | V5-8A complete: distributed multi-Agent runtime planning gate ready for review. | not full multi-Agent orchestration ready |
| V5-8B | minimal distributed run coordination slice ready for review | in-memory coordination core slice implemented; no route / no production worker | V5-8B complete: minimal distributed run coordination slice ready for review. | not distributed multi-Agent runtime ready |
| V5-8C | artifact lineage and attempt recovery slice ready for review | in-memory lineage/recovery projection implemented; no route / no production worker | V5-8C complete: artifact lineage and attempt recovery slice ready for review. | not full multi-Agent orchestration ready |
| V5-8D | policy / credential / observability slice ready for review | in-memory policy / credential / observability projection implemented; no route / no production worker | V5-8D complete: policy, credential, and observability slice ready for review. | not distributed multi-Agent runtime ready |
| V5-8E | distributed runtime acceptance package ready for review | final acceptance package generated | V5-8 complete: distributed multi-Agent runtime slice ready for review. | not full multi-Agent orchestration ready |

## 2. V5 Stage Plan

### V5-0 Production Productization Planning Gate

目标：

```text
freeze V5 target PRD
freeze V5 architecture
freeze V5 gap
freeze V5 acceptance plan
freeze V5 claim guard
```

允许声明：

```text
V5-0 complete: production productization planning gate ready for review.
```

不得声明：

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

### V5-1 Production Auth / Tenant Boundary

目标：实现生产认证与租户边界的最小可验收路径。

验收：cross-tenant denied、wrong workspace denied、wrong resource denied、audit actor refs present。

No False Green：V5-1 不能直接声明 enterprise auth ready，除非完整验收通过。

V5-1 实现前必须单独补：

```text
V5-1 PRD
V5-1 target architecture delta
identity / tenant / workspace / app ownership model
API / BFF route design
audit fields
test matrix
no false green guard
```

当前 V5-1 planning package：

```text
docs/design/V5.x/v5_1_production_auth_tenant_boundary_prd.md
docs/design/V5.x/v5_1_target_architecture_delta.md
docs/design/V5.x/v5_1_identity_tenant_ownership_model.md
docs/design/V5.x/v5_1_api_bff_route_design.md
docs/design/V5.x/v5_1_audit_fields.md
docs/design/V5.x/v5_1_test_matrix.md
docs/design/V5.x/v5_1_no_false_green_guard.md
docs/design/V5.x/v5_1_planning_audit_for_chatgpt.md
```

V5-1 implementation remains blocked until external audit findings are closed.

### V5-2 Credential / Provider Lifecycle

目标：实现 provider profile、credential lifecycle、redacted invocation evidence。

验收：key 不进日志、rotation/revocation 有审计、provider evidence 不暴露 secret。

V5-2 进入前必须先完成：

```text
V5-2 PRD
V5-2 target architecture delta
provider profile model
credential lifecycle model
API / BFF route design
audit fields
test matrix
no false green guard
```

V5-2 implementation must not start until those documents pass review.

当前 V5-2 planning package：

```text
docs/design/V5.x/v5_2_credential_provider_lifecycle_prd.md
docs/design/V5.x/v5_2_target_architecture_delta.md
docs/design/V5.x/v5_2_provider_profile_model.md
docs/design/V5.x/v5_2_credential_lifecycle_model.md
docs/design/V5.x/v5_2_api_bff_route_design.md
docs/design/V5.x/v5_2_audit_fields.md
docs/design/V5.x/v5_2_test_matrix.md
docs/design/V5.x/v5_2_no_false_green_guard.md
docs/design/V5.x/v5_2_planning_audit_for_chatgpt.md
```

V5-2 core lifecycle slice is ready for review after implementation and focused validation.

No False Green：V5-2 planning 不证明完整凭证生命周期已经实现，不证明 provider credential production lifecycle 已完成。

### V5-3 Observability / Audit Export

目标：实现 production audit retention/export、metrics、alerting baseline。

验收：audit export 可生成、correlation_id/request_id/actor_id 覆盖、incident timeline 可追溯。

V5-3 进入前必须先完成：

```text
V5-3 PRD
V5-3 target architecture delta
observability event model
audit retention / export model
metrics / alerting model
incident timeline model
API / BFF route design
test matrix
no false green guard
```

V5-3 implementation started only after the planning documents and audit questions were reviewed. The completed core slice remains limited to in-memory dev/local observability primitives and does not create production audit export infrastructure.

No False Green：V5-3 不得把 V4/V5-2 evidence 写成 production audit export ready。

Allowed completion claim:

```text
V5-3 complete: observability and audit export core slice ready for review.
```

This does not prove production audit export ready, production observability platform ready, Agent executor ready, controlled executor ready, production-ready external app support, complete Workflow Studio ready, or distributed multi-Agent runtime ready.

当前 V5-3 planning package：

```text
docs/design/V5.x/v5_3_observability_audit_export_prd.md
docs/design/V5.x/v5_3_target_architecture_delta.md
docs/design/V5.x/v5_3_observability_event_model.md
docs/design/V5.x/v5_3_audit_retention_export_model.md
docs/design/V5.x/v5_3_metrics_alerting_model.md
docs/design/V5.x/v5_3_incident_timeline_model.md
docs/design/V5.x/v5_3_api_bff_route_design.md
docs/design/V5.x/v5_3_test_matrix.md
docs/design/V5.x/v5_3_no_false_green_guard.md
docs/design/V5.x/v5_3_planning_audit_for_chatgpt.md
```

### V5-4 Agent Executor Safety Gate

目标：建立 Agent executor 安全门禁和受控执行边界。

验收：source=agent 不能绕过 policy/user confirmation；high-risk action approval-gated；kill switch 可审计。

建议拆分：

```text
V5-4A Agent Executor Design & Safety Gate
V5-4B Synthetic Controlled Executor Dev/Local Trial
V5-4C Existing V4 Local Runtime Controlled Trial, only if V5-4C audit passes
```

V5-4A 只能声明 safety gate core slice ready for review，不能声明 Agent executor ready。V5-4B 只能声明 synthetic controlled executor dev/local trial ready for review。V5-4C 必须单独审计 existing V4 local runtime entrypoint 后才能实现。

Allowed completion claim:

```text
V5-4A complete: Agent executor safety gate core slice ready for review.
```

This does not prove Agent executor ready, controlled executor ready, production controlled executor ready, autonomous workflow editing ready, complete Workflow Studio ready, production-ready external app support, or distributed multi-Agent runtime ready.

当前 V5-4A / V5-4B planning package：

```text
docs/design/V5.x/v5_4a_agent_executor_safety_gate_prd.md
docs/design/V5.x/v5_4a_target_architecture_delta.md
docs/design/V5.x/v5_4a_policy_capability_matrix.md
docs/design/V5.x/v5_4a_approval_sandbox_kill_switch_model.md
docs/design/V5.x/v5_4a_test_matrix.md
docs/design/V5.x/v5_4a_no_false_green_guard.md
docs/design/V5.x/v5_4a_planning_audit_for_chatgpt.md
docs/design/V5.x/v5_4b_controlled_executor_devlocal_trial_prd.md
docs/design/V5.x/v5_4b_target_architecture_delta.md
docs/design/V5.x/v5_4b_trial_runtime_boundary.md
docs/design/V5.x/v5_4b_test_matrix.md
docs/design/V5.x/v5_4b_no_false_green_guard.md
docs/design/V5.x/v5_4b_planning_audit_for_chatgpt.md
docs/design/V5.x/v5_4b_controlled_executor_devlocal_trial_completion_note.md
docs/design/V5.x/v5_4c_existing_v4_runtime_trial_plan.md
docs/design/V5.x/v5_4c_pre_implementation_audit.md
```

V5-4B allowed completion claim:

```text
V5-4B complete: synthetic controlled executor dev/local trial ready for review.
```

This does not prove controlled executor ready, Agent executor ready, production controlled executor ready, autonomous workflow editing ready, complete Workflow Studio ready, production-ready external app support, or distributed multi-Agent runtime ready.

V5-4C allowed completion claim:

```text
V5-4C complete: existing V4 local workflow controlled trial ready for review.
```

This would still not prove production controlled executor ready or Agent executor ready.

Historical note: older V5-4D / V5-4E planning docs are superseded by V5-7A / V5-7B after the product decision to place production controlled executor after V5-6.

V5-7A allowed future claim, only after planning audit:

```text
V5-7A complete: production controlled executor design gate ready for review.
```

This does not prove production controlled executor ready, Agent executor ready, autonomous workflow editing ready, or production-ready external app support.

V5-7B allowed future claim, only after implementation, real data validation, and high-risk proceed approval:

```text
V5-7B complete: limited production controlled executor runtime slice ready for review.
```

This still does not prove unrestricted Agent executor, autonomous workflow editing, full multi-Agent orchestration, complete Workflow Studio, or production-ready external app support.

### V5-5 Production External App Onboarding

目标：实现外部应用生产接入边界。

验收：app registration、domain verification、origin allowlist、quota、offboarding。

当前 V5-5 planning package：

```text
docs/design/V5.x/v5_5_external_app_onboarding_prd.md
docs/design/V5.x/v5_5_target_architecture_delta.md
docs/design/V5.x/v5_5_app_registration_domain_origin_model.md
docs/design/V5.x/v5_5_quota_rate_limit_offboarding_model.md
docs/design/V5.x/v5_5_api_sdk_compatibility_model.md
docs/design/V5.x/v5_5_test_matrix.md
docs/design/V5.x/v5_5_no_false_green_guard.md
docs/design/V5.x/v5_5_planning_audit_for_chatgpt.md
docs/design/V5.x/v5_5_external_app_onboarding_completion_note.md
```

V5-5 allowed completion claim:

```text
V5-5 complete: external app onboarding boundary core slice ready for review.
```

This does not prove production-ready external app support, enterprise auth ready, production tenant isolation, production credential lifecycle, Agent executor ready, controlled executor ready, complete Workflow Studio ready, or distributed multi-Agent runtime ready.

### V5-6 Web Studio Productization

目标：Thin Web Console productization first。Full Web Studio requires separate PRD and acceptance。

验收：人工确认、Evidence review、Report review、admin ops 不混淆。

边界：

```text
Evidence Review remains read-only.
Report Review remains read-only.
Admin ops cannot become runtime truth.
Do not return to Full Web Low-Code Studio first route.
```

当前 V5-6 planning / implementation package：

```text
docs/design/V5.x/v5_6_web_studio_productization_prd.md
docs/design/V5.x/v5_6_target_architecture_delta.md
docs/design/V5.x/v5_6_thin_web_console_productization_plan.md
docs/design/V5.x/v5_6_full_studio_separate_prd_gate.md
docs/design/V5.x/v5_6_ui_acceptance_matrix.md
docs/design/V5.x/v5_6_no_false_green_guard.md
docs/design/V5.x/v5_6_planning_audit_for_chatgpt.md
docs/design/V5.x/v5_6_thin_web_console_productization_completion_note.md
docs/design/V5.x/evidence/v5-6-thin-web-console/result-summary.md
```

### V5-7A / V5-7B Production Controlled Executor

目标：在 V5-6 Thin Web Console 之后，把 production controlled executor 作为单独高风险阶段承载。

V5-7A 是 design gate only：

```text
production execution policy
tenant isolation
credential boundary
approval gate
runtime sandbox
timeout / kill switch
rollback / recovery
idempotency
audit retention / export
incident response
limited action allowlist
```

V5-7B 是 runtime slice 候选，但默认 blocked：

```text
blocked until V5-7A passes
blocked until high-risk human proceed decision
limited action set only
source=agent cannot directly execute durable mutation
high-risk action approval-gated
production credential access must use credential boundary refs only
```

当前 V5-7A / V5-7B planning package：

```text
docs/design/V5.x/v5_7a_production_controlled_executor_design_gate_plan.md
docs/design/V5.x/v5_7a_planning_audit_for_chatgpt.md
docs/design/V5.x/v5_7a_policy_matrix.md
docs/design/V5.x/v5_7a_runtime_action_allowlist.json
docs/design/V5.x/v5_7a_execution_envelope.schema.json
docs/design/V5.x/v5_7a_sandbox_input_descriptor.schema.json
docs/design/V5.x/v5_7a_rollback_descriptor.schema.json
docs/design/V5.x/v5_7a_kill_switch_decision.schema.json
docs/design/V5.x/v5_7a_execution_evidence.schema.json
docs/design/V5.x/v5_7a_production_controlled_executor_design_gate_completion_note.md
docs/design/V5.x/evidence/v5-7a-production-controlled-executor-design-gate/result-summary.md
docs/design/V5.x/v5_7b_production_controlled_executor_runtime_plan.md
docs/design/V5.x/v5_7b_planning_audit_for_chatgpt.md
```

### V5-8 Distributed Multi-Agent Runtime

目标：实现生产级 serial / parallel / long-running multi-agent runtime。

验收：分布式状态恢复、attempt history、artifact lineage、tenant isolation、observability。

No False Green：V4 UX-08 / UX-09 / UX-10 are dev/local provider-backed evidence only。V5-8 必须证明 production distributed state recovery、tenant isolation、observability、artifact lineage at scale、failure recovery、attempt history、policy and credential boundary。

当前 V5-8A planning gate evidence：

```text
docs/design/V5.x/evidence/v5-8a-planning-gate/index.html
docs/design/V5.x/evidence/v5-8a-planning-gate/planning-gate-summary.md
docs/design/V5.x/evidence/v5-8a-planning-gate/real-data-readiness.json
docs/design/V5.x/evidence/v5-8a-planning-gate/prd-spec-review.md
docs/design/V5.x/evidence/v5-8a-planning-gate/architecture-risk-review.md
docs/design/V5.x/evidence/v5-8a-planning-gate/v5-8b-entry-decision.json
```

V5-8A allowed claim:

```text
V5-8A complete: distributed multi-Agent runtime planning gate ready for review.
```

V5-8A does not prove distributed multi-Agent runtime ready, full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.

当前 V5-8 planning package：

```text
docs/design/V5.x/v5_8_distributed_multi_agent_runtime_prd.md
docs/design/V5.x/v5_8_target_architecture_delta.md
docs/design/V5.x/v5_8_distributed_state_recovery_model.md
docs/design/V5.x/v5_8_attempt_history_lineage_model.md
docs/design/V5.x/v5_8_tenant_policy_credential_boundary.md
docs/design/V5.x/v5_8_test_matrix.md
docs/design/V5.x/v5_8_no_false_green_guard.md
docs/design/V5.x/v5_8_planning_audit_for_chatgpt.md
```

V5-8B next slice:

```text
DistributedRunCoordinator
AgentWorkerRegistry
worker assignment
run state transitions
coordinator restart recovery
tenant scope check before worker assignment
no source=agent durable mutation
no unrestricted connector.call
no unrestricted external_llm.call
```

当前 V5-8B evidence package：

```text
docs/design/V5.x/evidence/v5-8b-distributed-coordination/index.html
docs/design/V5.x/evidence/v5-8b-distributed-coordination/coordination-evidence.json
docs/design/V5.x/evidence/v5-8b-distributed-coordination/result-summary.md
```

V5-8B allowed claim:

```text
V5-8B complete: minimal distributed run coordination slice ready for review.
```

V5-8B does not prove distributed multi-Agent runtime ready, full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.

V5-8C next slice:

```text
AttemptHistoryStore hardening
ArtifactLineageService hardening
producer attempt tracking
lineage recovery after retry
Runtime Report attempt lineage projection
```

当前 V5-8C evidence package：

```text
docs/design/V5.x/evidence/v5-8c-lineage-recovery/index.html
docs/design/V5.x/evidence/v5-8c-lineage-recovery/lineage-recovery-evidence.json
docs/design/V5.x/evidence/v5-8c-lineage-recovery/runtime-report-projection.json
docs/design/V5.x/evidence/v5-8c-lineage-recovery/result-summary.md
```

V5-8C allowed claim:

```text
V5-8C complete: artifact lineage and attempt recovery slice ready for review.
```

V5-8C does not prove distributed multi-Agent runtime ready, full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.

V5-8D next slice:

```text
TenantRuntimeIsolationGuard for distributed actions
ProviderCredentialBoundary for worker/provider calls
distributed audit event recording
incident timeline projection
audit export package projection
redaction across worker logs / reports / evidence
```

当前 V5-8D evidence package：

```text
docs/design/V5.x/evidence/v5-8d-policy-observability/index.html
docs/design/V5.x/evidence/v5-8d-policy-observability/policy-observability-evidence.json
docs/design/V5.x/evidence/v5-8d-policy-observability/audit-export-projection.json
docs/design/V5.x/evidence/v5-8d-policy-observability/result-summary.md
```

V5-8D allowed claim:

```text
V5-8D complete: policy, credential, and observability slice ready for review.
```

V5-8D does not prove distributed multi-Agent runtime ready, full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.

V5-8E next package:

```text
end-to-end serial multi-agent scenario evidence
end-to-end parallel multi-agent scenario evidence
failure/recovery scenario evidence
audit export scenario evidence
No False Green scan
final V5-8 acceptance summary
```

当前 V5-8E evidence package：

```text
docs/design/V5.x/evidence/v5-8e-final-acceptance/index.html
docs/design/V5.x/evidence/v5-8e-final-acceptance/final-acceptance-data.json
docs/design/V5.x/evidence/v5-8e-final-acceptance/result-summary.md
docs/design/V5.x/evidence/v5-8e-final-acceptance/claims-scan.md
```

V5-8 allowed claim:

```text
V5-8 complete: distributed multi-Agent runtime slice ready for review.
```

V5-8 still does not prove full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, complete Workflow Studio ready, or autonomous workflow editing ready.

## 2.1 Remaining Planning Audit Package

V5-3 到 V5-8 的总审计入口：

```text
docs/design/V5.x/v5_3_to_v5_7_remaining_planning_audit_for_chatgpt.md
```

## 2.2 Planning Audit Entrypoint Rule

```text
Planning audit entrypoint does not equal implementation approval.
Each stage must review its detailed PRD, architecture delta, model documents, test matrix, and No False Green guard before implementation.
If detailed review finds HIGH spec drift or HIGH false-green risk, implementation must stop and return to planning.
```

## 2.3 Go / No-Go

Go:

```text
V5 planning audit cleanup
baseline freeze
detailed docs collection
stage-by-stage implementation readiness audit
```

No-Go:

```text
direct V5-6 implementation before V5-6 readiness audit closes
any V5-4C expansion beyond the reviewed BFF-only dev/local bridge
direct V5-7B implementation before V5-7A and human high-risk proceed decision
```

## 2.4 Per-Stage Implementation Readiness Checklist

### V5-3 Readiness

Must review:

```text
docs/design/V5.x/v5_3_observability_event_model.md
docs/design/V5.x/v5_3_audit_retention_export_model.md
docs/design/V5.x/v5_3_metrics_alerting_model.md
docs/design/V5.x/v5_3_incident_timeline_model.md
docs/design/V5.x/v5_3_api_bff_route_design.md
docs/design/V5.x/v5_3_test_matrix.md
docs/design/V5.x/v5_3_no_false_green_guard.md
```

Must prove design coverage:

```text
AuditExportPackage schema
AuditRetentionPolicy
SecurityEventLog
correlation_id / request_id / actor_id coverage
redaction
source=agent export denial
metrics and alerting are read-only observability outputs
incident timeline is a read model
```

### V5-4A Readiness

Must review:

```text
docs/design/V5.x/v5_4a_policy_capability_matrix.md
docs/design/V5.x/v5_4a_approval_sandbox_kill_switch_model.md
docs/design/V5.x/v5_4a_test_matrix.md
docs/design/V5.x/v5_4a_no_false_green_guard.md
```

Constraints:

```text
safety-gate only
no Agent executor route
no source=agent durable mutation
No False Green: no Agent executor ready claim
No False Green: no autonomous workflow editing ready claim
allowed claim only: V5-4A complete: Agent executor safety gate design ready for review.
```

### V5-4B Readiness

Must review:

```text
docs/design/V5.x/v5_4b_trial_runtime_boundary.md
docs/design/V5.x/v5_4b_test_matrix.md
docs/design/V5.x/v5_4b_no_false_green_guard.md
```

Constraints:

```text
V5-4B is synthetic-only
synthetic_only=true
runtime_backed=false
No False Green: no production controlled executor ready claim
source=agent still cannot directly mutate runtime
high-risk action must be approval-gated
```

### V5-4C Readiness

Must review:

```text
docs/design/V5.x/v5_4c_existing_v4_runtime_trial_plan.md
docs/design/V5.x/v5_4c_pre_implementation_audit.md
```

Constraints:

```text
exact V4 local runtime entrypoint reviewed: bff:/bff/v4_2/runtime
source=agent still cannot directly mutate runtime
user_confirmed=true required before runtime call
kill switch must block before runtime call
No False Green: no controlled executor ready claim
```

### V5-7A Readiness

Must review:

```text
docs/design/V5.x/v5_7a_production_controlled_executor_design_gate_plan.md
docs/design/V5.x/v5_7a_planning_audit_for_chatgpt.md
docs/design/V5.x/v5_7a_policy_matrix.md
docs/design/V5.x/v5_7a_runtime_action_allowlist.json
docs/design/V5.x/v5_7a_execution_envelope.schema.json
docs/design/V5.x/v5_7a_sandbox_input_descriptor.schema.json
docs/design/V5.x/v5_7a_rollback_descriptor.schema.json
docs/design/V5.x/v5_7a_kill_switch_decision.schema.json
docs/design/V5.x/v5_7a_execution_evidence.schema.json
```

Constraints:

```text
design-gate only
no production executor route
no production runtime worker
must define limited action allowlist
must require tenant isolation
must require credential boundary
must require audit retention/export
must require rollback and kill switch
must require incident response
No False Green: no production controlled executor ready claim
```

### V5-7B Readiness

Must review:

```text
docs/design/V5.x/v5_7b_production_controlled_executor_runtime_plan.md
docs/design/V5.x/v5_7b_planning_audit_for_chatgpt.md
```

Constraints:

```text
blocked until V5-7A passes
blocked until high-risk human proceed decision
limited action set only
source=agent cannot directly execute durable mutation
high-risk action approval-gated
production credential access must use credential boundary refs only
No False Green: no unrestricted controlled-execution claim
```

### V5-5 Readiness

Must review:

```text
docs/design/V5.x/v5_5_app_registration_domain_origin_model.md
docs/design/V5.x/v5_5_quota_rate_limit_offboarding_model.md
docs/design/V5.x/v5_5_api_sdk_compatibility_model.md
docs/design/V5.x/v5_5_test_matrix.md
docs/design/V5.x/v5_5_no_false_green_guard.md
```

Constraints:

```text
tenant-bound app registration
domain verification before origin allowlist
quota / rate limit denials auditable
offboarding revokes app access and credentials
SDK compatibility avoids direct browser /v1/rpc
No False Green: no production-ready external app support claim until full acceptance
```

### V5-6 Readiness

Must review:

```text
docs/design/V5.x/v5_6_thin_web_console_productization_plan.md
docs/design/V5.x/v5_6_full_studio_separate_prd_gate.md
docs/design/V5.x/v5_6_ui_acceptance_matrix.md
docs/design/V5.x/v5_6_no_false_green_guard.md
```

Constraints:

```text
Thin Web Console productization first
Full Studio requires separate PRD / architecture / acceptance matrix / No False Green gate
Evidence Review remains read-only
Report Review remains read-only
Admin ops cannot become runtime truth
Do not return to Full Web Low-Code Studio first route
```

### V5-8 Readiness

V5-8E final acceptance package is ready for review. Any next V5 stage must be defined by a separate planning audit. V5-8 cannot use V4 UX-08/09/10 dev/local evidence as full multi-Agent orchestration proof.

Must prove before V5-8 completion:

```text
production distributed state recovery
tenant isolation
observability
artifact lineage at scale
failure recovery
attempt history
policy and credential boundary
```

## 3. V5-0 Acceptance

V5-0 通过条件：

```text
V5 index exists
V5 target PRD exists
V5 target architecture exists
V5 gap markdown / drawio exist and XML valid
V5 development and acceptance plan exists
V5 claim guard exists
V4 closure boundary remains unchanged
No forbidden claim outside No False Green context
every production blocker has owner stage
V5-1 implementation not started
```

## 4. Regression Commands

V5-0 must run:

```bash
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
xmllint --noout docs/design/V5.x/v5_current_gap_analysis.drawio
```

## 5. Stop Conditions

Stop V5 implementation planning if:

```text
V5 document retroactively upgrades V4 to production-ready
forbidden claim appears outside No False Green context
V5-0 proposes direct Agent executor implementation without safety gate
V5-0 proposes production auth as already complete
Agent executor is claimed ready
production auth is claimed ready
external app support is claimed production-ready
complete Studio is claimed ready
distributed multi-Agent runtime is claimed ready
V5 gap loses production blocker classification
V5-0 proposes direct implementation before planning audit
V4 closure evidence is edited to hide evidence_scope
```
