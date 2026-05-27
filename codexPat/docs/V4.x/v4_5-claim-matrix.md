# V4.5 Claim Matrix

status: passed-scoped

date: 2026-05-27

## Allowed Claims

After automated preflight only:

```text
V4.5 managed Codex TUI wrapper preflight passed; real hook lifecycle acceptance remains pending.
```

After real hook lifecycle acceptance:

```text
V4.5 managed Codex TUI hook state mapping passed for tested local wrapper-launched scenario.
```

If `PermissionRequest` is not emitted locally:

```text
V4.5 managed Codex TUI hook state mapping passed for UserPromptSubmit, PreToolUse, and Stop in tested local wrapper-launched scenario; PermissionRequest remains blocked by local policy.
```

## Forbidden Claims

```text
V4.5 managed Codex TUI hook state mapping passed for PermissionRequest
V4.5 managed Codex TUI lifecycle acceptance passed for all hook events
interactive Codex TUI monitoring ready
already-open Codex window auto-monitoring ready
OS-level Codex window binding ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
PostToolUse failure hook evidence passed
```
