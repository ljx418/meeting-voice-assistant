# V1.1 Capability Manifest Contract

文档状态：V1.1-D/S1-FE browser smoke passed for supported text-source evidence navigation；S2 all-source-type contract discovery completed and found non-text source types not ready。

## Purpose

Capability manifest 是 V1.1 前端判断 Source Preview、DocumentUnit、EvidenceSpan、格式支持和 precise navigation 是否可用的唯一服务侧事实源。

前端不得硬编码 JSON/PPT/video/audio ready，也不得在 manifest 未声明时显示某格式已支持。

## Minimum DTO

```ts
type CapabilityManifest = {
  service_version?: string;
  schema_version?: string;
  capabilities: {
    source_preview: boolean;
    document_units: boolean;
    evidence_spans: boolean;
    source_level_preview: boolean;
    unit_level_navigation: boolean;
    precise_span_highlight: boolean;
    citation_backjump: boolean;
  };
  supported_source_types: Array<{
    source_type: string;
    preview: "none" | "source" | "unit" | "span";
    locators: Array<"page_no" | "slide_no" | "timestamp" | "json_path" | "offset">;
  }>;
};
```

## Current Behavior

ResearchNotebook now calls the manifest target route through `dataServiceClient.capabilities.get(workspaceId)`:

```text
GET /api/workspaces/{workspace_id}/capabilities
```

If the route is missing, the adapter normalizes the result to `capability_missing`. If the response shape is incompatible, the adapter normalizes it to `version_or_schema_mismatch`.

## V1.1-B Gate Result

The local data_service working tree now exposes a ResearchNotebook capability manifest route:

```text
GET /api/workspaces/{workspace_id}/capabilities
```

ResearchNotebook V1.1-B has adapted this route in `dataServiceClient.ts`, and real data_service smoke passed for source-level text preview.

## V1.1-C-BE Gate Result

The local `data_service` working tree now exposes a DocumentUnit backend contract. After backend route/test enablement, the manifest may report:

```json
{
  "source_preview": true,
  "document_units": true,
  "evidence_spans": true,
  "source_level_preview": true,
  "unit_level_navigation": true,
  "precise_span_highlight": true,
  "citation_backjump": true
}
```

For supported text sources, `supported_source_types[].preview` may be `"unit"`.

V1.1-C frontend now consumes these flags to enable manual unit-level source navigation in Source Preview Drawer. V1.1-C-RC real data_service HTTP smoke passed, so the feature is integration-ready for data_service-supported text sources.

## V1.1-D-BE Gate Result

The local `data_service` working tree now exposes an EvidenceSpan backend contract. After backend route/test/smoke enablement, the manifest may report:

```json
{
  "source_preview": true,
  "document_units": true,
  "evidence_spans": true,
  "source_level_preview": true,
  "unit_level_navigation": true,
  "precise_span_highlight": true,
  "citation_backjump": true
}
```

These true values are necessary but not sufficient for frontend precise navigation. ResearchNotebook now additionally requires each evidence item to carry `sourceId + unitId + evidenceId` before the UI calls the EvidenceSpan route.

V1.1-D frontend API-adapter/UI smoke is ready. Real data_service HTTP smoke has verified the manifest flags, workspace query jumpable evidence, unit detail route, EvidenceSpan detail route, and offset contract. Browser visual smoke has verified the visible citation -> preview drawer -> unit detail -> EvidenceSpan highlight path.

## V1.1-S2 All-Source-Type Discovery Result

S2 discovery observed the current manifest as:

```text
supported_source_types = text:unit
```

Therefore:

- `text` remains the only source type with preview/unit/evidence navigation ready in V1.1.
- `pdf`, `pptx`, `json`, `markdown`, `html`, `video`, and `audio` are not manifest-ready.
- Frontend must continue showing unsupported / unavailable for non-text source types.
- S3 must update data_service backend contracts before S4 can enable any non-text frontend behavior.

## Capability Rules For V1.1-B

- `source_preview=false` -> UI does not call preview route.
- `source_level_preview=false` -> UI does not call preview route.
- `supported_source_types[].preview="none"` -> UI shows unsupported.
- `supported_source_types[].preview="source"` -> UI may call source-level preview for that source type.
- `supported_source_types[].preview="unit"` or `"span"` -> V1.1-B may use source-level preview only and must not declare unit/span ready.
- `document_units=true` with `unit_level_navigation=false` -> V1.1-C-A may display units metadata-only if backend preview returns `units`.
- `document_units=false` -> V1.1-C-A must ignore preview-returned units or show an explicit disabled/ignored state.
- Missing manifest -> `capability_missing` disabled shell.
- Backend/network failure -> backend unavailable state.
- Schema mismatch -> version/schema mismatch state.

## Rules

- Manifest route shape 只能在 `src/shared/api/dataServiceClient.ts` 适配。
- Feature modules 不直接 fetch。
- Feature modules 不拼 route string。
- 后端未声明 capability 时，UI 必须显示 unsupported / capability missing。
- `source trace integration` 与 `source preview integration` 是两个独立声明，不得互相替代。
- `citation_backjump=true` in the manifest does not by itself make a citation jumpable. The evidence payload must include `sourceId + unitId + evidenceId`. Browser visual smoke has passed for supported text-source workspace and session query paths; all-source-type coverage remains not ready.
