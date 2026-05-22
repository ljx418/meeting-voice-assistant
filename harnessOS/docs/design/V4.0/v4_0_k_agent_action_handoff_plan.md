# V4.0-K Agent Action Handoff to User-Confirmed Operation Panels Plan

文档状态：V4.0-K implementation baseline。

## Positioning

V4.0-K builds on V4.0-J AgentTalk governance. It does not implement an Agent executor, autonomous workflow editing, or complete AgentTalkWindow. It only lets `AgentActionProposal` hand off context to existing operation panels where a user must explicitly confirm the final action.

Allowed exit claim:

```text
V4.0-K complete: Agent action handoff to user-confirmed operation panels ready for dev/local Workflow Console.
```

Forbidden:

```text
complete AgentTalkWindow ready
controlled executor ready
autonomous workflow editing ready
Agent executor ready
production-ready external app support
enterprise auth/OAuth/SSO ready
```

## Contract

`AgentActionHandoff` is a BFF/UI-layer object only. It does not enter the V3.6 Workflow Runtime Contract and does not write `WorkflowTemplate`, `WorkflowDraft`, `WorkflowVersion`, or `StationRun`.

Fields:

```text
handoff_id
proposal_id
workflow_instance_id
workflow_template_id
target_panel
target_resource
suggested_form_prefill
expires_at
status
created_at
created_by
redaction_status
```

Allowed `target_panel`:

```text
editing_panel
approval_panel
context_panel
quality_panel
artifact_panel
```

`suggested_form_prefill` is non-executable. It can prefill UI fields but cannot be used as a direct runtime payload.

## BFF Routes

```text
POST /bff/instances/{instance_id}/agent/action-proposals/{proposal_id}/handoff
GET  /bff/instances/{instance_id}/agent/action-handoffs/{handoff_id}
```

These routes create/read handoff DTOs only. They must not call:

```text
workflow.patch.apply
workflow.patch.reject
workflow.template.publish
approval.respond
workflow.context.update
business.event.emit
```

## User Confirmation Guard

Final operation routes continue using V4.0-G / V4.0-D execution paths. When invoked from an Agent handoff, requests carry:

```text
user_confirmed=true
source=editing_panel | approval_panel | context_panel
proposal_id
handoff_id
```

BFF rejects:

```text
source=agent
partial handoff pair
target_panel mismatch
expired handoff
proposal blocked / dismissed / expired
same-scope wrong-instance
cross-scope ownership mismatch
```

## UI

Agent proposal cards can show:

```text
查看详情
查看 Diff
前往编辑面板
前往审批面板
前往上下文面板
忽略建议
```

Agent panel must not show:

```text
Apply
Publish
Approve
Reject
Execute
Run
自动应用
自动发布
已帮你修改并发布
```

Operation panels display `来自 Agent 建议` and still require explicit user confirmation.

## Tests

```text
tests/test_v4_0_agent_action_handoff_bff.py
tests/test_v4_0_agent_action_handoff_scope.py
tests/test_v4_0_agent_action_handoff_redaction.py
tests/test_v4_0_agent_action_handoff_user_confirmation.py
apps/workflow-console/src/__tests__/agentActionHandoff.test.tsx
apps/workflow-console/e2e/workflow-agent-handoff-smoke.spec.ts
```

## Risk Controls

- Handoff route creates DTO only; it is not an executor.
- Existing panel routes remain the only execution path.
- Sensitive fields are redacted from DTO, audit, errors, and DOM.
- Stale/expired handoffs are visible and cannot silently execute.
