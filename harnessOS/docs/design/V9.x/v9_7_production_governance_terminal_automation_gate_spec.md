# V9-7 Production Governance / Evidence Hardening And Terminal Automation Gate Spec

文档状态：V9-7 high-risk gate spec / planned only。

## 1. Naming And Boundary

V9-7 的正式阶段名称为：

```text
Production Governance / Evidence Hardening and Terminal Automation Gate
```

该阶段兼容此前的 `Production Terminal Automation Gate` 口径：terminal/browser automation 只能作为高风险门禁范围内的子议题，核心验收对象是 tenant、credential、approval、audit、incident 和 evidence hardening。

Allowed claim:

```text
V9-7 complete: production governance and terminal automation gate ready for review.
```

Forbidden claim:

```text
production terminal automation ready
production browser automation ready
production automation ready
```

## 2. Required Contracts

```text
TenantIsolationDecision
CredentialLeaseDecision
HumanAuthorizationRef
ApprovalGateDecision
AuditExportPackage
IncidentTimelineEvent
TerminalAutomationPolicy
BrowserAutomationPolicy
EvidenceHardeningReport
```

## 3. High-Risk Gate Rules

```text
No terminal automation without tenant-bound identity.
No browser account automation without separate PRD and explicit human decision.
No credential lease without audience / operation / app / tenant binding.
No automation evidence may include raw secret, raw prompt, raw artifact content or signed URL.
Incident timeline is required for timeout, denied credential, denied policy and worker loss.
```

## 4. Acceptance Tests

```text
production_governance_requires_human_high_risk_decision
credential_lease_tenant_app_audience_operation_bound
terminal_automation_requires_policy_and_incident_boundary
browser_automation_blocked_without_separate_prd
audit_export_append_only
incident_timeline_records_denial_and_recovery
evidence_hardening_redaction_pass
production_automation_ready_claim_denied
```

## 5. Stop Conditions

```text
V9-7 is treated as production automation ready.
browser account automation starts without separate PRD.
terminal automation has raw credential access.
audit export is mutable without append-only trail.
incident timeline is missing for denied or failed automation action.
```
