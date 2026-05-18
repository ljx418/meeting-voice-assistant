# ResearchNotebook V1.0 E2E Smoke Plan

文档状态：P1 test plan；V1.0-RC1 smoke complete。
适用阶段：M1-RC1。

## 1. Purpose

V1.0 needs browser-level smoke coverage to prevent false green from unit tests alone.

## 2. Minimum Playwright Smoke Paths

### Smoke 1: Workspace Creation

Path:

```text
open app -> create workspace -> workspace appears -> enter workspace
```

Acceptance:

- workspace list refreshes;
- route changes to workspace view;
- create failure state is visible when backend returns error.

### Smoke 2: Source Import And Build

Path:

```text
workspace -> import source -> source appears -> build starts -> status completes/fails visibly
```

Acceptance:

- source state changes are visible;
- build operation polling state is visible;
- failure does not crash source library.

### Smoke 3: Query With Evidence

Path:

```text
workspace query -> answer renders -> evidence/no evidence state appears -> citation opens trace drawer
```

Acceptance:

- answer is not rendered as unqualified plain chat;
- no-evidence state is explicit;
- trace drawer failure is visible and non-fatal.

### Smoke 4: Session Workbench

Path:

```text
create session -> ingest snippet -> session query -> evidence UI appears
```

Acceptance:

- session scoped query is separate from workspace query;
- session query reuses evidence components;
- session not found/closed state is visible.

### Smoke 5: Graph Context And Feedback

Path:

```text
workspace -> graph context -> communities/neighbors render -> answer feedback submit -> session answer feedback submit
```

Acceptance:

- graph missing artifact state is explicit;
- graph page exposes no edit/rebuild/governance actions;
- session graph context does not block session answer;
- feedback failure is local and does not clear answer content.

## 3. Non-goals

V1.0 smoke tests do not need to cover:

- JSON/PPT/video/audio full ingestion;
- precise citation locator backjump;
- assessment generation/scoring/mastery;
- cloud sync;
- collaboration.

## 4. RC1 Local data_service Smoke

Command:

```bash
npm run smoke:rc1
```

Default target:

```text
http://127.0.0.1:8003
```

The smoke creates an RC-prefixed workspace, imports a minimal text source, runs workspace build/query, creates a session, ingests snippet context, runs session build/query, checks graph community context, submits feedback, then closes/archives its own created data.

Accepted degraded RC1 states:

- source trace unavailable for the minimal text source;
- session query no-evidence;
- graph missing artifact or graph community only.
