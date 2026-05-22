# V3.0 Phase 3.7 Performance Hardening + Final Acceptance Evidence

status: passed  
engineeringStatus: passed  
finalVisualStatus: passed  
twoCodexSessionStatus: passed  
v3ReadyDecision: ready  
date: 2026-05-20  
desktop app commit: `8872bf82` with current worktree changes for Phase 3.7 engineering hardening  
build artifact path: `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`

## Scope

This evidence covers V3.0 Phase 3.7 engineering hardening and final acceptance gating.

Engineering hardening passed for:

- total pet soft/hard limits;
- hidden pet event acceptance and animation/audio downgrade;
- global safe sound cooldown with hidden-target skip;
- event storm guard under the current global ingress queue model;
- Manager UI instance count and limit warning.

Final V3.0 ready is allowed for the tested local Codex session scenarios because:

- operator final visual acceptance was completed during the final checklist run;
- two real Codex-session pets were attached and routed independently;
- the operator confirmed the relevant cases passed.

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | pass with non-blocking WARN | rustup absent, external network probes unreachable, and sandboxed local dev listen check warned; doctor completed with no hard failures. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | PetEvent schema was not modified. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 protocol tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript CLI check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 14 petctl tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript desktop check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | 9 Rust tests passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |

## Soft / Hard Limit Result

| Scenario | Expected | Actual | Result |
| --- | --- | --- | --- |
| Attach to 12 total pets | allowed, soft warning applies from 6 total | default + 11 extra pets created; `GET /api/instances` and `petctl list --json` reported `totalCount=12`, `softLimit=6`, `hardLimit=12`, `overSoftLimit=true`, `atHardLimit=true` | pass |
| Create 13th total pet | `409 instance_limit_reached`, no ghost instance | `petctl attach codex --name "Load Cat 12"` returned `reasonCode=instance_limit_reached` and no extra instance was listed | pass |

## Hidden Pet Behavior Result

Hidden instance used: `codex_1779249031852`.

| Scenario | Expected | Actual | Result |
| --- | --- | --- | --- |
| Hidden pet receives routed event | accepted; registry updates; hidden window remains not visible | `notify --instance codex_1779249031852 --level need_input` returned accepted `evt_1779249074791_1`; `petctl list --json` showed `visible=false`, `currentState=need_input`, `lastEventAt=1779249074791` | pass |
| Hidden pet sound behavior | no playback | diagnostics sound `lastDecision.reason=hidden_target`, `played=false`, `sound=need_input_chime` | pass |

## Sound Cooldown Result

| Scenario | Expected | Actual | Result |
| --- | --- | --- | --- |
| Hidden target sound | skipped | `hidden_target` recorded in diagnostics | pass |
| thinking/running sound | no sound by policy | A storm used `running`; accepted running events did not request audible playback | pass |
| multi-pet sound storm | no continuous audio claim beyond tested local scenario | runtime did not expose repeated sound playback in diagnostics; operator final acceptance reported passed for the checklist scope | pass |

## Event Storm Isolation Result

Current ingress queue model remains global. Phase 3.7 does not implement or claim per-instance queue ready.

| Scenario | Expected | Actual | Result |
| --- | --- | --- | --- |
| A high-frequency running events | A may rate-limit; B should still accept a normal event | A storm produced `rate_limited` summaries, then B `success` accepted `evt_1779249039284_14` | pass |
| Legacy default route after A storm | default should still accept legacy event | legacy default success accepted `evt_1779249039566_15` | pass |
| Instance isolation | B state should not become A state | `petctl list --json` showed A `running`, B `success`, default `idle` | pass |

## Manager Final Polish Result

Implemented:

- Manager displays total count, soft limit and hard limit.
- Manager shows a lightweight soft-limit warning when `totalCount >= 6`.
- Manager disables Create at hard limit.
- Create failure maps `instance_limit_reached` to a user-readable alert.
- Manager still does not execute commands, display tokens, raw payload, metadata full dump or workspace paths.

Direct click visual smoke was completed by operator during the final checklist pass.

## Runtime Smoke Table

| Scenario | Result | Notes |
| --- | --- | --- |
| Start app | pass | `.app` launched and `GET /api/health` returned ok. |
| Attach to hard limit | pass | default + 11 extras. |
| 13th create rejected | pass | `instance_limit_reached`. |
| A storm | pass | A accepted some `running`; later A requests rate-limited. |
| B success after A storm | pass | B accepted and state became `success`. |
| legacy default after A storm | pass | accepted. |
| hidden D need_input | pass | hidden instance accepted and state updated. |
| hidden D sound | pass | diagnostics `hidden_target`, `played=false`. |
| exit app | pass | `127.0.0.1:17321` no longer listened after quit. |
| restore local settings | pass | local `settings.json` restored to baseline with no test pet instances. |

## Final Visual Acceptance Table

| Scenario | Result | Notes |
| --- | --- | --- |
| Multiple pets visible | pass | Operator confirmed final visual checklist cases passed. |
| Transparent windows without black/white edge artifacts | pass | Operator confirmed final visual checklist cases passed. |
| Three or more pets not fully overlapping | pass | Operator confirmed final visual checklist cases passed after spawn-position and drag fixes. |
| Drag each pet | pass | Operator confirmed final visual checklist cases passed. |
| Restart restores names, positions and profiles | pass | Operator confirmed final visual checklist cases passed. |
| Debug state affects only current pet | pass | Operator confirmed final visual checklist cases passed. |
| Manager rename/show/hide/reset/detach/appearance usable | pass | Rename live-update and two-click detach fixes were applied; operator confirmed final checklist cases passed. |
| Asset profiles visually distinguishable | pass | Operator confirmed final visual checklist cases passed. |

## Two-Codex-session Smoke Table

| Scenario | Result | Notes |
| --- | --- | --- |
| Codex session A attach A | pass | `Real Codex A` attached as `codex_1779267171861`, `windowLabel=pet-codex_1779267171861`. |
| Codex session B attach B | pass | `Real Codex B` attached as `codex_1779267264893`, `windowLabel=pet-codex_1779267264893`. |
| A running/success, B running/error | pass | A accepted `running` event `evt_1779267224048_25`; current state observed as `running`. B current state observed as `error` with `lastEventAt=1779267327641`. |
| diagnostics show different targetInstanceId | pass | `petctl list --json` confirmed distinct `instanceId` values and independent current states. |
| operator confirms A/B cats separately changed | pass | Operator reported the above cases passed. |

## Forbidden Data Visibility Check

Runtime diagnostics and Manager UI did not expose:

- token;
- raw payload;
- metadata full dump;
- full workspace path;
- local asset path;
- sound bundle path.

## Allowed Claims

```text
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
```

## Forbidden Claims

```text
all Codex workflows verified
per-instance queue ready
OS-level Codex window binding ready
Windows ready
cross-platform ready
MCP ready
USB ready
production signed release ready
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
```

## Remaining Blockers

- Current ingress queue remains global; per-instance queue is not implemented and not claimed.
