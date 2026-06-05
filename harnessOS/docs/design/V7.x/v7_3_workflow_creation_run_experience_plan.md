# V7-3 Workflow Creation And Run Experience Plan

文档状态：V7-3 next implementation candidate / pre-implementation review required。

## Dependency Gate

V7-3 不能提前实现 natural-language -> run 链路。进入 V7-3 前必须满足：

```text
V7-1 accepted
V7-2 accepted
V7-1 evidence package exists
V7-2 evidence package exists
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain link contract accepted
Evidence package data schema accepted
Real-data acceptance plan accepted
Schema manifest and examples accepted
Provider-backed evidence policy accepted
No False Green scan procedure accepted
Redaction scan procedure accepted
External audit accepted
```

V7-3 必须保持：

```text
Do not write transcript-only or report-only evidence as real runtime.
Do not bypass user confirmation.
Do not allow source=agent direct durable mutation.
```

## Goal

V7-3 打通主体验链路：

```text
natural language goal
 -> WorkflowSpec / Diff
 -> Workflow Blueprint
 -> user confirmation
 -> controlled run
 -> Runtime Report
 -> Review Console
 -> Evidence Chain
```

## Minimum Real Scenario

```text
用户输入：递归总结 Desktop/技术分享 下的 Markdown 技术文档。
系统读取 Desktop/技术分享 或 tests/fixtures/desktop/技术分享。
Markdown scanner 实际读取文件。
MiniMax 或 OpenAI-compatible provider 被调用。
每个子文件夹生成 summary。
生成 overview summary。
生成 quality_report.json。
TUI 展示状态线和 evidence links。
```

## Implementation Boundaries

```text
WorkflowSpec is not runtime truth.
Blueprint is read-only.
Runtime Report is read-only.
Evidence Chain is read-only.
User confirmation required before run.
source=agent direct mutation denied.
```

## Contract References

```text
docs/design/V7.x/v7_3_pre_implementation_review.md
docs/design/V7.x/v7_3_io_contracts_and_schemas.md
docs/design/V7.x/v7_3_real_data_acceptance_plan.md
docs/design/V7.x/v7_3_schema_manifest_and_examples.md
```

## Development Slices

```text
V7-3-PR1 Mission TUI runtime bridge
V7-3-PR2 WorkflowSpec / Diff / Blueprint
V7-3-PR3 Controlled run handoff
V7-3-PR4 Reports and Evidence
V7-3-PR5 Acceptance package
```

## Acceptance Tests

```text
natural_language_goal_generates_workflow_spec
workflow_spec_schema_valid
workflow_diff_ready_before_confirmation
blueprint_link_generated
user_confirmation_required_before_run
local_markdown_scanner_actual_read_count_gt_zero
provider_invocation_count_gt_zero
folder_summaries_generated
overview_summary_generated
quality_report_generated
evidence_chain_redacted
```

## Evidence Scope Rules

```text
real_runtime: scanner_actual_read_count > 0 and provider_invocation_count > 0.
fallback_demo_only: provider key missing or provider unavailable; cannot pass V7-3 runtime-backed acceptance.
transcript_only: TUI-only state line; cannot be claimed as controlled run.
report_only: static report exists; cannot be claimed as execution.
blocked: local path authorization, provider config or runtime handoff evidence missing.
```

V7-3 只有在 `real_runtime` 证据成立时才能声明完成。否则必须回到计划或标记 BLOCKED / PARTIAL，并停止进入 V7-4。

## Evidence Package

```text
docs/design/V7.x/evidence/v7-3-workflow-run/
  index.html
  tui-transcript.txt
  workflow.json
  workflow.yaml
  workflow.drawio
  workflow_status.drawio
  workflow_board.html
  artifacts.html
  quality.html
  evidence.html
  local-document-workflow-result.json
  evidence_chain.json
  quality_report.json
  result-summary.md
```

## Allowed Claim

```text
V7-3 complete: natural-language workflow creation and controlled run experience ready for review.
```
