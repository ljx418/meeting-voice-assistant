# V3.0 Phase 3.2 Multi-instance Foundation Evidence

status: passed  
date: 2026-05-19  
operator: manual visual acceptance deferred to V3.0 final acceptance  
desktop app commit: `8872bf82` with current worktree changes for Phase 3.2 multi-instance foundation  
build artifact path: `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`

## Scope

This evidence covers V3.0 Phase 3.2 Closure: Multi-instance Foundation Engineering Acceptance & Claim Update.

Phase 3.2 validates only the multi-instance pet foundation:

- PetInstance registry foundation.
- Multiple Tauri pet windows foundation.
- Per-window local CatStateMachine storage key foundation.
- Minimal settings page instance list.
- Legacy default pet path preserved.

Phase 3.2 does not validate or implement:

- `POST /api/instances/:instanceId/events`.
- `petctl attach codex`.
- `petctl notify --instance`.
- Multi-Codex-session routing.
- OS-level Codex window binding.
- Asset Pack v1.
- Performance hardening.
- MCP, Windows, USB, 3D, photo customization, production signing.

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | warn | No hard failures. WARN: rustup missing, external network checks unreachable, sandbox cannot listen on `127.0.0.1:1420`. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript check passed after pet-protocol build. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 6 tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |

## Runtime Baseline

| Scenario | Result | Evidence / notes |
| --- | --- | --- |
| Launch built `.app` | pass | App launched with `open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"`. |
| Health | pass | `GET /api/health` returned `ok=true`, app `agent-desktop-pet`, listen address `127.0.0.1:17321`. |
| Legacy `petctl notify` | pass | `node packages/petctl/dist/cli.js notify --level success --title "phase 3.2 legacy smoke"` returned accepted `eventId=evt_1779182762479_1`. |
| Legacy raw HTTP `POST /api/events` | pass | Authenticated raw HTTP success event returned `202 Accepted`, `eventId=evt_1779182790055_2`. |
| Config registry snapshot | deferred | Manual creation of extra pet instances is deferred to V3.0 final acceptance. Current `settings.json` had `petInstances: []` during this closure run. |

## Default Pet

| Field | Value |
| --- | --- |
| default pet id | `default` |
| default pet name | `Agent Desktop Pet` |
| default window label | `main` |
| default event path | legacy `/api/events` and legacy `petctl notify` |

## Extra Pet Instances

| Instance | Result | Notes |
| --- | --- | --- |
| Extra pet 1 | deferred | Manual creation and visual confirmation deferred to V3.0 final acceptance. |
| Extra pet 2 | deferred | Manual creation and visual confirmation deferred to V3.0 final acceptance. |

## InstanceId / WindowLabel Uniqueness Check

| Check | Result | Notes |
| --- | --- | --- |
| Default instance has stable id/windowLabel | pass | `default` / `main`. |
| Extra `instanceId` uniqueness | deferred | Requires at least two extra pet instances; deferred to V3.0 final acceptance. |
| Extra `windowLabel` uniqueness | deferred | Requires at least two extra pet instances; deferred to V3.0 final acceptance. |

## Visual Acceptance Table

| Scenario | Result | Notes |
| --- | --- | --- |
| Default pet visible | deferred | Manual visual confirmation deferred to V3.0 final acceptance. |
| Default pet transparent and no black border | deferred | Manual visual confirmation deferred to V3.0 final acceptance. |
| Default pet draggable | deferred | Manual visual confirmation deferred to V3.0 final acceptance. |
| Idle animation normal | deferred | Manual visual confirmation deferred to V3.0 final acceptance. |
| Three pets visible after creating two extra instances | deferred | Extra instance visual confirmation deferred to V3.0 final acceptance. |
| Three pets not fully overlapped | deferred | Extra instance visual confirmation deferred to V3.0 final acceptance. |
| Each pet shows independent name | deferred | Extra instance visual confirmation deferred to V3.0 final acceptance. |
| Extra pets have transparent frameless always-on-top windows | deferred | Extra instance visual confirmation deferred to V3.0 final acceptance. |

