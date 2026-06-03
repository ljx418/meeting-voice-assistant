# V4.x Auditable Development Blueprint

Status: post V4.1 completion review blueprint, updated for Headless-first V4 roadmap.

Stage-gate update:

Use `docs/design/V4.1/v4_1_stage_gate_development_plan.md` as the controlling stage outline. It adds bilingual stage names and mandatory Spec Drift Evaluation / 规格漂移评估 plus False Green Evaluation / 虚假验收评估 before every proceed decision.

This document is a consolidated V4.x development blueprint for human and ChatGPT review. It is not a completion report and does not claim that the current project already supports full multi-Agent workflow execution.

Headless-first route update:

```text
Headless Workflow Core
+ TUI / Command Palette
+ Drawio Workflow Visualization
+ HTML Runtime Reports
+ Thin Web Console
```

Full Web low-code Workflow Studio is no longer the current V4 mainline. Workflow Studio remains as Reference UI / Thin Web Console, while V4.2-A becomes the Headless Interaction Pivot before the controlled runtime stage.

Source planning documents:

```text
docs/design/V4.1/v4_x_interaction_experience_revised_plan.md
docs/design/V4.1/v4_1_desktop_folder_recursive_summary_acceptance.md
docs/design/V4.1/v4_1_stage_gate_development_plan.md
docs/design/V4.1/v4_x_frontend_rebuild_plan.md
docs/design/V4.1/v4_x_prototype_to_frontend_mapping.md
docs/design/V4.1/v4_1_stitch_frontend_rebuild_review.md
docs/design/V4.1/v4_1_frontend_button_inventory.md
docs/design/V4.x/v4_x_headless_first_roadmap.md
docs/design/V4.x/v4_x_headless_api_surface_map.md
docs/design/V4.x/v4_x_tui_drawio_html_report_plan.md
docs/design/V4.2/v4_2_headless_interaction_pivot_plan.md
```

## 1. Document Purpose

This blueprint exists to make the next V4.x development path auditable in one place.

Reviewers should check whether the revised roadmap is technically coherent, whether the stages are ordered correctly, whether the claims are safe, and whether the first implementation stage is small enough to deliver a real user-facing workflow MVP.

This document must not be read as a completion note. The current V4.1 completion note is `v4_1_e_local_knowledge_workflow_mvp_consolidation_gate_completion_note.md`. The current project status for V4.1 is:

```text
V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation.
```

## 2. Current Capability Assessment

### 2.1 Supported Today

Current V4.1 can support a governed proposal-first Workflow Console shell and one real dev/local local knowledge workflow:

1. Workflow Console renders board, station cards, events, artifacts, approvals, quality summaries, context, Patch Diff, and governance evidence from BFF DTOs.
2. Agent assistant accepts natural-language input and creates deterministic proposal / handoff objects.
3. Canvas and Inspector can create WorkflowPatch proposals.
4. Patch apply, patch reject, and publish paths require explicit user confirmation.
5. Approval, context update, business event, patch apply, patch reject, and publish actions stay inside operation panels.
6. EventBridge only triggers refresh; UI truth is reloaded from BFF.
7. Browser smoke tests enforce BFF-only browser access and no direct `/v1/rpc` or `/v1/events/subscribe`.
8. Governance evidence panels can show a user-confirmed operation chain.
9. The `Desktop/技术分享` recursive Markdown folder summary workflow can be proposed by Agent, applied, published, run, recovered after refresh, rerun after a scoped parse failure, and reviewed through generated artifacts, quality report, and governance evidence.

### 2.2 Not Supported Today

Current V4.1 does not support the requested complete interaction experience:

1. No real Agent executor.
2. No controlled executor runtime implementation.
3. No true multi-Agent serial execution with per-station Agent descriptors.
4. No true multi-Agent parallel deliberation.
5. No generic station-level rerun with downstream stale propagation in UI; V4.1 rerun is local Markdown workflow scoped.
6. No durable long-running engineering task board.
7. No production filesystem permission model.
8. No generic Agent-driven workflow build, publish, run, debug, and repair loop beyond the V4.1 local Markdown workflow slice.
9. No production auth, tenant control plane, production secret manager, or production-ready external app support.

Current completion level:

```text
V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation.
```

## 3. Revised Roadmap

### V4.1-F Frontend Rebuild Gate / 前端重构门禁

