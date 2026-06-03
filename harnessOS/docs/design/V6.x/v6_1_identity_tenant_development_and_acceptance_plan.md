# V6-1 Production Identity And Tenant Control Plane Development And Acceptance Plan

文档状态：V6-1 implementation-ready plan。V6-1 detailed PRD、架构增量、ownership model、route design、audit fields、test matrix 和 pre-implementation audit 已补齐。本文定义 V6-1 最小实现和验收门槛。

## Allowed Claim

```text
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
```

## Goal

建立生产试点级身份与租户边界，使 Mission Console、WorkflowSpec Registry、Runtime Report、Review Console、Evidence Chain 在 tenant / workspace / project / app / service account 范围内可审计。

## Non-Goals

```text
enterprise auth ready
multi-tenant control plane ready
production-ready external app support
complete Workflow Studio ready
```

## Development Scope

- ProductionIdentityContext：记录 tenant_id、workspace_id、project_id、app_id、user_id、actor_type、actor_id、service_account_id。
- TenantOwnershipChain：定义 tenant -> app -> project -> workspace -> workflow_instance -> resource。
- TenantScopeGuard：拒绝 cross-tenant、wrong-workspace、wrong-resource、wrong-service-account。
- TenantAuditActorRef：把 actor、tenant、workspace、project、app、request_id、correlation_id 写入审计证据。
- StagingIdentityProviderStatus：记录 staging IdP / OIDC 是否真实接入；未真实接入必须标记 BLOCKED 或 staging_only。
- ServiceAccountScopeAudit：记录 service_account_id、tenant_id、workspace_id、app_id、allowed_operations、denial_reason。
- WorkflowHeadIdentityProjection：把 identity refs 投影到 Mission Console、Workflow Blueprint、Runtime Report、Review Console、Evidence Chain 和 WorkflowSpec Registry。

## Acceptance Gates

- cross-tenant denied。
- same-tenant wrong-workspace denied。
- same-workspace wrong-resource denied。
- service account without tenant binding denied。
- service account scope mismatch denied。
- source=agent cannot bypass identity boundary。
- Mission Console / Runtime Report / Review Console / Evidence Chain 均携带 identity source refs。
- tenant / workspace / project / app / user / service_account refs 必须进入 audit evidence。
- 不能把 staging IdP 或 fixture 写成 enterprise auth ready。

## Evidence Package

```text
docs/design/V6.x/evidence/v6-1-identity-tenant/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  raw/
```

## Stop Conditions

- V6-1 文档或实现把 dev/local scope guard 写成 production tenant isolation ready。
- tenant_id / workspace_id / app_id 任一项缺少审计字段。
- source=agent 绕过身份边界。
- Forbidden claim scan 失败。

## Detailed Control Documents

```text
docs/design/V6.x/v6_1_identity_tenant_prd.md
docs/design/V6.x/v6_1_identity_tenant_architecture_delta.md
docs/design/V6.x/v6_1_identity_tenant_ownership_model.md
docs/design/V6.x/v6_1_api_bff_route_design.md
docs/design/V6.x/v6_1_audit_fields.md
docs/design/V6.x/v6_1_test_matrix.md
docs/design/V6.x/v6_1_pre_implementation_audit.md
```
