# V5.x Design Index

文档状态：V5 baseline frozen for planning audit。本文是 V5.x canonical index。

## Current V5 Baseline

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

V5.x 从 V4-U9 closure 之后开始。V4 已关闭功能开发，V5 不能反向升级 V4 的 dev/local 证据。V5-7B 当前只证明 isolated staging runtime semantics，不新增生产执行路由、不新增生产 worker、不允许 source=agent durable mutation。V5-8 证明 bounded distributed runtime slice ready for review，但不能声明完整 distributed multi-Agent runtime ready、full multi-Agent orchestration ready、Agent executor ready 或 production controlled executor ready。

## V4 Handoff Baseline

```text
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
V4 feature development closed.
V5 planning may proceed.
```

V5 可以继承：

```text
V4 dev/local Headless workflow core evidence
Mission Console / Workflow Blueprint / Runtime Report / Review Console / Evidence Chain baseline
UX-01 to UX-12 evidence inventory
Runtime Capability Matrix
WorkflowSpec Registry
V4 false-green audit result
V4 redaction result
```

## V5 No False Green

V5 不得把以下能力视为 V4 已完成：

```text
production auth
production tenant isolation
production token lifecycle
production credential lifecycle
production observability / audit export
production external app onboarding
Agent executor ready
production controlled executor ready
complete Workflow Studio
distributed multi-Agent runtime
production-ready external app support
```

V5-0 允许声明：

```text
V5-0 complete: production productization planning gate ready for review.
```

V5-0 仍禁止声明：

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

## Current Documents

