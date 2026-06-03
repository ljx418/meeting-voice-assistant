# V5-5 App Registration / Domain / Origin Model

文档状态：V5-5 core slice implemented for review。

## App Registration

```text
app_registration_id
tenant_id
workspace_id
app_id
owner_actor_id
allowed_capabilities
status
created_at
```

## Domain Verification

```text
domain_verification_id
domain
verification_method
verification_status
verified_at
evidence_ref
```

## Origin Allowlist

```text
origin
tenant_id
app_id
verified_domain_ref
status
policy_decision
```
