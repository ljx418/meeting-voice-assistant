# V5.8 Local Asset Import Smoke Evidence

status: passed

date: 2026-05-28

## Command

```bash
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
node scripts/v5_8_personalized_asset_pipeline_smoke.mjs
```

## Covered

- valid local GLTF pack imports into app-managed storage.
- valid local sprite pack imports into app-managed storage through petctl unit coverage.
- list returns sanitized pack records.
- activate links an imported pack to a PetInstance.
- missing core action is rejected.
- path traversal is rejected.
- outputs do not leak temp paths, full local user paths, token file names, or Authorization values.

## Claim

```text
V5.8 manifest-validated local personalized asset import passed for tested sprite and GLTF asset packs.
```
