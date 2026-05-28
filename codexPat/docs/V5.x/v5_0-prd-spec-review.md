# V5.0 PRD Spec Review

status: passed-planning

date: 2026-05-28

## Review Scope

This review compares V5.0 planning against the active product direction: keep V3/V4 Agent/Codex integration stable while improving the desktop pet visual system.

## PRD Alignment

Aligned:

- V5.0 does not change Codex event sources.
- V5.0 keeps the pet driven by accepted state/action IDs.
- V5.0 adds asset and renderer architecture before visual expansion.
- V5.0 preserves multi-instance behavior by keeping renderer state per PetInstance.
- V5.0 keeps security and privacy boundaries explicit.

## Product Risks

| Risk | Severity | Decision |
| --- | --- | --- |
| V5 could be mistaken for production release readiness. | Medium | Explicit forbidden claim added. |
| GLTF prototype could be mistaken for full 3D readiness. | Medium | V5.3 claim is prototype-only. |
| Asset import could expose local paths or scripts. | High if unbounded | V5.5 remains optional and gated by manifest validation plus app-managed storage. |
| Renderer could receive raw Agent payloads. | High | Renderer boundary forbids raw payload input. |
| Visual work could regress V3/V4 integration. | Medium | V3/V4 smoke remains in V5 acceptance. |

## Drift Assessment

No major PRD drift is present in the V5.0 planning documents.

Known limitation:

- V5.0 is contract and architecture work only. It should not be sold as visual upgrade completion.

## Go / No-go

Go for V5.0 implementation planning.

No-go for claiming any of:

```text
2D asset pack ready
3D ready
custom asset import ready
production signed release ready
```

