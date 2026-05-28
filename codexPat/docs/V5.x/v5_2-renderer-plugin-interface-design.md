# V5.2 Renderer Plugin Interface Design

status: planned-audit-ready

date: 2026-05-28

## Runtime Flow

```text
PetEvent
  -> CatStateMachine
  -> CatActionResolver
  -> RendererRegistry
  -> RendererAdapter
```

## Default Renderer

The live desktop pet continues to use CSS fallback as the default renderer.

Sprite renderer remains available through the registry, but V5.2 does not make sprite the default live renderer.

## Boundary

Renderer adapters receive only:

- safe action ID.
- renderer kind.
- safe profile ID.
- safe pack ID.
- playback intent.
- scale.
- visibility.

They do not receive event bodies, agent bodies, prompt content, tool content, credential material, local filesystem locations, network locations, command content, or executable script content.

