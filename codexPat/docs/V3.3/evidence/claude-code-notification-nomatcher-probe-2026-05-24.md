# Claude Code Notification No-Matcher Probe Evidence

status: failed

date: 2026-05-24

## Scope

Test whether omitting the `matcher` field from a Claude Code `Notification` hook fixes the prior false-negative risk in the V3.3-Fix trigger matrix.

This evidence uses real Claude Code runs. It does not use curl mock, ordinary shell `petctl`, manual `petctl notify`, or direct wrapper execution as acceptance.

## Change Under Test

The local hook example and main V3.3 smoke were changed so `Notification` hook config omits `matcher` instead of setting it to an empty string.

Relevant files:

- `skills/claude-agent-pet/settings-hooks.example.json`
- `scripts/v3_3_claude_code_hook_smoke.mjs`
- `scripts/v3_3_claude_notification_nomatcher_probe.mjs`

## Probe Command

```bash
node scripts/v3_3_claude_notification_nomatcher_probe.mjs
```

## Result Summary

| Check | Result | Notes |
| --- | --- | --- |
| Claude Code version | passed | `2.1.114 (Claude Code)` |
| no-matcher Bash process | passed | status `0` |
| no-matcher Bash Notification | failed | Notification not observed |
| no-matcher Bash hook marker | failed | marker missing |
| no-matcher Write process | passed | status `0` |
| no-matcher Write Notification | failed | Notification not observed |
| no-matcher Write hook marker | failed | marker missing |
| security redaction scan | passed | summary did not contain sensitive text |

## Main Smoke Rerun

Command:

```bash
node scripts/v3_3_claude_code_hook_smoke.mjs
```

Result: failed.

The main smoke still did not observe a `Notification` hook event, did not find accepted Claude `need_input`, and observed default pet state `idle`.

## Decision

Omitting `matcher` removes one possible false-negative source, but it does not solve the V3.3 acceptance failure in this local Claude Code 2.1.114 scenario.

The V3.3 pass claim remains not allowed.
