# V6-1 Identity / Tenant Architecture Delta

文档状态：V6-1 implementation-ready architecture delta。

## Delta Summary

V6-1 在 V5-1 core guard 上增加生产试点审计语义：

```text
V5-1 core guard
 -> V6-1 ProductionIdentityContext
 -> StagingIdentityProviderStatus
 -> ServiceAccountScopeAudit
 -> WorkflowHeadIdentityProjection
 -> V6-1 evidence package
```

## Components

```text
ProductionIdentityContext
TenantOwnershipChain
TenantScopeGuard
ServiceAccountScopePolicy
StagingIdentityProviderStatus
WorkflowHeadIdentityProjection
TenantAuditActorRef
```

## Data Flow

```text
BFF / Console request
 -> server-bound identity context
 -> client selector conflict check
 -> tenant/workspace/project/app ownership check
 -> service account allowed operation check
 -> source=agent durable mutation denial
 -> workflow head identity projection
 -> redacted audit evidence
```

## Runtime Truth Boundary

Identity context is an access and audit boundary. It does not write WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun, WorkflowSpec Registry runtime truth, Runtime Report truth, or Evidence Chain truth.

## Staging IdP Boundary

If no real staging IdP / OIDC provider is configured, V6-1 records:

```text
identity_provider_status=staging_only
evidence_scope=staging_fixture
enterprise_auth_ready=false
```

This is acceptable for V6-1 pilot slice review but cannot be claimed as enterprise auth ready.
