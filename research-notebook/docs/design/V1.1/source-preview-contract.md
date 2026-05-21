# V1.1 Source Preview Contract

文档状态：V1.1-C-RC real data_service HTTP smoke passed；source-level preview and manual unit navigation are integration-ready for supported text sources。

## Purpose

Source Preview 负责把 V1.0 的 citation metadata 升级为可打开的来源上下文。V1.1-B 已实现 source-level preview：Source Library / Source Detail Preview entry -> Source Preview Drawer -> data_service source preview route。

## DTO

```ts
type DocumentUnit = {
  unit_id: string;
  source_id: string;
  unit_type: "text" | "page" | "slide" | "section" | "transcript_segment" | "json_node";
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

type SourcePreview = {
  source_id: string;
  title?: string;
  source_type?: string;
  preview_available: boolean;
  content_type?: "text/plain" | "text/markdown" | "text/html";
  text_preview?: string;
  units?: DocumentUnit[];
  next_cursor?: string;
  artifact_refs?: string[];
  unsupported_reason?: string;
  preview_truncated?: boolean;
  preview_size_bytes?: number;
  max_preview_size_bytes?: number;
};
```

V1.1-B 只使用：

- `source_id`;
- `title`;
- `source_type`;
- `preview_available`;
- `content_type`;
- `text_preview`;
- `artifact_refs`;
- `unsupported_reason`;
- preview size / truncation metadata if provided.

V1.1-B 不依赖：

- `units`;
- `unit_id`;
- `evidence_id`;
- offsets;
- locators.

V1.1-C-A can map `units` as metadata-only when `document_units=true`, but it must not make those units clickable or claim unit-level navigation ready.

V1.1-C-BE adds dedicated backend unit list/detail routes. V1.1-C frontend uses those routes for manual unit-level navigation. Source preview still does not return units by default, so V1.1-B behavior remains stable.

## Required Backend Semantics

- Preview route must accept registry `source_id`, not llmwiki slug/page ref.
- `artifact_ref` is metadata only and must not be parsed as filesystem path.
- Large unit lists must provide `limit` / `cursor` / `page_token`, or frontend must cap rendering and show first-N state.
- V1.1-C-BE uses `/sources/{source_id}/units` and `/sources/{source_id}/units/{unit_id}` for DocumentUnit list/detail.
- If backend returns markdown/html, response must include `content_type`.
- Frontend must sanitize markdown/html and must not render backend content with unchecked `dangerouslySetInnerHTML`.

## V1.1-B Current Behavior

`sources.preview(workspaceId, sourceId)` is integrated through `src/shared/api/dataServiceClient.ts`.

UI behavior:

- Source Library / Source Detail preview entry can open the Source Preview drawer.
- Drawer first reads `capabilities.get(workspaceId)`.
- If manifest does not advertise source-level preview for the source type, UI shows unsupported and does not call preview route.
- If manifest supports the source type, drawer calls `sources.preview(workspaceId, sourceId)`.
- Drawer renders escaped `text_preview`, source metadata, artifact refs as metadata only, and truncation metadata.
- Preview failure remains drawer-local.
- Answer/evidence remains visible.
- Ready claim is limited to source-level preview for data_service-supported text sources.

## V1.1-B Entry Gate

V1.1-B requires data_service to provide or freeze:

1. capability/version manifest route;
2. manifest with `source_preview=true` or `source_level_preview=true`;
3. source preview route;
4. preview route accepts registry `source_id`;
5. preview route does not require llmwiki slug/page ref;
6. preview response does not contain raw filesystem path, cache path, or artifact physical path;
7. preview response declares `content_type`;
8. unsupported source type has stable unavailable/unsupported response.

Current entry gate result:

```text
READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
```

The local data_service working tree now exposes `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview` for source-level text preview. ResearchNotebook V1.1-B frontend route adaptation and real data_service smoke have passed for text source-level preview.

## Query / Citation Relationship

V1.1-B release-gate entry is:

```text
Source Library / Source Detail -> Preview button -> Source Preview Drawer
```

V1.1-B does not require answer citation to automatically open preview.

Optional enhancement, after manifest support exists:

- if `AnswerEvidence.sourceId` is a registry source id and capability manifest declares source-level preview available, citation may open source-level preview;
- `sourceRef`, slug, page id, or `artifact_ref` must not be sent to preview route;
- this does not make precise citation backjump ready.

## Content Safety

- `text/plain` renders as escaped text.
- `text/markdown` renders as escaped text unless a sanitizer is explicitly added and tested.
- `text/html` must not render as HTML unless a sanitizer is explicitly added and tested.
- Unknown `content_type` renders as text or unsupported.
- Backend content must not be rendered through unchecked `dangerouslySetInnerHTML`.
