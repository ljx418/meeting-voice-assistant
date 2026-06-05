# V7-3 I/O Contracts And Schemas

文档状态：V7-3 implementation contract / external audit draft。本文锁定 V7-3 的最小 I/O 合同，避免实现阶段自行推断。

## 1. Runtime Truth Boundary

```text
Mission TUI is a workflow head, not runtime truth.
WorkflowSpec is a portable spec, not WorkflowDraft / WorkflowVersion.
WorkflowDiff is a proposal, not a durable mutation.
Workflow Blueprint / Drawio is visualization only.
Runtime Report is a read model.
Evidence Chain is a read-only audit view.
Only user_confirmed controlled runtime handoff may execute durable mutation.
```

## 2. NaturalLanguageGoal

用途：用户在 `harness tui` 输入的目标。

Required fields:

```text
goal_id
natural_language_goal
source=mission_tui
actor_type=human_user
tenant_id
workspace_id
project_id
app_id
created_at
correlation_id
```

Validation:

```text
Only the local Markdown technical document workflow is supported in V7-3.
If goal cannot be mapped to the supported workflow, status=BLOCKED with reason=unsupported_goal.
No prompt or raw file content is stored in this DTO.
```

## 3. WorkflowSpecDraft

用途：从目标生成的可审查 workflow spec。

Required sections:

```text
metadata
stations
edges
artifact_contracts
quality_rules
approval_points
context_refs
evidence_refs
runtime_truth_boundary
```

Required metadata fields:

```text
workflow_spec_id
schema_version
goal_id
workflow_kind=local_markdown_technical_document_summary
created_by=mission_tui
created_at
source_refs
```

V7-3 supported stations:

```text
folder_authorization
markdown_scan
per_folder_summary
overview_summary
quality_check
runtime_report
evidence_record
```

Boundary:

```text
WorkflowSpecDraft cannot write WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun.
Unknown workflow_kind is rejected in V7-3.
Unknown fields are rejected by strict schema when schema files are added during implementation.
```

## 4. WorkflowDiff

用途：展示用户确认前将要创建/运行的变化。

Required fields:

```text
workflow_diff_id
goal_id
workflow_spec_id
change_summary
stations_added
edges_added
artifact_contracts_added
approval_points_added
requires_user_confirmation=true
durable_mutation_before_confirmation=false
created_at
```

Acceptance:

```text
WorkflowDiff must be ready before UserConfirmed.
WorkflowDiff cannot contain runtime_result_ref.
WorkflowDiff cannot claim workflow has run.
```

## 5. BlueprintLink

用途：指向 Workflow Blueprint / Drawio 输出。

Required fields:

```text
blueprint_id
workflow_spec_id
drawio_ref
visualization_only=true
xml_validated
created_at
```

Boundary:

```text
Drawio cannot construct runtime truth.
Drawio must not include token, raw prompt, raw file content, raw connector payload, signed URL or raw artifact content.
```

## 6. UserConfirmedRunHandoff

用途：用户确认后发起受控运行。

Required fields:

```text
handoff_id
workflow_spec_id
workflow_diff_id
source=mission_tui
actor_type=human_user
user_confirmed=true
human_authorization_ref
operation=workflow.instance.start
target_refs
policy_decision
capability_decision
risk_flags
created_at
correlation_id
```

Target refs:

```text
requested_path_ref
authorized_folder_ref
workflow_instance_target_ref
```

Validation:

```text
source=agent is rejected.
user_confirmed=false is rejected.
missing human_authorization_ref is rejected.
target_refs must point only to authorized local folder or fixture.
```

## 7. LocalDocumentWorkflowRunResult

用途：V7-3 对 V4-U5E 本地文档工作流结果的封装。

Required fields:

```text
workflow_instance_id
status
evidence_scope
runtime_backed
real_llm_backed
fallback_demo_only
scanner_actual_read_count
provider_invocation_count
provider
model_ref
provider_config_source
artifact_refs
quality_report_ref
evidence_chain_ref
redaction_status
```

Pass rule:

```text
runtime_backed=true only if scanner_actual_read_count > 0 and provider_invocation_count > 0.
real_llm_backed=true only if provider is not fake and provider invocation evidence exists.
fallback_demo_only cannot satisfy V7-3 completion.
```

## 8. RuntimeReportLink / QualityReportLink / EvidenceChainLink

用途：TUI 和最终报告中的只读链接。

Required fields:

```text
link_id
workflow_instance_id
source_ref
readonly=true
redaction_status
created_at
```

EvidenceChainLink additional fields:

```text
provider
model_ref
prompt_template_refs
input_artifact_refs
output_artifact_refs
runtime_result_refs
correlation_ids
raw_prompt_exposed=false
raw_file_content_exposed=false
token_exposed=false
```

## 9. State Line Contract

V7-3 runtime-backed state line:

```text
IntentCaptured
SpecDrafted
SchemaValidated
DiffReady
AwaitingConfirmation
UserConfirmed
RuntimeStarted
RuntimeReported
EvidenceRecorded
```

If run is blocked:

```text
IntentCaptured
SpecDrafted
SchemaValidated
DiffReady
AwaitingConfirmation
UserConfirmed
RuntimeBlocked
EvidenceRecorded
```

Blocked reasons:

```text
unsupported_goal
missing_user_confirmation
source_agent_denied
folder_authorization_missing
folder_path_forbidden
llm_key_missing
provider_unavailable
redaction_failed
schema_invalid
```

## 10. Evidence Package Data

`acceptance-data.json` must include:

```text
stage_id=V7-3
status=PASS | PARTIAL | FAIL | BLOCKED
evidence_scope=real_runtime | fallback_demo_only | transcript_only | report_only | blocked
runtime_backed
transcript_only
report_only
fallback_demo_only
scanner_actual_read_count
provider_invocation_count
user_confirmed
source_agent_denied
workflow_spec_schema_valid
drawio_xml_valid
claim_scan
redaction_scan
missing_evidence
evidence_refs
```

