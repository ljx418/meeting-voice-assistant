# ResearchNotebook V1.0-RC4 Final Readiness Report

文档状态：RC4 final docs cleanup complete。

## 1. Scope

RC4 is a documentation and release-readiness closure phase. It does not add M5+ product capability and does not change backend behavior.

RC4 finalizes:

- current-state documentation after RC3 real `data_service` smoke;
- clear separation between passed, accepted degraded, and not observed/backend-required items;
- No False Green release statements.

## 2. Current State

ResearchNotebook V1.0 M0-M4 is integration-smoke-ready:

- Workspace Home;
- Source Library;
- workspace build polling;
- workspace ask with evidence metadata;
- Source Trace Drawer fallback;
- Session Workbench;
- read-only Graph Context;
- Lightweight Feedback.

RC3 real smoke passed the product chain for workspace/source/build/query/session/graph/feedback. It also confirmed that node-scoped graph neighbors work when community members provide `node_id`.

## 3. Accepted Degraded

- Source trace for the RC3 minimal text registry `source_id` returned 404. The UI treats this as drawer-local trace unavailable and keeps answer/evidence visible.
- Workspace query evidence returned llmwiki/sourceRef-style hits. The UI renders these as display-only evidence metadata unless the value exactly matches registry `source_id`.
- Session query returned no evidence items. The UI renders explicit no-evidence state.

These are acceptable for V1.0 release candidate readiness, but they are not proof of source trace integration or precise evidence navigation.

## 4. Not Observed / Backend Required

- Successful `sources.trace` response for a registry `source_id`.
- Real session query with evidence items.
- Real workspace query hit where backend source ref equals registry `source_id`.

These remain backend/data-shape dependent and must not be marked as passed.

## 5. Final Statement

Allowed declaration:

```text
ResearchNotebook V1.0 release candidate documentation and smoke package are finalized.
ResearchNotebook V1.0 M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with trace-unavailable fallback.
```

Forbidden declaration:

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

## 6. Next Work

Next work should be release packaging or post-V1.0 planning. If `data_service` later returns successful source trace for registry source ids, the project can run a focused trace validation pass and update the readiness statement.
