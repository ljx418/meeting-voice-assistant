# V5.0 Acceptance Plan

status: planned-audit-ready

date: 2026-05-28

## Acceptance Goal

V5.0 passes only when the asset manifest contract, safe renderer boundary, fallback behavior, and claim/security language are audit-ready and covered by tests or evidence.

## Required Checks

Design evidence:

- `docs/V5.x/v5_0-asset-manifest-schema.md`
- `docs/V5.x/v5_0-security-boundary.md`
- `docs/V5.x/v5_0-architecture-design.md`
- `docs/V5.x/v5_x-detailed-design.md`
- `docs/V5.x/v5_x-development-scope.md`

Validation evidence must cover:

- valid manifest accepted.
- missing `idle` rejected.
- missing any other required core action rejected.
- missing optional action falls back to `idle` with sanitized warning.
- remote URL rejected.
- absolute local path rejected.
- relative path escape rejected.
- script/executable-like field rejected.
- unknown renderer kind rejected.
- previous active renderer/pack preserved after invalid manifest.

Security evidence must prove:

- no raw `PetEvent` enters renderer adapters.
- no raw Agent/Codex payload enters renderer adapters.
- no prompt text, tool command text, terminal text, token, Authorization header, transcript path, workspace path, config path, or full local path is recorded in evidence.

## Regression

Minimum regression before V5.0 acceptance:

```bash
pnpm --filter desktop check
pnpm --filter @agent-desktop-pet/petctl test
node scripts/v3_1_runtime_smoke.mjs
node scripts/v4_4_managed_session_smoke.mjs
```

If desktop is not running for runtime smoke, evidence must remain blocked rather than passed.

## Claim Scan

Forbidden claims may only appear in forbidden/not-ready context:

```text
2D asset pack ready
3D ready
Rive ready
Live2D ready
custom asset pack import ready
production signed release ready
```

## Pass / Block / Fail Rules

Passed:

- design docs complete.
- validator/security evidence complete.
- required checks pass.
- no forbidden claim used as ready.

Blocked:

- runtime smoke cannot run because desktop is unavailable.
- renderer/manifest implementation is not yet testable.

Failed:

- validator accepts forbidden URL/path/script content.
- renderer can receive raw Agent/Codex payload.
- evidence leaks sensitive content.

