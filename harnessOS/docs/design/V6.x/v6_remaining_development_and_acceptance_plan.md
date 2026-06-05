# V6 Remaining Development And Acceptance Plan

文档状态：V6 complete / ready for review。本文记录 V6-9 完成后的 V6 收口状态。

## 1. Current Baseline

```text
V6-0 complete: production pilot planning gate ready for review.
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
V6-3 complete: production observability and audit export pilot slice ready for review.
V6-4 complete: limited production controlled executor pilot slice ready for review.
V6-5 complete: governed Agent execution intent pilot gate ready for review.
V6-6 complete: production external app onboarding pilot slice ready for review.
V6-7 complete: distributed multi-Agent runtime productization pilot slice ready for review.
V6-8 complete: product console pilot slice ready for review.
V6 complete: production pilot baseline ready for review.
```

当前不得声明：

```text
Agent executor ready
production controlled executor ready
production-ready external app support
complete Workflow Studio ready
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous workflow editing ready
full production GA
```

## 2. Remaining Stage Outline

| Stage | Goal | Current Gate | Implementation Entry | Allowed Claim |
| --- | --- | --- | --- | --- |
| V6-5 | Governed Agent Execution Intent Pilot | complete / ready for review | completed | V6-5 complete: governed Agent execution intent pilot gate ready for review. |
| V6-6 | Production External App Onboarding | complete / ready for review | completed | V6-6 complete: production external app onboarding pilot slice ready for review. |
| V6-7A | Distributed Runtime Pre-Implementation Closure | complete / ready for review | detailed contracts accepted + external audit PASS | readiness audit complete |
| V6-7B | Distributed Runtime Productization | complete / ready for review | evidence package PASS + claim scan PASS | V6-7 complete: distributed multi-Agent runtime productization pilot slice ready for review. |
| V6-8 | Product Console And Studio Gate | complete / ready for review | evidence package PASS + claim scan PASS | V6-8 complete: product console pilot slice ready for review. |
| V6-9 | Final Production Pilot Acceptance | complete / ready for review | V6-0 through V6-8 evidence packages exist + final acceptance PASS | V6 complete: production pilot baseline ready for review. |

## 3. V6-5 Development And Acceptance Outline

Development slices:

```text
V6-5-PR1 AgentExecutionIntent contract
V6-5-PR2 AgentCapabilityDecision and policy resolver
V6-5-PR3 AgentExecutionHandoff to Review Console / Manual Confirmation UX
V6-5-PR4 source=agent mutation denial evidence
V6-5-PR5 evidence package, claim scan, redaction scan
```

Acceptance:

```text
agent cannot auto apply / publish / run / rerun
agent intent always becomes human-confirmed handoff
high-risk intent requires approval gate
agent cannot read raw credential / raw prompt / raw artifact content
source=agent direct durable mutation denied
Evidence Chain records agent_id / session_id / policy_decision / capability_decision / handoff_ref
```

No False Green stop conditions:

```text
Agent execution intent is described as Agent executor
source=agent durable mutation succeeds
human confirmation is bypassed
raw credential / raw prompt / raw artifact content leaks
No False Green claim scan fails
```

## 4. V6-6 Development And Acceptance Outline

Development slices:

```text
V6-6-PR1 tenant-bound app registration and service account binding
V6-6-PR2 domain verification before origin allowlist
V6-6-PR3 quota / rate limit policy and denial evidence
V6-6-PR4 offboarding revoke for credentials / origins / sessions / grants
V6-6-PR5 SDK compatibility guard, no direct internal runtime routes
```

Acceptance:

```text
wrong tenant app access denied
unverified domain cannot enter origin allowlist
quota / rate limit denial is auditable
offboarding revokes app credentials, origin allowlist, active sessions, pending grants
browser SDK cannot call internal runtime routes directly
```

No False Green stop conditions:

```text
external app bypasses tenant / credential / quota / origin boundary
SDK directly calls internal runtime routes
offboarding only updates UI state
production-ready external app support is claimed
```

## 5. V6-7A Pre-Implementation Closure Outcome

Documentation slices:

```text
V6-7A-DOC1 pre-implementation closure plan
V6-7A-DOC2 distributed runtime state machine
V6-7A-DOC3 worker lifecycle model
V6-7A-DOC4 runtime I/O contract
V6-7A-DOC5 failure recovery acceptance matrix
V6-7A-DOC6 drawio / canonical docs alignment
```

Acceptance:

