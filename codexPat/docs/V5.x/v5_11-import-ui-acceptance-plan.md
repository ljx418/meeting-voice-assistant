# V5.11 Personalized Asset Import UI Acceptance Plan

status: planned-audit-ready

date: 2026-05-28

## Required Checks

- Import a valid local sprite pack.
- Import a valid local GLTF pack.
- Reject missing required core action.
- Reject forbidden path traversal, absolute path, remote URL, and script-like fields.
- Verify previous active pack is preserved after invalid import.
- Verify imported metadata is sanitized.
- Verify V5.8 CLI import smoke still passes.

## Manual UI Scenarios

1. Open Desktop Manager and import a valid manifest.
2. Confirm the imported pack appears in the local pack list.
3. Import an invalid manifest and confirm a stable error appears.
4. Confirm no current cat renderer changes during import-only flow.
5. Confirm no local full path is shown in the UI or evidence.

## Regression

```bash
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop test
pnpm --filter desktop check
pnpm --filter desktop build
node scripts/v5_8_personalized_asset_pipeline_smoke.mjs
```

## Claim Boundary

V5.11 only proves local import UI. It does not prove runtime rendering of imported packs; that belongs to V5.12.
