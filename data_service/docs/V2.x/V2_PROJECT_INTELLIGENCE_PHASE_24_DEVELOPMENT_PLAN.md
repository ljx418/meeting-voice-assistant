# V2.4 Phase 24 Development Plan: Architecture Quality Overlay

> Scope: close the V2.4 minor deferred quality overlay item.
> Baseline: V2.4 Phase 23 closure accepted with quality overlay deferred.

Date: 2026-06-02

## Goal

Add quality governance target support for V2.4 architecture artifacts and apply approved rules as read-time overlays to architecture read payloads.

## Implementation

- Add supported target types:
  - `architecture_role`
  - `architecture_layer`
  - `architecture_boundary`
  - `architecture_pattern`
  - `architecture_drift_finding`
- Extend quality target resolver to read V2.4 architecture artifacts.
- Apply approved quality plan overlays to architecture role/layer/boundary/pattern/drift read payloads.
- Do not mutate architecture source artifacts.

## Out of Scope

- New UI.
- New quality rule types.
- Automatic correction of architecture artifacts.
- LLM-generated governance rules.
