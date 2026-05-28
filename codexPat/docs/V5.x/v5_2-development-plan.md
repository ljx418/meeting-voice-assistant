# V5.2 Development Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Integrate the V5 renderer contract into the live desktop pet runtime while keeping the visual output compatible with the existing CSS fallback.

## Scope

Allowed:

- use `CatActionResolver` in live pet state updates.
- mount a renderer adapter per pet window.
- route safe action IDs to the renderer adapter.
- keep CSS renderer as the default live renderer.
- preserve sprite renderer availability for registry tests.
- keep per-instance renderer state isolated.

Not allowed:

- GLTF / Three.js runtime production renderer.
- 3D readiness claim.
- custom import activation.
- remote asset loading.
- changes to V3/V4 Codex monitoring semantics.

## Acceptance

V5.2 passes only if the live pet runtime uses the renderer contract and tests prove the renderer receives safe action IDs only.

Allowed claim:

```text
V5.2 renderer plugin interface smoke passed for safe action-id driven renderers.
```

