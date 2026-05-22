# V4.0 Completion Audit Report

审计日期：2026-05-22  
审计对象：harnessOS V3.5 / V3.6 / V4.0 当前完成情况  
审计结论：当前可以声明 `V4.0-P complete: AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation.`。下一阶段只能进入 V4.0-Q Controlled Executor Design Gate，优先审计 policy、approval、capability、sandbox、rollback、kill switch 和 audit，而不是进入 Agent executor、controlled executor 实现或完整低代码编辑器。

## 1. 审计结论

当前项目的 V3.5、V3.6、V4.0 阶段声明与测试证据基本一致。

可以接受的完成声明：

```text
V3.5 complete at dev/local Application Adaptation Layer level.
V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development.
V4.0-P complete: AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation.
```

不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
full browser E2E ready
autonomous workflow editing ready
controlled executor ready
Agent executor ready
full low-code canvas editing ready
direct canvas-to-runtime mutation ready
```

关键原因：

- V4.0-E 已完成 component-level + BFF integration E2E。
- V4.0-F 已完成 Playwright browser smoke baseline。
- V4.0-G 已完成 governed patch apply/reject/publish editing hardening。
- V4.0-H 已完成 canvas / Inspector intent 到 governed WorkflowPatch proposal 的桥接。
- V4.0-I 已完成 BFF/UI 层 AgentTalk stateful assistant baseline，且 Agent 不能自动 apply/reject/publish/approval.respond/context.update/business.event.emit。
- V4.0-J 已完成 Agent action proposal governance，且没有新增 executor/run/apply/publish Agent route。
- V4.0-K 已完成 AgentActionHandoff 到 Editing / Approval / Context operation panels 的安全交接；handoff route 只创建 / 读取 DTO，最终执行仍复用用户显式确认的 operation panel 路径。
- V4.0-L 已完成 AgentActionHandoff lifecycle / audit / recovery hardening；handoff 使用 repository/store interface，支持 active/opened/used/dismissed/expired/stale/blocked 状态、lazy expiration、URL recovery、append-only audit 和 stale/blocked UI guard。
- V4.0-M 已完成 user-confirmed operation evidence / governance review baseline；patch apply/reject、publish、approval.respond、context.update 和 business.event.emit 的用户确认操作会生成 redacted evidence，Workflow Console 新增只读治理审计面板。
- V4.0-N 已完成 canvas editing readiness baseline；controlled catalog、CanvasDraftProjection、node/edge/Inspector proposal flow、edge validation、Inspector allowlist 和 layout boundary 均已覆盖。
- V4.0-O 已完成 governed canvas proposal workflow baseline；PatchQueueDTO、projection freshness、catalog versioning、Inspector mapping V2、edge validation V2、fixture isolation、redaction/event truth regression 和 claim guard 均已覆盖。
- V4.0-P 已完成 AgentTalkWindow interaction E2E baseline；AgentTalkInteractionState、explain/summarize read-only、suggest patch -> handoff -> panel、evidence review read-only、event refresh truth、multi-proposal stale guard、redaction 和 browser smoke 均已覆盖。
- 当前前端是 Workflow Console / Workflow Studio shell + governed editing hardening + patch proposal bridge，不是完整低代码编辑器。
- 完整 AgentTalkWindow、自主 Agent executor、生产级 auth/multi-tenant control plane 仍未完成。

## 2. 审计过的核心文档

V4.0 当前阶段主文档：

```text
docs/design/V4.0/00_README.md
docs/design/V4.0/v4_0_current_gap_analysis.md
docs/design/V4.0/v4_0_current_gap_analysis.drawio
docs/design/V4.0/v4_0_e_reference_console_completion_note.md
docs/design/V4.0/v4_0_f_browser_smoke_plan.md
docs/design/V4.0/v4_0_f_browser_smoke_completion_note.md
docs/design/V4.0/v4_0_g_editing_hardening_plan.md
docs/design/V4.0/v4_0_g_editing_hardening_completion_note.md
docs/design/V4.0/v4_0_h_canvas_runtime_bridge_plan.md
docs/design/V4.0/v4_0_h_canvas_runtime_bridge_completion_note.md
docs/design/V4.0/v4_0_i_agent_talk_window_stateful_plan.md
docs/design/V4.0/v4_0_i_agent_talk_window_completion_note.md
docs/design/V4.0/v4_0_j_agent_talk_governance_plan.md
docs/design/V4.0/v4_0_j_agent_talk_governance_completion_note.md
docs/design/V4.0/v4_0_k_agent_action_handoff_plan.md
docs/design/V4.0/v4_0_k_agent_action_handoff_completion_note.md
docs/design/V4.0/v4_0_l_agent_handoff_lifecycle_plan.md
docs/design/V4.0/v4_0_l_agent_handoff_lifecycle_completion_note.md
docs/design/V4.0/v4_0_m_operation_evidence_plan.md
docs/design/V4.0/v4_0_m_operation_evidence_completion_note.md
docs/design/V4.0/v4_0_n_canvas_editing_readiness_plan.md
docs/design/V4.0/v4_0_n_canvas_editing_readiness_completion_note.md
docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_plan.md
docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_completion_note.md
docs/design/V4.0/v4_0_p_agenttalk_window_interaction_e2e_plan.md
```

V4.0 UI / 协议映射文档：

```text
docs/design/V4.0/v4_0_ui_contract_map.md
docs/design/V4.0/v4_0_event_contract_map.md
docs/design/V4.0/v4_0_mock_to_real_contract_checklist.md
docs/design/V4.0/v4_0_frontend_stack_decision.md
docs/design/V4.0/v4_0_stitch_prototype_mapping.md
docs/design/V4.0/v4_0_workflow_studio_low_code_baseline.md
docs/design/V4.0/v4_0_workflow_studio_agent_copilot_prd.md
docs/design/V4.0/v4_target_architecture_workflow_console.md
```

V3.6 后端事实源文档：

```text
docs/design/V3.6/00_README.md
docs/design/V3.6/v3_6_current_gap_analysis.md
docs/design/V3.6/v3_6_current_gap_analysis.drawio
docs/design/V3.6/v3_6_acceptance_plan.md
docs/design/V3.6/v3_6_workflow_contract.md
docs/design/V3.6/v3_6_j_completion_note.md
docs/design/V3.6/v3_6_preflight_hardening_note.md
docs/integration/workflow_runtime_contract.md
```

V3.5 接入层文档：

```text
docs/design/V3.5/00_README.md
docs/design/V3.5/v3_5_current_gap_analysis.md
docs/design/V3.5/v3_5_completion_evidence_bundle.md
docs/design/V3.5/v3_5_acceptance_plan.md
docs/design/V3.5/v3_5_event_bridge_plan.md
docs/design/V3.5/v3_5_sdk_plan.md
docs/design/V3.5/v3_5_bff_template_plan.md
docs/design/V3.5/v3_5_embed_contract_plan.md
docs/integration/sdk_contract.md
docs/integration/bff_minimal_smoke.md
```

## 3. 审计过的测试证据

最新审计实际执行结果：

```text
./.venv/bin/python -m pytest tests/test_v4_0_canvas_patch_queue_bff.py tests/test_v4_0_canvas_projection_freshness.py tests/test_v4_0_canvas_edge_contracts.py tests/test_v4_0_inspector_mapping_v2.py tests/test_v4_0_node_catalog_versioning.py tests/test_v4_0_canvas_proposal_scope_redaction.py tests/test_v4_0_claim_guard.py -q
18 passed

