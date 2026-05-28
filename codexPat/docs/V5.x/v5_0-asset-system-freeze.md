# V5.0 Asset System Freeze

status: planned-audit-ready

date: 2026-05-28

## Freeze Decision

V5.0 freezes the renderer and asset contract before new renderer implementation begins.

The frozen boundary is:

```text
CatStateMachine -> CatActionResolver -> AssetManifestRegistry -> RendererRegistry -> RendererAdapter
```

No renderer adapter may consume raw Agent, Codex, hook, terminal, MCP, or HTTP payloads.

## Frozen Core Actions

Required core actions:

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

Required core actions are mandatory for every active asset pack. Missing any required action makes the pack invalid.

## Frozen Optional Actions

Optional actions:

```text
blink
walk
stretch
tease
```

Missing optional actions are not pack failures. They fall back to `idle` and record sanitized warnings.

## Frozen Renderer Kinds

Supported schema-level renderer kinds:

```text
css
sprite
gltf
rive
live2d
```

Only implemented renderer kinds may be activated. Schema recognition does not imply runtime readiness.

## Frozen Fallback Rules

- Existing CSS cat remains the fallback renderer.
- Invalid pack activation preserves the previous active pack.
- Unknown renderer kind fails safely.
- Missing optional action falls back to `idle`.
- Missing required action fails validation before activation.
- A transient `success` action must not overwrite a still-active `error` or `need_input` priority state.

## Frozen Security Boundary

Manifests and renderers must reject or avoid:

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
terminal text
token
Authorization
transcript_path
workspace path
config path
full local path
```

## Frozen Evidence Requirement

V5.0 cannot pass unless evidence covers:

- valid manifest accepted.
- missing core action rejected.
- missing optional action fallback.
- URL/path/script rejection.
- previous active pack preserved after invalid manifest.
- renderer boundary receives safe action IDs only.
- claim scan confirms no visual readiness claim.

## Non-goals

```text
2D asset pack readiness
3D readiness
Rive readiness
Live2D readiness
custom asset import readiness
production signed release readiness
```

