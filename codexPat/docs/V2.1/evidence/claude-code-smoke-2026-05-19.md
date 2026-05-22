# Claude Code Smoke Evidence 2026-05-19

status: blocked  
date: 2026-05-19  
tester: Codex local operator workflow  
environment: macOS local  
Claude Code version: 2.1.114  
desktop app commit: c774626a  
token source: desktop app config file  
token value recorded: no

## Scope

This evidence file covers V2.1-C:

- C1: Claude Code Skill Workflow Smoke.
- C2: Claude Code Hook Workflow Smoke.

No runtime code, PetEvent schema, state machine, Rust bridge, petctl argument, MCP, USB, Windows, 3D, photo customization, auto update, or signing behavior was changed.

## Setup

| Item | Result | Notes |
| --- | --- | --- |
| Desktop app running | pass | `/api/health` returned healthy before smoke. |
| `petctl` available | pass | `node packages/petctl/dist/cli.js` used by Claude Code prompts. |
| Skill reviewed | pass | `skills/claude-agent-pet/SKILL.md` requires `source.id=claude-code.local`, `source.kind=claude_code`, `source.name=Claude Code`. |
| Hook example reviewed | pass | `skills/claude-agent-pet/settings-hooks.example.json` now focuses on `Notification -> need_input`. `UserPromptSubmit`, `PreToolUse`, and `Stop` are intentionally not enabled as default acceptance hooks. |
| Token source | pass | Token loaded from desktop app config by wrapper command; token value was not written to evidence. |
| Skill/template loading method | prompt-referenced | Real `claude -p` prompts explicitly referenced and followed the skill file rules. |
| Hook loading method | blocked | Loaded with `claude --settings skills/claude-agent-pet/settings-hooks.example.json --include-hook-events --output-format stream-json --verbose`, but `Notification` did not trigger in tested non-interactive flows. |
| Hook settings location | project file | Global `~/.claude/settings.json` was not modified. |
| `/hooks` verification result | not-run | Non-interactive `claude -p` was used; lifecycle output showed hooks, but not a `Notification` event. |

## Runtime Baseline

Manual baseline was sent before real Claude Code smoke to confirm the write path. This does not count as Claude Code integration verified.

| Scenario | Result | Evidence |
| --- | --- | --- |
| Manual Claude Code baseline | pass | `evt_1779161415138_8`, `sourceId=claude-code.local`, `level=success`. |

## C1 Skill Workflow Evidence

| Scenario | Expected | Actual diagnostics evidence | Runtime result | Visual observation |
| --- | --- | --- | --- | --- |
| Smoke A: success path | `thinking` or `running`, then `success` | `evt_1779161559496_9` thinking; `evt_1779161598847_10` success | pass | blocked: operator visual confirmation not yet recorded. |
| Smoke B: failure path | `running`, then `error` | `evt_1779161673291_11` running; `evt_1779161691052_12` error | pass | blocked: operator visual confirmation not yet recorded. |
| Smoke C: need input | `need_input` | `evt_1779161749592_13` need_input | pass | blocked: operator visual confirmation not yet recorded. |

Claude Code executed the required safe local scenarios:

- Read project status documents.
- Ran `pnpm --filter @agent-desktop-pet/petctl test`.
- Ran a safe failing command path for error reporting.
- Stopped before an action that would require user confirmation and emitted `need_input`.

## C2 Hook Workflow Evidence

| Scenario | Expected | Actual | Result | Notes |
| --- | --- | --- | --- | --- |
| Hook capability audit | `Notification`, `PostToolUse`, `UserPromptSubmit`, `Stop` supported | pass | pass | Local Claude Code docs list `Notification`, `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreCompact`. No `PostToolUseFailure` event was found. |
| Hook settings updated | `Notification -> need_input` configured | pass | pass | `settings-hooks.example.json` now contains only the safe Notification hook by default. |
| Hook wrapper | Safe wrapper writes through `petctl` | pass | pass | `skills/claude-agent-pet/hooks/notify-pet.sh` uses `node packages/petctl/dist/cli.js notify`; it does not print token or hook stdin. |
| Hook lifecycle output | Real Claude Code lifecycle output available | pass | partial | `--include-hook-events --output-format stream-json --verbose` produced lifecycle output for built-in/global hooks and user prompt flows. |
| Notification -> need_input | `sourceId=claude-code.local`, `level=need_input` | No `Notification` event triggered in tested flows | blocked | Tested Bash permission, AskUserQuestion, and disallowed Bash paths; none emitted a `Notification` hook event in non-interactive `claude -p`. |
| PostToolUseFailure -> error | `sourceId=claude-code.local`, `level=error` | Not supported as a named event in local docs | pending | Use `PostToolUse` with result parsing in a future phase only if failure information is stable. |
| Hook does not print token | No token output | pass | pass | Wrapper redirects `petctl` output and does not echo env or stdin. |
| Hook failure does not interrupt Claude Code | Non-blocking hook behavior | pass by design | partial | Wrapper exits `0` and uses `|| true`; actual `Notification` event trigger remains blocked. |

