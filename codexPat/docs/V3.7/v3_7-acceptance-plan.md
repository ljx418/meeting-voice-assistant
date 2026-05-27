# V3.7 Acceptance Plan

status: passed

date: 2026-05-25

## Required Runtime Smoke

Run:

```bash
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

The smoke must cover:

| Scenario | Required structured signal | Required state |
| --- | --- | --- |
| simple answer | `turn.started`, `turn.completed` | `thinking -> success` or `idle` |
| tool success | `item.started`, `turn.completed` | `running -> success` |
| tool failure | `turn.failed` or `error` | `error` |

If the failure scenario does not expose `turn.failed` or `error` as structured JSONL event types, V3.7 is blocked. The smoke must not fall back to terminal text parsing.

`thread.started` is marker-only. It may be recorded as a safe event type but must not be treated as an emitted `idle` state.

## Security Acceptance

Evidence and smoke output must not contain:

```text
token
Authorization
raw JSONL payload
prompt text
tool command text
transcript_path
full /Users path
workspace path
config path
api-token.json
```

Evidence may record:

```text
event type
safe field names
mapped state
target route
diagnostics accepted result
```

## Regression

Before final acceptance, run:

```bash
node scripts/v3_1_runtime_smoke.mjs
node scripts/v3_2_mcp_adapter_smoke.mjs
node scripts/v3_2_third_party_contract_smoke.mjs
node scripts/v3_3_codex_window_binding_smoke.mjs
node scripts/v3_4_codex_hook_fixture_smoke.mjs
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/pet-mcp check
pnpm --filter @agent-desktop-pet/pet-mcp test
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop build
pnpm --filter desktop tauri build -b app
```

## Final Acceptance

V3.7 can pass only when:

- V3.6 remains explicitly blocked.
- JSONL monitor smoke passes for simple answer, tool success, and tool failure.
- tool failure maps to `error` from structured `turn.failed` or `error`.
- no sensitive output is recorded.
- no forbidden claim is used as ready/passed.
- automatic checks have no hard failure.
