# V4.5 Managed Codex TUI Hook Acceptance Development Plan

status: planned

date: 2026-05-27

## Scope

V4.5 focuses only on managed Codex TUI hook state mapping:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode tui \
  --monitor hooks \
  --name "V4.5 TUI Cat" \
  -- codex
```

The Codex TUI process must be launched through the project wrapper so it receives `AGENT_DESKTOP_PET_INSTANCE_ID` and project hooks can route events to the correct cat.

## Development Work

1. Verify the managed TUI wrapper path:
   - creates a PetInstance.
   - injects `AGENT_DESKTOP_PET_INSTANCE_ID`.
   - injects `AGENT_DESKTOP_PET_BINDING_ID`.
   - does not parse stdout or terminal text.
   - does not record prompt text, tool command text, raw hook payload, or local paths.
2. Add a V4.5 preflight smoke for wrapper readiness using a local fake TUI child process.
3. Document the real manual hook lifecycle acceptance path.
4. Preserve the V4.4 managed exec JSONL accepted path.

## Real Hook Lifecycle Target

The manual real TUI hook acceptance must observe:

| Hook | Expected pet state |
| --- | --- |
| `UserPromptSubmit` | `thinking` |
| `PreToolUse` | `running` |
| `PermissionRequest` | `need_input`, if local Codex policy emits it |
| `Stop` | `success` / idle marker |

`PostToolUse failure -> error` remains blocked unless real hook payload exposes stable failure fields.

## Non-goals

- no arbitrary already-open Codex TUI monitoring.
- no terminal text parsing.
- no screen reading.
- no transcript path monitoring.
- no OS-level Codex window binding ready claim.
- no all Codex workflows claim.

## Evidence

- `docs/V4.x/evidence/v4_5-managed-tui-preflight-smoke-2026-05-27.md`
- `docs/V4.x/evidence/v4_5-managed-tui-hook-lifecycle-smoke-2026-05-27.md`
- `docs/V4.x/v4_5-final-acceptance-report.md`

## Allowed Claim

Only after real hook lifecycle evidence:

```text
V4.5 managed Codex TUI hook state mapping passed for tested local wrapper-launched scenario.
```

If only preflight passes:

```text
V4.5 managed Codex TUI wrapper preflight passed; real hook lifecycle acceptance remains pending.
```
