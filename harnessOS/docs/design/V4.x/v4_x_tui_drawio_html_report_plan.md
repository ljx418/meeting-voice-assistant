# V4.x TUI / Drawio / HTML Report Plan

Status: planning document for Headless-first V4, updated for Unified Experience Rebaseline.

This plan defines the non-Web primary heads for V4.2-A and later stages.

## 1. Product Goal

V4 should let users define, inspect, run, repair, and audit workflows without depending on a full low-code Web Studio.

Primary heads:

```text
Mission Console
TUI / Command Palette
Workflow Blueprint / Drawio Renderer
Runtime Report / HTML Runtime Reports
Review Console
Evidence Chain
Thin Web Console
```

All heads must share:

```text
Experience State Machine
Interaction Orchestrator Contract
Agent Policy Layer
Report Schema
Runtime Capability Matrix
WorkflowSpec Registry
```

## 2. TUI / Command Palette

Role:

```text
Natural-language and command-driven workflow creation, diff, status, artifact review, quality review, evidence review, and governed operation handoff.
```

After V4-U4, TUI / Command Palette is treated as one implementation form of Mission Console.

V4.2-A boundary:

```text
V4.2-A implements or specifies create/diff/status/report/evidence interaction first.
Apply, publish, run, and rerun are user-confirmed transcript contracts in V4.2-A.
Generic apply/publish/run/rerun implementation belongs to V4.2-B/C unless an existing V4.1 local workflow path already supports the operation.
```

V4.2-A command target:

```text
harness tui
harness workflow create
harness workflow diff
harness workflow status
harness artifacts list
harness quality report
harness evidence show
```

Deferred mutating commands:

```text
harness workflow apply
harness workflow publish
harness workflow run
harness station rerun
```

V4.2-A target transcript:

```text
User: 创建一个工作流，递归总结 Desktop/技术分享 下的 Markdown 文件。
System: generated workflow.yaml
System: generated workflow.drawio
System: generated workflow_board.html
User: review diff
User: confirm apply
User: confirm publish
User: confirm run
System: generated artifacts.html, quality.html, evidence.html
```

The transcript may show user-confirmed apply/publish/run as evidence of the existing V4.1 local workflow path. It must not be used to claim generic controlled runtime readiness.

Governance:

```text
Agent can propose, explain, handoff, and navigate.
Agent cannot apply, publish, run, rerun, approval.respond, context.update, or business.event.emit.
Durable mutation requires user_confirmed=true.
```

## 3. Drawio Renderer

Role:

```text
Shareable, versionable, reviewable workflow visualization output.
```

After V4-U3, Drawio is a Workflow Blueprint projection generated from the shared Report Schema.

Planned files:

```text
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
quality_gate.drawio
rerun_history.drawio
```

Rendering rules:

```text
Drawio never becomes runtime truth.
Drawio is generated from WorkflowSpec plus BFF/runtime DTOs.
Event payload cannot directly mutate drawio truth.
Drawio output must be reproducible from source DTOs.
```

V4.2-A required diagrams:

```text
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
```

## 4. HTML Runtime Reports

Role:

```text
Readable runtime and audit evidence for users, reviewers, and future customer demos.
```

After V4-U3, HTML Runtime Reports are Runtime Report and Evidence Chain projections generated from the shared Report Schema.

Planned reports:

```text
workflow_board.html
station_detail.html
artifacts.html
quality.html
evidence.html
```

Report rules:

```text
Reports are read-only.
Reports must not contain hidden mutation forms.
Reports must not leak raw prompt, raw artifact content, connector payload, signed URL, token, or secret.
Reports must identify whether data came from spec, draft/version, runtime status, artifacts, quality, or evidence.
```

V4.2-A required reports:

```text
workflow_board.html
artifacts.html
quality.html
evidence.html
```

## 5. Thin Web Console

Role:

```text
Reference UI / observation and limited user-confirmed operations.
```

Thin Web Console should handle:

```text
view workflow board
view artifacts
view quality
view evidence
open HTML report
open Drawio file
open explicit user-confirmed operation handoffs where an existing BFF/runtime path supports the operation
```

Review Console is the restricted operation surface inside Thin Web Console or Mission Console. It may request user-confirmed handoffs but must not act as a full low-code editor.

Thin Web Console should not be responsible for:

```text
full drag-and-drop low-code editing
high-fidelity ComfyUI clone
complex inspector-first authoring
generic Agent executor UX
production auth or onboarding UX
```

## 6. Evidence Package

Every implementation stage should produce:

```text
1. TUI transcript
2. Drawio file
3. HTML report
4. Exported runtime / evidence JSON from governed sources
```

V4.2-A evidence path:

```text
docs/design/V4.2/evidence/headless-interaction/
  tui-transcript.txt
  workflow.yaml
  workflow.drawio
  workflow_status.drawio
  artifact_lineage.drawio
  workflow_board.html
  artifacts.html
  quality.html
  evidence.html
  result-summary.md
```

## 7. No False Green

This plan does not claim:

```text
complete Workflow Studio ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```
