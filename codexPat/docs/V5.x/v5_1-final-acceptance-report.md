# V5.1 Final Acceptance Report

status: passed

date: 2026-05-28

## Scope

V5.1 implemented bundled 2D sprite asset pack smoke for core pet states.

Implemented:

- bundled inline SVG sprite definitions.
- sprite v2 manifest.
- sprite renderer adapter.
- RendererRegistry sprite selection.
- visual fixture generation.
- visual screenshot evidence.
- unit tests and regression checks.

Not implemented:

- full runtime renderer plugin integration across the pet UI.
- GLTF / Three.js production renderer.
- 3D readiness.
- Rive / Live2D readiness.
- custom asset import activation.
- remote asset loading.
- production signed release readiness.

## Evidence

- `docs/V5.x/evidence/v5_1-sprite-asset-pack-v2-evidence-2026-05-28.md`
- `docs/V5.x/evidence/v5_1-visual-regression-2026-05-28.md`

## PRD Spec Review

Result: passed.

V5.1 remains aligned with PRD boundaries:

- visual improvement is bundled and local.
- no V3/V4 Codex monitoring semantic change.
- no network asset loading.
- no custom import activation.
- CSS fallback remains available.

## Plan Drift And False-green Risk Assessment

Result: no High risk.

Notes:

- V5.1 smoke proves bundled 2D sprite pack coverage, not full runtime plugin integration.
- Full runtime renderer integration remains V5.2.
- The final claim is scoped to bundled 2D sprite smoke.

## Test And Regression Result

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

Results:

| Check | Result |
| --- | --- |
| desktop check | passed |
| desktop test | passed |
| desktop build | passed |
| petctl test | passed |
| V3.1 runtime smoke | passed |
| V4.4 managed session smoke | passed after serial rerun |
| V4.5 managed TUI preflight smoke | passed after serial rerun |
| cargo check | passed |

Note:

- The first V4.4/V4.5 attempt was run concurrently with V3.1 hard-limit smoke and failed with `instance_limit_reached`.
- The smoke flow was corrected to run serially after V3.1 cleanup.
- The serial reruns passed.

## Security Scan Result

Result: passed.

Sprite fixtures and evidence do not include accepted network asset locations, arbitrary local filesystem locations, executable content, event bodies, prompt content, or tool content.

## Claim Scan Result

Allowed claim:

```text
V5.1 bundled 2D sprite asset pack smoke passed for core pet states.
```

Forbidden claims remain not made:

```text
3D ready
Rive ready
Live2D ready
custom asset pack import ready
production signed release ready
```

## Remaining Blockers For V5.2

V5.2 must add a phase-specific plan, acceptance plan, PRD/spec review, and plan audit before implementation.

Known V5.2 blockers:

- integrate RendererRegistry into the live pet UI.
- preserve per-instance renderer state.
- prove renderer switch dispose/mount behavior.
- prove default and non-default pets do not share renderer state.

## Final Decision

V5.1 final acceptance passed.

Only this scoped claim is allowed:

```text
V5.1 bundled 2D sprite asset pack smoke passed for core pet states.
```

