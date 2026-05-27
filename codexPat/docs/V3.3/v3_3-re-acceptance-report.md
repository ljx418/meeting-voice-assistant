# V3.3-Fix v1.1 Re-Acceptance Report

status: failed

date: 2026-05-23

commit: b304a1b0

## Scope

V3.3-Fix v1.1 investigated why V3.3 did not produce real Claude Code `Notification -> need_input` evidence.

No MCP feature, third-party product integration, Windows readiness, production release, OS-level Codex window binding, or per-instance queue work was added.

## Root Cause Result

Result: failed, with narrowed blocker.

Findings:

- Claude Code version: `2.1.114 (Claude Code)`.
- Temporary `--settings` hook configuration loads successfully.
- `SessionStart` hook marker was observed, proving settings loading is not the blocker.
- `permission_prompt` Notification matrix scenario ran with real Claude Code but did not emit Notification, did not execute hook marker, and did not create accepted `need_input`.
- A follow-up no-matcher probe removed `matcher` from the Notification config; Bash, Write, and manual idle variants still did not emit Notification.
- V3.3 hook smoke still failed because `Notification` was not observed and default pet remained `idle`.

Evidence:

- `docs/V3.3/evidence/claude-code-hook-config-load-2026-05-23.md`
- `docs/V3.3/evidence/claude-code-notification-trigger-matrix-2026-05-23.md`
- `docs/V3.3/evidence/claude-code-notification-nomatcher-probe-2026-05-24.md`
- `docs/V3.3/evidence/claude-code-hook-notification-smoke-2026-05-23.md`

## Re-Acceptance Smoke

| Gate | Command | Result |
| --- | --- | --- |
| V3.3 Claude hook smoke | `node scripts/v3_3_claude_code_hook_smoke.mjs` | failed |
| V3.1 runtime smoke | `node scripts/v3_1_runtime_smoke.mjs` | passed |
| V3.2 MCP adapter smoke | `node scripts/v3_2_mcp_adapter_smoke.mjs` | passed |
| V3.2 third-party contract smoke | `node scripts/v3_2_third_party_contract_smoke.mjs` | passed |

V3.3 hook smoke failed on:

- `Notification` hook event not observed.
- accepted Claude `need_input` event not found.
- target default pet state remained `idle`.

## Automatic Checks

| Command | Result |
| --- | --- |
| `pnpm run doctor` | passed with warnings only |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp test` | passed |
| `pnpm --filter desktop check` | passed |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | passed |
| `pnpm --filter desktop build` | passed |
| `pnpm --filter desktop tauri build -b app` | passed |

Doctor warnings were environmental network/listen warnings, not hard failures.

## Security Scan

Result: passed for V3.3-Fix evidence and report content.

No evidence file or final report includes token values, auth header values, raw event body, config location, workspace location, complete local path, unsafe sound value, or token file content.

Implementation scripts contain forbidden-pattern literals only as scan patterns or local token-resolution code; these are not evidence output.

## Claim Scan

Result: passed.

Forbidden claims appear only in forbidden, non-goal, or not-ready contexts.

## Git Artifact Check

`git status --short` was run.

Generated `dist/`, `target/`, and `node_modules/` artifacts are not listed as files to commit.

The worktree contains unrelated dirty files outside this V3.3-Fix scope; they were not changed or reverted.

## Allowed Claim

No V3.3 pass claim is allowed.

The scoped claim remains gated and must not be used:

```text
V3.3 Claude Code hook Notification -> need_input smoke passed for tested local Claude Code hook scenario.
```

## Forbidden Claims

The following claims remain forbidden:

```text
Claude Code integration verified
Claude Code all workflows verified
MCP ready
Third-party agent integration verified
all Codex workflows verified
Windows ready
cross-platform ready
USB ready
production signed release ready
OS-level Codex window binding ready
per-instance queue ready
```

## Final Decision

V3.3-Fix v1.1 re-acceptance failed.

Reason: Claude Code hook settings load successfully, but no tested real Claude Code Notification matcher produced an accepted `Notification -> need_input` event.

Additional team probe on 2026-05-24 closed the matcher-syntax hypothesis: omitting `matcher` still did not produce Notification.

The next development step should not expand integration scope. It should either obtain a real, documented Claude Code scenario that emits `Notification`, or record the local Claude Code 2.1.114 Notification behavior as an external blocker.
