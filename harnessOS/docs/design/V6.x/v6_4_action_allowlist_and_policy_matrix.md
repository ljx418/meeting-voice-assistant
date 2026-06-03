# V6-4 Action Allowlist And Policy Matrix

文档状态：V6-4 policy matrix / pre-implementation audit input。本文定义 action 风险、准入和拒绝矩阵。

## 1. Allowed Initial Action Set

| Operation | Risk | Confirmation | Approval Gate | Idempotency | Kill Switch | Rollback / Correction | Audit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `workflow.instance.start` | medium | required | optional | required | required | cancel_or_mark_failed_before_external_effect | required |
| `station.rerun` | medium | required | optional | required | required | old attempt retained, new attempt auditable | required |
| `artifact.write` | medium minimum | required | required | required | required | append correction or retract ref | required |
| `quality.evaluation.create` | medium minimum | required | required | required | required | append correction evaluation | required |

## 2. Excluded Actions

Always denied in V6-4:

```text
business.event.emit
context.update
workflow.template.publish
approval.respond
connector.call
external_llm.call
```

These actions require a separate approval policy, credential boundary and incident response review before any future production execution.

## 3. Source Policy

| Source | Allowed | Conditions |
| --- | --- | --- |
| `product_console` | yes | human_user, user_confirmed=true, human_authorization_ref |
| `approved_api` | yes | service_account_with_human_authorization, tenant-bound API client, quota/rate limit checked |
| `agent` | no | direct durable mutation denied |
| `browser_direct_internal_route` | no | browser cannot call internal runtime route directly |
| `external_app` | not in V6-4 default | requires V6-6 accepted boundary first |

## 4. Actor Policy

Allowed:

```text
human_user
service_account_with_human_authorization
```

Denied:

```text
agent
service_account_without_human_authorization
service_account_as_admin_override
anonymous
cross_tenant_actor
```

## 5. Required Denial Cases

```text
source_agent_durable_mutation_denied
approved_api_without_human_authorization_denied
approved_api_expired_human_authorization_denied
approved_api_wrong_tenant_denied
approved_api_wrong_workspace_denied
approved_api_source_agent_denied
service_account_without_human_authorization_denied
service_account_expired_authorization_denied
service_account_wrong_operation_denied
service_account_as_agent_executor_denied
kill_switch_active_denied
excluded_operation_denied
raw_artifact_content_denied
raw_secret_or_prompt_denied
idempotency_key_conflict_denied
```

## 6. No False Green Policy

Passing V6-4 policy matrix means:

```text
limited production controlled executor pilot slice ready for review
```

It does not mean:

```text
production controlled executor ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
```
