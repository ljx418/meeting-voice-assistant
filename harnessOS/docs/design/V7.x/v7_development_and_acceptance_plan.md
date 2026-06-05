# V7 Development And Acceptance Plan

文档状态：V7 development and acceptance control plan / V7-3 next implementation candidate。本文定义 V7 开发及验收计划。

## 1. Stage Status Table

| Stage | Purpose | Current Status | Allowed Claim | Boundary |
| --- | --- | --- | --- | --- |
| V7-0 | Planning Hardening Gate | complete / ready for review | V7-0 complete: V7 small studio and explainable TUI planning gate ready for review. | documentation only; does not start V7-1 / V7-2 runtime |
| V7-1 | Small Studio Control Plane | complete / ready for review | V7-1 complete: small studio production pilot control plane ready for review. | not full production GA; repo-backed fixture scope |
| V7-2 | Explainable Mission TUI | complete / ready for review | V7-2 complete: explainable Mission TUI pilot ready for review. | transcript-only; not complete Workflow Studio |
| V7-3 | Workflow Creation And Run Experience | complete / ready for review | V7-3 complete: natural-language workflow creation and controlled run experience ready for review. | limited to natural-language -> local Markdown technical document summary workflow; not Agent executor |
| V7-4 | Final Small Studio Acceptance | complete / ready for review | V7 complete: small studio production pilot and explainable TUI baseline ready for review. | not production ready |

## 1.1 Accepted V6 Baseline Boundary

V7 accepts this baseline only for planning:

```text
V6 complete: production pilot baseline ready for review.
```

It must preserve these V6 evidence facts:

```text
V6 final acceptance status=PASS
stage_count=9
claim_scan=PASS
redaction_scan=PASS
drawio_xml=PASS
blockers=0
production_ready=false
full_production_ga=false
agent_executor_ready=false
production_controlled_executor_ready=false
complete_workflow_studio_ready=false
production_ready_external_app_support=false
full_multi_agent_orchestration_ready=false
distributed_multi_agent_runtime_ready=false
autonomous_workflow_editing_ready=false
```

Canonical references:

```text
docs/design/V7.x/v7_v6_baseline_evidence.md
docs/design/V6.x/v6_final_completion_note.md
docs/design/V6.x/evidence/v6-9-final-acceptance/final-acceptance-data.json
```

## 1.2 V7-0 Audit Condition Reconciliation

V7-0 的 allowed claim 只有在以下清单全部存在并通过本地审计时才成立：

```text
Small Studio DTO/schema list
Mission TUI command contract
Experience state line contract
TUI screen layout contract
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain link contract
Evidence package data schema
V7 test matrix
claim scan procedure
redaction scan procedure
```

当前这些合同和测试矩阵已经由 `v7_0_contracts_and_test_matrix.md`、`schemas/` 和 `evidence/v7-0-planning-hardening/` 支撑，因此 V7-0 维持 `complete / ready for review`。如果任一合同或测试矩阵被删除、失效或审计打回，V7-0 必须回退为：

```text
V7-0 in progress / planning hardening started.
```

V7-0 completion never authorizes direct V7-3 implementation.

## 2. Development Order

```text
V7-0 -> V7-1 -> V7-2 -> V7-3 -> V7-4
```

V7-1 and V7-2 may be designed in parallel, but implementation must keep their boundaries separate:

```text
V7-1 controls studio scope.
V7-2 renders explainable interaction.
V7-3 connects them into a real run.
```

项目里程碑详见：

```text
docs/design/V7.x/v7_milestone_roadmap.md
```

## 3. Implementation Readiness Review

当前 V7-0 planning hardening、V7-1 Small Studio projection 与 V7-2 Explainable Mission TUI 已完成本地审计。V7-3 可以进入 external implementation-readiness audit；V7-3 实现前审计、I/O 合同、schema files 和真实数据验收计划已补齐为外部审计包，但仍不能跳过外部审计直接进入实现。V7-4 final acceptance data contract 已补齐，但只能在 V7-0 到 V7-3 evidence package 存在后执行。

V7-0 已补齐：

```text
DTO / schema contracts
CLI / TUI command contracts
TUI state and screen layout contracts
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain link contract
evidence package data schema
test matrix
claim scan and redaction scan procedure
```

V7-1 / V7-2 已完成 review baseline。进入 V7-3 前必须确认：

