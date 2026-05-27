# V3.6 Workflow Coverage Matrix

文档状态：historical blocked；deprecated active strategy

| Workflow | Expected mapping | Result | Notes |
| --- | --- | --- | --- |
| simple answer | `UserPromptSubmit -> thinking`, clean `Stop -> success` | passed | Real `codex exec` completed and target instance reached `success`. |
| tool success | `PreToolUse -> running`, clean `Stop -> success` | passed | Real shell command completed with exit code 0 in Codex output. |
| tool failure | `PostToolUse failure -> error`, later `Stop` must not overwrite error | blocked | Real shell command exited 17, but `PostToolUse` hook payload did not expose stable failure fields. |
| permission request | `PermissionRequest -> need_input` | not-run | Non-interactive `codex exec` did not provide a stable approval prompt path in this run. |
| compact/subagent | diagnostic only or deferred | deferred | Not part of V3.6 pass claim while blocked. |

## Stop Boundary

The fixture regression verifies:

- `PostToolUse failure -> error`.
- `Stop after failure` keeps `error`.
- a clean new turn can later reach `success`.

The real failure workflow remains historical blocked because stable failure data is not present in the local hook payload.

Current strategy: do not continue V3.6 hook-only monitoring. Use V3.7 JSONL monitor for supported wrapper-launched `codex exec --json` sessions.
