# V5-4A Approval / Sandbox / Kill Switch Model

文档状态：V5-4A core slice implemented for review。

## Approval Gate

```text
approval_required
approval_policy_id
risk_flags
human_approver_ref
approval_evidence_ref
```

## Sandbox Boundary

```text
redacted input only
approved artifact refs only
no raw connector payload
no raw prompt
no token or secret
no direct WorkflowStore write
```

## Kill Switch

```text
per-agent kill switch
per-workspace kill switch
capability revocation
operation timeout
manual recovery path
audit retention
```

## No Route In V5-4A

V5-4A 不新增 execute、run、kill-switch、rollback 或 admin override route。

## Implemented Core Slice

```text
ApprovalGatePlanner creates a future approval descriptor only.
ExecutorSandboxBoundary rejects token, secret, raw payload, and direct runtime truth write refs.
KillSwitchRegistry supports in-memory per-agent, per-workspace, and capability revocation decisions for focused validation.
```
