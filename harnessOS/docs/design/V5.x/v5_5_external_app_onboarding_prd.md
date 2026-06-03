# V5-5 Production External App Onboarding PRD

文档状态：V5-5 core slice implemented for review。

## Stage Goal

V5-5 规划生产外部应用接入边界：

```text
app registration
domain verification
origin allowlist
quota / rate limit
customer offboarding
SDK compatibility policy
```

## Acceptance Criteria

```text
app registration is tenant-bound
domain verification is required before production origin allowlist
origin allowlist blocks unknown origins
quota / rate limit denial is auditable
offboarding revokes app access
SDK compatibility policy is versioned
```

## No False Green

No False Green：V5-5 不证明 production-ready external app support，直到完整接入、隔离、凭证、审计、限流和 offboarding 全部验收通过。

## Current Implementation Scope

```text
Implemented:
- in-memory ExternalAppOnboardingRegistry
- tenant-bound app registration
- domain verification record
- origin allowlist guard requiring verified domain
- quota/rate-limit denial evidence
- customer offboarding access revocation
- SDK compatibility browser route guard

Not implemented:
- production onboarding routes
- production credential issuance
- production domain DNS verification
- production customer onboarding flow
- production external app support
```
