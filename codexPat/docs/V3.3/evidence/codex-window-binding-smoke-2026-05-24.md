# Codex Window/Session Binding Smoke Evidence

date: 2026-05-24

status: passed

commit: a09eaf3d

## Scope

This evidence covers V3.3 wrapper-first Codex window/session-to-pet binding for tested local macOS terminal scenarios.

It does not cover unqualified OS-level window binding, all Codex workflows, Claude Code, Windows, cross-platform, MCP ready, third-party product integration, production signing, or per-instance queue readiness.

## Command

```bash
node scripts/v3_3_codex_window_binding_smoke.mjs
```

The script was run with desktop app health available on localhost.

## Results

| Case | Result |
| --- | --- |
| desktop health | passed |
| rate limit window settled | passed |
| codex launch success exits 0 | passed |
| codex launch success has instance | passed |
| success launch final state is success | passed |
| codex launch failure exits nonzero | passed |
| codex launch failure has instance | passed |
| failure launch final state is error | passed |
| session B does not alter session A | passed |
| cleanup smoke instances | passed |
| security redaction scan | passed |

## Security Scan

The smoke summary did not include token, Authorization header, raw payload, config path, workspace path, full local path, raw tty path, or token file content.

## Allowed Claim

```text
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
```

## Forbidden Claims

The smoke does not allow:

```text
OS-level Codex window binding ready
all Codex workflows verified
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
production signed release ready
per-instance queue ready
```
