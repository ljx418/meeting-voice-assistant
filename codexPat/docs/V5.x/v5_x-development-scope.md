# V5.x Development Scope

status: planned-audit-ready

date: 2026-05-28

## One-line Scope

V5.x is the renderer and asset-system phase: it upgrades the pet's visual asset pipeline while preserving the existing V3/V4 Agent and Codex state sources.

## In Scope

### 1. Asset Contract

- Freeze a declarative asset manifest schema.
- Define required core actions.
- Define optional action fallback.
- Add validation for invalid renderer kinds, missing core actions, forbidden URLs, forbidden paths, and executable/script-like fields.
- Add sanitized manifest diagnostics.

Primary docs:

- `docs/V5.x/v5_0-asset-manifest-schema.md`
- `docs/V5.x/v5_0-security-boundary.md`

### 2. Safe Action Resolution

- Convert current `CatState` values into safe renderer actions.
- Preserve the current state priority model.
- Prevent success/idle transitions from incorrectly hiding active `error` or `need_input` states.
- Keep renderer input independent from raw `PetEvent` and raw Agent payloads.

Primary docs:

- `docs/V5.x/v5_0-architecture-design.md`
- `docs/blueprint/04-cat-state-machine.md`

### 3. Renderer Interface

- Define `PetRenderer`.
- Add `RendererRegistry`.
- Wrap the existing CSS cat as a `CSSRenderer` fallback.
- Add lifecycle rules for mount/switch/dispose.
- Keep per-instance renderer state isolated.

Primary docs:

- `docs/V5.x/v5_x-detailed-design.md`
- `docs/V5.x/v5_2-renderer-plugin-interface-design.md`

### 4. Bundled 2D Sprite Renderer

- Add a bundled sprite renderer and asset pack.
- Cover all eight core actions.
- Keep CSS renderer as fallback.
- Produce visual evidence for each core action.

Primary planned evidence:

- `docs/V5.x/v5_1-sprite-asset-pack-v2-evidence-YYYY-MM-DD.md`
- `docs/V5.x/v5_1-visual-regression-YYYY-MM-DD.md`

### 5. Bundled GLTF / Three.js Prototype

- Add a bundled GLTF/GLB renderer prototype.
- Use bundled assets only.
- Verify transparent window, drag behavior, animation switching, and nonblank canvas output.
- Record performance baseline.

Primary planned evidence:

- `docs/V5.x/v5_3-gltf-3d-prototype-evidence-YYYY-MM-DD.md`
- `docs/V5.x/v5_3-performance-baseline-YYYY-MM-DD.md`

### 6. Bundled 3D Action Pack

- Add bundled 3D clips for the eight core actions.
- Define action priorities and transitions.
- Make `error` and `need_input` visually distinct.
- Add license/attribution audit.

Primary planned evidence:

- `docs/V5.x/v5_4-3d-action-asset-pack-evidence-YYYY-MM-DD.md`
- `docs/V5.x/v5_4-license-attribution-audit-YYYY-MM-DD.md`

### 7. Optional Local Custom Asset Import

This is optional for V5.x final.

If included:

- import only local files selected by the user.
- copy validated assets into app-managed storage.
- reject remote URLs, arbitrary runtime paths, scripts, and executable files.
- preserve the previous active pack on failure.

Primary planned evidence:

- `docs/V5.x/v5_5-custom-asset-import-evidence-YYYY-MM-DD.md`

If not included, V5.x final must say custom asset import remains planned/not-ready.

## Out Of Scope

V5.x does not include:

- new Codex lifecycle monitoring.
- OS-level Codex active-window auto-monitoring.
- interactive TUI monitoring beyond the already accepted V4 scoped managed-hook path.
- Windows readiness.
- cross-platform readiness.
- USB readiness.
- production signed release readiness.
- asset marketplace.
- remote asset download.
- arbitrary user upload before V5.5 gates pass.
- photo-to-cat customization.
- Rive readiness.
- Live2D readiness.
- all Codex workflows verification.

## Concrete Deliverables

| Phase | Required Deliverable | Acceptance Type |
| --- | --- | --- |
| V5.0 | manifest schema, security boundary, architecture freeze, validator plan | design + tests |
| V5.1 | bundled 2D sprite renderer and core action pack | visual + regression |
| V5.2 | renderer registry and CSS/sprite adapter interface | unit + integration |
| V5.3 | bundled GLTF/Three.js prototype | visual + nonblank canvas + performance |
| V5.4 | bundled 3D core action clips | visual + license + transition audit |
| V5.5 | optional local custom import | validation + security + fallback |
| V5.x Final | final evidence index and claim scan | final acceptance |

## Acceptance Must Prove

- All core actions have distinct visual behavior for the claimed renderer.
- Invalid asset packs fail before activation.
- Optional missing actions fall back safely.
- Renderer adapters receive safe action IDs only.
- No raw Agent/Codex payload enters renderer or manifest.
- No remote URL or arbitrary local path is accepted.
- Existing V3/V4 runtime smoke remains green.
- Visual evidence exists for every claimed renderer/action pair.

## Audit Focus

Deep review should focus on:

- whether renderer adapters can accidentally receive raw payloads.
- whether manifest validation misses paths, URLs, or script-like fields.
- whether GLTF assets can execute or fetch anything unexpectedly.
- whether fallback behavior could hide a real error state.
- whether evidence supports only scoped claims.
- whether V5 documentation accidentally implies production signed release readiness.

