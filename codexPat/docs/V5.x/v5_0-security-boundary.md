# V5.0 Asset And Renderer Security Boundary

status: planned-audit-ready

date: 2026-05-28

## Boundary

V5 renderer work must preserve the existing event safety model:

```text
PetEvent -> CatStateMachine -> safe actionId -> RendererRegistry -> Renderer
```

Agents may influence only safe state/action IDs already accepted by the protocol and state machine. Agents must not directly control renderer internals.

## Allowed Inputs To Renderer

```text
profileId
rendererKind
actionId
playbackIntent
scale
visibility
theme/profile safe IDs
```

## Forbidden Inputs To Renderer

```text
raw PetEvent
raw Agent payload
prompt text
tool command text
terminal text
workspace path
config path
full local path
remote URL
token
Authorization
shell command
script source
shader source from asset pack
bone or rig command from Agent
arbitrary animation name from Agent
```

## Asset Pack Rules

- Bundled packs may use packaged app assets only.
- Runtime renderer must not load arbitrary local paths.
- Runtime renderer must not fetch remote URLs.
- Asset packs must not contain executable scripts.
- Invalid asset packs fail safely.
- Previous active pack remains active after validation failure.
- User import is forbidden until V5.5 and only after bundled packs pass.

## Diagnostics Rules

Diagnostics may record:

- manifest id.
- renderer kind.
- safe action id.
- validation reason code.
- warning count.

Diagnostics must not record:

- raw manifest text if it contains forbidden content.
- local path values.
- prompt/tool command text.
- tokens or authorization values.
- raw Agent payloads.

## Claim Boundary

Passing V5.0 security validation does not mean:

```text
3D ready
custom asset import ready
production signed release ready
Rive / Live2D ready
```
