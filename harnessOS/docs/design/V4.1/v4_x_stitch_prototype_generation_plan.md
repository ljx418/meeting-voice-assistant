# V4.x Stitch Prototype Generation Plan

Status: prototype planning document, updated for Headless-first V4 roadmap.

Purpose: define the Stitch prototype screens required to guide V4.x frontend development while keeping visual style consistent with `docs/design/V4.1/DESIGN.md`.

This document is for prototype generation and design review. It is not a runtime implementation contract and does not claim completion of Workflow Studio, Agent executor, controlled executor, production readiness, or full multi-Agent orchestration.

Headless-first update:

V4.x no longer uses full Web low-code Workflow Studio as the current mainline. Stitch prototypes should support Thin Web Console and report-viewer design, while TUI, Drawio, and HTML reports become primary V4.2-A outputs.

## 1. Source Documents

- `docs/design/V4.1/DESIGN.md`
- `docs/design/V4.1/harnessos_v4_1_workflow_studio_prd.md`
- `docs/design/V4.1/v4_x_interaction_experience_revised_plan.md`
- `docs/design/V4.1/v4_x_auditable_development_blueprint.md`
- `docs/design/V4.1/v4_1_stage_gate_development_plan.md`

## 2. Prototype Boundary

Use `docs/design/V4.1/DESIGN.md` as the visual style source of truth for every V4.x prototype.

The current prototype set has these boundaries:

1. V4.1 screens fully support the Local Knowledge Workflow MVP frontend design.
2. V4.2-A screens should focus on Thin Web Console views for generated WorkflowSpec, Drawio previews, HTML report links, TUI transcript review, and evidence package navigation.
3. V4.2-B screens are controlled execution runtime design previews only; they do not mean controlled executor ready.
4. V4.3, V4.4, V4.5, and V4.6 require stage-specific prototypes; V4.1 screens cannot replace those stage-specific designs.
5. Every prototype group must include this boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

## 3. Global Prototype Screens

These screens define the shared Thin Web Console / Reference UI visual and interaction system used by all V4.x stages.

1. `V4.x-00-Scenario-Hub`
   - Show cross-stage entries for 本地知识总结, 视频创作流水线, 罗马广场讨论, 长时工程任务, and Agent 工作流构建器.

2. `00-Design-System-Overview`
   - Show color, typography, buttons, inputs, status badges, node cards, evidence cards, artifact cards.

3. `01-Workflow-Studio-Base-Layout`
   - Show top bar, left node library, central canvas, right Agent/Inspector panel, bottom run panel.

4. `02-Node-Library-And-Canvas-States`
   - Show node categories, drag interaction, ghost nodes, pending nodes, running/completed/failed/waiting states.

5. `03-Agent-Assistant-Proposal-Only`
   - Show Agent suggestions, explanations, Patch Proposal, Handoff, and clear no-auto-execute copy.

6. `04-Patch-Diff-And-User-Confirmation`
   - Show Diff, Apply to Draft, Publish Version, Run Workflow, and user confirmation state.

7. `05-Governance-Evidence-ReadOnly`
   - Show read-only evidence chain without Apply, Publish, Approve, Reject, Execute, or Run controls.

8. `06-Headless-Outputs-Hub`
   - Show links or cards for workflow.yaml, workflow.drawio, workflow_status.drawio, artifact_lineage.drawio, workflow_board.html, artifacts.html, quality.html, and evidence.html.

9. `07-TUI-Transcript-Review`
   - Show a read-only transcript of the TUI workflow creation and user-confirmed operation path.

## 4. V4.1 Local Knowledge Workflow MVP Screens

Reference scenario: `Desktop/技术分享` recursive Markdown folder summary workflow.

Boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

V4.1 screens fully support the Local Knowledge Workflow MVP frontend design.

1. `V4.1-01-Local-Knowledge-Studio-Overview`
   - Show the full workflow studio with the 9-node local folder summary workflow.

2. `V4.1-02-Agent-Generates-Workflow-Draft`
   - Show user prompt, Agent draft plan, and ghost/pending nodes on canvas.

3. `V4.1-03-Folder-Authorization-Debug-Scan`
   - Show folder input inspector, authorization, debug scan, folder tree, and file statistics.

4. `V4.1-04-Run-Board-State-Transition`
   - Show pending, running, completed, failed, and waiting_approval states across the 9-node board.

5. `V4.1-05-Artifacts-And-Quality-Report`
   - Show artifact package structure, Markdown previews, and quality report.

