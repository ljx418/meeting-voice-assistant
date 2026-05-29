# V5.11 Manual Import Fixtures

These fixtures are for Desktop Manager manual acceptance only.

## Manifests

- `sprite/manifest.json`: valid local sprite pack.
- `gltf/manifest.json`: valid local GLTF pack with safe local `.gltf` files.
- `invalid/manifest.json`: intentionally invalid pack that references `../idle.png` and must be rejected.

## Expected Results

- Sprite import succeeds.
- GLTF import succeeds.
- Invalid import fails with a stable validation error.
- The UI list must not show the full source path after import.
- V5.11 must not activate these packs for any pet.
