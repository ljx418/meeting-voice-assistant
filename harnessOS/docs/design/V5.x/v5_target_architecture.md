# V5 Target Architecture

文档状态：V5-0 planning-only。本文描述 V5 目标架构，不实现 runtime。

## 1. Architecture Baseline

V5 继承 V4 的 dev/local baseline：

```text
Headless Workflow Core
Mission Console
Workflow Blueprint
Runtime Report
Review Console
Evidence Chain
Runtime Capability Matrix
WorkflowSpec Registry
```

这些能力在 V4 中是 dev/local evidence，不是 production readiness。

## 2. V5 Target Planes

V5 目标架构引入以下 production planes：

```text
Identity And Tenant Plane
Credential And Provider Plane
Policy And Capability Plane
Controlled Execution Safety Plane
Observability And Audit Plane
External App Onboarding Plane
Product Console Plane
```

## 3. Plane Responsibilities

### Identity And Tenant Plane

负责：

```text
tenant_id
workspace_id
project_id
app_id
user_id
service_account_id
agent_id
scope guard
ownership chain
```

### Credential And Provider Plane

负责：

```text
provider profile
credential storage boundary
rotation / revocation
origin binding
audience binding
provider invocation evidence
redaction
```

### Policy And Capability Plane

负责：

```text
operation policy matrix
capability profile
risk flags
approval gate
user confirmation requirements
source=agent restrictions
```

### Controlled Execution Safety Plane

负责：

```text
executor sandbox boundary
runtime input approval
kill switch
timeout
idempotency key
rollback descriptor
```

### Observability And Audit Plane

负责：

```text
correlation_id
request_id
actor_id
operation evidence
audit retention
audit export
metrics
alerting
incident timeline
```

V5-3 规划该平面的 audit retention/export、security event log、metrics、alerting 和 incident timeline。该平面输出 read-only evidence 和 export package，不构造 Workflow runtime truth。

### External App Onboarding Plane

负责：

```text
app registration
domain verification
origin allowlist
SDK compatibility
quota / rate limit
customer offboarding
data export / deletion
```

### Product Console Plane

负责：

```text
production operations UI
manual confirmation
evidence review
audit export access
external app management
```

V5-6 默认先产品化 Thin Web Console。Full Web Studio requires separate PRD and acceptance. Evidence Review remains read-only. Report Review remains read-only. Admin ops cannot become runtime truth.

## 4. Runtime Truth Boundary

V5 必须继续保留：

```text
WorkflowSpec does not replace WorkflowDraft / WorkflowVersion.
Drawio / Blueprint is visualization only.
HTML Report / Runtime Report is read-only.
Evidence Chain is read-only.
EventBridge triggers refresh only.
Agent cannot bypass policy or user confirmation.
```

V5-4 保持为 Agent executor safety and dev/local trial 系列：

```text
V5-4A Agent Executor Design & Safety Gate
V5-4B Controlled Executor Dev/Local Trial, only if V5-4A passes
V5-4C Existing V4 Local Runtime Controlled Trial
```

V5-4A 只证明 safety gate ready for review，不证明 Agent executor ready。

V5-4B 只有在 V5-4A 通过后，才允许进入 controlled executor dev/local trial。该 trial 不证明 production controlled executor ready。

V5-4C 只允许通过既有 `/bff/v4_2/runtime` dev/local BFF wrapper 证明 existing V4 local workflow controlled trial ready for review。

Production controlled executor is moved after V5-6 and is carried by:

```text
V5-7A Production Controlled Executor Design Gate
V5-7B Production Controlled Executor Runtime Slice
```

V5-7A 是 production controlled executor 的设计门禁，不实现 runtime。它必须把 Identity And Tenant Plane、Credential And Provider Plane、Policy And Capability Plane、Controlled Execution Safety Plane、Observability And Audit Plane 串成一个可审计的生产执行边界。

V5-7B 才是 production controlled executor runtime slice 候选阶段。它必须以 V5-1 / V5-2 / V5-3 / V5-6 / V5-7A 为前置，并默认 HIGH risk。没有人工 high-risk proceed decision，不得进入实现。

V5-8 必须单独证明 production distributed state recovery、tenant isolation、observability、artifact lineage at scale、failure recovery、attempt history、policy and credential boundary。V4 dev/local provider-backed evidence 不得写成 full multi-Agent orchestration ready。

V5-5 和 V5-6 分别产品化 External App Onboarding Plane 与 Product Console Plane。V5-6 默认 Thin Web Console first，完整 Web Studio 必须单独 PRD 和验收。

## 5. No False Green

V5 target architecture 不证明：

```text
Agent executor ready
production controlled executor ready
complete Workflow Studio
distributed multi-Agent runtime
production-ready external app support
```
