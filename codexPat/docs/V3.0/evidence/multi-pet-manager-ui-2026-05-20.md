# V3.0 Phase 3.5 Multi-pet Manager UI Evidence

status: passed  
date: 2026-05-20  
desktop app commit: `8872bf82` with current worktree changes for Phase 3.5 manager UI  
build artifact path: `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`

## Scope

This evidence covers V3.0 Phase 3.5: Multi-pet Manager UI.

Phase 3.5 implements:

- Settings page Multi-pet Manager section.
- Instance list with `displayName`, `instanceId`, `windowLabel`, `currentState`, read-only appearance, default marker, visibility, routing status and `lastEventAt`.
- Extra pet actions: rename, show/hide, reset position, detach, copy env export, copy notify template.
- Default pet actions: show/hide and reset position; detach disabled.
- Tauri commands:
  - `list_pet_instances`
  - `rename_pet_instance`
  - `detach_pet_instance`
  - `create_pet_instance`
  - `set_pet_instance_visible`
  - `reset_pet_instance_position`
- Routed event runtime sync for extra pets: `currentState` and `lastEventAt` update in the registry.

Phase 3.5 does not implement:

- Real two-Codex-session verification.
- Command execution UI.
- Notification center UI.
- Per-instance deep diagnostics.
- Asset Pack v1 or appearance switching.
- OS-level Codex window binding.
- MCP, Windows, USB, 3D, photo customization or production signing.

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm --filter desktop check` | pass | TypeScript desktop check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript CLI check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 14 petctl tests passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |
| `pnpm run doctor` | pass with non-blocking WARN | rustup absent, external network probes unreachable, and sandboxed local dev listen check warned; doctor completed with no hard failures. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | PetEvent schema was not modified in Phase 3.5. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 protocol tests passed. |

## Created Instance IDs

| Pet | instanceId | displayName |
| --- | --- | --- |
| A | `codex_1779245860399` | `Codex A` |
| B | `codex_1779245860737` | `Codex B` |

## Manager List Result

`petctl list --json` returned default + A + B:

```text
default / Agent Desktop Pet / visible / idle
codex_1779245860399 / Codex A / visible / idle
codex_1779245860737 / Codex B / visible / idle
```

After routing `manager smoke` to A, `petctl list --json` returned:

```text
codex_1779245860399 / Codex A / visible / success / lastEventAt=1779245861747
codex_1779245860737 / Codex B / visible / idle
```

This proves manager data is consistent with instance-scoped routing and registry runtime sync.

## UI Command Coverage

| Manager action | Result | Notes |
| --- | --- | --- |
| List default + A + B | pass | Manager uses the same `list_pet_instances` backing data as `petctl list`. |
| Rename | implemented | `rename_pet_instance` validates `instanceId` and `displayName`; invalid names return `display_name_invalid`. Direct click smoke is deferred to final visual acceptance. |
| Show / hide | implemented | `set_pet_instance_visible` only affects the target instance and persists `visible`. Hidden pets remain routable and update state while hidden. Direct click smoke is deferred to final visual acceptance. |
| Reset position | implemented | `reset_pet_instance_position` moves only the target instance to a primary-screen safe position with an offset for extra pets. Direct click smoke is deferred to final visual acceptance. |
| Copy env export | implemented | Copy-only UI text: `export AGENT_DESKTOP_PET_INSTANCE_ID=<instanceId>`. No token/config/workspace path included. |
| Copy notify template | implemented | Copy-only UI text includes `--instance <instanceId>`. No token/config/workspace path included. |
| Detach extra pet | implemented | `detach_pet_instance` closes the target window, removes registry entry and prevents restart restore. Direct click smoke is deferred to final visual acceptance. |
| Detach default guard | implemented | UI disables default detach; command returns `default_instance_cannot_detach`. |

## Command Execution Guard

The settings UI only calls `navigator.clipboard.writeText` for copy buttons. It does not execute shell, `petctl`, `curl`, `node`, `osascript` or any system command.

## Routing Regression Result

| Scenario | Result |
| --- | --- |
| `node packages/petctl/dist/cli.js notify --instance A --level success --title "manager smoke"` | accepted `evt_1779245861747_1`; A state updated to `success`; B remained `idle`. |
| `node packages/petctl/dist/cli.js notify --level success --title "legacy manager smoke"` | accepted `evt_1779245862064_2`; legacy default route preserved. |

Diagnostics accepted summaries included:

```text
targetInstanceId=codex_1779245860399
targetWindowLabel=pet-codex_1779245860399
titlePreview=manager smoke
```

## Persistence Result

status: implementation complete; direct restart visual smoke deferred to V3.0 final acceptance.

The implementation writes rename, visibility, reset position and detach changes to `settings.json`. Detach removes the instance from `petInstances`, so it will not restore on restart.

## Forbidden Data Visibility Check

Manager UI and copied commands do not include:

- token
- token file path
- config path
- full workspace path
- raw payload
- metadata full dump

`workspaceLabel` and `workspaceHash` remain stored/displayed only as safe label/hash values if present; full workspace path is not stored.

## Allowed Claims

```text
Phase 3.5 complete: multi-pet manager UI ready.
```

## Forbidden Claims

```text
V3.0 ready
Multi-instance Codex local workflow verified
OS-level Codex window binding ready
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
command execution UI ready
notification center ready
per-instance deep diagnostics ready
Asset Pack v1 ready
```
