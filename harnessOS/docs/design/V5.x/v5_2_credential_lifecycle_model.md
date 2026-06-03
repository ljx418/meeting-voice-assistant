# V5-2 Credential Lifecycle Model

文档状态：V5-2 implementation planning。

## 1. CredentialReferenceDTO

```json
{
  "credential_ref_id": "credential_ref_001",
  "tenant_id": "tenant_001",
  "workspace_id": "workspace_001",
  "app_id": "app_001",
  "provider_profile_id": "provider_profile_001",
  "secret_ref": "secret_store_ref_only",
  "status": "active",
  "issued_at": "2026-05-31T00:00:00Z",
  "expires_at": "2026-08-31T00:00:00Z",
  "last_rotated_at": null,
  "revoked_at": null,
  "created_by": "actor_001"
}
```

## 2. Lifecycle Events

```text
credential.issue
credential.validate
credential.rotate.request
credential.rotate.complete
credential.revoke.request
credential.revoke.complete
credential.emergency_revoke
credential.suspend
credential.resume
```

## 3. Required Guard

```text
all lifecycle mutation requires user_confirmed=true or admin-confirmed policy
source=agent cannot issue / rotate / revoke / reveal credential
cross-tenant lifecycle action denied
wrong workspace / app lifecycle action denied
credential secret never returned to browser, report, evidence, or error response
```

## 4. Audit Fields

```text
credential_event_id
credential_ref_id
provider_profile_id
operation
tenant_id
workspace_id
app_id
actor_type
actor_id
source
user_confirmed
policy_decision
risk_flags
request_id
correlation_id
redaction_status
created_at
```

## 5. No False Green

No False Green：V5-2 credential lifecycle 不是完整生产密钥管理平台，也不证明：

```text
enterprise auth ready
multi-tenant control plane ready
production-ready external app support
Agent executor ready
controlled executor ready
```

