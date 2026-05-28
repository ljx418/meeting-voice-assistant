# V5.0 Asset Manifest Schema

status: planned-audit-ready

date: 2026-05-28

## Purpose

Define the stable V5 asset pack manifest before new renderers or imported packs are implemented.

The manifest is a safe declarative contract. It must not contain executable behavior, raw Agent payloads, remote URLs, arbitrary local paths, shell commands, shader source, bone manipulation scripts, or renderer internals.

## Manifest Shape

```json
{
  "schemaVersion": "5.0",
  "packId": "bundled-cat-sprite-v2",
  "version": "1.0.0",
  "rendererKind": "sprite",
  "license": {
    "type": "bundled",
    "attribution": "Agent Desktop Pet"
  },
  "assets": {
    "idle": { "assetId": "idle", "kind": "clip" }
  },
  "actions": {
    "idle": { "assetId": "idle", "loop": true, "priority": "base" }
  }
}
```

## Required Fields

| Field | Rule |
| --- | --- |
| `schemaVersion` | Must equal the supported V5 schema version. |
| `packId` | Stable safe identifier: `[A-Za-z0-9._-]`, max 64 chars. |
| `version` | Semver-like string, max 32 chars. |
| `rendererKind` | One of `css`, `sprite`, `gltf`, `rive`, `live2d`. |
| `license` | Required for bundled and imported packs. |
| `assets` | Declarative asset IDs only. |
| `actions` | Maps safe action IDs to asset IDs. |

## Required Core Actions

Manifest validation fails if any required core action is missing:

```text
idle
thinking
running
success
warning
error
need_input
sleeping
```

## Optional Actions

Missing optional actions fall back to `idle` and record a warning:

```text
walk
blink
stretch
tease
```

## Forbidden Manifest Content

```text
remote URL
absolute local path
relative path escape
shell command
script source
executable asset
raw PetEvent
raw Agent payload
prompt text
tool command text
token
Authorization
workspace path
config path
full local path
```

## Validation Requirements

- Invalid schema fails before renderer activation.
- Missing required core action fails before renderer activation.
- Missing optional action records warning and falls back to `idle`.
- Unknown action IDs are rejected unless explicitly listed as optional extension IDs in a future schema.
- Unknown renderer kinds fail safely and preserve the previous active renderer.
- Imported assets, if later implemented, must be copied into app-managed storage before activation.

## Evidence Requirements

V5.0 evidence must include:

- valid manifest accepted.
- missing core action rejected.
- missing optional action falls back to `idle`.
- forbidden URL/path/script fields rejected.
- previous active pack preserved after invalid manifest.
