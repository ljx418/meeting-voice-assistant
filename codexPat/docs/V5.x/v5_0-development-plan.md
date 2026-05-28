# V5.0 Development Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Freeze the asset and renderer contract before implementing new visual renderers.

V5.0 must not claim 2D, 3D, Rive, Live2D, custom import, or production release readiness.

## Development Work

1. Define TypeScript asset manifest types.
2. Define safe action IDs and renderer kinds.
3. Implement or prepare validator tests for:
   - valid bundled manifest accepted.
   - missing required core action rejected.
   - missing optional action warning and fallback.
   - remote URL rejected.
   - absolute local path rejected.
   - path traversal rejected.
   - script/executable-like field rejected.
   - unknown renderer kind rejected.
4. Define `CatActionResolver` behavior.
5. Define renderer contract and registry interface without switching user-visible rendering yet.
6. Add design evidence and claim/security scan docs.

## Required Core Actions

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

## Implementation Boundary

Allowed:

- schema and validator.
- safe action resolver.
- renderer contract types.
- CSS renderer fallback design.
- tests and evidence docs.

Not allowed:

- remote asset loading.
- arbitrary local path references.
- user asset import activation.
- Three.js production renderer claim.
- Rive/Live2D readiness claim.
- changes to V3/V4 Codex monitoring semantics.

## Audit Before Code

Before implementation starts, close:

- `docs/V5.x/v5_0-asset-manifest-schema.md`
- `docs/V5.x/v5_0-security-boundary.md`
- `docs/V5.x/v5_0-architecture-design.md`
- `docs/V5.x/v5_x-detailed-design.md`
- `docs/V5.x/v5_x-development-scope.md`

Go condition:

- no High risk in manifest security boundary.
- no High risk in renderer receiving raw Agent payloads.
- no claim language implying 2D/3D/custom import readiness.

## Allowed Claim

```text
V5.0 asset system contract frozen with manifest validation and renderer security boundary ready for implementation.
```

## Forbidden Claims

```text
2D asset pack ready
3D ready
Rive ready
Live2D ready
custom asset pack import ready
production signed release ready
```

