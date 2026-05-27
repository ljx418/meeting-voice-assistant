# V4.4 Managed Codex Session State Binding Development Plan

status: planned

date: 2026-05-27

## Scope

V4.4 closes the user-facing gap left by V4.3:

```text
one project-managed Codex session -> one PetInstance -> scoped state mapping.
```

V4.4 does not try to monitor arbitrary already-open Codex TUI windows. A Codex session must be launched through the project wrapper so the process receives `AGENT_DESKTOP_PET_INSTANCE_ID` and a trusted event source can route state to the correct cat.

## Supported Modes

### Managed exec mode

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode exec \
  --monitor jsonl \
  --name "Review Cat" \
  -- codex exec --json "summarize this repository"
```

State source: structured `codex exec --json` JSONL stdout.

### Managed TUI mode

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode tui \
  --monitor hooks \
  --name "TUI Cat" \
  -- codex
```

State source: project-level Codex hooks through `.codex/hooks.json` and `scripts/codex-pet-hook.mjs`.

Managed TUI mode requires Codex hook trust / review. If hooks are not trusted or not loaded, state mapping is blocked rather than silently accepted.

## Implementation Work

1. Add `petctl codex session start`.
2. Support `--mode exec|tui`.
3. Support `--monitor jsonl|hooks|none`.
4. Reuse existing `launchCodex`.
5. Inject:
   - `AGENT_DESKTOP_PET_INSTANCE_ID`
   - `AGENT_DESKTOP_PET_BINDING_ID`
   - `AGENT_DESKTOP_PET_SOURCE_ID=codex.local`
   - `AGENT_DESKTOP_PET_SOURCE_KIND=codex`
   - `AGENT_DESKTOP_PET_SOURCE_NAME=Codex`
6. For JSONL mode, parse only structured event type fields.
7. For hooks mode, rely only on trusted hook lifecycle events.
8. Do not record terminal text, prompt text, tool command text, raw payloads, or local paths.

## State Mapping

### JSONL

| Codex JSONL event | Pet state |
| --- | --- |
| `turn.started` | `thinking` |
| `item.started` | `running` |
| `turn.completed` | `success` if no earlier error |
| `turn.failed` | `error` |
| `error` | `error` |

### Hooks

| Codex hook | Pet state |
| --- | --- |
| `SessionStart` | `running` marker |
| `UserPromptSubmit` | `thinking` |
| `PreToolUse` | `running` |
| `PermissionRequest` | `need_input` |
| `PostToolUse` | `error` only if stable failure fields are present |
| `Stop` | `success` only if no recent error / warning marker |

`Stop` remains a turn completion marker and does not prove business quality success.

## Non-goals

- no arbitrary already-open Codex TUI auto-monitoring.
- no terminal text parsing.
- no screen reading.
- no transcript path monitoring.
- no OS-level Codex window binding readiness claim.
- no all Codex workflows claim.
- no cross-terminal readiness claim.

## Evidence

- `docs/V4.x/evidence/v4_4-managed-exec-jsonl-smoke-2026-05-27.md`
- `docs/V4.x/evidence/v4_4-managed-tui-hooks-smoke-2026-05-27.md`
- `docs/V4.x/v4_4-final-acceptance-report.md`

## Allowed Claim

```text
V4.4 managed Codex session-to-PetInstance binding with scoped state mapping passed for tested local wrapper-launched scenarios.
```

## Forbidden Claims

```text
OS-level Codex window binding ready
already-open Codex window auto-monitoring ready
interactive Codex TUI monitoring ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
cross-platform ready
production signed release ready
```
