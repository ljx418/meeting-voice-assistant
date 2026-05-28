# V5.3 Performance Baseline

status: passed-with-risk-note

date: 2026-05-28

## Scope

V5.3 prototype performance and bundle-size baseline.

## Build Result

Command:

```bash
pnpm --filter desktop build
```

Result: passed.

Observed bundle output:

```text
desktop js bundle approx 1458.28 kB
gzip approx 272.45 kB
```

## Risk Note

Three.js significantly increases the desktop frontend bundle size compared with the earlier CSS/sprite-only build.

This is acceptable for V5.3 prototype acceptance, but V5.4/V5.x Final should evaluate:

- code splitting for 3D renderer.
- lazy loading GLTF renderer only when selected.
- preserving CSS/sprite fallback for low-resource environments.

