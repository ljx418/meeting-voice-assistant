# V4.1 Workflow Console UX Skill Review

Status: UX review only. This document records findings from the local UX Architect and UI Designer skill review. It is not a completion note.

Review date: 2026-05-27

Evidence:

- `docs/design/V4.1/ux-audit-evidence/01-default.png`
- `docs/design/V4.1/ux-audit-evidence/02-left-collapsed.png`
- `docs/design/V4.1/ux-audit-evidence/03-agent-tab.png`
- `docs/design/V4.1/ux-audit-evidence/04-node-tab.png`

Baseline:

- PRD: `docs/design/V4.1/harnessos_v4_1_workflow_studio_prd.md`
- Design system: `docs/design/V4.1/DESIGN.md`
- Stitch reference screens: `docs/design/V4.1/stitch-screenshots-review/`

## Executive Finding

The current Workflow Console is functional enough for automated V4.1 smoke and acceptance tests, but it is not yet a user-grade Workflow Studio experience.

The largest UX gap is that the product still opens as a technical fixture console instead of a task-oriented V4.1 local knowledge workflow. The screen contains real controls and a canvas, but the user has to infer the intended journey from scattered panels, debug-like labels, raw ids, and disabled-looking top actions. This creates a false sense of readiness: the system passes automated checks but does not yet guide a normal user through creating, applying, publishing, running, inspecting, and debugging the Desktop/技术分享 workflow.

## P0 Findings

### P0-1 Default Entry Does Not Match The V4.1 User Scenario

Observed:

- The default workflow is `Reference Workflow Console E2E`.
- The canvas shows `Collect Input`, `Transform Input`, and `Human Gate`.
- The PRD scenario is `Desktop/技术分享` recursive Markdown folder summary with 9 nodes.

Impact:

- A user cannot immediately understand how to complete the target task.
- The first screen feels like an internal test fixture, not a product surface.

Required correction:

- Default entry should be a V4.1 scenario workspace.
- Empty or initial state should guide the user to ask the Agent to create the local knowledge workflow.
- After proposal apply, the visible canvas should show the 9 PRD nodes:
  - 文件夹输入
  - 递归文件扫描
  - Markdown 文件过滤
  - Markdown 内容解析
  - 子文件夹分组
  - 子文件夹总结 Agent
  - 总目录总结 Agent
  - 质量检查 Agent
  - 输出总结文件

### P0-2 Agent Panel Exposes Raw Internal State

Observed:

- Agent panel shows long internal session / proposal / handoff / evidence identifiers.
- Some text resembles event-state serialization rather than product copy.

Impact:

- This violates the PRD's user-facing workflow assistant expectation.
- It increases perceived complexity and damages trust.

Required correction:

- Replace raw internal state with compact user-facing status:
  - 草案已生成，等待你查看 Diff
  - 需要你确认后才能应用到草稿
  - 已连接治理证据链
- Move raw ids to a developer diagnostics drawer hidden by default.

### P0-3 Primary User Journey Is Not Explicit Enough

Observed:

- Top actions show `保存草稿(后续)`, `调试运行(后续)`, `发布版本(后续)`.
- The product has many panels, but there is no clear stepper for:
  - 生成草案
  - 查看 Diff
  - 应用草稿
  - 授权读取
  - 调试扫描
  - 发布
  - 运行
  - 查看产物
  - 查看质量
  - 查看证据

Impact:

- A normal user cannot reliably discover the happy path.
- Buttons marked as future work reduce confidence in the current MVP.

Required correction:

- Add a V4.1 task rail or guided stepper.
- Show exactly one primary next action at a time.
- Only show `(后续)` labels in design gates, not in the main MVP path.

### P0-4 Canvas First Is Partially Met But Still Visually Contested

Observed:

- The canvas is visible and uses a dotted grid.
- However, left/right/bottom panels occupy most of the first viewport.
- Node labels and controls overlap visually with toolbar and panels in some states.

Impact:

- The canvas reads as a background container rather than the main work surface.

Required correction:

- Default mode should keep the canvas dominant.
- Left and bottom panels should be collapsed or slim by default for run-review mode.
- Add a clear canvas mode switch:
  - 搭建
  - 调试
  - 运行
  - 审计

## P1 Findings

### P1-1 Top Tabs Are Active But Semantically Weak

Observed:

- `工作流`, `节点`, `Agent`, `日志` are clickable.
- Switching tabs changes active styling but does not meaningfully reorganize the workbench.

Required correction:

- `工作流`: show scenario stepper, canvas, run status.
- `节点`: expand node library and inspector, focus node catalog / selected node.
- `Agent`: expand Agent assistant, show conversation and proposal cards.
- `日志`: expand bottom panel with events / traces / evidence.

### P1-2 Node Library Still Feels Like A Debug List

Observed:

- It contains category filters and node cards.
- Cards include date-like tags and mixed English/Chinese names.
- The most visible item is `角色一致性检查`, not the V4.1 folder workflow nodes.

Required correction:

