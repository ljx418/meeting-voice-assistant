# ResearchNotebook V1.0 E2E Smoke Plan

文档状态：P1 test plan；V1.0-RC6 source trace re-smoke complete。
适用阶段：M1-RC6。

## 1. Purpose

V1.0 needs browser-level smoke coverage to prevent false green from unit tests alone.

## 2. RC3/RC6 Smoke Matrix

### Workspace

Path:

```text
open app -> list workspaces -> create workspace -> enter workspace -> archive cleanup
```

Acceptance:

- workspace list refreshes;
- route changes to workspace view;
- archive cleanup is attempted for smoke-created workspaces;
- create failure state is visible when backend returns error.

### Source

Path:

```text
create minimal text source -> source appears -> source get/detail works
```

Acceptance:

- source state changes are visible;
- source detail/get is routed through `dataServiceClient`;
- source create/list/get does not require frontend parser or file upload support.

### Build

Path:

```text
start workspace build -> poll operation -> completed/failed/cancelled visible
```

Acceptance:

- build operation polling state is visible;
- completed/failed/cancelled are distinct;
- failure does not crash source library.

### Workspace Ask

Path:

```text
ask question -> answer renders -> evidence/no-evidence visible
```

Acceptance:

- answer is not rendered as unqualified plain chat;
- no-evidence state is explicit;
- traceable registry `sourceId` citation is clickable;
- non-traceable `sourceRef` citation is disabled.

### Trace Drawer

Path:

```text
trace success opens drawer -> trace 404 shows drawer-local unavailable state
```

Acceptance:

- answer/evidence remains visible after trace failure;
- trace 404 may show source metadata fallback;
- no full source preview or precise locator backjump is claimed.

### Session

Path:

```text
create session -> ingest snippet -> session build -> session query -> evidence/no-evidence visible
```

Acceptance:

- session scoped query is separate from workspace query;
- session query reuses evidence components;
- session not found/closed state is visible.

### Graph

Path:

```text
overview calls community/session graph only -> node/entity selection triggers neighbors only when ids exist
```

Acceptance:

- graph missing artifact state is explicit;
- graph overview makes no unscoped `graph.neighbors` request;
- no `node_id` / `entity_id` means “Select a graph node to inspect neighbors.”;
- node/entity scoped neighbors render when backend returns ids;
- graph page exposes no edit/rebuild/governance actions;
- session graph context does not block session answer.

### Feedback

Path:

```text
workspace/session answer feedback submit -> success/failure local state visible
```

Acceptance:

- feedback failure is local and does not clear answer content.

### Cleanup

Path:

```text
close session -> archive workspace created by smoke
```

Acceptance:

- smoke does not depend on pre-existing local data;
- smoke-created session/workspace are cleaned up when backend routes allow it.

## 3. Non-goals

V1.0 smoke tests do not need to cover:

- JSON/PPT/video/audio full ingestion;
- precise citation locator backjump;
- assessment generation/scoring/mastery;
- cloud sync;
- collaboration.

## 4. RC3/RC6 Local data_service Smoke

Command:

```bash
npm run smoke:release
```

Note: `smoke:rc1` remains as a legacy alias and runs the same release smoke script.

Default target:

```text
http://127.0.0.1:8003
```

The smoke creates an RC-prefixed workspace, imports a minimal text source, runs workspace build/query, validates source-level evidence metadata, creates a session, ingests snippet context, runs session build/query, checks graph community context, optionally checks node-scoped graph neighbors, submits feedback, then closes/archives its own created data.

Accepted degraded RC3/RC6 states:

- source trace unavailable for the minimal text registry source id;
- non-registry `sourceRef` evidence is display-only;
- session query no-evidence;
- graph missing artifact or graph community without node ids.

RC6 specifically revalidated:

- registry `source_id` from source create/list/get still returns `404 Unknown source_id` from `sources.trace`;
- source trace integration remains `NOT_READY`;
- trace-unavailable fallback remains accepted for V1.0 release candidate readiness.
