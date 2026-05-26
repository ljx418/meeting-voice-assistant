# V4.x Claim Matrix

status: v4-1-terminal-app-passed-v4-2-planned

date: 2026-05-26

## Current Baseline Claims

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
V4.1 macOS active window safe-field probe completed for Terminal.app on tested local environment.
V3.7 remains the default reliable path for wrapper-launched codex exec --json monitoring.
```

## Allowed Scoped Claims

V4.0, only after feasibility acceptance:

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
```

V4.1, only after safe-field probe evidence:

```text
V4.1 macOS active window safe-field probe completed for <terminal app> on tested local environment.
```

V4.2, only after preview / confirm binding evidence:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

V4.3, only after manual route-test evidence:

```text
V4.3 user-confirmed Terminal.app binding manual route-test prototype passed for tested local environment.
```

V4.x Final, only after V4.0-V4.3 evidence closure:

```text
V4.x Terminal.app scoped Codex candidate discovery, user-confirmed PetInstance binding, and explicit route-test prototype passed for tested local environment.
```

## Forbidden Claims

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
state lifecycle routing ready
lifecycle event routing from OS discovery
all terminal apps supported
iTerm2 support passed
VS Code support passed
Warp support passed
Ghostty support passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
MCP ready
Windows ready
cross-platform ready
production signed release ready
```

## Boundary Rules

- OS-level discovery can only establish candidate window/session identity and possible binding context.
- OS-level discovery does not automatically provide Codex lifecycle state events.
- V4.2 binding must require preview / confirm or an equivalent explicit confirmation gate; silent binding is forbidden.
- V4.2 must include stale / TTL fields and must not send PetEvent.
- V4.3 route-test is manual/test-only and must not be described as lifecycle routing.
- V4.3 must revalidate binding before routing and must never fall back to default.
- V4.0 must answer where state events come from and how they can be proven to belong to a bound session.
- V4.x must not parse terminal text or screen contents as state evidence.
- V4.x must not use `transcript_path` as a stable routing or monitoring interface.
- V4.x must not record prompt text, command text, shell history, clipboard contents, workspace path, full local paths, token, Authorization, raw payload, config path, or `api-token.json`.
- If `AGENT_DESKTOP_PET_INSTANCE_ID` cannot be injected into an already-running session, V4.x must consider prompting the user to relaunch through the wrapper path.
- V3.7 wrapper-launched JSONL monitoring remains the default reliable path but is not OS-level evidence.
