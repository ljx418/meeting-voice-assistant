# V8 Target Architecture

文档状态：V8 architecture baseline / station-agent workflow pilot planning entry。

## 1. Architecture Goal

V8 在 V7 小型工作室与可解释 TUI 基线上新增：

```text
Station Agent Operating Layer
```

它把 station 从“固定工位逻辑”升级为“独立 Agent 在岗”：

```text
station = AgentDescriptor + Context + Memory + Model + Skill + MCP + ToolPolicy + Evidence
```

## 2. Target Planes

```text
Small Studio Control Plane
Mission TUI Plane
Workflow Blueprint Plane
Station Agent Operating Layer
Agent Context And Memory Plane
Skill / MCP / Tool Capability Plane
LLM Provider Plane
Controlled Runtime Plane
Terminal Worker Connector Plane
Runtime Report Plane
Review Console Plane
Evidence And Audit Plane
```

## 3. Architecture Flow

```text
harness tui / Product Console
 -> MissionAgent
 -> PlannerAgent
 -> WorkflowSpec / Diff
 -> Workflow Blueprint
 -> StationAgentRegistry
 -> StationAgentDescriptor per station
 -> StationAgentContextEnvelope
 -> CapabilityResolver
 -> LLM Provider / Skill / MCP / Tool
 -> Controlled Runtime or Terminal Worker Handoff
 -> Runtime Report
 -> Evidence Chain
 -> WorkflowExplainerAgent
```

## 4. Current Architecture Delta

| Area | Current V7 Baseline | V8 Target Delta | Risk |
| --- | --- | --- | --- |
| Station Runtime | Station is fixed workflow logic plus provider adapter | Every station has independent AgentDescriptor | Medium |
| Agent Identity | Agent builder / intent pilot exists but not station-agent runtime | Agent role / goal / model / memory per station | Medium |
| Context Injection | Prompt templates and refs exist for local document workflow | Station-scoped context envelope and memory policy | High |
| Skills / MCP | Skills and MCP connector infrastructure exists in parts | Per-Agent Skill / MCP / Tool binding with allowlist | High |
| Terminal Access | Codex / Claude / connector traces exist historically | Governed terminal worker design and controlled pilot | High |
| Explainability | Mission TUI and Evidence Chain exist | Per-Agent explanation, forbidden reasons and capability evidence | Medium |

## 5. Component Responsibilities

| Component | Responsibility | Runtime Truth Boundary |
| --- | --- | --- |
| StationAgentRegistry | registers station-agent bindings | does not execute |
| StationAgentDescriptor | declares role / goal / model / memory / tools / skills / MCP | not runtime truth |
| StationAgentContextEnvelope | provides scoped context refs | no raw secrets or raw prompt leakage |
| CapabilityResolver | decides allowed / denied Agent actions | policy decision only |
| AgentSkillBinding | binds approved skills to Agent | cannot bypass policy |
| AgentMcpBinding | binds approved MCP servers/tools | allowlist and evidence required |
| TerminalWorkerConnector | provides Codex / Claude / ChromeCLI handoff | high-risk; no direct durable mutation |
| WorkflowExplainerAgent | explains workflow, station state and evidence | read-only explanation |
| Evidence Chain | records Agent inputs, outputs, decisions and redaction | read-only |

## 6. Runtime Truth Boundary

V8 必须保留 V7/V6 边界：

```text
WorkflowSpec does not replace WorkflowDraft / WorkflowVersion.
Workflow Blueprint / Drawio is visualization only.
Runtime Report is read-only.
Evidence Chain is read-only.
Agent cannot directly execute durable mutation.
source=agent cannot bypass user confirmation.
Terminal worker cannot execute outside approved scope.
ChromeCLI cannot automate production accounts without explicit high-risk gate.
```

## 7. Target Architecture Diagram Summary

V8 drawio 必须包含：

```text
目标架构与当前架构差异
Station Agent Operating Layer
V8-0 to V8-9 development and acceptance plan
project milestones
acceptance gates
exit conditions
forbidden claims
```

## 8. Exit Architecture

V8 完成后，目标架构只能声明为：

```text
V8 complete: station-agent workflow pilot ready for review.
```

它支持用户体验：

```text
输入自然语言目标
 -> 看到每个 station 的 Agent
 -> 看到每个 Agent 的 role / goal / model / skill / MCP / tools
 -> 人工确认后运行
 -> 查看每个 Agent 的产物、证据、上下文、能力决策
 -> 在 TUI / Runtime Report / Evidence Chain 中审计
```

但仍不得声明：

```text
Agent executor ready
production autonomous coding ready
complete Workflow Studio ready
full multi-Agent orchestration ready
unrestricted terminal worker ready
```