## Restart Persistence Table

| Scenario | Result | Notes |
| --- | --- | --- |
| Three pets restore after app restart | deferred | Manual restart smoke deferred to V3.0 final acceptance. |
| Names restore after restart | deferred | Manual restart smoke deferred to V3.0 final acceptance. |
| Positions restore after restart | deferred | Manual restart smoke deferred to V3.0 final acceptance. |
| No pet restores off-screen | deferred | Manual restart smoke deferred to V3.0 final acceptance. |
| Pets do not all stack at the same coordinate | deferred | Manual restart smoke deferred to V3.0 final acceptance. |

## Debug-state Isolation Table

| Scenario | Result | Notes |
| --- | --- | --- |
| running affects only current pet | deferred | Manual debug-state isolation deferred to V3.0 final acceptance. |
| success affects only current pet | deferred | Manual debug-state isolation deferred to V3.0 final acceptance. |
| error affects only current pet | deferred | Manual debug-state isolation deferred to V3.0 final acceptance. |
| need_input affects only current pet | deferred | Manual debug-state isolation deferred to V3.0 final acceptance. |
| Animations do not resize windows | deferred | Manual visual confirmation deferred to V3.0 final acceptance. |
| Sounds do not misfire across pets | deferred | Manual visual confirmation deferred to V3.0 final acceptance. |

## Legacy Event Regression Table

| Scenario | Result | Notes |
| --- | --- | --- |
| Legacy `petctl notify` accepted | pass | Accepted `evt_1779182762479_1`. |
| Legacy raw HTTP `/api/events` accepted | pass | Accepted `evt_1779182790055_2`. |
| Legacy event affects only default pet | deferred | Visual confirmation with extra pets deferred to V3.0 final acceptance. |
| Diagnostics shows accepted event | pass | Accepted event returned by bridge; settings diagnostics visual check not run in this closure. |

## Tray Behavior Table

| Scenario | Result | Notes |
| --- | --- | --- |
| Open settings from tray | deferred | Manual confirmation deferred to V3.0 final acceptance. |
| Mute toggle | deferred | Manual confirmation deferred to V3.0 final acceptance. |
| Show / hide scope | deferred | Must record in V3.0 final acceptance whether current behavior affects default pet only or all pet windows. |
| Reset position scope | deferred | Must record in V3.0 final acceptance whether current behavior affects default pet only or all pet windows. |
| Exit closes all pet windows | deferred | Manual confirmation deferred to V3.0 final acceptance. |
| Exit stops `127.0.0.1:17321` listener | deferred | Manual/runtime final close smoke deferred to V3.0 final acceptance. |

## Deferred Manual Acceptance

No Phase 3.2 engineering blockers remain after the revised acceptance policy.

The following manual checks are intentionally deferred to V3.0 final acceptance:

- Create two extra pet instances from settings UI.
- Confirm three pet windows are visible, distinct, transparent and frameless.
- Confirm each pet has unique `instanceId` and `windowLabel`.
- Drag and restart persistence.
- Debug-state isolation across pets.
- Legacy default-only visual event behavior with extra pets present.
- Tray show/hide and reset-position scope across multiple pet windows.

## Allowed Claims

Current allowed claims after this evidence:

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
V2.0 ready: local agent workflow integration and developer usability polish complete.
Third-party local HTTP contract smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
V3.0 Phase 3.1 complete: V2.x baseline frozen and complex integration backlog aligned.
Phase 3.2 complete: multi-instance pet foundation ready.
```

The revised Phase 3.2 acceptance defers manual visual acceptance to V3.0 final acceptance. The Phase 3.2 claim above only covers foundation engineering closure.

## Forbidden Claims

```text
V3.0 ready
instance-aware event routing ready
multi-instance Codex verified
petctl attach ready
petctl notify --instance ready
OS-level Codex window binding ready
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```
