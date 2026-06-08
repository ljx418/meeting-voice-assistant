# V9 Target PRD

文档状态：V9 target PRD / V9-2 evidence-aligned baseline。

## 1. Product Goal

V9 面向 V8 之后的高风险能力补齐：

```text
让 Agent 不只是“在岗解释和产出”，而是在受控边界内具备执行、协作、代码开发、Studio 编辑和终端自动化能力。
```

V9 的产品目标不是一次性宣布完整生产可用，而是建立可审计、可回滚、可人工接管的高风险执行基线。

## 1.1 Current Delivery State After V9-2

截至当前 V9 文档基线，已完成的 ready-for-review 能力是：

```text
V9-1 Agent Executor Safety Gate implementation.
V9-2 limited controlled Agent executor runtime slice.
```

V9-2 的产品解释必须保持受限：

```text
用户可以通过受控 runtime fixture 验证 workflow.instance.start / station.rerun / artifact.write / quality.evaluation.create 四类动作。
这些动作必须经过 policy / capability / HumanAuthorizationRef 或 user confirmation / approval / kill switch / idempotency / timeout / rollback / evidence chain。
source=agent direct durable mutation 仍被拒绝。
connector.call / external_llm.call / git.commit / git.push / production.deploy 等动作仍被拒绝。
```

V9-2 不得解释为：

```text
不得解释为通用 Agent executor 已完成
不得解释为受控执行器已完成
不得解释为生产级受控执行器已完成
不得解释为完整多 Agent 编排已完成
不得解释为自主代码工作流已完成
不得解释为完整 Workflow Studio 已完成
```

下一产品实现候选是 V9-3：真实 multi-Agent orchestration runtime slice。

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

当前距离该完整体验仍缺：

```text
V9-3 multi-Agent serial / parallel / fan-in / fan-out runtime evidence.
V9-4 coding workflow diff / test / review / fix-loop runtime evidence.
V9-5 governed terminal worker write sandbox evidence.
V9-6 Workflow Studio BFF / DTO / browser denylist evidence.
V9-7 production governance / evidence hardening high-risk evidence.
V9-8 final evidence aggregation.
```

V9 用户场景验收还必须覆盖三类更贴近真实使用的创意型工作流：

```text
Roman Forum debate: 不同身份 Agent 围绕哲学或复杂议题多轮讨论、互相质询并合成有 attribution 的结论。
Video creation storyboard workflow: 用户输入视频点子，系统生成 creative brief、script、shot list、storyboard prompts、分镜图 artifact refs 和 review report。
Natural-language workflow optimization: 用户用自然语言要求调整已有 workflow，系统生成 WorkflowDiff proposal，并在用户确认前不修改 runtime truth。
```

这些场景是 V9 的垂直验收切片，不得被解释为通用视频生产平台、完整自然语言工作流编辑器或完整多 Agent 编排已完成。

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

代表性用户场景：

```text
Roman Forum debate workflow.
Local technical design review workflow.
Video creation storyboard workflow.
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

自然语言优化工作流必须先产生 WorkflowDiff proposal，用户确认或 valid human_authorization_ref 存在前不得 durable mutation。

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
