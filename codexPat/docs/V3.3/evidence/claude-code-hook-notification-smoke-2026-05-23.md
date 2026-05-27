# Claude Code Hook Notification Smoke Evidence

status: failed

date: 2026-05-23

## Scope

Validate real Claude Code `Notification -> need_input` hook lifecycle for the tested local scenario.

This evidence does not use curl mock, ordinary shell `petctl`, manual `petctl notify`, or template-only review as acceptance.

## Required Evidence

| Item | Required |
| --- | --- |
| Claude Code version | `2.1.114 (Claude Code)` |
| hook config load method | temporary settings file for non-interactive run; local hook settings example for interactive probes |
| hook event | `Notification` |
| hook command | redacted |
| source id | `claude-code.local` |
| source kind | `claude_code` |
| source name | `Claude Code` |
| target route | default |
| diagnostics accepted | required but not observed |
| target pet state | required `need_input`, observed `idle` |
| security scan | passed for emitted smoke summary |

## Result

failed

## Smoke Runs

### Non-interactive Claude Code Hook Smoke

Command:

```bash
node scripts/v3_3_claude_code_hook_smoke.mjs
```

Result summary:

| Check | Result | Notes |
| --- | --- | --- |
| desktop health | passed | local bridge health ok |
| Claude Code version | passed | `2.1.114 (Claude Code)` |
| Claude Code process completed | passed | status `0` |
| Claude execution classification | passed | `completed` |
| Claude hook lifecycle event observed | failed | `Notification` hook event not observed |
| hook command redacted | passed | command recorded only as redacted summary |
| accepted Claude need_input event | failed | accepted event not found |
| target pet state entered need_input | failed | default state remained `idle` |
| invalid sound/path rejected | passed | rejected with safe reason code |
| invalid sound/path redacted | passed | unsafe input not echoed |
| security redaction scan | passed | emitted summary did not contain sensitive text |

### Interactive Permission Probe

Real interactive Claude Code session was launched with the hook settings example and a harmless Bash request.

Observed result:

- Claude Code executed the Bash command directly.
- No permission prompt Notification was observed.
- The default pet remained `idle`.

### Interactive Idle Probe

Real interactive Claude Code session was launched with the hook settings example and left idle for longer than 60 seconds.

Observed result:

- No idle Notification was observed.
- The default pet remained `idle`.

## Diagnostics Decision

No new diagnostics accepted event proving `sourceId=claude-code.local` and `level=need_input` was observed from a real Claude Code `Notification` hook lifecycle.

## Regression Impact

The failed V3.3 hook evidence did not break the previously accepted integration layer:

| Regression | Result |
| --- | --- |
| V3.1 runtime smoke rerun | passed |
| V3.2 MCP adapter smoke rerun | passed |
| V3.2 third-party contract smoke rerun | passed |

## Final Evidence Decision

V3.3 hook evidence is failed because the real Claude Code hook scenario ran but did not produce an accepted `need_input` event.

No V3.3 Claude Code hook pass claim is allowed from this evidence.
