# V5-1 Target Architecture Delta

文档状态：V5-1 pre-implementation planning。本文描述 V5-1 相对 V5 target architecture 的架构增量，不实现 runtime。

## 1. Architecture Delta

V5-1 引入 Identity And Tenant Boundary，作为所有 production BFF/API 操作的前置上下文。

新增 logical components：

```text
IdentityContextResolver
TenantScopeGuard
OwnershipResolver
ActorBindingValidator
ServiceAccountBindingValidator
TenantAuditContextBuilder
```

## 2. Request Flow

目标请求流：

```text
request enters BFF/API
 -> IdentityContextResolver resolves server-bound identity
 -> TenantScopeGuard checks tenant / workspace / project / app scope
 -> OwnershipResolver checks target resource ownership
 -> ActorBindingValidator checks human / service_account / agent session binding
 -> route handler executes only after guard pass
 -> TenantAuditContextBuilder writes audit refs
```

## 3. Runtime Truth Boundary

V5-1 不把 tenant control plane 写入 V4/V3.6 runtime objects：

```text
WorkflowSpec remains spec/read model boundary.
WorkflowDraft / WorkflowVersion remain runtime truth where applicable.
Tenant identity is an access boundary, not canvas/runtime truth.
Drawio / HTML Report / Evidence Chain remain read-only projections.
EventBridge still triggers refresh only.
```

## 4. Server-Bound Identity Requirement

Production identity must be server-bound. Client-supplied IDs may only be selectors and must be verified against server-resolved identity context.

Required behavior:

```text
client tenant_id alone is not trusted
client workspace_id alone is not trusted
client actor_id alone is not trusted
token claims require server verification
service account scope requires server-side binding lookup
agent_id / agent_session_id cannot become executor identity
```

## 5. No False Green

No False Green：本文不证明 enterprise auth ready、多租户控制台已完成、Agent executor ready、production controlled executor ready 或 production-ready external app support。
