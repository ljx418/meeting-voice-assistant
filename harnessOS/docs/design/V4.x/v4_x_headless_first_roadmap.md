# V4.x Headless-First Roadmap

Status: roadmap revision after V4.6 governed Agent workflow builder UX completion and Unified Experience Rebaseline.

This document replaces the previous "Full Web Low-Code Studio first" emphasis with a Headless-first multi-head workflow platform route. It is a planning document, not an implementation completion note.

Current baseline:

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

Still forbidden claims:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

Audit correction:

V4.2-A command names are interaction contracts and evidence targets, not a promise that generic controlled execution was implemented in V4.2-A. V4.2-B defined the implementation gate. V4.2-C now provides the dev/local controlled runtime MVP for user-confirmed start, station rerun, attempt history, downstream stale, and runtime evidence.

## 1. Roadmap Decision

V4 no longer treats a full drag-and-drop Web Workflow Studio as the main product path.

The main line was first reframed as:

```text
Headless Workflow Core
+ TUI / Command Palette
+ Drawio Workflow Visualization
+ HTML Runtime Reports
+ Thin Web Console
```

After V4.6, the V4.x route is further consolidated as:

```text
Headless Workflow Core
+ Mission Console
+ Workflow Blueprint
+ Runtime Report
+ Review Console
+ Evidence Chain
+ Interaction Orchestrator
+ Experience State Machine
+ Agent Policy Layer
+ Runtime Capability Matrix
+ Report Schema
+ WorkflowSpec Registry
```

Workflow Studio remains useful as a reference UI and Thin Web Console, but it is not the current primary delivery surface.

## 2. Why The Route Changes

The previous direction risked concentrating too much work in a complex low-code frontend:

```text
Full Web Low-Code Studio first
  -> drag nodes
  -> complex canvas
  -> inspector forms
  -> high-fidelity interaction polish
```

That route can be valuable later, but it is too expensive as the V4 main path. The project value is better served by proving that the same workflow core can be defined, visualized, run, inspected, repaired, and audited through multiple heads.

## 3. New Product Shape

### Headless Core

The durable facts remain backend/runtime objects:

```text
WorkflowSpec
WorkflowTemplate
WorkflowDraft
WorkflowVersion
WorkflowInstance
Station
StationRun
Artifact
ArtifactLineage
QualityEvaluation
Approval
WorkflowPatch
WorkflowContext
OperationEvidence
GovernanceReview
```

### Heads

```text
TUI / Command Palette
  Natural-language and command-driven workflow creation, modification, status review, report review, and governed operation handoff. Controlled run/rerun execution is available at dev/local MVP level after V4.2-C.

Drawio Renderer
  Workflow structure, runtime status, artifact lineage, quality gate, and rerun history visualization.

HTML Report
  Runtime board, station detail, artifacts, quality, errors, and evidence chain reporting.

Thin Web Console
  Lightweight browser viewing and limited user-confirmed operations.

Workflow Studio
  Reference UI only, not the primary current mainline.
```

## 4. Revised V4 Stages

### V4.1 Local Knowledge Workflow MVP / 本地知识工作流 MVP

Status: complete for dev/local validation.

V4.1 proves one real workflow slice:

```text
Desktop/技术分享
  -> recursive Markdown scan
  -> per-folder summaries
  -> overview summary
  -> quality report
  -> artifact and evidence review
```

Allowed claim:

```text
V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation.
```

### V4.2-A Headless Interaction Pivot / Headless 交互转向

Goal: expand the V4.1 workflow from a browser workbench experience into a headless interaction baseline.

Primary outputs:

```text
workflow.yaml
workflow.json
workflow.schema.json
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
workflow_board.html
station_detail.html
artifacts.html
quality.html
evidence.html
TUI transcript
exported evidence JSON from existing governed sources
```

Planned command surface:

