# V4.2-A Headless Interaction Pivot Plan

Status: planned.

Allowed planning claim:

```text
V4.2-A plan ready: headless interaction pivot prepared for implementation review.
```

Allowed completion claim after implementation:

```text
V4.2-A complete: headless interaction baseline ready for local workflow validation.
```

Forbidden claims:

```text
complete Workflow Studio ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```

## 1. Stage Goal

V4.2-A converts the V4.1 local recursive Markdown workflow from a browser-first workbench experience into a Headless-first multi-head baseline:

```text
WorkflowSpec
+ TUI / Command Palette
+ Drawio renderer
+ HTML report generator
+ Thin Web Console observation entry
```

This stage is not the controlled execution runtime implementation. V4.2-B owns controlled execution runtime MVP.

Audit correction:

```text
V4.2-A command names are interaction contracts and evidence targets.
Generic apply/publish/run/rerun implementation is not part of V4.2-A.
Mutating command transcript steps may only be used when backed by the existing V4.1 local workflow path.
Generic controlled execution belongs to V4.2-B/C.
```

## 2. Non-Goals

V4.2-A must not implement:

```text
full Web Workflow Studio
generic Agent executor
controlled executor runtime
production filesystem permission model
production auth
multi-Agent video workflow
parallel Agent deliberation
long-running engineering task board
production-ready external app support
```

## 3. PR Slices

### PR1 Roadmap And Document Baseline

Add and update Headless-first planning documents. Freeze V4.2-A as the next stage before controlled runtime work.

Deliverables:

```text
docs/design/V4.x/v4_x_headless_first_roadmap.md
docs/design/V4.x/v4_x_headless_api_surface_map.md
docs/design/V4.x/v4_x_tui_drawio_html_report_plan.md
docs/design/V4.2/v4_2_headless_interaction_pivot_plan.md
docs/design/V4.2/v4_2_headless_interaction_pivot_completion_note.md
```

### PR2 Workflow Spec Planning

Plan portable workflow spec outputs:

```text
workflow.yaml
workflow.json
workflow.schema.json
```

Minimum planned sections:

```text
metadata
stations
edges
artifact_contracts
quality_rules
approval_points
context_refs
evidence_refs
```

Boundary:

```text
WorkflowSpec is not runtime truth.
WorkflowSpec cannot directly mutate WorkflowDraft / WorkflowVersion / WorkflowStore.
```

### PR3 TUI / Command Palette Planning

Plan read/spec/report commands:

```text
harness tui
harness workflow create
harness workflow diff
harness workflow status
harness artifacts list
harness quality report
harness evidence show
```

Plan deferred mutating command contracts:

```text
harness workflow apply
harness workflow publish
harness workflow run
harness station rerun
```

Mutation boundary:

```text
apply / publish / run / rerun require user_confirmed=true
source=agent cannot execute mutation
generic start/rerun implementation is V4.2-B/C scope
```

### PR4 Drawio Renderer Planning

Plan outputs:

```text
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
quality_gate.drawio
rerun_history.drawio
```

V4.2-A required output:

```text
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
```

### PR5 HTML Report Planning

Plan reports:

```text
workflow_board.html
station_detail.html
artifacts.html
quality.html
evidence.html
```

Reports are read-only and must not leak sensitive data.

### PR6 Thin Web Console Repositioning

Thin Web Console remains a browser observation and limited user-confirmation head.

It handles:

```text
view workflow board
view artifacts
view quality
view evidence
open HTML report
open Drawio file
open explicit user-confirmed operation handoffs where an existing BFF/runtime path supports the operation
```

It does not carry:

```text
complete low-code editing
generic Agent execution
full drag-and-drop Workflow Studio as current mainline
```

## 4. Acceptance Plan

V4.2-A implementation must generate:

```text
docs/design/V4.2/evidence/headless-interaction/tui-transcript.txt
docs/design/V4.2/evidence/headless-interaction/workflow.yaml
docs/design/V4.2/evidence/headless-interaction/workflow.drawio
docs/design/V4.2/evidence/headless-interaction/workflow_status.drawio
docs/design/V4.2/evidence/headless-interaction/artifact_lineage.drawio
docs/design/V4.2/evidence/headless-interaction/workflow_board.html
docs/design/V4.2/evidence/headless-interaction/artifacts.html
docs/design/V4.2/evidence/headless-interaction/quality.html
docs/design/V4.2/evidence/headless-interaction/evidence.html
docs/design/V4.2/evidence/headless-interaction/result-summary.md
```

Behavioral acceptance:

```text
User can use TUI to create the Desktop/技术分享 workflow.
System can generate workflow spec.
System can generate Drawio.
User can confirm and run through the existing V4.1 local workflow path or a clearly marked transcript; generic run is deferred.
HTML report can show station status, artifacts, quality, and evidence.
source=agent cannot execute mutation.
Browser has no direct /v1/rpc.
Browser has no direct /v1/events/subscribe.
No token / raw payload leakage.
No false-green claims.
```

## 5. Risk Controls

Stop conditions:

```text
Spec Drift Risk = HIGH
False Green Risk = HIGH
Implementation requires changing V4.0 governance boundary
Implementation requires Agent executor
Implementation requires production auth
Implementation requires full Web Studio as prerequisite
```

Completion note must include:

```text
Spec Drift Evaluation
False Green Evaluation
Next Stage Audit
Proceed Decision
No False Green Statement
```

## 6. Next Stage Audit

Before starting V4.2-B, audit whether the planned controlled execution runtime can preserve:

```text
source=agent cannot execute mutation
user confirmation required
high-risk action approval-gated
EventBridge refresh-only
executor reads only redacted or approved inputs
```
