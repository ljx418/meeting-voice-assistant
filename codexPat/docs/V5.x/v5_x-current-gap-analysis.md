# V5.x Current Gap Analysis

status: planned

date: 2026-05-26

## Current State

Implemented today:

- built-in CSS cat profiles.
- per-instance appearance selection.
- safe action / sound whitelist.
- CatStateMachine-driven behavior.

Not implemented:

- high-quality 2D action pack.
- renderer plugin interface.
- GLTF / Three.js 3D renderer.
- bundled 3D action clips.
- Rive renderer.
- Live2D renderer.
- user asset upload.
- custom asset pack import.
- remote asset download.
- marketplace.

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| Asset manifest | reference design only | frozen validated schema | planned |
| Core action assets | CSS/profile-level expression | accepted visual assets per core state | planned |
| Renderer abstraction | current built-in renderer path | plugin boundary for css/sprite/gltf/rive/live2d | planned |
| 3D renderer | not implemented | bundled GLTF / Three.js prototype | planned |
| 3D action clips | not implemented | bundled core action clips | planned |
| User import | forbidden | manifest-validated local import after bundled assets pass | future |
| Remote assets | forbidden | no target until separate security review | out of scope |
| Photo customization | forbidden | separate future stage | out of scope |

## Main Risks

| Risk | Level | Notes |
| --- | --- | --- |
| Scope drift | High | 3D can expand into marketplace, upload, generation, or editor work. |
| Asset production cost | High | Motion quality depends on real asset creation, not just code. |
| Performance | Medium | Transparent always-on windows plus 3D can increase CPU/GPU use. |
| Security | Medium | User asset import can introduce path, script, and remote loading risks. |
| Claim expansion | High | A GLTF prototype must not become `3D ready` without full acceptance. |

overall risk: High

go / no-go: go for planning; no-go for implementation without V5.0 asset system freeze.

## Current Allowed Claim

```text
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
```
