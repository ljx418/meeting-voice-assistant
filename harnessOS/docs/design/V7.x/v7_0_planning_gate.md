# V7-0 Planning Hardening Gate

文档状态：V7-0 complete / ready for review / document-only stage。

## Goal

V7-0 的目标是冻结 V7 文档口径，不进入代码实现。

V7-0 必须证明：

```text
V7 继承 V6 production pilot baseline ready for review。
V7 不把 V6 升级成 production ready。
V7 同时承载 small studio production pilot 和 explainable Mission TUI。
V7 后续实现前有明确 PRD、架构、gap、验收和 claim guard。
```

V7-0 合同与测试矩阵已经完成并通过本地审计，因此允许声明：

```text
V7-0 complete: V7 small studio and explainable TUI planning gate ready for review.
```

该声明仍只表示 planning gate ready for review，不表示 V7-1 / V7-2 / V7-3 implementation 已开始。

## Deliverables

```text
00_README.md
v7_target_prd.md
v7_target_architecture.md
v7_current_gap_analysis.md
v7_current_gap_analysis.drawio
v7_development_and_acceptance_plan.md
v7_acceptance_gate_matrix.md
v7_no_false_green_claim_guard.md
v7_planning_audit_for_chatgpt.md
v7_0_contracts_and_test_matrix.md
v7_0_planning_hardening_completion_note.md
docs/design/V7.x/evidence/v7-0-planning-hardening/
```

## Required V7-0 Contract Backlog

V7-0 必须补齐以下实现前合同。未补齐前，V7-1 / V7-2 / V7-3 不能进入 implementation。

### Small Studio DTO / Schema List

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

### Mission TUI Command Contract

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

V7-0 只定义 command contract，不实现 runtime behavior。

### Experience State Line Contract

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

### TUI Screen Layout Contract

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

### Link Contract

WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain 必须互相可链接，但这些 heads 都不能构造 runtime truth。

```text
WorkflowSpecLink
WorkflowDiffLink
BlueprintLink
RuntimeReportLink
EvidenceChainLink
QualityReportLink
ArtifactLineageLink
```

### Evidence Package Data Schema

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

### V7 Test Matrix

```text
v7_0_contracts_exist
v7_0_claim_guard_contains_forbidden_terms
v7_0_redaction_scan_procedure_exists
v7_1_schema_list_complete_before_implementation
v7_2_tui_contract_complete_before_implementation
v7_3_requires_v7_1_and_v7_2_acceptance
v7_4_requires_v7_0_to_v7_3_evidence
v7_no_false_green_scan_passes
v7_drawio_xml_valid
```

### Claim Scan Procedure

Claim scan must reject forbidden claims outside explicit forbidden/no-false-green context.

### Redaction Scan Procedure

Redaction scan must reject raw secret, raw token, raw prompt, raw connector payload, raw artifact content and signed URL leakage.

## Acceptance

```text
All V7 canonical docs exist.
Drawio XML validates.
Allowed claims are explicit.
Forbidden claims are explicit.
V7 stage order is explicit.
No implementation work is started in V7-0.
Small Studio DTO/schema list exists.
Mission TUI command contract exists.
Experience state line contract exists.
TUI screen layout contract exists.
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain link contract exists.
Evidence package data schema exists.
V7 test matrix exists.
Claim scan procedure exists.
Redaction scan procedure exists.
```

## Allowed Claim

```text
V7-0 complete: V7 small studio and explainable TUI planning gate ready for review.
```

This allowed claim is now available because all V7-0 acceptance items passed local audit.

## Stop Conditions

```text
V7-0 claims production ready.
V7-0 claims complete Workflow Studio.
V7-0 claims Agent executor.
V7-0 starts runtime implementation.
V7-1 / V7-2 / V7-3 implementation starts before V7-0 accepted.
V7-0 marks complete while contract backlog remains open.
```
