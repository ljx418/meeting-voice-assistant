# V3.3-Fix Notification Trigger Matrix

文档状态：completed；no passing Notification trigger found.

## Baseline

Config loading is proven by `docs/V3.3/evidence/claude-code-hook-config-load-2026-05-23.md`.

Therefore this matrix treats hook settings loading as passed and focuses on whether Claude Code emits a real `Notification` matcher that can drive `Notification -> need_input`.

## Matrix

| Scenario | Matcher | Run Status | Notification Observed | Hook Marker | Accepted `need_input` | Target State | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Permission prompt | `permission_prompt` | ran | no | missing | no | `idle` | failed |
| No-matcher Bash | omitted | ran | no | missing | no | not read | failed |
| No-matcher Write | omitted | ran | no | missing | no | not read | failed |
| No-matcher idle | omitted | ran manually | no | missing | no | `idle` | failed |
| Idle prompt | `idle_prompt` | not run by automation | no | not run | no | not read | not accepted |
| Elicitation dialog | `elicitation_dialog` | not run | no | not run | no | not read | not accepted |
| Auth success | `auth_success` | not run | no | not run | no | not read | not accepted |

## Notes

- The permission prompt scenario used real Claude Code with a temporary `Notification.permission_prompt` hook.
- The hook would have written a non-sensitive marker and then called the existing Claude pet notification wrapper only if Claude Code emitted the Notification hook.
- The marker was missing, proving the Notification hook command did not run in that scenario.
- A follow-up no-matcher probe removed `matcher` entirely from the `Notification` config. Bash, Write, and manual idle variants still did not execute the hook marker.
- The idle prompt scenario still requires a real tty session. Prior V3.3 manual interactive idle probing did not emit Notification.
- `auth_success` is not rerun because the test must not alter or expose credentials.
- `elicitation_dialog` is not run because this repo has no safe local MCP elicitation scenario configured.

## Next-Phase Audit

Phase 4 must not implement a workaround that directly executes the wrapper.

Because config loading passed and Notification did not emit even after removing `matcher`, the correct Phase 4 path remains failed/blocker declaration plus re-acceptance report. No V3.3 pass claim is allowed.
