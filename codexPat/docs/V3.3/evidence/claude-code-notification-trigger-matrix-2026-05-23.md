# Claude Code Notification Trigger Matrix Evidence

status: failed

date: 2026-05-23

## Scope

Test whether real Claude Code `Notification` matchers can trigger the existing Claude pet hook and produce accepted `need_input` evidence.

This evidence does not use curl mock, ordinary shell `petctl`, manual `petctl notify`, or direct hook wrapper execution as acceptance.

## Command

```bash
node scripts/v3_3_claude_notification_trigger_matrix.mjs
```

## Result Summary

| Check | Result | Notes |
| --- | --- | --- |
| desktop health | passed | local bridge health ok |
| Claude Code version | passed | `2.1.114 (Claude Code)` |
| permission prompt scenario completed | passed | Claude process status `0` |
| permission prompt Notification observed | failed | Notification not observed |
| permission prompt hook marker | failed | marker missing |
| permission prompt accepted need_input | failed | accepted event missing |
| permission prompt target state | failed | default state remained `idle` |
| security redaction scan | passed | summary did not contain sensitive text |

## Scenario Results

| Scenario | Matcher | Result | Notes |
| --- | --- | --- | --- |
| permission prompt | `permission_prompt` | failed | Claude Code completed without Notification hook marker or accepted `need_input` |
| idle prompt | `idle_prompt` | not-run | requires tty; prior manual V3.3 idle probe did not emit Notification |
| elicitation dialog | `elicitation_dialog` | not-run | no safe local MCP elicitation scenario configured |
| auth success | `auth_success` | not-run | auth flow not rerun to avoid credential exposure or mutation |

## Decision

No tested Notification trigger produced:

```text
sourceId=claude-code.local
level=need_input
```

The V3.3 pass claim remains not allowed.
