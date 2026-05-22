# V3.0 Phase 3.6 Built-in Asset Pack v1 Evidence

status: passed  
date: 2026-05-20  
desktop app commit: `8872bf82` with current worktree changes for Phase 3.6 built-in profiles  
build artifact path: `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`

## Scope

This evidence covers V3.0 Phase 3.6: Built-in Asset Pack v1 + Per-instance Appearance.

Phase 3.6 implements:

- Built-in CatProfile registry.
- Per-instance `catProfileId` setting.
- Default pet profile persistence through app settings.
- Manager UI Appearance selector.
- Tauri commands:
  - `list_cat_profiles`
  - `set_pet_instance_profile`
- CSS profile classes for built-in placeholder cats.

Phase 3.6 does not implement:

- Rive / Live2D / Spine / Three.js / GLTF / GLB.
- Photo customization.
- User asset upload.
- Remote asset download.
- Custom asset pack import.
- Asset marketplace or skin editor.
- Multi-instance Codex real visual verification.
- OS-level Codex window binding.
- MCP, Windows, USB or production signing.

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | pass with non-blocking WARN | rustup absent, external network probes unreachable, and sandboxed local dev listen check warned; doctor completed with no hard failures. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | PetEvent schema was not modified in Phase 3.6. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 protocol tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript CLI check passed; `petctl` public command behavior was not changed in Phase 3.6. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 14 petctl tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript desktop check passed after profile UI implementation. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed after profile commands. |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | 8 Rust tests passed, including built-in profile safety and invalid profile rejection helper coverage. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |

## Built-in Profile List

| id | name | cssClass | visual distinction |
| --- | --- | --- | --- |
| `default-cat` | Default Cat | `cat-profile-default-cat` | slate coat, dark eyes, neutral name label. |
| `black-cat` | Black Cat | `cat-profile-black-cat` | dark coat, green eyes, light highlight. |
| `orange-tabby` | Orange Tabby | `cat-profile-orange-tabby` | orange coat, tabby striping, warm name label. |
| `white-cat` | White Cat | `cat-profile-white-cat` | white coat, blue eyes, gray head patch. |

No profile returns a file path, URL, local resource path or user-controlled CSS class.

## Profile Registry Validation

- `catProfileId` is validated against the built-in registry.
- Unknown, path-like or URL-like profile IDs return `cat_profile_invalid`.
- The user never submits a raw `cssClass`.
- External agent events cannot modify `catProfileId`; PetEvent schema and HTTP routing were not changed.

## Profile Persistence Result

Implementation writes `defaultCatProfileId` for the default pet and `catProfileId` for extra `PetInstance` records into app settings. Invalid stored profile IDs fall back to `default-cat` in instance views.

Direct restart visual smoke is deferred to V3.0 final acceptance.

## Per-instance Isolation Result

Profile updates are scoped by `instanceId`:

- Updating default changes only the main pet.
- Updating A changes only A.
- Updating B changes only B.
- Routed events do not change profile.
- Rename, show/hide, reset position and detach do not rewrite another instance's profile.
- Detach removes the instance record, so its profile does not restore as an orphan instance.

Direct click visual smoke is deferred to V3.0 final acceptance.

Runtime registry smoke used:

| Pet | instanceId | catProfileId | routed state |
| --- | --- | --- | --- |
| default | `default` | `default-cat` | `idle` |
| A | `codex_1779247835082` | `black-cat` | `success` |
| B | `codex_1779247835398` | `orange-tabby` | `error` |

`petctl list --json` confirmed default, A and B retained independent `catProfileId` values after routed events. Local settings were restored after the smoke run.

## Invalid Profile Rejection Result

Expected rejected inputs:

- `not-found-profile`
- `../../x.css`
- `file:///tmp/cat.css`
- `https://example.com/cat.css`

Expected result: `cat_profile_invalid`; existing profile remains unchanged.

## Unknown Instance Rejection Result

Expected result for valid profile with unknown instance: `instance_not_found`.

## Routing Regression Result

Phase 3.6 does not modify PetEvent, HTTP event routing, `petctl notify`, or CatStateMachine behavior. Instance-scoped events remain routed by Phase 3.3 rules and do not alter appearance.

Runtime smoke:

- `GET /api/health` returned ok.
- `notify --instance codex_1779247835082 --level success` was accepted and A changed to `success`.
- `notify --instance codex_1779247835398 --level error` was accepted and B changed to `error`.
- `petctl list --json` showed A `black-cat`, B `orange-tabby`, default `default-cat`.

## State/Profile Class Compatibility Result

Profile classes are applied alongside existing state classes on the pet shell. The profile CSS only changes internal cat colors, stripes, eyes and name label color. It does not:

- change window size;
- animate root containers;
- introduce window-level shadow;
- restore black external cat shadow;
- change CatStateMachine priority, lock or cooldown semantics.

## Visual Distinction Notes

The four built-in profiles each use at least two visible dimensions:

- coat color;
- eye color;
- head/body markings or stripes;
- name label color.

Final visual confirmation is intentionally deferred to V3.0 final acceptance.

## Forbidden Data Visibility Check

Manager UI, profile commands and profile registry do not expose:

- token;
- token file path;
- raw payload;
- metadata full dump;
- full workspace path;
- local resource path;
- URL input;
- uploaded asset path.

## Allowed Claims

```text
Phase 3.6 complete: built-in asset pack v1 and per-instance appearance selection ready.
```

## Forbidden Claims

```text
V3.0 ready
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
remote asset download ready
asset marketplace ready
custom asset pack import ready
custom skin editor ready
multi-instance Codex verified
OS-level Codex window binding ready
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```
