# V5.12 Runtime Imported Pack Rendering Acceptance Plan

status: planned-audit-ready

date: 2026-05-28

## Required Checks

- Activate imported pack for one PetInstance.
- Drive all core states and confirm that only the target PetInstance uses imported visuals.
- Confirm default and unrelated pets remain on their selected renderer/profile.
- Delete or invalidate imported pack metadata and confirm CSS fallback.
- Confirm renderer input remains safe and contains no raw source payloads.
- Desktop Manager lets a user select an imported pack for a specific PetInstance.
- Desktop Manager shows the current active pack per PetInstance.
- User can switch the PetInstance back to bundled/default rendering.
- App restart restores PetInstance to active pack mapping.
- Two pets can use the same imported pack without shared mutable renderer state.
- Renderer kind mismatch produces a stable error and does not partially render.
- Corrupt GLB and corrupt sprite frame fall back to CSS with sanitized diagnostics.

## GLTF / GLB Deep Scan

Imported GLTF / GLB assets must pass a structured scan before V5.12 runtime use:

- Parse GLTF JSON or GLB JSON chunk.
- Reject `http://`, `https://`, `file://`, `javascript:`, and `data:` URIs.
- Reject external `.bin` and external image references for the local single-file mode.
- Reject absolute paths and path traversal inside GLTF URI fields.
- Reject unknown `extensionsRequired` values unless explicitly allowlisted.
- Enforce maximum file size, mesh count, material count, texture count, animation count, and animation duration.
- Require accepted action clip names only: `idle`, `thinking`, `running`, `success`, `warning`, `error`, `need_input`, `sleeping`.
- Evidence must record safe field names and decision result only, never raw JSON chunks or local paths.

## Runtime Payload Snapshot

V5.12 evidence must prove renderer adapters receive only:

```text
safe action ID
renderer kind
safe profile/pack IDs
playback intent
scale
visibility
```

It must not contain:

```text
raw manifest path
raw provider payload
prompt text
photo metadata
token
Authorization
workspace path
config path
full local path
```

## Regression

```bash
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop test
pnpm --filter desktop check
pnpm --filter desktop build
node scripts/v5_8_personalized_asset_pipeline_smoke.mjs
node scripts/v4_4_managed_session_smoke.mjs
```

## Manual Visual Evidence

Screenshots or video must show:

- target cat using imported action visuals.
- default pet unchanged.
- unrelated pet unchanged.
- fallback state after invalid pack.

## Claim Boundary

V5.12 proves runtime use of local imported packs only. It does not prove automatic asset generation or provider integration.
