# V5.x Detailed Design

status: planned-audit-ready

date: 2026-05-28

## Purpose

V5.x turns the current CSS-only desktop cat into a renderer and asset system that can support higher-quality 2D assets, bundled GLTF/Three.js prototypes, bundled 3D action clips, and a later manifest-validated local asset import flow.

V5.x does not change the Codex monitoring contract. The reliable state sources remain the accepted V3/V4 sources. V5 only consumes the already-sanitized pet state/action output.

## Current Implementation Baseline

Current desktop implementation:

- `apps/desktop/src/main.ts` renders a CSS cat DOM tree directly.
- `apps/desktop/src/pet-states.ts` defines the eight accepted `CatState` values.
- `apps/desktop/src/state-machine.ts` queues and prioritizes state transitions.
- `apps/desktop/src/styles.css` defines the visual cat profiles and state animations.
- `apps/desktop/src-tauri/src/main.rs` owns built-in cat profiles and per-instance profile selection.
- `packages/pet-protocol/src/types.ts` constrains `PetEvent.level`, `PetEvent.action`, and accepted sound values.

This means V5 should add a renderer boundary after `CatStateMachine`, not before `PetEvent` validation.

## Target Flow

```text
Agent / Codex / petctl / MCP
  -> PetEvent validation and routing
  -> desktop event bridge
  -> per-instance CatStateMachine
  -> CatActionResolver
  -> AssetManifestRegistry
  -> RendererRegistry
  -> RendererAdapter
  -> visible pet animation
```

Only safe `CatState` / `SafeActionId` values cross into the renderer layer.

## Core State And Action Contract

Required core states/actions:

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

Optional bundled actions:

```text
blink
walk
stretch
tease
```

Optional actions must never be required for correctness. If an optional action is missing, the resolver falls back to `idle` and records a sanitized warning.

## Proposed Module Boundary

```text
apps/desktop/src/
  assets/
    asset-manifest.ts
    asset-pack-validator.ts
    asset-pack-loader.ts
    bundled-packs/
      css-default.manifest.json
      sprite-v2.manifest.json
      gltf-prototype.manifest.json
  renderer/
    renderer-contract.ts
    renderer-registry.ts
    css-renderer.ts
    sprite-renderer.ts
    gltf-renderer.ts
  state/
    cat-action-resolver.ts
```

The exact file layout can be adjusted during implementation, but the dependency direction must remain:

```text
state/action -> manifest -> renderer
```

Renderer code must not import petctl, Codex session code, hook payload types, or raw `PetEvent` payloads.

## Renderer Contract

```ts
export type SafeActionId =
  | "idle"
  | "thinking"
  | "running"
  | "success"
  | "warning"
  | "error"
  | "need_input"
  | "sleeping"
  | "blink"
  | "walk"
  | "stretch"
  | "tease";

export type RendererKind = "css" | "sprite" | "gltf" | "rive" | "live2d";

export type PlaybackIntent = {
  loop: boolean;
  priority: "base" | "transient" | "urgent";
  durationMs?: number;
};

export type SafeRendererProfile = {
  profileId: string;
  rendererKind: RendererKind;
  packId: string;
  scale: number;
};

export type PetRenderer = {
  mount(container: HTMLElement, profile: SafeRendererProfile): void;
  setAction(actionId: SafeActionId, playback: PlaybackIntent): void;
  setScale(scale: number): void;
  setVisible(visible: boolean): void;
  dispose(): void;
};
```

Allowed renderer inputs:

- safe action ID.
- renderer kind.
- safe profile/pack IDs.
- loop / one-shot playback intent.
- scale and visibility.

Forbidden renderer inputs:

- raw `PetEvent`.
- raw Agent/Codex payload.
- prompt text.
- tool command text.
- terminal text.
- transcript path.
- workspace/config/full local paths.
- token or Authorization header.
- remote URL.
- shell command or script source.

## Asset Manifest Responsibilities

The manifest layer must:

- validate `schemaVersion`, `packId`, `version`, `rendererKind`, `license`, `assets`, and `actions`.
- reject unknown renderer kinds.
- reject missing required core actions.
- reject remote URLs, absolute paths, path traversal, executable/script fields, and raw payload-like fields.
- preserve the previous active renderer/pack when validation fails.
- expose only sanitized diagnostics.

Detailed schema: `docs/V5.x/v5_0-asset-manifest-schema.md`.

## Renderer Phases

### V5.0 Asset System Freeze

Design and validate the contract without changing user-visible renderer behavior.

Implementation scope:

- Type definitions for manifest, renderer kind, safe action IDs.
- Validator tests for valid/invalid manifests.
- Resolver contract for state/action fallback.
- Security scan fixtures.

No 2D/3D readiness claim is allowed.

### V5.1 Sprite / 2D Asset Pack v2

Add a bundled 2D sprite renderer and bundled 2D asset pack.

Implementation scope:

- Sprite manifest.
- Sprite renderer adapter.
- Core state visuals for all eight core states.
- Visual evidence for every core state.
- CSS renderer remains fallback.

### V5.2 Renderer Plugin Interface

Move renderer selection behind `RendererRegistry`.

Implementation scope:

- Registry lifecycle: mount, switch, dispose.
- Per-instance renderer state.
- CSS renderer adapter around the existing DOM/CSS cat.
- Tests proving renderer adapters receive safe action IDs only.

### V5.3 GLTF / Three.js Prototype

Add bundled GLTF/GLB renderer prototype only.

Implementation scope:

- Bundled model asset only.
- Transparent window compatibility.
- Nonblank canvas checks.
- Basic action switching.
- Performance baseline.

This is not `3D ready`.

### V5.4 Bundled 3D Action Asset Pack

Add bundled 3D clips for the core states.

Implementation scope:

- Core action clip map.
- Priority and transition rules.
- Distinct `error` and `need_input` clips.
- No success override after an active error.
- License and attribution audit.

### V5.5 Local Custom Asset Import

Optional for V5.x final.

Implementation scope, if included:

- Manifest-validated local import.
- Copy assets into app-managed storage.
- Reject remote URLs, script/executable assets, and arbitrary runtime paths.
- Preserve previous active pack on failure.

If not implemented, V5.x final must explicitly say local custom import remains planned/not-ready.

## Visual Evidence Requirements

Every renderer claim needs visual evidence:

- one screenshot or short recording per core action.
- evidence index with renderer kind, action ID, pack ID, and date.
- nonblank canvas check for GLTF/Three.js.
- drag/transparent-window observation.
- performance note for animation loops.

Evidence must not include raw prompt text, tool command text, tokens, config paths, workspace paths, or full local paths.

## Performance Baseline

Minimum target for local macOS evidence:

- idle animation does not produce visible stutter.
- drag remains responsive while animation is active.
- GLTF prototype records approximate CPU/GPU/memory observation.
- hidden pets should pause or reduce renderer work where technically feasible.

Exact numeric budgets should be frozen in the phase-specific V5.3 plan after the prototype approach is selected.

## Claim Boundary

Allowed planning claim:

```text
V5.x Cat Renderer & Asset System detailed design is audit-ready for scoped 2D, renderer-interface, bundled GLTF prototype, bundled 3D action, and optional local custom asset import work.
```

Forbidden until accepted:

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