## C2 Attempted Commands

The following real Claude Code smoke attempts were executed:

| Attempt | Command shape | Hook evidence | Result |
| --- | --- | --- | --- |
| Bash permission path | `claude -p --settings ... --include-hook-events --output-format stream-json --verbose --permission-mode default "Use Bash..."` | stream-json showed lifecycle events, but no `Notification`. | blocked |
| AskUserQuestion path | `claude -p --settings ... --include-hook-events --output-format stream-json --verbose --permission-mode bypassPermissions --allowedTools=AskUserQuestion ...` | `AskUserQuestion` was attempted; no `Notification` hook event emitted. | blocked |
| Disallowed Bash path | `claude -p --settings ... --include-hook-events --output-format stream-json --verbose --disallowedTools=Bash ...` | Bash was unavailable, but no `Notification` hook event emitted. | blocked |

## Diagnostics Evidence

Accepted summaries from `GET /api/diagnostics` included:

| eventId | sourceId | level | titlePreview |
| --- | --- | --- | --- |
| `evt_1779161749592_13` | `claude-code.local` | `need_input` | `Claude Code 需要用户确认` |
| `evt_1779161691052_12` | `claude-code.local` | `error` | `Claude Code V2.1-C1 smoke test failed` |
| `evt_1779161673291_11` | `claude-code.local` | `running` | `Claude Code 正在执行 V2.1-C1 smoke test` |
| `evt_1779161598847_10` | `claude-code.local` | `success` | `Claude Code V2.1-C1 smoke 通过` |
| `evt_1779161559496_9` | `claude-code.local` | `thinking` | `Claude Code 正在分析项目状态` |

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | warn | No hard failures. Warnings: rustup not installed; network endpoints unreachable; sandbox could not listen on dev port 1420. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 6 tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |

Latest V2.1-C2 checks on 2026-05-19:

| Command | Result | Notes |
| --- | --- | --- |
| `bash -n skills/claude-agent-pet/hooks/notify-pet.sh` | pass | Hook wrapper syntax valid. |
| `node -e "JSON.parse(...settings-hooks.example.json...)"` | pass | Hook settings JSON valid. |
| `pnpm run doctor` | warn | No hard failures. Warnings: rustup not installed; network endpoints unreachable; sandbox could not listen on dev port 1420. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 6 tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |

## Safety Checks

| Check | Result | Notes |
| --- | --- | --- |
| No full token printed | pass | Evidence and command summaries do not record token values. |
| No illegal sound | pass | Used only whitelist IDs such as `success_chime`, `error_chime`, and `need_input_chime`. |
| No local path / URL sound | pass | No sound path or URL was sent. |
| No direct UI control | pass | Claude Code only wrote structured events via `petctl` / localhost API. |
| No desktop internal script execution | pass | Claude Code did not execute desktop internal scripts. |
| Anti-spam | pass | Events were sent only on scenario state changes, not per file/log line. |

## Claim Decision

Current status is blocked, not passed.

Allowed now:

```text
Claude Code skill runtime smoke produced accepted diagnostics evidence for tested local scenarios.
```

Not allowed yet:

```text
Claude Code skill workflow verified for tested local smoke scenarios.
Claude Code hook workflow verified.
Claude Code local workflow integration verified.
```

The first claim is blocked by missing operator visual acceptance. The second and third claims are blocked by incomplete hook verification.

## Remaining Blockers

1. Operator must visually confirm the cat changed state for `thinking/running`, `success`, `error`, and `need_input` during Claude Code C1 smoke.
2. A real Claude Code `Notification` event must be triggered in a mode that invokes `skills/claude-agent-pet/hooks/notify-pet.sh notification`.
3. diagnostics must show a new `sourceId=claude-code.local`, `level=need_input` accepted event caused by the hook.
4. If possible, add and verify a failure hook mapping for error reporting without breaking Claude Code tasks; no `PostToolUseFailure` event is currently documented locally.
