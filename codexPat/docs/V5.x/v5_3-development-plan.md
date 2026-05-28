# V5.3 Development Plan

status: passed-scoped

date: 2026-05-28

## Goal

V5.3 implements a bundled GLTF / Three.js 3D cat prototype using a project-authored scripted GLB generator.

## Required Before Implementation

- select 3D dependency and lock package impact.
- provide bundled GLTF/GLB asset.
- complete license / attribution review for the bundled model.
- define nonblank canvas evidence method.
- define performance baseline method.
- define fallback behavior when WebGL is unavailable.

## Blocker Resolution

The original Blender path was blocked because Blender could not be installed through the tested local path. V5.3 switched to a free scripted GLB generation path.

Generated local bundled asset:

- `apps/desktop/public/assets/3d/agent-desktop-pet-cat-prototype.glb`
- `apps/desktop/public/assets/3d/LICENSE-ASSET.md`

Generator:

- `scripts/generate_v5_3_gltf_asset.mjs`

## Forbidden Claims

```text
3D ready
production signed release ready
custom asset pack import ready
```
