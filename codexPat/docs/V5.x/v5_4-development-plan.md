# V5.4 Development Plan

status: passed-scoped

date: 2026-05-28

## Goal

Add bundled 3D core action clips to the project-authored local GLB prototype.

## Scope

- Generate eight named GLTF animation clips: `idle`, `thinking`, `running`, `success`, `warning`, `error`, `need_input`, and `sleeping`.
- Keep the asset local and bundled.
- Keep the renderer driven by safe action IDs only.
- Preserve CSS fallback.

## Out Of Scope

- 3D ready claim.
- production-quality character art.
- custom asset import.
- remote asset loading.
- Rive / Live2D.
- production signed release.

## Implementation Summary

- Extend the local scripted GLB generator to emit eight core action clips.
- Update GLTF renderer playback so `setAction` switches to the matching clip.
- Add a structural GLB action-pack smoke test.

## Risk Review

No unresolved High risk remains for the scoped smoke claim. The remaining risks are Medium: prototype animation quality and Three.js bundle size.