6. `V4.1-06-Rerun-And-Governance-Evidence`
   - Show failed node, rerun attempt history, old error retention, and governance evidence chain.

## 5. V4.2-A Headless Interaction Pivot Screens

Goal: define the Thin Web Console reference views for Headless-first outputs before implementation.

Boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

V4.2-A screens are Headless interaction previews only. They do not mean controlled executor ready.

1. `V4.2-A-01-Headless-Workflow-Spec-Review`
   - Show workflow.yaml / workflow.json summary and validation state.

2. `V4.2-A-02-TUI-Command-Palette-Transcript`
   - Show TUI creation, diff, user confirmation, publish, run, and status transcript.

3. `V4.2-A-03-Drawio-Visualization-Hub`
   - Show workflow.drawio, workflow_status.drawio, and artifact_lineage.drawio preview cards.

4. `V4.2-A-04-HTML-Report-Hub`
   - Show workflow_board.html, artifacts.html, quality.html, and evidence.html report links.

5. `V4.2-A-05-Headless-Evidence-Package`
   - Show generated evidence files and No False Green status.

## 6. V4.2-B Controlled Execution Runtime MVP Screens

Goal: define the frontend interaction model for governed execution runtime before implementation.

Boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

V4.2-B screens are only a design preview for controlled execution runtime interactions. They do not mean controlled executor ready.

1. `V4.2-01-Execution-Policy-Dashboard`
   - Show action policy categories, user_confirmed_only, approval_gated, forbidden, never_executor.

2. `V4.2-02-User-Confirmed-Workflow-Start`
   - Show explicit workflow start confirmation and blocked `source=agent` execution.

3. `V4.2-03-Station-Rerun-Attempt-History`
   - Show station rerun confirmation, new attempt creation, and old attempt/output retention.

4. `V4.2-04-Downstream-Stale-Propagation`
   - Show downstream stale state after middle-station rerun and user-confirmed continuation.

5. `V4.2-05-Kill-Switch-Timeout-Recovery`
   - Show timeout, cancel, kill switch, recovery, and manual recovery path.

6. `V4.2-06-Executor-Evidence-Audit`
   - Show runtime result, policy decision, capability decision, idempotency key, and correlation id.

V4.2 screens must show:

1. User-confirmed workflow start.
2. User-confirmed station rerun.
3. Attempt history.
4. Downstream stale state.
5. Timeout / kill switch.
6. Runtime evidence.
7. Agent cannot auto-execute.
8. All execution still requires user confirmation.

## 6. V4.3 Serial Multi-Agent Video Workflow MVP Screens

Reference scenario: serial video creation workflow.

Boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

V4.3 requires stage-specific prototypes. V4.1 screens cannot replace the video workflow designs.

1. `V4.3-01-Video-Workflow-Template-Overview`
   - Show Writer, Storyboard, Copywriting, Editing Plan, Quality Review, and Publish Preparation stations.

2. `V4.3-02-Agent-Station-Descriptor-Editor`
   - Show role, goal, model, tool refs, skill refs, input/output contract, quality rules, approval policy.

3. `V4.3-03-Serial-Run-Board`
   - Show station-by-station serial execution state.

4. `V4.3-04-Station-Output-Artifact-Review`
   - Show script, storyboard, copywriting, editing plan, review, and publish-prep artifacts.

5. `V4.3-05-Middle-Station-Rerun-And-Downstream-Stale`
   - Show rerun of a middle station and stale downstream stations.

6. `V4.3-06-Video-Workflow-Quality-Gate`
   - Show quality review, manual confirmation, and publish preparation.

V4.3 screens must show:

1. Writer / Storyboard / Copywriting / Editing Plan / Quality Review / Publish Preparation stations.
2. Per-station role / goal / model / tool / skill configuration.
3. Per-station output artifact review.
4. Middle-station rerun.
5. Downstream stale state.

## 7. V4.4 Parallel Multi-Agent Deliberation Workflow MVP Screens

Reference scenario: Roman forum workflow.

Boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

V4.4 requires stage-specific prototypes. V4.1 screens cannot replace the Roman forum parallel deliberation designs.

1. `V4.4-01-Roman-Forum-Workflow-Overview`
   - Show orchestrator, multiple persona Agents, optional cross-inspiration edges, synthesis node, review node.

2. `V4.4-02-Persona-Agent-Configuration`
   - Show persona name, viewpoint, reasoning style, model, tools, memory/context policy.

