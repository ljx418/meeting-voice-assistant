# HarnessOS Workflow Studio Design System

Status: V4.x prototype visual guideline, anchored on the V4.1 Workflow Studio PRD and updated for the Headless-first V4 roadmap.

Purpose: keep all Stitch-generated HarnessOS Workflow Studio prototype screens visually consistent and aligned with `harnessos_v4_1_workflow_studio_prd.md`.

This document is for prototype generation and design review. It is not a runtime implementation contract.

Headless-first product update:

V4.x no longer treats a full Web low-code Studio as the current mainline. The Web surface should be designed as Thin Web Console / Reference UI for observing workflow board state, opening Drawio and HTML reports, reviewing artifacts/quality/evidence, and triggering explicit user-confirmed operations. TUI / Command Palette, Drawio, and HTML reports are first-class product heads.

## 1. Product Feel

HarnessOS Workflow Studio / Thin Web Console should feel like a professional AI workflow operating workbench.

The product is not a pure chatbot, not a traditional dashboard, not a dark hacker console, and not currently a full low-code Studio mainline. It combines:

- low-code canvas
- Agent workflow assistant
- workflow run board
- artifact viewer
- quality panel
- governance evidence panel
- Drawio / HTML report launcher
- TUI transcript and command handoff review

The visual direction should be:

- modern SaaS
- light theme
- headless-first workbench
- thin Web Console
- ComfyUI-like canvas structure
- Dify-like clean interface
- professional, calm, and dense enough for repeated use
- Chinese UI copy
- clear user-confirmation boundary
- visible workflow state and evidence

## 2. Design Principles

1. Canvas first: the central workflow canvas is always the main visual focus.
2. Proposal first: generated workflows appear as ghost or pending nodes before user confirmation.
3. User confirmation is visible: Apply, Publish, Run, and Rerun must look user-triggered, not automatic.
4. Evidence is read-only: governance evidence must look inspectable but non-operational.
5. Operational density: this is a workbench, not a marketing page.
6. Clear hierarchy: canvas, Agent assistant, run board, artifacts, and evidence must be distinguishable at a glance.
7. Redaction by design: never show token, secret, raw payload, raw prompt, or signed URL-like content.
8. Accessible baseline: color cannot be the only status indicator.

## 3. Layout System

Use a 5-zone Workflow Studio layout:

```text
Top Bar
Left Node Library | Central Canvas | Right Agent / Inspector Panel
Bottom Run Panel
```

Recommended desktop frame:

- viewport: 1440 x 960
- top bar height: 56 px
- left rail width: 260 px
- right rail width: 360 px
- bottom panel height: 260 px
- central canvas fills remaining space
- collapsed side rail width: 64 px
- collapsed bottom rail height: 48 px

Responsive behavior:

- below 1024 px: left rail collapses first
- below 768 px: right rail becomes drawer or stacked panel
- bottom panel remains accessible by tabs
- no text overlap is allowed
- collapsed panels must leave a visible rail button so the user can reopen them

Do not use a landing-page hero. The first screen must be the usable Workflow Studio.

## 4. Color Tokens

Use a light neutral base with restrained blue and violet accents. Avoid a one-note purple theme.

```text
background.page: #F6F8FB
background.canvas: #F8FAFC
background.panel: #FFFFFF
background.subtle: #F1F5F9

border.default: #D9E2EC
border.strong: #B6C2D1

text.primary: #172033
text.secondary: #526173
text.muted: #7B8794

accent.blue: #2563EB
accent.violet: #7C3AED
accent.cyan: #0891B2

status.pending: #64748B
status.running: #2563EB
status.completed: #16A34A
status.failed: #DC2626
status.warning: #D97706
status.waiting: #9333EA

surface.pending: #F1F5F9
surface.running: #EFF6FF
surface.completed: #ECFDF5
surface.failed: #FEF2F2
surface.warning: #FFFBEB
surface.waiting: #F5F3FF
```

Rules:

