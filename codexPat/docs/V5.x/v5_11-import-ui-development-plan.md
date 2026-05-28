# V5.11 Personalized Asset Import UI Development Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Expose the accepted V5.8 local asset import path in Desktop Manager without changing renderer security boundaries.

V5.11 is a UI and diagnostics phase. It must not add remote upload, provider calls, arbitrary path loading, marketplace behavior, or production release claims.

## User Flow

1. User opens Desktop Manager.
2. User chooses a local personalized asset manifest.
3. UI runs the same V5.8 manifest validation rules.
4. Valid packs are copied into app-managed storage.
5. Imported pack appears in a local asset pack list with sanitized metadata.
6. Invalid packs fail with stable reason codes and preserve the current active pack.

## Implementation Scope

- Add a Manager import surface for local manifests.
- Reuse V5.8 validation and app-managed storage behavior.
- Show sanitized pack metadata only: pack id, display name, renderer kind, action coverage, imported timestamp, validation status.
- Add user-facing errors for missing core action, invalid renderer kind, forbidden path/URL/script field, missing file, malformed manifest.
- Keep CSS fallback and current renderer behavior unchanged.

## Out Of Scope

- Runtime activation from UI.
- External provider upload.
- Photo-to-3D generation.
- Remote asset download.
- Marketplace.
- Production signed release.

## Acceptance

- Valid local sprite and GLTF packs import through UI.
- Invalid manifest does not change current active pack.
- UI output and evidence do not expose full local paths, workspace path, config path, token, Authorization, raw payload, prompt text, or remote URL.
- Existing CLI V5.8 smoke remains passing.

## Evidence

- `docs/V5.x/evidence/v5_11-import-ui-smoke-YYYY-MM-DD.md`
- `docs/V5.x/v5_11-final-acceptance-report.md`

## Allowed Claim

```text
V5.11 personalized asset import UI passed for tested local manifest import scenarios.
```

## Forbidden Claims

```text
photo-to-3D ready
provider integration verified
remote asset loading ready
asset marketplace ready
production signed release ready
```
