# V6 Remaining Development And Acceptance Plan

文档状态：V6-6 complete / ready for review；V6-7 implementation NO-GO / planning refinement only。本文是 V6-7 到 V6-9 的剩余开发与验收控制计划。

## 1. Current Baseline

```text
V6-0 complete: production pilot planning gate ready for review.
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
V6-3 complete: production observability and audit export pilot slice ready for review.
V6-4 complete: limited production controlled executor pilot slice ready for review.
V6-5 complete: governed Agent execution intent pilot gate ready for review.
V6-6 complete: production external app onboarding pilot slice ready for review.
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
| V6-7 | Distributed Runtime Productization | NO-GO for implementation; planning refinement only | separate human high-risk proceed decision + detailed contracts accepted | V6-7 complete: distributed multi-Agent runtime productization pilot slice ready for review. |
| V6-8 | Product Console And Studio Gate | conditional GO for planning refinement | expanded UI/BFF/browser test matrix accepted | V6-8 complete: product console pilot slice ready for review. |
| V6-9 | Final Production Pilot Acceptance | framework only | V6-6 / V6-7 / V6-8 evidence packages exist | V6 complete: production pilot baseline ready for review. |

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

Stop conditions:

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

Stop conditions:

```text
external app bypasses tenant / credential / quota / origin boundary
SDK directly calls internal runtime routes
offboarding only updates UI state
production-ready external app support is claimed
```

## 5. V6-7 Development And Acceptance Outline

Development slices:

```text
V6-7-PR1 DistributedRunCoordinator for serial / parallel station orchestration
V6-7-PR2 tenant-bound AgentWorkerRegistry and worker assignment policy
V6-7-PR3 DistributedStateCheckpoint and retry / recovery state
V6-7-PR4 AttemptHistoryStore and old attempt preservation
V6-7-PR5 ArtifactLineageService with producer_attempt_id
V6-7-PR6 incident timeline, evidence package, claim scan
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

## 6. V6-8 Development And Acceptance Outline

Development slices:

```text
V6-8-PR1 Runtime Report read-only product console view
V6-8-PR2 Evidence Review read-only view
V6-8-PR3 Audit Export access view
V6-8-PR4 External App Admin view without runtime truth writes
V6-8-PR5 Manual Confirmation UX with human_authorization_ref
V6-8-PR6 Full Workflow Studio separate PRD gate notice
```

Acceptance:

```text
Runtime Report has no hidden mutation form
Evidence Review has no Apply / Publish / Approve / Reject / Execute / Run execution buttons
Manual confirmation records actor / operation / target_refs / human_authorization_ref
browser does not call internal runtime routes directly
Product Console admin ops cannot construct runtime truth
```

Stop conditions:

```text
Evidence Review becomes execution panel
Product Console admin ops become runtime truth
Full Web Studio becomes V6 default route
complete Workflow Studio ready is claimed
```

## 7. V6-9 Final Acceptance Outline

Development slices:

```text
V6-9-PR1 collect V6-0 to V6-8 evidence summaries
V6-9-PR2 generate final acceptance dashboard
V6-9-PR3 run No False Green and redaction scans
V6-9-PR4 validate drawio XML and canonical docs
V6-9-PR5 produce final completion note
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

## 8. Required Validation Commands

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

## 9. Completion Evidence Format

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
