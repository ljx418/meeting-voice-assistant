# ResearchNotebook V1.0-RC1 Integration Readiness Report

文档状态：RC1 smoke complete；2026-05-18。

## 1. data_service Version / Startup

- data_service commit: `a50027e6`.
- Startup command:

```bash
DATA_SERVICE_WORKSPACE_ROOT=/tmp/research-notebook-rc1-workspaces DATA_SERVICE_REQUIRE_API_KEY=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

- Health probe: `GET /api/v1/health` returned healthy.
- Base URL: `http://127.0.0.1:8003`.

## 2. Frontend Version

- ResearchNotebook workspace commit: `a50027e6`.
- RC1 work stays inside the ResearchNotebook frontend adapter, fixtures, smoke script, and V1.0 docs.

## 3. Route Alignment Summary

Required pass:

| Chain | Result |
| --- | --- |
| workspace create/list/get | pass |
| source create/list/get | pass |
| build start/status visible | pass |
| workspace query answer + evidence/no-evidence state | pass, evidence returned |
| session create/ingest/query | pass, session query no-evidence accepted |
| feedback submit | pass |

Allowed degraded:

| Chain | Result | Handling |
| --- | --- | --- |
| source trace | degraded: RC text source returned 404 | drawer-local unavailable state; answer remains visible |
| graph neighbors | degraded: backend requires `node_id/entity_id` | graph community route provides read-only graph context |
| graph missing artifact | not observed in latest RC smoke | fixture retained for adapter test |

## 4. Adapter Mapper Changes

- Added envelope unwrapping for `data.items`, `data.workspace`, `data.source`, `data.session`, and graph `data.items`.
- Mapped source create request to data_service text import contract.
- Mapped workspace/session query request from `question` to backend `query`.
- Mapped session ingest request to backend text snippet ingest contract.
- Mapped lightweight feedback rating to backend `target_id/action/metadata`.
- Mapped query `hits/items/results` into `AnswerEvidence`.
- Normalized blocked graph envelopes into `missing_graph_artifact`.
- Normalized operation status `succeeded` to frontend `completed`.

## 5. Smoke Test Results

Command:

```bash
npm run smoke:rc1
```

Latest result:

```text
PASS health probe - data_service
PASS workspace create
PASS workspace list
PASS workspace get
PASS source create
PASS source list/get
DEGRADED source trace - HTTP 404
PASS workspace build polling - completed
PASS workspace query - evidence
PASS session create
PASS session ingest
PASS session build polling - succeeded
PASS session query - no evidence
PASS graph community - ok
PASS feedback submit
PASS session cleanup close
PASS workspace cleanup archive
```

## 6. Real Fixtures

Sanitized fixtures are stored under `fixtures/real/`:

- `workspaces-list.json`
- `source-trace.json`
- `query-with-evidence.json`
- `query-no-evidence.json`
- `graph-missing-artifact.json`
- `graph-community.json`

## 7. Final Readiness Statement

ResearchNotebook V1.0 M0-M4 can be declared:

```text
Workspace / Source / Build / Ask / Session / Graph Community / Feedback integration smoke ready.
```

It should not yet be declared full source-grounded MVP integration ready until the source trace degradation is resolved or explicitly accepted as V1.0 backend behavior for minimal text imports.

No False Green remains in effect:

- source preview is not ready;
- precise citation backjump is not ready;
- multi-format ingestion is not ready;
- assessment is not ready;
- quality governance console is not ready;
- graph editing/governance is not ready.
