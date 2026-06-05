# V9 Evidence Package Schema And Validator Spec

文档状态：V9 P0 evidence package validator plan / required before V9-8。

## 1. Purpose

V9-8 必须聚合 V9-0 到 V9-7 的真实证据包。规划文档、PRD 或 readiness spec 不能被计为 runtime evidence。

P0 sample evidence fixtures:

```text
docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json
docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json
```

## 2. Evidence Package Fields

Required fields:

```text
evidence_package_id
stage_id
status
evidence_scope
runtime_backed
source_document_refs
runtime_artifact_refs
test_run_refs
human_decision_refs
claim_scan_result
redaction_scan_result
forbidden_raw_content_scan_result
drawio_validation_result
evidence_hash
created_by
created_at
auditor_decision
notes
```

Allowed `evidence_scope`:

```text
planning_only
contract_freeze
implementation_readiness
deterministic_fixture
real_runtime_fixture
real_runtime
manual_review
```

## 3. Validator Rules

```text
planning_only cannot satisfy runtime-backed stage acceptance.
runtime_backed=false blocks V9-8 if the stage requires runtime evidence.
missing human_decision_refs blocks high-risk stages.
forbidden claim outside allowed context blocks V9-8.
raw secret / raw prompt / raw artifact content blocks V9-8.
drawio_validation_result must be PASS.
evidence_hash must cover package contents.
source_document_refs must not be counted as runtime_artifact_refs.
```

Validator CLI contract:

```text
input: evidence package JSON path
output: validation_result JSON with status, blocking_reasons, warning_reasons, accepted_evidence_refs
exit 0: PASS only
exit 1: FAIL or BLOCKED
```

## 4. Stage Requirements

```text
V9-0 allows planning_only.
V9-1 allows contract_freeze.
V9-2 requires real_runtime_fixture or real_runtime.
V9-3 requires real_runtime_fixture or real_runtime.
V9-4 requires real_runtime_fixture or real_runtime.
V9-5 requires real_runtime_fixture or real_runtime.
V9-6 requires implementation_readiness plus browser/UI evidence before acceptance.
V9-7 requires manual_review plus high-risk decision evidence.
V9-8 requires all prior packages.
```

## 4.1 Front-Stage Evidence Minimums

V9-1 evidence package must contain:

```text
schema_validation_result
negative_fixture_result
contract_freeze_sample
No False Green scan
redaction scan
external audit decision
```

V9-2 evidence package must contain:

```text
runtime-backed controlled executor result
HumanAuthorizationRef validation result
CapabilityResolver decision chain
ApprovalGateDecision when high-risk
ExecutionEvidence with redacted refs
idempotency / timeout / rollback result
```

V9-3 evidence package must contain:

```text
serial run evidence
parallel branch evidence
fan-in / fan-out evidence
lost worker recovery evidence
attempt history evidence
artifact lineage with producer_agent_id and producer_attempt_id
```

V9-4 evidence package must contain:

```text
diff proposal evidence
sandboxed test evidence
review summary evidence
fix-loop evidence
no auto commit / auto push / auto deploy denial evidence
```

## 5. Negative Fixtures

```text
v9_8_planning_docs_only_rejected
v9_8_missing_v9_2_runtime_evidence_rejected
v9_8_missing_high_risk_human_decision_rejected
v9_8_forbidden_claim_rejected
v9_8_raw_secret_rejected
v9_8_drawio_invalid_rejected
```
