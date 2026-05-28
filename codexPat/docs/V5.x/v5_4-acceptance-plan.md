# V5.4 Acceptance Plan

status: passed-scoped

date: 2026-05-28

## Required Evidence

- Generated GLB contains all eight core action clips.
- Clip output data differs across actions.
- GLB contains no external URI, absolute local path, token text, auth header text, workspace path, config path, raw payload text, or script-like text.
- GLTF renderer switches clips through safe action IDs.
- CSS fallback remains available.

## Checks

- `node scripts/generate_v5_3_gltf_asset.mjs`
- `node scripts/v5_3_gltf_asset_smoke.mjs`
- `node scripts/v5_4_gltf_action_pack_smoke.mjs`
- `pnpm --filter desktop test`
- `pnpm --filter desktop check`
- `pnpm --filter desktop build`

## Allowed Claim

```text
V5.4 bundled 3D action asset pack smoke passed for core pet states.
```

## Forbidden Claims

```text
3D ready
production 3D renderer ready
custom asset import ready
Rive ready
Live2D ready
production signed release ready
```
