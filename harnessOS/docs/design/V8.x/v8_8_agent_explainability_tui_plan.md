# V8-8 Agent Explainability TUI Plan

文档状态：V8-8 development and acceptance plan。

目标：

```text
让 TUI 展示每个 station 的 Agent 身份、能力、状态、产物和证据。
```

TUI 必须展示：

```text
Agent role / goal
model profile
memory policy
skills
MCP
available actions
forbidden reasons
run evidence
artifact outputs
handoff status
```

验收：

```text
用户能看到每个 station 哪个 Agent 在岗。
用户能看到每个 Agent 能做什么和为什么不能做某些动作。
Runtime Report / Evidence Chain / Blueprint 互相可链接。
TUI 不构造 runtime truth。
```

