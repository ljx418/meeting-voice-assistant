# V3.2 Final Acceptance Report

status: passed

date: 2026-05-23

commit: b304a1b0

## Scope

V3.2 final acceptance passed for scoped Agent Integration Readiness closure.

This closure covers MCP adapter runtime evidence, third-party contract v3 runtime evidence, V3.1 runtime regression rerun, automatic checks, security redaction scan, claim consistency scan, and artifact check.

Claude Code hook real verification remains deferred. No Claude Code hook claim is made.

## Evidence Gate

| Evidence | Status | Notes |
| --- | --- | --- |
| `docs/V3.1/v3_1-final-acceptance-report.md` | passed | V3.1 baseline. |
| `docs/V3.2/evidence/mcp-adapter-smoke-2026-05-23.md` | passed | MCP adapter minimal runtime smoke passed. |
| `docs/V3.2/evidence/third-party-contract-v3-smoke-2026-05-23.md` | passed | Third-party contract v3 smoke passed. |
| `docs/V3.2/evidence/claude-code-hook-smoke-2026-05-23.md` | deferred | Real Claude Code hook lifecycle not run. |

## MCP Adapter Smoke Result

`node scripts/v3_2_mcp_adapter_smoke.mjs` passed with run id `1779548637375-10bd56`.

Passed coverage:

- health check before smoke.
- `pet_notify` default route accepted and did not alter target instance.
- `pet_notify` with `instanceId` updated only target instance.
- `pet_list_instances` returned sanitized list.
- `pet_get_capabilities` returned public summary.
- `pet_get_state` returned target state.
- unknown instance returned `instance_not_found`.
- invalid instance returned `instance_id_invalid`.
- invalid sound failed safely before bridge.
- temporary instance cleanup passed.
- smoke security scan passed.

Allowed scoped claim:

```text
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
```

## Third-party Contract v3 Smoke Result

`node scripts/v3_2_third_party_contract_smoke.mjs` passed with run id `1779548639344-b9d16e`.

Passed coverage:

- health check before smoke.
- missing token returned `401 auth_missing`.
- invalid token returned `401 auth_invalid`.
- `/api/events` legacy default route accepted.
- legacy default route did not alter target instance.
- `/api/instances/:instanceId/events` accepted and updated target.
- `petctl attach` created a smoke instance.
- `petctl notify --instance` updated target.
- unknown instance returned `instance_not_found`.
- invalid instance returned `instance_id_invalid`.
- hard limit returned `instance_limit_reached`.
- invalid sound redaction passed.
- curl, Node, and Python local contract examples passed.
- temporary instance cleanup passed.
- smoke security scan passed.

Allowed scoped claim:

```text
V3.2 third-party contract v3 smoke passed.
```

## Claude Code Hook Result

Real Claude Code hook lifecycle was not run in this closure.

Current result:

```text
Claude Code hook real verification remains deferred.
```

No Claude Code hook smoke claim is made.

## V3.1 Runtime Smoke Rerun

`node scripts/v3_1_runtime_smoke.mjs` passed with run id `1779548660924-2de5ae`.

Key results:

- desktop health passed.
- A/B instance attach passed.
- instance routing passed.
- environment instance routing passed.
- explicit instance override passed.
- legacy default route passed.
- unknown instance and invalid instance rejection passed.
- invalid sound redaction passed.
- hard limit rejection passed.
- cleanup passed.
- security redaction scan passed.

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | pass-with-warn | No hard failure. Warnings: rustup missing, network probes unreachable, sandbox dev-server listen EPERM. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | passed | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | passed | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed | 18 tests passed. |
| `pnpm --filter @agent-desktop-pet/pet-mcp check` | passed | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-mcp test` | passed | 7 tests passed. |
| `pnpm --filter desktop check` | passed | TypeScript check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | passed | Rust check passed. |
| `pnpm --filter desktop build` | passed | Vite production build passed. |
| `pnpm --filter desktop tauri build -b app` | passed | macOS local app bundle generated. |

## Security Redaction Scan

Passed.

Evidence and smoke summaries were checked for sensitive data leakage. No token values, auth header values, request-body dumps, config file names, workspace locations, full user-local paths, or rejected sound input were included in the accepted smoke summaries.

## Claim Consistency Scan

Passed.

Forbidden claims appear only in forbidden, deferred, or not-ready contexts:

```text
MCP ready
Claude Code integration verified
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
all Codex workflows verified
OS-level Codex window binding ready
per-instance queue ready
```

## Artifact Check

`git status --short` was run. Generated package-local `dist`, `target`, and `node_modules` artifacts are not intended for commit.

Tracked and new source/doc changes are limited to V3.2 docs, integration reference docs, package metadata, `packages/pet-mcp`, and V3.2 smoke scripts. The wider workspace still contains unrelated dirty files outside this project; they were not modified for this closure.

## Allowed Claims

```text
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
V3.2 third-party contract v3 smoke passed.
V3.2 final acceptance passed for scoped Agent Integration Readiness closure.
```

## Forbidden Claims

```text
MCP ready
Claude Code integration verified
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
all Codex workflows verified
OS-level Codex window binding ready
per-instance queue ready
```

## Final Decision

V3.2 final acceptance passed for scoped Agent Integration Readiness closure.

MCP adapter runtime smoke, third-party contract v3 smoke, V3.1 runtime regression, automatic checks, security redaction scan, claim consistency scan, and artifact check are complete.

Claude Code hook real verification remains deferred and no Claude Code claim is made.