- For V4.1, prioritize the 9 Markdown workflow nodes.
- Add compact node descriptions and ports in Chinese.
- Separate "推荐节点" from "全部节点".

### P1-3 Node Visual Language Needs Stronger Workflow Semantics

Observed:

- Nodes are cleaner than before but still look like generic cards.
- Port direction, node type, running state, quality state, and artifact count are not visually decisive.

Required correction:

- Use distinct headers for Input / Tool / Agent / Reviewer / Output.
- Make connections visually stronger and directional.
- Show run status with icon + label, not only color.

### P1-4 Bottom Panel Does Not Prioritize V4.1 Outputs

Observed:

- The default bottom panel is a generic run board.
- Artifacts and quality are hidden behind tabs.

Required correction:

- In completed state, default bottom panel should focus on:
  - 子文件夹总结
  - 总览总结
  - quality_report.json
- In running state, default bottom panel should focus on node progress.

## P2 Findings

### P2-1 Visual Density And Typography Need Tightening

Observed:

- Some top bar controls wrap or look too tall.
- English labels and Chinese labels are mixed without hierarchy.
- Several panels repeat labels and statuses.

Required correction:

- Use Chinese product copy for user-facing controls.
- Reserve English ids for diagnostics.
- Reduce top action height and prevent wrapping.

### P2-2 Collapsed Rails Work But Need Better Affordance

Observed:

- A collapsed left rail appears.
- The rail label is visible but feels like a floating tab rather than a stable workspace control.

Required correction:

- Use consistent rail icon plus vertical label.
- Keep rail controls pinned to the workspace edge.
- Add tooltip or accessible label for reopen behavior.

## Recommended Repair Sequence

### Stage UX-1: Scenario-First Entry

Goal:

- Replace default fixture presentation with the V4.1 local folder summary scenario.

Acceptance:

- First screen clearly invites the user to create or inspect the Desktop/技术分享 workflow.
- No raw fixture names or E2E labels appear in the main UI.

### Stage UX-2: Guided Task Flow

Goal:

- Add a visible V4.1 workflow progress stepper and next-action model.

Acceptance:

- A normal user can complete the PRD happy path without reading documentation.
- Each step has one clear primary button.

### Stage UX-3: Agent Panel Productization

Goal:

- Convert Agent output from diagnostic text into structured proposal cards, Diff cards, and handoff cards.

Acceptance:

- No raw ids or serialized state appear in normal Agent UI.
- Agent copy clearly states it cannot auto apply / publish / run.

### Stage UX-4: Canvas And Node Polish

Goal:

- Improve node layout, edge direction, category styling, and selected node behavior.

Acceptance:

- The 9-node Markdown workflow reads visually as a coherent pipeline.
- Node types and run states are understandable without opening Inspector.

### Stage UX-5: Output Review Focus

Goal:

- Make Artifacts / Quality / Governance views first-class in the completed workflow state.

Acceptance:

- User can find `AgentOS_总结.md`, `前端低代码_总结.md`, `项目复盘_总结.md`, `总览总结.md`, and `quality_report.json` within one click after run completion.

## No False Green Assessment

Current automated tests prove that core controls are present and the fixture flow can complete. They do not prove that the product is intuitive for a normal user.

Spec drift risk: MEDIUM

- Reason: implementation still opens as a reference fixture instead of the PRD scenario.

False green risk: HIGH

- Reason: E2E tests pass while the actual first-use workflow remains hard to understand.

Proceed decision:

- Do not claim user-grade V4.1 UX complete.
- Proceed with focused UX repair before adding V4.2 runtime scope.

## Repair Pass 2026-05-27

Status: focused UX repair implemented and verified.

Implemented:

- Default header and scenario rail now present the V4.1 `Desktop/技术分享` local knowledge workflow instead of making the reference fixture the main experience.
- Added a V4.1 guided stepper for draft proposal, Diff review, apply, authorization, debug scan, publish, run, artifacts, quality, and audit evidence.
- Header primary action now follows the current V4.1 stage and no longer exposes disabled future-work buttons as the main path.
- Agent status copy is user-facing; raw refresh ids are moved into a closed developer diagnostics section.
- Canvas and run-board station labels are projected into V4.1 local knowledge workflow labels while preserving underlying station ids for compatibility tests.
- Node library prioritizes V4.1 folder-summary nodes and moves extra BFF catalog nodes under a secondary controlled-node section.
- Forbidden copy such as `自动应用` and `自动发布` remains absent from normal UI.

Validation:

- `cd apps/workflow-console && npm test`: PASS, 76 passed.
- `cd apps/workflow-console && npm run build`: PASS.
- `./.venv/bin/python -m pytest tests/test_v4_1_folder_summary_bff.py -q`: PASS, 7 passed.
- `cd apps/workflow-console && CI=1 npm run test:e2e`: PASS, 17 passed.

Remaining UX risk:

- Spec drift risk: LOW to MEDIUM. The UI now matches the V4.1 scenario-first direction, but deeper usability still depends on manual inspection.
- False green risk: MEDIUM. Browser tests cover the main flow, but human review should still inspect whether the stepper and overlay feel natural in real use.
