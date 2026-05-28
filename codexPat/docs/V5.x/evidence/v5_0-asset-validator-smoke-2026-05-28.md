# V5.0 Asset Validator Smoke Evidence

status: passed

date: 2026-05-28

## Scope

This evidence covers V5.0 Asset System Freeze only.

It verifies manifest schema, validator behavior, CatActionResolver fallback, RendererRegistry CSS fallback, and renderer boundary constraints.

It does not verify or claim sprite renderer readiness, 2D asset pack readiness, GLTF/Three.js production rendering, 3D readiness, Rive readiness, Live2D readiness, custom asset import activation, remote asset loading, or production signed release readiness.

## Implementation Under Test

- TypeScript asset manifest contract.
- Safe action ID and renderer kind types.
- Asset manifest validator.
- Asset pack activation helper.
- CatActionResolver.
- Renderer contract.
- RendererRegistry interface.
- CSS renderer fallback wrapper.

## Unit / Fixture Smoke Result

Command:

```bash
pnpm --filter desktop test
```

Result: passed.

Observed coverage:

- valid CSS fallback manifest accepted.
- missing `idle` rejected.
- missing `thinking` rejected.
- missing `running` rejected.
- missing `success` rejected.
- missing `warning` rejected.
- missing `error` rejected.
- missing `need_input` rejected.
- missing `sleeping` rejected.
- missing optional `blink` falls back to `idle` with sanitized warning.
- missing optional `walk` falls back to `idle` with sanitized warning.
- missing optional `stretch` falls back to `idle` with sanitized warning.
- missing optional `tease` falls back to `idle` with sanitized warning.
- remote URL rejected.
- absolute local path rejected.
- relative path escape rejected.
- script/executable-like field rejected.
- unknown renderer kind rejected.
- invalid pack activation preserves previous active pack.
- valid pack activation replaces active pack.
- nested raw-payload-like fields rejected.
- core CatState values map to safe action IDs.
- transient `success` does not overwrite active `error`.
- transient `success` does not overwrite active `need_input`.
- unavailable renderer kind falls back to CSS.
- CSS renderer wrapper records only safe renderer metadata.

Summary:

```text
tests=24
pass=24
fail=0
```

## Typecheck Result

Command:

```bash
pnpm --filter desktop check
```

Result: passed.

## Renderer Boundary Result

Passed.

The V5.0 renderer contract only exposes:

- safe action ID.
- renderer kind.
- safe profile ID.
- safe pack ID.
- playback intent.
- scale.
- visibility.

The renderer contract does not expose event bodies, agent bodies, hook bodies, terminal bodies, bridge bodies, prompt content, tool content, credential material, auth header material, local filesystem locations, network locations, command content, or executable script content.

## Fallback Result

Passed.

- CSS renderer remains fallback.
- invalid pack activation preserves previous active pack.
- missing optional action falls back to `idle`.
- missing required core action fails validation.
- transient `success` does not overwrite active `error` or `need_input`.

## Security Redaction Result

Passed.

Evidence and smoke output were recorded without credential material, auth header material, event bodies, prompt content, tool content, or local filesystem locations.

## Claim Boundary

Allowed claim:

```text
V5.0 asset system contract frozen with manifest validation and security boundary evidence.
```

Forbidden claims remain not made:

```text
2D asset pack ready
3D ready
Rive ready
Live2D ready
custom asset pack import ready
production signed release ready
```
