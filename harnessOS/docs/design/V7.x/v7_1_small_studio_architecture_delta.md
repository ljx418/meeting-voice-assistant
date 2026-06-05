# V7-1 Small Studio Architecture Delta

文档状态：V7 planning package / architecture delta。

## Baseline

V7-1 inherits from V6:

```text
Identity And Tenant Control Plane
Credential And Provider Lifecycle Plane
Observability And Audit Export Plane
External App Onboarding Plane
Product Console Plane
```

## Delta

V7-1 adds a product-level aggregation layer:

```text
Small Studio Control Plane
```

It collects existing refs into a studio-scoped read model:

```text
tenant_id
studio_id
workspace_id
project_id
app_id
provider_profile_id
credential_ref
role_binding_id
quota_policy_ref
audit_ref
```

## Data Flow

```text
V6 identity / credential / quota / audit evidence
 -> Small Studio Context Resolver
 -> Studio Inventory Projection
 -> Product Console / TUI display
```

## Boundaries

```text
Small Studio Control Plane is a product aggregation plane.
It does not directly write WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun or Artifact records.
It may create user-confirmed handoff evidence.
It must not expose raw credential material.
```

