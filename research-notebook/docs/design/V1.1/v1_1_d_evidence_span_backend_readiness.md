# V1.1-D EvidenceSpan Backend Readiness

文档状态：V1.1-D-BE backend contract complete；V1.1-D frontend and V1.1-D-RC browser visual smoke passed for supported text-source workspace query path。
日期：2026-05-20。

## 1. Backend Version

- data_service branch: `main`
- data_service commit observed before local edits: `8872bf822a2c041f64af98f3629a0e224754a4f8`
- implementation state: local data_service working tree changes

## 2. Routes Exposed

```text
GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}
```

No `/api/v1/knowledge/*` route was added for EvidenceSpan.

## 3. Capability Manifest

After V1.1-D-BE route/test/smoke enablement, the manifest reports:

```text
source_preview=true
document_units=true
evidence_spans=true
source_level_preview=true
unit_level_navigation=true
precise_span_highlight=true
citation_backjump=true
```

These flags mean the backend contract is ready. They do not mean ResearchNotebook frontend highlight or citation jump UX has been implemented.

## 4. EvidenceSpan DTO

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

## 5. Query Evidence Shape

Workspace query can return:

```ts
type QueryEvidence = {
  evidence_key: string;
  source_id?: string;
  source_title?: string;
  unit_id?: string;
  evidence_id?: string;
  snippet?: string;
  confidence?: number;
  locator?: object;
  preview_available?: boolean;
};
```

Session query evidence is not EvidenceSpan-ready in this backend phase.

## 6. Offset And Text Basis

V1.1-D-BE freezes:

```text
offset_basis = normalized_text
offset_range = half_open
text_basis = document_unit_text
```

Offsets are relative to the normalized text of the referenced `DocumentUnit`.

## 7. Error Semantics

- unknown source id: `404 SOURCE_NOT_FOUND`
- unknown unit id: `404 UNIT_NOT_FOUND`
- unknown evidence id: `404 EVIDENCE_NOT_FOUND`
- evidence id from another source/unit: `404 EVIDENCE_NOT_FOUND`
- artifact ref, slug, or path used as evidence id: `422 VALIDATION_ERROR`

Responses must not contain raw filesystem paths, cache paths, artifact physical paths, private filenames, or stack traces.

## 8. Backend Tests

Focused verification:

```text
python3 -m pytest backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py backend/tests/test_target_http_evidence_spans.py -q
16 passed

python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py backend/tests/test_target_http_evidence_spans.py -q
27 passed
```

Warnings were existing `datetime.utcnow()` deprecation warnings and are not EvidenceSpan contract failures.

## 9. Backend-only Smoke

Backend-only smoke result:

```text
PASS
workspace_id: rn-v11dbe-smoke-workspace
source_id: src_04979571353567c0
unit_id: unit_06899678a1a8340c
evidence_id: ev_2e14b7785f3fbb06
cleanup: workspace archived
```

Covered:

- create workspace;
- create text source;
- GET capabilities;
- list units;
- workspace query returns registry `source_id`, backend `unit_id`, and backend `evidence_id`;
- GET EvidenceSpan by `source_id + unit_id + evidence_id`;
- verify offset/text basis;
- unknown evidence returns 404;
- artifact-like evidence id is rejected; latest ResearchNotebook HTTP smoke observed 404 instead of preferred 422 and records this as an accepted backend error-semantics gap;
- archive cleanup.

## 10. Fixtures

Sanitized fixtures were saved in:

```text
fixtures/real/v1_1/evidence-spans/
```

Fixture files:

- `capability-manifest-evidence-spans.json`
- `query-evidence-with-evidence-span.json`
- `evidence-span-detail-success.json`
- `evidence-span-not-found.json`
- `evidence-span-artifact-ref-rejected.json`

Fixture hygiene scan passed for raw path/cache/path/physical path markers.

## 11. Frontend Entry Decision

```text
data_service EvidenceSpan backend contract:
READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW

ResearchNotebook V1.1-D frontend EvidenceSpan highlight:
BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY

ResearchNotebook precise citation backjump UI:
BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
```

## 12. Still Not Ready

- all-session precise citation navigation
- all-source-type precise citation navigation
- precise citation backjump UI
- session query EvidenceSpan navigation
- source trace integration
- multi-format ingestion
- assessment
- quality governance console
- graph editing/governance
- cloud sync/collaboration