Reason for insertion:

The Stitch prototype review shows that the product experience should be rebuilt around a light five-zone Workflow Studio workbench. The existing implementation already has many V4.1 data and governance paths, but the page shell, right Agent panel, node library, run panel, and visual hierarchy need to be re-aligned before later V4.x work expands the surface area.

Goal:

Rebuild the workflow-console frontend around the Stitch light prototypes and the V4.1 PRD without adding new runtime authority.

Key deliverables:

1. Light Workflow Studio design system.
2. Five-zone layout: top bar, node library, canvas, Agent / Inspector panel, bottom run panel.
3. V4.1 local knowledge node library.
4. Agent Chat TUI panel as proposal-first shared UX.
5. User-confirmed folder proposal, apply, publish, run, and rerun controls.
6. Artifacts, quality, patch, and governance evidence tabs.
7. Prototype-to-frontend mapping documentation.
8. Button-level alignment with the canonical Stitch path `V4.1-00` through `V4.1-17`.

Canonical V4.1 frontend path:

```text
V4.1-00-Workflow-Studio-Home
V4.1-01-Agent-Create-Draft
V4.1-02-Agent-Draft-Proposal
V4.1-03-Patch-Diff-Review
V4.1-04-Apply-Confirmation
V4.1-05-Draft-Applied-Canvas
V4.1-06-Folder-Input-Inspector
V4.1-07-Folder-Authorization
V4.1-08-Debug-Scan-Result
V4.1-09-Publish-Version-Confirm
V4.1-10-Run-Workflow-Confirm
V4.1-11-Run-Board-In-Progress
V4.1-12-Run-Completed-Artifacts
V4.1-13-Quality-Report
V4.1-14-Refresh-Recovery
V4.1-15-Failure-And-Rerun
V4.1-16-Agent-Debug-Fix-Proposal
V4.1-17-Governance-Evidence-ReadOnly
```

Minimum PASS:

1. Workflow Console renders as a light low-code workbench, not a dark console or pure chatbot.
2. V4.1 local Markdown workflow is the first-class scenario.
3. Agent copy clearly says proposals are not execution.
4. No browser direct `/v1/rpc` or `/v1/events/subscribe`.
5. No false-green copy or forbidden completion claims.
6. Manual inspection can follow all 18 canonical V4.1 Stitch screens without falling into a dead button or misleading operation.

Allowed claim:

```text
V4.1-F complete: Stitch-aligned frontend rebuild ready for local knowledge workflow validation.
```

