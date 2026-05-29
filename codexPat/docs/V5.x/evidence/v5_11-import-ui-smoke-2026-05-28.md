# V5.11 Import UI Smoke Evidence

status: passed

date: 2026-05-28

## Scope

This evidence covers V5.11 automated backend and frontend checks for local personalized asset import UI.

Manual Desktop Manager UI import was completed on 2026-05-29.

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

## Manual UI Cases

- Open Desktop Manager: passed.
- Import real local sprite manifest: passed.
- Import real local GLTF/GLB manifest: passed.
- Import invalid manifest and confirm stable error: passed.
- Confirm imported pack list shows sanitized metadata only: passed by operator confirmation.
- Confirm no runtime activation control exists in V5.11 import-only flow: passed by operator confirmation.

## Claim Decision

V5.11 scoped import UI claim is allowed.
