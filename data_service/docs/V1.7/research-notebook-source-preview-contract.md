# V1.7 ResearchNotebook Source Preview Contract

Date: 2026-05-19
Status: implemented for V1.1-BE backend contract enablement.

## 1. Scope

This phase opens the minimal target HTTP contract required to unblock ResearchNotebook V1.1-B source-level preview integration.

It adds only:

- `GET /api/workspaces/{workspace_id}/capabilities`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview`

It does not add MCP tools, CLI commands, compatibility `/api/v1/knowledge/*` routes, DocumentUnit routes, EvidenceSpan routes, precise citation backjump, multi-format ingestion, assessment, graph editing, or quality governance UI.

## 2. Capability Manifest

Route:

```http
GET /api/workspaces/{workspace_id}/capabilities
```

Envelope shape:

```json
{
  "status": "ok",
  "data": {
    "manifest": {
      "workspace_id": "ws_123",
      "service_version": "0.1.0",
      "schema_version": "v1.1-source-preview",
      "generated_at": "...",
      "capabilities": {
        "source_preview": true,
        "document_units": false,
        "evidence_spans": false,
        "source_level_preview": true,
        "unit_level_navigation": false,
        "precise_span_highlight": false,
        "citation_backjump": false
      },
      "supported_source_types": [
        {
          "source_type": "text",
          "preview": "source",
          "locators": []
        }
      ]
    }
  },
  "warnings": [],
  "next_actions": []
}
```

## 3. Source Preview

Route:

```http
GET /api/workspaces/{workspace_id}/sources/{source_id}/preview
```

Semantics:

- `workspace_id` is the stable managed workspace id.
- `source_id` must be a registry source id such as `src_...`.
- The route does not accept llmwiki slug, page id, sourceRef, or artifact_ref as source id.
- Source-level preview does not depend on build; imported text sources can be previewed immediately.
- V1.7 exposes text source preview only.

Success response:

```json
{
  "status": "ok",
  "data": {
    "preview": {
      "source_id": "src_123",
      "title": "Architecture notes",
      "source_type": "text",
      "preview_available": true,
      "content_type": "text/plain",
      "text_preview": "Queues absorb burst traffic...",
      "artifact_refs": [
        {
          "type": "source",
          "source_id": "src_123",
          "artifact_ref": "source://src_123"
        }
      ],
      "preview_truncated": false,
      "preview_size_bytes": 1234,
      "max_preview_size_bytes": 50000
    }
  },
  "warnings": [],
  "next_actions": []
}
```

Unsupported response uses 200 plus `preview_available=false`:

```json
{
  "status": "ok",
  "data": {
    "preview": {
      "source_id": "src_123",
      "title": "Video notes",
      "source_type": "mp4",
      "preview_available": false,
      "content_type": "text/plain",
      "unsupported_reason": "source_type_not_supported"
    }
  },
  "warnings": [],
  "next_actions": ["source_type_not_supported"]
}
```

## 4. Error Semantics

- unknown workspace -> `404`
- invalid source id format -> `422 VALIDATION_ERROR`
- unknown registry source id -> `404 SOURCE_NOT_FOUND`
- unsupported source type -> `200 preview_available=false`
- preview unavailable -> `200 preview_available=false`
- backend failure -> standard service error

## 5. Privacy And Path Sanitization

Preview responses must not expose:

- raw filesystem path
- cache path
- artifact physical path
- local absolute path
- private storage filename
- stack trace
- internal exception

`artifact_refs` remain stable metadata and must not be interpreted as paths.

## 6. Verification

Focused tests:

```bash
python3 -m pytest backend/tests/test_target_http_source_preview.py -q
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_source_preview.py -q
```

Current result:

```text
5 passed
16 passed
```

Fixtures:

```text
backend/tests/fixtures/research_notebook/source_preview/capability-manifest-source-preview.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-text-success.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-unsupported.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-not-found.json
backend/tests/fixtures/research_notebook/source_preview/source-preview-artifact-ref-rejected.json
```