cd apps/workflow-console && npm test
48 passed

cd apps/workflow-console && npm run build
passed

cd apps/workflow-console && npm run test:e2e
12 passed

./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
134 passed

./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed

./.venv/bin/python -m pytest -q
575 passed, 3 skipped, 6 warnings
```

重点测试文件：

```text
tests/test_v4_0_reference_workflow_console_e2e.py
tests/test_v4_0_reference_console_scope_isolation.py
tests/test_v4_0_reference_console_eventbridge_e2e.py
tests/test_v4_0_reference_console_operation_panels_e2e.py
tests/test_v4_0_reference_console_redaction.py
tests/test_v4_0_editing_hardening_bff_routes.py
tests/test_v4_0_canvas_runtime_bridge_bff.py
tests/test_v4_0_canvas_runtime_bridge_contract.py
tests/test_v4_0_canvas_runtime_bridge_redaction.py
tests/test_v4_0_canvas_editing_readiness_bff.py
tests/test_v4_0_canvas_editing_readiness_contract.py
tests/test_v4_0_canvas_editing_readiness_scope.py
tests/test_v4_0_canvas_editing_readiness_redaction.py
tests/test_v4_0_canvas_patch_queue_bff.py
tests/test_v4_0_canvas_projection_freshness.py
tests/test_v4_0_canvas_edge_contracts.py
tests/test_v4_0_inspector_mapping_v2.py
tests/test_v4_0_node_catalog_versioning.py
tests/test_v4_0_canvas_proposal_scope_redaction.py
tests/test_v4_0_claim_guard.py
tests/test_v4_0_agent_talk_stateful_bff.py
tests/test_v4_0_agent_talk_stateful_scope.py
tests/test_v4_0_agent_talk_stateful_redaction.py
tests/test_v4_0_agent_talk_patch_governance.py
tests/test_v4_0_agent_action_proposals_bff.py
tests/test_v4_0_agent_action_policy_guard.py
tests/test_v4_0_agent_action_scope.py
tests/test_v4_0_agent_action_redaction.py
tests/test_v4_0_agent_action_handoff_bff.py
tests/test_v4_0_agent_action_handoff_scope.py
tests/test_v4_0_agent_action_handoff_redaction.py
tests/test_v4_0_agent_action_handoff_user_confirmation.py
tests/test_v4_0_agent_handoff_repository.py
tests/test_v4_0_agent_handoff_lifecycle.py
tests/test_v4_0_agent_handoff_recovery.py
tests/test_v4_0_agent_handoff_audit.py
tests/test_v4_0_agent_handoff_stale_guards.py
tests/test_v4_0_operation_evidence_bff.py
tests/test_v4_0_operation_evidence_correlation.py
tests/test_v4_0_operation_evidence_scope.py
tests/test_v4_0_operation_evidence_redaction.py
tests/test_v4_0_operation_evidence_idempotency.py
tests/test_v4_0_governance_review_panel.py
tests/test_v4_0_frontend_no_direct_core_calls.py
tests/test_v4_0_contract_doc_alignment.py
apps/workflow-console/e2e/workflow-console-smoke.spec.ts
apps/workflow-console/e2e/workflow-editing-smoke.spec.ts
apps/workflow-console/e2e/workflow-canvas-bridge-smoke.spec.ts
apps/workflow-console/e2e/workflow-canvas-editing-readiness-smoke.spec.ts
apps/workflow-console/e2e/workflow-canvas-patch-queue-smoke.spec.ts
apps/workflow-console/e2e/workflow-inspector-mapping-smoke.spec.ts
apps/workflow-console/e2e/workflow-catalog-versioning-smoke.spec.ts
apps/workflow-console/e2e/workflow-agent-talk-smoke.spec.ts
apps/workflow-console/e2e/workflow-agent-governance-smoke.spec.ts
apps/workflow-console/e2e/workflow-agent-handoff-smoke.spec.ts
apps/workflow-console/e2e/workflow-agent-handoff-recovery-smoke.spec.ts
apps/workflow-console/e2e/workflow-operation-evidence-smoke.spec.ts
tests/test_v3_6_dummy_pipeline_e2e.py
tests/test_v3_6_preflight_scope_hardening.py
tests/test_v3_6_preflight_patch_governance.py
tests/test_v3_6_preflight_approval_legacy.py
tests/test_v3_5_mvp_e2e.py
tests/test_v3_5_reference_app.py
```

## 4. 架构审计结果

### 4.1 七平面边界

当前文档与实现仍以七平面为正式基线：

```text
Plane-0 Product UI / Workflow Studio / AgentTalkWindow
Plane-1 Application Adaptation Layer
Plane-2 Workflow Runtime Layer
Plane-3 Harness Core
Plane-4 Runtime Adapter & Governance
Plane-5 Domain Pack / Descriptor Plane
Plane-6 Connector / Tool / Store / Asset Plane
```

审计结果：

- V4.0 UI 当前通过 BFF structured routes 消费 V3.6 runtime DTO。
- 前端 source scan 覆盖 no direct `/v1/rpc`、no direct `/v1/events/subscribe`、no direct Core/Gateway/Store import。
- V4.0-E 使用 BFF/Gateway/V3.6 runtime fixture，而不是 frontend-only demoData。

### 4.2 UI / BFF / Runtime 边界

审计结果：

- 前端默认不直接调用 `/v1/rpc` 或 `/v1/events/subscribe`。
- BFF 返回 redacted frontend DTO，不直接透传 raw Gateway response。
- EventBridge 只触发 refresh/display，UI 不从 event payload 构造 runtime truth。
- Patch Diff 可展示，但 UI 不调用 patch apply/reject/publish。
- Agent shell 不自动调用 `approval.respond`。
- Quality panel 不调用 `quality.evaluation.create/attach`。

### 4.3 Scope / Capability / Ownership

审计结果：

- V4.0-E 覆盖 cross-scope 和 same-scope wrong-instance denial。
- 覆盖资源包括 approval、artifact、quality、context、business event、patch。
- BFF route ownership guard 与 V3.6 preflight scope hardening 均有测试证据。

## 4.4 V4.0 hardening follow-up

本次收口已修复代码检视发现的关键缺口：

- BFF `business-events` route 在请求携带 `binding` 时额外要求 `workflow_context.write`。
- BFF 拒绝 `meeting.*` / `knowledge.*` / `video.*` 作为 business event 类型。
- BFF 新增 `workflow.patch.propose` / template-scoped patch diff structured routes，并返回 redacted DTO。
- BFF instance-scoped patch diff 不再只按 template 校验，而是要求 patch metadata 绑定同一个 `workflow_instance_id`。
- Workflow Console 前端 EventSource 使用 BFF `follow=true`，避免只 replay 不 follow。
- Workflow Console station outputs 优先使用 instance-scoped BFF route。
- Workflow Console Approval / Context 操作面板已从 `App` 通过 `ConsoleShell` 接入真实 operation handlers。
- Workflow Console runtime refresh 会重新拉取 status、board、approval、quality、context 和 station outputs，不再只保留旧实例数据。
- 直接 `/v1/events/subscribe` SSE 输出增加 redaction，避免泄露 token/raw payload 字段。

## 5. 风险细化评估

当前主要风险集中在 V4.0-O 后的 AgentTalkWindow interaction E2E，而不是 V3.6 runtime 基础能力。风险优先级如下：

| 风险 | 等级 | 完成度影响 | 建议动作 |
| --- | --- | --- | --- |
| Agent interaction 被误写为 executor | critical | 会把 P 阶段 interaction E2E 误升级为 Agent executor。 | Agent 仍只能 propose / handoff / explain / navigate，禁止 source=agent 执行 mutation。 |
| Event payload 被当作 Agent truth | high | fake event 可能污染 session、proposal、handoff、evidence 或 board/status/context。 | EventBridge 只触发 refresh，UI 必须重新拉 BFF DTO。 |
| Handoff / evidence 跨 scope 混用 | high | 可能把错误 proposal/handoff/evidence 显示给用户。 | 强校验 proposal_id、handoff_id、resource_refs 和 workflow_instance_id。 |
| Agent DOM / DTO redaction 回归 | high | Agent 建议可能泄露 raw prompt、token、Authorization 或 raw payload。 | 扩展 DTO/DOM/error/event redaction regression。 |
| 多 proposal / handoff stale state | high | UI 可能展示旧 diff 或旧 evidence。 | selected state guard、refresh 后 stale warning。 |
| Browser E2E fixture 污染 | medium/high | P 阶段 smoke 可能出现 false green。 | 每个 spec 独立 seed workflow_instance_id、agent_session_id、proposal_id、handoff_id。 |
| 文档过度声明 | medium/high | 容易把 interaction baseline 写成 complete AgentTalkWindow 或 executor ready。 | 扩展 claim guard 并同步 README/gap/audit/drawio。 |

完整风险登记表见 `docs/design/V4.0/v4_0_p_agenttalk_window_interaction_e2e_plan.md`。

## 6. 功能完成度判断

已完成：

- V3.5 dev/local Application Adaptation Layer。
- V3.6 Workflow Runtime Contract & Pipeline Operating Model。
- V3.6/V4.0 preflight hardening。
- V4.0 Workflow Console / Workflow Studio shell。
- V4.0 Real Data Bridge。
- V4.0 Quality / Approval / Context operation panels。
- V4.0 Reference Workflow Console component-level + BFF integration E2E。
- V4.0-F/G/H Playwright browser smoke：read/event、editing、canvas bridge paths。
- V4.0-I governed stateful Agent assistant baseline：session/message/suggestion/action intent、source=agent propose-only、Agent browser smoke。
- V4.0-J AgentTalk governance：action proposal queue、policy guard、proposal lifecycle、redacted audit 和 governance browser smoke。
- V4.0-K Agent action handoff：AgentActionProposal 安全交接到 Editing / Approval / Context operation panels；handoff 本身不执行 mutation，最终执行仍需要用户显式确认。
- V4.0-L Agent handoff lifecycle：handoff lifecycle、audit、URL recovery、stale/expired/blocked guard 和 UI disable 逻辑已补齐；仍不是 executor。
- V4.0-M Operation evidence：用户确认操作会形成 evidence chain，治理审计面板只读展示 evidence / handoff / runtime result refs；仍不是 executor。
- V4.0-N Canvas editing readiness：controlled catalog、CanvasDraftProjection、node/edge/Inspector proposal flow、edge validation、Inspector allowlist 和 layout boundary 已完成；仍不是完整低代码编辑器。
- V4.0-O Governed canvas proposal workflow：PatchQueueDTO、projection freshness、catalog versioning、Inspector mapping V2、edge validation V2、fixture isolation、redaction/event truth regression 和 claim guard 已完成；仍不是完整 Workflow Studio。
- V4.0-P AgentTalkWindow interaction E2E：AgentTalkInteractionState、explain/summarize read-only、suggest patch handoff、evidence review、event truth、redaction 和 browser smoke 已完成；仍不是 complete AgentTalkWindow 或 Agent executor。

未完成：

- full browser E2E。
- 完整 Workflow Studio 低代码编辑器。
- 真实节点拖入后直接创建 Station 不是 V4.0-H 目标；当前只生成 patch proposal。
- 连线直接写回 WorkflowEdge 不是 V4.0-H 目标；当前只生成 patch proposal。
- Inspector 已通过 WorkflowPatch proposal 桥接，但仍未完成完整可视化编辑器。
- 完整 AgentTalkWindow 状态机、真实 Agent executor 和 controlled executor。
- production-ready external app support。

## 7. 审计建议

当前可以进入后续 V4.0 开发，下一阶段应在 V4.0-P AgentTalkWindow interaction E2E baseline 之上执行 V4.0-Q Controlled Executor Design Gate，而不是直接声明完整 Workflow Studio、完整 AgentTalkWindow 或 controlled executor：

1. V4.0-Q Controlled Executor Design Gate：只做受控执行器设计门禁，覆盖 policy、approval、capability、sandbox、rollback、kill switch 和 audit。
2. V4.0-R Production Readiness Preflight：单独审计 auth/SSO/multi-tenant/observability/security/secret management，不提前声明 production-ready。

当前阶段声明：

```text
V4.0-P complete: AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation.
```

仍不能升级为：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full browser E2E ready
autonomous workflow editing ready
controlled executor ready
Agent executor ready
```

仍不能声明 complete Workflow Studio ready、complete AgentTalkWindow ready 或 production-ready external app support。
