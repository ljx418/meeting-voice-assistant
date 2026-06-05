# V6 Target PRD

文档状态：V6-6 complete / ready for review；V6-7 implementation NO-GO / planning refinement only。本文定义 V6 production pilot readiness 目标和剩余产品化路径。

## 0. Current Baseline

当前 V6 基线：

```text
V6-0 complete: production pilot planning gate ready for review.
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
V6-3 complete: production observability and audit export pilot slice ready for review.
V6-4 complete: limited production controlled executor pilot slice ready for review.
V6-5 complete: governed Agent execution intent pilot gate ready for review.
V6-6 complete: production external app onboarding pilot slice ready for review.
```

以上 completion 仅代表对应 pilot slice ready for review，不代表完整生产 GA。

## 1. Product Goal

V6 的目标是把 V5 的 bounded dev/local、staging runtime 和 ready-for-review 证据推进到可审计的生产试点能力。

V6 不是完整 GA。V6 不默认证明 complete Workflow Studio、Agent executor ready、production controlled executor ready、production-ready external app support 或 full multi-Agent orchestration ready。

## 2. Target User Experience

V6 目标体验：

```text
生产用户完成认证和租户绑定
 -> 创建或选择 workspace / project / app
 -> 配置 provider profile 和 credential
 -> 通过 Mission Console 或 approved API 创建 workflow
 -> 用户确认或审批后运行受控 workflow
 -> Runtime Report 观察生产试点运行
 -> Review Console 处理失败、重跑、修复和审批
 -> Evidence Chain / Audit Export 支持审计复盘
 -> External App 在租户、凭证、配额和审计边界内接入
```

## 3. Capability Groups

### V6-0 Production Pilot Planning Gate

冻结 V6 PRD、目标架构、gap、验收矩阵、里程碑、No False Green claim guard。

### V6-1 Production Identity And Tenant Control Plane

生产身份、租户、workspace、project、app、service account 和 ownership boundary 的生产试点切片。

### V6-2 Production Credential And Provider Lifecycle

生产凭证引用、secret boundary、credential lease、rotation、revocation、provider invocation evidence 和 redaction。

### V6-3 Production Observability And Audit Export

生产试点级 audit retention/export、security event log、metrics、alerting 和 incident timeline。

### V6-4 Production Controlled Executor Runtime

生产试点级受控执行器，仅覆盖有限 action set：

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

### V6-5 Governed Agent Execution Intent Pilot

Agent 只能进入受治理 execution intent / handoff，不得绕过 policy、approval、credential boundary 或 user confirmation。

当前状态：complete / ready for review。V6-5 证明 MiniMax-backed AgentExecutionIntent、policy/capability decision、human-confirmed handoff 和 source=agent direct mutation denial，但不证明 Agent executor ready。

### V6-6 Production External App Onboarding

租户绑定 app registration、domain verification、origin allowlist、quota/rate limit、offboarding 和 SDK compatibility。

当前状态：complete / ready for review。V6-6 证明 tenant-bound app registration、domain verification before origin allowlist、quota/rate denial evidence、offboarding revocation 和 browser SDK internal route denial，但不证明 production-ready external app support。

### V6-7 Distributed Multi-Agent Runtime Productization

分布式 run coordination、worker assignment、attempt recovery、artifact lineage at scale、tenant/policy/credential boundary。

当前状态：complete / ready for review。V6-7 证明 repo-backed distributed runtime pilot slice，仍不证明 full multi-Agent orchestration ready 或 distributed multi-Agent runtime ready。

### V6-8 Product Console And Workflow Studio Gate

Thin Web Console 产品化优先。Full Workflow Studio 需要单独 PRD、架构和验收矩阵。

当前状态：complete / ready for review。V6-8 证明 Product Console / Thin Web Console read-only projection、BFF/browser route guard 和 manual confirmation UX，仍不证明 complete Workflow Studio ready。

### V6-9 Final Production Pilot Acceptance

汇总 V6-0 到 V6-8 证据，生成 HTML 验收看板，判断是否达到 production pilot baseline ready for review。

当前状态：complete / ready for review。V6-9 汇总 V6-0 到 V6-8 evidence package，claim scan、redaction scan 和 drawio XML validation 均通过。V6 complete 仍只代表 production pilot baseline ready for review，不代表 production ready 或 full production GA。

## 4. Non-Goals

V6-0 planning 不证明：

```text
production-ready external app support
enterprise auth ready
multi-tenant control plane ready
Agent executor ready
controlled executor ready
production controlled executor ready
complete Workflow Studio ready
complete AgentTalkWindow ready
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous workflow editing ready
```

## 5. Success Criteria

V6 成功标准：

```text
production pilot identity / tenant boundary is auditable
credential and provider lifecycle is redacted and revocable
audit export and incident timeline are usable
controlled execution pilot requires confirmation / approval / idempotency / kill switch
Agent execution remains governed and cannot mutate directly
external app onboarding pilot stays tenant-bound, auditable and SDK-safe
external app onboarding is tenant-bound and quota-governed
distributed multi-Agent runtime pilot has recovery and lineage evidence
product console remains observation and confirmation oriented
No False Green scan passes
```
