# V5-2 Provider Profile Model

文档状态：V5-2 implementation planning。

## 1. ProviderProfileDTO

```json
{
  "provider_profile_id": "provider_profile_001",
  "tenant_id": "tenant_001",
  "workspace_id": "workspace_001",
  "project_id": "project_001",
  "app_id": "app_001",
  "provider": "minimax",
  "provider_kind": "llm",
  "base_url_ref": "provider_base_url_ref",
  "model_refs": ["model_ref"],
  "credential_ref_id": "credential_ref_001",
  "capability_refs": ["llm.chat", "llm.summarize"],
  "status": "active",
  "created_at": "2026-05-31T00:00:00Z",
  "created_by": "actor_001",
  "updated_at": "2026-05-31T00:00:00Z"
}
```

## 2. Required Fields

```text
provider_profile_id
tenant_id
workspace_id
project_id
app_id
provider
provider_kind
model_refs
credential_ref_id
capability_refs
status
created_at
created_by
updated_at
```

## 3. Status Values

```text
draft
active
suspended
revoked
rotation_required
validation_failed
```

## 4. Forbidden Fields

No False Green：ProviderProfileDTO 禁止包含：

```text
API key
capability_token
subscription_token
Authorization
Bearer
secret
raw prompt
raw_trace_payload
raw_artifact_content
raw_connector_payload
upstream signed URL
```

## 5. Acceptance Rules

```text
unknown fields rejected
provider profile must be tenant/workspace/app bound
credential_ref_id must not be raw secret
model_ref cannot bypass credential policy
source=agent cannot mutate provider profile
```

