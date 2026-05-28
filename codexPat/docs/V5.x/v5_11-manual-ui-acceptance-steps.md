# V5.11 Manual UI Acceptance Steps

status: pending-user-validation

date: 2026-05-28

## Goal

Verify the Desktop Manager import UI with real local manifest files.

## Preconditions

- Desktop app is running.
- At least one valid local sprite manifest exists.
- At least one valid local GLTF/GLB manifest exists.
- At least one invalid manifest exists for rejection testing.

## Steps

1. Open Agent Desktop Pet settings from the tray.
2. Find the `个性化资产包` section.
3. Enter the valid sprite `manifest.json` path.
4. Click `导入`.
5. Confirm the pack appears in the list with pack id, display name, renderer, action count, hash, imported timestamp, and status.
6. Confirm the list does not show the source full local path.
7. Enter the valid GLTF/GLB manifest path.
8. Click `导入`.
9. Confirm the GLTF/GLB pack appears in the list with sanitized metadata.
10. Enter the invalid manifest path.
11. Click `导入`.
12. Confirm a stable Chinese error appears and no current cat renderer changes.
13. Confirm V5.11 has no pack activation control and no cat switches to the imported pack.

## Pass Criteria

- Valid sprite import succeeds.
- Valid GLTF/GLB import succeeds.
- Invalid import fails safely.
- Import path input is cleared after each attempt.
- Imported list does not show full local source paths.
- Current cat runtime renderer does not change.
- No token, Authorization, raw payload, workspace path, config path, full local user path, or remote asset URL appears in evidence.

## If Failed

Record:

- visible error text.
- whether the pack list changed.
- whether any cat renderer changed.
- whether a full local path appeared in the UI.
