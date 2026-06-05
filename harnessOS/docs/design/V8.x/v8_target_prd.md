# V8 Target PRD

文档状态：V8 PRD baseline / station-agent workflow pilot planning entry。

## 1. Product Positioning

V8 不追求完整 Agent executor、生产级自主开发、完整 Web Studio 或无限制多 Agent 编排。V8 的定位是：

```text
Station Agent Workflow Pilot
+ Explainable Agent TUI
+ Governed Terminal Worker Design
```

V8 的核心目标：

```text
让每个工作流 station 都有一个独立 Agent 在岗。
让每个 Agent 有独立 role / goal / memory / model / tools / skills / MCP。
让用户能看到每个 Agent 为什么做、能做什么、不能做什么、产出了什么。
让 Codex / Claude / ChromeCLI 只能作为受治理 connector / worker，而不是无限 Agent executor。
```

## 2. Target Users

| User | Goal | V8 Experience |
| --- | --- | --- |
| Workflow Operator | 用自然语言创建和运行工作流 | 看到每个 station 的 Agent、状态、产物和解释。 |
| Studio Admin | 管理 Agent 能力边界 | 配置 station Agent 的 model、skill、MCP、tool policy。 |
| Reviewer | 审查 Agent 输出和风险 | 查看 Agent context、能力决策、LLM invocation、evidence。 |
| Developer Operator | 让受控 Agent 生成代码建议 | 通过 Codex / Claude terminal worker 获取 diff proposal，并人工确认。 |

## 3. Main User Journey

```text
用户输入自然语言目标
 -> MissionAgent 捕获意图
 -> PlannerAgent 生成 WorkflowSpec / Diff
 -> Workflow Blueprint 展示 station 与 Agent
 -> 用户确认运行
 -> 每个 station 的 Agent 按 role / goal / context / skill / MCP 执行
 -> Runtime Report 展示 station Agent 状态
 -> Evidence Chain 展示 Agent 输入、输出、能力、模型和证据
 -> WorkflowExplainerAgent 解释整体流程、风险和结果
 -> Review Console 支持失败解释、handoff、局部重跑建议
```

## 4. Capability Groups

### Station Agent Contract

```text
StationAgentDescriptor
AgentRuntimeProfile
AgentRole
AgentGoal
AgentModelProfile
AgentMemoryPolicy
AgentToolPolicy
AgentSkillBinding
AgentMcpBinding
```

### Agent Context And Memory

```text
StationAgentContextEnvelope
WorkflowContextRef
ArtifactContextRef
EvidenceContextRef
MemoryContextRef
PromptTemplateRef
RedactionStatus
```

### Skill / MCP / Tool Binding

```text
CapabilityResolver
ToolAllowlist
SkillAllowlist
McpServerAllowlist
McpToolCallEvidence
HighRiskHandoffPolicy
```

### Terminal Worker Connectors

```text
CodexCliWorkerDescriptor
ClaudeCliWorkerDescriptor
ChromeCliSessionConnectorDescriptor
TerminalSessionPolicy
WorkspaceScopeGuard
CommandAllowlist
TranscriptCapture
DiffCapture
HumanReviewHandoff
KillSwitch
TimeoutPolicy
```

## 5. Success Criteria

V8 通过条件：

```text
每个 workflow station 都有 StationAgentDescriptor。
每个 Agent 有独立 role / goal / model / memory / tools / skills / MCP。
每个 workflow 默认至少有一个 WorkflowExplainerAgent。
每个 Agent LLM invocation 都记录 provider / model / prompt_template_ref / input_refs / output_refs。
Agent 只能读取 station-scoped context。
未授权 Skill / MCP / Tool 调用被拒绝。
source=agent durable mutation 被拒绝。
Codex / Claude / ChromeCLI 不绕过 controlled handoff。
TUI 能展示每个 station Agent 的身份、能力、状态、产物和证据。
No False Green scan PASS。
Redaction scan PASS。
```

## 6. Non-Goals

V8 不证明：

```text
Agent executor ready
production Agent executor ready
autonomous coding workflow ready
autonomous workflow editing ready
complete Workflow Studio ready
production-ready external app support
full multi-Agent orchestration ready
unrestricted terminal worker ready
ChromeCLI production automation ready
```

