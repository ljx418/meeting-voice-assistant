# V1.1-C Frontend Unit-Level Navigation Plan

文档状态：implemented and V1.1-C-RC real data_service HTTP smoke passed.
日期：2026-05-20。

## Scope

This phase implements manual unit-level source navigation inside Source Preview Drawer:

```text
Source Library / Source Detail
-> Preview
-> Source Preview Drawer
-> DocumentUnit outline
-> select unit
-> load unit detail
-> render unit-level preview
```

## Implemented

- `sources.listUnits(workspaceId, sourceId, request?)`
- `sources.getUnit(workspaceId, sourceId, unitId)`
- DocumentUnit list mapper
- DocumentUnit detail mapper
- capability-gated unit outline
- selected unit detail panel
- load-more pagination
- drawer-local list/detail error states
- escaped text rendering for unit preview

## Not Implemented

- EvidenceSpan highlight
- offset-based highlight
- precise citation backjump
- answer citation direct unit jump as release-gate capability
- frontend parser
- multi-format ingestion UI

## Verification

```text
npm run check
Boundary checks passed
91 tests passed
production build passed
```

Real data_service HTTP smoke passed against `http://127.0.0.1:8003`:

- capability manifest reported `document_units=true`, `unit_level_navigation=true`, `evidence_spans=false`, and `citation_backjump=false`;
- source-level preview regression passed;
- unit list returned a backend-generated `DocumentUnit`;
- selected unit detail loaded and rendered;
- pagination with `has_more=true` returned a non-duplicate next page;
- unknown unit returned 404;
- artifact-like unit id returned 422;
- smoke workspace was archived.

## Declaration

```text
ResearchNotebook V1.1 Unit-Level Source Navigation is integration-ready for data_service-supported text sources.
```
