# V3.4 Development Plan

文档状态：implemented for fixture gate；real Codex hook lifecycle remains gated by hook trust.

## Goal

V3.4 builds on V3.3 `petctl codex launch` session binding and adds Codex lifecycle hook state mapping.

Target mappings:

| Codex hook | Pet state |
| --- | --- |
| `SessionStart` | `running` |
| `UserPromptSubmit` | `thinking` |
| `PreToolUse` | `running` |
| `PermissionRequest` | `need_input` |
| `PostToolUse` failure | `error` |
| `Stop` | `success` |

## Implementation

- Project hook config: `.codex/hooks.json`
- Hook wrapper: `scripts/codex-pet-hook.mjs`
- Fixture smoke: `scripts/v3_4_codex_hook_fixture_smoke.mjs`
- Real lifecycle smoke gate: `scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs`

The hook wrapper reads hook stdin JSON but never prints raw stdin. It calls `node packages/petctl/dist/cli.js notify` and relies on `AGENT_DESKTOP_PET_INSTANCE_ID` for routing to the current cat.

## Boundaries

V3.4 does not:

- guarantee Codex internal reasoning exact mapping.
- provide `ModelThinkingStart` / `ModelThinkingEnd`.
- parse terminal text.
- use `transcript_path` as a stable interface.
- implement OS-level Codex window binding.
- verify all Codex workflows.

## Hook Trust

Non-managed Codex hooks must be reviewed and trusted through `/hooks`.

`--dangerously-bypass-hook-trust` is allowed only for explicit local smoke or investigation and must not be documented as the normal user path.

## Status

Fixture-level hook wrapper implementation is complete.

Real Codex lifecycle acceptance remains blocked until an operator runs `/hooks`, trusts the project hooks, and records real lifecycle evidence.
