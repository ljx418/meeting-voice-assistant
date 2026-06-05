# V8-9 Final Acceptance Plan

文档状态：V8-9 final acceptance framework PASS。

目标：

```text
生成 V8 最终验收看板和 evidence package。
```

必须包含：

```text
Station Agent inventory
Agent capability matrix
Agent context injection evidence
Agent LLM invocation evidence
Skill / MCP / Tool binding evidence
Terminal worker evidence if enabled
Runtime Report
Evidence Chain
No False Green scan
Redaction scan
drawio XML validation
```

通过条件：

```text
V8-0 到 V8-8 evidence package exists。
无 FAIL / BLOCKED。
所有高风险阶段有人类 proceed decision。
所有 station 都有 Agent。
至少一个 WorkflowExplainerAgent。
source=agent durable mutation denied。
Terminal worker 不越权。
No False Green PASS。
Redaction PASS。
drawio XML valid。
```

允许最终声明：

```text
V8 complete: station-agent workflow pilot ready for review.
```

当前阻断：

```text
none。
V8-9 已生成 framework evidence，final_claim_allowed=true。
V8-7 evidence_scope=bounded_runtime_fixture，不能被升级为 full multi-Agent orchestration。
```
