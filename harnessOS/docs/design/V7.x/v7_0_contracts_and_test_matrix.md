# V7-0 Contracts And Test Matrix

文档状态：V7-0 planning hardening contract / document-only stage。

## 1. Scope

本文把 V7-0 从方向规划收紧为实现前合同。它不实现 V7-1 / V7-2 / V7-3 功能。

Allowed current statement:

```text
V7-0 complete: V7 small studio and explainable TUI planning gate ready for review.
```

This statement is valid because this package has passed local audit. It remains planning-only and does not authorize V7-1 / V7-2 / V7-3 implementation without their own entry-gate closure.

If any required contract, schema list, evidence package, claim scan procedure, redaction scan procedure or test matrix is removed or fails audit, the only allowed statement becomes:

```text
V7-0 in progress / planning hardening started.
```

## 2. Small Studio DTO / Schema List

```text
docs/design/V7.x/schemas/StudioContext.schema.json
docs/design/V7.x/schemas/StudioInventory.schema.json
docs/design/V7.x/schemas/WorkspaceInventory.schema.json
docs/design/V7.x/schemas/ProjectInventory.schema.json
docs/design/V7.x/schemas/AppInventory.schema.json
docs/design/V7.x/schemas/StudioRoleBinding.schema.json
docs/design/V7.x/schemas/ProviderProfileProjection.schema.json
docs/design/V7.x/schemas/CredentialRefProjection.schema.json
docs/design/V7.x/schemas/QuotaStatusProjection.schema.json
docs/design/V7.x/schemas/AuditSourceRefProjection.schema.json
```

Boundary:

```text
Small Studio Control Plane is product aggregation plane.
It must not write WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun / Artifact.
It must not expose raw credential material.
```

## 3. Mission TUI Command Contract

The command contract is:

```text
harness tui
harness mission create
harness mission explain
harness mission diff
harness mission confirm
harness mission run
harness mission status
harness mission evidence
```

V7-0 defines the command contract only. Runtime behavior belongs to V7-2 / V7-3.

## 4. Mission TUI State Contracts

```text
docs/design/V7.x/schemas/MissionTuiState.schema.json
docs/design/V7.x/schemas/MissionInputEvent.schema.json
docs/design/V7.x/schemas/ExperienceStateTimeline.schema.json
docs/design/V7.x/schemas/AvailableAction.schema.json
docs/design/V7.x/schemas/ForbiddenActionReason.schema.json
```

State line:

```text
IntentCaptured
SpecDrafted
SchemaValidated
DiffReady
AwaitingConfirmation
UserConfirmed
RuntimeStarted
RuntimeObserved
EvidenceRecorded
ReviewReady
```

## 5. TUI Screen Layout Contract

```text
Mission input panel
Experience state line
WorkflowSpec / Diff preview
Workflow Blueprint link panel
Available actions panel
Forbidden reasons panel
Runtime Report link panel
Evidence Chain link panel
Confirmation prompt panel
```

## 6. Link Contract

```text
docs/design/V7.x/schemas/EvidenceLink.schema.json
docs/design/V7.x/schemas/BlueprintLink.schema.json
docs/design/V7.x/schemas/RuntimeReportLink.schema.json
docs/design/V7.x/schemas/WorkflowExperienceLinkContract.schema.json
```

Rules:

```text
WorkflowSpec link is not runtime truth.
Blueprint / Drawio link is visualization only.
Runtime Report link is read-only.
Evidence Chain link is read-only.
Link contract cannot execute durable mutation.
```

## 7. Evidence Package Data Schema

```text
docs/design/V7.x/schemas/V7EvidencePackage.schema.json
```

Required fields:

```text
stage_id
status
evidence_scope
runtime_backed
transcript_only
report_only
provider_backed
real_data_used
evidence_refs
commands_run
claim_scan_result
redaction_scan_result
prd_drift_evaluation
false_green_evaluation
next_stage_audit
proceed_decision
```

## 8. Claim Scan Procedure

Scan V7 markdown and drawio files for forbidden claims outside no-false-green / forbidden context.

Forbidden claims include:

```text
production ready
full production GA
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous workflow editing ready
小型工作室生产可用
TUI 工作流工作台已完成
```

## 9. Redaction Scan Procedure

Scan V7 evidence, reports and schemas for forbidden raw fields:

```text
raw secret
raw token
raw prompt
raw connector payload
raw artifact content
signed URL
Authorization
Bearer
capability_token
subscription_token
```

## 10. V7-0 Test Matrix

```text
v7_0_all_canonical_docs_exist
v7_0_all_schema_files_parse
v7_0_schema_files_are_strict
v7_0_small_studio_schema_list_complete
v7_0_mission_tui_schema_list_complete
v7_0_link_schema_list_complete
v7_0_evidence_package_schema_complete
v7_0_claim_guard_contains_required_terms
v7_0_redaction_scan_terms_exist
v7_0_stage_entry_gates_block_v7_1_v7_2_v7_3
v7_0_drawio_xml_valid
v7_0_no_runtime_implementation_started
```

## 11. V7-0 Audit Opinion

```text
prd_drift_evaluation=LOW
false_green_evaluation=LOW
critical_blockers=0
major_blockers=0
recommendation=proceed_to_v7_1_pre_implementation_review
implementation_allowed=false
```

V7-1 / V7-2 implementation remains blocked until each stage closes its own PRD/spec review and acceptance plan.
