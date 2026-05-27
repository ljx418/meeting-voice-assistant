# V3.7 Final Acceptance Report

status: passed

date: 2026-05-25

commit: 9c9cd634

## Scope

V3.7 validates a project-owned structured JSONL monitor for wrapper-launched `codex exec --json` sessions.

Strategy update on 2026-05-26: V3.7 is the current recommended Codex exec monitoring path. V3.6 remains historical blocked evidence and is deprecated as the active hook-only monitoring strategy.

## Evidence Gate

Passed:

- `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-2026-05-25.md`

## V3.6 Boundary

V3.6 remains historical blocked evidence:

```text
V3.6 final acceptance blocked on real PostToolUse failure evidence.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

V3.7 is project-owned JSONL monitoring and is not official Codex hook lifecycle evidence.

## Runtime Smoke

| Scenario | Result |
| --- | --- |
| simple answer | passed |
| tool success | passed |
| tool failure | passed via structured `turn.failed` |
| security redaction scan | passed |
| claim scan | passed |

`thread.started` was treated as marker-only. It was not used to emit an `idle` pet state.

Command:

```bash
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

Result:

```text
status=passed
runId=1779757764038-0596be
```

## Regression Results

| Command | Result |
| --- | --- |
| `node scripts/v3_1_runtime_smoke.mjs` | passed |
| `node scripts/v3_2_mcp_adapter_smoke.mjs` | passed |
| `node scripts/v3_2_third_party_contract_smoke.mjs` | passed |
| `node scripts/v3_3_codex_window_binding_smoke.mjs` | passed |
| `node scripts/v3_4_codex_hook_fixture_smoke.mjs` | passed |
| `pnpm run doctor` | passed with warnings, no hard failures |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp test` | passed |
| `pnpm --filter desktop check` | passed |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | passed |
| `pnpm --filter desktop build` | passed |
| `pnpm --filter desktop tauri build -b app` | passed |

Doctor warnings were environment warnings only: rustup missing, network endpoints unreachable, and sandbox inability to listen on the Vite port while the dev app was already running.

## Security Scan

Passed. Evidence and smoke output did not record:

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

## Claim Scan

Passed. Forbidden claims are not used as ready/passed claims.

## PRD Conformance Note

The active PRD matches the V3.7 boundary: JSONL monitoring is a project-owned source and does not change V3.6 hook-only status.

Known non-blocking naming risk: JSON CLI output stores the sanitized monitor summary at `raw.monitor`. This is not raw JSONL. It contains only safe event type and mapped-state summary, but the field name can be confusing and should be considered for a future compatibility-reviewed rename.

## Final Decision

V3.7 final acceptance passed for scoped Codex exec JSONL monitor state mapping.

Current strategy decision: use V3.7 JSONL monitor as the primary Codex exec state monitoring path for supported wrapper-launched `codex exec --json` sessions.

## Allowed Claim

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```

## Forbidden Claims

```text
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
OS-level Codex window binding ready
```
