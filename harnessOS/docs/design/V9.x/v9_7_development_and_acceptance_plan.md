# V9-7 Development And Acceptance Plan

文档状态：V9-7 detailed development and acceptance plan / implementation complete for review / production governance high-risk gate.

This document records the implemented V9-7 governance/evidence hardening slice. It does not authorize production automation readiness, production browser automation, raw credential access or unrestricted terminal automation.

## 1. Entry Baseline

V9-7 entered implementation only after:

```text
V9-6 Studio boundary evidence PASS.
Production governance engineering design accepted.
Tenant isolation matrix accepted.
Credential lease validator accepted.
Audit export and incident timeline contracts accepted.
Evidence hardening validator accepted.
human high-risk proceed decision recorded for production governance and terminal automation gate.
No False Green scan PASS.
Redaction scan PASS.
```

## 2. Scope

V9-7 hardens governance and evidence boundaries:

```text
tenant isolation decision
credential lease decision
service account binding policy
append-only audit export
incident timeline
evidence hardening report
terminal automation policy
browser automation separate PRD gate
```

V9-7 must not:

```text
claim production automation readiness.
enable production browser automation without separate PRD and human decision.
allow credential use without tenant, app, audience and operation binding.
allow audit export mutation.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-7A Tenant and app scope checks | tenant isolation decisions | wrong tenant/app/workspace denied |
| V9-7B Credential lease validator | credential lease decisions | audience, operation, expiry and revocation checked |
| V9-7C Service account binding | binding decisions | service account cannot become autonomous override |
| V9-7D Audit export hardening | audit export package | append-only, redacted refs only |
| V9-7E Incident timeline | incident events | policy denial, credential denial, timeout and worker loss recorded |
| V9-7F Automation gate dashboard | HTML and acceptance data | reviewer sees governance, evidence and remaining blocked automation |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/governance/tenant_bound_credential_lease_and_audit_export.json
```

Negative fixtures:

```text
fixtures/governance/wrong_tenant_credential_lease.json
fixtures/governance/wrong_operation_credential_lease.json
fixtures/governance/expired_credential_lease.json
fixtures/governance/revoked_credential_lease.json
fixtures/governance/audit_export_mutation_attempt.json
fixtures/governance/browser_automation_without_separate_prd.json
```

## 5. Acceptance Tests

```text
v9_7_tenant_isolation_wrong_tenant_denied
v9_7_credential_lease_wrong_operation_denied
v9_7_credential_lease_expired_denied
v9_7_credential_lease_revoked_denied
v9_7_audit_export_append_only
v9_7_incident_timeline_records_policy_denial
v9_7_incident_timeline_records_credential_denial
v9_7_evidence_hardening_scan_pass
v9_7_browser_automation_blocked_without_separate_prd
v9_7_claim_scan_pass
v9_7_redaction_scan_pass
```

## 6. Evidence Package

V9-7 completion evidence includes:

```text
docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json
docs/design/V9.x/evidence/v9-7-production-governance/index.html
docs/design/V9.x/evidence/v9-7-production-governance/result-summary.md
docs/design/V9.x/evidence/v9-7-production-governance/tenant-isolation-decisions.json
docs/design/V9.x/evidence/v9-7-production-governance/credential-lease-decisions.json
docs/design/V9.x/evidence/v9-7-production-governance/service-account-binding-decisions.json
docs/design/V9.x/evidence/v9-7-production-governance/audit-export-package.json
docs/design/V9.x/evidence/v9-7-production-governance/incident-timeline.json
docs/design/V9.x/evidence/v9-7-production-governance/evidence-hardening-report.json
docs/design/V9.x/evidence/v9-7-production-governance/terminal-automation-policy.json
docs/design/V9.x/evidence/v9-7-production-governance/browser-automation-policy.json
docs/design/V9.x/decisions/v9_7_high_risk_human_decision.json
```

## 7. Stop Conditions

```text
Credential decision lacks tenant, app, audience or operation binding.
Audit export is mutable.
Incident timeline is missing for denied high-risk action.
Browser automation starts without separate PRD and human decision.
Terminal automation is claimed as production ready.
Production readiness claim appears in completion context.
```