- Use blue for primary workflow actions.
- Use violet only for Agent/proposal emphasis.
- Use green only for completed states.
- Use red only for failed/error states.
- Use amber for warnings and quality issues.
- Governance evidence should use neutral surfaces with subtle blue accents.

## 5. Typography

Recommended font stack:

```text
Inter, PingFang SC, Microsoft YaHei, system-ui, sans-serif
```

Typography scale:

```text
page title: 20 px / 28 px / 600
section title: 16 px / 24 px / 600
panel title: 14 px / 20 px / 600
body: 14 px / 22 px / 400
caption: 12 px / 18 px / 400
node title: 13 px / 18 px / 600
monospace artifact: 12 px / 18 px
```

Rules:

- Do not use oversized hero typography.
- Do not use negative letter spacing.
- Keep Chinese copy compact and readable.
- Buttons should use 13 to 14 px text.

## 6. Spacing And Shape

Spacing scale:

```text
4 px, 8 px, 12 px, 16 px, 20 px, 24 px, 32 px
```

Shape:

```text
small radius: 6 px
panel radius: 8 px
node radius: 8 px
button radius: 6 px
input radius: 6 px
```

Rules:

- Do not use highly rounded pill-heavy UI.
- Do not place cards inside cards.
- Use cards only for nodes, repeated artifacts, evidence records, and modal-like focused panels.
- Page sections should be full layout regions, not floating decorative cards.

## 7. Core Components

### Top Bar

Must include:

- HarnessOS Workflow Studio
- current project name
- current workflow name
- Draft / Version status
- run status
- publish action
- run action
- search
- notification icon
- user avatar placeholder

Copy examples:

```text
HarnessOS Workflow Studio
技术分享资料递归总结工作流
Draft rev. 2
Version v1
运行状态：Completed
发布版本
运行工作流
```

### Left Node Library

Use these V4.1 categories:

```text
输入节点
文件处理节点
AI Agent 节点
质量治理节点
审批节点
输出节点
```

V4.1 node list:

```text
文件夹输入
递归文件扫描
Markdown 文件过滤
Markdown 内容解析
子文件夹分组
子文件夹总结 Agent
总目录总结 Agent
质量检查 Agent
输出总结文件
```

Node library item anatomy:

```text
icon
node name
short description
category tag
```

### Central Canvas

Canvas requirements:

- light dotted grid background
- 24 px grid rhythm
- 9 visible nodes in a left-to-right or top-left-to-bottom-right linear flow
- clear connector lines
- ghost/pending node style before apply
- status badge on each node
- selected node outline
- failed node red border
- running node blue accent

Node card anatomy:

```text
node icon
node name
node type
status badge
input artifact label
output artifact label
quality mini-state
attempt count
```

Node states:

```text
Pending
Running
Completed
Failed
Waiting Approval
Ghost
```

### Right Panel

Tabs:

```text
Agent 助手
节点配置
Patch Diff
运行详情
治理审计
```

Agent assistant should look like a compact workbench chat, not a consumer chatbot.

Agent response must show:

- workflow draft name
- 9-node plan
- linear connection summary
- required user confirmations
- View Diff / 查看 Diff
- Apply to Draft / 应用到草稿

Boundary copy must be visible:

```text
Agent 只生成建议，不会自动执行。
应用草稿、发布版本和运行工作流都需要用户确认。
```

### Folder Input Inspector

Must show:

- path input: `Desktop/技术分享`
- authorize read button: `授权读取`
- debug scan button: `调试扫描`
- authorization status
- folder tree
- total file count
- Markdown file count
- child folder count
- unsupported file count
- empty folder count

Debug scan warning:

```text
调试扫描只预览文件结构，不生成总结。
```

### Bottom Run Panel

Tabs:

```text
Events
Trace
Artifacts
Quality
Approval
Patch
Evidence
```

Events tab:

- timestamp
- node name
- event type
- status

Artifacts tab:

```text
技术分享_总结结果/
  总览总结.md
  文件清单.json
  quality_report.json
  子文件夹总结/
    AgentOS_总结.md
    前端低代码_总结.md
    项目复盘_总结.md
```

