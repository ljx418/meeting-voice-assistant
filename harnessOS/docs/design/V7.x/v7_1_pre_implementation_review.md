# V7-1 Pre-Implementation Review

文档状态：V7-1 pre-implementation review / no runtime coding yet。

## 1. Current Stage

```text
previous_stage: V7-0 complete / ready for review
current_stage: V7-1 pre-implementation PRD/spec review
implementation_allowed: true_after_this_review_passes
runtime_code_started: false
```

## 2. PRD Spec Review

V7-1 must implement only:

```text
Small Studio production pilot control plane
StudioContext and inventory projections
provider profile projection
credential ref projection
role binding projection
quota status projection
audit source ref projection
HTML evidence review page
```

V7-1 must not implement:

```text
full production GA
enterprise auth ready
multi-tenant control plane ready
production-ready external app support
workflow runtime execution
Mission TUI runtime
natural-language workflow run
Agent executor
production controlled executor
complete Workflow Studio
```

## 3. Architecture Delta Review

V7-1 adds:

```text
Small Studio Context Resolver
Studio Inventory Projection
Provider / Credential / Quota / Role / Audit read models
Studio evidence package generator
```

V7-1 reads from existing V6 evidence and repo-backed fixtures. It does not write:

```text
WorkflowDraft
WorkflowVersion
WorkflowInstance
StationRun
Artifact
```

## 4. Implementation Slices

```text
PR1 Studio projection data model and fixture builder
PR2 Provider and credential redacted projections
PR3 Role, quota and audit source projections
PR4 Cross-workspace denial evidence
PR5 HTML evidence package and acceptance data
```

## 5. Acceptance Criteria

```text
studio_context_contains_tenant_workspace_project_app_refs
studio_inventory_contains_counts
workspace_project_app_inventory_refs_exist
provider_profile_projection_redacts_secret
credential_ref_projection_no_raw_secret
role_binding_projection_auditable
quota_denial_explainable
cross_workspace_access_denied
studio_control_plane_does_not_construct_runtime_truth
no_false_green_claim_scan_passes
redaction_scan_passes
```

## 6. Required Evidence

```text
docs/design/V7.x/evidence/v7-1-small-studio/index.html
docs/design/V7.x/evidence/v7-1-small-studio/acceptance-data.json
docs/design/V7.x/evidence/v7-1-small-studio/result-summary.md
docs/design/V7.x/evidence/v7-1-small-studio/claims-scan.md
docs/design/V7.x/evidence/v7-1-small-studio/redaction-scan.md
docs/design/V7.x/evidence/v7-1-small-studio/raw/studio-context.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/studio-inventory.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/workspace-inventory.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/project-inventory.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/app-inventory.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/provider-profiles.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/credential-refs.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/role-bindings.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/quota-decisions.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/audit-source-refs.json
docs/design/V7.x/evidence/v7-1-small-studio/raw/cross-workspace-denial.json
```

## 7. Test Plan

```text
./.venv/bin/python -m pytest tests/test_v7_1_small_studio.py -q
./.venv/bin/python -m pytest tests/test_v7_0_planning_hardening.py -q
./.venv/bin/python -m pytest tests/test_v6_9_final_acceptance.py -q
xmllint --noout docs/design/V7.x/v7_current_gap_analysis.drawio
```

## 8. PRD Drift Evaluation

```text
LOW
```

The V7-1 plan stays within Small Studio product aggregation and does not expand into runtime execution or enterprise GA.

## 9. False Green Evaluation

```text
LOW
```

V7-1 will use `repo_backed_fixture` evidence scope and must not claim full production GA or production-ready external app support.

## 10. Proceed Decision

```text
proceed_to_v7_1_implementation
```

V7-1 implementation may start after this review because no critical or major PRD drift was found.
