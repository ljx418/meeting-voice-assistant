# V1.1 Unit Navigation Smoke Report

文档状态：V1.1-C-RC real data_service HTTP smoke passed；Unit-Level Source Navigation integration-ready for supported text sources。
日期：2026-05-20。

## Environment

| Item | Value |
| --- | --- |
| data_service branch | `main` |
| data_service commit | `8872bf822a2c041f64af98f3629a0e224754a4f8` |
| frontend branch | `main` |
| frontend commit | `8872bf822a2c041f64af98f3629a0e224754a4f8` |
| base URL | `http://127.0.0.1:8003` |
| smoke timestamp | `2026-05-20T03:56:21.669Z` |

## Frontend Verification

Command:

```text
npm run check
```

Result:

```text
Boundary checks passed
lint passed
91 tests passed
production build passed
```

Covered UI paths:

- Source Preview Drawer shows unit outline.
- Unit item click loads selected unit detail.
- Unit detail renders escaped text.
- Load more failure keeps already loaded units visible.
- Manifest false prevents unit list route use.
- Source-level preview still works when unit navigation is unsupported.

## Real data_service HTTP Smoke

Status:

```text
PASS
```

Observed result:

```text
workspace_id: rn-v11c-rc-1779249381671-workspace
source_id: src_1ac6bb73df65b33f
selected_unit_id: unit_1fa7b49a24a14819
pagination: has_more=true next page passed
cleanup: workspace archived
```

Smoke matrix:

| Area | Result |
| --- | --- |
| Workspace create/get/archive cleanup | PASS |
| Source create/list/get | PASS |
| Capability manifest | PASS: `document_units=true`, `unit_level_navigation=true`, `evidence_spans=false`, `citation_backjump=false` |
| Source-level preview regression | PASS |
| Unit list | PASS: text source returned at least one backend-generated `DocumentUnit` |
| Unit detail | PASS: selected unit loaded by backend `unit_id` |
| Pagination | PASS: `has_more=true` page fetch appended non-duplicate unit ids |
| Unknown unit | PASS: valid unknown unit id returned 404 |
| Artifact-like unit id | PASS: rejected with 422 validation error |
| Unsupported source type | NOT_OBSERVED in this HTTP smoke; existing sanitized backend fixture retained |

Updated fixtures:

- `fixtures/real/v1_1/document-units/capability-manifest-document-units.json`
- `fixtures/real/v1_1/document-units/document-units-list-success.json`
- `fixtures/real/v1_1/document-units/document-unit-detail-success.json`
- `fixtures/real/v1_1/document-units/document-unit-not-found.json`
- `fixtures/real/v1_1/document-units/document-unit-artifact-ref-rejected.json`

Retained backend fixture:

- `fixtures/real/v1_1/document-units/document-units-unsupported.json`

Path/privacy status:

```text
fixtures do not contain /Users, file://, cache_path, artifact_path, physical_path,
/private/tmp, /tmp/, C:\, raw filesystem paths, stack traces, or private content.
```

## Current Declaration

```text
ResearchNotebook V1.1 Unit-Level Source Navigation is integration-ready for data_service-supported text sources.
```

## Still Not Ready

- EvidenceSpan highlight
- precise citation backjump
- multi-format ingestion
- assessment
- quality governance console
- graph editing/governance
- cloud sync/collaboration
- source trace integration
