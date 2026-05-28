# V5.1 Sprite Asset Pack v2 Evidence

status: passed

date: 2026-05-28

## Scope

This evidence covers V5.1 bundled 2D sprite asset pack smoke for core pet states.

It does not claim GLTF, 3D, Rive, Live2D, custom import, remote asset loading, marketplace, or production signed release readiness.

## Implementation Under Test

- bundled inline SVG sprite definitions.
- `sprite-v2` asset manifest.
- `SpriteRenderer` adapter.
- `RendererRegistry` sprite selection with CSS fallback preserved.

## Core Action Coverage

Covered actions:

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

## Test Result

Command:

```bash
pnpm --filter desktop test
```

Result: passed.

Observed:

```text
tests=28
pass=28
fail=0
```

V5.1-specific cases:

- sprite v2 manifest validates.
- every core action has a bundled sprite frame.
- sprite frames do not contain network locations, local filesystem locations, or script-like content.
- sprite renderer is selected without changing CSS fallback behavior.

## Renderer Boundary Result

Passed.

The sprite renderer consumes safe action IDs, renderer kind, safe profile/pack IDs, playback intent, scale, and visibility only.

## License / Attribution

The bundled sprite pack is project-authored static SVG data and is attributed to Agent Desktop Pet.

## Allowed Claim

```text
V5.1 bundled 2D sprite asset pack smoke passed for core pet states.
```

## Forbidden Claims Not Made

```text
3D ready
Rive ready
Live2D ready
custom asset pack import ready
production signed release ready
```

