# V1.1 Evidence Navigation Contract

文档状态：V1.1-D workspace query browser smoke passed；V1.1-S1-FE session query browser smoke passed；S3 markdown/json EvidenceSpan backend/API smoke passed。

## Purpose

Evidence Navigation defines how an answer citation opens source-level, unit-level, or precise span-level context.

## AnswerEvidence Extension

```ts
type AnswerEvidence = {
  evidenceKey: string;
  sourceId?: string;
  sourceRef?: string;
  sourceTitle?: string;
  traceAvailable: boolean;
  artifactRefs?: string[];
  snippet?: string;
  confidence?: number;
  traceUnavailableReason?: "missing_source_id" | "source_ref_not_traceable" | "trace_route_failed";

  unitId?: string;
  evidenceId?: string;
  locator?: {
    pageNo?: number;
    slideNo?: number;
    timestampStartMs?: number;
    timestampEndMs?: number;
    jsonPath?: string;
  };
  previewAvailable?: boolean;
};
```

## EvidenceSpan DTO

```ts
type EvidenceSpan = {
  evidence_id: string;
  source_id: string;
  unit_id?: string;
  snippet?: string;
  start_offset?: number;
  end_offset?: number;
  offset_basis?: "utf8_bytes" | "unicode_codepoints" | "utf16_code_units" | "normalized_text";
  offset_range?: "half_open" | "closed";
  text_basis?: "document_unit_text" | "normalized_source_text";
  locator?: {
    page_no?: number;
    slide_no?: number;
    timestamp_start_ms?: number;
    timestamp_end_ms?: number;
    json_path?: string;
  };
  preview_available?: boolean;
};
```

## Backend Contract Status

V1.1-D-BE adds the backend EvidenceSpan contract in `data_service`:

```text
GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}
```

The route uses registry `source_id`, backend `unit_id`, and backend `evidence_id`.
It rejects artifact refs, slugs, paths, and malformed ids.

Workspace query evidence can now return:

```ts
type QueryEvidence = {
  evidence_key: string;
  source_id?: string;
  source_ref?: string;
  source_title?: string;
  unit_id?: string;
  evidence_id?: string;
  snippet?: string;
  confidence?: number;
  locator?: {
    page_no?: number;
    slide_no?: number;
    timestamp_start_ms?: number;
    timestamp_end_ms?: number;
    json_path?: string;
  };
};
```

Session query evidence is browser-smoke-ready after S1-FIX and S1-FE for data_service-supported text-source session query citations carrying `source_id + unit_id + evidence_id`. S1-FIX proved the API ids; S1-FE proved the browser citation click path through the existing Drawer, DocumentUnit, and EvidenceSpan highlight flow.

S2 all-source-type discovery found no non-text source type with preview/unit/evidence contracts ready at that baseline. S3 then added backend/API evidence support for `markdown` and `json`:

```text
markdown workspace query evidence ids = PASS
markdown EvidenceSpan detail = PASS
json workspace query evidence ids = PASS
json EvidenceSpan detail = PASS
```

S4 has now browser-smoked markdown/json frontend EvidenceSpan navigation for workspace query citations. `pdf`, `pptx`, `html`, `video`, and `audio` remain `NOT_READY_NOT_SMOKED` for EvidenceSpan navigation.

## Navigation Rules

- `sourceId + unitId + evidenceId` -> precise evidence preview only if manifest supports EvidenceSpan navigation and backend returns a valid EvidenceSpan offset contract.
- `sourceId + unitId` -> unit-level preview.
- `sourceId only` -> source-level preview.
- `sourceRef only` -> display-only, no preview call.
- `artifact_ref only` -> metadata only, never path parsing.
- Preview route failure -> drawer-local unavailable; answer/evidence remains visible.

## Offset P0 Rule

Precise highlight is not ready unless backend provides:

- `start_offset`;
- `end_offset`;
- `offset_basis`;
- `offset_range`.

If `offset_basis` is missing, frontend must degrade to unit-level or source-level preview and must not claim precise highlight ready.

V1.1-D-BE offset decision:

```text
offset_basis = normalized_text
offset_range = half_open
text_basis = document_unit_text
```

Offsets are relative to the normalized text of the `DocumentUnit` identified by `unit_id`.

## Frontend V1.1-D Rules

ResearchNotebook now implements the frontend API-adapter/UI path for workspace and supported session query citations carrying `sourceId + unitId + evidenceId`:

