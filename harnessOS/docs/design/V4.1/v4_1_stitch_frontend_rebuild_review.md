# V4.1 Stitch Frontend Rebuild Review

Status: auditable review of Stitch `4.1-xx` and `0.x` prototype screens for the next workflow-console frontend rebuild.

Source project:

```text
https://stitch.withgoogle.com/projects/10240451325799222489
```

Local screenshot evidence:

```text
docs/design/V4.1/stitch-screenshots-review/index.html
docs/design/V4.1/stitch-screenshots-review/
```

This document is a frontend planning and audit artifact. It does not claim complete Workflow Studio, complete AgentTalkWindow, Agent executor, controlled executor, production-ready external app support, or full multi-Agent orchestration readiness.

## 1. Prototype Understanding

The Stitch prototype is a light, professional low-code AI workflow workbench. The UI direction is not a dark control console, not a pure chatbot, and not a generic metrics dashboard.

The stable product frame is:

```text
Top Bar
Left Node Library | Central Canvas | Right Agent / Inspector Panel
Bottom Run Panel
```

The interaction model is:

1. Canvas first.
2. Agent proposes and explains.
3. User confirms durable operations.
4. Runtime state is visible in the bottom run panel.
5. Artifacts, quality report, failure state, rerun history, and governance evidence are inspection surfaces.
6. Governance evidence is read-only.

## 2. Screens Seen In Stitch

### 2.1 Global Screens

| Screen | Interpretation |
| --- | --- |
| `00-Design-System-Overview` | Source for light visual language, spacing, status colors, and component density. |
| `01-Workflow-Studio-Base-Layout` | Source for the five-zone workbench layout. |
| `02-Node-Library-And-Canvas-States` | Source for controlled node library and pending/running/completed/failed canvas states. |
| `03-Agent-Assistant-Proposal-Only` | Source for Agent proposal-only boundaries. |
| `04-Patch-Diff-And-User-Confirmation` | Source for user-confirmed patch review. |
| `05-Governance-Evidence-ReadOnly` | Source for read-only governance evidence. |
| `V4.x-00-Scenario-Hub` | Cross-stage entry concept for V4.1 through V4.6 scenarios. |

### 2.2 Canonical V4.1 Screens

| Screen | Required UX meaning |
| --- | --- |
| `V4.1-00-Workflow-Studio-Home` | First usable workbench screen for local knowledge workflow. |
| `V4.1-01-Agent-Create-Draft` | User enters the Desktop/技术分享 natural-language request. |
| `V4.1-02-Agent-Draft-Proposal` | Agent generates a proposal only; ghost/pending nodes appear. |
| `V4.1-03-Patch-Diff-Review` | User reviews generated workflow diff. |
| `V4.1-04-Apply-Confirmation` | User explicitly confirms apply to draft. |
| `V4.1-05-Draft-Applied-Canvas` | Draft truth refreshes and formal nodes appear. |
| `V4.1-06-Folder-Input-Inspector` | User configures folder input in Inspector. |
| `V4.1-07-Folder-Authorization` | User explicitly authorizes folder read. |
| `V4.1-08-Debug-Scan-Result` | Debug scan displays file tree and counts without generating summaries. |
| `V4.1-09-Publish-Version-Confirm` | User confirms publish version. |
| `V4.1-10-Run-Workflow-Confirm` | User confirms workflow run. |
| `V4.1-11-Run-Board-In-Progress` | Bottom board shows 9 nodes progressing. |
| `V4.1-12-Run-Completed-Artifacts` | Artifact viewer shows required Markdown summaries and quality report. |
| `V4.1-13-Quality-Report` | Quality panel shows unsupported files, empty folders, and coverage. |
| `V4.1-14-Refresh-Recovery` | Refresh restores workflow instance state and artifacts. |
| `V4.1-15-Failure-And-Rerun` | Failed node exposes user-confirmed rerun and attempt history. |
| `V4.1-16-Agent-Debug-Fix-Proposal` | Agent debug creates read-only explanation or patch proposal only. |
| `V4.1-17-Governance-Evidence-ReadOnly` | Evidence chain is visible and non-operational. |

### 2.3 Duplicate Or Reference Screens

The Stitch project also contains earlier V4.1 reference screens such as:

```text
V4.1-01-Local-Knowledge-Studio-Overview
V4.1-02-Agent-Generates-Workflow-Draft
V4.1-03-Folder-Authorization-Debug-Scan
V4.1-04-Run-Board-State-Transition
V4.1-05-Artifacts-And-Quality-Report
V4.1-06-Rerun-And-Governance-Evidence
```

These remain useful for cross-checking, but the `V4.1-00` through `V4.1-17` sequence should be treated as the canonical button-level MVP path.

## 3. Interaction Logic

The expected user path is:

