# Codex Smoke Evidence

status: passed  
date: 2026-05-19  
tester: Codex CLI smoke executed by local `codex exec`  
environment: macOS local

## Setup

- App launched: pass
- `/api/health`: pass
- diagnostics with token: pass
- Manual baseline `codex.local` event: pass, not counted as Codex verified
- Codex CLI version: `codex-cli 0.124.0`
- Desktop app commit / workspace commit: `c774626a`
- Token source: desktop app config `api-token.json`; token value was not recorded
- Codex skill/template loading method: prompt-referenced
- Codex command mode: `codex exec -C /Users/Zhuanz/Desktop/workspace/codexPat --full-auto`

## Scope Boundary

This evidence uses real `codex exec` tasks. It does not use ordinary shell `petctl` commands to fake Codex verification. The initial manual `Codex baseline` event only proved that `petctl` and diagnostics could accept `sourceId=codex.local`; it is excluded from the verified smoke decision.

## Codex Transcript Evidence

Smoke A transcript excerpt:

```text
OpenAI Codex v0.124.0
session id: 019e3e23-6d75-75f2-b2bb-4d2814976fec
...
node packages/petctl/dist/cli.js notify ... --level thinking --title "Codex analyzing smoke"
accepted eventId=evt_1779159099911_2
...
node packages/petctl/dist/cli.js notify ... --level running --title "Codex running smoke"
accepted eventId=evt_1779159112801_3
...
pnpm --filter @agent-desktop-pet/petctl test
tests 6, pass 6
...
node packages/petctl/dist/cli.js notify ... --level success --title "Codex smoke complete" --sound success_chime
accepted eventId=evt_1779159127209_4
```

Smoke B transcript excerpt:

```text
OpenAI Codex v0.124.0
session id: 019e3e26-284e-7b32-84da-157bc2a8752b
...
node packages/petctl/dist/cli.js notify ... --level running --title "Codex smoke running" --sound none
accepted eventId=evt_1779159276972_5
...
/bin/zsh -lc false
exited 1
...
node packages/petctl/dist/cli.js notify ... --level error --title "Codex smoke error" --sound error_chime
accepted eventId=evt_1779159290677_6
```

Smoke C transcript excerpt:

```text
OpenAI Codex v0.124.0
session id: 019e3e28-9d32-73b0-ba9e-656c2c08d717
...
node packages/petctl/dist/cli.js notify ... --level need_input --title "Codex 需要确认" --sound need_input_chime
accepted eventId=evt_1779159433916_7
...
User confirmation is required before committing or pushing changes.
```

Codex CLI printed a non-blocking local skill loading warning for an unrelated user skill:

```text
failed to load skill /Users/Zhuanz/.agents/skills/awesome-design-md/SKILL.md: missing YAML frontmatter delimited by ---
```

The requested `skills/codex-agent-pet/SKILL.md` was explicitly read and followed in all three smoke tasks.

## Diagnostics Evidence

| Scenario | Result | diagnostics evidence | Visual observation |
| --- | --- | --- | --- |
| Baseline manual event | pass | `evt_1779158932412_1`, `sourceId=codex.local`, `level=success`, title `Codex baseline` | Not counted as Codex verified. |
| Smoke A thinking | pass | `evt_1779159099911_2`, `sourceId=codex.local`, `level=thinking`, title `Codex analyzing smoke` | Operator confirmed. |
| Smoke A running | pass | `evt_1779159112801_3`, `sourceId=codex.local`, `level=running`, title `Codex running smoke` | Operator confirmed. |
| Smoke A success | pass | `evt_1779159127209_4`, `sourceId=codex.local`, `level=success`, title `Codex smoke complete` | Operator confirmed. |
| Smoke B running | pass | `evt_1779159276972_5`, `sourceId=codex.local`, `level=running`, title `Codex smoke running` | Operator confirmed. |
| Smoke B error | pass | `evt_1779159290677_6`, `sourceId=codex.local`, `level=error`, title `Codex smoke error` | Operator confirmed. |
| Smoke C need_input | pass | `evt_1779159433916_7`, `sourceId=codex.local`, `level=need_input`, title `Codex 需要确认` | Operator confirmed. |

## Operator Visual Acceptance

Operator confirmation source: user request to execute `V2.1-B Closure: Codex Visual Acceptance & Claim Update`.

| Check | Result | Operator | Timestamp |
| --- | --- | --- | --- |
| desktop pet visible | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| cat changed state during Codex smoke | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| running/thinking visible | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| success visible | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| error visible | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| need_input visible | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| diagnostics shows `sourceId=codex.local` | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| no high-frequency spam | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| no illegal sound | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| no token leakage | pass | Zhuanz | 2026-05-19 11:12:57 CST |
| no direct UI control | pass | Zhuanz | 2026-05-19 11:12:57 CST |

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | warn | No hard failures. WARN: no rustup, external network checks unreachable, sandbox cannot listen on `127.0.0.1:1420`. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 6 tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |

## Safety Checks

- No high-frequency event spam: pass. Codex sent events only at phase changes across three sessions.
- No local path / URL sound: pass. Sounds used: `none`, `success_chime`, `error_chime`, `need_input_chime`.
- No direct UI control: pass. Codex only used `petctl notify`.
- No pet script execution: pass. Codex did not execute desktop internals or control the pet UI.
- No full token disclosure: pass. Token source was used through environment/config, token value was not recorded.

## Closure

The real Codex CLI smoke produced the required diagnostics evidence for `thinking`, `running`, `success`, `error`, and `need_input`. Operator visual acceptance was provided on 2026-05-19, confirming that the desktop pet was visible and changed state during the Codex smoke.

## Claim Decision

- `V2.1-B complete: Codex local workflow integration smoke passed.`
- `Codex local workflow integration verified for tested local Codex CLI smoke scenarios.`
- This does not imply Claude Code, MCP, Windows, USB, cross-platform, or production signed release readiness.
