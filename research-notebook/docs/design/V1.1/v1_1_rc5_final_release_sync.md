# ResearchNotebook V1.1-RC5 Final Release Sync

文档状态：RC5 final release sync ready for scoped commit / remote push.
日期：2026-05-22。

## 1. Final Release Sync Summary

RC5 是 V1.1 收尾同步阶段，不新增产品能力，不进入 V1.2。

本阶段固化以下状态：

- V1.1-B Source Preview：PASS；
- V1.1-C Unit-Level Source Navigation：PASS；
- V1.1-D EvidenceSpan Highlight：browser-smoke-ready；
- V1.1-RC2 Live Experience Smoke：PASS；
- V1.1-RC4 Source Trace Backend Fix / Re-Smoke：PASS for scoped registry source trace；
- Source trace integration：LIMITED PASS for registry source_id-backed sources covered by RC4 smoke。

## 2. Verified Command Results

Required verification commands for RC5:

```text
npm run check
npm run smoke:v1.1-rc4-trace
```

Backend focused verification:

```text
python3 -m pytest tests/test_target_http_source_trace.py tests/test_target_http_source.py::test_v16b2_source_trace_target_route_unchanged tests/test_public_surface_guard.py::test_v16a_target_http_contract_smoke_matches_legacy_contracts -q
python3 -m pytest tests/test_target_http_source_preview.py tests/test_target_http_document_units.py tests/test_target_http_evidence_spans.py -q
```

Observed RC5 pre-sync status:

| Check | Status |
| --- | --- |
| data_service source trace focused tests | PASS |
| data_service Source Preview / DocumentUnit / EvidenceSpan regression tests | PASS |
| ResearchNotebook `npm run check` | PASS |
| ResearchNotebook `npm run smoke:v1.1-rc4-trace` | PASS |
| V1.0 / V1.1 drawio XML parse | PASS |
| fixture path hygiene | PASS |

## 3. Source Trace Scoped Pass Evidence

RC4 re-smoke verified:

```text
source create/list/get registry source id: PASS
direct source trace: HTTP 200
workspace query evidence mapping: PASS
final decision: PASS
```

Claim boundary:

```text
ResearchNotebook source trace integration is ready for registry source_id-backed sources covered by RC4 smoke.
```

This does not imply all-source-type source trace readiness.

## 4. V1.1-B/C/D Unchanged Evidence

RC5 does not modify the V1.1-B/C/D frontend capability surface.

Existing evidence remains:

- Source Preview real data_service smoke passed for supported text sources.
- DocumentUnit unit list/detail smoke passed for supported text sources.
- EvidenceSpan HTTP smoke passed for workspace query citations carrying `source_id + unit_id + evidence_id`.
- EvidenceSpan browser visual smoke passed for the same supported text-source workspace query path.
- RC2 live experience smoke passed on already-running local services.

## 5. Accepted Degraded States

Accepted degraded states remain:

- trace-unavailable fallback remains accepted for unsupported or failing trace cases;
- artifact-like evidence id returning 404 instead of preferred 422 remains accepted from earlier EvidenceSpan smoke;
- sourceRef-only citations remain metadata-only and do not call trace / preview / evidence routes.

## 6. Still NOT_READY Capabilities

Still not ready:

- all-session precise navigation;
- all-source-type precise backjump;
- all-source-type source trace;
- multi-format ingestion;
- assessment / mastery;
- quality governance console;
- graph editing/governance;
- cloud sync/collaboration.

## 7. Fixture And Path Hygiene

RC5 fixture rules:

- `fixtures/real/v1_1/source-trace/` contains sanitized RC4 source trace fixtures;
- `.smoke-artifacts/` is not committed;
- no `.bkp` files are retained;
- fixtures must not contain local absolute paths, cache path, artifact physical path, backend stack trace, or private file content.

## 8. Git Scope And Staged Files

RC5 scoped sync may include:

- data_service source trace backend contract fix;
- data_service source trace focused tests;
- ResearchNotebook source trace smoke script and package script;
- `fixtures/real/v1_1/source-trace/`;
- V1.0 / V1.1 readiness, gap, route matrix, and drawio documentation.

RC5 must not include:

- `.smoke-artifacts/`;
- unrelated sibling project changes;
- new product functionality;
- V1.2 features.

## 9. Commit Hash / Branch / Remote

To be recorded after push:

```text
branch: main
remote: origin
commit hash: recorded from git after commit
```

## 10. Final Declaration

After scoped commit / push succeeds:

```text
ResearchNotebook V1.1 release handoff is committed and pushed.
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.
ResearchNotebook source trace integration is ready for registry source_id-backed sources covered by RC4 smoke.
```

## 11. Recommended Next Phase

Recommended next phase:

```text
Session Precise Navigation Smoke
```

That phase should verify whether session query citations can carry `source_id + unit_id + evidence_id` and reuse the V1.1-D precise evidence navigation path.