3. `V4.4-03-Parallel-Execution-Board`
   - Show multiple persona Agents running in parallel.

4. `V4.4-04-Cross-Inspiration-Edges`
   - Show one persona output used as another persona input.

5. `V4.4-05-Persona-Artifacts-And-Attribution`
   - Show independent persona artifacts and attribution.

6. `V4.4-06-Synthesis-And-Contradiction-Review`
   - Show final synthesis, contradiction review, and viewpoint attribution.

V4.4 screens must show:

1. Orchestrator.
2. Multiple persona Agents.
3. Parallel execution board.
4. Cross-inspiration edges.
5. Persona artifacts.
6. Synthesis output with attribution.

## 8. V4.5 Long-Running Engineering Workflow MVP Screens

Reference scenario: long-running engineering workflow.

Boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

V4.5 requires stage-specific prototypes. V4.1 screens cannot replace the long-running engineering workflow designs.

1. `V4.5-01-Engineering-Workflow-Blueprint`
   - Show the full engineering lifecycle from planning to human confirmation.

2. `V4.5-02-Durable-Task-Board`
   - Show stage state, Agent owner, blockers, artifacts, and next action.

3. `V4.5-03-Stage-Agent-Descriptor`
   - Show stage-specific role, input, output, quality rules, and approval policy.

4. `V4.5-04-Planning-Spec-Architecture-Artifacts`
   - Show PRD, spec, blueprint, and architecture review artifacts.

5. `V4.5-05-Substage-Implementation-Run`
   - Show substage implementation logs, code artifacts, failed step, retry, and recovery.

6. `V4.5-06-Code-Review-And-E2E-Acceptance`
   - Show code review findings, E2E acceptance, screenshots, and evidence.

7. `V4.5-07-Quality-And-Risk-Lens`
   - Show process quality, spec drift risk, false-green risk, test coverage, and blockers.

8. `V4.5-08-Human-Confirmation-Gate`
   - Show manual confirmation, continue, rollback, stop, and audit decision.

V4.5 screens must show:

1. Durable task board.
2. Planning / spec / blueprint / architecture artifacts.
3. Substage implementation run.
4. Code review / E2E acceptance.
5. Quality and risk lens.
6. Human confirmation gate.

## 9. V4.6 Agent Workflow Builder UX Screens

Goal: define a more usable Agent workflow builder experience.

Boundary copy:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

V4.6 requires stage-specific prototypes. V4.1 screens cannot replace the Agent workflow builder designs.

1. `V4.6-01-Agent-Workflow-Builder-Chat-TUI`
   - Show a compact chatbot/TUI-like workbench input for workflow building.

2. `V4.6-02-Agent-Clarifying-Questions`
   - Show Agent asking clarifying follow-up questions before generating a workflow draft.

3. `V4.6-03-Agent-Plan-To-Canvas`
   - Show Agent converting natural-language plan into canvas proposal.

4. `V4.6-04-Agent-Debug-Loop`
   - Show read-only explanation and proposal-only repair loop.

5. `V4.6-05-Handoff-To-Operation-Panels`
   - Show Agent handoff to Editing, Run, Approval, and Evidence panels without executing.

6. `V4.6-06-Conversation-And-Canvas-CoEditing`
   - Show side-by-side conversation and canvas proposal editing.

V4.6 screens must show:

1. Agent clarifying questions.
2. Agent plan to canvas.
3. Agent debug loop.
4. Handoff to operation panels.
5. Conversation and canvas co-editing.
6. Agent cannot auto apply / publish / run / rerun.

## 10. Recommended Generation Order

Minimum frontend planning batch:

```text
V4.x-00-Scenario-Hub
00-Design-System-Overview
01-Workflow-Studio-Base-Layout
02-Node-Library-And-Canvas-States
03-Agent-Assistant-Proposal-Only
04-Patch-Diff-And-User-Confirmation
05-Governance-Evidence-ReadOnly
V4.1-01-Local-Knowledge-Studio-Overview
V4.1-02-Agent-Generates-Workflow-Draft
V4.1-03-Folder-Authorization-Debug-Scan
V4.1-04-Run-Board-State-Transition
V4.1-05-Artifacts-And-Quality-Report
V4.1-06-Rerun-And-Governance-Evidence
V4.2-01-Execution-Policy-Dashboard
V4.2-02-User-Confirmed-Workflow-Start
V4.2-03-Station-Rerun-Attempt-History
V4.2-04-Downstream-Stale-Propagation
V4.2-05-Kill-Switch-Timeout-Recovery
V4.2-06-Executor-Evidence-Audit
```

