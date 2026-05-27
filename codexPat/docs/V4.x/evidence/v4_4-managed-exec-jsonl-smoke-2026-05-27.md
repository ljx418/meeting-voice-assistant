# V4.4 Managed Exec JSONL Smoke Evidence

status: passed

date: 2026-05-27

## Scope

This evidence covers only project-managed `codex session start --mode exec --monitor jsonl` scenarios.

It does not cover arbitrary already-open Codex TUI windows or interactive TUI lifecycle monitoring.

## Command

```bash
node scripts/v4_4_managed_session_smoke.mjs
```

The smoke uses a local fake `codex exec --json` child process to emit structured JSONL event types. It verifies the project-owned wrapper path without recording raw JSONL payloads, prompt text, tool commands, local paths, or tokens.

## Results

| Case | Result |
| --- | --- |
| desktop health | passed |
| managed session creates a cat | passed |
| `AGENT_DESKTOP_PET_INSTANCE_ID` injected | passed |
| `AGENT_DESKTOP_PET_BINDING_ID` injected | passed |
| managed session mode recorded as `exec` | passed |
| managed binding id recorded as redacted `bind_managed_*` | passed |
| simple answer observes `turn.started` | passed |
| simple answer maps `thinking` | passed |
| simple answer final state `success` | passed |
| tool success observes `item.started` | passed |
| tool success maps `running` | passed |
| tool success final state `success` | passed |
| tool failure observes `turn.failed` / `error` | passed |
| tool failure marks structured failure | passed |
| tool failure final state `error` | passed |
| cleanup | passed |
| security redaction scan | passed |
| claim scan | passed |

## Accepted Runtime Summary

```text
status=passed
sessionMode=exec
bindingId=bind_managed_*
simple: turn.started -> thinking -> success
tool success: item.started -> running -> success
tool failure: turn.failed/error -> error
```

## Security Review

Evidence does not include:

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
full local path
workspace path
config path
api-token.json
```

## Allowed Conclusion

```text
V4.4 managed Codex exec JSONL state mapping passed for tested local wrapper-launched scenario.
```

## Forbidden Conclusion

```text
OS-level Codex window binding ready
already-open Codex window auto-monitoring ready
interactive Codex TUI monitoring ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
```
