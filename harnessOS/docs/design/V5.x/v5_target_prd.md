# V5 Target PRD

文档状态：V5-0 planning-only。本文定义 V5 production productization 目标，不实现功能。

## 1. Product Goal

V5 的目标是把 V4 dev/local Headless workflow baseline 推进到可审计的 production productization 路线。

V5 不是继续扩张 V4。V5 必须单独处理生产认证、租户隔离、凭证生命周期、生产审计、外部应用接入和 Agent executor 安全门禁。

## 2. Target User Experience

V5 目标体验是：

```text
生产用户完成认证和租户绑定
 -> 注册或选择 workspace / project / app
 -> 配置 provider / credential / capability
 -> 通过 Mission Console 或 API 创建 workflow
 -> 用户确认后运行受控 workflow
 -> Runtime Report 观察生产运行
 -> Review Console 处理失败、重跑和审批
 -> Evidence Chain / Audit Export 支持合规复盘
 -> External App 可通过受控 API 接入
```

## 3. V5 Capability Groups

### V5-0 Production Productization Planning

只做规划、gap、claim guard、验收标准和架构冻结。

### V5-1 Production Auth / Tenant Boundary

目标：

```text
tenant identity
workspace / project ownership
production auth boundary
scope guard
service account identity
```

No False Green：V5-1 不能直接声明 `enterprise auth ready`，除非 production auth / tenant boundary 的完整验收通过。

### V5-2 Credential / Provider Lifecycle

目标：

```text
provider profile
credential issue / rotate / revoke
origin / audience / tenant binding
redacted provider invocation evidence
```

### V5-3 Observability / Audit Export

目标：

```text
audit retention
audit export
security event log
metrics
alerting
incident timeline
correlation_id / request_id coverage
```

V5-3 必须单独证明 audit retention/export、metrics、alerting、incident timeline 与 redaction。V4 Evidence Chain 和 V5-2 provider evidence 只能作为输入证据，不能直接声明 production audit export ready。

### V5-4 Agent Executor Safety Gate

目标：

```text
policy matrix
capability decision
approval gate
executor sandbox boundary
kill switch
runtime evidence
```

V5-4 不能直接把 Agent 变成 autonomous executor。所有 durable mutation 仍必须经过 policy、user confirmation 和 evidence。

建议后续拆分：

```text
V5-4A Agent Executor Design & Safety Gate
V5-4B Controlled Executor Dev/Local Trial, only if V5-4A passes
```

V5-4A 只能声明 safety gate ready for review，不能声明 Agent executor ready。

V5-4B 只能在 V5-4A 通过后进入 dev/local controlled executor trial，不得声明 production controlled executor ready。

V5-4C 只证明 existing V4 local workflow controlled trial ready for review。它不得升级为生产级受控执行能力。

Production controlled executor 已移动到 V5-6 之后，作为 V5-7A / V5-7B 纳入 V5 计划：

```text
V5-7A Production Controlled Executor Design Gate
V5-7B Production Controlled Executor Runtime Slice
```

V5-7A 只做设计门禁，必须覆盖 production policy enforcement、tenant isolation、credential boundary、approval gate、sandbox、timeout、kill switch、rollback、idempotency、audit retention/export 和 incident response。V5-7A 不实现生产执行器。

V5-7B 只有在 V5-7A 通过且高风险人工 proceed decision 记录后才允许进入实现。V5-7B 必须先证明 limited production-controlled action set，不得默认开放 Agent 自动执行、任意 connector.call 或 autonomous workflow editing。

### V5-5 Production External App Onboarding

目标：

```text
app registration
domain verification
origin allowlist
quota / rate limit
customer offboarding
SDK compatibility policy
```

### V5-6 Web Studio Productization

目标：

```text
Thin Web Console productization first
Full Web Studio requires separate PRD and acceptance
operational UX
manual confirmation UX
evidence review UX
```

完整低代码 Studio 不是 V5-0 前提，必须单独验收。Evidence Review 和 Report Review 继续只读；admin ops 不能成为 runtime truth。V5-6 不得让路线回到 Full Web Low-Code Studio first。

### V5-7A / V5-7B Production Controlled Executor

目标：

```text
production execution policy
tenant-isolated controlled execution
credential-bound runtime inputs
approval-gated high-risk actions
idempotency / rollback / kill switch
audit export and incident timeline
```

No False Green：V5-7A 是设计门禁，V5-7B 是受限 production controlled executor runtime slice 候选。二者均不得把 V5-4B synthetic evidence 或 V5-4C dev/local bridge evidence 写成生产执行能力。

### V5-8 Distributed Multi-Agent Runtime

目标：

```text
distributed run coordination
parallel / serial multi-agent runtime
attempt recovery
artifact lineage at scale
runtime isolation
```

No False Green：V4 UX-08 / UX-09 / UX-10 只是 dev/local provider-backed evidence。V5-8 必须单独证明 production distributed state recovery、tenant isolation、observability、artifact lineage at scale、failure recovery、attempt history、policy and credential boundary，才能进入生产级多 Agent runtime 声明。

V5-8 还必须继承 V5-1 tenant boundary、V5-2 credential boundary、V5-3 observability / audit export 和 V5-7A/B production controlled executor gate 作为前置条件。

## 4. Non-Goals And No False Green

V5 planning 不证明：

```text
production-ready external app support
Agent executor ready
controlled executor ready
production controlled executor ready
complete Workflow Studio ready
full multi-Agent orchestration ready
autonomous workflow editing ready
```

V5 不能把 V4 dev/local evidence 写成 production-ready。

## 5. Success Criteria

V5-0 通过条件：

```text
V5 target PRD reviewed
V5 target architecture reviewed
V5 gap analysis reviewed
V5 acceptance plan reviewed
V5 claim guard reviewed
V4 closure boundary preserved
No forbidden production claim outside No False Green context
V5-1 implementation not started
```
