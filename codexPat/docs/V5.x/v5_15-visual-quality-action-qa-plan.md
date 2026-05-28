# V5.15 Visual Quality And Action QA Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Harden visual quality, action clarity, performance, and evidence for bundled and imported asset packs.

## Quality Criteria

- Every core action is visually distinguishable.
- `thinking` and `running` are readable but low-distraction loops.
- `error` and `need_input` are prominent and distinct.
- `success` is transient and does not overwrite active error or need_input priority state.
- No blank frames, broken scale, off-canvas rendering, or uncontrolled resizing.

## Required Evidence

- Desktop screenshots or recordings for all core actions.
- Nonblank render check for GLTF/canvas paths.
- Performance baseline for idle and active animation.
- Visual regression notes for imported pack rendering after V5.12.

## Quantitative Thresholds

- Each core action has at least 3 seconds of recording or a fixed-frame screenshot set.
- GLTF/canvas nonblank pixel ratio is greater than 1%.
- Cat bounding box stays inside the viewport with at least 4px margin.
- Action switches contain no full blank frame.
- Idle CPU and memory baselines are recorded.
- Active animation CPU and memory baselines are recorded.
- Hidden/minimized renderer work is reduced or technically justified.
- `warning`, `error`, and `need_input` remain visually distinguishable at 1x and 0.75x scale.
- `success` does not override active `error` or `need_input` priority state.

## Regression

```bash
pnpm --filter desktop test
pnpm --filter desktop check
pnpm --filter desktop build
node scripts/v5_8_personalized_asset_pipeline_smoke.mjs
```

## Allowed Claim

```text
V5.15 visual quality and action QA passed for tested bundled and imported asset scenarios.
```

## Forbidden Claims

```text
production signed release ready
3D ready
asset marketplace ready
provider integration verified
```
