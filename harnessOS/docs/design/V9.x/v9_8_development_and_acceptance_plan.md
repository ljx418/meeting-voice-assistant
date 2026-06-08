# V9-8 Development And Acceptance Plan

文档状态：V9-8 detailed development and acceptance plan / validator implemented / final acceptance PASS with provider-backed storyboard evidence.

This document now records the implemented V9-8 final acceptance validator. The validator generates a PASS dashboard because US-V9-08 now has valid provider-backed storyboard image artifacts.

## 1. Entry Baseline

V9-8 final claim may be emitted only after:

```text
V9-0..V9-7 evidence packages exist.
US-V9-01..US-V9-09 user scenario results exist.
Runtime-backed user scenarios cite real_runtime_fixture or real_runtime evidence.
Planning docs, transcript-only reports and report-only dashboards are rejected for runtime-backed user scenario PASS.
No required stage is FAIL or BLOCKED.
PARTIAL scenarios have documented proceed decisions.
High-risk stages include human decision refs.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
```

## 2. Scope

V9-8 aggregates stage and user evidence:

```text
stage evidence discovery
evidence package schema validation
runtime-backed evidence checks
user scenario acceptance checks
high-risk decision checks
claim scan
redaction scan
drawio XML validation
final dashboard generation
final result summary
```

V9-8 must not:

```text
accept planning docs as runtime evidence.
ignore missing user scenario evidence.
emit final claim while any stage is FAIL or BLOCKED.
upgrade ready for review to production completion.
```

Current V9-8 output:

```text
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-dashboard.html
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-result-summary.md
```

Current final acceptance result:

```text
status=PASS
blockers=[]
US-V9-08 provider-backed storyboard image artifacts=4
final_claim=V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-8A Evidence discovery | stage evidence index | V9-0..V9-7 roots found |
| V9-8B Package validation | validation report | schema, refs and status fields valid |
| V9-8C Runtime evidence checker | runtime-backed report | runtime stages have runtime evidence, not docs-only |
| V9-8D User scenario checker | user scenario matrix | US-V9-01..US-V9-09 reviewed and runtime_backed requirements enforced |
| V9-8E Claim and redaction gate | scan reports | both PASS |
| V9-8F Final dashboard | HTML, JSON and summary | final claim emitted only when all gates pass |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/evidence/v9_8_all_required_evidence_present_sample.json
```

Negative fixtures:

```text
fixtures/evidence/v9_8_reject_planning_only_sample.json
fixtures/evidence/v9_8_missing_v9_3_runtime_evidence.json
fixtures/evidence/v9_8_missing_user_scenario_result.json
fixtures/evidence/v9_8_missing_high_risk_human_decision.json
fixtures/evidence/v9_8_forbidden_claim.json
fixtures/evidence/v9_8_forbidden_content_leakage.json
fixtures/evidence/v9_8_drawio_invalid.json
```

## 5. Acceptance Tests

```text
v9_8_discovers_v9_0_to_v9_7_evidence
v9_8_rejects_planning_docs_as_runtime_evidence
v9_8_requires_user_scenarios_01_to_09
v9_8_requires_runtime_backed_user_scenario_evidence
v9_8_rejects_transcript_only_or_report_only_user_scenario_pass
v9_8_rejects_missing_high_risk_human_decision
v9_8_rejects_fail_or_blocked_without_proceed_decision
v9_8_claim_scan_pass
v9_8_redaction_scan_pass
v9_8_drawio_xml_valid
v9_8_generates_final_dashboard_and_data
v9_8_final_claim_limited_to_ready_for_review
```

## 6. Final Outputs

```text
v9-final-acceptance-dashboard.html
v9-final-acceptance-data.json
v9-final-claim-scan.md
v9-final-redaction-scan.md
v9-final-result-summary.md
v9-final-user-scenario-matrix.json
```

## 7. Stop Conditions

```text
Any V9-0..V9-7 evidence package is missing.
Any required user scenario result is missing.
Any runtime-backed user scenario lacks real_runtime_fixture or real_runtime evidence.
Any runtime-backed user scenario uses planning docs, transcript-only or report-only evidence.
Any runtime-backed stage uses docs-only evidence.
Any forbidden readiness claim appears in positive completion context.
Any forbidden content leakage appears in evidence.
Drawio XML validation fails.
Final claim is stronger than ready for review.
```
