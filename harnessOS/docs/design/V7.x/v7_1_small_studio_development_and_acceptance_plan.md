# V7-1 Small Studio Development And Acceptance Plan

文档状态：V7-1 complete / ready for review。

## Entry Gate

V7-1 进入 implementation 前必须满足：

```text
V7-0 accepted
v7_1_pre_implementation_review.md accepted
StudioContext.schema.json accepted
StudioInventory.schema.json accepted
WorkspaceInventory.schema.json accepted
ProjectInventory.schema.json accepted
AppInventory.schema.json accepted
StudioRoleBinding.schema.json accepted
ProviderProfileProjection.schema.json accepted
CredentialRefProjection.schema.json accepted
QuotaStatusProjection.schema.json accepted
AuditSourceRefProjection.schema.json accepted
```

当前 V7-0 与 V7-1 pre-implementation review 均已完成本地审计。V7-1 Small Studio repo-backed fixture implementation 已完成，但不得扩展到 runtime execution、Mission TUI 或 full production GA。

## Runtime Truth Boundary

```text
Small Studio Control Plane is product aggregation plane.
It must not write WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun / Artifact.
It must not expose raw credential material.
```

## PR Slices

```text
PR1 StudioContext and inventory DTOs
PR2 Provider profile and credential ref projection
PR3 Role / permission / quota projection
PR4 Studio audit source refs
PR5 Evidence package and HTML review page
```

## Scope Guard

```text
V7-1 is product aggregation only.
V7-1 must not write runtime truth.
V7-1 must not expose raw credential material.
V7-1 must not claim enterprise auth ready.
V7-1 must not claim production-ready external app support.
```

## Acceptance Tests

```text
studio_context_contains_tenant_workspace_project_app_refs
provider_profile_projection_redacts_secret
credential_ref_projection_no_raw_secret
role_binding_projection_auditable
quota_denial_explainable
cross_workspace_access_denied
studio_control_plane_does_not_construct_runtime_truth
```

## Evidence Package

```text
docs/design/V7.x/evidence/v7-1-small-studio/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  redaction-scan.md
  raw/studio-context.json
  raw/provider-profiles.json
  raw/credential-refs.json
  raw/quota-decisions.json
```

## Validation

```text
./.venv/bin/python -m pytest tests/test_v7_1_*.py -q
./.venv/bin/python -m pytest tests/test_v6_*.py -q
xmllint --noout docs/design/V7.x/v7_current_gap_analysis.drawio
```