```text
V7-1 evidence package exists.
V7-2 evidence package exists.
V7-3 real-data acceptance plan is closed.
V7-3 schema files, manifest and examples are accepted.
Natural-language parsing contract is accepted.
WorkflowSpec / Diff / Blueprint generation contract is accepted.
User-confirmed run handoff contract is accepted.
Provider-backed or blocked/fallback evidence policy is accepted.
No False Green scan procedure remains active.
External audit has no critical or major open issue.
```

V7-3 PASS requires:

```text
status=PASS
evidence_scope=real_runtime or real_runtime_fixture
runtime_backed=true
scanner_actual_read_count > 0
provider_invocation_count > 0
folder_summaries_generated=PASS
overview_summary_generated=PASS
quality_report_generated=PASS
runtime_report_generated=PASS
evidence_chain_generated=PASS
fallback_demo_only=false
transcript_only=false
report_only=false
claim_scan=PASS
redaction_scan=PASS
```

Fallback, transcript-only or report-only evidence may be retained as PARTIAL / BLOCKED / debug evidence, but cannot satisfy V7-3 completion or unlock V7-4 final claim.

## 4. Detailed Stage Plan

### V7-0 Planning Hardening Gate

Goal:

```text
Turn the current V7 planning package into implementation-ready contracts.
```

Required outputs:

```text
Small Studio DTO/schema list accepted
Mission TUI command contract accepted
Experience state line contract accepted
TUI screen layout contract accepted
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain link contract accepted
Evidence package schema accepted
V7 test matrix accepted
No False Green scan plan accepted
Redaction scan plan accepted
V7 drawio XML valid
```

Exit condition:

```text
V7-1 / V7-2 implementation can start only after V7-0 has no critical PRD drift, no major false-green risk, and no missing P0 contract.
```

### V7-1 Small Studio Production Pilot Control Plane

Entry checklist:

```text
V7-0 accepted
StudioContext.schema.json accepted
StudioInventory.schema.json accepted
WorkspaceInventory.schema.json accepted
ProjectInventory.schema.json accepted
AppInventory.schema.json accepted
StudioRoleBinding.schema.json accepted
ProviderProfileProjection.schema.json accepted
CredentialRefProjection.schema.json accepted
QuotaStatusProjection.schema.json accepted
AuditSourceRefProjection.schema.json accepted
```

Implementation outline:

```text
Create StudioContext and inventory read models.
Project V6 identity / credential / provider / quota / audit evidence into studio-scoped views.
Render a static HTML evidence page.
Keep all raw credentials and raw provider payloads out of evidence.
```

Minimum DTOs:

```text
StudioContext
StudioInventory
WorkspaceInventory
ProjectInventory
AppInventory
StudioRoleBinding
ProviderProfileProjection
CredentialRefProjection
QuotaStatusProjection
AuditSourceRefProjection
```

Runtime truth boundary:

```text
Small Studio Control Plane is product aggregation plane.
It must not write WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun / Artifact.
It must not expose raw credential material.
```

Acceptance:

```text
studio_context_contains_tenant_workspace_project_app_refs
provider_profile_projection_redacts_secret
credential_ref_projection_no_raw_secret
role_binding_projection_auditable
quota_denial_explainable
cross_workspace_access_denied
studio_control_plane_does_not_construct_runtime_truth
```

### V7-2 Explainable Mission TUI

Entry checklist:

```text
V7-0 accepted
harness tui command contract accepted
MissionTuiState schema accepted
MissionInputEvent schema accepted
ExperienceStateTimeline schema accepted
AvailableAction schema accepted
ForbiddenActionReason schema accepted
EvidenceLink schema accepted
BlueprintLink schema accepted
RuntimeReportLink schema accepted
TUI screen layout contract accepted
```

Implementation outline:

```text
Add a real `harness tui` entry.
Render mission input, transcript, state timeline, available actions, forbidden reasons and evidence links.
Reuse existing ExperienceStateProjection where possible.
Keep mutation behind user confirmation.
```

Minimum contracts:

```text
MissionTuiState
MissionInputEvent
ExperienceStateTimeline
AvailableAction
ForbiddenActionReason
EvidenceLink
BlueprintLink
RuntimeReportLink
```

Runtime truth boundary:

```text
TUI is workflow head, not runtime truth.
TUI cannot execute durable mutation before user confirmation.
TUI cannot let source=agent directly mutate runtime.
TUI cannot claim complete Workflow Studio.
```

Acceptance:

```text
harness_tui_command_exists
tui_accepts_natural_language_goal
tui_renders_state_timeline
tui_renders_available_actions
tui_renders_forbidden_reasons
tui_links_blueprint_report_evidence
tui_blocks_mutation_before_user_confirmation
tui_blocks_source_agent_direct_mutation
tui_no_false_green_copy
```

