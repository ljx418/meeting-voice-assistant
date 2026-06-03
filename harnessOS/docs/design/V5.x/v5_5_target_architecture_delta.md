# V5-5 Target Architecture Delta

文档状态：V5-5 core slice implemented for review。

## Logical Components

```text
ExternalAppRegistry
DomainVerificationService
OriginAllowlistGuard
QuotaRateLimitService
SDKCompatibilityPolicy
CustomerOffboardingService
ExternalAppEvidenceRecorder
```

## Boundary

```text
external app cannot bypass tenant boundary
external app cannot receive raw secrets
external app cannot access /v1/rpc directly from browser
external app cannot mutate runtime without policy and confirmation
```

## Implemented Core Slice

```text
core/apps/external_onboarding.py
 -> ExternalAppOnboardingRegistry
 -> DomainVerification
 -> OriginAllowlistEntry
 -> QuotaDecision
 -> OffboardingRecord
 -> SDKCompatibilityPolicy
```

The implementation is in-memory and focused on boundary validation. It does not add production routes or issue credentials.
