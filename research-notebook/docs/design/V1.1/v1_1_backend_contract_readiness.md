# V1.1 Backend Contract Readiness

文档状态：V1.1-BE backend contract implemented in local data_service working tree；V1.1-B frontend integration completed for source-level text preview。
日期：2026-05-19。

## 1. data_service Version / Commit

Current workspace Git HEAD:

```text
426f9917
```

V1.1-BE backend changes are currently in the local `data_service/` working tree and are not represented by a dedicated committed data_service hash in this workspace.

## 2. Routes Exposed

V1.1-BE adds two target HTTP routes:

```text
GET /api/workspaces/{workspace_id}/capabilities
GET /api/workspaces/{workspace_id}/sources/{source_id}/preview
```

No `/api/v1/knowledge/*` route is added for this feature.

## 3. Response Contract

Capability manifest:

```text
status/data/warnings/next_actions envelope
schema_version = v1.1-source-preview
source_preview = true
source_level_preview = true
document_units = false
evidence_spans = false
unit_level_navigation = false
precise_span_highlight = false
citation_backjump = false
supported_source_types = text/source only
```

Source preview:

```text
registry source_id only
content_type = text/plain
preview_available true for supported text sources
preview_available false for unsupported source types
preview_truncated / preview_size_bytes / max_preview_size_bytes included
no DocumentUnit / EvidenceSpan / locator fields exposed
```

## 4. Backend Test Results

Focused source preview tests:

```text
python3 -m pytest backend/tests/test_target_http_source_preview.py -q
5 passed
```

Route guard and closure compatibility tests:

```text
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_source_preview.py -q
16 passed
```

## 5. Backend-Only Smoke Results

Backend-only smoke generated sanitized fixtures for:

- capability manifest;
- text source preview success;
- unsupported preview;
- not found source id;
- artifact_ref rejected as source id.

## 6. Fixtures

data_service fixtures:

```text
backend/tests/fixtures/research_notebook/source_preview/capability-manifest-source-preview.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-text-success.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-unsupported.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-not-found.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-artifact-ref-rejected.json
```

ResearchNotebook copied fixtures:

```text
fixtures/real/v1_1/source-preview/capability-manifest-source-preview.json
fixtures/real/v1_1/source-preview/source-preview-text-success.json
fixtures/real/v1_1/source-preview/source-preview-unsupported.json
fixtures/real/v1_1/source-preview/source-preview-not-found.json
fixtures/real/v1_1/source-preview/source-preview-artifact-ref-rejected.json
```

Fixture hygiene check:

```text
No /Users, file://, cache_path, artifact_path, physical_path, /tmp/, /private/, debug_path, or raw path keys.
```

## 7. Known Unsupported Types

Current V1.1-BE manifest only declares:

```text
text -> source-level preview
```

JSON, PPT, video, audio, DocumentUnit, EvidenceSpan, unit navigation, and precise span highlight remain not ready.

## 8. Source Trace Status

V1.1-BE does not fix or re-declare source trace.

Current status remains:

```text
source trace integration: NOT_READY
trace-unavailable fallback: DEGRADED_ACCEPTED
```

Source preview route success must not be treated as source trace integration success.

## 9. OpenAPI / Schema

The route contract is exposed through FastAPI's generated OpenAPI schema once the backend app is running.

The dedicated human-readable contract is recorded in:

```text
data_service/docs/V1.7/research-notebook-source-preview-contract.md
```

## 10. V1.1-B Frontend Entry Gate Decision

V1.1-B frontend implementation has consumed this backend contract after the local data_service working tree exposed the required routes.

Current decision:

```text
CONSUMED_BY_FRONTEND_INTEGRATION_SMOKE_FOR_TEXT_SOURCE
```

ResearchNotebook V1.1-B has now adapted the real routes and passed source-level text preview smoke. See `v1_1_source_preview_smoke_report.md` for the frontend integration result.
