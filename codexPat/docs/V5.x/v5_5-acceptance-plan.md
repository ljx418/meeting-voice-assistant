# V5.5 Acceptance Plan

status: passed-scoped

date: 2026-05-28

## Required Evidence

- Default runtime renderer remains CSS.
- Explicit `gltf` selection resolves the bundled GLTF manifest.
- Unsupported but known renderer kinds fall back to CSS.
- Invalid renderer strings fall back to CSS.
- Renderer selection does not introduce URLs, local paths, raw payloads, token text, or auth header text.

## Checks

- `pnpm --filter desktop test`
- `pnpm --filter desktop check`
- `pnpm --filter desktop build`

## Allowed Claim

```text
V5.5 local renderer selection smoke passed for CSS fallback and bundled GLTF prototype renderer.
```

## Forbidden Claims

```text
3D ready
custom asset import ready
remote asset loading ready
production signed release ready
```
