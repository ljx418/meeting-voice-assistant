# V5.x Current Gap Analysis

status: personalized-extension-passed-scoped / productization-planned

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
- personalized prompt-pack generation.
- manifest-validated local personalized asset import smoke.
- imported pack activation records.

Not implemented:

- Rive renderer.
- Live2D renderer.
- user asset upload.
- remote asset download.
- marketplace.
- automatic photo-to-3D generation.
- external provider integration.

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
| Personalized prompt pack | V5.7 passed | standardized external-generation prompts | passed V5.7 |
| User import | V5.8 passed scoped | manifest-validated local import after bundled assets pass | passed V5.8 CLI smoke |
| Imported pack activation | V5.9 passed scoped | imported pack to PetInstance mapping | passed V5.9 CLI smoke |
| Provider feasibility | V5.10 completed scoped | optional adapter boundary | completed V5.10 |
| Import UI | Not implemented | Desktop Manager local manifest import UX | planned V5.11 |
| Runtime imported rendering | Not implemented | activated imported pack renders per PetInstance | planned V5.12 |
| Photo-guided workflow | Not implemented | local prompt and import-instruction flow | planned V5.13 |
| Provider adapter | Feasibility only | explicit-consent provider smoke if pursued | planned V5.14 |
| Visual QA | Partial per previous renderer phases | productized bundled/imported action quality evidence | planned V5.15 |
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

go / no-go: V5.0 through V5.10 passed scoped acceptance. Go for V5.11 planning review. No-go for production 3D readiness, provider integration, marketplace, or signed release claims.

## Remaining Product Gaps

- Production-quality 3D art and animation polish.
- Lazy loading or code splitting for Three.js before any product default.
- Rive / Live2D exploration.
- Desktop Manager UI for personalized asset import and preview.
- Runtime renderer selection for imported asset packs.
- Real external provider integration after separate privacy/cost/license review.
- Productization packaging, signing, license audit, and release artifact integrity.

## Current Allowed Claim

```text
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
V5.x scoped renderer and bundled asset acceptance passed final regression.
V5 personalized prompt-pack and local import pipeline passed scoped CLI acceptance.
```
