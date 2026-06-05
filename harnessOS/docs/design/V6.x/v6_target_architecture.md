# V6 Target Architecture

文档状态：V6-6 complete / ready for review；V6-7 implementation NO-GO / planning refinement only。本文描述 V6 目标架构、当前实现基线和剩余架构差距。

## 1. Architecture Baseline

V6 继承 V5 的 bounded evidence：

```text
Headless Workflow Core
Mission Console
Workflow Blueprint
Runtime Report
Review Console
Evidence Chain
Runtime Capability Matrix
WorkflowSpec Registry
Limited staging controlled executor semantics
Bounded distributed multi-Agent runtime slice
```

这些能力仍是 ready-for-review / dev-local / staging / bounded slice，不是完整生产 GA。

## 2. V6 Target Planes

V6 目标架构包含以下生产试点平面：

```text
Identity And Tenant Control Plane
Credential And Provider Lifecycle Plane
Policy And Capability Plane
Production Controlled Execution Plane
Agent Governance Plane
Observability And Audit Export Plane
External App Onboarding Plane
Distributed Runtime Plane
Product Console Plane
```

## 2.1 Current Plane Status

| Plane | Owner Stage | Current Status | Boundary |
| --- | --- | --- | --- |
| Identity And Tenant Control Plane | V6-1 | complete / ready for review | not enterprise auth ready |
| Credential And Provider Lifecycle Plane | V6-2 | complete / ready for review | not production secret lifecycle ready |
| Observability And Audit Export Plane | V6-3 | complete / ready for review | not production audit export ready |
| Policy And Capability Plane | V6-4 | complete / ready for review for limited action set | not unrestricted policy runtime |
| Production Controlled Execution Plane | V6-4 | complete / ready for review for limited action set | not production controlled executor ready |
| Agent Governance Plane | V6-5 | complete / ready for review | not Agent executor ready |
| External App Onboarding Plane | V6-6 | complete / ready for review | not production-ready external app support |
| Distributed Runtime Plane | V6-7 | complete / ready for review | not full multi-Agent orchestration ready |
| Product Console Plane | V6-8 | complete / ready for review | not complete Workflow Studio ready |
| Final Acceptance Boundary | V6-9 | complete / ready for review | not full production GA |

## 3. Plane Responsibilities

### Identity And Tenant Control Plane

负责 tenant_id、workspace_id、project_id、app_id、user_id、service_account_id、ownership chain、tenant admin boundary 和 scope guard。

### Credential And Provider Lifecycle Plane

负责 provider profile、credential reference、secret store boundary、lease、rotation、revocation、emergency revoke、provider invocation evidence 和 redaction。

### Policy And Capability Plane

负责 operation policy matrix、capability decision、risk flags、approval gate、source=agent restrictions 和 user confirmation requirements。

### Production Controlled Execution Plane

负责 production execution envelope、runtime action allowlist、approval gate、idempotency key、kill switch、timeout、rollback descriptor 和 execution evidence。

### Agent Governance Plane

负责 Agent execution intent、handoff、capability decision、mutation denial evidence 和 source=agent direct mutation denial。

### Observability And Audit Export Plane

负责 audit retention、audit export package、security event log、metrics、alerting、incident timeline、correlation_id、request_id 和 actor_id coverage。

### External App Onboarding Plane

负责 tenant-bound app registration、domain verification、origin allowlist、quota/rate limit、SDK compatibility、offboarding 和 app access audit。

### Distributed Runtime Plane

负责 distributed run coordinator、agent worker registry、state checkpoint、attempt history、artifact lineage、worker recovery 和 per-worker policy/credential boundary。

### Product Console Plane

负责 Runtime Report、Evidence Review、Audit Export、External App Admin、Manual Confirmation UX 和 Review Console handoff。Full Workflow Studio 仍需单独 PRD。

## 4. Runtime Truth Boundary

V6 必须继续保留：

```text
WorkflowSpec does not replace WorkflowDraft / WorkflowVersion.
Blueprint / Drawio is visualization only.
Runtime Report is read-only.
Evidence Chain is read-only.
EventBridge triggers refresh only.
Agent cannot bypass policy, approval, credential boundary, or user confirmation.
Product Console admin ops cannot become runtime truth.
```

## 5. No False Green

V6 target architecture 不证明：

```text
complete Workflow Studio ready
Agent executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```
