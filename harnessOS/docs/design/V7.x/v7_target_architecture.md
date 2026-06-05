# V7 Target Architecture

文档状态：V7 architecture baseline / ready for review。本文定义 V7 目标架构。

当前口径：

```text
V7-0 complete: V7 small studio and explainable TUI planning gate ready for review.
V7-1 complete: small studio production pilot control plane ready for review.
V7-2 complete: explainable Mission TUI pilot ready for review.
V7-3 complete: natural-language workflow creation and controlled run experience ready for review.
V7 complete: small studio production pilot and explainable TUI baseline ready for review.
```

## 1. Architecture Goal

V7 在 V6 production pilot baseline 上增加两个面向产品使用的架构层：

```text
Small Studio Control Plane
Explainable Mission TUI
```

它们不替代 runtime truth，而是把 V6 的 identity、credential、policy、controlled runtime、distributed runtime、Product Console 和 Evidence Chain 串成小型工作室可用体验。

## 2. Target Planes

```text
Small Studio Control Plane
Identity / Tenant / Workspace / Project / App Plane
Credential And Provider Plane
Policy And Capability Plane
Explainable Mission TUI Plane
Workflow Blueprint Plane
Controlled Runtime Plane
Distributed Runtime Pilot Plane
Runtime Report Plane
Review Console Plane
Evidence And Audit Plane
Product Console Plane
```

## 3. Architecture Flow

```text
harness tui / Product Console
 -> Small Studio Context Resolver
 -> Mission Intent Capture
 -> Experience State Projection
 -> WorkflowSpec / Diff
 -> Workflow Blueprint Projection
 -> User Confirmation
 -> Controlled Runtime / Distributed Runtime Pilot
 -> Runtime Report
 -> Review Console
 -> Evidence Chain / Audit Export
```

## 3.1 Current Architecture Delta

| Area | Current V6/V7 Baseline | V7 Target Delta | Status |
| --- | --- | --- | --- |
| Studio Scope | V6 production pilot evidence and V7-1 repo-backed studio projection | Small Studio aggregation plane for workspace/project/app/provider/credential/quota/audit refs | V7-1 complete / ready for review |
| Mission Interaction | V7-2 `harness tui` transcript-only state line and links | Explainable TUI becomes the main workflow head for goal capture and action explanation | V7-2 complete / ready for review |
| Workflow Creation | Existing V4/V6 headless specs and local document workflow evidence | Natural language -> WorkflowSpec / Diff -> Blueprint | V7-3 complete / ready for review |
| Workflow Run | V6 controlled runtime pilot boundaries | User-confirmed local Markdown technical document workflow run with provider-backed evidence | V7-3 complete / ready for review |
| Final Acceptance | V6 final acceptance dashboard pattern | V7 final small studio dashboard proving create/run/review/evidence experience | V7-4 complete / ready for review |

## 4. Component Responsibilities

| Component | Responsibility | Runtime Truth Boundary |
| --- | --- | --- |
| Small Studio Context Resolver | resolves studio/workspace/project/app/provider refs | does not execute workflow |
| Mission TUI | captures natural language and renders state line | does not mutate without confirmation |
| Experience State Projection | shared UX read model | not runtime truth |
| WorkflowSpec Registry | stores portable workflow specs | not WorkflowDraft / WorkflowVersion |
| Workflow Blueprint | Drawio/text visualization | read-only visualization |
| Controlled Runtime | limited confirmed action execution | action allowlist only |
| Review Console | failure explanation and handoff | cannot directly execute |
| Evidence Chain | audit replay | read-only |
| Product Console | browser observation and manual confirmation | admin ops cannot construct runtime truth |

## 5. Runtime Truth Boundary

V7 必须保留 V6 边界：

```text
WorkflowSpec does not replace WorkflowDraft / WorkflowVersion.
Blueprint / Drawio is visualization only.
Runtime Report is read-only.
Evidence Chain is read-only.
EventBridge triggers refresh only.
Agent cannot bypass policy, approval, credential boundary, or user confirmation.
Product Console admin ops cannot construct runtime truth.
```

## 6. Target Architecture Diagram Summary

V7 drawio 必须包含：

```text
目标架构与当前架构差异
Small Studio production pilot
Explainable Mission TUI
Workflow creation / run / evidence path
V7-0 to V7-4 stage plan
acceptance gates
exit conditions
forbidden claims
```

## 7. Exit Architecture

V7 完成后，目标架构只能声明为：

```text
Small Studio production pilot and explainable TUI baseline ready for review.
```

它应支持用户理解并体验：

```text
输入自然语言目标
 -> 看到状态线、可用动作和禁止原因
 -> 生成 WorkflowSpec / Diff / Blueprint
 -> 人工确认后启动受控运行
 -> 查看 Runtime Report / Quality / Evidence Chain
 -> 通过 Review Console 做失败复核和 handoff
```

但仍不得声明：

```text
production ready
full production GA
complete Workflow Studio ready
Agent executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```
