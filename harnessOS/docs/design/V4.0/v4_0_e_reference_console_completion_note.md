# V4.0-E Reference Workflow Console Completion Note

文档状态：V4.0-E complete at integration baseline。

## Allowed Claim

```text
V4.0 dev/local Workflow Console integration baseline ready.
```

由于本阶段未引入 Playwright browser-level smoke，不能升级为完整 browser E2E baseline。

## Completed Scope

- 平台中立 reference workflow fixture，不依赖 Meeting / Knowledge / Video / external MCP。
- Fixture 生成或加载 WorkflowTemplate、WorkflowVersion、WorkflowInstance、StationRun、Job、Artifact、Approval、QualityEvaluation、WorkflowContext、Trace summary。
- Fixture 包含 BusinessEventBinding：
  - `event_type = business.video.scene.selected`
  - `payload_path = event.payload.scene_id`
  - `target_path = context.business.selected_scene`
  - `mode = set`
- E2E 验证 `business.event.emit -> binding -> context.business.selected_scene` 更新。
- Seeded patch diff 来自 V3.6 patch repository / Gateway fixture，不来自 frontend demoData。
- UI 通过 BFF PatchDiffDTO 渲染 before / after / risk_flags。
- Source scan 继续禁止 `workflow.patch.apply`、`workflow.patch.reject`、`workflow.template.publish`。
- Approval E2E 验证 workflow-bound `approval.respond` side effect：
  - approve 前 workflow / station 处于 `waiting_approval`
  - 用户显式 approve 后 board/status 刷新
  - workflow / station 继续并完成
  - Agent shell 不触发 `approval.respond`
- EventBridge 只作为 refresh/display signal：
  - fake event payload status 不被 UI 采信
  - UI 重新拉 board/status/context/approval DTO
  - SSE proxy 保留 `id/event/data`
  - 不暴露 upstream subscription token 或 signed URL
- DTO redaction 覆盖 BoardDTO、InstanceStatusDTO、ApprovalDTO、QualityEvaluationDTO、ContextDTO、PatchDiffDTO、EventEnvelopeDTO。
- Demo fixture 双重禁用：
  - reference frontend E2E-style test 不 import demoData
  - real mode 下 BFF/runtime fixture 不可用时测试失败，不 silent fallback demoData
- Scope / ownership 覆盖 cross-scope 与 same-scope wrong-instance：
  - approval
  - artifact metadata / lineage
  - quality
  - context
  - business event
  - patch diff

## Evidence Files

Backend and BFF integration:

```text
tests/v4_0_reference_support.py
tests/test_v4_0_reference_workflow_console_e2e.py
tests/test_v4_0_reference_console_scope_isolation.py
tests/test_v4_0_reference_console_eventbridge_e2e.py
tests/test_v4_0_reference_console_operation_panels_e2e.py
tests/test_v4_0_reference_console_redaction.py
```

Frontend integration-style tests:

```text
apps/workflow-console/src/__tests__/referenceConsoleE2E.test.tsx
```

Regression guard tests:

```text
tests/test_v4_0_frontend_no_direct_core_calls.py
tests/test_v4_0_contract_doc_alignment.py
tests/test_v4_0_workflow_console_readonly.py
tests/test_v4_0_workflow_editing_mvp.py
tests/test_v4_0_agent_talk_window_preparation.py
```

## Latest Verified Results

```text
./.venv/bin/python -m pytest tests/test_v4_0_reference_* tests/test_v4_0_operation_panels_bff_routes.py -q
12 passed

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

./.venv/bin/python -m pytest -q
491 passed, 3 skipped

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

## No False Green

Still cannot claim:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
```

Browser-level smoke remains pending. The next planned phase is `V4.0-F Browser Smoke Baseline`, documented in:

```text
docs/design/V4.0/v4_0_f_browser_smoke_plan.md
```

V4.0-F should add fixed Playwright coverage using `npm run build` + Vite preview, a seeded test BFF / V3.6 runtime fixture, explicit `VITE_HARNESSOS_DEMO_MODE=false`, open console, select instance, render board, approve via ApprovalPanel, update context.business, controlled EventBridge refresh, no direct browser `/v1/rpc` or `/v1/events/subscribe`, no Demo / Fixture badge, and DOM / HTML redaction.

If V4.0-F passes, the only upgraded claim is:

```text
V4.0 dev/local Workflow Console browser smoke baseline ready.
```

It still cannot claim complete Workflow Studio ready, complete AgentTalkWindow ready, production-ready external app support, or full browser E2E ready.
