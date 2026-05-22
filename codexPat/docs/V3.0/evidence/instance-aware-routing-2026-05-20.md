# V3.0 Phase 3.3 Instance-aware Event Routing Evidence

status: passed  
date: 2026-05-20  
desktop app commit: `8872bf82` with current worktree changes for Phase 3.3 routing  
build artifact path: `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`

## Scope

This evidence covers V3.0 Phase 3.3: Instance-aware Event Routing.

Phase 3.3 implements:

- `POST /api/instances/:instanceId/events`.
- `GET /api/instances`.
- Auth before instance lookup for instance-scoped endpoints.
- `instanceId` format validation.
- `404 instance_not_found` for valid but unknown instances.
- Targeted Tauri event emission for known instance windows.
- Frontend filtering by `targetInstanceId`.
- Diagnostics summaries with `targetInstanceId` and `targetWindowLabel`.

Phase 3.3 does not implement:

- `petctl attach codex`.
- `petctl notify --instance`.
- Multi-Codex-session verification.
- Per-instance diagnostics endpoint.
- Per-instance rate limit.
- OS-level Codex window binding.
- MCP, Windows, USB, 3D, photo customization or production signing.

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm --filter desktop check` | pass | TypeScript check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | 5 Rust tests passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |
| `pnpm run doctor` | warn | No hard failures. WARN: rustup not installed, external network checks unreachable, sandbox cannot bind 127.0.0.1:1420. These do not block cached local check/build. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | TypeScript protocol check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 protocol tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript CLI check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 6 petctl tests passed. |

## Used Instance IDs

Temporary local app config was used to create two route smoke instances:

| Pet | instanceId | windowLabel | name |
| --- | --- | --- | --- |
| default | `default` | `main` | `Agent Desktop Pet` |
| A | `pet_route_a` | `pet-pet_route_a` | `Route Cat A` |
| B | `pet_route_b` | `pet-pet_route_b` | `Route Cat B` |

The original local `settings.json` was backed up to:

```text
~/Library/Application Support/com.agentdesktoppet.desktop/settings.phase3.3-backup.json
```

## HTTP Smoke

| Scenario | Command / endpoint | Result | Evidence |
| --- | --- | --- | --- |
| Health | `GET /api/health` | pass | Returned `ok=true`, listen address `127.0.0.1:17321`. |
| `GET /api/instances` without token | pass | Returned `401 auth_missing`. |
| `GET /api/instances` with token | pass | Returned default, `pet_route_a`, `pet_route_b`. |
| Legacy `petctl notify` | `node packages/petctl/dist/cli.js notify --level success --title "legacy default smoke"` | pass | Accepted `evt_1779241933920_3`. |
| Legacy raw HTTP | `POST /api/events` | pass | Accepted `evt_1779241933631_1`. |
| Instance A routing | `POST /api/instances/pet_route_a/events` | pass | Accepted `evt_1779241933882_2`, diagnostics target `pet_route_a` / `pet-pet_route_a`. |
| Instance B routing | `POST /api/instances/pet_route_b/events` | pass | Accepted `evt_1779241934068_4`, diagnostics target `pet_route_b` / `pet-pet_route_b`. |
| Unknown instance | `POST /api/instances/not-found/events` | pass | Returned `404 instance_not_found`. |
| Invalid instance path | `POST /api/instances/../../bad/events` with `--path-as-is` | pass | Returned `400 instance_id_invalid`; diagnostics did not echo `../../bad`. |
| No token known instance | `POST /api/instances/pet_route_a/events` without token | pass | Returned `401 auth_missing`. |
| No token unknown instance | `POST /api/instances/not-found/events` without token | pass | Returned `401 auth_missing`, not `404`. |
| Invalid level | `POST /api/instances/pet_route_a/events` with `level=nope` | pass | Returned `400 whitelist_invalid`, `reasonField=level`. |
| Invalid sound path | `POST /api/instances/pet_route_a/events` with `sound=../../x.wav` | pass | Returned `400 whitelist_invalid`, `reasonField=sound`; diagnostics did not echo path. |
| Rate limit | 14 rapid `running` events to `pet_route_a` | pass | First 10 returned `202`; last 4 returned `429 rate_limited`; diagnostics target remained `pet_route_a`. |

## Diagnostics Evidence

Diagnostics accepted event summaries include:

```text
sourceId=route.rate
level=running
targetInstanceId=pet_route_a
targetWindowLabel=pet-pet_route_a
status=202
```

Diagnostics rejected event summaries include:

```text
reasonCode=rate_limited
reasonField=rate_limit
targetInstanceId=pet_route_a
targetWindowLabel=pet-pet_route_a
```

Redaction check over rejected event summary fields found none of:

```text
../../bad
../../x.wav
file://
https://
http://
/tmp/
/Users/
C:\Users
api-token
Application Support
```

## Acceptance Notes

- Legacy `/api/events` and legacy `petctl notify` remain compatible.
- Instance-scoped endpoint accepts valid known instances.
- Unknown instance and invalid instance id are rejected before event execution.
- Auth is checked before instance lookup.
- `targetInstanceId` / `targetWindowLabel` are routing metadata, not PetEvent schema fields.
- PetEvent schema was not changed.
- Per-instance diagnostics endpoint is not implemented.
- Per-instance rate limit is not implemented.

Manual visual confirmation that only the target cat changed is deferred to V3.0 final acceptance, consistent with the current V3.0 acceptance policy.

## Allowed Claims

```text
Phase 3.3 complete: instance-aware event routing ready.
```

## Forbidden Claims

```text
V3.0 ready
multi-instance Codex verified
petctl attach ready
petctl notify --instance ready
OS-level Codex window binding ready
per-instance diagnostics ready
per-instance rate limit ready
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```
