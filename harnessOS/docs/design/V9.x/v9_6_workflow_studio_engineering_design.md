# V9-6 Workflow Studio Engineering Design

文档状态：V9-6 engineering design / implementation complete for review。

## 1. Boundary

Workflow Studio is a productization slice through BFF / DTO / read models. It cannot directly write WorkflowStore, WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun or Artifact. The implemented V9-6 fixture proves the bounded read-model/productization slice only; it does not prove complete Workflow Studio readiness.

## 2. Panels

```text
Mission Console
Workflow Blueprint
Agent Station Inspector
Runtime Report
Review Console
Evidence Chain
Human Authorization Review
Studio Audit Export
```

## 3. BFF Route Allowlist

```text
GET /bff/v9/studio-state
GET /bff/v9/runtime-report
GET /bff/v9/evidence-chain
GET /bff/v9/workflow-blueprint
POST /bff/v9/workflow-diff-proposal
POST /bff/v9/manual-confirmation
POST /bff/v9/review-handoff
```

Browser denylist:

```text
/v1/rpc
/v1/events/subscribe
/v1/internal/*
/internal/v9/*
```

## 4. Manual Confirmation Flow

```text
user reviews proposal.
Studio posts manual confirmation to BFF.
BFF records human_authorization_ref.
Runtime action still requires CapabilityResolver and high-risk approval when applicable.
```

## 5. UI Safety Tests

```text
studio_browser_no_direct_runtime_truth
studio_browser_no_direct_v1_rpc
studio_browser_no_direct_events_subscribe
studio_hidden_mutation_form_absent
runtime_report_readonly_no_execute_buttons
evidence_chain_readonly_no_execute_buttons
manual_confirmation_records_human_authorization_ref
studio_copy_no_agent_executed_automatically
```

## 6. Evidence Package

```text
studio_network_log.json
studio_hidden_form_scan.json
studio_ui_copy_claim_scan.json
studio_manual_confirmation_evidence.json
studio_bff_route_allowlist_result.json
studio_browser_denylist_result.json
```
