# V3.7 Development Plan

status: passed

date: 2026-05-25

## Goal

V3.7 introduces a scoped project-owned monitor for wrapper-launched `codex exec --json` sessions. It maps structured JSONL stdout event types to desktop pet state, especially failure-to-error mapping.

Strategy update on 2026-05-26: V3.7 is the current recommended Codex exec monitoring path. V3.6 remains historical blocked evidence and is deprecated as the active hook-only monitoring strategy.

## Scope Boundary

V3.7 is:

- project-owned structured JSONL monitoring.
- limited to `petctl codex launch --monitor jsonl`.
- limited to wrapper-launched `codex exec --json` sessions.
- routed through existing PetEvent / HTTP / Event Bridge.
- current recommended Codex exec monitoring path.

V3.7 is not:

- official Codex hook lifecycle evidence.
- V3.6 hook-only acceptance.
- interactive Codex TUI coverage.
- OS-level Codex window binding.
- all Codex workflows verification.
- exact Codex internal reasoning mapping.

## Implementation Plan

Add `--monitor jsonl` to `petctl codex launch`:

```bash
petctl codex launch --monitor jsonl --name "<cat>" -- codex exec --json "<prompt>"
```

The default remains `--monitor none`, preserving existing behavior.

When JSONL monitoring is enabled:

- attach a Codex PetInstance as today.
- inject `AGENT_DESKTOP_PET_INSTANCE_ID`.
- read child stdout as JSONL.
- parse only JSON object `type` and safe field names.
- never record raw JSONL, prompt text, tool command text, token, Authorization, transcript path, full local paths, workspace path, or config path.
- notify the target instance through existing `notify()`.

## State Mapping

| JSONL event type | Pet state | Notes |
| --- | --- | --- |
| `thread.started` | marker-only | Does not emit pet state or prove success. |
| `turn.started` | `thinking` | Clears current-turn error flag. |
| `item.started` | `running` | Marks structured activity. |
| `item.completed` | marker / keep current | Does not infer success. |
| `turn.completed` | `success` | Only if current turn has no error. |
| `turn.failed` | `error` | Sets current-turn error flag. |
| `error` | `error` | Sets current-turn error flag. |

`turn.completed` is only a non-error turn completion marker. It is not a business quality success signal.

## Risk Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| V3.6 false-green | Medium | V3.7 docs must state V3.6 remains historical blocked and not converted to passed. |
| Terminal text parsing drift | Medium | Parser only accepts JSON object event types; invalid/non-JSON lines are ignored and not interpreted. |
| Security leakage | Medium | Evidence and diagnostics record event types, safe field names, mapped states, and accepted results only. |
| Unsupported JSONL failure shape | High | If no `turn.failed` or `error` is observed, V3.7 is blocked. |

overall risk: Medium

go / no-go: completed

## Deliverables

- `petctl codex launch --monitor jsonl`.
- `scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs`.
- `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-2026-05-25.md`.
- `docs/V3.7/v3_7-final-acceptance-report.md`.
