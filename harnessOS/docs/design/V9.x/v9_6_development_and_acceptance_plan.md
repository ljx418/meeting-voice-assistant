# V9-6 Development And Acceptance Plan

文档状态：V9-6 detailed development and acceptance plan / Studio productization slice / implementation complete for review.

This document records the V9-6 stage plan and completed bounded Workflow Studio evidence package. It does not authorize complete Workflow Studio readiness, direct runtime truth writes or autonomous workflow editing.

## 1. Entry Baseline

V9-6 entered implementation after:

```text
Workflow Studio PRD accepted.
BFF route allowlist accepted.
browser denylist accepted.
read-only Runtime Report and Evidence Chain boundaries accepted.
manual confirmation and HumanAuthorizationRef flow accepted.
No False Green scan PASS.
Redaction scan PASS.
```

Implementation evidence is now recorded in:

```text
docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json
docs/design/V9.x/evidence/v9-6-workflow-studio/index.html
docs/design/V9.x/evidence/v9-6-workflow-studio/result-summary.md
```

## 2. Scope

V9-6 productizes workflow review and proposal workflows through Studio:

```text
workflow graph view
station Agent profile inspector
runtime status read model
artifact lineage view
Runtime Report read-only panel
Evidence Chain read-only panel
WorkflowDiff proposal panel
manual confirmation panel
natural-language workflow optimization proposal path
```

V9-6 must not:

```text
directly write WorkflowStore, WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun or Artifact.
hide runtime mutation behind browser forms.
call internal runtime routes directly from browser.
claim complete Workflow Studio readiness.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-6A Studio BFF read models | studio-state DTOs | graph, Agent profile, runtime status and lineage available |
| V9-6B Read-only review panels | Runtime Report and Evidence Chain UI evidence | no execute / apply / publish buttons |
| V9-6C WorkflowDiff proposal flow | proposal DTO and handoff refs | natural-language optimization creates proposal before mutation |
| V9-6D Manual confirmation flow | human_authorization_ref evidence | confirmation captured before durable mutation handoff |
| V9-6E Browser safety checks | network log and hidden form scan | no direct internal runtime route and no hidden mutation form |
| V9-6F Studio acceptance dashboard | HTML and acceptance data | user can inspect workflow, Agents, artifacts and evidence |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/studio/studio_review_and_workflow_diff_proposal.json
```

Negative fixtures:

```text
fixtures/studio/studio_direct_runtime_write.json
fixtures/studio/studio_hidden_mutation_form.json
fixtures/studio/studio_browser_direct_internal_runtime_route.json
fixtures/studio/nl_optimization_direct_mutation_attempt.json
fixtures/studio/ui_copy_agent_executed_automatically.json
```

## 5. Acceptance Tests

```text
v9_6_studio_loads_workflow_graph_from_bff
v9_6_station_agent_profile_is_visible
v9_6_runtime_report_is_read_only
v9_6_evidence_chain_is_read_only
v9_6_natural_language_optimization_creates_workflow_diff
v9_6_manual_confirmation_records_human_authorization_ref
v9_6_browser_no_direct_internal_runtime_routes
v9_6_hidden_mutation_form_absent
v9_6_ui_copy_no_automatic_agent_execution_claim
v9_6_claim_scan_pass
v9_6_redaction_scan_pass
```

## 6. Evidence Package

V9-6 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
studio_network_log.json
studio_hidden_form_scan.json
studio_ui_copy_claim_scan.json
manual_confirmation_evidence.json
workflow_diff_proposal_refs
claim_scan_result
redaction_scan_result
```

## 7. Stop Conditions

```text
Studio directly writes runtime truth.
Browser calls internal runtime routes directly.
Evidence Chain or Runtime Report exposes execution buttons.
Natural-language optimization mutates before confirmation.
UI copy implies automatic Agent execution.
Stage is claimed as complete Workflow Studio.
```