- `EvidenceList` shows precise navigation only when the capability manifest advertises `evidence_spans=true`, `precise_span_highlight=true`, `citation_backjump=true`, `document_units=true`, and `unit_level_navigation=true`.
- Each evidence item must also include `sourceId`, `unitId`, and `evidenceId`; manifest truth alone is not sufficient.
- Clicking a jumpable citation opens `SourcePreviewDrawer`, loads source preview, loads the referenced `DocumentUnit`, loads the EvidenceSpan detail, validates ids, and highlights the span.
- EvidenceSpan failure is drawer-local and does not clear the answer, evidence list, source preview, or unit detail.
- Unsupported offset basis/range/text basis, missing offsets, id mismatch, or out-of-range offsets show `Highlight unavailable` and do not fabricate a highlight.

Real data_service HTTP smoke has verified the route/evidence contract for a supported text-source workspace query:

- capability manifest advertised `document_units=true`, `unit_level_navigation=true`, `evidence_spans=true`, `precise_span_highlight=true`, and `citation_backjump=true`;
- workspace query returned evidence carrying registry `source_id`, backend `unit_id`, and backend `evidence_id`;
- the unit-scoped EvidenceSpan route returned `offset_basis=normalized_text`, `offset_range=half_open`, and `text_basis=document_unit_text`;
- unknown evidence returned 404;
- artifact-like evidence id returned 404 instead of the preferred 422 and remains a backend error-semantics gap.

Browser visual smoke has also verified:

- a workspace query answer renders a jumpable citation;
- clicking that citation opens/focuses `SourcePreviewDrawer`;
- the drawer loads source preview, selected DocumentUnit detail, and EvidenceSpan detail;
- a non-empty highlight is visible inside the selected unit detail;
- answer/source preview/unit detail remain visible during the successful path;
- no `/api/v1/knowledge/*` network request was observed.

S1-FE browser smoke has separately verified the session query path:

- session query answer rendered a jumpable citation carrying `source_id + unit_id + evidence_id`;
- clicking the session citation opened/focused `SourcePreviewDrawer`;
- the drawer displayed the source preview, selected the correct DocumentUnit, and rendered the EvidenceSpan highlight;
- the highlighted text was non-empty and inside the selected unit detail;
- answer/source preview/unit detail remained visible;
- no `/api/v1/knowledge/*` network request was observed.

## Current Declaration Boundary

Can declare:

```text
data_service EvidenceSpan backend contract is ready for ResearchNotebook V1.1-D frontend integration after backend change review.
ResearchNotebook V1.1-D EvidenceSpan highlight is browser-smoke-ready for workspace query citations carrying source_id + unit_id + evidence_id.
ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query path.
ResearchNotebook session precise evidence navigation is browser-smoke-ready for data_service-supported text-source session query citations carrying source_id + unit_id + evidence_id.
data_service markdown/json EvidenceSpan backend contracts are API-smoke-ready.
ResearchNotebook markdown/json EvidenceSpan highlight is browser-smoke-ready for workspace query citations carrying source_id + unit_id + evidence_id.
```

Cannot declare:

- all-source-type source trace integration ready;
- all-session precise navigation ready;
- all-source-type precise backjump ready.
- PDF/PPTX/HTML/video/audio precise navigation ready.

## V1.1-S1 Session Query Boundary

V1.1-S1 verified the session query path separately from the workspace query path:

```text
POST /api/workspaces/{workspace_id}/sessions/{session_id}/query
```

Observed result:

```text
Session build = PASS
Session query = HTTP 200
Before S1-FIX session evidence shape = GRAPH_ONLY_NO_EVIDENCE
After S1-FIX session evidence shape = HAS_EVIDENCE_SPAN_IDS
```

The first response returned session graph nodes/edges, but did not return a citation evidence item carrying `source_id + unit_id + evidence_id`. S1-FIX then updated the backend/API contract so session query evidence ids resolve through DocumentUnit detail and EvidenceSpan detail. S1-FE then verified the browser click path. Therefore:

- workspace query EvidenceSpan readiness does not apply to session query;
- session precise navigation is `BROWSER_SMOKE_READY` for the supported text-source session query path;
- session answer citation jump may call EvidenceSpan route only when the evidence item itself carries `source_id + unit_id + evidence_id`;
- this still must not be generalized to all sessions, all source types, or evidence items that lack resolvable ids.

## RC4 Source Trace Re-Smoke Boundary

V1.1-RC4 reran the direct source trace route with a registry `source_id` returned by source create/list/get:

```text
GET /api/workspaces/rn-v11-rc4-trace-1779418233906-workspace/sources/src_cce80f0ca6dad217/trace
```

Result:

```text
HTTP 200 trace/provenance payload
```

Therefore:

- Source Preview success does not prove Source Trace success;
- DocumentUnit navigation success does not prove Source Trace success;
- EvidenceSpan highlight success does not prove Source Trace success;
- source trace integration is `LIMITED PASS` for registry source_id-backed sources covered by RC4 smoke;
- trace-unavailable fallback remains `DEGRADED_ACCEPTED` for unsupported or failing trace cases.
