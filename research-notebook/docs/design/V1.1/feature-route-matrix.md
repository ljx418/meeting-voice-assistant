# ResearchNotebook V1.1 Feature Route Matrix

文档状态：V1.1-D-RC browser visual smoke passed；RC4 source trace backend fix 和 re-smoke passed with scoped source trace integration。
日期：2026-05-22。

## Classification

Every V1.1 feature must be classified as:

- `backed by data_service target route`;
- `adapter shell only`;
- `unsupported`;
- `future backend phase`.

## V1.1 Source Preview / Evidence Navigation

| Feature | Status | Backend route or dependency | Notes |
| --- | --- | --- | --- |
| Capability manifest | backed by data_service target route | `GET /api/workspaces/{workspace_id}/capabilities` | Integrated through `dataServiceClient.capabilities.get(workspaceId)`. Missing manifest maps to `capability_missing`. |
| Source Preview drawer shell | backed by data_service target route | app UI + `sources.preview()` | Opens from Source Library / Source Detail Preview entry and renders source-level preview or drawer-local unavailable state. |
| Source-level preview integration | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview` | Integrated for registry `source_id` and data_service-supported source types. Real smoke passed for text source. |
| Source trace direct route | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace` | V1.1-RC4 backend fix 后 re-smoke observed source create/list/get registry `source_id` and direct trace returned HTTP 200. Source trace integration is LIMITED PASS for RC4-covered registry source_id-backed text sources. |
| DocumentUnit backend list | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}/units` | Integrated through `sources.listUnits`; enabled only when manifest allows unit navigation. |
| DocumentUnit backend detail | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}` | Integrated through `sources.getUnit`; unit id must come from backend DocumentUnit response. |
| DocumentUnit metadata display | adapter shell only | preview response `units` + capability manifest | V1.1-C-A only; metadata-only, non-clickable, shown only when manifest advertises `document_units=true`. |
| Manual unit selection in preview drawer | backed by data_service target route | unit list/detail routes | Integration-ready for data_service-supported text sources after V1.1-C-RC HTTP smoke. |
| Scroll-to-unit / answer citation unit jump | unsupported | none in V1.1-C | Not implemented; this is not precise citation backjump. |
| EvidenceSpan backend detail | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}` | Backend contract ready after V1.1-D-BE tests and smoke; real HTTP smoke now verifies route and offset contract. |
| Query evidence span ids | backed by data_service target route | `POST /api/workspaces/{workspace_id}/query` | Real HTTP smoke observed workspace query evidence with registry `source_id`, backend `unit_id`, and backend `evidence_id` for a text source. Session query is not EvidenceSpan-ready. |
| EvidenceSpan highlight | browser-smoke-ready for supported text workspace query path | EvidenceSpan route + offset semantics | Workspace query citation path implemented, real HTTP-smoked, and browser visual-smoked. |
| Precise citation backjump | browser-smoke-ready for supported text workspace query path | answer citation UX + EvidenceSpan route | Supported only for workspace query citations carrying `source_id + unit_id + evidence_id`; session/all-source coverage remains NOT_READY. |
| Answer citation opens preview | unsupported in V1.1-B release gate | optional only after manifest support | Source Library / Source Detail Preview button is the V1.1-B release-gate entry. |

## V1.1-BE Backend Contract Status

V1.1-BE has added the following backend contract in the local `data_service` working tree:

```text
capability/version manifest
source preview route
registry source_id preview semantics
content_type
unsupported preview response
no raw filesystem/cache/artifact physical path
```

Current state:

```text
Backend source preview contract = READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
Frontend Source Preview integration = INTEGRATION_SMOKE_READY_FOR_TEXT_SOURCE
Source Preview shell = READY_WITH_REAL_ROUTE
```

V1.1-B frontend implementation is complete for source-level preview. V1.1-C frontend implementation and real unit navigation smoke are complete for supported text sources. V1.1-D frontend EvidenceSpan highlight is browser-smoke-ready for supported text-source workspace query citations.

## V1.1-C-A DocumentUnit Shell Status

```text
DocumentUnit DTO = DRAFT_READY
DocumentUnit metadata-only display = READY_DISABLED_SHELL
Unit detail route = SUPERSEDED_BY_V1.1-C_READY
Unit-level navigation = SUPERSEDED_BY_V1.1-C_INTEGRATION_READY_FOR_SUPPORTED_TEXT_SOURCES
EvidenceSpan highlight = SUPERSEDED_BY_V1.1-D_BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
Precise citation backjump = LIMITED_BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
```

## V1.1-C-BE DocumentUnit Backend Contract Status

```text
Backend capability manifest document_units = TRUE
Backend capability manifest unit_level_navigation = TRUE
Backend unit list route = READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
Backend unit detail route = READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
Backend pagination contract = READY
Backend fixtures = SAVED
Frontend unit-level navigation = INTEGRATION_READY_FOR_SUPPORTED_TEXT_SOURCES
Frontend clickable unit outline = READY_IN_SOURCE_PREVIEW_DRAWER
Real unit navigation smoke = PASS
EvidenceSpan highlight = NOT_READY
Precise citation backjump = NOT_READY
```

V1.1-C integration is limited to manual Source Preview Drawer navigation. It does not make answer citation unit jump, EvidenceSpan highlight, or precise citation backjump ready.

## V1.1-D-BE EvidenceSpan Backend Contract Status

```text
Backend capability manifest evidence_spans = TRUE
Backend capability manifest precise_span_highlight = TRUE
Backend capability manifest citation_backjump = TRUE
Backend EvidenceSpan detail route = READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
Workspace query evidence source_id/unit_id/evidence_id = READY_FOR_TEXT_SOURCES
Session query EvidenceSpan shape = NOT_READY
Real data_service HTTP smoke = PASS_WITH_ACCEPTED_DEGRADED_STATES
Browser visual smoke = PASS
Frontend EvidenceSpan highlight = BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
Frontend precise citation backjump = BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
```

V1.1-D frontend has now wired the workspace query citation path to `SourcePreviewDrawer`, `sources.getUnit`, and `sources.getEvidenceSpan`. It passed mocked/API-adapter UI smoke through `npm run check`, `node scripts/v1_1_d_evidence_smoke.mjs` verified the real data_service HTTP route/evidence contract, and `npm run smoke:v1.1-d-browser` verified the browser-visible highlight path.

Current declaration:

```text
Frontend EvidenceSpan highlight = BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
Frontend precise evidence navigation = BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
```

## V1.1-RC4 Source Trace Re-Smoke Status

```text
Registry source_id observed from source create/list/get = TRUE
Workspace query evidence with registry source id = TRUE
Direct source trace route = HTTP 200
Source trace integration = LIMITED_PASS_FOR_RC4_REGISTRY_SOURCE_ID_TEXT_PATH
Trace-unavailable fallback = DEGRADED_ACCEPTED for unsupported or failing trace cases
```

RC4 confirms that Source Preview, DocumentUnit, EvidenceSpan, and Source Trace are separate contracts. Source Trace is now smoke-proven only for the RC4 registry source_id path.

## Boundary Rules

- no `/api/v1/knowledge/*`;
- no direct fetch in feature modules;
- route strings only in `src/shared/api/dataServiceClient.ts`;
- `artifact_ref` is metadata only and never parsed as filesystem path;
- no frontend parser logic;
- no hard-coded JSON/PPT/video/audio support;
- no unsafe backend HTML rendering.
