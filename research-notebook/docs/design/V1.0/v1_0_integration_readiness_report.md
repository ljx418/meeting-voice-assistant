# ResearchNotebook V1.0-RC6 Integration Readiness Report

文档状态：RC6 source trace re-smoke complete；source trace fallback remains accepted degraded。

## 1. data_service Version / Startup

- data_service commit: `c774626a`.
- RC3 startup command:

```bash
DATA_SERVICE_WORKSPACE_ROOT=/tmp/research-notebook-rc3-workspaces DATA_SERVICE_REQUIRE_API_KEY=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

- RC6 startup command:

```bash
JWT_DEV_MODE=1 JWT_DEV_BYPASS_AUTH=1 DATA_SERVICE_REQUIRE_API_KEY=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

- Health probe: `GET /api/v1/health` returned healthy.
- Base URL: `http://127.0.0.1:8003`.

## 2. Frontend Version

- ResearchNotebook workspace commit: `c774626a` plus current RC2-RC6 working-tree updates.
- RC6 work stays inside ResearchNotebook fixtures and V1.0 docs; no product capability or M5+ work was added.

## 3. Route Alignment Summary

Required pass:

| Chain | Result |
| --- | --- |
| workspace create/list/get | pass |
| source create/list/get | pass |
| build start/status visible | pass |
| workspace query answer + evidence/no-evidence state | pass, evidence returned |
| session create/ingest/build/query | pass, session query no-evidence accepted |
| graph community overview | pass |
| graph node-scoped neighbors | pass when community members provide `node_id` |
| feedback submit | pass |

Allowed degraded:

| Chain | Result | Handling |
| --- | --- | --- |
| source trace | degraded: registry `source_id` trace returned 404 for minimal text source | drawer-local unavailable state; answer/evidence remain visible |
| traceable registry citation | not observed as successful with current minimal text backend data | UI and adapter support it when backend returns traceable registry `sourceId` |
| non-traceable sourceRef | observed in workspace query hits | display-only evidence metadata; no trace call |
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

## 5. RC3 / RC6 Real Smoke Results

Command:

```bash
npm run smoke:release
```

`smoke:rc1` remains as a legacy alias and runs the same release smoke script.

Latest RC3 result:

```text
PASS health probe - data_service
PASS workspace create - rn-rc3-1779160515184-workspace
PASS workspace list
PASS workspace get
PASS source create - src_a5d47ec8f30ed0e1
PASS source list/get
DEGRADED source trace - HTTP 404 /api/workspaces/{workspace_id}/sources/{source_id}/trace
PASS workspace build polling - completed
PASS workspace query - evidence
PASS session create - ksess_92d7a29cead8643b
PASS session ingest
PASS session build polling - succeeded
PASS session query - no evidence
PASS graph neighbors node-scoped - theme:rc3
PASS graph community - ok
PASS feedback submit
PASS session cleanup close
PASS workspace cleanup archive
```

Latest RC6 result:

```text
PASS health probe - data_service
PASS workspace create - rn-release-1779172346009-workspace
PASS workspace list
PASS workspace get
PASS source create - src_2003ad3198c69861
PASS source list/get
DEGRADED source trace - HTTP 404 /api/workspaces/rn-release-1779172346009-workspace/sources/src_2003ad3198c69861/trace
PASS workspace build polling - completed
PASS workspace query - evidence
PASS session create - ksess_3429745e39419cbd
PASS session ingest
PASS session build polling - succeeded
PASS session query - no evidence
PASS graph neighbors node-scoped - theme:researchnotebook
PASS graph community - ok
PASS feedback submit
PASS session cleanup close
PASS workspace cleanup archive
```

RC6 source trace decision:

```text
source trace integration: NOT_READY
trace-unavailable fallback: DEGRADED_ACCEPTED
```

## 6. Real Fixtures

Sanitized fixtures are stored under `fixtures/real/`:

- `workspaces-list.json`
- `source-trace.json`
- `source-trace-404.json`
- `query-hit-source-slug.json`
- `graph-community-with-node-id.json`
- `graph-neighbors-node-scoped.json`
- `query-with-evidence.json`
- `query-no-evidence.json`
- `session-query-no-evidence.json`
- `graph-missing-artifact.json`
- `graph-community.json`

Adapter-only fixtures are stored under `fixtures/adapter/` and must not be reported as real backend pass cases:

- `query-hit-source-registry-id.json`;
- `session-query-with-evidence.json`;
- `graph-community-without-node-id.json`.

## 7. Final Readiness Statement

ResearchNotebook V1.0 M0-M4 can be declared:

```text
ResearchNotebook V1.0 release gate M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with source-level evidence metadata and trace-unavailable fallback.
```

It should not be declared source trace integration ready yet because RC6 registry `source_id` trace still returned 404 for the minimal text source. It should not be declared full source preview or precise citation backjump ready.

No False Green remains in effect:

- source preview is not ready;
- precise citation backjump is not ready;
- multi-format ingestion is not ready;
- assessment is not ready;
- quality governance console is not ready;
- graph editing/governance is not ready.
