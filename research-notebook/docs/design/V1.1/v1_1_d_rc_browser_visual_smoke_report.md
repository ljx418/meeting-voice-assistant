# V1.1-D-RC Browser Visual Smoke Report

文档状态：V1.1-D browser visual smoke passed；release-readiness docs updated.
日期：2026-05-21.

## 1. Environment

| Item | Value |
| --- | --- |
| data_service branch | `main` |
| data_service commit | `8872bf82` |
| frontend commit | local working tree, base `8872bf82` |
| data_service base URL | `http://127.0.0.1:8003` |
| Vite app URL | `http://127.0.0.1:5173` |
| browser engine | Chromium headless via Chrome DevTools Protocol |
| smoke timestamp | `1779329420314` |

Startup command:

```text
JWT_DEV_MODE=1 JWT_DEV_BYPASS_AUTH=1 DATA_SERVICE_REQUIRE_API_KEY=false DATA_SERVICE_WORKSPACE_ROOT=/private/tmp/research-notebook-v11d-browser-smoke python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003
VITE_DATA_SERVICE_BASE_URL=http://127.0.0.1:8003 npm run dev -- --host 127.0.0.1 --port 5173
```

## 2. Commands

```text
npm run check
npm run smoke:v1.1-d-http
npm run smoke:v1.1-d-browser
```

Results:

```text
npm run check: PASS
npm run smoke:v1.1-d-http: PASS_WITH_ACCEPTED_DEGRADED_STATES
npm run smoke:v1.1-d-browser: PASS
```

## 3. Browser Smoke Evidence

Observed ids:

```text
workspace_id = rn-v11d-browser-1779329420314-workspace
source_id = src_255a571fc7ee11e7
unit_id = unit_325a5a7bd3379019
evidence_id = ev_de80f5196a74dcdd
```

Highlighted text:

```text
Queues absorb burst traffic during release validation. EvidenceSpan navigation should highlight this sentence after query evidence resolves to a source id, unit id, and evidence id.
```

Smoke artifact locations are intentionally under `.smoke-artifacts/`, which is gitignored:

```text
.smoke-artifacts/v1_1_d_browser/1779329420314/browser-smoke-result.json
.smoke-artifacts/v1_1_d_browser/1779329420314/evidence-highlight.png
```

The report records artifact paths only. Smoke screenshots/logs should not be committed.

## 4. Matrix

| Check | Result |
| --- | --- |
| data_service target route probe | PASS |
| Vite app opened in browser | PASS |
| no blank screen | PASS |
| workspace create and enter | PASS |
| source import visible | PASS |
| Source Preview Drawer opens | PASS |
| source preview remains visible | PASS |
| Document Units outline visible | PASS |
| unit selection loads detail | PASS |
| workspace query answer renders | PASS |
| jumpable evidence citation visible | PASS |
| citation opens/focuses preview drawer | PASS |
| EvidenceSpan detail loads | PASS |
| highlighted text visible | PASS |
| highlight is inside selected unit detail | PASS |
| console/pageerror blocking errors | PASS, none observed |
| `/api/v1/knowledge/*` browser network requests | PASS, none observed |
| cleanup archive workspace | PASS |

## 5. Accepted Degraded States

The V1.1-D HTTP smoke still records one backend error-semantics gap:

```text
artifact-like evidence id returned 404 instead of preferred 422
```

This does not block browser-release-ready for the supported text-source workspace query path because:

- valid workspace query evidence resolves through registry `source_id + unit_id + evidence_id`;
- valid EvidenceSpan detail returns the supported offset contract;
- invalid evidence ids remain drawer-local/error-local in frontend behavior.

## 6. Declaration Decision

```text
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.

ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query citation path.
```

## 7. Still Not Ready

- source trace integration ready;
- all-session precise navigation ready;
- all-source-type precise backjump ready;
- multi-format ingestion ready;
- assessment ready;
- quality governance console ready;
- graph editing/governance ready;
- cloud sync/collaboration ready.
