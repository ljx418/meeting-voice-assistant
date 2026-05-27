# V4.7 Managed Session Status Development Plan

status: completed

date: 2026-05-27

## Scope

V4.7 adds sanitized managed session status for wrapper-launched Codex sessions:

```bash
petctl codex session status --json
```

## Allowed Fields

- `instanceId`
- redacted `bindingId`
- `mode`
- `monitor`
- `status`
- `lastEventKind`
- `lastSeenAt`

## Forbidden Fields

- raw TTY
- raw args
- window title
- path
- prompt
- tool command
- raw hook payload
- token
- Authorization

## Implementation

- Managed launch writes a local sanitized session status record.
- JSONL monitor updates status with structured event types only.
- Hook wrapper updates status with hook event names only.
- `petctl codex session status --json` returns the latest record or `unknown`.

## Drift And False-Green Risk

| Risk | Level | Mitigation |
| --- | --- | --- |
| Session status treated as lifecycle monitoring readiness | Low | Claim is diagnostics/status only. |
| Raw binding id exposed | Low | Output uses hashed binding summary. |
| Prompt/tool/path leakage | Low | Store and output contain only allowed fields. |

No High risk remains for V4.7.
