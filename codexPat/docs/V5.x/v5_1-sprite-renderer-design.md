# V5.1 Sprite Renderer Design

status: planned-audit-ready

date: 2026-05-28

## Design

V5.1 adds a bundled sprite renderer based on inline SVG sprite definitions.

The renderer consumes only:

- safe action ID.
- renderer kind.
- safe profile ID.
- safe pack ID.
- playback intent.
- scale.
- visibility.

## Asset Model

Each core action maps to a bundled static SVG view definition.

The sprite pack is represented as TypeScript data:

```text
actionId -> sprite frame definition
```

No external file path, remote URL, script, shell command, raw Agent payload, or prompt/tool content is accepted.

## Visual Evidence

Visual fixtures are generated as static local HTML evidence files under V5.x evidence output. They show all eight core states in one grid.

This is sufficient for V5.1 bundled sprite smoke. Full runtime renderer switching remains V5.2.

