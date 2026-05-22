# V3.1 Phase 5 Evidence：Local App Migration and Backup

status: passed

date: 2026-05-21

commit: 26101b87
lastRecheckedAt: 2026-05-22 Asia/Shanghai
lastRecheckedCommit: 26101b87
freezeAuditCheckedAt: 2026-05-22 Asia/Shanghai
freezeAuditCommit: 96b6a393

## Config Audit Result

| Item | Result | Notes |
| --- | --- | --- |
| `node scripts/v3_1_config_audit.mjs` | passed | Human-readable output used redacted `~/...` path and printed no token or raw settings. |
| `node scripts/v3_1_config_audit.mjs --json` | passed | JSON output used redacted `~/...` path and printed no token or raw settings. |

## 2026-05-22 Final Acceptance Re-run

| Item | Result | Notes |
| --- | --- | --- |
| `node scripts/v3_1_config_audit.mjs` | passed | Output remained redacted and printed no token or raw settings. |
| `node scripts/v3_1_config_audit.mjs --json` | passed | JSON output remained redacted and printed no token or raw settings. |

## 2026-05-22 Freeze Evidence Audit Re-run

| Item | Result | Notes |
| --- | --- | --- |
| `node scripts/v3_1_config_audit.mjs` | passed | Output used redacted `~/Library/...` path and printed no token, Authorization header, raw settings or full user path. |
| `node scripts/v3_1_config_audit.mjs --json` | passed | JSON output used redacted `~/Library/...` path and printed no token, Authorization header, raw settings or full user path. |

## Detected Config Paths

| Path | Source | Notes |
| --- | --- | --- |
| `~/Library/Application Support/com.agentdesktoppet.desktop/settings.json` | Tauri `app_config_dir()` + `settings.json` | macOS path, redacted with `~` |
| `~/Library/Application Support/com.agentdesktoppet.desktop/api-token.json` | `petctl` token lookup + bridge token path | macOS path, redacted with `~` |

## Settings Summary

| Field | Result |
| --- | --- |
| settings exists | true |
| settings readable | true |
| pet instance count | 2 |
| has muted | true |
| has position | true |
| has visible | true |
| has profiles | true |
| has default profile | true |

## Redaction Checks

| Check | Result | Notes |
| --- | --- | --- |
| token file existence check | passed | `tokenFile.exists=true`; token value not printed. |
| token redaction check | passed | `tokenValuePrinted=false`. |
| raw settings redaction check | passed | `rawSettingsPrinted=false`. |
| workspace path redaction check | passed | No workspace path printed. |
| full user path redaction check | passed | `fullUserPathPrinted=false`; path shown as `~/Library/...`. |
| Authorization header redaction check | passed | `authorizationHeaderPrinted=false`. |

## Documentation Review

| Item | Result | Notes |
| --- | --- | --- |
| migration doc review | passed | States unsigned local app, not production release. |
| backup checklist review | passed | Distinguishes source/config from rebuildable artifacts. |
| troubleshooting coverage | passed | Covers token, port, missing cat, config damage, Gatekeeper and build path. |
| README entry | passed | README links to guide without duplicating it. |
| ops cross references | passed | ops docs link to this guide and avoid large duplicated sections. |

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | pass-with-warn | No hard failures. WARN: rustup missing, network probes unreachable, local dev server listen EPERM in sandbox. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | passed | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | passed | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed | 18 tests passed. |
| `pnpm --filter desktop check` | passed | `tsc --noEmit` passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | passed | Rust check passed. |
| `pnpm --filter desktop build` | passed | Vite production build passed. |
| `pnpm --filter desktop tauri build -b app` | passed | `.app` generated. |

## Manual Review Checklist

- Migration doc does not describe unsigned local app as production release.
- Backup checklist includes source directory, lockfiles, docs, settings.json and personal secure backup of api-token.json.
- Rebuildable artifacts are listed as not requiring backup.
- Config audit output does not include token, raw settings, Authorization header, full `/Users/<name>/...` path or full workspace path.
- README only links to the guide.
- active gap and drawio agree on Phase 5 state.

## Allowed Claim

Only if this evidence status is `passed`:

```text
V3.1 Phase 5 complete: local app migration and backup guidance ready.
```

## Forbidden Claims

```text
V3.1 ready
Windows ready
cross-platform ready
MCP ready
USB ready
production signed release ready
notarized release ready
auto update ready
OS-level Codex window binding ready
all Codex workflows verified
per-instance queue ready
```
