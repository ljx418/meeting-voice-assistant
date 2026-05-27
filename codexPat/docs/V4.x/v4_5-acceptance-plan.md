# V4.5 Managed Codex TUI Hook Acceptance Plan

status: planned

date: 2026-05-27

## Gate 1: PRD Review

V4.5 aligns with the PRD only if it proves a managed Codex TUI session can drive one cat through real Codex hooks.

Passing a wrapper preflight alone is not sufficient for the final TUI hook state mapping claim.

## Gate 2: Automated Wrapper Preflight

Command:

```bash
node scripts/v4_5_managed_tui_preflight_smoke.mjs
```

Acceptance:

- desktop health is ok.
- `petctl codex session start --mode tui --monitor hooks` creates one PetInstance.
- fake managed TUI child receives `AGENT_DESKTOP_PET_INSTANCE_ID`.
- fake managed TUI child receives `AGENT_DESKTOP_PET_BINDING_ID`.
- output summary records `sessionMode=tui`.
- output summary records `mode=hooks`.
- output summary records only redacted `bind_managed_*`.
- no sensitive fields are recorded.

This gate proves wrapper readiness, not real Codex hook lifecycle.

## Gate 3: Manual Real Hook Lifecycle

Command:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode tui \
  --monitor hooks \
  --name "V4.5 TUI Cat" \
  -- codex
```

Manual steps:

1. In the launched Codex TUI, run `/hooks`.
2. Review and trust the project hooks.
3. Submit a real user prompt.
4. Observe target cat state.
5. Trigger a tool use.
6. Trigger a permission request if local policy allows.
7. Let the turn stop.
8. Confirm default and unrelated pets are unchanged.

Required evidence:

- `UserPromptSubmit -> thinking` passed.
- `PreToolUse -> running` passed.
- `Stop -> success` or idle marker passed.
- `PermissionRequest -> need_input` passed or explicitly blocked by local policy.
- no curl, manual `petctl notify`, fixture smoke, terminal text parsing, or transcript path evidence is used.

## Gate 4: Regression

Required:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
node scripts/v4_4_managed_session_smoke.mjs
node scripts/v4_5_managed_tui_preflight_smoke.mjs
```

## Gate 5: Final Decision

- If only preflight passes, V4.5 remains pending manual acceptance.
- If real hook lifecycle passes, V4.5 final acceptance may pass with the scoped TUI claim.
- If hooks are not trusted or not loaded, V4.5 is blocked.

## Forbidden Claims

```text
interactive Codex TUI monitoring ready
already-open Codex window auto-monitoring ready
OS-level Codex window binding ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
```
