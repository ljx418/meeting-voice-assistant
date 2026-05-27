# V5.x Claim Matrix

status: planned

date: 2026-05-26

## Allowed Planning Claims

```text
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
V4.x does not include asset, renderer, release packaging, or productization acceptance gates.
```

## Not-ready Claims

```text
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
asset marketplace ready
```

## Boundary Rules

- V5.x renderer work must not change PetEvent security boundaries.
- Agents may only request safe state/action IDs, not renderer internals.
- Asset packs must not reference arbitrary external paths or remote URLs.
- User import is out of scope until bundled assets and manifest validation pass.
- Rive, Live2D, and GLTF claims must be separate; one renderer passing does not imply another.
- Bundled asset integrity, license / attribution, and asset productization checks belong to V5.x or a later productization track, not V4.x.
