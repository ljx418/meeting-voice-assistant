# V4.4 Managed TUI Hooks Smoke Evidence

status: not-run

date: 2026-05-27

## Scope

This evidence is reserved for real managed Codex TUI hook lifecycle validation:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode tui \
  --monitor hooks \
  --name "V4.4 TUI Cat" \
  -- codex
```

## Current Result

The real managed TUI hook lifecycle smoke was not run in this automated closure.

No TUI hook claim is made by this evidence.

## Required Manual Acceptance

1. Build `petctl`.
2. Keep desktop app running.
3. Start a managed TUI session with `--mode tui --monitor hooks`.
4. Use `/hooks` in Codex to review/trust project hooks if required.
5. Confirm the managed process has `AGENT_DESKTOP_PET_INSTANCE_ID`.
6. Trigger a real prompt and observe:
   - `UserPromptSubmit -> thinking`
   - `PreToolUse -> running`
   - `Stop -> success` or idle marker
7. Trigger a permission request if local policy allows and observe:
   - `PermissionRequest -> need_input`
8. Confirm default and unrelated pets are unchanged.

## Blocked / Deferred Boundaries

- `PostToolUse failure -> error` remains blocked unless real hook payload exposes stable failure fields.
- This evidence cannot be replaced by curl, manual `petctl notify`, fixture smoke, or terminal text parsing.

## Forbidden Conclusion

```text
interactive Codex TUI monitoring ready
all Codex workflows verified
OS-level Codex window binding ready
already-open Codex window auto-monitoring ready
```
