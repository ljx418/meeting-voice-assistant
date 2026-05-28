# V5.x Claim Matrix

status: v5_5-passed-scoped

date: 2026-05-28

## Allowed Planning Claims

```text
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
V4.x does not include asset, renderer, release packaging, or productization acceptance gates.
```

## Allowed Scoped Claims After Phase Acceptance

```text
V5.0 asset system contract frozen with manifest validation and security boundary evidence.
V5.1 bundled 2D sprite asset pack smoke passed for core pet states.
V5.2 renderer plugin interface smoke passed for safe action-id driven renderers.
V5.3 bundled GLTF renderer prototype smoke passed for tested local macOS environment.
V5.4 bundled 3D action asset pack smoke passed for core pet states.
V5.5 local renderer selection smoke passed for CSS fallback and bundled GLTF prototype renderer.
```

Current accepted scoped claim:

```text
V5.0 asset system contract frozen with manifest validation and security boundary evidence.
V5.1 bundled 2D sprite asset pack smoke passed for core pet states.
V5.2 renderer plugin interface smoke passed for safe action-id driven renderers.
V5.3 bundled GLTF renderer prototype smoke passed for tested local macOS environment.
V5.4 bundled 3D action asset pack smoke passed for core pet states.
V5.5 local renderer selection smoke passed for CSS fallback and bundled GLTF prototype renderer.
```

Evidence:

- `docs/V5.x/v5_0-final-acceptance-report.md`
- `docs/V5.x/evidence/v5_0-asset-validator-smoke-2026-05-28.md`
- `docs/V5.x/v5_1-final-acceptance-report.md`
- `docs/V5.x/evidence/v5_1-sprite-asset-pack-v2-evidence-2026-05-28.md`
- `docs/V5.x/evidence/v5_1-visual-regression-2026-05-28.md`
- `docs/V5.x/v5_2-final-acceptance-report.md`
- `docs/V5.x/evidence/v5_2-renderer-plugin-interface-evidence-2026-05-28.md`
- `docs/V5.x/v5_3-final-acceptance-report.md`
- `docs/V5.x/evidence/v5_3-gltf-3d-prototype-evidence-2026-05-28.md`
- `docs/V5.x/evidence/v5_3-performance-baseline-2026-05-28.md`
- `docs/V5.x/v5_4-final-acceptance-report.md`
- `docs/V5.x/evidence/v5_4-3d-action-pack-evidence-2026-05-28.md`
- `docs/V5.x/v5_5-final-acceptance-report.md`
- `docs/V5.x/evidence/v5_5-renderer-selection-smoke-2026-05-28.md`

V5.x Final, only after accepted evidence:

```text
V5.x Cat Renderer & Asset System scoped acceptance passed for bundled assets and tested renderer paths.
```

## Not-ready Claims

```text
Rive / Live2D / 3D ready
bundled 3D action pack ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
asset marketplace ready
production signed release ready
```

## Boundary Rules

- V5.x renderer work must not change PetEvent security boundaries.
- Agents may only request safe state/action IDs, not renderer internals.
- Asset packs must not reference arbitrary external paths or remote URLs.
- User import is out of scope until bundled assets and manifest validation pass.
- Rive, Live2D, and GLTF claims must be separate; one renderer passing does not imply another.
- Bundled asset integrity, license / attribution, and asset productization checks belong to V5.x or a later productization track, not V4.x.
- GLTF prototype acceptance does not imply full 3D readiness.
- Custom asset import is not allowed until bundled assets and manifest validation pass.
- Asset pack manifests may reference only bundled IDs or app-managed imported asset IDs, never arbitrary runtime paths or remote URLs.
