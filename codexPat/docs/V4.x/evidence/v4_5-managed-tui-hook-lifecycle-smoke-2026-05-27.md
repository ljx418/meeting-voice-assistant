# V4.5 Managed TUI Hook Lifecycle Smoke Evidence

status: passed-scoped

date: 2026-05-27

## Scope

This evidence covers real Codex TUI hook lifecycle validation for a wrapper-launched managed TUI session.

## Current Result

Passed for the tested local wrapper-launched scenario, scoped to:

- `UserPromptSubmit -> thinking`
- `PreToolUse -> running`
- `Stop -> success`
- target PetInstance routing only
- default and unrelated PetInstances unchanged

`PermissionRequest -> need_input` was not observed because the tested local Codex policy did not emit a permission request during the acceptance run. It remains not-passed for this local run and is not included in the scoped passed claim.

## Real Acceptance Command

The managed TUI session was started through the project wrapper:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode tui \
  --monitor hooks \
  --name "V4.5 TUI Cat" \
  -- codex
```

Inside the launched Codex TUI:

1. Run `/hooks`.
2. Review and trust project hooks.
3. Submit a real prompt.
4. Trigger a tool use.
5. Trigger a permission request if local policy allows.
6. Let the turn stop.

## Observed Results

| Observation | Result |
| --- | --- |
| Desktop health available before lifecycle run | passed |
| Managed PetInstance created for the TUI session | passed |
| `/hooks` showed project hooks installed and active | passed |
| Project hooks were trusted before lifecycle validation | passed |
| Real prompt submission changed target PetInstance to `thinking` | passed |
| Real tool-use turn changed target PetInstance to `running` | passed |
| Real Stop hook changed target PetInstance to `success` | passed |
| Default PetInstance stayed `idle` | passed |
| Unrelated PetInstances were not changed by the tested lifecycle events | passed |
| `PermissionRequest -> need_input` | not observed; local policy did not emit permission request |

## Sanitized Evidence Notes

The evidence records only hook event names, mapped states, target instance identity, and sanitized acceptance results. It does not record terminal screen contents, raw hook payloads, prompt text, tool command text, transcript paths, tokens, authorization headers, config paths, workspace paths, or full local paths.

## Forbidden Evidence

The acceptance did not use:

```text
curl mock
manual petctl notify
fixture smoke
terminal text parsing
transcript_path
raw hook payload
prompt text
tool command text
```
