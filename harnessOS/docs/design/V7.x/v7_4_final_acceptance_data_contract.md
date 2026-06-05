# V7-4 Final Acceptance Data Contract

文档状态：V7-4 final acceptance contract / framework only。本文定义 V7 最终验收数据合同。V7-4 不得在 V7-3 evidence package 缺失时执行。

## 1. Purpose

V7-4 汇总 V7-0 到 V7-3 证据，生成最终 HTML 验收看板和 `acceptance-data.json`，证明用户可以理解如何创建、运行、查看和复核工作流。

## 2. Entry Gate

V7-4 can generate a PARTIAL review package if limited scope evidence has explicit human proceed decision. V7-4 can make the final allowed V7 complete claim only if V7-3 has real runtime evidence.

V7-4 can run only if:

```text
V7-0 evidence package exists.
V7-1 evidence package exists.
V7-2 evidence package exists.
V7-3 evidence package exists.
V7-3 evidence package exists.
No FAIL / BLOCKED without human proceed decision.
No False Green scan procedure exists.
Redaction scan procedure exists.
V7 drawio XML validates.
```

## 3. Final Acceptance Data Fields

`docs/design/V7.x/evidence/final-acceptance/acceptance-data.json` must include:

```text
stage_id=V7-4
status=PASS | PARTIAL | FAIL | BLOCKED
v7_allowed_claim
stage_results
ux_summary
prd_main_path_result
architecture_target_result
runtime_truth_assertions
claim_scan
redaction_scan
drawio_xml_validation
evidence_inventory
missing_evidence
human_acceptance_summary
next_stage_recommendation
```

`stage_results` must include:

```text
V7-0 status and evidence_scope
V7-1 status and evidence_scope
V7-2 status and evidence_scope
V7-3 status and evidence_scope
```

## 4. Final HTML Dashboard

`docs/design/V7.x/evidence/final-acceptance/index.html` must show:

```text
V7 stage status table
Small Studio inventory summary
Mission TUI transcript link
WorkflowSpec / Diff / Blueprint links
Runtime Report link
Artifact and Quality report links
Evidence Chain link
No False Green scan result
Redaction scan result
Runtime truth assertions
Forbidden claims section
Human acceptance summary
```

HTML restrictions:

```text
read-only dashboard
no hidden mutation form
no Apply / Publish / Execute / Run button
no browser direct /v1/rpc
no browser direct /v1/events/subscribe
no raw prompt / raw file content / token / secret
```

## 5. PASS Conditions

```text
V7-0 to V7-3 evidence exists.
V7-3 status=PASS.
V7-3 evidence_scope=real_runtime or real_runtime_fixture.
V7-3 scanner_actual_read_count > 0.
V7-3 provider_invocation_count > 0.
User can trace natural language goal -> WorkflowSpec -> Blueprint -> user confirmation -> runtime report -> evidence chain.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML PASS.
No forbidden completion claim outside forbidden/no-false-green context.
```

PARTIAL review package allowed:

```text
V7-3 limited scope evidence exists.
Human proceed decision is recorded.
V7 complete final claim is not emitted.
Dashboard clearly marks V7-4 as PARTIAL and blocks final completion.
```

## 6. Stop Conditions

```text
V7-4 starts before V7-3 evidence exists.
V7-3 fallback_demo_only is counted as final runtime PASS.
V7-3 transcript_only or report_only is counted as final runtime PASS.
V7 complete final claim is emitted without V7-3 PASS real_runtime evidence.
V7 complete is summarized as production ready.
Complete Workflow Studio or Agent executor is claimed.
Evidence dashboard exposes raw secret, raw prompt or raw file content.
Runtime Report / Evidence Chain constructs runtime truth.
```

## 7. Allowed Final Claim

This final claim is allowed only if V7-3 has:

```text
status=PASS
evidence_scope=real_runtime or real_runtime_fixture
scanner_actual_read_count > 0
provider_invocation_count > 0
runtime_backed=true
fallback_demo_only=false
transcript_only=false
report_only=false
```

```text
V7 complete: small studio production pilot and explainable TUI baseline ready for review.
```

This does not prove:

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
