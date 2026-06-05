# V6-8 Product Console And Workflow Studio Gate Development And Acceptance Plan

文档状态：V6-8 complete / ready for review。本文定义开发与验收门槛，并链接实现证据。

## Allowed Claim

```text
V6-8 complete: product console pilot slice ready for review.
```

## Goal

产品化 Product Console / Thin Web Console：Runtime Report、Evidence Review、Audit Export、External App Admin、Manual Confirmation UX、Review Console handoff。

## Non-Goals

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
full low-code canvas editing ready
```

## Development Scope

- Runtime Report：只读展示 runtime state、attempt、artifact、quality。
- Evidence Review：只读展示 evidence chain。
- Audit Export Access：只读下载或打开 export package。
- External App Admin：管理 app onboarding 状态，但不构造 runtime truth。
- Manual Confirmation UX：记录 human_authorization_ref。
- Full Studio Gate：完整 Workflow Studio 必须走单独 PRD。
- Product Console Admin Ops：只能管理观察、确认、接入和审计入口，不能构造 runtime truth。

Expanded UI / BFF / browser safety plan:

```text
v6_8_ui_bff_browser_safety_plan.md
v6_8_product_console_bff_contract.md
v6_8_browser_safety_test_matrix.md
v6_8_manual_confirmation_ux_contract.md
```

## PR Slices

```text
PR1 Runtime Report read-only product console view
PR2 Evidence Review read-only view
PR3 Audit Export access view
PR4 External App Admin view without runtime truth writes
PR5 Manual Confirmation UX with human_authorization_ref
PR6 Full Workflow Studio separate PRD gate notice
```

## Architecture Delta

```text
Product Console
 -> Runtime Report read model
 -> Evidence Review read model
 -> Audit Export read model
 -> External App Admin read model
 -> Manual Confirmation UX
 -> Review Console handoff
```

Product Console can create confirmation / handoff evidence but cannot construct runtime truth directly.

## Acceptance Gates

- Runtime Report 只读，不含 hidden mutation form。
- Evidence Review 和 Runtime Report 均保持只读。
- Evidence Review 不出现 Apply / Publish / Approve / Reject / Execute / Run 执行按钮。
- Manual confirmation 记录 actor、operation、target_refs、human_authorization_ref。
- Browser 不直连内部 runtime routes。
- UI 不出现自动应用、自动发布、Agent 已执行、Agent 已发布。

## Focused Tests

```text
tests/test_v6_8_runtime_report_readonly.py
tests/test_v6_8_evidence_review_readonly.py
tests/test_v6_8_audit_export_access.py
tests/test_v6_8_manual_confirmation_ux.py
tests/test_v6_8_browser_route_guard.py
tests/test_v6_8_no_false_green.py
```

Required named cases:

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

## Evidence Package

```text
docs/design/V6.x/evidence/v6-8-product-console/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  screenshots/
  raw/
```

## Completion Evidence

```text
core/product_console/v6_8_product_console.py
tests/test_v6_8_product_console.py
scripts/v6_8_product_console_evidence.py
docs/design/V6.x/v6_8_product_console_completion_note.md
docs/design/V6.x/evidence/v6-8-product-console/acceptance-data.json
```

Current result:

```text
status: PASS
evidence_scope: repo_backed_product_console_projection
claim_violations: 0
redaction_status: PASS
```

## Stop Conditions

- Product Console admin ops 变成 runtime truth。
- Evidence Review 变成执行面板。
- Full Web Studio 被当作 V6 默认前提。
- Forbidden claim scan 失败。
