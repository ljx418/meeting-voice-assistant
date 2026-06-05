# V6 Acceptance Gate Matrix

文档状态：V6 complete / ready for review。本文定义 V6 阶段验收门槛。

| Stage | Required Evidence | Must Pass | Human Decision |
| --- | --- | --- | --- |
| V6-0 | canonical docs, gap, drawio, claim guard, V5-8 handoff | XML valid, claim scan PASS, P0 closure PASS | no |
| V6-1 | identity / tenant audit evidence | cross-tenant and wrong-resource denial | optional |
| V6-2 | credential lifecycle and provider invocation evidence | no raw secret leakage, revoke denial | optional |
| V6-3 | audit export and incident timeline evidence | export valid, correlation coverage, source=agent export denial | optional |
| V6-4 | execution envelope, runtime evidence, pre-implementation closure, human proceed evidence | confirmation, approval, kill switch, idempotency, source=agent denial, no connector/external_llm call | recorded |
| V6-5 | MiniMax intent evidence, Agent execution intent, handoff, denial evidence | no source=agent direct mutation; Agent can only produce intent / handoff | recorded |
| V6-6 | app onboarding DTO/schema, domain/origin/quota/offboarding/SDK evidence package | domain before origin, wrong tenant denied, quota/rate denial auditable, offboarding revoke, browser SDK no direct runtime routes | optional / completed |
| V6-7A | pre-implementation closure docs, state machine, I/O, lifecycle, recovery matrix | contracts externally auditable; human high-risk decision required before V6-7B | recorded before V6-7B |
| V6-7B | distributed runtime and recovery evidence after human proceed | recovery, lineage, tenant/policy boundary, old attempts retained, claim scan PASS | recorded |
| V6-8 | UI/BFF/browser safety evidence and product console evidence package | read-only reports, no hidden mutation form, manual confirmation UX, claim scan PASS | optional / completed |
| V6-9 | final HTML dashboard and final-acceptance-data.json | V6-0 through V6-8 evidence exists, no FAIL / BLOCKED, claim scan PASS, redaction PASS, drawio XML PASS | completed |

## Required Global Assertions

```text
WorkflowSpec cannot replace runtime truth
Blueprint / Drawio is visualization only
Runtime Report is read-only
Evidence Chain is read-only
EventBridge refresh-only
durable mutation requires user confirmation or human authorization
source=agent cannot directly execute durable mutation
browser does not call internal runtime routes directly
raw secret / raw prompt / raw artifact content does not leak
V6-5 / V6-7B high-risk implementation requires separate human proceed decision
```

## No False Green Boundary

通过某一阶段验收只代表该阶段 pilot slice ready for review。不得把单阶段 PASS 改写成以下完整能力：

```text
complete Workflow Studio ready
Agent executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous workflow editing ready
```
