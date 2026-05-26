# V4.x Prototype To Frontend Mapping

Status: auditable mapping between Stitch prototypes, PRD intent, and workflow-console implementation targets.

This document maps screens in Stitch project `10240451325799222489` to frontend rebuild work. It is not a runtime capability claim.

## 1. Design And Global Screens

| Stitch screen | Frontend purpose | Implementation target |
| --- | --- | --- |
| `00-Design-System-Overview` | Light workbench visual language, density, tokens, status colors | `styles.css`, shared CSS tokens |
| `01-Workflow-Studio-Base-Layout` | Five-zone Workflow Studio layout | `ConsoleShell.tsx`, `WorkflowHeader.tsx` |
| `02-Node-Library-And-Canvas-States` | Controlled node library and canvas status states | `ConsoleShell.tsx`, `StationBoard.tsx`, `StationCard.tsx` |
| `03-Agent-Assistant-Proposal-Only` | Agent proposal-only behavior and copy | `AgentTalkShell.tsx`, proposal cards |
| `Patch Diff 确认面板` | User-confirmed proposal review | `WorkflowEditingPanel.tsx`, right and bottom patch tabs |
| `治理审计证据链页` | Read-only evidence review | `GovernanceReviewPanel.tsx`, governance bottom tab |
| `V4.x-00-Scenario-Hub` | Cross-stage scenario entry reference | future scenario hub, not V4.1 runtime proof |

Implementation rule:

- The visible light prototype and `DESIGN.md` override stale dark project metadata.
- The first rendered product screen must be the usable workbench, not a landing page.

## 2. V4.1 Local Knowledge Workflow Screens

Use `V4.1-00` through `V4.1-17` as the canonical button-level MVP sequence.

| Stitch screen | Required frontend behavior | Current implementation target |
| --- | --- | --- |
| `V4.1-00-Workflow-Studio-Home` | Light five-zone workbench opens directly into local knowledge workflow | `ConsoleShell.tsx`, `WorkflowHeader.tsx`, `StationBoard.tsx` |
| `V4.1-01-Agent-Create-Draft` | Agent prompt entry for Desktop/技术分享 workflow | `AgentTalkShell.tsx` |
| `V4.1-02-Agent-Draft-Proposal` | Agent generates proposal only, canvas shows pending/ghost nodes | `AgentTalkShell.tsx`, `ConsoleShell.tsx`, `StationBoard.tsx` |
| `V4.1-03-Patch-Diff-Review` | User reviews patch diff before apply | `WorkflowEditingPanel.tsx`, patch bottom tab |
| `V4.1-04-Apply-Confirmation` | Apply requires explicit user confirmation | `WorkflowEditingPanel.tsx`, operation handlers |
| `V4.1-05-Draft-Applied-Canvas` | Draft truth refreshes and formal nodes appear | `useWorkflowConsoleData.ts`, `StationBoard.tsx` |
| `V4.1-06-Folder-Input-Inspector` | Folder input path configuration in Inspector | `ConsoleShell.tsx` folder summary controls |
| `V4.1-07-Folder-Authorization` | Explicit read authorization before scan | BFF folder authorization client, folder summary controls |
| `V4.1-08-Debug-Scan-Result` | Debug scan tree and counts without summary generation | Folder scan result panel |
| `V4.1-09-Publish-Version-Confirm` | Publish requires explicit confirmation | publish operation controls |
| `V4.1-10-Run-Workflow-Confirm` | Run requires explicit confirmation | run workflow controls |
| `V4.1-11-Run-Board-In-Progress` | Bottom run panel shows 9 node states | `StationBoard.tsx`, bottom run tab |
| `V4.1-12-Run-Completed-Artifacts` | Required summary artifacts are visible | artifact viewer |
| `V4.1-13-Quality-Report` | Quality report shows coverage, unsupported file, empty folder | quality panel |
| `V4.1-14-Refresh-Recovery` | Refresh restores instance, node state, artifacts, quality report | data hooks, BFF state refresh |
| `V4.1-15-Failure-And-Rerun` | Failed parse shows error, user-confirmed rerun, attempt history | failure/rerun UI, bottom run tab |
| `V4.1-16-Agent-Debug-Fix-Proposal` | Agent debug produces explanation or proposal, no auto apply | `AgentTalkShell.tsx`, proposal card |
| `V4.1-17-Governance-Evidence-ReadOnly` | Evidence chain is visible and read-only | `GovernanceReviewPanel.tsx` |

Older V4.1 summary screens remain reference material:

```text
V4.1-01-Local-Knowledge-Studio-Overview
V4.1-02-Agent-Generates-Workflow-Draft
V4.1-03-Folder-Authorization-Debug-Scan
V4.1-04-Run-Board-State-Transition
V4.1-05-Artifacts-And-Quality-Report
V4.1-06-Rerun-And-Governance-Evidence
```

They must not replace the canonical `V4.1-00` through `V4.1-17` acceptance path.

V4.1 node library categories:

- 输入节点
- 文件处理节点
- AI Agent 节点
- 工具 / 连接器节点
- 质量与治理节点
- 输出节点

V4.1 logical nodes:

- 文件夹输入
- 递归文件扫描
- Markdown 文件过滤
- Markdown 内容解析
- 子文件夹分组
- 子文件夹总结 Agent
- 总目录总结 Agent
- 质量检查 Agent
- 输出总结文件

## 3. V4.2 Controlled Execution UX Preview

| Stitch screen | Blueprint meaning | Frontend boundary |
| --- | --- | --- |
| `V4.2-01-Execution-Policy-Dashboard` | Policy and user confirmation visibility | UX preview only |
| `V4.2-02-User-Confirmed-Workflow-Start` | Start workflow requires user confirmation | no Agent executor |
| `V4.2-04-Downstream-Stale-Propagation` | Rerun makes downstream state stale | no generic executor claim |
| `V4.2-05-Kill-Switch-Timeout-Recovery` | Future timeout and kill-switch controls | design preview only |
| `V4.2-06-Executor-Evidence-Audit` | Runtime evidence review | no controlled executor ready claim |

V4.2 screens should guide shared run panel UX after V4.1, but they do not prove executor implementation.

## 4. V4.3 Serial Multi-Agent Video Workflow

Representative screens:

- `V4.3-01-Video-Workflow-Template-Overview`
- `V4.3-02-Agent-Station-Descriptor-Editor`
- `V4.3-03-Serial-Run-Board`
- `V4.3-04-Station-Output-Artifact-Review`
- `V4.3-05-Middle-Station-Rerun-And-Downstream-Stale`
- `V4.3-06-Video-Workflow-Quality-Gate`

Blueprint impact:

- Reuse the V4.1 canvas, node inspector, artifact viewer, and run board.
- Add station descriptor editing for role, goal, model, tool, and skill configuration.
- Add serial multi-Agent run board with local rerun and downstream stale state.
- Do not implement this before V4.1 UI completion and shared Agent Chat TUI stabilization.

## 5. V4.4 Parallel Multi-Agent Deliberation

Representative screens:

- `V4.4-01-Roman-Forum-Workflow-Overview`
- `V4.4-02-Persona-Agent-Configuration`
- `V4.4-03-Parallel-Execution-Board`
- `V4.4-04-Cross-Inspiration-Edges`

Blueprint impact:

- Requires parallel board view and cross-inspiration edge visualization.
- Requires persona artifact attribution and synthesis output.
- Should not be folded into V4.1 local knowledge workflow UI.

## 6. V4.5 Long-Running Engineering Workflow

Representative screens:

- `V4.5-01-Engineering-Workflow-Blueprint`
- `V4.5-02-Durable-Task-Board`
- `V4.5-03-Stage-Agent-Descriptor`
- `V4.5-05-Substage-Implementation-Run`
- `V4.5-06-Code-Review-And-E2E-Acceptance`
- `V4.5-08-Human-Confirmation-Gate`

Blueprint impact:

- Requires durable task board, stage artifacts, quality and risk lenses, code review, E2E acceptance, and human confirmation.
- This is a later product surface after V4.2 execution UX and V4.3/V4.4 orchestration patterns.

## 7. V4.6 Agent Workflow Builder UX

Representative screens:

- `V4.6-01-Agent-Workflow-Builder-Chat-TUI`
- `V4.6-02-Agent-Clarifying-Questions`
- `V4.6-04-Agent-Debug-Loop`
- `V4.6-06-Conversation-And-Canvas-CoEditing`

Blueprint impact:

- The Chat TUI should be extracted early as the shared right-panel interaction pattern.
- The full builder remains future work.
- Agent can propose, explain, handoff, and navigate only.
- Agent cannot auto apply, publish, run, or rerun.

## 8. No False Green Checklist

The frontend must not display or imply:

- `complete Workflow Studio ready`
- `complete AgentTalkWindow ready`
- `Agent executor ready`
- `controlled executor ready`
- `production-ready external app support`
- `full multi-Agent orchestration ready`
- `自动应用`
- `自动发布`
- `Agent 已执行`
- `Agent 已发布`

Every prototype-driven frontend milestone must include a spec drift and false green review before advancing to the next stage.
