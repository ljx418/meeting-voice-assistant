# V6-2 Credential / Provider Lifecycle PRD

文档状态：V6-2 implementation-ready PRD。

## Current Baseline

```text
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 implementation may start only after this PRD, architecture delta, lease model, audit fields, test matrix, and pre-implementation audit pass.
```

## Goal

V6-2 的目标是把 V5-2 core credential/provider lifecycle slice 升级为生产试点级凭证与 provider 生命周期切片：

```text
tenant-bound provider profile
credential reference without raw secret
credential lease bound to tenant/app/audience/operation
rotation / revocation / emergency revoke evidence
provider invocation evidence with redacted refs only
revoked / expired / wrong-operation lease denial
```

## User Experience

```text
管理员在租户范围内配置 provider profile
 -> 用户确认后创建 credential reference
 -> 系统签发 operation-bound CredentialLease
 -> provider smoke / invocation 使用 lease 和 redacted refs
 -> revoked / expired / wrong-scope credential 被拒绝
 -> Evidence Chain 记录 provider/model/credential_ref/lease_ref，不记录 raw secret 或 raw prompt
```

## Required Fields

```text
provider_profile_id
credential_ref_id
credential_lease_id
tenant_id
workspace_id
project_id
app_id
provider
model_ref
capability_ref
audience
operation
secret_ref
lease_status
expires_at
provider_config_source
redaction_status
request_id
correlation_id
```

## Non-Goals

```text
production secret lifecycle ready
production managed secret store ready
production-ready external app support
Agent executor ready
production controlled executor ready
```

## Acceptance

V6-2 PASS 需要：

```text
CredentialLease is tenant-bound
CredentialLease is app-bound
CredentialLease is audience-bound
CredentialLease is operation-bound
revoked credential invocation denied
expired lease denied
wrong operation lease denied
wrong audience lease denied
provider/model/capability mismatch denied
emergency revoke blocks invocation
provider invocation evidence contains redacted provider/model/credential/lease refs
no raw secret / raw prompt / raw connector payload leakage
No False Green scan PASS
```

## Allowed Claim

```text
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
```

## No False Green

V6-2 不证明 production secret lifecycle ready、production managed secret store ready、Agent executor ready、production controlled executor ready 或 production-ready external app support。
