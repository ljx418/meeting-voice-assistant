# V4.0-L Agent Handoff Lifecycle / Audit / Recovery Hardening Plan

文档状态：V4.0-L implementation baseline。

## Positioning

V4.0-L builds on V4.0-K. It hardens `AgentActionHandoff` lifecycle, audit, and recovery for the dev/local Workflow Console. It does not implement an Agent executor, autonomous workflow editing, complete AgentTalkWindow, or production persistence.

Allowed exit claim:

```text
V4.0-L complete: Agent handoff lifecycle, audit, and recovery baseline ready for dev/local Workflow Console.
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

## Repository

`AgentHandoffRepository` / `InMemoryAgentHandoffStore` is the BFF boundary for handoffs. It is dev/local only and is not production persistence.

Allowed methods:

```text
create
get
list
mark_opened
mark_used
dismiss
expire
mark_stale
mark_blocked
append_audit
list_audit
```

No arbitrary `update_status` is exposed.

## Lifecycle

States:

```text
active
opened
used_for_user_confirmed_action
dismissed
expired
stale
blocked
```

Allowed transitions:

```text
active -> opened / dismissed / expired / stale / blocked
opened -> used_for_user_confirmed_action / dismissed / expired / stale / blocked
```

Terminal:

```text
used_for_user_confirmed_action
dismissed
expired
stale
blocked
```

Repeated open and repeated dismiss are idempotent. Terminal states cannot reopen or execute. No `executed` state exists.

## Recovery

The UI supports:

```text
?handoff_id=...
```

Recovery reads the BFF handoff DTO, opens the matching panel, and performs no mutation. It still checks scope, ownership, capability, expiration, and stale state.

## Stale / Blocked Guards

Editing handoff stale / blocked conditions:

- `patch.status != proposed`
- draft revision mismatch
- patch diff missing
- `requires_approval=true` blocks direct apply

Approval handoff stale conditions:

- approval status not pending
- workflow binding inactive
- workflow instance ended

Context handoff stale conditions:

- current context revision differs from expected revision
- target path is not `business.*`

## Audit

Audit routes:

```text
GET /bff/instances/{instance_id}/agent/action-handoffs
GET /bff/instances/{instance_id}/agent/action-handoffs/{handoff_id}/audit
```

Audit is append-only and redacted. No audit update/delete route exists.

## Tests

```text
tests/test_v4_0_agent_handoff_repository.py
tests/test_v4_0_agent_handoff_lifecycle.py
tests/test_v4_0_agent_handoff_recovery.py
tests/test_v4_0_agent_handoff_audit.py
tests/test_v4_0_agent_handoff_stale_guards.py
apps/workflow-console/src/__tests__/agentHandoffLifecycle.test.tsx
apps/workflow-console/e2e/workflow-agent-handoff-recovery-smoke.spec.ts
```

