# ResearchNotebook V1.0-RC3 Real Data Service Re-Smoke / Release Readiness Plan

文档状态：RC3 entry gate plan；do not execute real smoke until entry gate passes。
适用阶段：V1.0-RC3；不进入 M5+。

## 1. Entry Gate

- M0-M4 implementation is complete.
- RC2 Source Trace / Graph Context Alignment is complete in code and docs.
- `npm run check` passes.
- Boundary checks pass.
- `v1_0_current_gap_analysis.md` and `.drawio` show RC2 as the current completed state and RC3 as next.

## 2. Smoke Matrix

| Area | Path | Required Observation |
| --- | --- | --- |
| Workspace | open app -> list workspaces -> create workspace -> enter workspace -> archive cleanup | smoke-created workspace is visible and cleaned up |
| Source | create minimal text source -> source appears -> source get/detail works | source registry `source_id` is stable |
| Build | start workspace build -> poll operation | completed/failed/cancelled is visible |
| Workspace Ask | ask question -> answer renders -> evidence/no-evidence visible | traceable registry `sourceId` citation clickable; non-traceable `sourceRef` disabled |
| Trace Drawer | trace success or trace 404 | success opens drawer; 404 shows drawer-local unavailable state; answer/evidence remains visible |
| Session | create session -> ingest snippet -> session build -> session query | evidence/no-evidence visible and reuses M2 evidence UI |
| Graph | overview calls community/session graph only | no unscoped neighbors request; node/entity selection triggers neighbors only when ids exist |
| Feedback | workspace/session answer feedback submit | success/failure local state visible |
| Cleanup | close session / archive workspace | no dependency on pre-existing data |

## 3. RC3 Allowed Work

- Re-run real `data_service` smoke.
- Fix remaining real response / adapter mapper deviations.
- Update sanitized real fixtures.
- Add or adjust adapter tests.
- Complete release readiness report and checklist.
- Update gap markdown / drawio and route matrix.
- Improve backend unavailable / trace unavailable / graph unavailable states if needed.

## 4. RC3 Forbidden Work

- No Source Preview.
- No precise page/slide/timestamp/json_path backjump.
- No frontend parsing of `artifact_ref` as a path.
- No `/api/v1/knowledge/*` feature calls.
- No graph mutation/edit/merge/delete.
- No correction rules CRUD.
- No hard-coded JSON/PPT/video/audio support.
- No Assessment generation/scoring/mastery.
- No Quality/Governance console.
- No cloud sync/collaboration.

## 5. Real Response Checks

- Whether `query.hits[].source` is an llmwiki ref or registry source id.
- Whether `sources.list/get` registry `source_id` can be used for trace.
- Whether trace 404 normalizes to drawer-local unavailable state.
- Whether `graph.community?include_members=true` returns members.
- Whether `graph.neighbors?node_id=...` / `entity_id=...` works.
- Whether session query evidence shape matches workspace query evidence.

All backend shape deviations must be handled only in `src/shared/api/dataServiceClient.ts`.

## 6. Completion Statement

If real smoke passes with trace fallback:

```text
ResearchNotebook V1.0 release gate M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with source-level evidence metadata and trace-unavailable fallback.
```

If registry source trace succeeds:

```text
ResearchNotebook V1.0 source-grounded ask and trace integration ready.
```

Still cannot declare: source preview, precise citation backjump, multi-format ingestion, assessment, quality governance console, graph editing/governance, cloud sync/collaboration.
