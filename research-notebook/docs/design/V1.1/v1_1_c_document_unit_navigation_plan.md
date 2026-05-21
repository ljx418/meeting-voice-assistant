# V1.1-C-A DocumentUnit Navigation Plan

文档状态：V1.1-C-A implemented as contract discovery / disabled shell；full V1.1-C remains blocked by backend contract。
日期：2026-05-20。

## Decision

Go for V1.1-C-A only.

No-Go for full V1.1-C Unit-Level Navigation implementation.

## Implemented Scope

- Confirmed/extended `DocumentUnit` DTO with `order_index` and `preview_available`.
- Added `DocumentUnitListResponse` draft type.
- Kept `sources.getUnit(workspaceId, sourceId, unitId)` as `capability_missing` shell.
- Added query key placeholders:
  - `['source-units', workspaceId, sourceId]`;
  - `['source-unit', workspaceId, sourceId, unitId]`.
- Source Preview Drawer now renders a Document Units section.
- Units returned by preview are metadata-only and non-clickable.
- If manifest says `document_units=false`, returned units are ignored and shown as disabled/ignored state.
- If manifest says `document_units=true` and `unit_level_navigation=false`, returned units can display metadata but navigation remains disabled.

## Still Blocked For Full V1.1-C

Full V1.1-C requires:

- `document_units=true`;
- `unit_level_navigation=true`;
- stable unit list/detail route or preview-by-unit request;
- pagination contract;
- unknown unit not found semantics;
- artifact_ref / slug / path rejection;
- no raw filesystem/cache/artifact physical paths;
- backend-only smoke fixtures.

## Declaration

Allowed:

```text
ResearchNotebook V1.1-C-A DocumentUnit navigation disabled shell is ready.
Unit-level navigation remains NOT_READY until data_service provides and smokes the DocumentUnit route/model/pagination contract.
```

Still prohibited:

- unit-level navigation ready;
- EvidenceSpan highlight ready;
- precise citation backjump ready;
- multi-format ingestion ready;
- assessment ready;
- quality governance console ready;
- graph editing/governance ready;
- cloud sync/collaboration ready.
