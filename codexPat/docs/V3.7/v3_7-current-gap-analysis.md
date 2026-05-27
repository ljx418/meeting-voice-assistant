# V3.7 Current Gap Analysis

status: passed

date: 2026-05-26

## Current State

V3.7 Codex Exec JSONL Monitor is implemented and accepted for tested local wrapper-launched `codex exec --json` scenarios. It is now the current recommended Codex exec monitoring strategy.

Implemented:

- `petctl codex launch --monitor jsonl`.
- wrapper-launched `codex exec --json` JSONL stdout monitoring.
- structured event type parsing only.
- target instance routing through existing PetEvent / HTTP / Event Bridge.
- smoke coverage for simple answer, tool success, and tool failure.

Evidence:

- `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-2026-05-25.md`
- `docs/V3.7/v3_7-final-acceptance-report.md`

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| JSONL monitor command | `--monitor jsonl` implemented on `petctl codex launch`. | Explicit wrapper-launched `codex exec --json` support. | closed |
| simple answer mapping | `turn.started` and `turn.completed` smoke passed. | `thinking -> success` for non-error turn completion. | closed |
| tool success mapping | `item.started` and `turn.completed` smoke passed. | `running -> success`. | closed |
| tool failure mapping | structured `turn.failed` smoke passed. | `error` from structured failure event. | closed |
| `thread.started` mapping | marker-only; no pet state is emitted. | No status mutation from session marker. | closed |
| V3.6 hook-only evidence | official `PostToolUse` failure payload still lacks stable failure fields. | Keep as historical blocked evidence; do not continue as active strategy. | historical blocked / deprecated |
| interactive Codex TUI | not covered. | Keep out of V3.7 scope. | not in scope |
| OS-level window binding | not covered. | Keep out of V3.7 scope. | not in scope |

## Known Naming Risk

`petctl codex launch --monitor jsonl --json` currently returns a sanitized monitor summary under `raw.monitor`.

This is not raw JSONL and does not contain raw payloads, prompt text, tool command text, token, Authorization, transcript path, full local paths, workspace path, config path, or `api-token.json`.

However, the field name `raw` can be confusing during audits. A future compatibility-reviewed cleanup may rename this to `monitorSummary`. V3.x Final records this as a naming risk, not a security leak.

## Claim Boundary

Allowed:

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

Still forbidden:

```text
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
OS-level Codex window binding ready
```
