# V6-6 External App Onboarding DTO Contract

文档状态：V6-6 complete / ready for review。本文定义 V6-6 DTO / schema 合同和完成后仍需遵守的边界。

## Current Decision

```text
V6-6 status: complete / ready for review.
DTO/schema and test matrix were accepted before implementation.
V6-7 implementation remains NO-GO.
```

## Required Common Fields

Every V6-6 DTO must include:

```text
tenant_id
workspace_id
app_id
service_account_id
actor_id
request_id
correlation_id
audit_ref
policy_decision
created_at
```

All DTOs must use redacted references only. They must not include raw secret, raw token, raw prompt, raw connector payload, raw artifact content, or signed URL.

## DTO List

### ExternalAppRegistrationDTO

Purpose: records tenant-bound external app registration and service account binding.

Required additional fields:

```text
registration_id
app_display_name
domain_refs
status
```

### DomainVerificationDecisionDTO

Purpose: records whether a domain is verified before any origin allowlist decision.

Required additional fields:

```text
domain
verification_method
verification_status
verified_at
denial_reason
```

### OriginAllowlistDecisionDTO

Purpose: records allow/deny for browser origin access.

Required additional fields:

```text
origin
domain_verification_ref
decision
denial_reason
```

### QuotaDecisionDTO

Purpose: records quota and rate-limit allow/deny decisions.

Required additional fields:

```text
quota_policy_ref
rate_limit_policy_ref
current_usage
limit
decision
denial_reason
```

### ExternalAppOffboardingEvidenceDTO

Purpose: records complete external app offboarding and revocation.

Required additional fields:

```text
offboarding_id
revoked_app_credentials
revoked_origin_allowlist
revoked_active_sessions
revoked_pending_capability_grants
revocation_refs
```

### SdkCompatibilityPolicyDTO

Purpose: records SDK route compatibility and internal route denial policy.

Required additional fields:

```text
sdk_policy_id
allowed_bff_routes
denied_internal_routes
browser_direct_runtime_route_denied
browser_direct_v1_rpc_denied
browser_direct_v1_events_subscribe_denied
```

## Acceptance Matrix

```text
unverified_domain_origin_allowlist_denied
wrong_tenant_app_access_denied
unknown_origin_denied
quota_denial_auditable
rate_limit_denial_auditable
offboarding_revokes_credentials
offboarding_revokes_origins
offboarding_revokes_sessions
offboarding_revokes_pending_grants
browser_sdk_no_direct_internal_runtime_route
```

## No False Green

V6-6 allowed claim:

```text
V6-6 complete: production external app onboarding pilot slice ready for review.
```

Forbidden claims:

```text
production-ready external app support
production customer onboarding ready
complete developer platform ready
```
