# V5.x Acceptance Plan

status: planned

date: 2026-05-26

## Acceptance Principle

V5.x cannot pass by only showing the existing CSS cat profiles.

Every renderer or asset claim must have visual evidence, security evidence, and regression evidence. A 3D prototype does not imply Rive, Live2D, user upload, marketplace, or photo customization readiness.

## Required Gates

| Gate | Required Result |
| --- | --- |
| Asset manifest validation | Valid packs load; invalid packs fail safely. |
| Core action coverage | `idle`, `thinking`, `running`, `success`, `warning`, `error`, `need_input`, `sleeping` have accepted visual behavior. |
| Fallback behavior | Missing optional action falls back to `idle` and records warning. |
| Renderer isolation | Renderer consumes safe action IDs only, not raw Agent payloads. |
| Window behavior | Transparent window, drag, scale, and position persistence still work. |
| Performance | CPU/GPU usage and memory remain acceptable on target macOS hardware. |
| Security scan | No external paths, URLs, scripts, shell commands, or raw Agent payloads in asset packs. |
| Claim scan | Forbidden asset claims appear only in forbidden / not-ready contexts. |

## Manual Visual Scenarios

1. Switch through every core state and confirm the animation is visually distinct.
2. Confirm `thinking` and `running` are low-distraction loops.
3. Confirm `error` and `need_input` are obvious enough to notice.
4. Confirm `success` does not override an active `error` state incorrectly.
5. Confirm drag remains smooth while the renderer is animating.
6. Confirm hidden/minimized pets do not waste renderer work.
7. Confirm switching asset packs does not reset unrelated instance state.

## Required Regression

V5.x must preserve:

```bash
node scripts/v3_1_runtime_smoke.mjs
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
pnpm --filter desktop check
pnpm --filter desktop build
```

Additional renderer-specific smoke should be added when implementation begins.

## Required Evidence

Planned files:

- `docs/V5.x/v5_0-asset-system-freeze.md`
- `docs/V5.x/v5_1-sprite-asset-pack-v2-evidence-YYYY-MM-DD.md`
- `docs/V5.x/v5_2-renderer-plugin-interface-evidence-YYYY-MM-DD.md`
- `docs/V5.x/v5_3-gltf-3d-prototype-evidence-YYYY-MM-DD.md`
- `docs/V5.x/v5_4-3d-action-asset-pack-evidence-YYYY-MM-DD.md`
- `docs/V5.x/v5_x-final-acceptance-report.md`

## Forbidden Claims Before Final Acceptance

```text
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
asset marketplace ready
```
