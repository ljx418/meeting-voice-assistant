# V4.0-M Operation Evidence / Governance Review Plan

阶段定位：V4.0-M 只做 user-confirmed operation evidence 和 governance review。它不做 Agent executor、不做 controlled executor、不做 autonomous workflow editing、不新增新的执行能力。

完成后最多声明：

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

## PR Slices

| Slice | 目标 | 边界 |
| --- | --- | --- |
| M-PR1 Evidence contract / repository | 新增 `OperationEvidenceRecord`、`OperationEvidenceChain`、`GovernanceReviewSummary`、`OperationRuntimeResultRef` 和 dev/local `AgentOperationEvidenceRepository`。 | BFF/UI 层对象，不进入 V3.6 runtime contract；不写 WorkflowTemplate / WorkflowDraft / WorkflowVersion / StationRun。 |
| M-PR2 Evidence creation hooks | 在用户显式确认的 operation routes 返回结果后创建 evidence。 | 覆盖 patch apply/reject、publish、approval.respond、context.update、business.event.emit；handoff created/opened/dismissed 只进入 audit。 |
| M-PR3 Read-only BFF routes | 新增 operation evidence / governance review 只读 structured routes。 | Routes 不执行 mutation；校验 scope、instance ownership 和 capability。 |
| M-PR4 Governance Review Panel | 新增只读“治理审计”面板，展示建议来源、handoff 状态、用户确认、执行结果、风险、策略和 runtime result ref。 | 不出现 Apply / Publish / Approve / Reject / Execute / Run；后续动作只能跳转已有 operation panels。 |
| M-PR5 Redaction / docs / tests | DTO、audit、DOM 和 error response 全链路 redaction；同步 docs 与 drawio。 | 不记录 raw prompt / raw trace / raw artifact / raw connector payload。 |

## Evidence Contract

`OperationEvidenceRecord` 固定字段：

```text
evidence_id
workflow_instance_id
workflow_template_id
operation
status
correlation_id
operation_id
idempotency_key
handoff_id
proposal_id
handoff_status_at_execution
proposal_status_at_execution
user_confirmed
source
risk_flags
policy_decision
runtime_result_ref
audit_refs
created_at
created_by
redaction_status
```

`status` 固定为：

```text
succeeded
failed
idempotent_replayed
blocked
stale_rejected
expired_rejected
```

`GovernanceReviewSummary` 是派生 read model，不是可写事实源。

## BFF Routes

```text
GET /bff/instances/{instance_id}/agent/operation-evidence
GET /bff/instances/{instance_id}/agent/operation-evidence/{evidence_id}
GET /bff/instances/{instance_id}/agent/governance-review
```

能力：

```text
operation_evidence.read
governance_review.read
```

## Test Plan

新增 / 更新：

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

验收覆盖：

- proposal -> handoff -> user action -> runtime result -> evidence chain。
- patch apply/reject、publish、approval.respond、context update、business event evidence。
- failed / blocked / stale / expired operation attempt 有明确 evidence status。
- idempotent replay 不重复生成 success evidence。
- evidence routes read-only。
- same-scope wrong-instance denied，cross-scope denied，missing capability denied。
- governance review 只读。
- DOM / DTO / audit redaction。
- Browser 不请求 `/v1/rpc` 或 `/v1/events/subscribe`。

## Risk Controls

- Evidence 只在已有 user-confirmed operation route 返回后创建，不参与 runtime 决策。
- Public BFF routes 只读；store append-only，不提供 delete 或 arbitrary update。
- EventBridge 仍只触发 refresh，UI 不从 event payload 构造 evidence truth。
- Agent panel 仍不能执行 apply/publish/approval/context/business event。
- 所有 evidence / governance review DTO 均 redacted。
