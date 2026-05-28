# V5.1 PRD Spec Review

status: passed-planning

date: 2026-05-28

## Review Scope

Review V5.1 planned work against the product direction: improve pet visual quality while preserving local agent integration safety.

## Alignment

Aligned:

- V5.1 only adds bundled 2D sprite assets.
- V5.1 does not change Codex monitoring.
- V5.1 does not load remote assets.
- V5.1 keeps renderer inputs limited to safe action IDs and safe profile/pack metadata.
- V5.1 preserves CSS fallback.

## Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Sprite smoke could be mistaken for 3D readiness. | Medium | Claim matrix remains scoped to bundled 2D sprite smoke. |
| Visual evidence could be too weak. | Medium | Generate per-action visual fixture and evidence index. |
| SVG content could behave like scriptable asset content. | Medium | Bundled static TS definitions only; no external SVG file import or script tags. |
| Runtime integration could exceed V5.1 scope. | Low | V5.2 remains the full runtime plugin integration phase. |

## Decision

No major PRD drift found.

Go for V5.1 implementation.

