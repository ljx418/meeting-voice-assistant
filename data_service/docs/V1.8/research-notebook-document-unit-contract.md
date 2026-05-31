# V1.8 ResearchNotebook DocumentUnit Contract

Date: 2026-05-20
Status: implemented for V1.1-C-BE backend contract enablement.

## 1. Scope

This phase opens the minimum target HTTP contract required to unblock ResearchNotebook V1.1-C frontend unit-level navigation integration.

It adds only:

- `GET /api/workspaces/{workspace_id}/sources/{source_id}/units`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}`

It does not add MCP tools, CLI commands, compatibility `/api/v1/knowledge/*` routes, EvidenceSpan routes, precise citation backjump, multi-format ingestion, assessment, graph editing, or quality governance UI.

## 2. Capability Manifest

The existing manifest route now reports DocumentUnit backend capability after route/test enablement:

```json
{
  "capabilities": {
    "source_preview": true,
    "document_units": true,
    "evidence_spans": false,
    "source_level_preview": true,
    "unit_level_navigation": true,
    "precise_span_highlight": false,
    "citation_backjump": false
  },
  "supported_source_types": [
    {
      "source_type": "text",
      "preview": "unit",
      "locators": []
    }
  ]
}
```

EvidenceSpan and citation backjump remain disabled.

## 3. Unit List

Route:

```http
GET /api/workspaces/{workspace_id}/sources/{source_id}/units?limit=50&cursor=...
```

Response data shape:

```json
{
  "units": {
    "source_id": "src_123",
    "items": [
      {
        "unit_id": "unit_1234abcd5678ef90",
        "source_id": "src_123",
        "unit_type": "section",
        "title": "Overview",
        "text_preview": "Queues absorb burst traffic...",
        "content_type": "text/plain",
        "order_index": 0,
        "artifact_ref": "unit://src_123/unit_1234abcd5678ef90",
        "preview_available": true,
        "preview_truncated": false,
        "preview_size_bytes": 1234,
        "max_preview_size_bytes": 50000
      }
    ],
    "next_cursor": null,
    "limit": 50,
    "has_more": false
  }
}
```

Pagination rules:

- default limit: `50`
- max limit: `100`
- cursor is opaque
- invalid cursor returns `422 VALIDATION_ERROR`
- order is deterministic by `order_index`, then `unit_id`

## 4. Unit Detail

Route:

```http
GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}
```

Error rules:

- unknown source id -> `404 SOURCE_NOT_FOUND`
- unknown unit id -> `404 UNIT_NOT_FOUND`
- artifact ref, slug, or path used as unit id -> `422 VALIDATION_ERROR`
- unit id from another source -> `404 UNIT_NOT_FOUND`

## 5. Unsupported Response

Unsupported source type uses `200 OK` plus an empty list:

```json
{
  "units": {
    "source_id": "src_123",
    "items": [],
    "next_cursor": null,
    "limit": 50,
    "has_more": false,
    "unsupported_reason": "source_type_not_supported"
  }
}
```

## 6. Source Preview Relationship

Source-level preview remains unchanged. The preview route does not return units by default. ResearchNotebook must use the `/units` list/detail routes for V1.1-C frontend navigation.

## 7. Privacy And Path Sanitization

Responses must not expose raw filesystem path, cache path, artifact physical path, local absolute path, private storage filename, stack trace, or internal exception. `artifact_ref` remains metadata only.

## 8. Verification

Focused tests:

```bash
python3 -m pytest backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py -q
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py -q
```

Current result:

```text
11 passed
23 passed
```

Fixtures:

```text
backend/tests/fixtures/research_notebook/document_units/capability-manifest-document-units.json
backend/tests/fixtures/research_notebook/document_units/document-units-list-success.json
backend/tests/fixtures/research_notebook/document_units/document-unit-detail-success.json
backend/tests/fixtures/research_notebook/document_units/document-unit-not-found.json
backend/tests/fixtures/research_notebook/document_units/document-unit-artifact-ref-rejected.json
backend/tests/fixtures/research_notebook/document_units/document-units-unsupported.json
```
