# V6-2 Production Credential And Provider Lifecycle Development And Acceptance Plan

文档状态：V6-2 implementation-ready plan。V6-2 detailed PRD、架构增量、CredentialLease model、audit fields、test matrix 和 pre-implementation audit 已补齐。本文定义 V6-2 最小实现和验收门槛。

## Allowed Claim

```text
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
```

## Goal

把 V5 provider / credential core slice 推进为生产试点级凭证生命周期：credential reference、lease、rotation、revocation、emergency revoke、provider invocation evidence 和 redaction。

## Non-Goals

```text
production secret lifecycle ready
production-ready external app support
Agent executor ready
```

## Development Scope

- ProviderProfile：记录 provider、model allowlist、capability allowlist、tenant/workspace/app binding。
- CredentialReference：只保存 secret_ref，不保存 raw secret。
- CredentialLease：记录 lease_id、tenant_id、app_id、audience、operation、expires_at、origin、scope；必须 tenant-bound、app-bound、audience-bound、operation-bound。
- CredentialLifecycleEvent：记录 issue、rotate、revoke、emergency_revoke。
- ProviderInvocationEvidence：记录 provider、model_ref、provider_config_source、credential_ref、redaction_status。

## Acceptance Gates

- raw secret 不出现在日志、HTML、JSON、evidence、prompt。
- revoked credential invocation denied。
- expired lease denied。
- provider/model/capability mismatch denied。
- emergency revoke 立即阻断。
- provider invocation evidence 只含 redacted refs。
- provider invocation evidence 不记录 raw secret / raw prompt / raw connector payload。

## Evidence Package

```text
docs/design/V6.x/evidence/v6-2-credential-provider/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  raw/
```

## Stop Conditions

- raw secret、Authorization、Bearer、capability_token、subscription_token 泄露。
- credential rotation / revocation 只有文档没有 evidence。
- provider fallback 被写成 real provider PASS。
- Forbidden claim scan 失败。

## Detailed Control Documents

```text
docs/design/V6.x/v6_2_credential_provider_prd.md
docs/design/V6.x/v6_2_credential_provider_architecture_delta.md
docs/design/V6.x/v6_2_credential_lease_model.md
docs/design/V6.x/v6_2_audit_fields.md
docs/design/V6.x/v6_2_test_matrix.md
docs/design/V6.x/v6_2_pre_implementation_audit.md
```
