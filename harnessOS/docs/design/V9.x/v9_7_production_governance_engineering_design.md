# V9-7 Production Governance Engineering Design

文档状态：V9-7 engineering design / implemented governance slice / ready for review。

## 1. Boundary

V9-7 hardens production governance, evidence and terminal automation gates. It does not prove production automation ready or production browser automation ready.

Implemented evidence:

```text
core/governance/v9_7_production_governance.py
tests/test_v9_7_production_governance.py
tools/v9/generate_v9_7_production_governance_evidence.py
docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json
```

## 2. Required Models

```text
TenantIsolationMatrix
CredentialLease
ServiceAccountBinding
AuditExportPackage
IncidentTimelineEvent
EvidenceHardeningReport
TerminalAutomationPolicy
BrowserAutomationSeparatePrd
```

## 3. Credential Lease Validator

CredentialLease must bind:

```text
tenant_id
workspace_id
project_id
app_id
audience
operation
service_account_id
expires_at
revoked
audit_ref
```

Denied:

```text
wrong tenant
wrong app
wrong audience
wrong operation
expired lease
revoked lease
raw secret access
```

## 4. Audit And Incident Rules

```text
audit export is append-only.
incident timeline required for timeout, denied credential, denied policy and worker loss.
evidence hardening validator scans raw secret, raw prompt and raw artifact content.
browser automation blocked unless separate PRD and explicit human decision exist.
```

## 5. Acceptance Tests

```text
credential_lease_wrong_tenant_denied
credential_lease_wrong_operation_denied
credential_lease_expired_denied
audit_export_append_only
incident_timeline_records_policy_denial
evidence_hardening_redaction_pass
browser_automation_blocked_without_separate_prd
production_automation_ready_claim_denied
```

## 6. Non-Claims

V9-7 ready-for-review evidence must not be summarized as:

```text
production automation ready
production terminal automation ready
production browser automation ready
production ready
full production GA
```
