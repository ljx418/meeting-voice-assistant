# V7-4 Final Small Studio Acceptance Plan

文档状态：V7 planning package / V7-4 final acceptance framework only。

V7-4 不得在 V7-0 到 V7-3 evidence package 缺失时执行。
V7-4 不得在 V7-3 缺少 real_runtime / real_runtime_fixture PASS 证据时声明 V7 complete。

Final acceptance data contract:

```text
docs/design/V7.x/v7_4_final_acceptance_data_contract.md
```

## Goal

V7-4 汇总 V7-0 到 V7-3 证据，生成小型工作室最终验收看板。

## Required Final Evidence

```text
V7-0 planning package
V7-1 small studio evidence
V7-2 TUI evidence
V7-3 workflow run evidence
V7-4 final acceptance data contract
V7 drawio XML validation
No False Green scan
redaction scan
human acceptance summary
```

## Final Dashboard

```text
docs/design/V7.x/evidence/final-acceptance/index.html
```

The dashboard must show:

```text
stage status table
studio inventory
workflow inventory
run inventory
artifact inventory
quality report
evidence chain
audit export refs
TUI transcript links
Drawio blueprint links
claim scan result
redaction scan result
runtime truth assertions
```

## Pass Conditions

```text
V7-0 to V7-3 evidence exists.
V7-3 evidence_scope is real_runtime or real_runtime_fixture.
V7-3 scanner_actual_read_count > 0.
V7-3 provider_invocation_count > 0.
No FAIL / BLOCKED.
PARTIAL has human proceed decision.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
User can understand how to create, run, inspect and review a workflow.
```

## Allowed Claim

```text
V7 complete: small studio production pilot and explainable TUI baseline ready for review.
```

该声明只有在 V7-3 status=PASS 且 evidence_scope=real_runtime / real_runtime_fixture 时允许。fallback_demo_only、transcript_only、report_only 或 BLOCKED 只能生成 PARTIAL review package，不得声明 V7 complete。

## Forbidden Claims

```text
production ready
full production GA
complete Workflow Studio ready
Agent executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```
