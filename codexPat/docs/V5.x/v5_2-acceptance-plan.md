# V5.2 Acceptance Plan

status: planned-audit-ready

date: 2026-05-28

## Required Checks

- desktop state updates call `CatActionResolver`.
- renderer adapter receives safe action IDs only.
- CSS fallback remains default live renderer.
- sprite renderer remains selectable by registry without becoming default runtime renderer.
- default and non-default pets keep separate state storage keys.
- V3/V4 runtime smokes still pass.

## Regression

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

## Pass / Block / Fail

Passed:

- contract integration tests pass.
- real desktop app regression passes.
- no forbidden claim is used as ready.

Blocked:

- desktop health unavailable.

Failed:

- renderer receives unsafe payload.
- fallback renderer unavailable.
- V3/V4 monitoring semantics regress.

