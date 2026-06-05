# V7 Milestone Roadmap

文档状态：V7 current milestone roadmap。本文用于锁定 V7 剩余开发、验收门槛和出门条件。

## 1. Current Milestone Status

| Milestone | Stage | Status | Evidence Scope | Exit Claim |
| --- | --- | --- | --- | --- |
| M0 | V7-0 Planning Hardening | complete / ready for review | planning_gate | V7-0 complete: V7 small studio and explainable TUI planning gate ready for review. |
| M1 | V7-1 Small Studio Control Plane | complete / ready for review | repo_backed_fixture | V7-1 complete: small studio production pilot control plane ready for review. |
| M2 | V7-2 Explainable Mission TUI | complete / ready for review | transcript_only | V7-2 complete: explainable Mission TUI pilot ready for review. |
| M3 | V7-3 Workflow Creation And Controlled Run | complete / ready for review | real_runtime_fixture | V7-3 complete: natural-language workflow creation and controlled run experience ready for review. |
| M4 | V7-4 Final Small Studio Acceptance | complete / ready for review | final_acceptance | V7 complete: small studio production pilot and explainable TUI baseline ready for review. |

## 2. Remaining Blockers

```text
none for V7 ready-for-review baseline.
Future blockers belong to V7 closure review or V8 planning.
```

## 3. V7-3 Exit Criteria

```text
natural_language_goal_generates_workflow_spec=PASS
workflow_spec_schema_valid=PASS
workflow_diff_ready_before_confirmation=PASS
blueprint_link_generated=PASS
user_confirmation_required_before_run=PASS
local_markdown_scanner_actual_read_count_gt_zero=PASS
provider_invocation_count_gt_zero=PASS is required for V7-3 PASS
fallback_demo_only may be recorded only as PARTIAL/BLOCKED/debug evidence and cannot satisfy V7-3 completion
folder_summaries_generated=PASS
overview_summary_generated=PASS
quality_report_generated=PASS
evidence_chain_redacted=PASS
No False Green scan=PASS
redaction scan=PASS
```

## 4. V7-4 Exit Criteria

```text
V7-0 evidence package exists.
V7-1 evidence package exists.
V7-2 evidence package exists.
V7-3 evidence package exists.
No FAIL / BLOCKED.
PARTIAL has human proceed decision.
Final acceptance dashboard opens.
User can understand how to create, run, inspect and review a workflow.
Drawio XML validates.
No False Green scan passes.
Redaction scan passes.
```

## 5. Stop Conditions

```text
V7-3 writes transcript-only or report-only evidence as runtime-backed.
V7-3 evidence is removed or rewritten as transcript-only.
V7-3 bypasses user confirmation.
source=agent executes durable mutation.
Provider key absence is written as real provider-backed PASS.
fallback_demo_only is written as V7-3 PASS.
Drawio / Runtime Report / Evidence Chain constructs runtime truth.
V7-4 final claim is emitted without V7-3 PASS real_runtime_fixture evidence.
Any forbidden completion claim appears outside no-false-green context.
```

## 6. Allowed Final Claim

```text
V7 complete: small studio production pilot and explainable TUI baseline ready for review.
```

This does not prove production ready, full production GA, complete Workflow Studio, Agent executor, production controlled executor, production-ready external app support or full multi-Agent orchestration.