### V7-3 Workflow Creation And Controlled Run Experience

Dependency checklist:

```text
V7-1 accepted
V7-2 accepted
V7-3 pre-implementation review accepted
real-data acceptance plan accepted
V7-3 I/O contracts accepted
V7-3 schema files and manifest accepted
External audit accepted
Natural-language -> run chain must not be implemented before those acceptances.
Transcript-only evidence must not be written as real runtime.
Report-only evidence must not be written as real runtime.
User confirmation cannot be bypassed.
source=agent direct durable mutation remains denied.
```

Implementation outline:

```text
Convert a natural-language goal into WorkflowSpec and Diff.
Generate Workflow Blueprint / Drawio.
Require user confirmation before run.
Run the existing local Markdown technical document workflow with real provider evidence when key is configured.
Render Runtime Report, Quality and Evidence Chain links in TUI.
```

Minimum real scenario:

```text
requested_path=Desktop/技术分享 or tests/fixtures/desktop/技术分享
scanner_actual_read_count > 0
provider_invocation_count > 0
folder summaries generated
overview summary generated
quality_report.json generated
evidence_chain.json generated
```

Acceptance:

```text
natural_language_goal_generates_workflow_spec
workflow_spec_schema_valid
workflow_diff_ready_before_confirmation
blueprint_link_generated
user_confirmation_required_before_run
local_markdown_scanner_actual_read_count_gt_zero
provider_invocation_count_gt_zero
folder_summaries_generated
overview_summary_generated
quality_report_generated
evidence_chain_redacted
```

PR slices:

```text
V7-3-PR1 Mission TUI runtime bridge
V7-3-PR2 WorkflowSpec / Diff / Blueprint
V7-3-PR3 Controlled run handoff
V7-3-PR4 Reports and Evidence
V7-3-PR5 Acceptance package
```

Exit condition:

```text
V7-3 evidence package must prove the full create/run/review chain or explicitly mark missing provider/key/path evidence as BLOCKED.
V7-3 cannot pass with transcript-only, report-only, or deterministic-only evidence if the claim says runtime-backed.
```

Required contract references:

```text
docs/design/V7.x/v7_3_pre_implementation_review.md
docs/design/V7.x/v7_3_io_contracts_and_schemas.md
docs/design/V7.x/v7_3_real_data_acceptance_plan.md
docs/design/V7.x/v7_3_schema_manifest_and_examples.md
```

### V7-4 Final Small Studio Acceptance

Dependency checklist:

```text
V7-0 evidence package exists
V7-1 evidence package exists
V7-2 evidence package exists
V7-3 evidence package exists
V7-4 final acceptance data contract accepted
No FAIL / BLOCKED
PARTIAL has human proceed decision
No False Green scan PASS
Redaction scan PASS
Drawio XML validation PASS
```

Implementation outline:

```text
Collect V7-0 to V7-3 evidence packages.
Generate final HTML dashboard and acceptance-data.json.
Run claim scan, redaction scan and drawio XML validation.
Produce completion note.
```

Acceptance:

```text
V7-0 to V7-3 evidence exists
no FAIL / BLOCKED
PARTIAL has human proceed decision
No False Green scan PASS
redaction scan PASS
drawio XML valid
final dashboard opens
```

## 5. Stage Acceptance Rules

每个阶段必须：

```text
produce stage evidence package
run focused V7 tests
run V6 regression
validate V7 drawio XML
run claim scan
run redaction scan when sensitive fields are involved
perform PRD spec review
perform False Green evaluation
record next stage audit
```

## 6. Evidence Package Layout

```text
docs/design/V7.x/evidence/v7-N-stage-name/
  index.html
  result-summary.md
  acceptance-data.json
  claims-scan.md
  redaction-scan.md
  logs/
  screenshots/
  raw/
```

## 7. Global Validation Commands

```text
./.venv/bin/python -m pytest tests/test_v7_*.py -q
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V7.x/v7_current_gap_analysis.drawio
```

Frontend-related stages also run:

```text
cd apps/workflow-console && npm test -- --runInBand
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
```

## 8. Stop Conditions

停止并回到规划审计：

```text
V7 docs upgrade V6 evidence to production-ready.
Small Studio becomes full production GA.
Mission TUI becomes complete Workflow Studio.
Agent receives direct durable mutation.
Controlled runtime bypasses confirmation or policy.
Raw secret / raw prompt / raw artifact content leaks.
Evidence Chain or Runtime Report constructs runtime truth.
No False Green claim scan fails.
```
