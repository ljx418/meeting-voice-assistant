# V5.2 Renderer Plugin Interface Evidence

status: passed

date: 2026-05-28

## Scope

V5.2 validates that the live desktop pet runtime uses the V5 renderer contract path with CSS fallback.

## Runtime Integration

Runtime path:

```text
CatStateMachine -> CatActionResolver -> RendererRegistry -> CSS RendererAdapter
```

The live pet continues to render with the CSS fallback. Sprite remains selectable through the registry and is not promoted to 3D or production renderer readiness.

## Test Result

Commands:

```bash
pnpm --filter desktop check
pnpm --filter desktop test
pnpm --filter desktop build
pnpm --filter @agent-desktop-pet/petctl test
node scripts/v3_1_runtime_smoke.mjs
node scripts/v4_4_managed_session_smoke.mjs
node scripts/v4_5_managed_tui_preflight_smoke.mjs
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
```

Result: passed.

## Boundary Result

Passed.

Renderer adapters receive safe action IDs, renderer kind, safe profile/pack IDs, playback intent, scale, and visibility.

## Regression Notes

V3/V4 smoke was run serially to avoid the V3.1 hard-limit scenario interfering with V4 managed session setup.

## Allowed Claim

```text
V5.2 renderer plugin interface smoke passed for safe action-id driven renderers.
```

