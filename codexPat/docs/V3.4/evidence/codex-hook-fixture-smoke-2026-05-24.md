# Codex Hook Fixture Smoke Evidence

date: 2026-05-24

status: passed

## Command

```bash
node scripts/v3_4_codex_hook_fixture_smoke.mjs
```

## Expected Coverage

| Case | Result |
| --- | --- |
| desktop health | passed |
| attach hook fixture instance | passed |
| `SessionStart -> running` | passed |
| `UserPromptSubmit -> thinking` | passed |
| `PreToolUse -> running` | passed |
| duplicate `PreToolUse` cooldown no-op | passed |
| `PermissionRequest -> need_input` | passed |
| `PostToolUse failure -> error` | passed |
| `Stop -> success` | passed |
| missing instance no-op | passed |
| cleanup fixture instance | passed |
| security redaction scan | passed |

## Smoke Summary

The fixture smoke used a temporary Codex instance and invoked `scripts/codex-pet-hook.mjs` with redacted fixture JSON. It verified target instance state after each mapped hook event.

The hook wrapper emitted only `{}` to stdout in fixture cases.

No token, Authorization header, raw hook stdin, prompt text, tool input command, transcript path, config path, workspace path, or full local path was included in the smoke summary.

## Claim Boundary

This evidence can only allow:

```text
V3.4 Codex hook wrapper fixture smoke passed.
```

It cannot allow real Codex lifecycle claims.
