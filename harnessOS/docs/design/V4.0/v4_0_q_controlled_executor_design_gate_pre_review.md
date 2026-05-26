# V4.0-Q Controlled Executor Design Gate Pre-Review

文档状态：pre-review only；V4.0-Q implementation completed as design gate on 2026-05-22。
适用范围：仅用于 V4.0-Q Controlled Executor Design Gate 阶段启动前审查。
本文件是 Q 阶段前置审查入口，用于替代逐个打开大量历史文档；历史文档仍保留为证据来源，但本阶段优先审查本文。

审查后实现结论：V4.0-Q 只落地 controlled executor design gate、机器可读 policy matrix、capability profile、approval gate design、sandbox boundary、rollback / kill switch design、future evidence contract 和 claim guard。它没有实现 executor route、worker、runtime service、connector.call path、external_llm.call path 或 Agent 自动 mutation。

## 1. 当前基线

Q 启动前允许声明：

```text
V4.0-P complete: AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation.
```

Q 启动前仍不能声明：

```text
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
autonomous workflow editing ready
complete Workflow Studio ready
production-ready external app support
full low-code canvas editing ready
```

## 2. Q 阶段定位

V4.0-Q 只做 Controlled Executor Design Gate。

它不是 executor implementation，不新增执行 route，不让 Agent 执行 mutation，不改变 V3.6 runtime contract。

Q 阶段最多产出：

```text
controlled executor design gate ready for review
```

不能产出：

```text
controlled executor ready
Agent executor ready
autonomous workflow editing ready
production-ready external app support
```

## 3. 必须保持的边界

Agent 仍只能：

```text
propose
handoff
explain
navigate
```

Agent 仍不能：

```text
apply patch
reject patch
publish workflow
approval.respond
context.update
business.event.emit
start workflow
rerun station
call connector
call external LLM
write artifact
create quality evaluation
```

所有 durable mutation 仍必须走已有用户显式确认路径：

```text
Editing Panel
Approval Panel
Context Panel
V4.0-G governed workflow.patch apply/reject/publish path
V4.0-D approval/context/business event user-confirmed path
```

## 4. Q 阶段审查清单

### Q1 Policy Matrix

必须审查每类 action 的策略：

```text
forbidden
proposal_only
handoff_only
user_confirmed_only
approval_gated_future
never_executor
```

覆盖 action：

```text
workflow.patch.apply
workflow.patch.reject
workflow.template.publish
approval.respond
workflow.context.update
business.event.emit
workflow.instance.start
station.rerun
connector.call
external_llm.call
artifact.write
quality.evaluation.create
```

### Q2 Capability Profile

Q 阶段只设计 capability，不启用 executor capability。

建议 profile：

```text
agent.propose
agent.handoff
agent.explain
agent.navigate
executor.dry_run
executor.user_confirmed_execute
executor.approval_gated_execute
executor.admin_override
```

本阶段必须确认：

```text
executor.* capability remains inactive
source=agent cannot execute mutation
capability token cannot bypass user confirmation
```

### Q3 Approval Gate

必须定义哪些未来 action 永远需要 approval 或 user confirmation。

高风险条件：

```text
requires_approval=true
risk_flags contains high-risk item
external side effect
connector mutation
publish workflow
context mutation
business event emit
artifact write
quality score mutation
```

### Q4 Sandbox Boundary

未来 executor 即使被允许，也只能访问 redacted DTO。

禁止访问：

```text
capability_token
subscription_token
Authorization
Bearer
secret
raw_trace_payload
raw_artifact_content
raw_connector_payload
raw prompt
upstream signed URL
WorkflowStore direct write
WorkflowDraft direct write
WorkflowVersion direct write
StationRun direct write
```

### Q5 Rollback and Kill Switch

必须先设计：

```text
per-agent kill switch
per-workspace kill switch
capability revocation
operation timeout
idempotency key
rollback descriptor
manual recovery path
audit retention
```

### Q6 Evidence and Audit

未来 executor 任何 action 都必须形成 evidence chain。

Evidence fields 至少包括：

```text
proposal_id
handoff_id
user_confirmed
approval_id
capability_decision
policy_decision
runtime_result_ref
correlation_id
idempotency_key
redaction_status
created_at
created_by
```

### Q7 Event Truth

EventBridge 继续只触发 refresh。

禁止从 event payload 构造：

```text
executor truth
agent action truth
patch truth
approval truth
evidence truth
board/status truth
context truth
```

收到事件后必须重新拉 BFF DTO。

### Q8 Claim Guard

必须扫描设计内容、源码、UI copy 和 completion note，禁止误导声明。

禁止完成声明：

```text
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
autonomous workflow editing ready
complete Workflow Studio ready
production-ready external app support
full low-code canvas editing ready
```

禁止 UI 文案：

```text
自动应用
自动发布
已帮你修改并发布
Agent 已执行
Agent 已发布
```

## 5. 已完成阶段摘要

以下内容是 Q 阶段前置审查所需的全部历史上下文摘要。审查时不需要另行打开其他设计文档。

### V3.5 基线

V3.5 已冻结为 dev/local Application Adaptation Layer。

已完成能力：

```text
SDK
BFF
React hooks
EventBridge
Embed Contract
capability token
scope guard
Reference App boundary
```

V3.5 的边界：

```text
它是应用接入层，不是 workflow runtime。
它不提供 Agent executor。
它不提供 production-ready auth or multi-tenant control plane。
```

### V3.6 基线

V3.6 已冻结为 Workflow Runtime Contract and Pipeline Operating Model。

已完成 runtime truth：

```text
WorkflowTemplate
WorkflowVersion
WorkflowDraft
WorkflowInstance
Station
StationRun
ArtifactContract
QualityEvaluation
Pipeline Board
Business Event Bridge
Workflow Context
WorkflowPatch
Approval point
Trace summary
```

