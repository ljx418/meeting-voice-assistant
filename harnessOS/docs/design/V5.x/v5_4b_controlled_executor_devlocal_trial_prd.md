# V5-4B Controlled Executor Dev/Local Trial PRD

文档状态：V5-4B synthetic-only core slice implemented for review。本文只覆盖 synthetic in-memory controlled executor trial，不接入真实 V4 runtime。

## Stage Goal

V5-4B 规划并验证一个 synthetic in-memory dev/local controlled executor trial，用于验证 user-confirmed execution、approval-gated high-risk action、runtime evidence 和 kill switch。

## Entry Condition

```text
V5-4A safety gate passed
no Agent executor ready claim
policy matrix reviewed
sandbox boundary reviewed
```

## No False Green

No False Green：V5-4B 不证明 production controlled executor ready、Agent executor ready 或 autonomous workflow editing ready。

## Current Implementation Scope

```text
Implemented:
- synthetic in-memory workflow state
- user-confirmed synthetic workflow.instance.start
- user-confirmed synthetic station.rerun
- synthetic attempt history retention
- downstream stale marker
- synthetic runtime evidence with synthetic_only=true and runtime_backed=false
- source=agent mutation denial
- kill switch denial before synthetic state change

Not implemented:
- existing V4 local runtime integration
- production controlled executor
- Agent executor
- production connector.call
- production external_llm.call
```
