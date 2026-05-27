# V3.7 Claim Matrix

status: passed

date: 2026-05-25

## Allowed Claim

Allowed after final acceptance:

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```

This is also the current recommended Codex exec monitoring strategy for supported wrapper-launched `codex exec --json` sessions.

## Historical V3.6 Claim

V3.6 remains historical blocked evidence:

```text
V3.6 final acceptance blocked on real PostToolUse failure evidence.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

## Forbidden Claims

```text
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```

## Claim Boundary

The JSONL monitor claim applies only to wrapper-launched `codex exec --json` sessions started through `petctl codex launch --monitor jsonl`.

It does not apply to:

- interactive Codex TUI sessions.
- arbitrary already-running Codex terminals.
- Codex official lifecycle hooks.
- OS-level window discovery.
- non-Codex third-party agents.
