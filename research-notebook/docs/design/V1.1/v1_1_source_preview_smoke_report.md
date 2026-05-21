# V1.1 Source Preview Smoke Report

Date: 2026-05-19

## 1. Scope

This report records the V1.1-B real `data_service` smoke for source-level preview integration.

V1.1-B only validates:

- capability manifest route;
- source-level preview route;
- registry `source_id` preview semantics;
- Source Preview Drawer integration path.

It does not validate DocumentUnit navigation, EvidenceSpan highlight, precise citation backjump, source trace integration, multi-format ingestion, assessment, graph editing, or cloud collaboration.

## 2. Environment

| Item | Value |
| --- | --- |
| data_service base URL | `http://127.0.0.1:8003` |
| data_service branch | `main` |
| data_service commit | `8872bf82` |
| frontend branch | `main` |
| frontend commit | `8872bf82` |
| smoke timestamp UTC | `2026-05-19T09:39:58Z` |
| startup command | `python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003` from `data_service/backend` |

## 3. Smoke Matrix

| Step | Result | Evidence |
| --- | --- | --- |
| Create workspace | PASS | `rn-v11b-1779183344-workspace` |
| Create minimal text source | PASS | `src_7df92304c64b476b` |
| Get capability manifest | PASS | `schema_version=v1.1-source-preview`; `source_preview=true`; `source_level_preview=true`; `document_units=false`; `evidence_spans=false` |
| Get source preview with registry `source_id` | PASS | `preview_available=true`; `source_type=text`; `content_type=text/plain`; `preview_size_bytes=76`; `max_preview_size_bytes=50000` |
| Reject slug/page ref as source id | PASS | `source-src-preview-smoke` returned HTTP `422` |
| Archive cleanup | PASS | workspace archived |
| Frontend `npm run check` | PASS | boundary checks, lint, 83 tests, production build |

## 4. Frontend Integration Result

Implemented:

- `dataServiceClient.capabilities.get(workspaceId)` calls `GET /api/workspaces/{workspace_id}/capabilities`.
- `dataServiceClient.sources.preview(workspaceId, sourceId)` calls `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview`.
- Source Preview Drawer checks the manifest before preview.
- Manifest unsupported state prevents preview route calls.
- Source Preview Drawer renders source metadata, artifact refs as metadata only, truncation metadata, and escaped `text_preview`.
- `text/html` and `text/markdown` are rendered as escaped text, not HTML.
- Preview route failure remains drawer-local.

## 5. Fixtures

Sanitized fixtures remain under:

```text
fixtures/real/v1_1/source-preview/
```

Existing fixture set:

- `capability-manifest-source-preview.json`
- `source-preview-text-success.json`
- `source-preview-unsupported.json`
- `source-preview-not-found.json`
- `source-preview-artifact-ref-rejected.json`

Fixtures must not contain local absolute paths, cache paths, artifact physical paths, private filenames, or stack traces.

## 6. Declaration Decision

```text
ResearchNotebook V1.1 Source-Level Preview is integration-ready for data_service-supported text sources.
```

This declaration is limited to source-level preview. It does not make V1.0 source trace integration ready.

## 7. Still Not Ready

- source trace integration ready;
- unit-level navigation ready;
- EvidenceSpan highlight ready;
- precise citation backjump ready;
- multi-format ingestion ready;
- assessment ready;
- quality governance console ready;
- graph editing/governance ready;
- cloud sync/collaboration ready.
