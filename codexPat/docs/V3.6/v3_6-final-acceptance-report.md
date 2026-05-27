# V3.6 Final Acceptance Report

status: historical blocked / deprecated active strategy

date: 2026-05-25

## Scope

V3.6 attempted selected real Codex workflow coverage expansion. The key no-false-green requirement was to prove that `PostToolUse failure -> error` is not overwritten by a later `Stop`.

Strategy update on 2026-05-26: V3.6 hook-only monitoring is no longer the active Codex monitoring strategy. It remains historical blocked evidence. V3.7 JSONL monitoring supersedes it for supported wrapper-launched `codex exec --json` sessions.

## Evidence Gate

Blocked:

- `docs/V3.6/evidence/codex-real-workflow-smoke-2026-05-25.md`

## Completed Work

- `Stop` handling was hardened so it is treated as a turn completion marker.
- fixture regression now verifies that `Stop after failure` keeps `error`.
- safe hook debug summaries can be enabled without printing raw payloads.

## Regression Results

| Command | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `node scripts/v3_1_runtime_smoke.mjs` | passed |
| `node scripts/v3_3_codex_window_binding_smoke.mjs` | passed |
| `node scripts/v3_4_codex_hook_fixture_smoke.mjs` | passed |

## Blocker

The tested local Codex `PostToolUse` hook payload for a failing shell command did not expose a stable failure field. It included only sanitized field categories equivalent to `cwd`, `hook_event_name`, `model`, `permission_mode`, `session_id`, and `tool_input`.

V3.x explicitly forbids parsing terminal text or using `transcript_path` as a stable interface. Therefore V3.6 cannot truthfully claim real failure workflow coverage.

## Additional Fix Attempt

An expanded resolution pass checked whether V3.6 could be unblocked through hook config/schema changes, Codex CLI flags, or structured `codex exec --json` monitoring.

Result: still blocked.

- No supported local hook configuration was found that exposes stable failure fields in real `PostToolUse` stdin.
- `codex exec --json` monitoring may be useful for a future project-owned wrapper, but it is outside the current V3.6 hook-only acceptance boundary.
- The existing hook wrapper remains future-compatible with stable failure fields if Codex exposes them later.

## Risk Assessment

| Risk | Level | Notes |
| --- | --- | --- |
| Development plan drift | Low | Work stayed within V3.6 hook coverage and Stop false-green hardening. |
| False-green acceptance | High | Claiming V3.6 passed would require treating fixture evidence or terminal output as real failure hook evidence. |
| Claim expansion | High | `selected workflow coverage passed` would overstate current real failure evidence. |
| Security redaction | Low | Debug captured only field names/status summaries and was removed. |
| Regression coverage | Low | V3.1, V3.3, V3.4 fixture, and petctl checks passed. |

overall risk: High

go / no-go: no-go

## Allowed Claim

No V3.6 pass claim is allowed.

Allowed historical / strategy claim:

```text
V3.6 final acceptance blocked on real PostToolUse failure evidence; V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

## Final Decision

V3.6 final acceptance is blocked and is now historical. Do not continue trying to pass V3.6 hook-only acceptance unless official Codex hook lifecycle payloads later expose stable failure fields and the acceptance plan is explicitly revived, revised, and audited.

Current recommended Codex exec monitoring path:

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```
