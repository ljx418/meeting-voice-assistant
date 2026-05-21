# V1.1-D Frontend Evidence Navigation Smoke Report

文档状态：frontend mocked/API-adapter smoke passed；real data_service HTTP smoke passed；browser visual smoke passed.
日期：2026-05-21.

## 1. Environment

- frontend branch/commit: local working tree
- data_service branch/commit: `main` / `8872bf82`
- data_service base URL: `http://127.0.0.1:8003`
- data_service startup command:

```text
JWT_DEV_MODE=1 JWT_DEV_BYPASS_AUTH=1 DATA_SERVICE_REQUIRE_API_KEY=false DATA_SERVICE_WORKSPACE_ROOT=/private/tmp/research-notebook-v11d-smoke python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

## 2. Smoke Command

```text
npm run check
```

Result:

```text
PASS
Boundary checks passed
94 tests passed
production build passed
```

Real HTTP smoke command:

```text
node scripts/v1_1_d_evidence_smoke.mjs
```

Result:

```text
PASS target route probe - http://127.0.0.1:8003
PASS workspace create - rn-v11d-1779329409618-workspace
PASS source create - src_255a571fc7ee11e7
PASS capability manifest evidence flags
PASS unit list - unit_325a5a7bd3379019
PASS unit detail - text/plain
PASS workspace build polling - completed
PASS workspace query jumpable evidence - src_255a571fc7ee11e7/unit_325a5a7bd3379019/ev_de80f5196a74dcdd
PASS evidence span detail - normalized_text/half_open/document_unit_text
PASS evidence not found semantics - 404
DEGRADED artifact_ref evidence id rejected - HTTP 404 /api/workspaces/rn-v11d-1779329409618-workspace/sources/src_255a571fc7ee11e7/units/unit_325a5a7bd3379019/evidence/artifact%3A%2F%2Fev
PASS fixtures saved
PASS workspace archive cleanup
```

## 3. Capability Manifest Flags

Mocked UI smoke and real HTTP smoke covered:

```text
source_preview=true
document_units=true
evidence_spans=true
source_level_preview=true
unit_level_navigation=true
precise_span_highlight=true
citation_backjump=true
```

## 4. Workspace Query Evidence Shape

Real HTTP smoke observed a workspace answer citation carrying:

```text
source_id=src_255a571fc7ee11e7
unit_id=unit_325a5a7bd3379019
evidence_id=ev_de80f5196a74dcdd
snippet=EvidenceSpan navigation should highlight this sentence after query evidence resolves to a source id, unit id, and evidence id.
```

## 5. UI Result

- mocked UI smoke: citation opened Source Preview Drawer;
- mocked UI smoke: source-level preview remained visible;
- mocked UI smoke: selected unit detail loaded;
- mocked UI smoke: EvidenceSpan detail loaded;
- real HTTP smoke: unit detail and EvidenceSpan detail routes returned stable payloads;
- real HTTP smoke: `offset_basis=normalized_text`, `offset_range=half_open`, `text_basis=document_unit_text`;
- mocked UI smoke: highlighted span rendered safely as escaped React text.

## 6. Real Data Service Smoke

Real data_service HTTP smoke was executed and passed the V1.1-D route/evidence contract.

Browser visual smoke was later executed through:

```text
npm run smoke:v1.1-d-browser
```

Result:

```text
PASS browser opened app
PASS workspace create and enter
PASS source import visible
PASS source preview opens
PASS unit navigation visible
PASS workspace query jumpable citation visible
PASS evidence highlight visible
PASS screenshot saved
PASS browser console/network guard
PASS cleanup archive workspace
```

Accepted degraded states:

- artifact-like evidence id returned 404 instead of the preferred 422. This remains a backend error-semantics gap, not a frontend blocker.

Fixtures saved under:

```text
fixtures/real/v1_1/evidence-spans/
```

## 7. Declaration Decision

```text
ResearchNotebook V1.1-D EvidenceSpan route and query-evidence contract passed real data_service HTTP smoke for supported text-source workspace query citations.
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.
ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query citation path.
```

## 8. Still Not Ready

- source trace integration;
- all session query precise navigation;
- all source-type precise backjump;
- multi-format ingestion;
- assessment;
- quality governance console;
- graph editing/governance;
- cloud sync/collaboration.
