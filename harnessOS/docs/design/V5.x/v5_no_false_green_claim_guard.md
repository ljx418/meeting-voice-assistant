# V5 No False Green Claim Guard

文档状态：V5-0 planning-only。本文定义 V5 claim guard，不实现功能。

## 1. Allowed V5-0 Claim

```text
V5-0 complete: production productization planning gate ready for review.
```

该声明只代表 V5 planning 文档、gap、验收和 claim guard 准备好接受审查。

## 2. Forbidden Claims

No False Green：以下声明不得作为完成声明出现：

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
autonomous workflow editing ready
distributed multi-Agent runtime ready
unrestricted Agent executor
```

No False Green：以下中文误报词不得作为完成声明出现：

```text
生产可用
企业认证已完成
多租户已完成
Agent执行器已完成
受控执行器已完成
完整工作流工作台已完成
完整低代码平台已完成
生产级外部应用接入已完成
自主工作流编辑已完成
生产级Agent执行器已完成
生产级受控执行器已完成
分布式多Agent运行时已完成
```

## 3. Required Context For Mentions

如果文档必须提及 forbidden claims，必须出现在以下上下文之一：

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

## 3.1 Ready For Review Wording Rule

No False Green：`ready for review` 不得在摘要、completion note、gap、README 或审计包中被改写为 `ready`。

示例：

```text
allowed: V5-3 planning package ready for review
forbidden: V5-3 ready
allowed: V5-4A safety gate design ready for review
forbidden: Agent executor ready
```

## 4. V4 To V5 Boundary Guard

No False Green：V5 文档不得把以下 V4 evidence 改写为 production-ready：

```text
transcript_only evidence
report_only evidence
deterministic_devlocal evidence
dev/local provider-backed real_runtime evidence
V4 Agent Workflow Builder UX
V4 Runtime Capability Matrix
V4 WorkflowSpec Registry
```

## 5. Required V5 Evidence Fields

每个 V5 capability 必须记录：

```text
capability_id
owner_stage
status: inherited_from_v4_devlocal / planned / partial / not_implemented / production_blocker
evidence_ref
production_blocker
false_green_risk
claim_guard_notes
```

## 6. Acceptance

V5 claim guard passes when:

```text
all forbidden claims are guarded
no V4 evidence is upgraded to production-ready
all production blockers have owner stages
V5-0 remains planning-only
V5-3 core slice docs do not claim production audit export readiness
V5-4A to V5-8 docs do not overclaim implementation completion
V5-4A remains safety-gate only
V5-4B remains gated by V5-4A
V5-7A remains design-gate only
V5-7B may claim only limited staging runtime slice ready for review after focused validation; it must not claim production controlled executor ready
V5-6 keeps Full Studio behind separate PRD
V5-8 does not convert V4 dev/local multi-Agent evidence into production distributed runtime
ready for review is never shortened to ready
```
