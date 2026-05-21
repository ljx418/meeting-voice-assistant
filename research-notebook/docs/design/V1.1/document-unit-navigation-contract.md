# V1.1 DocumentUnit Navigation Contract

文档状态：V1.1-C-RC real data_service HTTP smoke passed；Unit-Level Source Navigation integration-ready for supported text sources。
日期：2026-05-20。

## Purpose

DocumentUnit navigation is the V1.1-C layer after source-level preview. It should allow users to inspect stable source-internal units such as pages, slides, sections, transcript segments, or JSON nodes.

V1.1-C-A does not implement real unit navigation. It only defines the contract, keeps adapter shells, and displays metadata-only units when the backend response and capability manifest allow it.

## Required Backend Gate For Full V1.1-C

Full unit-level navigation requires `data_service` to freeze:

1. capability manifest:
   - `document_units=true`;
   - `unit_level_navigation=true`;
2. stable `DocumentUnit` model;
3. unit list contract with pagination:
   - `limit`;
   - `cursor`;
   - `next_cursor`;
   - `has_more`;
4. unit detail route or equivalent preview-by-unit request:
   - `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}`; or
   - `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview?unit_id=...`;
5. registry `source_id` + stable `unit_id` semantics;
6. unsupported source type response;
7. no raw filesystem path, cache path, artifact physical path, slug, page ref, or private storage filename in response;
8. OpenAPI/schema or equivalent machine-readable contract update.

V1.1-C-BE satisfies the backend side of this gate in the local `data_service` working tree. V1.1-C frontend integration wires the routes, passes mocked adapter/UI tests, and V1.1-C-RC real data_service HTTP smoke passed for supported text sources.

## DTO

```ts
type DocumentUnit = {
  unit_id: string;
  source_id: string;
  unit_type:
    | "text"
    | "page"
    | "slide"
    | "section"
    | "transcript_segment"
    | "json_node";
  title?: string;
  text_preview?: string;
  content_type?: "text/plain" | "text/markdown" | "text/html";
  order_index?: number;
  page_no?: number;
  slide_no?: number;
  timestamp_start_ms?: number;
  timestamp_end_ms?: number;
  json_path?: string;
  artifact_ref?: string;
  preview_available?: boolean;
  preview_truncated?: boolean;
  preview_size_bytes?: number;
  max_preview_size_bytes?: number;
};

type DocumentUnitListResponse = {
  source_id: string;
  items: DocumentUnit[];
  next_cursor?: string | null;
  limit: number;
  has_more: boolean;
  unsupported_reason?: string;
};
```

## V1.1-C-BE Backend Routes

```http
GET /api/workspaces/{workspace_id}/sources/{source_id}/units?limit=50&cursor=...
GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}
```

Rules:

- `source_id` must be a registry source id.
- `unit_id` must be a stable backend-generated DocumentUnit id.
- `artifact_ref`, slug, page ref, raw path, and cache key are rejected as `unit_id`.
- default `limit=50`; maximum `limit=100`.
- `cursor` is opaque.
- invalid cursor returns `422 VALIDATION_ERROR`.
- items are ordered deterministically by `order_index` and `unit_id`.
- unknown source returns `SOURCE_NOT_FOUND`.
- unknown unit returns `UNIT_NOT_FOUND`.
- source preview route does not return units by default.
- EvidenceSpan and precise citation backjump remain disabled.

## V1.1-C Frontend Behavior

- `sources.listUnits(workspaceId, sourceId, request?)` is the only typed wrapper for the unit list route.
- `sources.getUnit(workspaceId, sourceId, unitId)` is the only typed wrapper for unit detail.
- Source Preview Drawer shows unit outline only when manifest advertises `document_units=true`, `unit_level_navigation=true`, and the source type advertises `preview="unit"` or `"span"`.
- `selectedUnitId` is drawer-local state.
- switching source clears selected unit by source-id scoping.
- closing drawer unmounts and clears selected unit.
- load-more failure keeps already loaded units visible.
- unit detail failure is drawer-local and does not clear source-level preview.
- `artifact_ref`, `sourceRef`, slug, page ref, `order_index`, and raw path are never used as unit ids.

## V1.1-C-A Frontend Behavior

- `sources.getUnit(workspaceId, sourceId, unitId)` remains a typed adapter shell and returns `capability_missing`.
- `SourcePreviewDrawer` includes a Document Units section.
- If `document_units=false`, unit metadata is not displayed as available capability.
- If preview response includes `units` while `document_units=false`, the drawer shows `Document units ignored`.
- If `document_units=true` but `unit_level_navigation=false`, units may be displayed as metadata only.
- Unit items are not clickable, focusable as actions, scroll targets, or highlight anchors.
- `artifact_ref` remains metadata only and is never parsed as a path.

## Capability Rules

- `document_units=false` -> do not enable unit outline or navigation.
- `unit_level_navigation=false` -> do not call unit detail route.
- `supported_source_types[].preview="source"` -> source-level preview only.
- `supported_source_types[].preview="unit"` -> enable manual unit-level navigation only when unit routes are available and HTTP smoke passes.
- `supported_source_types[].preview="span"` -> V1.1-C may use unit-level navigation only; it still does not claim EvidenceSpan highlight.

## No False Green

V1.1-C-A can declare:

```text
ResearchNotebook V1.1-C-A DocumentUnit navigation disabled shell is ready.
```

V1.1-C-A cannot declare:

- unit-level navigation ready;
- unit selection ready;
- scroll-to-unit ready;
- unit highlight ready;
- EvidenceSpan highlight ready;
- precise citation backjump ready.

V1.1-C can declare:

```text
ResearchNotebook V1.1 Unit-Level Source Navigation is integration-ready for data_service-supported text sources.
```

It still cannot declare EvidenceSpan highlight, answer citation unit jump, or precise citation backjump ready.
