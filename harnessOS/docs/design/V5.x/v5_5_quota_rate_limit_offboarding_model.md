# V5-5 Quota / Rate Limit / Offboarding Model

文档状态：V5-5 core slice implemented for review。

## Quota Model

```text
quota_policy_id
tenant_id
app_id
limit_type
limit_value
window_seconds
enforcement_status
```

## Offboarding Model

```text
offboarding_id
tenant_id
app_id
revoked_capability_refs
revoked_credential_refs
data_export_status
deletion_status
evidence_ref
```

## Acceptance Rules

```text
quota denial is auditable
rate limit cannot leak sensitive payload
offboarding revokes app access
offboarding evidence is redacted
```
