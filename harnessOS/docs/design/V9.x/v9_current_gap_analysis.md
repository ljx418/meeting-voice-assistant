# V9 Current Gap Analysis

文档状态：V9 gap analysis / planning baseline。

## 1. Current Baseline

```text
V8 complete: station-agent workflow pilot ready for review.
```

V8 已证明：

```text
每个 station 有 AgentDescriptor。
每个 Agent 有 role / goal / memory / tools / skills / MCP。
V8-4 real runtime fixture PASS。
V8-6 controlled terminal worker fixture PASS。
V8-7 bounded multi-Agent project workflow fixture PASS。
V8-8 read-only explainability TUI PASS。
V8-9 final framework PASS。
```

V8 未证明：

```text
Agent executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
```

## 2. Gap Table

| Area | Current V8 State | V9 Required State | Status | Owner Stage | Risk |
| --- | --- | --- | --- | --- | --- |
| Agent Executor | Agent can propose / handoff; direct durable mutation denied | policy-gated controlled Agent execution | planned | V9-1 / V9-2 | high |
| Multi-Agent Orchestration | bounded project workflow fixture | serial / parallel / fan-in/fan-out runtime with recovery | planned | V9-3 | high |
| Autonomous Coding | terminal handoff proposal only | controlled coding workflow with diff/test/review/fix loop | planned | V9-4 | high |
| Terminal Worker | readonly shell fixture | workspace write sandbox and command tiers | planned | V9-5 | high |
| Workflow Studio | thin console / report / TUI evidence | productized Studio via BFF/DTO | planned | V9-6 | medium |
| Production Governance / Automation | no production terminal/browser automation | production governance / evidence hardening and terminal automation gate | planned | V9-7 | critical |
| Final Acceptance | V8 final framework PASS | V9 evidence aggregation and claim guard | planned | V9-8 | high |

## 3. Gap Classification

```text
complete_for_v8: inherited evidence can be reused only as input.
planned: V9 design / implementation / evidence required.
high_risk: separate human proceed decision required.
critical: production or credential-related boundary.
out_of_scope: not part of default V9.
```

## 4. Current Blockers

```text
No AgentExecutionEnvelope schema accepted.
No controlled Agent executor runtime evidence.
No V9-1 contract package external audit acceptance.
No full orchestration recovery evidence.
No coding workflow sandbox and review loop evidence.
No terminal write sandbox evidence.
No complete Studio BFF/UI acceptance.
No production terminal automation high-risk gate evidence.
```

## 5. No False Green Notes

V9 gap 文档不得把 planned / ready for review 写成 ready：

```text
Agent executor ready
full multi-Agent orchestration ready
autonomous coding workflow ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
production ready
```