| File | Purpose |
| --- | --- |
| `v5_0_production_productization_planning_brief.md` | V5-0 前置 planning brief，不实现 V5。 |
| `v5_target_prd.md` | V5 目标 PRD，描述 production productization 的用户价值、非目标和阶段边界。 |
| `v5_target_architecture.md` | V5 目标架构，描述 production auth、tenant、credential、audit、executor safety 和 external app 进入方式。 |
| `v5_current_gap_analysis.md` | V5 当前 gap 分析，区分 inherited from V4、planned、not implemented、production blocker。 |
| `v5_current_gap_analysis.drawio` | V5 gap 图形版。 |
| `v5_development_and_acceptance_plan.md` | V5 开发与验收计划。 |
| `v5_no_false_green_claim_guard.md` | V5 禁止声明、claim guard 和验收扫描规则。 |
| `v5_post_v5_6_document_audit_and_next_plan_for_chatgpt.md` | V5-6 后文档审计入口，汇总 drawio/gap/后续计划和 ChatGPT 审计问题。 |
| `v5_0_planning_audit_for_chatgpt.md` | V5-0 规划审计包，供外部复核 planning-only 边界、claim guard 和阶段风险。 |
| `v5_0_production_productization_planning_completion_note.md` | V5-0 完成说明，记录文档、验收命令和 No False Green 结果。 |
| `v5_1_production_auth_tenant_boundary_prd.md` | V5-1 Production Auth / Tenant Boundary PRD，定义实现前目标规格。 |
| `v5_1_target_architecture_delta.md` | V5-1 目标架构增量，描述 IdentityContextResolver、TenantScopeGuard 等逻辑组件。 |
| `v5_1_identity_tenant_ownership_model.md` | V5-1 identity / tenant / workspace / app ownership model。 |
| `v5_1_api_bff_route_design.md` | V5-1 API / BFF route design，不新增实际路由。 |
| `v5_1_audit_fields.md` | V5-1 audit fields，定义 tenant boundary 决策所需审计字段。 |
| `v5_1_test_matrix.md` | V5-1 test matrix，定义实现阶段必须覆盖的 scope denial 和 audit 场景。 |
| `v5_1_no_false_green_guard.md` | V5-1 No False Green guard，防止误报 enterprise auth ready / multi-tenant control plane ready。 |
| `v5_1_planning_audit_for_chatgpt.md` | V5-1 planning audit package，供外部审计是否可以进入实现。 |
| `v5_1_planning_completion_note.md` | V5-1 planning completion note，记录实现前规划结果和停止条件。 |
| `v5_1_production_auth_tenant_boundary_completion_note.md` | V5-1 完成说明，记录 core tenant boundary guard slice、测试结果和 No False Green 边界。 |
| `v5_2_credential_provider_lifecycle_prd.md` | V5-2 Credential / Provider Lifecycle PRD。 |
| `v5_2_target_architecture_delta.md` | V5-2 架构增量，描述 provider profile、credential lifecycle 和 redaction boundary。 |
| `v5_2_provider_profile_model.md` | V5-2 ProviderProfileDTO 模型规划。 |
| `v5_2_credential_lifecycle_model.md` | V5-2 CredentialReferenceDTO 与 lifecycle event 规划。 |
| `v5_2_api_bff_route_design.md` | V5-2 API / BFF route design，不新增实际路由。 |
| `v5_2_audit_fields.md` | V5-2 provider invocation 与 credential lifecycle audit fields。 |
| `v5_2_test_matrix.md` | V5-2 implementation test matrix。 |
| `v5_2_no_false_green_guard.md` | V5-2 No False Green guard。 |
| `v5_2_planning_audit_for_chatgpt.md` | V5-2 planning audit package，供外部审计是否可以进入实现。 |
| `v5_2_planning_completion_note.md` | V5-2 planning completion note，记录 planning package 和 implementation block。 |
| `v5_2_credential_provider_lifecycle_completion_note.md` | V5-2 完成说明，记录 credential/provider lifecycle core slice、真实本地 provider 配置验收和 No False Green 边界。 |
| `v5_3_to_v5_8_remaining_planning_audit_for_chatgpt.md` | V5-3 到 V5-8 剩余阶段规划总审计包，当前控制文件。 |
| `v5_3_to_v5_7_remaining_planning_audit_for_chatgpt.md` | Historical V5-3 到 V5-7 剩余阶段规划总审计包；canonical scope moved to V5-8。 |
| `v5_3_planning_audit_for_chatgpt.md` | V5-3 Observability / Audit Export 规划审计入口。 |
| `v5_3_observability_audit_export_completion_note.md` | V5-3 完成说明，记录 observability/audit export core slice、测试结果和 No False Green 边界。 |
| `v5_4a_planning_audit_for_chatgpt.md` | V5-4A Agent Executor Safety Gate 规划审计入口。 |
| `v5_4a_agent_executor_safety_gate_completion_note.md` | V5-4A 完成说明，记录 safety gate core slice、测试结果和 No False Green 边界。 |
| `v5_4b_planning_audit_for_chatgpt.md` | V5-4B Controlled Executor Dev/Local Trial 规划审计入口。 |
| `v5_4b_pre_implementation_audit.md` | V5-4B 实现前自动审计结论，记录人工选择 Option B synthetic-only trial。 |
| `v5_4b_controlled_executor_devlocal_trial_completion_note.md` | V5-4B 完成说明，记录 synthetic controlled executor trial、测试结果和 No False Green 边界。 |
| `v5_4c_existing_v4_runtime_trial_plan.md` | V5-4C 规划与验收，承载 existing V4 local runtime controlled trial。 |
| `v5_4c_pre_implementation_audit.md` | V5-4C 实现前审计，记录 runtime entrypoint 已限定为 `/bff/v4_2/runtime`。 |
| `v5_4c_existing_v4_runtime_trial_completion_note.md` | V5-4C 完成说明，记录 dev/local bridge、真实 fixture 验收和 No False Green 边界。 |
| `v5_5_planning_audit_for_chatgpt.md` | V5-5 Production External App Onboarding 规划审计入口。 |
| `v5_5_external_app_onboarding_completion_note.md` | V5-5 完成说明，记录 external app onboarding boundary core slice、测试结果和 No False Green 边界。 |
| `v5_6_planning_audit_for_chatgpt.md` | V5-6 Web Studio Productization 规划审计入口。 |
| `v5_6_thin_web_console_productization_completion_note.md` | V5-6 完成说明，记录 Thin Web Console productization slice、证据包和 No False Green 边界。 |
| `v5_7a_production_controlled_executor_design_gate_plan.md` | V5-7A production controlled executor design gate 规划，不实现生产执行器。 |
| `v5_7a_planning_audit_for_chatgpt.md` | V5-7A 规划审计入口，供外部复核高风险边界。 |
| `v5_7a_policy_matrix.md` | V5-7A policy matrix，定义候选 action 风险、确认、审批、rollback、idempotency 和 audit 要求。 |
| `v5_7a_runtime_action_allowlist.json` | V5-7A runtime action allowlist design contract，只定义不执行。 |
| `v5_7a_execution_envelope.schema.json` | V5-7A ProductionExecutionEnvelope schema。 |
| `v5_7a_sandbox_input_descriptor.schema.json` | V5-7A SandboxInputDescriptor schema。 |
| `v5_7a_rollback_descriptor.schema.json` | V5-7A RollbackDescriptor schema。 |
| `v5_7a_kill_switch_decision.schema.json` | V5-7A KillSwitchDecision schema。 |
| `v5_7a_execution_evidence.schema.json` | V5-7A ExecutionEvidenceContract schema。 |
| `v5_7a_production_controlled_executor_design_gate_completion_note.md` | V5-7A 完成说明，记录 design gate、合同证据和 No False Green 边界。 |
| `v5_7b_production_controlled_executor_runtime_plan.md` | V5-7B production controlled executor runtime 候选实现计划。 |
| `v5_7b_planning_audit_for_chatgpt.md` | V5-7B 规划审计入口，必须在 V5-7A 通过后使用。 |
| `v5_7b_pre_implementation_audit.md` | V5-7B 实现前审计，记录 entry gate、逐 action 验收矩阵、approved_api 边界和条件放行结论。 |
| `v5_7b_no_go_closure_summary.md` | V5-7B 条件闭环摘要，记录 limited staging runtime slice 与生产入口阻断项。 |
| `v5_7b_staging_fixture_design.md` | V5-7B staging fixture 设计，仅 design_only，不创建 runtime worker。 |
| `v5_7b_limited_runtime_slice_completion_note.md` | V5-7B limited staging runtime slice 完成证据，不声明 production controlled executor ready。 |
| `evidence/v5-7b-external-review/` | V5-7B 外部审计与依赖评审闭环包，允许进入 V5-8 planning entry。 |
| `v5_8_entry_gate_plan.md` | V5-8 entry gate，允许 planning / pre-implementation audit，不批准 runtime implementation。 |
| `v5_8_pre_implementation_audit.md` | V5-8 实现前审计。 |
| `v5_8_development_and_acceptance_plan.md` | V5-8 后续开发与验收计划。 |
| `v5_8_distributed_multi_agent_runtime_prd.md` | V5-8 Distributed Multi-Agent Runtime PRD，V5-7A/B 之后的生产分布式多 Agent 规划。 |
| `v5_8_target_architecture_delta.md` | V5-8 目标架构增量。 |
| `v5_8_distributed_state_recovery_model.md` | V5-8 分布式状态恢复模型。 |
| `v5_8_attempt_history_lineage_model.md` | V5-8 attempt history / lineage 模型。 |
| `v5_8_tenant_policy_credential_boundary.md` | V5-8 tenant / policy / credential boundary。 |
| `v5_8_test_matrix.md` | V5-8 test matrix。 |
| `v5_8_no_false_green_guard.md` | V5-8 No False Green guard。 |
| `v5_8_planning_audit_for_chatgpt.md` | V5-8 planning audit entrypoint。 |
| `evidence/v5-8a-planning-gate/` | V5-8A planning gate evidence package，含真实 UX-12 本地 Markdown 读取和 MiniMax provider-backed 证据复核。 |
| `v5_8a_distributed_runtime_planning_gate_completion_note.md` | V5-8A completion note，记录 planning gate 证据、真实数据输入和 No False Green 边界。 |
| `evidence/v5-8b-distributed-coordination/` | V5-8B minimal distributed coordination evidence package，使用 V4 UX-08/09/10 真实 provider-backed 证据作为输入。 |
| `v5_8b_minimal_distributed_coordination_completion_note.md` | V5-8B completion note，记录最小协调切片、测试结果和 No False Green 边界。 |
| `evidence/v5-8c-lineage-recovery/` | V5-8C lineage / attempt recovery evidence package，使用 V4 UX-10 真实 provider-backed 证据作为输入。 |
| `v5_8c_lineage_recovery_completion_note.md` | V5-8C completion note，记录血缘、attempt recovery、只读 runtime report projection 和 No False Green 边界。 |
| `evidence/v5-8d-policy-observability/` | V5-8D policy / credential / observability evidence package，使用 V4 UX-09 真实 provider-backed 证据作为输入。 |
| `v5_8d_policy_observability_completion_note.md` | V5-8D completion note，记录策略、凭证、审计投影和 No False Green 边界。 |
| `evidence/v5-8e-final-acceptance/` | V5-8E final acceptance package，汇总 V5-8A/B/C/D 和 V4 UX-08/09/10 证据。 |
| `v5_8_distributed_runtime_acceptance_completion_note.md` | V5-8 completion note，记录最终验收、测试结果和 No False Green 边界。 |
| `v5_7_planning_audit_for_chatgpt.md` | Historical V5-7 Distributed Multi-Agent Runtime 规划入口；canonical stage moved to V5-8。 |

## Recommended Next Step

```text
V5-8 final acceptance package is ready for review after validating V5-8A/B/C/D evidence, UX-08/09/10 provider-backed scenario evidence, No False Green scan, and redaction.
Next candidate: define the next V5 stage only after a separate planning audit; do not automatically expand V5-8 into full orchestration or Agent executor behavior.
Do not claim distributed multi-Agent runtime ready, full multi-Agent orchestration ready, Agent executor ready, or production controlled executor ready.
Do not allow source=agent durable mutation.
Do not expand connector.call or external_llm.call beyond the reviewed tenant / policy / credential boundaries.
```
