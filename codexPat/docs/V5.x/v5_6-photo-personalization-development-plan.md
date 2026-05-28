# V5.6 Photo Personalization Development Plan

status: passed-scoped

date: 2026-05-28

## Goal

Define the personalized cat asset pipeline without changing the accepted V5.0-V5.5 bundled renderer baseline.

## Scope

- Treat user cat photos as sensitive reference input.
- Prefer local description and prompt-pack generation first.
- Require all generated assets to enter through manifest validation before rendering.
- Keep photos, prompt originals, local paths, tokens, and Authorization values out of renderer and evidence.

## Out Of Scope

- automatic local photo-to-3D generation.
- default external provider upload.
- production 3D readiness.
- custom asset import readiness before V5.8 acceptance.

## Allowed Claim

```text
V5.6 personalized cat asset pipeline design completed with scoped privacy and claim boundaries.
```
