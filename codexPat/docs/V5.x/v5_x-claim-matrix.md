# V5.x Claim Matrix

status: personalized-extension-passed-scoped / productization-planned

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
V5.7 personalized cat AI prompt pack generated for standardized external asset creation.
V5.8 manifest-validated local personalized asset import passed for tested sprite and GLTF asset packs.
V5.9 personalized asset action mapping passed for imported local asset packs in tested CLI activation path.
V5.10 external asset generation provider feasibility completed with scoped adapter boundary.
V5.11 personalized asset import UI passed for tested local manifest import scenarios.
V5.12 runtime imported asset pack rendering passed for tested local PetInstance scenarios.
V5.13 photo-guided personalized asset workflow passed for local prompt and import-instruction generation.
V5.14 external generation provider feasibility completed with explicit consent boundary.
V5.15 visual quality and action QA passed for tested bundled and imported asset scenarios.
```

## Conditional Claim Boundaries

| Capability | Earliest Phase | Claim Condition | Must Not Imply |
| --- | --- | --- | --- |
| CLI local import | V5.8 | petctl import/list/activate smoke passes with sanitized output | user-facing import UI or runtime rendering |
| UI local import | V5.11 | Desktop Manager imports valid local manifests and lists sanitized metadata | runtime activation/rendering |
| Runtime rendering | V5.12 | user-selected imported pack renders per PetInstance with fallback | provider generation or photo-to-3D |
| Guided prompt workflow | V5.13 | local prompt/instruction generation passes privacy review | automatic asset generation |
| Provider smoke | V5.14 | explicit consent, credential redaction, retention/license evidence, and imported output validation pass | provider integration verified |
| Productization gate | V5.x Gate | V5.11-V5.15 accepted with security/claim/license scans | production signed release ready |

Current accepted scoped claim:

```text
V5.0 asset system contract frozen with manifest validation and security boundary evidence.
V5.1 bundled 2D sprite asset pack smoke passed for core pet states.
V5.2 renderer plugin interface smoke passed for safe action-id driven renderers.
V5.3 bundled GLTF renderer prototype smoke passed for tested local macOS environment.
V5.4 bundled 3D action asset pack smoke passed for core pet states.
V5.5 local renderer selection smoke passed for CSS fallback and bundled GLTF prototype renderer.
V5.7 personalized cat AI prompt pack generated for standardized external asset creation.
V5.8 manifest-validated local personalized asset import passed for tested sprite and GLTF asset packs.
V5.9 personalized asset action mapping passed for imported local asset packs in tested CLI activation path.
V5.10 external asset generation provider feasibility completed with scoped adapter boundary.
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
- `docs/V5.x/v5_personalized_asset_pipeline_final_report.md`
- `docs/V5.x/evidence/v5_7_prompt_pack_smoke_2026-05-28.md`
- `docs/V5.x/evidence/v5_8_local_asset_import_smoke_2026-05-28.md`
- `docs/V5.x/v5_11-import-ui-development-plan.md`
- `docs/V5.x/v5_12-runtime-imported-pack-rendering-development-plan.md`
- `docs/V5.x/v5_13-photo-to-asset-guided-workflow-development-plan.md`
- `docs/V5.x/v5_14-provider-adapter-feasibility-and-consent-plan.md`
- `docs/V5.x/v5_15-visual-quality-action-qa-plan.md`
- `docs/V5.x/v5_x-productization-gate-plan.md`

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
remote asset loading ready
custom asset pack import ready
asset marketplace ready
production signed release ready
automatic photo-to-3D ready
provider integration verified
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
- V5.11-V5.15 claims require new acceptance evidence; planning documents alone do not make those claims accepted.
- V5.11 import UI acceptance must not be described as ordinary-user end-to-end personalization until V5.12 activation/rendering and V5.13 guided workflow also pass.
- V5.14 feasibility-only acceptance must not use wording that suggests external generation was verified.
