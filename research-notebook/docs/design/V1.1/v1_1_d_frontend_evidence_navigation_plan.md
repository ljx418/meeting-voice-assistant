# V1.1-D Frontend Evidence Navigation Plan

文档状态：implemented as API-adapter/UI smoke path；real data_service HTTP smoke passed；browser visual smoke passed.
日期：2026-05-20.

## Scope

Implement the frontend path:

```text
workspace answer citation -> Source Preview Drawer -> DocumentUnit detail -> EvidenceSpan detail -> safe text highlight
```

This phase does not implement V1.2, multi-format ingestion, Assessment, Quality/Governance console, graph editing, cloud sync, or source trace integration.

## Implemented

- `sources.getEvidenceSpan(workspaceId, sourceId, unitId, evidenceId)` target wrapper.
- EvidenceSpan DTO mapping with id validation and offset basis/range/text basis fields.
- Query evidence mapping already preserves `sourceId`, `unitId`, and `evidenceId`.
- `EvidenceList` can mark a citation jumpable only when manifest flags and per-evidence ids are present.
- Workspace query panel opens `SourcePreviewDrawer` from jumpable evidence.
- `SourcePreviewDrawer` loads source preview, selected unit detail, EvidenceSpan detail, and highlights supported offsets.
- Highlight is disabled for missing/unsupported/out-of-range offsets and id/schema mismatches.
- Unit/source/evidence failures remain local to the drawer.

## Verification

```text
npm run check
Boundary checks passed
94 tests passed
production build passed
```

Added UI smoke coverage:

- answer citation with `sourceId + unitId + evidenceId` opens preview drawer;
- drawer loads unit detail;
- drawer loads EvidenceSpan detail;
- EvidenceSpan text is highlighted;
- source-level preview remains visible.

## Not Executed In This Phase

Browser visual smoke against local `data_service` was executed in V1.1-D-RC.

Real data_service HTTP smoke was executed later through:

```text
node scripts/v1_1_d_evidence_smoke.mjs
```

It verified capability flags, unit list/detail, workspace query evidence with `source_id + unit_id + evidence_id`, EvidenceSpan detail, and the supported offset contract.

Browser visual smoke command:

```text
npm run smoke:v1.1-d-browser
```

It verified source preview opening, unit navigation, jumpable citation click, and visible EvidenceSpan highlight.

## Declaration

```text
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.
ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query citation path.
```

Still not ready:

- source trace integration;
- all session query precise navigation;
- all source-type precise backjump;
- multi-format ingestion;
- assessment;
- quality governance console;
- graph editing/governance;
- cloud sync/collaboration.
