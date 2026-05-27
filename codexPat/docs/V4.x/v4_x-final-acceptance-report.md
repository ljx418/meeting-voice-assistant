# V4.x Final Acceptance Report

status: passed

date: 2026-05-27

## Scope

V4.x Final closes the scoped Codex session-to-PetInstance work completed in V4.0-V4.7.

This final closure covers:

- Terminal.app candidate discovery feasibility and safe-field probe.
- User-confirmed Terminal.app candidate-to-PetInstance binding.
- Explicit manual route-test for a confirmed binding.
- Managed wrapper-launched `codex exec --json` JSONL state mapping.
- Managed wrapper-launched Codex TUI hook mapping for observed hook events.
- Managed session startup diagnostics.
- Sanitized managed session status.

V4.x Final does not add features.

## Evidence

| Phase | Result | Evidence |
| --- | --- | --- |
| V4.0 feasibility | passed | `docs/V4.x/v4_0-os-binding-feasibility-review.md` |
| V4.1 Terminal.app safe-field probe | passed | `docs/V4.x/v4_1-final-acceptance-report.md`, `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md` |
| V4.2 user-confirmed binding UX | passed | `docs/V4.x/v4_2-final-acceptance-report.md`, `docs/V4.x/evidence/v4_2-binding-ux-smoke-2026-05-26.md` |
| V4.3 manual route-test prototype | passed | `docs/V4.x/v4_3-final-acceptance-report.md`, `docs/V4.x/evidence/v4_3-manual-route-test-smoke-2026-05-27.md` |
| V4.4 managed exec JSONL mapping | passed | `docs/V4.x/v4_4-final-acceptance-report.md`, `docs/V4.x/evidence/v4_4-managed-exec-jsonl-smoke-2026-05-27.md` |
| V4.5 managed TUI hook lifecycle | passed scoped | `docs/V4.x/v4_5-final-acceptance-report.md`, `docs/V4.x/evidence/v4_5-managed-tui-hook-lifecycle-smoke-2026-05-27.md` |
| V4.6 startup diagnostics | passed | `docs/V4.x/evidence/v4_6-startup-diagnostics-smoke-2026-05-27.md` |
| V4.7 session status | passed | `docs/V4.x/evidence/v4_7-session-status-smoke-2026-05-27.md` |

## Automatic Checks

| Check | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed, 51 tests |
| `node scripts/v4_4_managed_session_smoke.mjs` | passed |
| `node scripts/v4_5_managed_tui_preflight_smoke.mjs` | passed |
| `node packages/petctl/dist/cli.js codex doctor --json` | passed |
| `node packages/petctl/dist/cli.js codex session status --json` | passed |

## PRD Review

Result: no critical or major mismatch.

V4.x remains aligned with the active PRD because:

- The user-facing reliable monitoring path is wrapper-launched managed sessions.
- Already-open OS-level window discovery remains candidate/binding only, not a lifecycle event source.
- V4.5 TUI hook evidence is scoped to observed real hook events.
- `PermissionRequest` was not observed in the local V4.5 run and is not claimed passed.
- V4.6 and V4.7 are diagnostics/status only and do not create new lifecycle claims.

## Security Scan

Result: passed.

Accepted evidence records sanitized summaries only. It does not record raw TTY, raw process args, window title, terminal text, prompt text, tool command text, shell history, screen contents, clipboard contents, token, Authorization header value, raw payload, transcript path value, full local path, workspace path value, config path value, or `api-token.json` content.

## Claim Scan

Allowed final claim:

```text
V4.x managed Codex session-to-PetInstance state mapping passed for tested local wrapper-launched exec JSONL and scoped managed TUI hook scenarios, with Terminal.app candidate binding and manual route-test prototype accepted.
```

Forbidden as ready / passed:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
already-open Codex window auto-monitoring ready
state lifecycle routing ready
lifecycle event routing from OS discovery
all terminal apps supported
iTerm2 support passed
VS Code support passed
Warp support passed
Ghostty support passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
production signed release ready
```

## Drift And False-Green Risk

| Risk | Level | Decision |
| --- | --- | --- |
| OS-level discovery mistaken for lifecycle monitoring | Low | Final claim distinguishes Terminal.app binding prototype from managed wrapper event sources. |
| V4.5 diagnostics/preflight mistaken for real lifecycle | Low | Final evidence links real lifecycle smoke separately. |
| PermissionRequest overclaimed | Low | Final report explicitly excludes it for the local run. |
| Session status mistaken for monitoring readiness | Low | V4.7 is read-only diagnostics/status. |

No High risk remains.

## Final Decision

V4.x final acceptance passed for the scoped managed-session and Terminal.app prototype closure described above.

V4.x still does not support or claim:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-monitoring ready
all terminal apps
iTerm2 / VS Code / Warp / Ghostty support
all Codex workflows verified
production signed release ready
```
