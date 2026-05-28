# V5.1 Visual Regression Evidence

status: passed

date: 2026-05-28

## Scope

V5.1 visual fixture for the bundled 2D sprite asset pack.

## Generated Evidence

Generated fixture:

- `docs/V5.x/evidence/v5_1-sprite-visual-fixture-2026-05-28.html`
- `docs/V5.x/evidence/v5_1-sprite-visual-fixture-2026-05-28.png`

Generation command:

```bash
node scripts/v5_1_generate_sprite_visual_evidence.mjs
```

Screenshot command:

```bash
npx playwright screenshot <fixture> <png-output>
```

## Visual Coverage

The fixture contains all eight core actions:

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

Visual differentiation:

- `thinking` uses a distinct blue/teal thinking palette.
- `running` uses a distinct motion palette.
- `success` uses a green positive palette.
- `warning` uses an amber alert palette.
- `error` uses a red crouch/error palette.
- `need_input` uses a purple attention palette.
- `sleeping` uses a muted sleep palette.

## Result

Passed for V5.1 bundled 2D sprite visual smoke.

This is not a 3D readiness claim and does not claim production release readiness.