```text
harness tui
harness workflow create
harness workflow diff
harness workflow status
harness artifacts list
harness quality report
harness evidence show
```

Deferred mutating command surface:

```text
harness workflow apply
harness workflow publish
harness workflow run
harness station rerun
```

In V4.2-A, deferred mutating commands were documented as confirmation contracts and could appear in transcripts only when backed by the existing V4.1 local workflow path. V4.2-C adds a BFF-only controlled runtime MVP for dev/local validation.

Allowed claim:

```text
V4.2-A complete: headless interaction baseline ready for local workflow validation.
```

### V4.2-B Controlled Runtime Design Gate / 受控运行时设计门禁

Goal: define the controlled runtime implementation gate before any generic runtime behavior is added.

Required behavior:

```text
machine-readable design gate contract
real-data acceptance standard
runtime evidence contract
route and capability guard
PRD and architecture audit
no false-green guard
```

Allowed claim:

```text
V4.2-B complete: controlled runtime design gate ready for implementation review.
```

### V4.2-C Controlled Runtime MVP / 受控运行时 MVP

Status: complete for dev/local validation.

Goal: implement the governed runtime foundation required by V4.3, V4.4, and V4.5.

Required behavior:

```text
user-confirmed workflow start
user-confirmed station rerun
StationRun attempt history
downstream stale propagation
artifact read/write sandbox
policy-controlled connector / model invocation
runtime result evidence
timeout baseline
kill switch baseline
```

Governance boundaries:

```text
source=agent cannot execute mutation
user confirmation required for start/rerun/publish/apply/approval/context mutation
high-risk actions require approval gate
event payload never becomes truth
executor reads only redacted or approved inputs
```

Allowed claim:

```text
V4.2-C complete: controlled runtime MVP ready for dev/local validation.
```

Still forbidden:

```text
Agent executor ready
production-ready external app support
autonomous workflow editing ready
```

### V4.3 Serial Multi-Agent Video Workflow MVP / 串行多 Agent 视频工作流 MVP

Status:

```text
V4.3 complete: serial multi-Agent video workflow MVP ready for dev/local validation.
```

Goal: prove a serial multi-Agent video creation workflow with visible per-station outputs.

Reference stations:

```text
Writer Agent
Storyboard Agent
Copywriting Agent
Editing Plan Agent
Quality Review Agent
Publish Preparation Agent
```

### V4-U0 to V4-U6 Unified Experience Rebaseline / 统一体验收口

Status: current forward route after V4.6.

Goal: unify V4.1-V4.6 dev/local evidence into a single user experience:

```text
用户说目标
 -> Mission Console 捕获意图
 -> 生成 WorkflowSpec / Diff
 -> Workflow Blueprint 理解结构
 -> 用户确认
 -> Runtime Report 观察运行
 -> Review Console 做局部重跑 / 修复 / 确认
 -> Evidence Chain 审计复盘
```

Stages:

```text
V4-U0 Documentation Rebase
V4-U1 Experience State Machine
V4-U2 Interaction Orchestrator Contract
V4-U3 Report Schema And Projection Unification
V4-U4 Mission Console UX
V4-U5A Scenario Evidence Hardening
V4-U5B Experience State Projection
V4-U5C Mission Console Closed Loop
V4-U5D Review Console And Evidence Chain
V4-U5 Scenario Path Acceptance Package
V4-U6 Unified Experience Gate
```

This rebaseline does not add Agent executor, production controlled executor, production external app support, or complete Workflow Studio readiness.

Interaction priority:

```text
TUI create and refine
Drawio workflow visualization
HTML artifact and quality report
Thin Web Console status observation
```

Allowed claim:

```text
V4.3 complete: serial multi-Agent video workflow MVP ready for dev/local validation.
```

### V4.4 Parallel Multi-Agent Deliberation Workflow MVP / 并行多 Agent 讨论工作流 MVP

Status:

```text
V4.4 complete: parallel multi-Agent deliberation workflow MVP ready for dev/local validation.
```

Goal: prove a Roman forum style parallel deliberation workflow.

Topology:

```text
Orchestrator
  -> Persona Agent A
  -> Persona Agent B
  -> Persona Agent C
  -> Synthesis Node
  -> Contradiction Review
```

Interaction priority:

```text
workflow.yaml topology
drawio parallel structure
HTML persona outputs
TUI deliberation round control
```

Allowed claim:

```text
V4.4 complete: parallel multi-Agent deliberation workflow MVP ready for dev/local validation.
```

### V4.5 Long-Running Engineering Workflow MVP / 长时工程工作流 MVP

Status:

```text
V4.5 complete: long-running engineering workflow MVP ready for dev/local validation.
```

Goal: prove a durable engineering workflow that can show stage state, artifacts, quality gates, evidence, and manual checkpoints.

Reference lifecycle:

```text
product planning
specification
project blueprint
architecture review
substage plan audit
substage architecture review
implementation
development acceptance
code review
E2E acceptance
human confirmation
```

Interaction priority:

```text
TUI task control
HTML durable task board
Drawio project blueprint
Evidence report
Quality gate report
```

Allowed claim:

```text
V4.5 complete: long-running engineering workflow MVP ready for dev/local validation.
```

### V4.6 Agent Workflow Builder UX / Agent 工作流搭建体验

Status:

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

Goal: make Agent useful as a governed workflow-building entrypoint across TUI and Thin Web Console.

Required capabilities:

```text
Agent asks clarifying questions
Agent generates workflow spec
Agent explains workflow plan
Agent creates patch proposal
Agent debugs failed workflow
Agent proposes repair
Agent cannot auto apply
Agent cannot auto run
```

Allowed claim:

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

## 5. Old Route vs New Route

| Dimension | Full Web Low-Code Studio first | Headless Core + TUI + Drawio + HTML Report + Thin Web Console |
| --- | --- | --- |
| Implementation complexity | High frontend and interaction complexity before runtime value is fully proven. | Lower first-step complexity; proves core outputs before visual polish. |
| User experience | Rich if completed, but slow to reach a reliable MVP. | Practical for power users and validation; Web remains a thin observation head. |
| Visualization ability | Canvas-heavy and browser-bound. | Drawio artifacts are shareable, reviewable, and versionable. |
| Long-running tasks | Hard to express only through an interactive canvas. | HTML reports and durable evidence are better suited to long tasks. |
| Multi-Agent support | Risks becoming UI simulation without runtime semantics. | Workflow specs and reports can model serial/parallel semantics first. |
| Customer demo | Visually attractive but fragile if runtime is incomplete. | Demo can show spec, run, artifacts, quality, and evidence as durable outputs. |
| Engineering speed | Slow due to UI polish and edge interaction work. | Faster because each head consumes the same core outputs. |
| Future extensibility | May overfit to one Web app. | Multi-head architecture can support TUI, reports, Web, and future business apps. |

## 6. Stage Gate

Every future stage completion note must include:

```text
Spec Drift Evaluation
False Green Evaluation
Next Stage Audit
Proceed Decision
No False Green Statement
```

Stop if:

```text
Spec drift risk = HIGH
False green risk = HIGH
The stage requires changing the V4.0 governance boundary
The stage requires Agent executor
The stage requires production auth
The stage requires full Web Studio as prerequisite
```

## 7. V4 Success Standard

V4 success is no longer defined by a high-fidelity Web Studio alone.

V4 succeeds when:

```text
Users can define workflows through natural language or TUI.
The system can generate workflow specs.
The system can generate Drawio visualization.
Users can confirm and run.
Each station state and output artifact is visible.
Failed stations can be rerun under user confirmation.
Quality reports are visible.
Evidence chains are auditable.
The same core can be consumed by TUI, HTML reports, Thin Web Console, and future business apps.
```
