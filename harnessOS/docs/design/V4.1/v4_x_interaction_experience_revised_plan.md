# V4.x Interaction Experience Revised Development Plan

Status: revised post V4.1 completion baseline; updated for Headless-first V4 roadmap.

Stage-gate update:

All future stages must follow `docs/design/V4.1/v4_1_stage_gate_development_plan.md`. Stage names are bilingual, and every stage completion note must include Spec Drift Evaluation / 规格漂移评估, False Green Evaluation / 虚假验收评估, Next Stage Audit / 下一阶段审计, and a proceed decision.

Headless-first update:

V4.x no longer treats a complete Web low-code Workflow Studio as the current mainline. The route is now:

```text
Headless Workflow Core
+ TUI / Command Palette
+ Drawio Workflow Visualization
+ HTML Runtime Reports
+ Thin Web Console
```

Workflow Studio remains as Reference UI / Thin Web Console, but the main product path is Headless-first. The latest roadmap source is:

```text
docs/design/V4.x/v4_x_headless_first_roadmap.md
docs/design/V4.x/v4_x_headless_api_surface_map.md
docs/design/V4.x/v4_x_tui_drawio_html_report_plan.md
docs/design/V4.2/v4_2_headless_interaction_pivot_plan.md
```

This document now re-centers the V4.x roadmap around Headless-first workflow interaction and three later target interaction experiences:

1. Serial multi-Agent workflow orchestration, using a video creation pipeline as the reference scenario.
2. Parallel multi-Agent deliberation workflow orchestration, using a Roman forum style discussion workflow as the reference scenario.
3. Long-running engineering workflow orchestration, using a large coding task lifecycle as the reference scenario.

V4.1 is now the current dev/local interaction baseline: the local recursive Markdown folder summary workflow MVP is ready for dev/local validation. V4.1 does not prove complete Workflow Studio, complete AgentTalkWindow, Agent executor, controlled executor, autonomous workflow editing, production-ready external app support, or full multi-Agent orchestration.

## 1. Current Support Assessment

### 1.1 What Current V4.1 Can Support

Current V4.1 can support the proposal-first shell plus one real dev/local local knowledge workflow:

1. Workflow Console can render a board, station cards, events, artifacts, approvals, quality summaries, context, Patch Diff, and governance evidence from BFF DTOs.
2. Agent assistant can accept natural-language input and create deterministic proposal / handoff objects.
3. Canvas and Inspector can create WorkflowPatch proposals.
4. User-confirmed apply / reject / publish paths exist for governed patch editing.
5. Operation panels require explicit user confirmation for approval, context, business event, patch apply, patch reject, and publish.
6. EventBridge is used only to trigger refresh; UI truth is reloaded from BFF.
7. Browser smoke tests enforce no direct `/v1/rpc` or `/v1/events/subscribe`.
8. Agent can propose the `Desktop/技术分享` recursive Markdown folder summary workflow.
9. User-confirmed apply, publish, run, failure rerun, refresh recovery, artifacts, quality report, and governance evidence are covered for the V4.1 local workflow slice.

### 1.2 What Current V4.1 Cannot Support Yet

Current V4.1 cannot fully support the three requested larger experiences:

1. It cannot let Agent autonomously build, publish, run, debug, and rerun a real workflow end to end.
2. It cannot execute a real multi-Agent video pipeline with custom per-station model, tool, skill, role, and capability bindings.
3. It cannot run arbitrary station-level local reruns with downstream propagation; V4.1 rerun is limited to the local Markdown workflow slice.
4. It cannot run true parallel Agent deliberation, cross-Agent memory exchange, or orchestrator-mediated synthesis.
5. It cannot run a long coding workflow with durable task board, stage quality gates, substage audit, engineering artifact tracking, and manual confirmation gates.
6. It cannot safely expose local workspace filesystem operations as a user-facing workflow capability beyond existing lower-level connector / artifact primitives.
7. It cannot claim controlled executor or Agent executor readiness.

Current product status for the local knowledge workflow:

```text
V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation.
```

The project has enough architecture foundation to start V4.2-A Headless Interaction Pivot. Multi-Agent and production-facing experiences remain future stages.

## 2. Revised V4.x Roadmap

