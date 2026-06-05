# V6-8 UI / BFF / Browser Safety Plan

文档状态：V6-8 complete / ready for review。本文定义 Product Console / Thin Web Console 的 UI、BFF、browser safety 和 read-only 验收矩阵，并由 V6-8 evidence package 验证。

## Current Decision

```text
V6-8 status: complete / ready for review.
Implementation evidence exists under docs/design/V6.x/evidence/v6-8-product-console/.
```

## Default Scope

V6-8 默认产品化 Product Console / Thin Web Console。

Full Workflow Studio requires:

```text
separate PRD
separate architecture
separate acceptance matrix
separate No False Green gate
```

## BFF Route Allowlist

Allowed browser-facing BFF routes must be explicit and purpose-bound:

```text
GET /bff/v6/runtime-report
GET /bff/v6/evidence-review
GET /bff/v6/audit-export
GET /bff/v6/external-app-admin
POST /bff/v6/manual-confirmation
```

Browser must not call internal runtime routes directly.

## Browser Network Denylist

```text
/v1/rpc
/v1/events/subscribe
/v1/internal/runtime
/v1/internal/executor
/v1/internal/workflow-store
/v1/internal/station-run
```

## Read-Only Panel Schema

Read-only panels:

```text
Runtime Report
Evidence Review
Audit Export Access
External App Admin status view
```

Read-only panels must not include hidden mutation forms, execution buttons, or hidden POST routes.

## Manual Confirmation DTO

Required fields:

```text
human_authorization_ref
tenant_id
workspace_id
app_id
actor_id
operation
target_refs
policy_decision
created_at
correlation_id
audit_ref
```

Manual confirmation can create confirmation / handoff evidence. It cannot construct runtime truth directly.

## External App Admin Boundary

External App Admin may show and request changes to app onboarding state through approved BFF routes. It must not directly write WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun, Artifact, QualityEvaluation, or Evidence runtime truth.

## Required Tests

```text
runtime_report_readonly_no_hidden_form
evidence_review_readonly_no_execute_buttons
audit_export_access_requires_authorized_view
external_app_admin_does_not_construct_runtime_truth
manual_confirmation_records_human_authorization_ref
browser_no_direct_internal_runtime_routes
browser_no_direct_v1_rpc
browser_no_direct_v1_events_subscribe
ui_no_auto_apply_auto_publish_agent_executed_copy
```

## UI Copy False Green Scan

Forbidden UI copy:

```text
自动应用
自动发布
Agent 已执行
Agent 已发布
生产可用
完整工作流工作台已完成
```
