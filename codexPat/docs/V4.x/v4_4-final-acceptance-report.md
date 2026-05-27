# V4.4 Final Acceptance Report

status: passed-scoped-exec-jsonl

date: 2026-05-27

## Scope

V4.4 adds a managed session user entry:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode exec \
  --monitor jsonl \
  --name "Review Cat" \
  -- codex exec --json "task"
```

This phase passes for managed exec JSONL state mapping. Managed TUI hooks remain not-run and no TUI hook claim is made.

## Implementation Summary

- Added `petctl codex session start`.
- Added `--mode exec|tui`.
- Added `--monitor jsonl|hooks|none`.
- Reused existing `launchCodex`.
- Injected `AGENT_DESKTOP_PET_BINDING_ID` in addition to `AGENT_DESKTOP_PET_INSTANCE_ID`.
- Recorded managed monitor summary with `sessionMode` and redacted `bind_managed_*` binding id.
- Added `scripts/v4_4_managed_session_smoke.mjs`.

## Evidence

| Evidence | Result |
| --- | --- |
| `docs/V4.x/v4_4-development-plan.md` | completed |
| `docs/V4.x/v4_4-acceptance-plan.md` | completed |
| `docs/V4.x/v4_4-prd-spec-review.md` | no major mismatch |
| `docs/V4.x/v4_4-plan-audit.md` | no High risk |
| `docs/V4.x/evidence/v4_4-managed-exec-jsonl-smoke-2026-05-27.md` | passed |
| `docs/V4.x/evidence/v4_4-managed-tui-hooks-smoke-2026-05-27.md` | not-run |

## Automatic Checks

| Check | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed, 46 tests |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |
| `node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs` | passed |
| `node scripts/v4_4_managed_session_smoke.mjs` | passed with local bridge access |

## Runtime Result

Managed exec JSONL smoke passed:

```text
simple: turn.started -> thinking -> success
tool success: item.started -> running -> success
tool failure: turn.failed/error -> error
```

The smoke verified:

- managed session receives an instance id.
- managed session receives a managed binding id.
- state updates route to the managed session cat.
- structured failure maps to `error`.
- cleanup succeeds.

## PRD Spec Review

Result: no critical or major mismatch for managed exec JSONL.

V4.4 aligns with the PRD's "one Codex session one cat" goal for wrapper-launched managed exec sessions.

Remaining PRD gap:

```text
Managed interactive TUI hook lifecycle requires real hook trust and manual lifecycle evidence before any TUI state mapping claim.
```

## Drift / False-green Risk

| Risk | Level | Result |
| --- | --- | --- |
| Exec JSONL passed generalized to TUI monitoring | High | mitigated by scoped final status and not-run TUI evidence |
| V4.3 OS binding treated as lifecycle monitoring | High | mitigated; V4.4 uses managed launch only |
| Hook trust skipped | High | mitigated; TUI evidence is not-run, not passed |
| Sensitive evidence leakage | Medium | security scan passed |

Overall risk after scoped closure: Medium.

No High risk remains for the scoped exec JSONL claim. High risk remains if this is generalized to TUI or already-open window monitoring.

## Security Scan

Passed for accepted exec JSONL evidence.

Evidence does not include token, Authorization header value, raw JSONL payload, raw hook payload, prompt text, tool command text, terminal text, screen contents, clipboard contents, transcript path value, full local path, workspace path value, config path value, or `api-token.json` content.

## Claim Scan

Allowed claim:

```text
V4.4 managed Codex exec JSONL state mapping passed for tested local wrapper-launched scenario.
```

Forbidden as ready / passed:

```text
OS-level Codex window binding ready
already-open Codex window auto-monitoring ready
interactive Codex TUI monitoring ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
cross-platform ready
production signed release ready
```

## Final Decision

V4.4 is passed for scoped managed exec JSONL state mapping.

V4.4 managed TUI hook state mapping remains not-run and requires manual trust/lifecycle evidence before it can be accepted.
