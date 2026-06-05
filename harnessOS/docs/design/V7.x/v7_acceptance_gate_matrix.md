# V7 Acceptance Gate Matrix

文档状态：V7 acceptance control matrix / V7-3 next implementation candidate。

| Stage | Entry Gate | Acceptance Gate | Stop Condition |
| --- | --- | --- | --- |
| V7-0 | V6 final acceptance accepted with bounded baseline | Contract backlog, test matrix, claim scan and redaction scan procedures accepted | V7-0 claims complete before contract backlog closes |
| V7-1 | V7-0 accepted and Small Studio schema list complete | StudioContext, provider, credential, role, quota, audit evidence exist | studio scope bypasses tenant/workspace/project/app or writes runtime truth |
| V7-2 | V7-0 accepted and TUI command/state/screen contracts complete | `harness tui` starts and renders explainable state line | TUI executes mutation before confirmation |
| V7-3 | V7-1/V7-2 evidence exists, V7-3 I/O contracts, schema files, real-data plan and external audit accepted | natural language -> local Markdown document summary workflow -> spec -> blueprint -> confirm -> run -> evidence path passes with real runtime evidence | source=agent executes durable mutation or transcript-only / fallback evidence is claimed runtime-backed |
| V7-4 | V7-0 to V7-3 evidence exists, V7-3 PASS has real_runtime or real_runtime_fixture evidence, and final acceptance data contract accepted | final HTML dashboard, claim scan, redaction scan and drawio XML pass | V7 complete claim is emitted while V7-3 is fallback_demo_only / transcript_only / report_only / BLOCKED |

## V7-0 Contract Gate

```text
Small Studio DTO/schema list must exist.
Mission TUI command contract must exist.
Experience state line contract must exist.
TUI screen layout contract must exist.
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain link contract must exist.
Evidence package data schema must exist.
V7 test matrix must exist.
Claim scan procedure must exist.
Redaction scan procedure must exist.
```

If any V7-0 contract gate item is missing or fails audit, V7-0 must be marked:

```text
V7-0 in progress / planning hardening started.
```

V7-0 complete never means V7-1 / V7-2 / V7-3 implementation can skip their own gates.

## V7-1 Entry Schema Gate

```text
StudioContext.schema.json
StudioInventory.schema.json
WorkspaceInventory.schema.json
ProjectInventory.schema.json
AppInventory.schema.json
StudioRoleBinding.schema.json
ProviderProfileProjection.schema.json
CredentialRefProjection.schema.json
QuotaStatusProjection.schema.json
AuditSourceRefProjection.schema.json
```

## V7-2 Entry Contract Gate

```text
harness tui command contract
MissionTuiState schema
MissionInputEvent schema
ExperienceStateTimeline schema
AvailableAction schema
ForbiddenActionReason schema
EvidenceLink schema
BlueprintLink schema
RuntimeReportLink schema
TUI screen layout contract
```

## V7-3 Entry And Exit Gate

Entry gate:

```text
V7-1 evidence package exists.
V7-2 evidence package exists.
V7-3 pre-implementation review is accepted.
Natural-language parsing contract accepted.
WorkflowSpec / Diff / Blueprint generation contract accepted.
V7-3 schema files, manifest and examples accepted.
User confirmation and controlled run handoff contract accepted.
Real-data path authorization or fixture fallback contract accepted.
Provider-backed evidence policy accepted.
No False Green and redaction scan procedure accepted.
External audit has no critical or major open issue.
```

Exit gate:

```text
TUI transcript proves natural-language goal capture.
workflow.json / workflow.yaml generated and schema valid.
workflow.drawio generated and XML valid.
User confirmation is recorded before controlled run.
scanner_actual_read_count > 0.
provider_invocation_count > 0 is required for V7-3 PASS.
fallback_demo_only may be recorded only as PARTIAL / BLOCKED / debug evidence and cannot satisfy V7-3 completion.
Runtime Report, Quality and Evidence Chain are generated and cross-linked.
No raw prompt, raw file content, raw token or raw secret leakage.
```

Contract references:

```text
docs/design/V7.x/v7_3_pre_implementation_review.md
docs/design/V7.x/v7_3_io_contracts_and_schemas.md
docs/design/V7.x/v7_3_real_data_acceptance_plan.md
docs/design/V7.x/v7_3_schema_manifest_and_examples.md
```

## V7-4 Final Gate

```text
V7-0 to V7-3 evidence packages exist.
V7-4 final acceptance data contract accepted.
Final HTML acceptance dashboard opens.
Acceptance data JSON parses.
No FAIL / BLOCKED unless there is a recorded proceed decision.
No False Green scan PASS.
Redaction scan PASS.
V7 drawio XML valid.
V7-3 status=PASS.
V7-3 evidence_scope=real_runtime or real_runtime_fixture.
V7-3 scanner_actual_read_count > 0.
V7-3 provider_invocation_count > 0.
V7-3 fallback_demo_only=false, transcript_only=false and report_only=false.
Final allowed claim remains ready for review, not production ready.
```

Contract reference:

```text
docs/design/V7.x/v7_4_final_acceptance_data_contract.md
```

## Global Acceptance Requirements

```text
No raw secrets.
No raw prompt in evidence.
No raw artifact content in HTML / JSON evidence.
No browser direct /v1/rpc.
No browser direct /v1/events/subscribe.
No hidden mutation form.
No complete Workflow Studio claim.
No Agent executor claim.
```