```text
V6-7A accepted for implementation after external audit and human high-risk decision
human high-risk proceed decision recorded in conversation before V6-7B implementation
worker lifecycle and assignment denial cases are specified
serial / parallel branch state model is specified
retry, recovery, attempt history and lineage acceptance matrix is specified
```

Stop conditions:

```text
V6-7 documentation authorizes runtime implementation without human decision
V5-8 bounded evidence is upgraded to production distributed runtime complete
source=agent worker assignment is allowed
```

## 6. V6-7B Development And Acceptance Outcome

Development slices:

```text
V6-7-PR1 DistributedRunCoordinator for serial / parallel station orchestration
V6-7-PR2 tenant-bound AgentWorkerRegistry and worker assignment policy
V6-7-PR3 DistributedStateCheckpoint and retry / recovery state
V6-7-PR4 AttemptHistoryStore and old attempt preservation
V6-7-PR5 ArtifactLineageService with producer_attempt_id
V6-7-PR6 incident timeline, evidence package, claim scan
```

Result:

```text
status: PASS
evidence_scope: repo_backed_pilot_runtime_slice
claim_violations: 0
redaction_status: PASS
```

Acceptance:

```text
lost worker can recover or mark failed
retry preserves old attempts and old errors
artifact lineage records producer_attempt_id
parallel branches expose independent state
worker identity is tenant-bound and not reused across tenants without explicit binding
tenant / credential / policy boundary applies to every worker action
```

Stop conditions:

```text
V4/V5 dev-local evidence is upgraded to full orchestration readiness
worker bypasses tenant / credential / policy boundary
attempt history overwrites old attempts
distributed multi-Agent runtime ready is claimed
```

## 7. V6-8 Development And Acceptance Outcome

Development slices:

```text
V6-8-PR1 Runtime Report read-only product console view - complete
V6-8-PR2 Evidence Review read-only view - complete
V6-8-PR3 Audit Export access view - complete
V6-8-PR4 External App Admin view without runtime truth writes - complete
V6-8-PR5 Manual Confirmation UX with human_authorization_ref - complete
V6-8-PR6 Full Workflow Studio separate PRD gate notice - complete
```

Required planning contracts:

```text
v6_8_product_console_bff_contract.md
v6_8_browser_safety_test_matrix.md
v6_8_manual_confirmation_ux_contract.md
```

Acceptance:

```text
status: PASS
evidence_scope: repo_backed_product_console_projection
claim_violations: 0
redaction_status: PASS
Runtime Report has no hidden mutation form
Evidence Review has no Apply / Publish / Approve / Reject / Execute / Run execution buttons
Manual confirmation records actor / operation / target_refs / human_authorization_ref
browser does not call internal runtime routes directly
Product Console admin ops cannot construct runtime truth
```

Evidence:

```text
docs/design/V6.x/evidence/v6-8-product-console/
docs/design/V6.x/v6_8_product_console_completion_note.md
```

No False Green stop conditions:

```text
Evidence Review becomes execution panel
Product Console admin ops become runtime truth
Full Web Studio becomes V6 default route
complete Workflow Studio ready is claimed
```

## 8. V6-9 Final Acceptance Outline

Development slices:

```text
V6-9-PR1 collect V6-0 to V6-8 evidence summaries
V6-9-PR2 generate final acceptance dashboard
V6-9-PR3 run No False Green and redaction scans
V6-9-PR4 validate drawio XML and canonical docs
V6-9-PR5 produce final completion note
```

Required planning contracts:

```text
v6_9_final_acceptance_evidence_inventory_plan.md
v6_9_no_false_green_and_redaction_scan_plan.md
```

Acceptance:

```text
V6-0 to V6-8 all have evidence summary
no FAIL / BLOCKED
all PARTIAL have recorded proceed decision
No False Green scan PASS
redaction scan PASS
drawio XML valid
runtime truth boundary preserved
```

## 9. Required Validation Commands

```text
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V6.x/v6_current_gap_analysis.drawio
```

Frontend stages must additionally run:

```text
cd apps/workflow-console && npm test -- --runInBand
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
```

## 10. Completion Evidence Format

Each remaining stage must produce:

```text
docs/design/V6.x/evidence/v6-N-stage-name/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  redaction-scan.md when sensitive data is involved
  raw/
  logs/
  screenshots/ when UI is involved
```

Completion notes must include:

```text
Allowed claim
Forbidden claims
Implementation evidence
Validation commands
Evidence outputs
PRD Spec Review
False Green Evaluation
Next Stage Audit
Proceed Decision
No False Green Statement
```
