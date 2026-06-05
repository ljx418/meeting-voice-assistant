# V9-6 Workflow Studio Productization PRD

文档状态：V9-6 separate Studio PRD / planned only。

## 1. Product Goal

V9-6 productizes a bounded Workflow Studio experience on top of BFF / DTO / read-model boundaries. It does not deliver complete Workflow Studio ready unless a separate future Studio acceptance gate proves that claim.

Allowed claim:

```text
V9-6 complete: Workflow Studio productization slice ready for review.
```

Forbidden claim:

```text
complete Workflow Studio ready
```

## 2. Studio Scope

Allowed panels:

```text
Mission Console
Workflow Blueprint
Runtime Report
Review Console
Evidence Chain
Agent Station Inspector
Human Authorization Review
Studio Audit Export
```

Disallowed by default:

```text
direct WorkflowStore write
direct WorkflowDraft write
direct WorkflowVersion write
direct WorkflowInstance write
direct StationRun write
direct Artifact write
hidden mutation form
browser direct /v1/rpc
browser direct /v1/events/subscribe
```

## 3. BFF / DTO Boundary

Studio must use:

```text
BFF route allowlist
browser network denylist
read-only report DTOs
manual confirmation DTO
human_authorization_ref capture flow
EvidenceLink / RuntimeReportLink / BlueprintLink
```

Studio must not construct runtime truth. Admin operations create proposals or handoffs, not direct writes.

## 4. UI Acceptance Matrix

```text
runtime_report_readonly_no_hidden_form
evidence_chain_readonly_no_execute_buttons
review_console_generates_handoff_not_direct_execution
manual_confirmation_records_human_authorization_ref
browser_no_direct_v1_rpc
browser_no_direct_v1_events_subscribe
browser_no_direct_internal_runtime_routes
studio_copy_no_agent_executed_or_auto_applied_claim
```

## 5. Evidence Package

Required evidence:

```text
studio_acceptance_data.json
browser_network_log.json
hidden_form_scan.json
ui_copy_claim_scan.json
manual_confirmation_evidence.json
runtime_report_readonly_evidence.json
evidence_chain_readonly_evidence.json
```

## 6. Stop Conditions

```text
Studio directly writes runtime truth.
Browser calls internal runtime route directly.
Evidence Chain exposes Execute / Run / Apply / Publish buttons.
Report Review becomes execution panel.
UI copy says Agent executed automatically.
```
