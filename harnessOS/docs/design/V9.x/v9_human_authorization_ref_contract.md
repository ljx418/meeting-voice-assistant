# V9 HumanAuthorizationRef Contract

文档状态：V9 shared authorization contract / required before V9-2 implementation。

## 1. Purpose

`HumanAuthorizationRef` 是 durable mutation 的人工授权证据引用。它可以作为 `user_confirmed=true` 的等价授权入口，但不能绕过 policy、capability、approval、kill switch、timeout、rollback 和 evidence 边界。

核心不变量：

```text
Durable mutation is denied unless user_confirmed=true OR human_authorization_ref is present and valid.
source=agent default durable mutation remains denied even when human_authorization_ref exists.
Approval gate is an additional gate for high-risk operations, not a replacement for human authorization.
```

## 2. Contract Fields

Required fields:

```text
human_authorization_ref
issuer_type
issuer_id
authorization_subject_actor_id
tenant_id
workspace_id
project_id
app_id
operation
operation_hash
target_refs
allowed_sources
allowed_actor_types
scope
created_at
expires_at
revoked
revoked_at
revocation_reason
correlation_id
request_id
audit_ref
```

Rules:

```text
additionalProperties=false
human_authorization_ref must be immutable after creation except revocation fields.
operation_hash must bind operation + target_refs + scope.
target_refs must be non-empty and operation-specific.
expires_at must be present for every non-read operation.
revoked=true blocks runtime use.
raw prompt / raw file content / raw artifact content / raw provider payload / raw connector payload / token / secret fields are forbidden.
```

## 3. Issuer And Scope

Allowed `issuer_type`:

```text
human_user
product_console
approved_api_with_human_authorization
```

Denied issuer/source patterns:

```text
source=agent
autonomous_executor
unrestricted_terminal_worker
browser_automation_without_user_session
```

Scope requirements:

```text
tenant_id / workspace_id / project_id / app_id must match the execution envelope.
operation must match the requested durable mutation.
target_refs must match the requested runtime target.
allowed_sources must include product_console or approved_api before those sources can use the ref.
allowed_actor_types must include human_user or service_account_with_human_authorization before those actors can use the ref.
```

## 4. Validation Rules

`HumanAuthorizationRef` is valid only if:

```text
ref exists.
revoked=false.
created_at <= execution_requested_at < expires_at.
operation_hash matches the execution envelope operation and target_refs.
tenant/workspace/project/app refs match.
actor_type and source are allowed.
audit_ref exists.
redaction scan PASS.
```

It is invalid if:

```text
ref belongs to another tenant/workspace/project/app.
ref has expired.
ref was revoked.
ref was issued by source=agent.
operation_hash does not match.
target_refs are missing or weaker than the execution envelope target_refs.
raw secret / token / raw prompt / raw content appears in the authorization record.
```

## 5. Negative Tests

```text
human_authorization_ref_missing_for_durable_mutation_denied
human_authorization_ref_expired_denied
human_authorization_ref_revoked_denied
human_authorization_ref_wrong_tenant_denied
human_authorization_ref_wrong_workspace_denied
human_authorization_ref_wrong_operation_hash_denied
human_authorization_ref_missing_target_refs_denied
human_authorization_ref_source_agent_issuer_denied
human_authorization_ref_raw_secret_denied
human_authorization_ref_does_not_replace_approval_gate_for_high_risk_action
```

## 6. Evidence Requirements

Every runtime evidence package that uses `human_authorization_ref` must record:

```text
human_authorization_ref
operation
operation_hash
target_refs
authorization_subject_actor_id
created_at
expires_at
revoked
audit_ref
correlation_id
request_id
redaction_status
```

The evidence package must not record raw user prompt, raw file content, raw provider payload, raw connector payload, API key, Bearer token, signed URL, or raw artifact content.
