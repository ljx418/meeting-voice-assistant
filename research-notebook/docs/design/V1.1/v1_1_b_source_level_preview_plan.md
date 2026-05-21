# V1.1-B Source-Level Preview Integration Plan

文档状态：V1.1-B Source-Level Preview frontend integration completed；real data_service smoke passed for source-level text preview。
日期：2026-05-19。

## Decision

V1.1-B direction is correct. It was initially blocked because `data_service` did not expose the required ResearchNotebook source-level preview contract. V1.1-BE has now added the minimum backend contract in the local data_service working tree.

Current outcome:

```text
V1.1-A Source Preview shell: READY
V1.1-BE backend contract: READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
V1.1-B frontend integration: INTEGRATION_SMOKE_READY_FOR_TEXT_SOURCE
```

## Entry Gate Result

Required backend contract:

| Requirement | Current Result |
| --- | --- |
| capability/version manifest route | Added: `GET /api/workspaces/{workspace_id}/capabilities` |
| manifest says `source_preview=true` or `source_level_preview=true` | Added |
| source preview route | Added: `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview` |
| route accepts registry `source_id` | Added |
| route does not require llmwiki slug/page ref | Added; slug/page refs rejected |
| response excludes raw filesystem/cache/artifact physical path | Tested |
| response declares `content_type` | Added: `text/plain` |
| unsupported source type has stable response | Added: `preview_available=false` |

Result:

```text
Backend contract is ready for ResearchNotebook V1.1-B frontend integration after backend change review.
Frontend route adaptation and real data_service smoke have passed for source-level text preview.
```

## Corrected Query / Citation Relationship

V1.1-B does not require answer citation to automatically open preview.

V1.1-B release-gate entry:

```text
Source Library / Source Detail -> Preview button -> Source Preview Drawer
```

Optional enhancement, only after manifest support exists:

- if `AnswerEvidence.sourceId` is a registry source id and manifest declares source-level preview available, citation may open source-level preview;
- `sourceRef`, slug, page id, and `artifact_ref` must not be sent to preview route;
- this does not make precise citation backjump ready.

## Allowed After Contract Exists

- `capabilities.get()` real route alignment;
- `sources.preview(workspaceId, sourceId)` real route alignment;
- source-level drawer rendering;
- loading / unsupported / unavailable / backend unavailable / version mismatch states;
- safe escaped preview rendering;
- API adapter mapper hardening;
- real fixtures and smoke report.

## Still Prohibited

- DocumentUnit outline / unit navigation;
- unit selection state / scroll-to-unit / unit highlight;
- EvidenceSpan highlight;
- precise citation backjump;
- answer citation direct preview navigation as ready;
- JSON/PPT/video/audio ingestion UI as ready;
- Assessment;
- Quality/Governance console;
- graph editing/governance;
- cloud sync/collaboration;
- frontend parser;
- `artifact_ref` path parsing;
- `/api/v1/knowledge/*` calls;
- unsafe backend HTML rendering.

## Next Backend Dependency

data_service should provide:

```text
GET /api/workspaces/{workspace_id}/capabilities
GET /api/workspaces/{workspace_id}/sources/{source_id}/preview
```

The concrete route names may differ, but ResearchNotebook can only adapt them inside `src/shared/api/dataServiceClient.ts` after they are frozen.
