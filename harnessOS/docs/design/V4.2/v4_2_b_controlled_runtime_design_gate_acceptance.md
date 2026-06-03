# V4.2-B Controlled Runtime Design Gate Acceptance

Status: complete.

## 1. Acceptance Purpose

This document defines the acceptance standard that V4.2-C must satisfy before it can claim a controlled runtime MVP. V4.2-B itself is only a design gate and must not claim runtime implementation.

## 2. Required V4.2-C Real Data Scenario

V4.2-C must validate against real dev/local workflow data:

```text
Scenario A: tests/fixtures/desktop/技术分享
Scenario B: tests/fixtures/desktop/技术分享_损坏
```

Scenario A validates generic user-confirmed workflow start.

Scenario B validates generic station rerun, attempt history, error preservation, and downstream stale recovery.

V4.2-C acceptance cannot pass on static reports alone.

## 3. V4.2-C PASS Criteria

V4.2-C cannot pass unless all criteria below are true:

1. `harness workflow run` or equivalent BFF-backed command creates a real WorkflowInstance from runtime truth.
2. Workflow start requires `user_confirmed=true`.
3. `source=agent` workflow start is rejected.
4. `harness station rerun` or equivalent BFF-backed command creates a new StationRun attempt.
5. Station rerun requires `user_confirmed=true`.
6. `source=agent` station rerun is rejected.
7. Previous attempts and previous errors remain visible after rerun.
8. Downstream stations are marked stale after upstream rerun.
9. Downstream continuation requires user confirmation and refreshes from runtime truth.
10. Artifact reads and writes stay inside the approved dev/local sandbox.
11. Runtime evidence is generated from real operation results.
12. Timeout baseline and kill switch baseline are visible in operation evidence.
13. Drawio and HTML reports are regenerated from runtime truth after run/rerun.
14. Browser does not directly call `/v1/rpc` or `/v1/events/subscribe`.
15. No token, secret, raw payload, raw prompt, or signed URL appears in DTOs, reports, DOM, logs, or evidence.
16. No false-green claim appears in docs, UI copy, reports, or completion note.

## 4. Required V4.2-C Evidence Package

V4.2-C must generate:

```text
docs/design/V4.2/evidence/controlled-runtime/
  tui-transcript.txt
  workflow.yaml
  runtime-start-result.json
  station-rerun-result.json
  attempt-history.json
  downstream-stale.json
  runtime-evidence.json
  workflow_status.drawio
  rerun_history.drawio
  runtime_report.html
  evidence.html
  result-summary.md
```

The evidence package must mark whether each operation is:

```text
user_confirmed=true
source!=agent
backed_by=generic_controlled_runtime
```

## 5. Fail And Replan Rules

If any V4.2-C acceptance item fails:

1. Do not downgrade it to PARTIAL.
2. Do not declare V4.2 complete.
3. Return to V4.2-C planning.
4. Update the audit document with the failure root cause.
5. Re-run implementation only after the plan is corrected.

If Spec Drift Risk or False Green Risk becomes HIGH, stop and request user decision.
