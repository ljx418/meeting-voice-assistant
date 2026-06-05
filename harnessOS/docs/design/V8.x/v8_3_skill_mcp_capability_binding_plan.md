# V8-3 Skill / MCP / Tool Capability Binding Plan

文档状态：V8-3 development and acceptance plan。

目标：

```text
每个 station Agent 可以定制 Skill、MCP 和工具能力，但必须通过 allowlist 和 CapabilityResolver。
```

核心合同：

```text
AgentSkillBinding
AgentMcpBinding
AgentToolPolicy
CapabilityResolver
ToolAllowlist
McpToolCallEvidence
HighRiskHandoffPolicy
```

验收：

```text
不同 station Agent 有不同 skill / MCP / tool policy。
未授权 Skill / MCP / Tool 调用被拒绝。
MCP tool call 有 evidence。
高风险工具必须 handoff / approval gate。
```

