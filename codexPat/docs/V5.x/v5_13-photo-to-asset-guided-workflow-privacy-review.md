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

Forbidden:

- default photo upload.
- raw photo persistence without explicit user action.
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
