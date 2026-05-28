# V5.0 Renderer And Asset Architecture Design

status: planned-audit-ready

date: 2026-05-28

## Target Architecture

```text
PetEvent
  -> Event Bridge
  -> PetInstance State
  -> CatStateMachine
  -> CatActionResolver
  -> AssetManifestRegistry
  -> RendererRegistry
  -> Renderer Adapter
      - CSSRenderer
      - SpriteRenderer
      - GltfRenderer
      - future RiveRenderer
      - future Live2DRenderer
```

## Module Plan

Suggested module locations:

```text
apps/desktop/src/
  renderer/
    renderer-contract.ts
    renderer-registry.ts
    css-renderer.ts
    sprite-renderer.ts
    gltf-renderer.ts
  assets/
    asset-manifest.ts
    asset-pack-loader.ts
    asset-pack-validator.ts
    bundled-packs/
  state/
    cat-action-resolver.ts
```

Exact file names may adapt to the existing desktop code layout, but the boundaries must remain.

## Renderer Contract

Renderer adapters receive safe commands only:

```ts
type PetRenderer = {
  mount(container: HTMLElement, profile: SafeRendererProfile): void;
  setAction(actionId: SafeActionId, playback: PlaybackIntent): void;
  setScale(scale: number): void;
  setVisible(visible: boolean): void;
  dispose(): void;
};
```

No renderer adapter receives raw PetEvent or raw Agent payload.

## Action Resolution

Action resolution is responsible for:

- mapping state/action to safe action IDs.
- preserving error state from inappropriate success override.
- falling back optional missing actions to `idle`.
- reporting validation warnings.

## Renderer Registry

Renderer registry is responsible for:

- selecting renderer by safe `rendererKind`.
- falling back to the existing CSS renderer when a renderer is unavailable.
- disposing previous renderer before switching renderer kind.
- keeping renderer state per PetInstance.

## Visual Evidence Flow

Each renderer phase must produce visual evidence:

```text
core action -> renderer frame/animation -> screenshot or recording -> evidence index
```

V5.3 and later must include nonblank canvas checks and performance notes.

## Non-goals

```text
remote asset loading
marketplace
photo customization
arbitrary local model import
production signing/notarization
OS-level Codex binding
```
