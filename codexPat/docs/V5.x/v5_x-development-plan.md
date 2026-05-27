# V5.x Development Plan

status: planned

date: 2026-05-26

## Scope

V5.x is the dedicated Cat Renderer & Asset System track.

This stage owns:

- high-quality 2D action assets.
- renderer plugin boundary.
- GLTF / Three.js 3D cat prototype.
- bundled 3D action asset pack.
- future custom asset pack import.

This stage is separate from:

- V3.x Codex workflow monitoring.
- V4.x OS-level Codex window/session binding.
- V4.x feasibility, probe, binding, and routing work.

## Current Baseline

The current product has:

- built-in CSS cat profiles.
- per-instance appearance selection.
- CatStateMachine action/state mapping.
- PetEvent action / sound white-listing.
- no Rive / Live2D / 3D renderer readiness.
- no user asset upload.
- no remote asset download.
- no custom asset pack import.

Reference design:

- `docs/reference/06-cat-pack.md`
- `docs/blueprint/01-tech-stack.md`
- `docs/blueprint/04-cat-state-machine.md`
- `docs/blueprint/05-desktop-window.md`
- `docs/blueprint/10-risks-and-decisions.md`
- `docs/V3.0/evidence/asset-pack-v1-2026-05-20.md`

## Product Goal

Make the pet feel more like a polished companion without weakening the existing Agent integration safety model.

The renderer must remain driven by safe state/action IDs:

```text
PetEvent -> CatStateMachine -> safe action ID -> renderer clip
```

Agents must not directly control model internals, local files, URLs, scripts, bones, shaders, or arbitrary animation names.

## Phase Plan

| Phase | Goal | Output |
| --- | --- | --- |
| V5.0 | Asset System Freeze | manifest schema, action mapping, fallback rules, security boundary |
| V5.1 | Sprite / 2D Asset Pack v2 | high-quality bundled 2D actions for core states |
| V5.2 | Renderer Plugin Interface | renderer abstraction for CSS/sprite/GLTF/Rive/Live2D |
| V5.3 | GLTF / Three.js 3D Cat Prototype | bundled GLB/GLTF renderer prototype |
| V5.4 | 3D Action Asset Pack | bundled 3D clips for core pet states |
| V5.5 | Asset Import / Custom Pack | manifest-validated local import, no remote or script execution |
| V5.x Final | scoped asset acceptance | final report, visual evidence, security scan, claim scan |

## V5.0 Asset System Freeze

Define the stable asset pack contract before adding new renderers.

Required decisions:

- required core actions: `idle`, `thinking`, `running`, `success`, `warning`, `error`, `need_input`, `sleeping`.
- optional actions: `walk`, `tease`, `stretch`, `blink`.
- renderer types: `css`, `sprite`, `gltf`, `rive`, `live2d`.
- fallback: missing action falls back to `idle` and records warning.
- no arbitrary local paths, remote URLs, scripts, or shell commands.

## V5.1 Sprite / 2D Asset Pack v2

Produce or integrate a higher-quality bundled 2D pack first.

Reason:

- validates action semantics before 3D complexity.
- keeps productization risk lower than immediate 3D.
- provides fallback if 3D performance or packaging is not acceptable.

## V5.2 Renderer Plugin Interface

Introduce renderer abstraction without changing PetEvent.

The state machine should continue to emit safe actions. Renderer plugins only receive:

```text
profileId
rendererKind
actionId
loop/one-shot intent
scale
```

They must not receive raw Agent payloads.

## V5.3 GLTF / Three.js 3D Cat Prototype

Implement bundled GLTF / GLB rendering only.

No user upload, no remote download, and no custom model import in this phase.

Acceptance must include:

- transparent window still works.
- drag does not jitter.
- animation switching is stable.
- idle animation continues when no Agent event is present.
- CPU/GPU usage remains acceptable on target macOS hardware.

## V5.4 3D Action Asset Pack

Add bundled 3D clips for core states.

Action behavior:

- `thinking` and `running` are low-distraction loops.
- `success`, `warning`, `error`, and `need_input` are short one-shot or priority clips.
- `error` and `need_input` must be visually distinct.
- `Stop` / completion events must not force a happy animation after an error state.

## V5.5 Asset Import / Custom Pack

Only after bundled assets pass.

Required constraints:

- local import must copy into app-managed storage.
- manifest validation required before activation.
- no direct external path references at runtime.
- no remote URL loading.
- no embedded scripts.
- no executable assets.
- invalid packs fail safely and preserve the previous active pack.

## Allowed Planning Claim

```text
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
```

## Forbidden Claims Until Accepted

```text
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
asset marketplace ready
```

## V4.x Boundary

V4.x does not include asset, renderer, release packaging, or productization acceptance gates.

V4.x owns OS-level Codex window/session binding feasibility and any later scoped probe / binding / routing work.

Full 3D, action asset development, bundled asset integrity, license / attribution, and asset productization checks belong to V5.x or a later productization track.
