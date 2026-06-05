# V8-7 Multi-Agent Project Workflow Pilot Plan

文档状态：V8-7 bounded runtime fixture PASS / ready for review。

目标：

```text
实现一个 bounded multi-Agent project workflow pilot。
```

建议 Agent：

```text
ProductAgent
ArchitectureAgent
PlanningAgent
ImplementationAgent
TestAgent
ReviewAgent
EvidenceAgent
ExplainerAgent
```

验收：

```text
每个 Agent 有独立 role / goal / memory / tools / skills / MCP。
每个 station attempt history 保留。
Agent handoff 可审计。
失败 station 可解释、可修复、可局部重跑。
No False Green scan PASS。
```

## 当前实现证据

```text
Evidence package:
docs/design/V8.x/evidence/v8-7-multi-agent-project-workflow/

status: PASS
evidence_scope: bounded_runtime_fixture
runtime_backed: true
station_count: 8
agent_descriptor_count: 8
attempt_history_count: 8
artifact_count: 8
implementation_agent_uses_handoff_not_direct_shell: PASS
test_agent_uses_allowlisted_readonly_command: PASS
source_agent_mutation_denied: PASS
claim_scan: PASS
redaction_scan: PASS
```

V8-7 实现的是受限项目工作流试点：每个工位有独立 Agent、attempt history 和 artifact，ImplementationAgent / TestAgent 只引用 V8-6 controlled terminal worker 的只读 handoff、transcript、diff proposal 和 command results。

禁止：

```text
full multi-Agent orchestration ready
autonomous coding workflow ready
Agent executor ready
```