Recommended full frontend planning batch:

```text
Global screens: 7
V4.1 screens: 6
V4.2 screens: 6
V4.3 screens: 6
V4.4 screens: 6
V4.5 screens: 8
V4.6 screens: 6
Total: 45 screens
```

## 11. Stitch Prompts

### Global Stitch Prompt

Use this prefix for every Stitch generation task:

```text
Use docs/design/V4.1/DESIGN.md as the visual design source of truth. Generate a light-theme Chinese low-code AI workflow workbench for HarnessOS Workflow Studio. The product is not a pure chatbot, not a traditional dashboard, and not a dark control console. Use the five-zone layout: Top Bar, Left Node Library, Central Canvas, Right Agent / Inspector Panel, Bottom Run Panel. Keep Canvas first and Proposal first. Apply, Publish, Run, and Rerun must be shown as user-triggered actions. Governance Evidence must be read-only. Agent can only propose, explain, handoff, and navigate; it cannot auto execute. 本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

### V4.1 Prompt

```text
Generate the V4.1 Local Knowledge Workflow MVP prototype screens for HarnessOS Workflow Studio. Scenario: user asks Agent to create a workflow that reads Desktop/技术分享, recursively parses Markdown files, generates one summary per child folder, and generates an overview summary. Show the 9-node workflow: 文件夹输入, 递归文件扫描, Markdown 文件过滤, Markdown 内容解析, 子文件夹分组, 子文件夹总结 Agent, 总目录总结 Agent, 质量检查 Agent, 输出总结文件. Include Agent draft proposal, ghost/pending nodes, folder authorization, debug scan, run board, artifacts, quality report, rerun attempt history, and read-only governance evidence. 本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

### V4.2 Prompt

```text
Generate V4.2 Controlled Execution Runtime MVP design-preview prototype screens. Show user_confirmed workflow start, user-confirmed station rerun, attempt history, downstream stale propagation, timeout, kill switch, recovery path, and runtime evidence. Clearly state that Agent cannot auto execute, controlled executor is not ready, and all execution still requires user confirmation. Keep governance boundaries visible and use the V4.x five-zone Workflow Studio layout. 本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

### V4.3 Prompt

```text
Generate V4.3 Serial Multi-Agent Video Workflow MVP prototype screens. Show a serial video creation pipeline with Writer, Storyboard, Copywriting, Editing Plan, Quality Review, and Publish Preparation stations. Each station must show configurable role, goal, model, tool, and skill settings. Show station output artifacts, middle-station rerun, preserved attempts, and downstream stale state. Agent may propose workflow changes but cannot auto execute. 本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

### V4.4 Prompt

```text
Generate V4.4 Parallel Multi-Agent Deliberation Workflow MVP prototype screens. Show a Roman forum workflow with an Orchestrator, multiple persona Agents, a parallel execution board, optional cross-inspiration edges, persona artifacts, and synthesis output with attribution. Show independent persona outputs and a contradiction review. Agent cannot auto execute; all durable actions require user confirmation. 本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

### V4.5 Prompt

```text
Generate V4.5 Long-Running Engineering Workflow MVP prototype screens. Show a durable engineering task board covering planning, specification, blueprint, architecture review, substage implementation, development acceptance, code review, E2E acceptance, and human confirmation. Include planning/spec/blueprint/architecture artifacts, substage implementation run, code review and E2E evidence, quality and risk lens, rerun history, and human confirmation gate. 本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

### V4.6 Prompt

```text
Generate V4.6 Agent Workflow Builder UX prototype screens. Show a compact Agent workflow builder chat/TUI, Agent clarifying questions, Agent plan-to-canvas conversion, Agent debug loop, Handoff to operation panels, and conversation plus canvas co-editing. Agent can propose, explain, handoff, and navigate, but cannot auto apply, publish, run, or rerun. All durable workflow changes must require user confirmation. 本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```

## 12. No False Green Checklist

Do not include these claims in any generated screen:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
autonomous workflow editing ready
production-ready external app support
full multi-Agent orchestration ready
自动应用
自动发布
Agent 已执行
Agent 已发布
```

Every prototype group must include:

```text
本原型用于指导前端交互，不代表该阶段运行时能力已经完成。
```
