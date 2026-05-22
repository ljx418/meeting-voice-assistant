# V4.0-P AgentTalkWindow Interaction E2E Plan

文档状态：V4.0-P revised and implemented；基于 V4.0-O governed canvas proposal workflow complete。本文定义 AgentTalkWindow 交互端到端验证计划。V4.0-P 不是完整 AgentTalkWindow，不是 Agent executor，不是 controlled executor，也不是 autonomous workflow editing。

## 1. Allowed Claim

```text
V4.0-P complete: AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation.
```

## 2. Forbidden Claims

```text
complete Workflow Studio ready
full low-code canvas editing ready
complete AgentTalkWindow ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
direct canvas-to-runtime mutation ready
production-ready external app support
```

## 3. Stage Boundary

V4.0-P 只补 AgentTalkWindow 的交互闭环和浏览器级证据，不引入执行器。

必须保持：

```text
Agent can propose / handoff / explain / navigate.
Agent cannot apply / publish / reject / approval.respond / context.update / business.event.emit / start workflow / rerun station.
EventBridge only triggers refresh.
UI must reload Agent session, suggestions, action proposals, handoffs, patch queue, canvas projection, board/status, context and evidence DTOs from BFF truth.
```

## 4. PR Slices

| Slice | Goal | Required Evidence |
| --- | --- | --- |
| P-PR1 AgentTalk Interaction State Contract | 固定 AgentTalkWindow 交互态：session、message、suggestion、action proposal、handoff、selected evidence。 | BFF DTO tests、frontend state tests、source scan。 |
| P-PR2 Explain and Summarize E2E | 验证 Agent explain workflow、summarize events、summarize context 只读交互。 | Browser smoke、DOM redaction、no mutation route。 |
| P-PR3 Suggest Patch to Handoff E2E | 验证 Agent suggest patch -> proposal -> handoff -> Editing Panel，但 apply 仍由用户显式确认。 | Handoff scope tests、patch queue refresh tests、no source=agent apply。 |
| P-PR4 Evidence Review Interaction | Agent 面板可导航到 governance review / operation evidence，只读展示 evidence chain。 | Evidence DTO redaction、wrong-instance denial、browser navigation smoke。 |
| P-PR5 Event Truth Regression | fake event payload 不得构造 Agent session、patch、handoff、evidence、board/status 或 context truth。 | fake event unit tests、browser smoke request assertions。 |
| P-PR6 Multi-Proposal State Race | 多 suggestion / 多 action proposal / 多 handoff / 多 patch 时 selected state 不静默指向 stale object。 | stale selected proposal tests、refresh-after-dismiss tests。 |
| P-PR7 Fixture Isolation | 每个 browser spec 独立 seed workflow_instance_id、agent_session_id、proposal_id、handoff_id。 | 独立运行和调换顺序通过。 |
| P-PR8 Claim Guard and Docs Sync | claim guard 扩展到 P 文档和 source copy，禁止过度声明。 | claim guard tests、README/gap/audit/drawio sync。 |

## 5. Test Plan

新增或扩展后端 / 合同测试：

```text
tests/test_v4_0_agenttalk_interaction_e2e_bff.py
tests/test_v4_0_agenttalk_interaction_event_truth.py
tests/test_v4_0_agenttalk_interaction_redaction.py
tests/test_v4_0_agenttalk_interaction_scope.py
tests/test_v4_0_agenttalk_interaction_claim_guard.py
```

新增或扩展前端测试：

```text
apps/workflow-console/src/__tests__/agentTalkInteractionE2E.test.tsx
apps/workflow-console/src/__tests__/agentTalkEventTruth.test.tsx
apps/workflow-console/src/__tests__/agentTalkEvidenceReview.test.tsx
```

新增 browser smoke：

```text
apps/workflow-console/e2e/workflow-agenttalk-interaction-smoke.spec.ts
apps/workflow-console/e2e/workflow-agenttalk-event-truth-smoke.spec.ts
```

必测断言：

```text
Agent explain/summarize sends no mutation request.
Agent suggest patch creates proposal only.
Agent handoff opens target panel without executing operation.
Apply/reject/publish still require user_confirmed=true and source=editing_panel.
Evidence review is read-only and redacted.
Fake event payload cannot create Agent session/suggestion/proposal/handoff/evidence truth.
No direct /v1/rpc browser request.
No direct /v1/events/subscribe browser request.
No forbidden copy such as 自动应用 / 自动发布 / complete AgentTalkWindow.
Claim guard blocks forbidden completion claims.
```

## 6. Regression Commands

```bash
./.venv/bin/python -m pytest tests/test_v4_0_agenttalk_interaction_*.py tests/test_v4_0_claim_guard.py -q
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q

cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e

cd sdk/typescript && npm test

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
```

## 7. Completion Evidence Format

Completion note must record:

```text
Allowed claim
Forbidden claims
BFF / API files changed
workflow-console files changed
tests added or changed
docs updated
focused P test result
V4.0 focused test result
V3.6 focused regression
V3.5 focused regression
full pytest result
workflow-console npm test
workflow-console build
workflow-console e2e
TypeScript SDK npm test
drawio XML validation
No False Green statement
```

## 8. Documents to Audit Before Implementation

```text
docs/design/V4.0/00_README.md
docs/design/V4.0/v4_0_current_gap_analysis.md
docs/design/V4.0/v4_0_current_gap_analysis.drawio
docs/design/V4.0/v4_0_completion_audit_report.md
docs/design/V4.0/v4_0_ui_contract_map.md
docs/design/V4.0/v4_0_event_contract_map.md
docs/design/V4.0/v4_0_mock_to_real_contract_checklist.md
docs/design/V4.0/v4_0_stitch_prototype_mapping.md
docs/design/V4.0/v4_0_workflow_studio_low_code_baseline.md
docs/design/V4.0/v4_0_workflow_studio_agent_copilot_prd.md
docs/design/V4.0/v4_0_i_agent_talk_window_stateful_plan.md
docs/design/V4.0/v4_0_j_agent_talk_governance_plan.md
docs/design/V4.0/v4_0_k_agent_action_handoff_plan.md
docs/design/V4.0/v4_0_l_agent_handoff_lifecycle_plan.md
docs/design/V4.0/v4_0_m_operation_evidence_plan.md
docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_plan.md
docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_completion_note.md
docs/design/V3.6/00_README.md
docs/design/V3.6/v3_6_current_gap_analysis.md
docs/design/V3.6/v3_6_workflow_contract.md
```

## 9. No False Green

V4.0-P 只证明 AgentTalkWindow interaction E2E baseline。

它不证明：

```text
complete AgentTalkWindow
Agent executor
controlled executor
autonomous workflow editing
complete Workflow Studio
full low-code canvas editing
production-ready external app support
```
