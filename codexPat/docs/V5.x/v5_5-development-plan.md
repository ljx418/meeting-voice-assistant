# V5.5 Development Plan

status: passed-scoped

date: 2026-05-28

## Goal

Add an explicit local renderer selection path for CSS, sprite, and bundled GLTF prototype renderers while keeping CSS as the default.

## Scope

- Resolve renderer kind from a local browser storage key.
- Accept only `css`, `sprite`, or `gltf` as runtime renderer choices.
- Fall back to CSS for missing, invalid, or unavailable renderer choices.
- Keep asset manifests bundled and local.

## Out Of Scope

- Making GLTF the default renderer.
- custom asset import.
- remote asset loading.
- production renderer readiness.
- product settings UI.

## Implementation Summary

- Add runtime renderer selection helper.
- Integrate selected renderer manifest into live desktop pet render path.
- Add unit tests for default, GLTF selection, unavailable renderer fallback, and invalid value fallback.

## Risk Review

No High plan drift or false-green risk remains. Runtime renderer selection is explicitly local and does not imply 3D production readiness.
