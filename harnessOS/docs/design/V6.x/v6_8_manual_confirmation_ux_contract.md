# V6-8 Manual Confirmation UX Contract

文档状态：V6-8 complete / ready for review。本文定义人工确认 UX 合同，并已由 V6-8 Product Console evidence package 验证。

## Purpose

Manual Confirmation UX converts a user-visible confirmation action into an auditable `human_authorization_ref`. It does not execute runtime actions by itself.

## Required Fields

```text
human_authorization_ref
tenant_id
workspace_id
project_id
app_id
actor_id
actor_type
operation
target_refs
risk_flags
policy_decision_ref
created_at
expires_at
correlation_id
request_id
audit_ref
```

## Allowed Operations

The UI may request confirmation for operations allowed by the current stage policy. For the V6-8 pilot, this means confirming or opening handoff for already governed V6-4 / V6-5 / V6-6 flows.

## Forbidden Behavior

- Manual confirmation cannot bypass V6-4 controlled executor policy.
- Manual confirmation cannot turn source=agent into direct durable mutation.
- Manual confirmation cannot expose raw credential, raw prompt, raw artifact content or token.
- Manual confirmation cannot become an execution panel for Evidence Review.

## Acceptance

The evidence package must prove:

```text
confirmation button creates human_authorization_ref
runtime action is still delegated to controlled executor or approved handoff
audit_ref and correlation_id are recorded
no hidden mutation form exists
```

Evidence:

```text
docs/design/V6.x/evidence/v6-8-product-console/raw/product-console-state.json
docs/design/V6.x/evidence/v6-8-product-console/acceptance-data.json
tests/test_v6_8_product_console.py
```
