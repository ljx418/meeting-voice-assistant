# V1.1 DocumentUnit Backend Readiness

文档状态：V1.1-C-BE backend contract complete；superseded by V1.1-C-RC integration-ready state。
日期：2026-05-20。

## 1. Backend Version

- data_service branch: `main`
- data_service base commit observed before local edits: `8872bf822a2c041f64af98f3629a0e224754a4f8`
- implementation state: local data_service working tree changes

## 2. Routes Exposed

```text
GET /api/workspaces/{workspace_id}/capabilities
GET /api/workspaces/{workspace_id}/sources/{source_id}/units
GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}
```

No `/api/v1/knowledge/*` route was added for DocumentUnit.

## 3. Capability Manifest Result

The V1.1-C-BE manifest enables backend DocumentUnit capability:

```text
source_preview=true
document_units=true
source_level_preview=true
unit_level_navigation=true
evidence_spans=false
precise_span_highlight=false
citation_backjump=false
```

For text sources, `supported_source_types[].preview` is `unit`.

## 4. Unit List Response

The unit list route returns envelope-wrapped payload:

```text
data.units.source_id
data.units.items[]
data.units.next_cursor
data.units.limit
data.units.has_more
data.units.unsupported_reason?
```

Pagination rules:

- default limit: `50`
- max limit: `100`
- cursor: opaque
- invalid cursor: `422 VALIDATION_ERROR`
- ordering: deterministic by `order_index`, then `unit_id`

## 5. Unit Detail Response

The unit detail route returns envelope-wrapped payload:

```text
data.unit.unit_id
data.unit.source_id
data.unit.unit_type
data.unit.title
data.unit.text_preview
data.unit.content_type
data.unit.order_index
data.unit.artifact_ref
data.unit.preview_available
data.unit.preview_truncated
data.unit.preview_size_bytes
data.unit.max_preview_size_bytes
```

`unit_id` is backend-generated and stable across list/detail calls for the same source content. It is namespaced by `source_id` and does not expose raw paths, cache keys, or artifact physical paths.

## 6. Error And Unsupported Behavior

- unknown source id: `404 SOURCE_NOT_FOUND`
- unknown unit id: `404 UNIT_NOT_FOUND`
- artifact ref, slug, or path used as unit id: `422 VALIDATION_ERROR`
- unsupported source type: `200 OK`, `items=[]`, `unsupported_reason=source_type_not_supported`

## 7. Backend Tests

Focused verification passed:

```text
python3 -m pytest backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py -q
12 passed

python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py -q
23 passed
```

`python3 -m py_compile backend/app/api/v1/data_service.py` was not used as a verification source because the sandbox blocked writing backend `__pycache__`; pytest imported and executed the module successfully.

## 8. Fixtures Saved

Sanitized fixtures were saved in:

```text
fixtures/real/v1_1/document-units/
```

Fixture files:

- `capability-manifest-document-units.json`
- `document-units-list-success.json`
- `document-unit-detail-success.json`
- `document-unit-not-found.json`
- `document-unit-artifact-ref-rejected.json`
- `document-units-unsupported.json`

Fixture hygiene scan passed for:

```text
/Users
file://
cache_path
artifact_path
physical_path
/private/tmp
/tmp/
C:\
```

## 9. Frontend Entry Decision

```text
data_service DocumentUnit backend contract:
READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW

ResearchNotebook V1.1-C frontend unit navigation:
INTEGRATION_READY_FOR_SUPPORTED_TEXT_SOURCES_AFTER_V1.1-C-RC_SMOKE

ResearchNotebook V1.1-C-A disabled shell:
FALLBACK_BEHAVIOR_WHEN_CAPABILITY_IS_MISSING_OR_UNSUPPORTED
```

## 10. Still Not Ready

- scroll-to-unit
- unit highlight
- EvidenceSpan highlight
- precise citation backjump
- multi-format ingestion
- assessment
- quality governance console
- graph editing/governance
- cloud sync/collaboration
- source trace integration
