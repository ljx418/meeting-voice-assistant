# V5-7B Service Account Boundary Review

文档状态：V5-7B closure evidence。本文只记录 service_account_with_human_authorization 边界审查要求，不启用 runtime。

## Required Fields

```text
service_account_id
tenant_id
workspace_id
human_authorization_ref
authorization_subject_actor_id
authorization_created_at
authorization_expires_at
allowed_operations
policy_decision
audit_ref
```

## Explicit Non-Executor Boundary

```text
service_account_with_human_authorization is not Agent executor
service_account_with_human_authorization is not autonomous executor
service_account_with_human_authorization is not production admin override
```

## Required Tests

```text
service_account_without_human_authorization_denied
service_account_expired_authorization_denied
service_account_wrong_operation_denied
service_account_as_agent_executor_denied
service_account_records_human_authorization_ref
```

## Current Review Decision

```text
NEEDS_MORE_EVIDENCE
```

Reason:

```text
service_account_with_human_authorization boundary has not been proven by runtime or staging fixture evidence.
```
