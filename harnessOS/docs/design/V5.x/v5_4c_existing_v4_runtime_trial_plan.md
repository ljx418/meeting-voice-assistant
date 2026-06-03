# V5-4C Existing V4 Local Runtime Controlled Trial Plan

文档状态：V5-4C core slice implemented for review。本文承载从 V5-4B synthetic trial 进入 existing V4 local workflow runtime trial 的受控 dev/local 阶段规划与验收结果。

## Stage Goal

V5-4C 目标是在 dev/local 范围内，把 V5-4B controlled executor trial 从 synthetic in-memory state 扩展到现有 V4 local workflow runtime。

已审计入口：

```text
bff:/bff/v4_2/runtime
```

V5-4C 只允许通过该 BFF-only dev/local controlled runtime wrapper 进入现有 V4 local workflow path。不得直接写 WorkflowStore、WorkflowDraft、WorkflowVersion 或 StationRun。

Allowed claim, only after implementation and validation:

```text
V5-4C complete: existing V4 local workflow controlled trial ready for review.
```

## Scope

```text
user-confirmed workflow.instance.start against existing V4 local workflow path
user-confirmed station.rerun against existing V4 local workflow path
runtime evidence from actual V4 local workflow result
attempt history visible
artifact refs visible
quality refs visible
kill switch blocks before runtime call
```

## Strict Boundaries

```text
source=agent cannot execute mutation
user_confirmed=true required for every runtime action
no production executor service
no production connector.call
no production external_llm.call beyond existing approved provider boundary
no production auth
no production external app onboarding
no direct WorkflowStore write bypass
no direct WorkflowDraft / WorkflowVersion write bypass
```

## Required Evidence

```text
real V4 local workflow instance id
real runtime_result_ref
real station_run attempt refs
artifact refs
quality report refs
operation evidence
kill switch denial evidence
source=agent denial evidence
redaction scan
```

## Stop Conditions

```text
cannot identify safe existing V4 local runtime entrypoint
runtime action bypasses user_confirmed=true
source=agent can execute mutation
runtime writes bypass governed path
evidence cannot distinguish real_runtime_devlocal from production_ready
redaction fails
```

## Required Tests

```text
tests/test_v5_4c_v4_runtime_trial_start.py
tests/test_v5_4c_v4_runtime_trial_rerun.py
tests/test_v5_4c_v4_runtime_trial_evidence.py
tests/test_v5_4c_v4_runtime_trial_no_false_green.py
tests/test_v5_4c_v4_runtime_trial_evidence_package.py
```

## Evidence Package

```text
docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial/
  tui-transcript.txt
  runtime-start-result.json
  runtime-failed-result.json
  station-rerun-result.json
  continue-downstream-result.json
  source-agent-denial.json
  existing-runtime-evidence.json
  v5-4c-bridge-evidence.json
  runtime-report.html
  evidence-chain.html
  runtime-bridge.drawio
  result-summary.md
```

## No False Green

V5-4C may only prove an existing V4 local workflow controlled trial. It must not prove controlled executor ready, Agent executor ready, production controlled executor ready, autonomous workflow editing ready, production external app support, or distributed multi-Agent runtime ready.
