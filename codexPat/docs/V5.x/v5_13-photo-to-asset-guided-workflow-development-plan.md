# V5.13 Photo-To-Asset Guided Workflow Development Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Provide a privacy-preserving guided workflow where users can use their cat photo or description to create standardized external-generation prompts and import instructions.

The product does not upload photos by default and does not generate 3D assets locally in V5.13.

## Required Behavior

- User can enter cat traits or optionally select a local photo for reference.
- The app generates a standardized prompt pack for sprite or GLTF/action assets.
- If a photo is selected, the app stores only user-approved metadata needed for prompts, not the raw photo by default.
- The workflow outputs required action list, file naming rules, manifest template, and import checklist.
- Generated assets still must pass V5.8/V5.11 validation before use.

## Out Of Scope

- Automatic photo-to-3D generation.
- Default provider upload.
- Remote asset loading.
- Provider integration verified claim.

## Acceptance

- Prompt pack covers all core actions.
- Workflow produces manifest template and import checklist.
- No raw photo, local path, prompt text containing sensitive path, token, Authorization, or provider payload appears in evidence.
- User can take generated instructions to create assets externally and import them through the existing local import path.

## Evidence

- `docs/V5.x/evidence/v5_13-photo-guided-workflow-smoke-YYYY-MM-DD.md`
- `docs/V5.x/v5_13-final-acceptance-report.md`

## Allowed Claim

```text
V5.13 photo-guided personalized asset workflow passed for local prompt and import-instruction generation.
```
