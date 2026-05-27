# V4.4 Managed Codex Session State Binding Acceptance Plan

status: planned

date: 2026-05-27

## Gate 1: PRD Conformance

V4.4 may pass only if it satisfies the PRD goal:

```text
one Codex session can be represented by one cat, and trusted session state events can update that cat.
```

The implementation must also preserve the PRD boundary that the product is not an OS-level text/screen monitor.

## Gate 2: Managed Exec JSONL

Command:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode exec \
  --monitor jsonl \
  --name "V4.4 Exec Cat" \
  -- codex exec --json "simple local task"
```

Acceptance:

- creates or attaches exactly one PetInstance for the managed session.
- injects `AGENT_DESKTOP_PET_INSTANCE_ID`.
- observes structured JSONL event types.
- maps `turn.started -> thinking`.
- maps `item.started -> running` when tool events exist.
- maps `turn.completed -> success` if no error occurred.
- maps `turn.failed` or `error -> error`.
- does not overwrite an earlier error with success.
- affects only the managed session cat.

## Gate 3: Managed TUI Hooks

Command:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode tui \
  --monitor hooks \
  --name "V4.4 TUI Cat" \
  -- codex
```

Acceptance:

- Codex hook config is loaded and trusted.
- target Codex process receives `AGENT_DESKTOP_PET_INSTANCE_ID`.
- at least `UserPromptSubmit -> thinking`, `PreToolUse -> running`, and `Stop -> success/idle` are observed in a real managed TUI session, or the TUI hook gate is marked blocked.
- `PermissionRequest -> need_input` passes if the local Codex permission policy emits the hook; otherwise it is explicitly blocked, not passed.
- `PostToolUse failure -> error` remains blocked unless stable failure fields appear in the real hook payload.

## Gate 4: Regression

Required checks:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

## Gate 5: Security Scan

Evidence and output must not contain:

```text
token
Authorization
raw JSONL payload
raw hook payload
prompt text
tool command text
terminal text
screen contents
clipboard contents
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Gate 6: Claim Scan

Allowed final claim:

```text
V4.4 managed Codex session-to-PetInstance binding with scoped state mapping passed for tested local wrapper-launched scenarios.
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

## Final Decision Rule

- If managed exec JSONL passes but managed TUI hooks are not trusted or not observable, V4.4 may pass only for managed exec JSONL and must not claim TUI hook state mapping.
- If both managed exec JSONL and managed TUI hook lifecycle pass, V4.4 may use the full scoped allowed claim.
- If neither trusted event source can produce state updates, V4.4 is blocked.
