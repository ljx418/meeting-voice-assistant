# ResearchNotebook V1.0-RC6 Source Trace Re-Smoke Report

文档状态：RC6 source trace contract re-smoke complete；source trace integration remains not ready。

## 1. Runtime Baseline

| Item | Value |
| --- | --- |
| data_service commit | `c774626a` |
| frontend commit baseline | `c774626a` plus RC2-RC6 working-tree updates |
| startup command | `JWT_DEV_MODE=1 JWT_DEV_BYPASS_AUTH=1 DATA_SERVICE_REQUIRE_API_KEY=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003` |
| base URL | `http://127.0.0.1:8003` |
| health result | `GET /api/v1/health` returned healthy |
| smoke command | `npm run smoke:release` |
| smoke timestamp | 2026-05-19 |

## 2. Registry Source ID Observed

RC6 smoke created a minimal text source and observed this registry source id:

```text
src_2003ad3198c69861
```

The source was visible through source create/list/get before trace was attempted.

## 3. Query Evidence Mapping Result

Workspace query returned evidence, but the observable hit sources remained llmwiki/page style refs rather than the registry `source_id`:

```text
hit.source = src
hit.source = source-src-2003ad3198c69861-19415ab2
hit.source = ""
```

The llmwiki citation payload included an internal source id:

```text
source_id = 19415ab28f91cbe1
```

This is not the same as the registry source id `src_2003ad3198c69861`, so the frontend must continue to treat these as display-only `sourceRef` metadata unless the value exactly matches a registry `source_id`.

## 4. Source Trace Request

The release smoke attempted the target route through the product contract:

```text
GET /api/workspaces/{workspace_id}/sources/src_2003ad3198c69861/trace
```

The route returned:

```json
{
  "detail": "Unknown source_id: src_2003ad3198c69861"
}
```

## 5. Source Trace Result

| Check | Result |
| --- | --- |
| registry source id trace | `404 trace unavailable` |
| source trace integration | `NOT_READY` |
| trace-unavailable fallback | `PASS` |
| answer/evidence preservation contract | `PASS` by existing UI tests and adapter behavior |

RC6 does not upgrade the release statement to source trace integration ready.

## 6. Full Smoke Result

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

## 7. Fixture Updates

RC6 refreshed sanitized real fixtures under `fixtures/real/`.

Important observed fixtures:

- `source-trace.json`: `404 Unknown source_id` response.
- `source-trace-404.json`: `404 Unknown source_id` response.
- `query-with-evidence.json`: workspace query evidence with llmwiki/sourceRef style hits.
- `session-query-no-evidence.json`: session query no-evidence state.
- `graph-community.json` / `graph-community-with-node-id.json` / `graph-neighbors-node-scoped.json`: graph regression pass.

Adapter-only fixtures remain under `fixtures/adapter/` and must not be reported as real backend pass cases.

## 8. Release Checklist Decision

Decision:

```text
source trace integration: NOT_READY
trace-unavailable fallback: DEGRADED_ACCEPTED / PASS
```

Backend blocking contract:

```text
data_service must return stable trace/provenance for registry source_id values created and returned by sources.create/list/get before ResearchNotebook can declare source trace integration ready.
```

## 9. Final Declaration Wording

RC6 allowed declaration:

```text
ResearchNotebook V1.0 release candidate package is repository-ready.
ResearchNotebook V1.0 M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with trace-unavailable fallback.
```

Still not allowed:

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
