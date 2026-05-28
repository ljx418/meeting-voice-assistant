# V5.12 Runtime Imported Pack Rendering Acceptance Plan

status: planned-audit-ready

date: 2026-05-28

## Required Checks

- Activate imported pack for one PetInstance.
- Drive all core states and confirm that only the target PetInstance uses imported visuals.
- Confirm default and unrelated pets remain on their selected renderer/profile.
- Delete or invalidate imported pack metadata and confirm CSS fallback.
- Confirm renderer input remains safe and contains no raw source payloads.

## Regression

```bash
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop test
pnpm --filter desktop check
pnpm --filter desktop build
node scripts/v5_8_personalized_asset_pipeline_smoke.mjs
node scripts/v4_4_managed_session_smoke.mjs
```

## Manual Visual Evidence

Screenshots or video must show:

- target cat using imported action visuals.
- default pet unchanged.
- unrelated pet unchanged.
- fallback state after invalid pack.

## Claim Boundary

V5.12 proves runtime use of local imported packs only. It does not prove automatic asset generation or provider integration.
