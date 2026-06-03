# V6-6 Production External App Onboarding Development And Acceptance Plan

文档状态：V6-6 complete / ready for review。本文记录开发与验收门槛、完成证据和禁止误报边界。

## Allowed Claim

```text
V6-6 complete: production external app onboarding pilot slice ready for review.
```

## Goal

把 V5 external app onboarding boundary 推进为生产试点级接入：tenant-bound app registration、domain verification、origin allowlist、quota/rate limit、offboarding、SDK compatibility。

## Non-Goals

```text
production-ready external app support
production customer onboarding ready
complete developer platform ready
```

## Development Scope

- ExternalAppRegistration：绑定 tenant_id、workspace_id、app_id、service_account_id。
- DomainVerificationDecision：domain 验证通过前不得加入 origin allowlist。
- OriginAllowlistDecision：拒绝 unknown origin / wrong tenant。
- QuotaDecision：记录 quota / rate limit allow/deny。
- ExternalAppOffboardingEvidence：撤销 app access、app credentials、origin allowlist、active sessions、pending capability grants。
- SdkCompatibilityPolicy：浏览器 SDK 不直连内部 runtime 或 `/v1/rpc`。

Detailed DTO / schema contract:

```text
v6_6_external_app_onboarding_dto_contract.md
schemas/v6_6_external_app_registration.schema.json
schemas/v6_6_domain_verification_decision.schema.json
schemas/v6_6_origin_allowlist_decision.schema.json
schemas/v6_6_quota_decision.schema.json
schemas/v6_6_external_app_offboarding_evidence.schema.json
schemas/v6_6_sdk_compatibility_policy.schema.json
```

## Entry Conditions

```text
V6-5 completion package accepted or explicit dependency waiver recorded
V6-1 tenant boundary evidence available
V6-2 credential lifecycle evidence available
V6-3 audit export evidence available
V6-4 controlled executor boundary evidence available
No False Green claim scan PASS
```

V6-6 不需要单独 high-risk proceed decision，除非计划引入生产客户真实数据、第三方生产域名验证或超出 pilot scope 的外部应用权限。

## PR Slices

```text
PR1 tenant-bound app registration and service account binding - complete
PR2 domain verification before origin allowlist - complete
PR3 quota / rate limit policy and denial evidence - complete
PR4 offboarding revoke for credentials / origins / sessions / grants - complete
PR5 SDK compatibility guard and no direct internal runtime route evidence - complete
```

## Architecture Delta

```text
External App Admin
 -> ExternalAppRegistration
 -> DomainVerificationDecision
 -> OriginAllowlistDecision
 -> QuotaDecision
 -> Credential / Provider boundary
 -> Audit Export / Evidence Chain
```

External app access cannot bypass tenant, credential, quota, origin or human authorization boundary.

## Acceptance Gates

- 未验证 domain 不能加入 origin allowlist。
- wrong tenant app access denied。
- quota / rate limit denial 可审计。
- offboarding 后 app credentials、origin allowlist、active sessions、pending capability grants 被撤销。
- Browser SDK 不直连内部 runtime routes。
- approved API 仍需 tenant-bound API client、service account binding 和 human_authorization_ref。
- external app 不能绕过 V6-4 controlled executor 或 V6-5 Agent intent handoff boundary。

## PRD Spec Review Checklist / No False Green

```text
Does app registration stay tenant / workspace / app bound?
Does domain verification happen before origin allowlist?
Does offboarding revoke access, credentials, sessions and pending grants?
Does SDK compatibility avoid direct browser /v1/rpc and internal runtime routes?
Does V6-6 avoid claiming production-ready external app support?
```

## Architecture Change Checklist

```text
Add External App Onboarding Plane implementation slice.
Reuse V6-1 identity / tenant refs.
Reuse V6-2 credential refs, not raw secrets.
Reuse V6-3 audit export / incident timeline refs.
Route execution through approved API / product console boundaries only.
Do not create runtime truth from admin UI or SDK metadata.
```

## Focused Tests

```text
tests/test_v6_6_external_app_onboarding.py
scripts/v6_6_external_app_onboarding_evidence.py
```

## Completion Evidence

```text
docs/design/V6.x/v6_6_external_app_onboarding_completion_note.md
docs/design/V6.x/evidence/v6-6-external-app-onboarding/index.html
docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json
docs/design/V6.x/evidence/v6-6-external-app-onboarding/result-summary.md
docs/design/V6.x/evidence/v6-6-external-app-onboarding/claims-scan.md
docs/design/V6.x/evidence/v6-6-external-app-onboarding/raw/runtime-results.json
```

Required named cases:

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

## Evidence Package

```text
docs/design/V6.x/evidence/v6-6-external-app-onboarding/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  raw/
```

## Stop Conditions

- external app 绕过 tenant / credential / quota / origin boundary。
- SDK 直连内部 runtime。
- offboarding 只更新 UI，不撤销 access。
- Forbidden claim scan 失败。