### V4.1 Local Knowledge Workflow MVP / 本地知识工作流 MVP

Reference scenario:

`Desktop/技术分享` recursive folder summary workflow.

Goal:

Prove a real user can ask Agent to create a local document workflow, confirm the generated workflow, configure a folder input, run the workflow, and receive per-folder Markdown summaries plus an overview summary.

Key deliverables:

1. Local folder input node with explicit read authorization.
2. Recursive folder scan node.
3. Markdown parse node.
4. Per-child-folder grouping node.
5. Per-folder summary node.
6. Overview summary node.
7. Quality report node.
8. Artifact publishing to visible summary files.
9. Browser automation acceptance using the V4.1 acceptance standard.

Allowed completion claim:

```text
V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation.
```

Still forbidden:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
```

### V4.2-A Headless Interaction Pivot / Headless 交互转向

Goal:

Extend the V4.1 local knowledge workflow from a browser workbench experience into a Headless-first interaction baseline.

Required heads:

1. WorkflowSpec as portable workflow definition.
2. TUI / Command Palette as the primary creation, review, report, and governed operation handoff entry.
3. Drawio renderer for workflow, status, and artifact lineage visualization.
4. HTML runtime reports for board, artifacts, quality, and evidence review.
5. Thin Web Console as observation and limited user-confirmed operation surface.

Required planned outputs:

```text
workflow.yaml / workflow.json
workflow.schema.json
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
workflow_board.html
station_detail.html
artifacts.html
quality.html
evidence.html
```

Required V4.2-A read/spec/report commands:

```text
harness tui
harness workflow create
harness workflow diff
harness workflow status
harness artifacts list
harness quality report
harness evidence show
```

Deferred mutating command contracts:

```text
harness workflow apply
harness workflow publish
harness workflow run
harness station rerun
```

In V4.2-A, apply/publish/run/rerun must be treated as user-confirmed transcript or handoff contracts unless an existing V4.1 local workflow path already backs the operation. Generic controlled execution belongs to V4.2-B/C.

Allowed completion claim:

```text
V4.2-A complete: headless interaction baseline ready for local workflow validation.
```

Forbidden scope:

```text
complete Workflow Studio ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```

### V4.2-B Controlled Execution Runtime MVP / 受控执行运行时 MVP

Goal:

Implement the minimum governed execution layer required by V4.1, V4.3, V4.4, and V4.5 without violating V4.0-Q/Y gates.

Required capabilities:

1. User-confirmed workflow start.
2. User-confirmed station rerun.
3. Station attempt history.
4. Downstream stale propagation.
5. Artifact read/write through approved sandbox boundaries.
6. Connector/model invocation through policy-controlled runtime.
7. Runtime evidence generation.
8. Kill switch and timeout baseline.

Governance requirements:

1. `source=agent` cannot execute mutation.
2. User confirmation is mandatory for start, rerun, publish, apply, approval, and context mutation.
3. High-risk actions require approval gate.
4. Event payload never becomes truth.
5. Executor reads redacted or policy-approved inputs only.

Allowed completion claim:

```text
V4.2 complete: controlled execution runtime MVP ready for dev/local validation.
```

This is the earliest stage where a limited controlled executor claim may be considered, but only if the implementation passes the Q/Y gate requirements and the V4.2 acceptance suite.

### V4.3 Serial Multi-Agent Video Workflow MVP / 串行多 Agent 视频工作流 MVP

Reference scenario:

Video creation pipeline with writer, storyboard, copywriting, editing, quality review, and publish-prep stations.

Goal:

Support a serial multi-Agent workflow where each station has a configurable Agent descriptor and each station output is visible, rerunnable, and usable as downstream input.

Required station model:

1. Writer Agent.
2. Storyboard Agent.
3. Copywriting Agent.
4. Editing Plan Agent.
5. Quality Review Agent.
6. Publish Preparation Agent.

Required per-station configuration:

1. Role.
2. Goal.
3. Model reference.
4. Tool references.
5. Skill references.
6. Input artifact contract.
7. Output artifact contract.
8. Quality rules.
9. Approval policy.

Required runtime behavior:

1. Start workflow from UI after user confirmation.
2. Execute stations in serial order.
3. Display each station run status.
4. Display each station output artifact.
5. Rerun any station after user confirmation.
6. Preserve old attempt and old output.
7. Propagate rerun output to downstream stations.
8. Show downstream stale state before rerun.

Acceptance focus:

1. User can deploy and run a video workflow.
2. User can inspect writer, storyboard, copywriting, editing, review, and publish-prep outputs.
3. User can customize at least role, model, tools, skills, and prompt for one station.
4. User can rerun one middle station and then continue downstream execution.

Allowed completion claim:

```text
V4.3 complete: serial multi-Agent video workflow MVP ready for dev/local validation.
```

### V4.4 Parallel Multi-Agent Deliberation Workflow MVP / 并行多 Agent 讨论工作流 MVP

Reference scenario:

Roman forum workflow: one orchestrator node assigns a project question to multiple Agents with different personalities or viewpoints, lets them exchange ideas, and routes all views to a synthesis node.

Goal:

Support parallel branches, shared prompt context, optional cross-Agent inspiration inputs, and final synthesis.

Required topology:

1. Orchestrator node.
2. Multiple parallel persona Agent nodes.
3. Optional cross-inspiration edges between persona nodes.
4. Synthesis node.
5. Quality / contradiction review node.

Required persona configuration:

1. Persona name.
2. Viewpoint.
3. Reasoning style.
4. Model reference.
5. Tool references.
6. Memory / context input policy.
7. Output artifact contract.

Required runtime behavior:

1. Orchestrator freezes the shared question.
2. Persona Agents run in parallel.
3. Each persona output is visible as a separate artifact.
4. Optional second-pass reflection can use other personas' outputs as input.
5. Synthesis node receives all final persona outputs.
6. Final report preserves viewpoint attribution.

Acceptance focus:

1. User can create a Roman forum style workflow from Agent assistant.
2. User can configure at least three different persona Agents.
3. Parallel station states are visible.
4. Persona outputs are independent artifacts.
5. Synthesis output cites each persona's contribution.

Allowed completion claim:

```text
V4.4 complete: parallel multi-Agent deliberation workflow MVP ready for dev/local validation.
```

### V4.5 Long-Running Engineering Workflow MVP / 长时工程工作流 MVP

Reference scenario:

Large coding task lifecycle:

```text
产品规划
规格梳理
项目计划蓝图绘制
总架构评审
项目子阶段计划审计
项目子阶段架构评审
项目子阶段开发实施
开发验收
代码检视
项目子阶段端到端验收
人工确认
```

Goal:

Support a durable long-running task board where each stage is an Agent station with visible artifacts, quality gates, review status, rerun support, and manual approval checkpoints.

Required stage types:

1. Planning stage.
2. Specification stage.
3. Blueprint stage.
4. Architecture review stage.
5. Subphase plan audit stage.
6. Subphase architecture review stage.
7. Implementation stage.
8. Development acceptance stage.
9. Code review stage.
10. End-to-end acceptance stage.
11. Human confirmation stage.

Required views:

1. Task board view.
2. Process quality view.
3. Artifact lineage view.
4. Stage evidence view.
5. Manual approval view.
6. Long-running recovery view.

Required runtime behavior:

1. Workflow can stay running across page refresh.
2. Completed stage outputs remain visible.
3. Failed stage can be rerun with a new attempt.
4. Old attempts remain visible.
5. Manual confirmation gates block downstream mutation.
6. Quality review can block publish or next-stage progression.

Acceptance focus:

1. User can start a large coding workflow.
2. Board shows all stages and current status.
3. Each stage produces a visible artifact.
4. Manual approval is required before implementation and final confirmation.
5. Rerun preserves history.
6. Page refresh restores the workflow instance.

Allowed completion claim:

```text
V4.5 complete: long-running engineering workflow MVP ready for dev/local validation.
```

### V4.6 Agent Workflow Builder UX / Agent 工作流搭建体验

Goal:

Upgrade Agent assistant from deterministic proposal helper to a usable workflow builder UX while preserving user-confirmed governance.

Required behavior:

1. Agent can ask follow-up questions before generating workflow.
2. Agent can generate a complete workflow draft with nodes, edges, station descriptors, artifact contracts, quality rules, and approval points.
3. Agent can explain what will happen before applying.
4. Agent can create a patch proposal but cannot apply automatically.
5. Agent can debug failed workflows with read-only explanations.
6. Agent can propose repairs as patch proposals.

Acceptance focus:

1. User can create V4.1, V4.3, V4.4, and V4.5 workflow drafts through chat.
2. Agent-generated drafts are reviewable in Canvas and Patch Diff.
3. All durable changes require user confirmation.

Allowed completion claim:

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

## 3. Experience-by-Experience Gap Matrix

| Target experience | Current support | Missing capabilities | First stage that should satisfy it |
| --- | --- | --- | --- |
| Serial video pipeline | Canvas shell, station board, artifacts panel, Agent patch proposal, user-confirmed editing | Real serial multi-Agent runtime, per-station Agent descriptors, model/tool/skill binding UI, station rerun, downstream stale propagation, visible per-station outputs | V4.3, backed by V4.2 |
| Parallel Roman forum | Current WorkflowTemplate can represent edges, but UI/runtime does not provide real parallel Agent deliberation | Parallel scheduler, persona descriptors, cross-Agent inspiration edges, synthesis node, attributed output artifacts | V4.4, backed by V4.2 |
| Long coding workflow | Board/evidence/approval panels exist as shell primitives | Durable long-running board, stage lifecycle, stage-specific artifacts, quality gates, rerun history, recovery, manual checkpoints | V4.5, backed by V4.2 |
| Natural-language workflow creation | Agent assistant can create limited deterministic proposals | Complete workflow generator, follow-up clarification, descriptor validation, multi-node patch proposal, repair proposal flow | V4.6 |
| Local folder recursive summary | V4.1 completed for dev/local validation with browser evidence | PRD-level product polish remains, including richer result packaging and visual refinement | V4.1 completed; polish can continue without changing runtime boundary |

## 4. Revised Priority

The old V4.0-Z line should stop expanding. V4.x should proceed in this order:

1. V4.1 Local Knowledge Workflow MVP.
2. V4.2-A Headless Interaction Pivot for WorkflowSpec, TUI transcript, Drawio, HTML reports, and Thin Web Console evidence.
3. V4.2-B/C Controlled Execution Runtime foundation for generic user-confirmed start/rerun.
4. V4.3 Serial Multi-Agent Video Workflow MVP.
5. V4.4 Parallel Multi-Agent Deliberation Workflow MVP.
6. V4.5 Long-Running Engineering Workflow MVP.
7. V4.6 Agent Workflow Builder UX hardening across all scenarios.

Reason:

V4.1 is the smallest real workflow with local files and artifacts. V4.2-A first makes the workflow usable as headless specs, transcripts, diagrams, reports, and reviewable evidence. V4.2-B/C then supplies the generic runtime foundation before V4.3 to V4.5 can be more than demos. V4.3 and V4.4 prove serial and parallel workflow semantics. V4.5 proves durability, quality gates, and long-running engineering process visibility. V4.6 consolidates the Agent UX after the runtime semantics are real enough to be useful.

## 5. Immediate Next Step

V4.1-A through V4.1-E are complete for dev/local validation. The next planning and audit stage is:

```text
V4.2-A Headless Interaction Pivot / Headless 交互转向
```

Pre-implementation audit scope:

1. Confirm V4.1 completion evidence remains PASS.
2. Confirm Headless-first route has replaced full Web low-code Studio as the current mainline.
3. Define WorkflowSpec, TUI transcript, Drawio, HTML report, and Thin Web Console evidence package requirements.
4. Keep apply/publish/run/rerun as deferred mutating command contracts unless backed by the existing V4.1 local workflow path.
5. Preserve the `source=agent` proposal-only boundary.
6. Define V4.2-A acceptance around generated specs, diagrams, reports, redaction, and no false-green claims.
7. Stop for user decision if V4.2-A requires generic controlled execution runtime, Agent executor, production auth, or full Web Studio.

This stage should not attempt generic controlled runtime, generic station rerun, Agent executor, autonomous workflow editing, production auth, production filesystem access, or production-ready external app support.

Allowed V4.2-A planning claim before implementation:

```text
V4.2-A plan audited: headless interaction pivot ready for implementation review.
```

Forbidden V4.2-A planning claims:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```
