# V2.4 Phase 21 Development Plan: Code-Derived Model and Design-Code Drift

> Scope: V2.4 Phase 21 only.
> Baseline: Phase 19 roles/layers and Phase 20 boundaries/patterns are implemented and accepted.

Date: 2026-06-02

## 1. Goal

Phase 21 aggregates V2.4 code-derived architecture facts into a single model and compares it with the V2.3 design-side architecture model when available.

Outputs:

- `code_derived_model.json`
- `design_code_drift.jsonl`

## 2. Implementation Design

Add focused modules:

- `code_model_builder.py`: aggregates roles, layers, boundaries, patterns, summary, source refs.
- `drift.py`: compares design nodes against code-derived model tokens and emits drift findings.

Extend:

- artifact paths and persistence for code-derived model and drift findings;
- service build/read payloads;
- no additional public tools are required beyond existing build/roles/patterns reads for Phase 21.

## 3. Drift Types

Allowed finding types:

```text
DESIGN_LAYER_MISSING_CODE
CODE_LAYER_NOT_IN_DESIGN
ROLE_MISMATCH
BOUNDARY_LEAK
UNMAPPED_PUBLIC_SURFACE
PATTERN_WITHOUT_DESIGN
DESIGN_ONLY_PATTERN
LOW_CONFIDENCE_ROLE
EVIDENCE_MISSING
```

## 4. Out of Scope

Phase 21 must not:

- produce HTML/Mermaid views;
- apply quality rules;
- claim full call graph/data flow/control flow/type inference;
- fail when no design-side model exists; code-derived model must still build.

## 5. Gate

Implementation may start only when this plan, acceptance plan, and audit report exist and the audit report has no open fatal or major finding.
