# Claude Code Hook Smoke Evidence 2026-05-19

status: blocked  
date: 2026-05-19  
phase: V3.0 Phase 3.2 - Claude Code Hook Hardening  
environment: macOS local  
Claude Code version: 2.1.114  
token value recorded: no

## Scope

This evidence covers the V3.0 Phase 3.2 attempt to harden and verify Claude Code hook integration.

No PetEvent schema, CatStateMachine, Rust bridge, petctl argument, MCP, USB, Windows, 3D, photo customization, signing, or auto-update behavior was changed.

## Hook Readiness Changes

| Item | Result | Notes |
| --- | --- | --- |
| Hook wrapper root detection | pass | `notify-pet.sh` now resolves repo root from the script path instead of assuming `pwd` is the repo root. |
| Cooldown write timing | pass | Cooldown stamp is written only after a send succeeds. |
| `petctl` path | pass | Primary path still uses `node packages/petctl/dist/cli.js notify`. |
| HTTP fallback | pass | If `petctl` fails, wrapper falls back to localhost HTTP with curl and token from env/config. |
| Settings default hook | pass | `settings-hooks.example.json` only configures `Notification -> need_input`. |
| Default shell | pass | Settings command uses `zsh skills/claude-agent-pet/hooks/notify-pet.sh notification` for macOS local compatibility. |

## Static Checks

| Check | Result | Notes |
| --- | --- | --- |
| `bash -n skills/claude-agent-pet/hooks/notify-pet.sh` | pass | Syntax valid under bash. |
| `JSON.parse(settings-hooks.example.json)` | pass | Hook settings JSON valid. |
| `claude --version` | pass | `2.1.114 (Claude Code)`. |

## Wrapper Baseline

Manual wrapper baseline was executed to prove the wrapper can write a PetEvent. This does not count as Claude Code hook verification.

| Scenario | Result | Evidence |
| --- | --- | --- |
| `zsh skills/claude-agent-pet/hooks/notify-pet.sh notification` | pass | diagnostics accepted `evt_1779177684787_2`, `sourceId=claude-code.local`, `level=need_input`, title `Claude Code needs attention`. |

## Real Claude Code Hook Attempt

Command shape:

```text
claude -p --settings skills/claude-agent-pet/settings-hooks.example.json --include-hook-events --output-format stream-json --verbose --permission-mode default "<prompt>"
```

Observed lifecycle evidence:

- `SessionStart` hooks started.
- Global/user `SessionStart` hooks attempted to write under `/Users/Zhuanz/.claude/session-env/...` and failed with EPERM in this sandbox.
- `UserPromptSubmit` hook started and responded.
- No `Notification` hook event was observed.
- Claude API retried with `error: unknown` and the process was manually terminated to avoid an indefinite wait.

## Diagnostics Evidence

Accepted summaries after the attempt:

| eventId | sourceId | level | titlePreview | Cause |
| --- | --- | --- | --- | --- |
| `evt_1779177684787_2` | `claude-code.local` | `need_input` | `Claude Code needs attention` | manual wrapper baseline, not real Claude Code Notification hook |
| `evt_1779177531486_1` | `claude-code.local` | `error` | `Claude Code hook reported an error` | manual/raw baseline, not real Claude Code Notification hook |

No hook-caused `Notification -> need_input` event was proven in diagnostics.

## Safety Checks

| Check | Result | Notes |
| --- | --- | --- |
| No token printed | pass | Token value was not printed or recorded. |
| No hook stdin echoed | pass | Wrapper does not read or echo stdin. |
| No payload copied into message | pass | Wrapper sends fixed title only. |
| No illegal sound path/URL | pass | Wrapper uses `need_input_chime` or `error_chime` only. |
| No direct UI control | pass | Wrapper writes only structured PetEvent via `petctl` or localhost HTTP. |
| No `eval` | pass | Wrapper does not use `eval`. |
| Anti-spam | pass | Wrapper has 8 second cooldown. |

## Claim Decision

Current status is `blocked`, not `passed`.

Allowed now:

```text
Claude Code hook wrapper readiness hardened.
Claude Code hook example prepared.
```

Still forbidden:

```text
Claude Code hook workflow verified.
Claude Code integration verified.
```

## Remaining Blockers

1. A real Claude Code `Notification` hook event must be triggered.
2. The project hook must be observed in `/hooks` or stream-json lifecycle output.
3. diagnostics must show a new hook-caused `sourceId=claude-code.local`, `level=need_input` accepted event.
4. Operator must visually confirm the cat entered `need_input` because of the hook event.