V3.6 的关键边界：

```text
WorkflowDraft and WorkflowVersion are runtime truth.
WorkflowPatch is the governed mutation mechanism for draft changes.
Board and InstanceStatus are runtime read DTOs.
EventBridge is notification and refresh trigger only.
UI and Agent must not write WorkflowStore directly.
UI-only state must not be persisted into runtime objects.
```

### V4.0-O 基线

V4.0-O 已完成 governed canvas proposal workflow。

已完成能力：

```text
PatchQueueDTO
selected patch stale guard
CanvasDraftProjection freshness marker
controlled node catalog versioning
Inspector schema mapping V2
edge contract validation V2
proposal apply refresh and race hardening
fixture isolation
DTO and DOM redaction
event payload not trusted as truth
claim guard
```

V4.0-O 的边界：

```text
Canvas is not runtime truth.
Node drag creates proposal only.
Edge drag creates proposal only.
Inspector typing updates local dirty state only.
Apply, reject and publish remain user-confirmed governed operations.
PatchQueueDTO, CanvasDraftProjection and catalog versioning are BFF/UI read models.
```

### V4.0-P 基线

V4.0-P 已完成 AgentTalkWindow interaction E2E baseline。

已完成能力：

```text
AgentTalkInteractionState read model
selected_suggestion_id
selected_proposal_id
selected_handoff_id
selected_patch_id
selected_evidence_id
stale_reasons
refresh_generation
read-only explain workflow
read-only summarize events
read-only summarize context
read-only summarize quality
suggest patch to proposal
proposal to handoff
handoff to Editing, Approval or Context panel
read-only evidence review
fake event payload not trusted
DOM, DTO, error and event redaction
browser smoke for interaction and event truth
```

V4.0-P 的边界：

```text
AgentTalkInteractionState is BFF/UI read model only.
Explain and summarize do not create patch proposal.
Explain and summarize do not create handoff.
Handoff opens panel only.
Opening panel does not execute operation.
Apply, reject and publish still require Editing Panel user confirmation.
approval.respond still requires Approval Panel user confirmation.
context.update and business.event.emit still require Context Panel user confirmation.
source=agent remains forbidden for mutation.
Evidence review is read-only.
EventBridge only triggers refresh.
```

## 6. Q 阶段应产出的内容

Q 阶段应新增一份 controlled executor design gate plan 和一份 completion note。文件命名由实现阶段决定，但内容必须覆盖本节。

计划文档必须包含：

```text
stage positioning
allowed claim
forbidden claims
policy matrix
capability profile
approval gate
sandbox boundary
rollback and kill switch
evidence and audit contract
event truth regression
redaction rules
claim guard
No False Green statement
validation commands
```

完成说明必须记录：

```text
actual files changed
tests added
docs updated
policy matrix result
capability profile result
approval gate result
sandbox boundary result
rollback and kill switch result
evidence and audit contract result
claim guard result
validation command results
No False Green statement
```

## 7. Q 阶段建议测试内容

后端和合同测试应覆盖：

```text
controlled executor design gate exists as design only
no executor route added
no Agent execute route added
policy matrix classifies every action
forbidden actions remain blocked
source=agent mutation remains rejected
executor capabilities remain inactive
capability token cannot bypass user confirmation
approval gate requires user confirmation or approval for high risk actions
sandbox boundary rejects token, secret, raw payload and raw prompt fields
evidence contract requires proposal, handoff, policy, capability and idempotency fields
event payload cannot construct executor truth
claim guard blocks forbidden completion claims
```

前端 source scan 应覆盖：

```text
no UI copy says 自动应用
no UI copy says 自动发布
no UI copy says 已帮你修改并发布
no UI copy says Agent 已执行
no UI copy says Agent 已发布
no direct core runtime route is called
no executor route is called
no browser request calls direct runtime event subscription
```

Browser smoke 如需新增，只允许 read-only design gate smoke。

Browser smoke 不得覆盖或触发：

```text
execute
apply by Agent
publish by Agent
approval respond by Agent
context update by Agent
business event emit by Agent
connector call by Agent
external LLM call by Agent
```

## 8. Q 阶段建议回归命令

实现阶段应至少执行：

```text
Q focused backend and contract tests
all V4.0 focused tests
V3.6 focused regression
V3.5 focused regression
full pytest
workflow-console unit tests
workflow-console build
workflow-console e2e if browser smoke is changed
TypeScript SDK tests
drawio XML validation if diagram is changed
```

## 9. 给 ChatGPT 的审查问题

请逐项审查以下问题：

```text
1. 本 Q 阶段计划是否仍只是 design gate，而不是 executor implementation？
2. 是否存在任何让 Agent 自动执行 mutation 的路径？
3. Policy matrix 是否覆盖所有高风险 action？
4. Capability profile 是否明确 executor capability 不启用？
5. Approval gate 是否阻止 high risk action 绕过用户确认？
6. Sandbox boundary 是否禁止 token、secret、raw payload、raw prompt 和 direct store access？
7. Rollback and kill switch 是否足以作为未来 executor 前置门禁？
8. Evidence contract 是否能审计每一次未来执行意图？
9. EventBridge 是否仍只触发 refresh？
10. 文档是否有 controlled executor ready、Agent executor ready 或 production-ready 的过度声明？
11. UI copy 是否存在自动应用、自动发布、Agent 已执行、Agent 已发布等误导文案？
12. 测试计划是否能防止 false green？
```

## 10. No False Green

V4.0-Q 只证明 controlled executor design gate。

它不证明：

```text
controlled executor ready
Agent executor ready
autonomous workflow editing ready
complete AgentTalkWindow ready
complete Workflow Studio ready
production-ready external app support
```
