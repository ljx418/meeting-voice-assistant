# V3.1 Phase 4 Evidence：Runtime Regression Harness

status: passed

date: 2026-05-21

commit: 8872bf82
lastRecheckedAt: 2026-05-22 Asia/Shanghai
lastRecheckedCommit: 26101b87
freezeAuditCheckedAt: 2026-05-22 Asia/Shanghai
freezeAuditCommit: 96b6a393

script path: `scripts/v3_1_runtime_smoke.mjs`

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | pass-with-warn | 无 hard failure。WARN：未安装 rustup；网络探测不可达；沙箱下 127.0.0.1:1420 listen EPERM。 |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript check passed。 |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 18 tests passed。 |
| `pnpm --filter desktop check` | pass | `tsc --noEmit` passed。 |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed。 |
| `pnpm --filter desktop build` | pass | Vite production build passed。 |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` generated at `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`。 |

## Runtime Smoke Summary

| Field | Value |
| --- | --- |
| preExistingInstanceCount | 3 |
| createdSmokeInstances | 9 smoke instances created during run `1779355372867-933cbe` |
| cleanupResult | passed |

## 2026-05-22 Final Acceptance Re-run

| Field | Value |
| --- | --- |
| command | `node scripts/v3_1_runtime_smoke.mjs` |
| result | passed |
| runId | `1779414750926-4ac98b` |
| preExistingInstanceCount | 3 |
| createdSmokeInstances | 9 |
| cleanupResult | passed |
| notes | Legacy route, instance route, unknown/invalid instance rejection, invalid sound redaction and hard limit cases passed. |

## 2026-05-22 Freeze Evidence Audit Re-run

| Field | Value |
| --- | --- |
| command | `node scripts/v3_1_runtime_smoke.mjs` |
| result | passed |
| runId | `1779438063505-3601c8` |
| preExistingInstanceCount | 3 |
| createdSmokeInstances | 9 |
| cleanupResult | passed |
| notes | Health, attach A/B, list, instance routing, env routing, explicit instance override, legacy route, unknown/invalid instance rejection, invalid sound redaction, hard limit, cleanup and detached-instance 404 all passed. |

## Runtime Cases

| Case | Result | Notes |
| --- | --- | --- |
| health API | passed | Desktop app reachable on `127.0.0.1:17321`。 |
| attach A/B | passed | Created `codex_1779355373540` and `codex_1779355374066`。 |
| petctl list default + A + B | passed | `default=true A=true B=true`。 |
| notify --instance A | passed | Accepted and routing check passed。 |
| notify --instance B | passed | Accepted and routing check passed。 |
| env routes to A | passed | `AGENT_DESKTOP_PET_INSTANCE_ID=A` routed to A。 |
| explicit --instance overrides env | passed | `--instance B` overrode env A。 |
| legacy notify default route | passed | Legacy route did not change A/B state。 |
| unknown instance 404 | passed | `reasonCode=instance_not_found`。 |
| invalid instanceId safe error | passed | `reasonCode=instance_id_invalid`。 |
| env not-found no fallback | passed | `reasonCode=instance_not_found`。 |
| invalid sound redaction | passed | Raw HTTP returned 400 and did not echo forbidden input in script summary。 |
| hard limit 13th rejected | passed | Filled to 12 total pets, 13th returned `instance_limit_reached`。 |
| cleanup smoke instances | passed | All 9 created Smoke instances detached。 |
| notify detached instance 404 | passed | Detached A returned `instance_not_found`。 |

## Security Redaction

| Forbidden text | Result |
| --- | --- |
| `AGENT_DESKTOP_PET_TOKEN=` | passed |
| `Authorization: Bearer` | passed |
| `api-token.json` | passed |
| `Application Support` | passed |
| `raw payload` | passed |
| `../../x.wav` | passed |
| `file://` | passed |
| `/Users/` | passed |

## Skipped / Blocked Cases

- None.

## Allowed Claim

仅当本 evidence status 改为 `passed` 后，才允许声明：

```text
V3.1 Phase 4 complete: repeatable runtime regression smoke ready.
```

## Forbidden Claims

```text
V3.1 ready
Windows ready
cross-platform ready
MCP ready
USB ready
production signed release ready
OS-level Codex window binding ready
all Codex workflows verified
per-instance queue ready
```
