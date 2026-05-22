# V4.0-M Operation Evidence / Governance Review Completion Note

状态：V4.0-M complete；完整回归与浏览器 smoke 均已完成。

允许声明：

```text
V4.0-M complete: user-confirmed operation evidence and governance review baseline ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete AgentTalkWindow ready
controlled executor ready
autonomous workflow editing ready
Agent executor ready
production-ready external app support
enterprise auth/OAuth/SSO ready
```

## Implementation Evidence

新增 / 更新代码：

```text
apps/api/agent_operation_evidence_store.py
apps/api/routers/bff.py
apps/workflow-console/src/api/types.ts
apps/workflow-console/src/api/workflowConsoleClient.ts
apps/workflow-console/src/hooks/useWorkflowConsoleData.ts
apps/workflow-console/src/components/GovernanceReviewPanel.tsx
apps/workflow-console/src/components/ConsoleShell.tsx
apps/workflow-console/src/App.tsx
```

新增 BFF routes：

```text
GET /bff/instances/{instance_id}/agent/operation-evidence
GET /bff/instances/{instance_id}/agent/operation-evidence/{evidence_id}
GET /bff/instances/{instance_id}/agent/governance-review
```

新增 tests：

```text
tests/test_v4_0_operation_evidence_bff.py
tests/test_v4_0_operation_evidence_correlation.py
tests/test_v4_0_operation_evidence_scope.py
tests/test_v4_0_operation_evidence_redaction.py
tests/test_v4_0_operation_evidence_idempotency.py
tests/test_v4_0_governance_review_panel.py
apps/workflow-console/src/__tests__/operationEvidence.test.tsx
apps/workflow-console/e2e/workflow-operation-evidence-smoke.spec.ts
```

## Verified Behavior

- Patch apply/reject、publish、approval.respond、workflow.context.update、business.event.emit 的用户确认操作会生成 `OperationEvidenceRecord`。
- Failed / blocked / stale / expired operation attempt 使用明确 evidence status，不伪装 success。
- Idempotent replay 使用 `idempotent_replayed`，不重复生成 success evidence。
- Governance Review Panel 是只读派生视图，不执行 operation。
- Evidence / governance review routes 校验 scope、instance ownership 和 capability。
- DTO / audit / DOM 不泄露 token、Authorization、raw trace、raw artifact、raw connector payload 或 raw prompt。

## Validation Commands

本阶段已执行：

```text
./.venv/bin/python -m pytest tests/test_v4_0_operation_evidence_*.py tests/test_v4_0_governance_review_panel.py -q
10 passed

cd apps/workflow-console && npm test
35 passed

cd apps/workflow-console && npm run build
passed

./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
105 passed
```

完整冻结回归已执行：

```text
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

./.venv/bin/python -m pytest -q
546 passed, 3 skipped

cd apps/workflow-console && npm run test:e2e
8 passed

cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

## No False Green

V4.0-M 只证明 user-confirmed operation evidence 和 governance review baseline。它不证明 Agent executor、controlled executor、autonomous workflow editing、complete Workflow Studio、complete AgentTalkWindow 或 production-ready external app support。
