# V7-2 Explainable Mission TUI PRD

文档状态：V7 planning package / V7-2 detailed PRD。

## Goal

V7-2 将当前 CLI / `--oh` TUI / Mission Console 规划收敛成真实 `harness tui`。

TUI 的核心不是聊天窗口，而是可解释工作流驾驶舱：

```text
自然语言输入
状态线
可用动作
禁止原因
Workflow Blueprint
Runtime Report
Review Console
Evidence Chain
```

## Main Screen

```text
Left: mission input and transcript
Center: state timeline and workflow blueprint summary
Right: available actions, forbidden reasons, evidence links
Bottom: runtime report and quality summary
```

## Required State Line

```text
IntentCaptured
SpecDrafted
SchemaValidated
DiffReady
AwaitingConfirmation
UserConfirmed
RuntimeStarted
EvidenceRecorded
```

## Required Explainability

For every suggested action, TUI must show:

```text
operation
source
actor_type
requires_user_confirmation
policy_decision
capability_decision
risk_flags
target_refs
forbidden_reason when denied
evidence_refs
```

## UX Boundaries

```text
TUI cannot execute durable mutation before user confirmation.
TUI cannot let source=agent directly mutate runtime.
TUI cannot hide policy denial.
TUI cannot present transcript-only actions as runtime-backed.
TUI cannot claim complete Workflow Studio.
```

## Allowed Claim

```text
V7-2 complete: explainable Mission TUI pilot ready for review.
```

