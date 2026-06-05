# V6-8 Product Console BFF Contract

文档状态：V6-8 complete / ready for review。本文定义 Product Console BFF 合同；V6-8 pilot 以 repo-backed projection 验证，不新增生产 BFF route。

## Route Allowlist

```text
GET /bff/v6/runtime-report
GET /bff/v6/evidence-review
GET /bff/v6/audit-export
GET /bff/v6/external-app-admin
POST /bff/v6/manual-confirmation
```

## Browser Denylist

Browser clients must not call:

```text
/v1/rpc
/v1/events/subscribe
/v1/internal/runtime
/v1/internal/executor
/v1/internal/workflow-store
/v1/internal/station-run
```

## BFF Output Principles

- Runtime Report is read-only and uses runtime/evidence/audit refs.
- Evidence Review is read-only and exposes view/export/open_handoff only.
- Audit Export Access requires authorized view decision.
- External App Admin may show app onboarding state and offboarding evidence; it cannot construct runtime truth.
- Manual Confirmation may create human_authorization_ref for allowed operations.

## Forbidden UI / BFF Behavior

```text
hidden mutation form
direct internal runtime route from browser
Evidence Review execution buttons
admin operation writes WorkflowStore directly
source=agent auto apply / auto publish / auto run
```

## Validation Evidence

```text
docs/design/V6.x/evidence/v6-8-product-console/network-log.json
docs/design/V6.x/evidence/v6-8-product-console/raw/route-decisions.json
tests/test_v6_8_product_console.py
```