1. Open Workflow Studio and see a light five-zone workbench.
2. In the right Agent assistant, ask for the Desktop/技术分享 recursive Markdown summary workflow.
3. Agent returns a workflow draft proposal only.
4. Canvas shows pending or ghost nodes, but no file scan and no runtime mutation has happened.
5. User opens Patch Diff.
6. User confirms apply to draft.
7. Draft truth refreshes; the 9 official nodes appear on canvas.
8. User selects folder input node.
9. Inspector asks for folder path and explicit read authorization.
10. User authorizes folder read.
11. User clicks debug scan.
12. Debug scan displays file tree and counts; it does not generate summaries.
13. User confirms publish.
14. User confirms run.
15. Bottom run panel shows 9 node states.
16. User opens Artifacts and reviews per-folder summaries, overview summary, and quality report.
17. User opens Quality panel and checks unsupported file and empty folder records.
18. User refreshes and confirms state recovery.
19. User reviews a failed parse case and triggers user-confirmed rerun.
20. User asks Agent why a folder has no summary; Agent explains or proposes a fix, but does not apply it.
21. User opens Governance Evidence and sees proposal -> handoff -> user_confirmed -> runtime result chain.

## 4. Manual Acceptance UX Path

Use this as the manual inspection script after the frontend rebuild:

1. Start Workflow Console in dev/local mode.
2. Confirm first screen is not a landing page or pure chatbot.
3. Confirm left node library has V4.1 local knowledge categories and the 9 required nodes.
4. Confirm central canvas is the primary visual focus.
5. Confirm right panel can switch between Agent assistant and Inspector behavior.
6. Ask Agent:

```text
帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。
```

7. Confirm proposal appears and no scan/run happens.
8. Open Diff and confirm apply is user-triggered.
9. Configure folder input and authorize read.
10. Run debug scan and confirm only tree/counts are shown.
11. Publish and run with explicit confirmation.
12. Watch bottom run panel states.
13. Review artifacts and quality report.
14. Refresh page and confirm state recovery.
15. Trigger or inspect failure/rerun path.
16. Ask Agent debug question and confirm it does not auto apply.
17. Open governance evidence and confirm it is read-only.
18. Confirm browser requests stay under `/bff/*` and static assets.
19. Confirm DOM and network evidence do not expose token, secret, raw payload, raw prompt, or signed URL text.

## 5. Frontend Rebuild Plan

### FE-1 Prototype Evidence Update

Deliverables:

1. Maintain all 18 canonical V4.1 screenshots in `stitch-screenshots-review/`.
2. Keep `index.html` as local human-preview evidence.
3. Mark duplicate V4.1 screens as reference, not canonical flow blockers.

### FE-2 Button Inventory And UI Contract

Create a button-level implementation inventory before coding the next UI pass.

Required controls:

```text
查看 Diff
应用到草稿
确认应用
授权读取
调试扫描
发布版本
确认发布
运行工作流
确认运行
查看产物
查看质量报告
刷新恢复
重跑当前节点
确认重跑
Agent 解释
Agent 生成修复 Proposal
查看治理证据
```

Rules:

1. Controls that mutate draft, version, runtime, or rerun state require user confirmation.
2. Agent controls can propose, explain, handoff, or navigate only.
3. Browser never directly calls `/v1/rpc` or `/v1/events/subscribe`.

### FE-3 Page And Component Mapping

Map canonical screens to current frontend modules:

| Screen range | Primary components |
| --- | --- |
| `V4.1-00` to `V4.1-05` | `WorkflowHeader`, `ConsoleShell`, `StationBoard`, `WorkflowEditingPanel`, `AgentTalkShell` |
| `V4.1-06` to `V4.1-08` | `ConsoleShell` Inspector/folder summary controls, BFF folder scan client |
| `V4.1-09` to `V4.1-11` | publish/run controls, bottom run panel, station cards |
| `V4.1-12` to `V4.1-13` | artifact viewer, quality panel |
| `V4.1-14` to `V4.1-15` | recovery state, failure and attempt history UI |
| `V4.1-16` to `V4.1-17` | Agent debug proposal, governance evidence panel |

### FE-4 Blueprint Revision

Revise the V4.x blueprint so that:

1. V4.1 frontend completion depends on the 18-screen canonical path, not the older 7-screen summary.
2. V4.2 can reuse the V4.1 run panel for controlled execution preview.
3. V4.3-V4.6 remain future stage-specific work and cannot be represented as complete by V4.1 screens.

### FE-5 Focused Validation

Run focused frontend validation after code changes:

```bash
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
```

## 6. No False Green

The frontend rebuild must not display or imply:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
自动应用
自动发布
Agent 已执行
Agent 已发布
```

Completion language allowed after this frontend-planning update:

```text
V4.1 Stitch frontend rebuild plan ready for implementation review.
```
