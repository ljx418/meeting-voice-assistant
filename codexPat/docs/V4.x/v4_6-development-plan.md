# V4.6 Managed Session Startup Diagnostics Development Plan

status: completed

date: 2026-05-27

## Scope

V4.6 hardens managed Codex session startup diagnostics and user-facing guidance for wrapper-launched scenarios.

Allowed scope:

- desktop health preflight
- hooks config check
- hook wrapper script check
- Codex CLI check
- clear `/hooks` trust instruction
- stable reasonCode output

Out of scope:

- new state mapping
- new TUI lifecycle claim
- OS-level binding readiness
- already-open Codex window monitoring

## Implementation

- `petctl codex doctor` reports sanitized diagnostics for Codex CLI, hook config, hook wrapper, binding env, hook trust, token, and desktop health.
- Managed TUI hooks startup runs strict diagnostics before creating the PetInstance.
- Stable reason codes include `desktop_not_running`, `hook_config_missing`, `hook_wrapper_missing`, `hook_trust_required`, `codex_not_found`, and `binding_env_missing`.

## Drift And False-Green Risk

| Risk | Level | Mitigation |
| --- | --- | --- |
| Diagnostics treated as lifecycle state mapping | Low | Claim is diagnostics only. |
| Hook trust warning treated as passed lifecycle evidence | Low | Evidence records it as a warning/instruction. |
| Raw local paths or tokens printed | Low | Diagnostic details are sanitized. |

No High risk remains for V4.6.
