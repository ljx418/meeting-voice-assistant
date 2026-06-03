# V5-2 API / BFF Route Design

文档状态：V5-2 implementation planning。本文只定义 route design，不新增实际路由。

## 1. Proposed Routes

```text
GET    /bff/v5/provider-profiles
POST   /bff/v5/provider-profiles
GET    /bff/v5/provider-profiles/{provider_profile_id}
PATCH  /bff/v5/provider-profiles/{provider_profile_id}
POST   /bff/v5/provider-profiles/{provider_profile_id}/validate
POST   /bff/v5/credentials/{credential_ref_id}/rotate
POST   /bff/v5/credentials/{credential_ref_id}/revoke
POST   /bff/v5/credentials/{credential_ref_id}/emergency-revoke
GET    /bff/v5/provider-invocation-evidence/{evidence_id}
```

## 2. Required Request Guard

```text
server-bound IdentityContext required
tenant/workspace/project/app ownership validation required
source=agent denied for credential mutation
user_confirmed=true required for create/update/rotate/revoke/emergency-revoke
all responses redacted
```

## 3. Forbidden Route Behavior

```text
no route returns raw secret
no route returns Authorization header
no route returns Bearer token
no route returns raw prompt
no route returns raw file content
no route allows browser direct /v1/rpc credential mutation
no route allows event payload to construct credential truth
```

## 4. Stable Error Codes

```text
CREDENTIAL_SCOPE_DENIED
CREDENTIAL_USER_CONFIRMATION_REQUIRED
CREDENTIAL_AGENT_MUTATION_DENIED
CREDENTIAL_SECRET_REDACTED
PROVIDER_PROFILE_NOT_FOUND
PROVIDER_PROFILE_INVALID
PROVIDER_VALIDATION_FAILED
PROVIDER_CAPABILITY_DENIED
```

## 5. Implementation Gate

Do not implement these routes until this V5-2 planning package passes review.

