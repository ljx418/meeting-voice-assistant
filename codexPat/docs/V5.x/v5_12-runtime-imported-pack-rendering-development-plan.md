# V5.12 Runtime Imported Pack Rendering Development Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Make imported and activated asset packs render in the live desktop pet runtime for the selected PetInstance.

V5.12 closes the gap between V5.9 CLI activation metadata and actual runtime renderer usage.

## Required Behavior

- A PetInstance with an activated imported pack uses that pack for safe action IDs.
- Default pet and unrelated pets remain unchanged.
- If the imported pack is missing, invalid, or stale, the target pet falls back to CSS without crashing.
- Renderer adapters still receive only safe action IDs, renderer kind, safe pack/profile IDs, playback intent, scale, and visibility.
- Runtime never receives raw prompt text, raw provider payload, raw local paths, shell commands, tokens, or Authorization values.

## Implementation Scope

- Load sanitized imported-pack activation metadata at runtime.
- Resolve active pack per PetInstance.
- Route safe CatActionResolver output to the chosen renderer.
- Add stale/missing-pack diagnostics.
- Add tests proving per-instance isolation and fallback.

## Out Of Scope

- Provider generation.
- Photo upload.
- Marketplace.
- Remote asset loading.
- Production 3D readiness claim.

## Acceptance

- Imported sprite pack renders for the selected PetInstance.
- Imported GLTF pack renders for the selected PetInstance if the local renderer is selected and available.
- Default pet remains unchanged.
- Other Codex pets remain unchanged.
- Invalid or missing imported pack falls back to CSS.
- Security and claim scans pass.

## Evidence

- `docs/V5.x/evidence/v5_12-runtime-imported-pack-rendering-smoke-YYYY-MM-DD.md`
- `docs/V5.x/v5_12-final-acceptance-report.md`

## Allowed Claim

```text
V5.12 runtime imported asset pack rendering passed for tested local PetInstance scenarios.
```

## Forbidden Claims

```text
3D ready
photo-to-3D ready
provider integration verified
remote asset loading ready
production signed release ready
```
