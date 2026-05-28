# V5.x Current Gap Analysis

status: final-passed-scoped

date: 2026-05-28

## Current State

Implemented today:

- built-in CSS cat profiles.
- per-instance appearance selection.
- safe action / sound whitelist.
- CatStateMachine-driven behavior.

Implemented scoped:

- high-quality 2D action smoke path.
- renderer plugin interface.
- GLTF / Three.js prototype renderer.
- bundled scripted GLTF core action clips.
- local explicit runtime renderer selection.

Not implemented:

- Rive renderer.
- Live2D renderer.
- user asset upload.
- custom asset pack import.
- remote asset download.
- marketplace.

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| Asset manifest | V5.0 passed scoped | frozen validated schema | passed V5.0 |
| Asset security boundary | V5.0 passed scoped | explicit no path / no URL / no script / no raw payload contract | passed V5.0 |
| Architecture design | V5.0 passed scoped | renderer registry, manifest loader, action resolver, visual evidence flow | passed V5.0 |
| Bundled 2D sprite smoke | V5.1 passed scoped | bundled 2D core state visuals with evidence | passed V5.1 |
| Runtime renderer plugin interface | V5.2 passed scoped | live pet runtime uses safe action-id renderer contract | passed V5.2 |
| GLTF 3D prototype | V5.3 passed scoped | bundled scripted GLB and Three.js prototype evidence | passed V5.3 |
| Core action assets | V5.4 passed scoped for GLTF prototype | accepted visual assets per core state | passed V5.4 |
| Renderer abstraction | V5.2 passed scoped | plugin boundary for css/sprite/gltf/rive/live2d | passed V5.2 for css/sprite/gltf |
| 3D renderer | V5.3 passed scoped | bundled GLTF / Three.js prototype | passed V5.3 |
| 3D action clips | V5.4 passed scoped | bundled core action clips | passed V5.4 |
| Runtime renderer selection | V5.5 passed scoped | explicit local CSS/sprite/GLTF selection with CSS fallback | passed V5.5 |
| User import | forbidden | manifest-validated local import after bundled assets pass | future |
| Remote assets | forbidden | no target until separate security review | out of scope |
| Photo customization | forbidden | separate future stage | out of scope |
| Production signed release | not covered | separate productization track | out of scope |

## Main Risks

| Risk | Level | Notes |
| --- | --- | --- |
| Scope drift | Medium | V5.4/V5.5 stay limited to bundled local generated assets and local renderer selection. |
| Asset production cost | Medium | Current 3D action clips are prototype motion, not final art quality. |
| Performance | Medium | Transparent always-on windows plus 3D can increase CPU/GPU use. |
| Security | Medium | User asset import can introduce path, script, and remote loading risks. |
| Claim expansion | Medium | Final claim remains scoped and keeps `3D ready` forbidden. |
| Evidence weakness | Medium | GLB structural smoke, nonblank fixture evidence, and build checks exist; full animation quality remains future work. |

overall risk: Medium

go / no-go: V5.0 through V5.5 and V5.x Final passed scoped acceptance. No-go for production 3D readiness, custom imports, Rive, Live2D, marketplace, or signed release claims.

## Remaining Product Gaps

- Production-quality 3D art and animation polish.
- Lazy loading or code splitting for Three.js before any product default.
- Rive / Live2D exploration.
- Manifest-validated custom import after separate security review.
- Productization packaging, signing, license audit, and release artifact integrity.

## Current Allowed Claim

```text
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
V5.x scoped renderer and bundled asset acceptance passed final regression.
```
