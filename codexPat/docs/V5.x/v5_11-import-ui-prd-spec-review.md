# V5.11 PRD Spec Review

status: planned-audit-ready

date: 2026-05-28

## Alignment

V5.11 aligns with the PRD goal of making personalized cat assets usable by non-CLI users while preserving the accepted V5.8 local import and privacy boundary.

## Drift Risks

| Risk | Level | Mitigation |
| --- | --- | --- |
| UI import could be mistaken for photo generation. | Medium | Claim matrix keeps photo-to-3D and provider claims forbidden. |
| UI might leak local paths. | High if unbounded | Evidence must scan UI output and docs for full path leakage. |
| Import UI might imply runtime activation. | Medium | V5.11 remains import-only; V5.12 owns runtime rendering. |
| Duplicate or partial imports could leave unclear user state. | Medium | V5.11 freezes duplicate/retry/cancel/rollback behavior before implementation. |

## Audit Opinion

Go for V5.11 implementation only after this plan and acceptance plan are reviewed. No unresolved High risk remains if the implementation reuses V5.8 validation and does not show full local paths.

## Frozen UX Decisions

- Import entry lives in Desktop Manager under a personalized asset pack section.
- File selection accepts a local manifest path; cancelled selection returns `import_cancelled` and does not change state.
- Imported pack list displays only pack id, display name, renderer kind, action coverage count, manifest hash, imported timestamp, and validation status.
- Duplicate `packId` replaces the previous sanitized record only after the new import fully validates and copies successfully.
- Re-importing the same manifest is idempotent except for refreshed `createdAt` / manifest hash if content changed.
- Partial copy failure rolls back app-managed storage for that import attempt and preserves the previous record.
- UI diagnostics show stable reason codes and concise user messages, never raw validator payloads.
- V5.11 does not include pack activation controls; V5.12 owns instance-level activation, restore, and runtime rendering.

## Required Reason Codes

```text
import_cancelled
asset_manifest_not_found
asset_manifest_invalid_json
asset_manifest_schema_invalid
asset_pack_invalid
asset_display_name_invalid
asset_renderer_invalid
asset_license_missing
core_action_missing
asset_missing
asset_file_invalid
asset_file_not_found
asset_manifest_forbidden_content
asset_pack_too_large
asset_symlink_rejected
gltf_external_resource_rejected
gltf_required_extension_rejected
asset_import_copy_failed
```
