# V3.x Claim Matrix

status: passed

date: 2026-05-26

## Allowed Claims

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
V3.2 third-party contract v3 smoke passed.
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
V3.4 Codex hook wrapper fixture smoke passed.
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.
V3.6 final acceptance blocked on real PostToolUse failure evidence.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
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

## Boundary Rules

- V3.6 hook-only monitoring remains historical blocked evidence and is deprecated as the active strategy.
- V3.7 JSONL monitor is the current recommended Codex exec monitoring path for wrapper-launched `codex exec --json`.
- V3.7 JSONL monitor is a project-owned structured source, not official hook lifecycle evidence.
- V3.7 does not convert V3.6 to passed.
- V3.7 does not cover interactive Codex TUI or OS-level window discovery.
- MCP and third-party claims remain smoke/contract scoped.
- Claude Code remains not verified.
- macOS local app build does not imply production signed release.