Quality tab:

- summary coverage
- unsupported files
- empty folders
- missing summaries
- parse failed files
- low quality summaries
- suggestions

Evidence tab:

- read-only timeline
- proposal id
- handoff id
- user confirmed
- operation type
- runtime result ref
- risk flags
- policy decision
- correlation id
- redaction status

## 8. Page Templates

Generate prototype screens using these templates.

### Screen 1: Workflow Studio Overview

Show the full Studio layout with the 9-node workflow on canvas. Right panel defaults to Agent 助手. Bottom panel defaults to Events.

### Screen 2: Agent Draft Proposal

Show user request and Agent workflow plan. Canvas nodes are ghost/pending. Include 查看 Diff and 应用到草稿.

### Screen 3: Folder Authorization And Debug Scan

Show 文件夹输入 selected. Inspector displays path authorization, debug scan result, folder tree, and file stats.

### Screen 4: Workflow Running Board

Show nodes in mixed states: pending, running, completed, failed, waiting approval. Highlight current running node.

### Screen 5: Artifacts And Quality Report

Show artifact package structure, Markdown preview, and quality report with unsupported file and empty folder.

### Screen 6: Governance Evidence Chain

Show read-only evidence chain:

```text
Agent 建议 -> Handoff -> 用户确认 -> Operation Panel 执行 -> Runtime 结果 -> Evidence 记录
```

Do not show operation buttons inside governance evidence.

## 9. Content Requirements

Use Simplified Chinese UI copy.

Primary scenario text:

```text
帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。
```

Summary artifact names:

```text
AgentOS_总结.md
前端低代码_总结.md
项目复盘_总结.md
总览总结.md
文件清单.json
quality_report.json
```

Required child-folder summary sections:

```text
内容概览
核心主题
关键知识点
重要文件列表
可用于技术分享的材料
待补充 / 不完整内容
引用文件
```

Required overview summary sections:

```text
文件夹结构概览
主要技术主题
每个子文件夹摘要
推荐技术分享顺序
可直接用于 PPT 的内容
未处理文件 / 异常文件
生成时间与统计信息
```

## 10. Interaction Boundaries

The interface must communicate these boundaries:

```text
Agent 只能生成建议、解释、Patch Proposal、Handoff。
Agent 不能自动 Apply、Publish、Run、Rerun。
用户确认前，工作流草案只显示为 ghost / pending。
Debug Scan 不生成总结。
Apply 后才正式写入草稿。
Publish 后才生成可运行版本。
Run 必须由用户确认。
Rerun 必须由用户确认。
EventBridge 只触发刷新，不构造状态。
Governance Evidence 面板只读。
浏览器不能直接访问 /v1/rpc 或 /v1/events/subscribe。
```

## 11. Forbidden UI Copy

Do not show:

```text
自动应用
自动发布
Agent 已执行
Agent 已发布
完整 Workflow Studio 已完成
完整 AgentTalkWindow 已完成
Agent executor ready
controlled executor ready
production-ready external app support
```

## 12. Accessibility Requirements

- Text contrast must meet WCAG AA.
- Status must use both color and label.
- Buttons need clear disabled states.
- Inputs need visible labels.
- Focus states must be visible.
- Click targets should be at least 36 px high.
- Do not rely on hover-only information.

## 13. Visual Anti-Patterns

Do not generate:

- dark hacker UI
- pure chatbot product
- traditional admin dashboard
- landing page hero
- decorative gradient blobs
- excessive illustration
- deeply nested cards
- huge rounded pills everywhere
- dense tables as the primary canvas
- production-ready claims

## 14. Stitch Usage Prompt

When generating prototypes, prepend this instruction:

```text
Use docs/design/V4.1/DESIGN.md as the visual design source of truth. Generate a light-theme Chinese low-code AI workflow workbench for HarnessOS Workflow Studio. Keep the central canvas as the main visual focus, use the V4.1 local recursive Markdown folder summary workflow scenario, and preserve all user-confirmation and governance boundaries.
```
