# V3.6 Codex Real Workflow Smoke Evidence

date: 2026-05-25

status: blocked

## Commands

Representative commands were run through `petctl codex launch` with real local `codex exec` child sessions:

```bash
node packages/petctl/dist/cli.js codex launch --json --name "V3.6 Real Workflow" --bin codex -- exec --dangerously-bypass-hook-trust --sandbox read-only --json "Respond with exactly: v36-ok"
node packages/petctl/dist/cli.js codex launch --json --name "V3.6 Tool Success" --bin codex -- exec --dangerously-bypass-hook-trust --sandbox read-only --json "Use a shell command to print v36-tool-ok, then answer exactly: v36-tool-ok"
node packages/petctl/dist/cli.js codex launch --json --name "V3.6 Failure Debug" --bin codex -- exec --dangerously-bypass-hook-trust --sandbox read-only --json "Use a shell command that exits with code 17, then answer exactly: v36-debug-failed-observed"
```

`--dangerously-bypass-hook-trust` was used only for local smoke. It is not the normal user path.

## Results

| Case | Result |
| --- | --- |
| Codex CLI available | passed |
| desktop health | passed |
| simple answer real workflow | passed |
| tool success real workflow | passed |
| tool failure command observed by Codex | passed |
| `PostToolUse` stable failure field available | blocked |
| `PostToolUse failure -> error` real workflow | blocked |
| `Stop` fixture false-green guard | passed |
| V3.1 runtime smoke rerun | passed |
| V3.3 binding smoke rerun | passed |
| V3.4 fixture smoke rerun | passed |
| petctl check | passed |
| petctl test | passed |

## Safe Hook Payload Summary

The tested local Codex `PostToolUse` hook payload for the failing shell command exposed safe field names equivalent to:

```text
cwd, hook_event_name, model, permission_mode, session_id, tool_input
```

It did not expose stable failure fields such as:

```text
exitCode, exit_code, status, success, error, result
```

Fixture coverage now includes an observed-shape `PostToolUse` payload with `tool` and `tool_input` only. That case exits cleanly and leaves the current state unchanged, so the hook remains schema-compatible without inferring failure from command text.

The debug summary did not record raw hook stdin, raw payload, prompt text, command text, transcript path, config path, workspace path, token, Authorization header, or full local path.

## Security

Temporary debug output was removed after inspection. Evidence records only sanitized field names and status conclusions.

## Claim Boundary

This evidence does not allow:

```text
V3.6 selected Codex workflow hook coverage smoke passed for tested local scenarios.
```

V3.6 remains historical blocked evidence until real `PostToolUse` failure evidence is available through a stable hook payload field and the acceptance plan is explicitly revived, revised, and audited. Current Codex exec monitoring uses V3.7 JSONL monitor instead.
