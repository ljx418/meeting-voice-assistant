# V5.0 Final Acceptance Report

status: passed

date: 2026-05-28

## Scope

V5.0 completed Asset System Freeze implementation only.

Implemented scope:

- TypeScript asset manifest types.
- SafeActionId and renderer kind types.
- Asset manifest validator.
- CatActionResolver.
- Renderer contract type.
- RendererRegistry interface.
- CSS renderer fallback wrapper.
- Unit / fixture tests.
- Evidence documentation.

Not implemented:

- high-quality 2D asset pack.
- sprite renderer visual readiness.
- Three.js / GLTF production renderer.
- 3D readiness.
- Rive / Live2D readiness.
- custom asset import activation.
- remote asset loading.
- arbitrary local path references.
- production signed release readiness.
- V3/V4 Codex monitoring semantic changes.

## Manifest Validator Result

Result: passed.

Evidence:

- `docs/V5.x/evidence/v5_0-asset-validator-smoke-2026-05-28.md`

Validated:

- valid manifest accepted.
- every required core action missing case rejected.
- optional actions fall back to `idle` with sanitized warnings.
- remote URL rejected.
- absolute local path rejected.
- relative path escape rejected.
- script/executable-like field rejected.
- unknown renderer kind rejected.
- nested raw-payload-like fields rejected.
- invalid pack activation preserves previous active pack.

## Renderer Boundary Result

Result: passed.

Renderer adapter receives only:

- safe action ID.
- renderer kind.
- safe profile/pack IDs.
- playback intent.
- scale.
- visibility.

Renderer adapter does not receive event bodies, agent bodies, hook bodies, terminal bodies, bridge bodies, prompt content, tool content, credential material, auth header material, local filesystem locations, network locations, command content, or executable script content.

## Fallback Result

Result: passed.

- CSS renderer remains fallback.
- unavailable renderer kind falls back to CSS.
- invalid pack activation preserves previous active pack.
- missing optional action falls back to `idle`.
- missing required core action fails validation.
- transient `success` does not overwrite active `error` or `need_input`.

## Regression Result

Commands executed with real local desktop app available:

```bash
pnpm --filter desktop check
pnpm --filter desktop test
pnpm --filter @agent-desktop-pet/petctl test
node scripts/v3_1_runtime_smoke.mjs
node scripts/v4_4_managed_session_smoke.mjs
node scripts/v4_5_managed_tui_preflight_smoke.mjs
```

Results:

| Check | Result |
| --- | --- |
| desktop check | passed |
| desktop test | passed |
| petctl test | passed |
| V3.1 runtime smoke | passed |
| V4.4 managed session smoke | passed |
| V4.5 managed TUI preflight smoke | passed |

Note:

- The first V3/V4 smoke attempt was blocked because desktop health was unavailable.
- The desktop app was then started locally and the runtime smokes were rerun against the real local app.
- The rerun passed.

## Security Scan Result

Result: passed.

No evidence or smoke summary records credential material, auth header material, event bodies, prompt content, tool content, local filesystem locations, network locations, command content, or executable script content as accepted renderer/manifest input.

## Claim Scan Result

Result: passed.

Allowed claim:

```text
V5.0 asset system contract frozen with manifest validation and security boundary evidence.
```

Forbidden claims were not made as ready:

```text
2D asset pack ready
3D ready
Rive ready
Live2D ready
custom asset pack import ready
production signed release ready
```

## PRD Spec Review

Result: passed.

V5.0 remains aligned with the PRD boundary:

- renderer and asset contract only.
- no new Codex monitoring semantics.
- no visual asset readiness claim.
- no production release readiness claim.

## Remaining Blockers For V5.1

V5.1 must not start until it has its own phase-specific plan, acceptance plan, PRD/spec review, and audit.

Known V5.1 blockers:

- choose bundled 2D sprite asset format.
- define visual evidence capture method.
- define visual regression screenshots or recordings for all eight core states.
- confirm license / attribution for bundled 2D assets.
- preserve CSS fallback behavior after sprite renderer introduction.

## Final Decision

V5.0 final acceptance passed.

The only allowed final claim is:

```text
V5.0 asset system contract frozen with manifest validation and security boundary evidence.
```
