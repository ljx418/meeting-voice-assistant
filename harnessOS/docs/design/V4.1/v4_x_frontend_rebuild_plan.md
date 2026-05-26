# V4.x Frontend Rebuild Plan

Status: implementation guide for the Workflow Console frontend rebuild.

This document is based on the Stitch project `10240451325799222489`, the V4.1 PRD, and `DESIGN.md`. It is a frontend implementation plan only. It does not claim new runtime, executor, Agent executor, production auth, or production external app capability.

Allowed near-term claim:

```text
V4.1 frontend rebuild ready for focused local knowledge workflow validation.
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

## 1. Prototype Baseline

The frontend rebuild uses the light Stitch screens as the source of visual and interaction direction:

- `00-Design-System-Overview`
- `01-Workflow-Studio-Base-Layout`
- `02-Node-Library-And-Canvas-States`
- `03-Agent-Assistant-Proposal-Only`
- `04-Patch-Diff-And-User-Confirmation`
- `05-Governance-Evidence-ReadOnly`
- `V4.x-00-Scenario-Hub`
- `V4.1-00-Workflow-Studio-Home`
- `V4.1-01-Agent-Create-Draft`
- `V4.1-02-Agent-Draft-Proposal`
- `V4.1-03-Patch-Diff-Review`
- `V4.1-04-Apply-Confirmation`
- `V4.1-05-Draft-Applied-Canvas`
- `V4.1-06-Folder-Input-Inspector`
- `V4.1-07-Folder-Authorization`
- `V4.1-08-Debug-Scan-Result`
- `V4.1-09-Publish-Version-Confirm`
- `V4.1-10-Run-Workflow-Confirm`
- `V4.1-11-Run-Board-In-Progress`
- `V4.1-12-Run-Completed-Artifacts`
- `V4.1-13-Quality-Report`
- `V4.1-14-Refresh-Recovery`
- `V4.1-15-Failure-And-Rerun`
- `V4.1-16-Agent-Debug-Fix-Proposal`
- `V4.1-17-Governance-Evidence-ReadOnly`

If Stitch project metadata conflicts with the visible light prototype, the visible prototype and `DESIGN.md` win.

Local screenshot evidence and the detailed interpretation are recorded in:

```text
docs/design/V4.1/stitch-screenshots-review/index.html
docs/design/V4.1/v4_1_stitch_frontend_rebuild_review.md
docs/design/V4.1/v4_1_frontend_button_inventory.md
```

## 2. Frontend Architecture Direction

The Workflow Console must present a five-zone workbench:

```text
Top Bar
Left Node Library | Central Canvas | Right Agent / Inspector Panel
Bottom Run Panel
```

Key interaction rules:

- Canvas remains the primary surface.
- Agent is a proposal, explanation, handoff, and navigation assistant.
- Durable mutation requires explicit user confirmation.
- Apply, publish, run, and rerun are user-triggered controls.
- Governance evidence is read-only.
- Browser traffic remains BFF-only.

## 3. Implementation Slices

### FE-1 Design System And Shell Rebuild

Update the workflow-console visual system to the light workbench baseline:

- Light page background and neutral panels.
- Blue primary actions and violet Agent/proposal emphasis.
- Compact workbench typography.
- Five-zone layout with stable left, right, canvas, and bottom regions.
- No marketing hero, no pure chatbot landing screen, no dark console theme.

Primary implementation area:

- `apps/workflow-console/src/styles.css`
- `apps/workflow-console/src/components/WorkflowHeader.tsx`
- `apps/workflow-console/src/components/ConsoleShell.tsx`

### FE-2 V4.1 Local Knowledge Main Flow

Make the V4.1 local Markdown folder summary flow the first-class scenario:

- Controlled node library categories for folder input, file processing, Agent summary, quality governance, and output.
- Agent prompt that generates a workflow proposal only.
- Canvas pending or ghost nodes before apply.
- Folder authorization and debug scan controls.
- User-confirmed apply, publish, run, and rerun actions.
- Artifact and quality report panels.
- Read-only governance evidence chain.
- Button-level coverage for:
  - `查看 Diff`
  - `应用到草稿`
  - `确认应用`
  - `授权读取`
  - `调试扫描`
  - `发布版本`
  - `确认发布`
  - `运行工作流`
  - `确认运行`
  - `查看产物`
  - `查看质量报告`
  - `重跑当前节点`
  - `确认重跑`
  - `Agent 解释`
  - `Agent 生成修复 Proposal`
  - `查看治理证据`

Primary implementation area:

- `apps/workflow-console/src/components/ConsoleShell.tsx`
- `apps/workflow-console/src/components/StationBoard.tsx`
- `apps/workflow-console/src/components/StationCard.tsx`
- `apps/workflow-console/src/api/canvasPatchIntents.ts`

### FE-3 Agent Chat TUI Panel

Refactor the right Agent panel toward the V4.6 Chat TUI pattern without claiming V4.6 completion:

- Conversational input is prominent.
- Agent messages explain that proposals are not execution.
- Proposal cards show risk, policy, lifecycle, and handoff targets.
- Handoff opens operation panels only.
- Agent debug produces explanation or patch proposal.

Primary implementation area:

- `apps/workflow-console/src/components/AgentTalkShell.tsx`

### FE-4 Run Panel And Evidence UX

Turn the bottom panel into a validation-grade run cockpit:

- Run board tab.
- Artifacts tab.
- Quality tab.
- Patch tab.
- Governance evidence tab.
- Attempt history and rerun controls for V4.1 local workflow.

Primary implementation area:

- `apps/workflow-console/src/components/ConsoleShell.tsx`
- `apps/workflow-console/src/components/GovernanceReviewPanel.tsx`
- `apps/workflow-console/src/components/QualityPanel.tsx`

### FE-5 Scenario Hub And Future Blueprint

The V4.x scenario hub should guide later stage work, but it should not block V4.1 validation:

- Local knowledge summary.
- Video creation pipeline.
- Roman forum deliberation.
- Long-running engineering task.
- Agent workflow builder.

V4.2-V4.6 remain stage-specific future work and must not be presented as complete runtime capability.

## 4. Acceptance Criteria

Focused frontend acceptance:

- Workflow Console renders as a light five-zone workbench.
- Node library exposes V4.1 local knowledge workflow nodes.
- Agent panel uses chat-style proposal-first copy.
- Canvas shows proposal-only and draft read model language.
- Folder summary controls are visible and user-triggered.
- Artifacts, quality report, and governance tabs remain available.
- No browser copy claims Agent execution or controlled executor readiness.
- The canonical `V4.1-00` through `V4.1-17` user path can be manually followed.
- The older V4.1 summary screens remain reference only and do not replace the 18-screen canonical path.

Regression commands:

```bash
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
```

Global assertions:

- No `/v1/rpc` browser request.
- No `/v1/events/subscribe` browser request.
- No token, secret, raw payload, raw prompt, or signed URL in DOM or network evidence.
- No misleading copy such as `自动应用`, `自动发布`, `Agent 已执行`, or `Agent 已发布`.

## 5. Blueprint Update Direction

After V4.1 frontend rebuild, the later V4.x blueprint should be revised in this order:

1. V4.1 local knowledge workflow UI completion.
2. Shared Agent Chat TUI and canvas co-editing UX foundation.
3. V4.2 user-confirmed execution UX preview.
4. V4.3 serial multi-Agent video workflow.
5. V4.4 parallel multi-Agent deliberation workflow.
6. V4.5 long-running engineering workflow.
7. V4.6 Agent workflow builder UX completion.

This order keeps the highest-impact interaction fix ahead of later orchestration expansion.
