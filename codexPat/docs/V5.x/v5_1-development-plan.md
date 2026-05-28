# V5.1 Development Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Implement a bundled 2D sprite asset pack and sprite renderer smoke path for the eight core pet states.

V5.1 does not implement 3D, GLTF production rendering, Rive, Live2D, custom asset import, remote asset loading, or production release readiness.

## Scope

Allowed:

- bundled sprite manifest.
- bundled inline SVG sprite definitions.
- sprite renderer adapter.
- visual fixture generation for core states.
- unit tests for sprite asset coverage and renderer boundary.
- CSS fallback remains available.

Not allowed:

- arbitrary local path references.
- network asset loading.
- user import activation.
- GLTF / Three.js production renderer.
- 3D readiness claim.
- changes to V3/V4 Codex monitoring semantics.

## Core States

V5.1 must cover:

```text
idle
thinking
running
success
warning
error
need_input
sleeping
```

## Asset Format Decision

V5.1 uses bundled inline SVG sprite definitions stored in TypeScript modules.

Reason:

- no runtime path lookup.
- no remote fetch.
- easy license/attribution audit.
- deterministic visual fixture generation.
- compatible with V5.0 manifest security boundary.

## Evidence

Required evidence:

- `docs/V5.x/evidence/v5_1-sprite-asset-pack-v2-evidence-2026-05-28.md`
- `docs/V5.x/evidence/v5_1-visual-regression-2026-05-28.md`

Allowed claim after acceptance:

```text
V5.1 bundled 2D sprite asset pack smoke passed for core pet states.
```

