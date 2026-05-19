# V4.0 Completion Audit Report

审计日期：2026-05-19  
审计对象：harnessOS V3.5 / V3.6 / V4.0 当前完成情况  
审计结论：当前可以声明 `V4.0 dev/local Workflow Console integration baseline ready`。

## 1. 审计结论

当前项目的 V3.5、V3.6、V4.0 阶段声明与测试证据基本一致。

可以接受的完成声明：

```text
V3.5 complete at dev/local Application Adaptation Layer level.
V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development.
V4.0 dev/local Workflow Console integration baseline ready.
```

不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
full browser E2E ready
```

关键原因：

- V4.0-E 已完成 component-level + BFF integration E2E。
- V4.0-E 尚未引入 Playwright / Cypress browser-level smoke。
- 当前前端是 Workflow Console / Workflow Studio shell + integration baseline，不是完整低代码编辑器。
- Patch apply/reject/publish、完整 AgentTalkWindow 状态机、生产级 auth/multi-tenant control plane 仍未完成。

## 2. 审计过的核心文档

V4.0 当前阶段主文档：

```text
docs/design/V4.0/00_README.md
docs/design/V4.0/v4_0_current_gap_analysis.md
docs/design/V4.0/v4_0_current_gap_analysis.drawio
docs/design/V4.0/v4_0_e_reference_console_completion_note.md
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

本次审计实际执行结果：

```text
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
50 passed

cd apps/workflow-console && npm test
18 passed

cd apps/workflow-console && npm run build
passed

./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed

./.venv/bin/python -m pytest -q
491 passed, 3 skipped
```

重点测试文件：

```text
tests/test_v4_0_reference_workflow_console_e2e.py
tests/test_v4_0_reference_console_scope_isolation.py
tests/test_v4_0_reference_console_eventbridge_e2e.py
tests/test_v4_0_reference_console_operation_panels_e2e.py
tests/test_v4_0_reference_console_redaction.py
tests/test_v4_0_frontend_no_direct_core_calls.py
tests/test_v4_0_contract_doc_alignment.py
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

## 5. 功能完成度判断

已完成：

- V3.5 dev/local Application Adaptation Layer。
- V3.6 Workflow Runtime Contract & Pipeline Operating Model。
- V3.6/V4.0 preflight hardening。
- V4.0 Workflow Console / Workflow Studio shell。
- V4.0 Real Data Bridge。
- V4.0 Quality / Approval / Context operation panels。
- V4.0 Reference Workflow Console component-level + BFF integration E2E。

未完成：

- browser-level smoke / full browser E2E。
- 完整 Workflow Studio 低代码编辑器。
- 真实节点拖入后创建 Station。
- 连线写回 WorkflowEdge。
- Inspector 通过 WorkflowPatch 写回 draft。
- Patch apply/reject/publish UI E2E。
- 完整 AgentTalkWindow 状态机。
- production-ready external app support。

## 6. 审计建议

当前可以进入后续 V4.0 开发，但建议下一阶段优先补：

1. Browser-level smoke：Playwright/Cypress 覆盖 open console、select instance、render board、approve、context update、event refresh。
2. Editing hardening：真实 `workflow.patch.apply/reject/publish` BFF/UI E2E。
3. Canvas-to-runtime bridge：节点拖入、连线、Inspector 表单只通过 patch/draft 合同写回，不直接写 runtime store。
4. AgentTalkWindow 正式化：将当前 preparation shell 升级为有状态但仍受 governance 约束的 Agent workflow assistant。

在这些完成前，保持当前阶段声明：

```text
V4.0 dev/local Workflow Console integration baseline ready.
```
