# V5.11 Import UI Smoke Evidence

status: automated-passed / manual-ui-pending

date: 2026-05-28

## Scope

This evidence covers V5.11 automated backend and frontend checks for local personalized asset import UI.

It does not claim final V5.11 acceptance until Desktop Manager manual UI import is completed.

## Commands

```bash
node scripts/v5_11_import_ui_smoke.mjs
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop build
node scripts/v5_8_personalized_asset_pipeline_smoke.mjs
```

## Automated Results

- Tauri asset import command tests: passed.
- Desktop typecheck: passed.
- Desktop unit tests: passed.
- Cargo check: passed.
- Petctl regression tests: passed.
- Desktop build: passed.
- V5.8 personalized asset pipeline smoke: passed.
- Smoke output redaction scan: passed.

## Covered Automated Cases

- Valid sprite pack import.
- Duplicate pack id replacement.
- Missing core action rejected.
- Manifest forbidden path traversal rejected.
- GLTF external resource URI rejected.
- Sanitized imported pack list shape.
- Import UI source compiles and does not add runtime activation.

## Pending Manual UI Cases

- Open Desktop Manager.
- Import a real local sprite manifest.
- Import a real local GLTF/GLB manifest.
- Import an invalid manifest and confirm stable error.
- Confirm imported pack list shows sanitized metadata only.
- Confirm no cat runtime renderer changes during V5.11 import-only flow.

## Claim Decision

Do not claim V5.11 passed until manual UI cases are accepted.
