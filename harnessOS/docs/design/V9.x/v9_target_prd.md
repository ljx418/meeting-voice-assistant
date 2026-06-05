# V9 Target PRD

文档状态：V9 target PRD / planning baseline。

## 1. Product Goal

V9 面向 V8 之后的高风险能力补齐：

```text
让 Agent 不只是“在岗解释和产出”，而是在受控边界内具备执行、协作、代码开发、Studio 编辑和终端自动化能力。
```

V9 的产品目标不是一次性宣布完整生产可用，而是建立可审计、可回滚、可人工接管的高风险执行基线。

## 2. Target User Experience

用户期望的完整体验：

```text
用户提出目标
 -> 系统生成工作流和 Agent 分工
 -> Agent 形成执行计划
 -> 用户确认高风险动作
 -> Agent 在受控 executor 中执行
 -> 多 Agent 串行 / 并行协作
 -> 自动生成或修改代码
 -> 测试和 Review Agent 审查
 -> Studio 展示工作流、Agent、产物、diff、证据和 rerun
 -> 终端 worker 在受限 sandbox 中执行命令
 -> Evidence Chain 记录每一步
```

## 3. V9 Capability Goals

### Agent Executor

Agent 可以在 policy 允许、scope 限定、用户确认和 evidence 记录后执行动作。

必须具备：

```text
AgentExecutionPolicy
AgentExecutionEnvelope
CapabilityResolver
ApprovalGateDecision
KillSwitchDecision
TimeoutPolicy
RollbackDescriptor
ExecutionEvidence
```

### Multi-Agent Orchestration Runtime Target

支持真实串行、并行、fan-in / fan-out 和 synthesis。

必须具备：

```text
Agent message protocol
private memory / shared context boundary
attempt history
downstream stale propagation
artifact lineage with producer_agent_id / producer_attempt_id
failure recovery
lost worker recovery
conflict review
```

### Autonomous Coding Workflow Pilot

支持受控代码开发工作流：

```text
PlanningAgent
ImplementationAgent
TestAgent
ReviewAgent
FixAgent
EvidenceAgent
```

必须默认禁止：

```text
auto commit
auto push
auto deploy
secret read
unreviewed patch apply
```

### Workflow Studio Productization

从 Thin Console / TUI / Report 进一步产品化：

```text
workflow graph editor
station inspector
Agent profile editor
Skill / MCP / Tool binding UI
diff / publish / run / rerun UI
review console
evidence browser
```

Studio 必须通过 BFF / DTO 消费后端，不得直接写 runtime truth。

### Governed Terminal Worker Expansion

V9 不建议做真正 unrestricted terminal worker。目标改为：

```text
workspace-scoped write sandbox
command allowlist tiers
file write policy
diff capture
session replay
approval-gated commit / push / deploy proposal
```

### Production Governance / Evidence Hardening And Terminal Automation Gate

V9-7 兼容此前的 Production Terminal Automation Gate 口径，但正式范围是 production governance、evidence hardening 和 terminal automation 高风险门禁。它不能被解释为 production terminal automation ready。

生产终端自动化必须是高风险门禁：

```text
tenant isolation
credential lease
service account binding
human authorization
quota / rate limit
audit export
incident timeline
browser automation separate PRD
```

## 4. Out Of Scope For Default V9

```text
unrestricted arbitrary shell
automatic production deploy without approval
production browser account automation without separate PRD
full production GA
complete Workflow Studio GA
unbounded Agent self-modification
source=agent default durable mutation
```

## 5. Success Criteria

V9 completion can only be claimed after:

```text
V9-0..V9-7 evidence packages exist.
No FAIL / BLOCKED.
High-risk stages have human proceed decisions.
Durable mutation is denied unless user_confirmed=true OR valid human_authorization_ref is present.
source=agent default durable mutation is always denied.
No False Green claim scan PASS.
Redaction scan PASS.
Drawio XML valid.
Runtime evidence proves controlled execution, not just docs.
```

Allowed final claim:

```text
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

Forbidden final interpretations:

```text
production ready
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
production browser automation ready
production automation ready
```
