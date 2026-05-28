# V5.13 Photo-To-Asset Guided Workflow Privacy Review

status: planned-audit-ready

date: 2026-05-28

## Privacy Boundary

Allowed:

- user-entered cat traits.
- user-approved descriptive notes derived from a photo.
- renderer target.
- action list.
- sanitized manifest template.
- optional in-memory photo inspection after explicit user selection.
- user-approved coat, eye, marking, tail, and style notes.

Forbidden:

- default photo upload.
- raw photo persistence without explicit user action.
- EXIF/GPS persistence.
- file name or full path persistence.
- thumbnail persistence by default.
- crash log inclusion of prompt text, photo metadata, file names, or paths.
- provider raw payload.
- full local path.
- workspace path.
- config path.
- token.
- Authorization.
- remote URL in imported manifest.

## Required User Disclosure

The workflow must clearly state that external AI generation is performed outside the app unless a later provider adapter is explicitly enabled and accepted.

## Risk Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| User assumes the app generates 3D locally. | Medium | UI and docs must label this as guided prompt generation. |
| Photo data leaves device unexpectedly. | High if unbounded | No default upload; provider adapter is V5.14+ and explicit opt-in only. |
| Imported assets bypass validation. | High if unbounded | All assets must pass V5.8/V5.11 validation. |

## Data Handling Decisions

- A selected photo may be read into memory only for the active prompt-generation session.
- Raw photo bytes are not persisted by default.
- Thumbnails are not persisted by default.
- EXIF, GPS, original file name, and source path are stripped from saved metadata.
- Saved metadata may contain only user-approved descriptive notes and renderer target.
- Prompt text persistence is opt-in; default evidence records prompt category and action coverage only.
- User can delete saved notes and prompt packs from the guided workflow UI.
- Logs and crash diagnostics must redact prompt text, photo notes, file names, local paths, token, Authorization, provider payloads, and config/workspace paths.
