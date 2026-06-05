# V6-8 Browser Safety Test Matrix

文档状态：V6-8 complete / ready for review。本文定义 UI / browser / BFF 验收矩阵，并已由 V6-8 focused tests 和 evidence package 验证。

## Required Named Cases

| Case | Expected Result |
| --- | --- |
| `runtime_report_readonly_no_hidden_form` | Runtime Report has no hidden mutation form. |
| `evidence_review_readonly_no_execute_buttons` | Evidence Review has no Apply / Publish / Approve / Reject / Execute / Run buttons. |
| `audit_export_access_requires_authorized_view` | Audit export route denies unauthorized view. |
| `external_app_admin_does_not_construct_runtime_truth` | External App Admin does not write WorkflowStore or StationRun truth. |
| `manual_confirmation_records_human_authorization_ref` | Confirmation records actor, operation, target_refs and human_authorization_ref. |
| `browser_no_direct_internal_runtime_routes` | Browser network log has no `/v1/internal/*` runtime calls. |
| `browser_no_direct_v1_rpc` | Browser network log has no `/v1/rpc`. |
| `browser_no_direct_v1_events_subscribe` | Browser network log has no `/v1/events/subscribe`. |
| `ui_no_auto_apply_auto_publish_agent_executed_copy` | UI copy does not claim auto apply, auto publish or Agent executed. |

## Evidence Requirements

```text
network-log.json
screenshots/
dom-scan.json
hidden-form-scan.json
ui-copy-scan.md
claims-scan.md
```

Evidence package:

```text
docs/design/V6.x/evidence/v6-8-product-console/
```

## Full Studio Boundary

Full Workflow Studio remains outside V6-8 default scope. It requires separate PRD, architecture, acceptance matrix and No False Green gate.
