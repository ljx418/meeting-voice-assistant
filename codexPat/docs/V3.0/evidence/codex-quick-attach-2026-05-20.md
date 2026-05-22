# V3.0 Phase 3.4 Codex Quick Attach Evidence

status: passed  
date: 2026-05-20  
desktop app commit: `8872bf82` with current worktree changes for Phase 3.4 quick attach  
build artifact path: `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`

## Scope

This evidence covers V3.0 Phase 3.4: Codex Quick Attach.

Phase 3.4 implements:

- `POST /api/instances` for server-generated PetInstance creation.
- `petctl attach codex`.
- `petctl list`.
- `petctl notify --instance`.
- `AGENT_DESKTOP_PET_INSTANCE_ID` routing.
- Explicit `--instance` override over environment routing.
- JSON stdin support with `--instance`.
- Codex `SKILL.md` instance-aware guidance.

Phase 3.4 does not implement:

- Real two-Codex-session verification with operator visual acceptance.
- OS-level Codex window binding.
- MCP.
- Claude Code verification.
- Windows, USB, 3D, photo customization or production signing.

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript CLI check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 14 petctl tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript desktop check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | 5 Rust tests passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |
| `pnpm run doctor` | warn | No hard failures. WARN: rustup not installed, external network checks unreachable, sandbox cannot bind 127.0.0.1:1420. These do not block cached local check/build. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | TypeScript protocol check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 protocol tests passed. |

## Attach A/B Results

| Pet | instanceId | windowLabel | displayName |
| --- | --- | --- | --- |
| A | `codex_1779243995528` | `pet-codex_1779243995528` | `Codex A` |
| B | `codex_1779243995958` | `pet-codex_1779243995958` | `Codex B` |

Both were created by:

```bash
node packages/petctl/dist/cli.js attach codex --name "Codex A" --json
node packages/petctl/dist/cli.js attach codex --name "Codex B" --json
```

The response included `instanceId`, `displayName`, `windowLabel`, and an export command. No token was printed.

## petctl list Result

`node packages/petctl/dist/cli.js list` and `node packages/petctl/dist/cli.js list --json` returned:

- default pet: `default` / `main`.
- Codex A: `codex_1779243995528`.
- Codex B: `codex_1779243995958`.

No token, config path, full workspace path, raw payload or metadata dump was printed.

## Routing Smoke

| Scenario | Command | Result |
| --- | --- | --- |
| Env routing | `AGENT_DESKTOP_PET_INSTANCE_ID=A node packages/petctl/dist/cli.js notify --level success --title "A success"` | accepted `evt_1779243997763_1`; diagnostics target A. |
| Explicit `--instance` routing | `node packages/petctl/dist/cli.js notify --instance B --level error --title "B error"` | accepted `evt_1779243998364_2`; diagnostics target B. |
| Explicit overrides env | `AGENT_DESKTOP_PET_INSTANCE_ID=A node packages/petctl/dist/cli.js notify --instance B --level success --title "B override success"` | accepted `evt_1779243998801_3`; diagnostics target B. |
| Legacy default | `node packages/petctl/dist/cli.js notify --level success --title "legacy default"` | accepted `evt_1779243999157_4`; diagnostics target is null/default path. |
| JSON stdin with instance | `... | node packages/petctl/dist/cli.js notify --instance A --json` | accepted `evt_1779243999504_5`; diagnostics target A. |

## Error Scenarios

| Scenario | Result |
| --- | --- |
| `--instance not-found` | rejected with `instance_not_found`; no fallback to default. |
| `--instance ../../bad` | rejected locally with `instance_id_invalid`; no HTTP request and no fallback to default. |
| `AGENT_DESKTOP_PET_INSTANCE_ID=not-found` | rejected with `instance_not_found`; no fallback to default. |
| invalid sound path | rejected before execution; no target state change. |
| no token attach | raw HTTP `POST /api/instances` without token returned `401 auth_missing`. |
| no token list | raw HTTP `GET /api/instances` without token returned `401 auth_missing`. |
| displayName length 41 | rejected with `display_name_invalid`. |
| displayName containing newline/control character | rejected; raw invalid JSON path returned `schema_invalid`, CLI validation returns `display_name_invalid`. |

## Diagnostics Evidence

Accepted event summaries included:

```text
sourceId=codex.local
level=running
titlePreview=JSON instance smoke
targetInstanceId=codex_1779243995528
targetWindowLabel=pet-codex_1779243995528
```

```text
sourceId=custom.local
level=success
titlePreview=B override success
targetInstanceId=codex_1779243995958
targetWindowLabel=pet-codex_1779243995958
```

Legacy default event summary had no `targetInstanceId`, preserving the legacy default path.

Rejected event summaries included `auth_missing`, `display_name_invalid`, `schema_invalid`, and `instance_not_found`.

Redaction check over rejected summary fields found none of:

```text
../../x.wav
../../bad
file://
https://
http://
/tmp/
/Users/
C:\Users
api-token
Application Support
```

## Optional Two-Codex-Session Smoke

status: not-run

Reason: this phase completed CLI/HTTP quick attach and instance-scoped petctl routing. The user-facing two-Codex-session visual verification is intentionally not claimed here unless operator visual acceptance is completed.

## Allowed Claims

```text
Phase 3.4 complete: Codex quick attach and instance-scoped petctl routing ready.
```

## Forbidden Claims

```text
V3.0 ready
Multi-instance Codex local workflow verified for tested local Codex session scenarios
all Codex sessions globally verified
OS-level Codex window binding ready
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```
