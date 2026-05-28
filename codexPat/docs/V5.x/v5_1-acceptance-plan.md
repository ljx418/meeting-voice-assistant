# V5.1 Acceptance Plan

status: planned-audit-ready

date: 2026-05-28

## Acceptance Goal

V5.1 passes only if the bundled 2D sprite pack covers all core pet states, renderer inputs remain safe, visual evidence exists, and V3/V4/V5.0 regressions still pass.

## Required Checks

Sprite coverage:

- every core action has a bundled sprite asset.
- manifest validates.
- renderer accepts safe action IDs only.
- unavailable renderer still falls back to CSS.

Visual evidence:

- generated visual fixture for all eight core actions.
- evidence index records action ID and renderer kind.
- `error` and `need_input` are visually distinct.
- `thinking` and `running` are visually distinct.

Regression:

```bash
pnpm --filter desktop check
pnpm --filter desktop test
pnpm --filter @agent-desktop-pet/petctl test
node scripts/v3_1_runtime_smoke.mjs
node scripts/v4_4_managed_session_smoke.mjs
node scripts/v4_5_managed_tui_preflight_smoke.mjs
```

## Pass / Block / Fail

Passed:

- visual fixture generated.
- unit tests pass.
- runtime regressions pass against real desktop app.
- no forbidden claim is used as ready.

Blocked:

- desktop health unavailable.
- visual fixture cannot be generated.

Failed:

- missing sprite for a core state.
- renderer receives unsafe payload.
- manifest accepts forbidden content.

