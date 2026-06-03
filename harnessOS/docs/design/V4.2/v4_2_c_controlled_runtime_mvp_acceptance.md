# V4.2-C Controlled Runtime MVP Acceptance / 验收标准

Status: complete.

## Real Data Scenarios

```text
Scenario A: tests/fixtures/desktop/技术分享
Scenario B: tests/fixtures/desktop/技术分享_损坏
```

Scenario A validates user-confirmed workflow start and artifact generation.

Scenario B validates failed Markdown parse, user-confirmed rerun, attempt history, stale downstream state, user-confirmed continuation, and recovery.

## Required Evidence

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

## PASS Criteria

1. Start request contains `user_confirmed=true`.
2. Start request with `source=agent` is rejected.
3. Rerun request contains `user_confirmed=true`.
4. Rerun request with `source=agent` is rejected.
5. Rerun creates a new attempt.
6. Previous failed attempt and error remain visible.
7. Downstream stations are marked stale.
8. Continue downstream requires user confirmation.
9. Runtime evidence includes real `runtime_result_ref`.
10. Evidence includes timeout and kill switch baseline.
11. Reports are read-only.
12. Browser client uses `/bff/v4_2/runtime/*`.
13. No direct browser `/v1/rpc`.
14. No direct browser `/v1/events/subscribe`.
15. No token, secret, raw payload, raw prompt, or signed URL leak.

If any item fails, V4.2-C must return to planning and cannot be declared complete.
