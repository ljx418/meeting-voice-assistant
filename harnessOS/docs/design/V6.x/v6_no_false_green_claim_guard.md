# V6 No False Green Claim Guard

文档状态：V6-6 complete / ready for review；V6-7 implementation NO-GO / planning refinement only。本文定义 V6 claim guard。

## 1. Allowed Claims To Date

```text
V6-0 complete: production pilot planning gate ready for review.
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
V6-3 complete: production observability and audit export pilot slice ready for review.
V6-4 complete: limited production controlled executor pilot slice ready for review.
V6-5 complete: governed Agent execution intent pilot gate ready for review.
V6-6 complete: production external app onboarding pilot slice ready for review.
```

V6-5 不得改写为 Agent executor ready。
V6-6 不得改写为 production-ready external app support。

## 2. Forbidden Completion Claims

以下声明不得作为完成声明出现，除非对应阶段完成单独完整验收：

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

中文误报词：

```text
生产可用
企业认证已完成
多租户已完成
Agent执行器已完成
受控执行器已完成
生产级受控执行器已完成
完整工作流工作台已完成
完整低代码平台已完成
生产级外部应用接入已完成
分布式多Agent运行时已完成
自主工作流编辑已完成
生产试点已全面可用
生产级多租户平台已完成
```

## 3. Required Safe Context

如果必须提及 forbidden claims，必须出现在以下上下文之一：

```text
No False Green
Forbidden Claims
Non-Goals
不得声明
不能声明
禁止声明
不证明
not complete
not implemented
planned future
production blocker
```

## 4. Ready For Review Rule

`ready for review` 不得被摘要、completion note、gap、README 或审计包改写成 `ready`。

## 5. V5 To V6 Boundary Guard

V6 文档不得把以下 V5 evidence 改写为 production-ready：

```text
core slice ready for review
synthetic controlled executor trial
existing V4 local runtime trial
limited staging runtime slice
bounded distributed runtime slice
provider-backed dev/local evidence
read-only report projection
read-only audit projection
```

## 6. Acceptance

V6 claim guard passes when：

```text
all forbidden claims are guarded
no V5 evidence is upgraded to production-ready
all production blockers have V6 owner stages
high-risk stages require human proceed decision
ready for review is never shortened to ready
```
