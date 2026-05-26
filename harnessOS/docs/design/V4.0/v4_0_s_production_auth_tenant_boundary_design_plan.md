# V4.0-S Production Auth / Tenant Boundary Follow-up Design Plan

文档状态：V4.0-S implemented as design gate. 本阶段只做 production auth / tenant boundary follow-up design，不实现 production auth、OAuth、SSO、OIDC、SAML、login callback、tenant control plane、production onboarding、token rotate/revoke、Agent executor 或 controlled executor。

## 1. Stage Claim

允许完成声明：

```text
V4.0-S complete: production auth and tenant boundary follow-up design ready for review.
```

禁止完成声明：

```text
production-ready external app support
enterprise auth ready
multi-tenant control plane ready
OAuth ready
SSO ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
complete Workflow Studio ready
complete AgentTalkWindow ready
full low-code canvas editing ready
```

## 2. Implementation Summary

V4.0-S 将 V4.0-R gap register 中的 auth / tenant boundary 方向细化为机器可读设计合同、claim guard、route scan、identity matrix、tenant isolation matrix、service account / agent identity design、OAuth / SSO gap contract 和 capability token binding design。

本阶段不新增可调用 production route，不改变 V3.6 runtime contract，不把 tenant/auth 设计写入 WorkflowTemplate / WorkflowDraft / WorkflowVersion / StationRun。

## 3. PR Slices

| Slice | Scope | Result |
| --- | --- | --- |
| S-PR1 Production Auth Boundary Matrix | 定义 identity field metadata：source_of_truth、trusted_source、client_supplied_allowed、server_bound_required、token_claim_allowed、audit_required、current_status、production_gap、risk_level、blocking_for_production。 | `v4_0_s_production_auth_tenant_boundary_design_contract.json` |
| S-PR2 Tenant Isolation Design Gate | 定义 tenant -> app -> project -> workspace -> instance -> resource ownership chain 和 cross-tenant / cross-scope denial rules。 | tenant isolation matrix |
| S-PR3 Service Account and Agent Identity Design | 定义 future service account lifecycle、agent binding、actor_type policy；agent_id 不等于 executor identity。 | service account / agent identity design |
| S-PR4 OAuth / SSO Gap Contract | 登记 IdP registration、OIDC discovery、SAML metadata、JWKS、callback、tenant mapping、provisioning 等 gap。 | gap_only / planned_future only |
| S-PR5 Capability Token Binding Design | 细化 origin/audience/tenant/workspace/actor/capability/expiration/rotation/revocation/emergency revoke/audit binding。 | no user confirmation bypass |
| S-PR6 Runtime Boundary and Route Scan | 扫描 BFF/frontend，确认无 OAuth/SSO/OIDC/SAML/callback/tenant/token lifecycle route。 | tests |
| S-PR7 Documentation Sync | 同步 README、gap、drawio、audit、UI/event/contract map 和 target architecture。 | docs |

## 4. Risk Controls

- Design-only guard：不新增 `/oauth/*`、`/sso/*`、`/oidc/*`、`/saml/*`、`/login/callback`、`/tenant/*`、`/admin/tenant/*`、`/token/rotate` 或 `/token/revoke`。
- Agent boundary：`source=agent` 仍只能 propose / handoff / explain / navigate，不能执行 mutation。
- Capability token boundary：capability token 不能绕过 user confirmation；`executor.*` 仍 inactive。
- Runtime boundary：tenant/auth design 不写入 V3.6 runtime contract 或 workflow runtime objects。
- Event truth：EventBridge 只触发 refresh，不构造 auth、tenant、token 或 executor truth。
- No False Green：claim guard 阻止 enterprise auth、multi-tenant、OAuth、SSO、production ready 等过度声明。

## 5. Tests

新增：

```text
tests/test_v4_0_production_auth_tenant_boundary_design.py
tests/test_v4_0_production_tenant_isolation_design.py
tests/test_v4_0_production_identity_matrix.py
tests/test_v4_0_production_oauth_sso_gap_contract.py
tests/test_v4_0_production_capability_token_binding_design.py
tests/test_v4_0_production_auth_claim_guard.py
apps/workflow-console/src/__tests__/productionAuthTenantBoundaryDesign.test.tsx
apps/workflow-console/src/__tests__/productionAuthNoFalseGreen.test.tsx
```

Required validation：

```text
auth tenant design contract exists
every identity field has required metadata
every identity field has blocking_for_production
tenant isolation matrix covers ownership boundaries
tenant isolation matrix includes cross-tenant denied
OAuth / SSO remain gaps only
no OAuth / SSO / OIDC / SAML / callback route
no tenant admin route
no token rotate/revoke route
source=agent still cannot execute mutation
capability token cannot bypass user confirmation
executor.* remains inactive
secret redaction still passes
claim guard blocks enterprise auth / multi-tenant / OAuth / SSO ready claims
V3.6 workflow contract is not modified to include production tenant control plane fields
```