Forbidden claims:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```

Blueprint impact:

V4.1-F is now treated as Thin Web Console / Reference UI groundwork, not as a full low-code Studio mainline. V4.6 Agent Workflow Builder UX should be mined early for the shared Agent Chat TUI panel, but full V4.6 completion remains a later stage. V4.2-V4.5 should consume the headless core through TUI, Drawio, HTML reports, and Thin Web Console rather than adding stage-specific full Web Studio shells.

### V4.1 Local Knowledge Workflow MVP / 本地知识工作流 MVP

Reference scenario:

```text
Desktop/技术分享 recursive Markdown folder summary workflow.
```

Goal:

The user asks Agent to create a local folder summary workflow, confirms the generated workflow, configures a folder input, runs the workflow, and receives one Markdown summary per child folder plus a final overview summary.

Key deliverables:

1. Local folder input with explicit read authorization.
2. Recursive folder scan.
3. Markdown parse.
4. Child folder grouping.
5. Per-folder summary generation.
6. Overview summary generation.
7. Quality report generation.
8. Artifact publishing and review in Workflow Console.
9. ChromeCLI / browser automation acceptance.

Minimum PASS:

1. `Desktop/技术分享` or equivalent fixture can be scanned through BFF/runtime, not browser direct file access.
2. Markdown files are parsed.
3. Unsupported files are recorded.
4. Empty folders are recorded.
5. Required summary artifacts are visible.
6. Global redaction and no-direct-`/v1/*` assertions pass.

Allowed claim:

```text
V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation.
```

Forbidden claims:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
```

### V4.2-A Headless Interaction Pivot / Headless 交互转向

Reason for insertion:

The project should prove that the V4.1 workflow can be described, visualized, reported, and operated from a headless multi-head baseline before building more runtime power.

Goal:

Make the local Markdown workflow usable through WorkflowSpec, TUI / Command Palette, Drawio visualization, HTML runtime reports, and Thin Web Console.

Key deliverables:

1. `workflow.yaml` / `workflow.json` planning contract.
2. `workflow.schema.json` planning contract.
3. workflow-to-drawio, workflow-status-to-drawio, and artifact-lineage-to-drawio renderer plans.
4. TUI command plan for create, diff, status, artifact list, quality report, and evidence show.
5. Deferred mutating command contracts for apply, publish, run, and rerun. In V4.2-A these are transcript or handoff contracts only unless backed by the existing V4.1 local workflow path.
6. HTML report plan for workflow board, station detail, artifacts, quality, and evidence.
7. Thin Web Console repositioning as observation and limited user-confirmed operation surface.

Minimum PASS:

1. The user can create the `Desktop/技术分享` workflow through TUI in the planned acceptance path.
2. The system can output workflow spec, drawio files, HTML reports, and evidence JSON in the planned acceptance path.
3. Durable mutation still requires `user_confirmed=true`.
4. `source=agent` cannot execute mutation.
5. No direct browser `/v1/rpc` or `/v1/events/subscribe`.
6. No token / raw payload leakage.

Allowed claim:

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

### V4.2-B Controlled Runtime Design Gate / 受控运行时设计门禁

Reason for early placement:

V4.3, V4.4, and V4.5 require real user-confirmed start, station run, rerun, artifact production, attempt history, and recovery. V4.2-B prevents those needs from becoming an uncontrolled executor implementation.

Goal:

Define the controlled runtime implementation contract, real-data acceptance plan, and no-false-green audit before V4.2-C starts.

Key deliverables:

1. Machine-readable controlled runtime design gate contract.
2. Acceptance plan for generic workflow start and station rerun.
3. Real-data validation requirement using V4.1 local Markdown workflow fixtures.
4. Runtime evidence contract.
5. Route and capability guard.
6. PRD and architecture audit.

Allowed claim:

```text
V4.2-B complete: controlled runtime design gate ready for implementation review.
```

Forbidden claim:

```text
controlled executor ready
```

### V4.2-C Controlled Runtime MVP / 受控运行时 MVP

Reason for early placement:

V4.3, V4.4, and V4.5 require real user-confirmed start, station run, rerun, artifact production, attempt history, and recovery. Without V4.2, those stages would remain UI demos.

Goal:

Implement the minimum governed execution layer needed for real dev/local workflows while preserving V4.0-Q/Y governance gates.

Key deliverables:

1. User-confirmed workflow start.
2. User-confirmed station rerun.
3. Station attempt history.
4. Downstream stale propagation.
5. Artifact read/write through approved sandbox boundaries.
6. Policy-controlled model and connector invocation.
7. Runtime result evidence.
8. Timeout and kill switch baseline.

Minimum PASS:

1. `source=agent` cannot execute mutation.
2. User confirmation is required for start, rerun, publish, apply, approval, and context mutation.
3. High-risk action handling follows approval gate policy.
4. Event payload never becomes truth.
5. Executor reads only redacted or explicitly approved inputs.

Allowed claim:

```text
V4.2 complete: controlled execution runtime MVP ready for dev/local validation.
```

Forbidden claims until all V4.2 acceptance passes:

```text
controlled executor ready
Agent executor ready
autonomous workflow editing ready
production-ready external app support
```

### V4.3 Serial Multi-Agent Video Workflow MVP / 串行多 Agent 视频工作流 MVP

Reference scenario:

Video creation pipeline with writer, storyboard, copywriting, editing, quality review, and publish-prep stations.

Goal:

Support a serial multi-Agent workflow where each station has a configurable Agent descriptor and each station output is visible, rerunnable, and usable as downstream input.

Key deliverables:

1. Writer Agent station.
2. Storyboard Agent station.
3. Copywriting Agent station.
4. Editing Plan Agent station.
5. Quality Review Agent station.
6. Publish Preparation Agent station.
7. Per-station role, goal, model, tool, skill, input contract, output contract, quality rule, and approval policy.
8. Station rerun with downstream stale propagation.

Minimum PASS:

1. User can deploy and run the serial video workflow.
2. Every station output is visible.
3. User can customize at least one station's role, model, tools, skills, and prompt.
4. User can rerun one middle station.
5. Downstream stale state is visible before downstream continuation.

Allowed claim:

```text
V4.3 complete: serial multi-Agent video workflow MVP ready for dev/local validation.
```

### V4.4 Parallel Multi-Agent Deliberation Workflow MVP / 并行多 Agent 讨论工作流 MVP

Reference scenario:

Roman forum workflow with one orchestrator, multiple persona Agents, optional cross-inspiration, and a synthesis node.

Goal:

Support parallel branches, shared prompt context, optional cross-Agent inspiration inputs, and final synthesis with viewpoint attribution.

Key deliverables:

1. Orchestrator node.
2. Multiple parallel persona Agent nodes.
3. Optional cross-inspiration edges.
4. Synthesis node.
5. Quality / contradiction review node.
6. Persona configuration for name, viewpoint, reasoning style, model, tools, memory/context policy, and output artifact contract.

Minimum PASS:

1. User can create a Roman forum workflow from Agent assistant.
2. User can configure at least three persona Agents.
3. Parallel station states are visible.
4. Persona outputs are independent artifacts.
5. Synthesis output cites each persona contribution.

Allowed claim:

```text
V4.4 complete: parallel multi-Agent deliberation workflow MVP ready for dev/local validation.
```

### V4.5 Long-Running Engineering Workflow MVP / 长时工程工作流 MVP

Reference scenario:

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

Key deliverables:

1. Task board view.
2. Process quality view.
3. Artifact lineage view.
4. Stage evidence view.
5. Manual approval view.
6. Long-running recovery view.
7. Stage-specific artifacts for planning, spec, blueprint, architecture review, implementation, acceptance, code review, E2E, and final confirmation.

Minimum PASS:

1. User can start a large coding workflow.
2. Board shows all stages and current status.
3. Each stage produces a visible artifact.
4. Manual approval is required before implementation and final confirmation.
5. Rerun preserves history.
6. Page refresh restores the workflow instance.

Allowed claim:

```text
V4.5 complete: long-running engineering workflow MVP ready for dev/local validation.
```

### V4.6 Agent Workflow Builder UX / Agent 工作流搭建体验

Goal:

Upgrade Agent assistant from deterministic proposal helper to a usable workflow builder UX while preserving user-confirmed governance.

Key deliverables:

1. Agent can ask follow-up questions before generating workflow.
2. Agent can generate complete workflow drafts with nodes, edges, station descriptors, artifact contracts, quality rules, and approval points.
3. Agent can explain the draft before apply.
4. Agent can create patch proposals but cannot apply automatically.
5. Agent can debug failed workflows with read-only explanations.
6. Agent can propose repairs as patch proposals.

Minimum PASS:

1. User can create V4.1, V4.3, V4.4, and V4.5 workflow drafts through chat.
2. Drafts are reviewable in Canvas and Patch Diff.
3. All durable changes require user confirmation.
4. Agent repair proposals never auto-apply.

Allowed claim:

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

## 4. Recommended Implementation Order

The recommended order is:

```text
V4.1 -> V4.2 -> V4.3 -> V4.4 -> V4.5 -> V4.6
```

Rationale:

1. V4.1 is the smallest real workflow with local files, deterministic parsing, artifacts, and quality report.
2. V4.2 is required before serial, parallel, and long-running workflows can become real execution experiences.
3. V4.3 proves serial multi-Agent semantics.
4. V4.4 proves parallel multi-Agent semantics.
5. V4.5 proves durability, long-running process visibility, rerun, quality gates, and human checkpoints.
6. V4.6 consolidates the Agent builder UX after runtime semantics are real enough.

## 5. Stage Acceptance Gates

| Stage | PASS gate | Required evidence |
| --- | --- | --- |
| V4.1 | Local Markdown folder summary workflow runs and produces required artifacts. | Screenshots, network log, console errors, artifact list, quality report. |
| V4.2 | User-confirmed start/rerun works with attempt history, stale propagation, evidence, and policy boundary. | Runtime tests, browser tests, governance evidence, redaction scan. |
| V4.3 | Serial video pipeline runs, station outputs are visible, middle station rerun works. | Browser E2E, station output artifacts, rerun attempt history. |
| V4.4 | Parallel persona workflow runs, independent outputs converge into attributed synthesis. | Parallel board evidence, persona artifacts, synthesis artifact. |
| V4.5 | Long engineering workflow restores after refresh and preserves stage artifacts and approvals. | Long-running smoke, recovery screenshots, approval evidence. |
| V4.6 | Agent builds and repairs workflow drafts across V4.1 and V4.3-V4.5 without auto mutation. | Chat transcripts, patch diffs, no-auto-apply network assertions. |

Every stage must enforce:

1. Browser does not call `/v1/rpc`.
2. Browser does not call `/v1/events/subscribe`.
3. DOM and network logs do not expose secrets or raw payloads.
4. Event payload does not become truth.
5. Agent cannot execute mutation as `source=agent`.
6. Durable mutation requires explicit user confirmation.

## 6. Audit Checklist

Use this checklist for ChatGPT or human review. Record each item as:

```text
PASS | PARTIAL | FAIL | QUESTION
```

### Roadmap Coherence

1. Is V4.1 small enough to be the first real MVP?
2. Is the new V4.2 controlled execution runtime correctly placed before V4.3 / V4.4 / V4.5?
3. Does the roadmap avoid claiming complete Workflow Studio too early?
4. Does V4.6 correctly come after runtime semantics are proven?
5. Are the three target experiences represented clearly?

### Runtime and Governance

1. Are workflow start and station rerun explicitly user-confirmed?
2. Is `source=agent` still blocked from mutation?
3. Are high-risk actions gated?
4. Is EventBridge still refresh-only?
5. Is executor sandbox input restricted to redacted or approved data?

### Serial Multi-Agent Workflow

1. Are per-station role, model, tools, skills, capabilities, input contracts, and output contracts covered?
2. Is station output visible?
3. Is local rerun covered?
4. Is downstream stale propagation covered?
5. Are old attempts preserved?

### Parallel Multi-Agent Workflow

1. Are persona descriptors covered?
2. Are parallel branch states visible?
3. Are independent persona artifacts preserved?
4. Is cross-Agent inspiration optional and explicit?
5. Does synthesis preserve attribution?

### Long-Running Engineering Workflow

1. Are all required stages represented?
2. Is the task board durable across refresh?
3. Are stage artifacts visible?
4. Are quality gates and manual approvals represented?
5. Is failed-stage rerun with history represented?

### Local Folder Summary Workflow

1. Is local folder read authorization explicit?
2. Is browser direct file access avoided?
3. Are unsupported files recorded?
4. Are empty folders recorded?
5. Are per-folder summaries and overview summary required?

### No False Green

1. Are forbidden claims present and enforced?
2. Is current status correctly marked as `V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation`?
3. Does any stage imply production-ready support before production blockers close?
4. Does any stage imply Agent executor readiness before V4.2 passes?
5. Does the blueprint distinguish proposal generation from execution?

## 7. Immediate Implementation Recommendation

The next planning and audit stage should be:

```text
V4.2-A Headless Interaction Pivot / Headless 交互转向
```

Pre-implementation audit scope:

1. Confirm V4.1 completion evidence remains PASS.
2. Confirm the project no longer treats full Web low-code Studio as the current V4.x mainline.
3. Define WorkflowSpec, TUI transcript, Drawio, HTML report, and Thin Web Console evidence outputs.
4. Mark apply/publish/run/rerun as deferred mutating command contracts unless backed by the existing V4.1 local workflow path.
5. Preserve `source=agent` proposal-only boundary.
6. Stop for user decision if V4.2-A requires generic controlled execution runtime, Agent executor, production auth, or full Web Studio as a prerequisite.
7. Prepare a separate V4.2-B audit before adding generic user-confirmed start/rerun behavior.

Deliberately out of scope for V4.2-A pre-implementation planning:

1. PPTX parsing.
2. DOCX parsing.
3. PDF parsing.
4. Production filesystem permission model.
5. Production auth or tenant control plane.
6. Agent executor.
7. Autonomous workflow editing.
8. Production-ready external app support.
9. Generic controlled execution runtime.
10. Generic station rerun.

Allowed V4.2-A planning claim:

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

## 8. Review Output Template

ChatGPT or human reviewers should respond with:

```text
Overall verdict:
Recommended changes:
Blocking concerns:
Roadmap order review:
V4.2 scope review:
Runtime governance review:
No False Green review:
Missing acceptance criteria:
```
