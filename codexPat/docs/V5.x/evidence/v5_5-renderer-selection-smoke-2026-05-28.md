# V5.5 Renderer Selection Smoke Evidence

status: passed

date: 2026-05-28

## Scope

This evidence covers local explicit renderer selection for bundled CSS, sprite, and GLTF prototype renderers.

## Smoke Result

`pnpm --filter desktop test`: passed.

Covered cases:

- no local selection defaults to CSS.
- explicit `gltf` selects the bundled GLTF prototype manifest.
- unavailable renderer kind falls back to CSS.
- invalid renderer string falls back to CSS.

## Runtime Boundary

Runtime renderer selection uses bundled manifests only. It does not accept remote URLs, arbitrary local paths, user-uploaded packs, shell commands, raw event payloads, prompt text, tool command text, tokens, or Authorization header values.

## Claim Boundary

Allowed:

```text
V5.5 local renderer selection smoke passed for CSS fallback and bundled GLTF prototype renderer.
```

Forbidden:

```text
3D ready
custom asset import ready
remote asset loading ready
production signed release ready
```
