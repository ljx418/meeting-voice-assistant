# ResearchNotebook V1.0-RC7 Release Handoff

文档状态：RC7 final repository sync / release handoff record。

## 1. Release Candidate Summary

ResearchNotebook V1.0 is a source-grounded personal knowledge MVP release candidate. The V1.0 release gate is M0-M4:

- M0 Scaffold / Design System / App Shell;
- M1 API Adapter / Workspace Home;
- M2 Source Library / Build / Ask with Evidence;
- M3 Session Workbench;
- M4 Read-only Graph Context / Lightweight Feedback.

RC7 does not add product capability. It packages the RC6 result into a repository handoff state.

## 2. Verified Commands

Latest required verification:

```bash
npm run check
```

Result:

```text
PASS
Boundary checks passed
70 tests passed
production build passed
```

Latest real data_service smoke was completed in RC6:

```bash
npm run smoke:release
```

Result:

```text
PASS main V1.0 product chain
DEGRADED_ACCEPTED source trace unavailable
```

RC7 did not rerun `npm run smoke:release`. It relies on the RC6 smoke report because RC7 is only the final repository sync / release handoff phase.

## 2.1 Release Status Table

| Capability / Gate | Status |
| --- | --- |
| M0-M4 integration smoke | `PASS` |
| Workspace | `PASS` |
| Source | `PASS` |
| Build | `PASS` |
| Ask | `PASS` |
| Session | `PASS` |
| Graph | `PASS` |
| Feedback | `PASS` |
| Trace-unavailable fallback | `DEGRADED_ACCEPTED` |
| Source trace integration | `NOT_READY` |
| Source preview | `NOT_READY` |
| Precise citation backjump | `NOT_READY` |
| Multi-format ingestion | `NOT_READY` |
| Assessment | `NOT_READY` |
| Quality governance console | `NOT_READY` |
| Graph editing/governance | `NOT_READY` |
| Cloud sync/collaboration | `NOT_READY` |

## 3. Real Smoke Evidence

RC6 verified:

- workspace create/list/get/archive cleanup;
- source create/list/get;
- workspace build polling;
- workspace query with evidence metadata;
- session create/ingest/build/query;
- graph community overview;
- node-scoped graph neighbors;
- lightweight feedback;
- session/workspace cleanup.

RC6 observed registry source id:

```text
src_2003ad3198c69861
```

RC6 source trace result:

```text
GET /api/workspaces/{workspace_id}/sources/src_2003ad3198c69861/trace
-> 404 Unknown source_id
```

## 4. Accepted Degraded States

V1.0 accepts these degraded states:

- source trace unavailable for registry `source_id`;
- workspace query evidence may be llmwiki/sourceRef metadata and display-only;
- session query may return no evidence items;
- graph context may show missing/unavailable states.

The UI must keep answer/evidence visible when trace fails.

## 5. Not-Ready Capabilities

Do not declare:

```text
source trace integration ready
source preview ready
precise citation backjump ready
multi-format ingestion ready
assessment ready
quality governance console ready
graph editing/governance ready
cloud sync/collaboration ready
```

## 6. Fixture And Boundary Hygiene

Fixtures are split by meaning:

- `fixtures/real/`: sanitized real `data_service` smoke responses;
- `fixtures/adapter/`: synthetic adapter contract fixtures.

Adapter fixtures must not be reported as real backend pass cases.

Boundary rules remain:

- no `/api/v1/knowledge/*`;
- no direct `fetch` in `src/features`;
- route strings only in `src/shared/api/dataServiceClient.ts`;
- `artifact_ref` is never parsed as a filesystem path.

## 7. Git Sync Scope

RC7 handoff must only stage and commit the `research-notebook/` scope from the upper workspace repository.

Allowed:

```bash
git add research-notebook/
git commit -m "Finalize ResearchNotebook V1.0 RC7 release handoff"
git push
```

Forbidden:

```bash
git add .
```

## 8. Final Handoff Statement

Allowed declaration:

```text
ResearchNotebook V1.0 release candidate repository handoff is complete.
ResearchNotebook V1.0 M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with trace-unavailable fallback.
```

## 9. Next Backend Dependency

The only current V1.0 declaration blocker is source trace integration.

`data_service` must return stable trace/provenance for registry `source_id` values created and returned by source create/list/get routes before ResearchNotebook can declare:

```text
ResearchNotebook V1.0 source trace integration ready.
```

## 10. Post-V1.0 Roadmap Pointer

The next product development phase should be V1.1, not another V1.0 feature expansion:

```text
V1.1 Source Preview / Evidence Navigation
```

V1.1 entry gate requires backend contracts for:

- `DocumentUnit`;
- `EvidenceSpan`;
- source preview route;
- precise locator model;
- citation backjump semantics;
- capability/version manifest.
