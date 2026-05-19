# ResearchNotebook V1.0 Release Checklist

文档状态：RC6 source trace re-smoke checklist；No False Green closure。

Verification command:

```bash
npm run check
```

Release smoke command:

```bash
npm run smoke:release
```

RC5 verification result:

- `PASS` 2026-05-19 `npm run check` passed: boundary checks, lint, 70 tests, and production build.
- `DEGRADED_ACCEPTED` `npm run smoke:release` was not rerun during RC5 packaging because local `data_service` was not running; RC3 real smoke remains the integration evidence for this release candidate.

RC6 verification result:

- `PASS` 2026-05-19 `npm run check` passed: boundary checks, lint, 70 tests, and production build.
- `PASS` 2026-05-19 `npm run smoke:release` completed against local `data_service`.
- `DEGRADED_ACCEPTED` RC6 registry `source_id` trace still returned 404: `Unknown source_id: src_2003ad3198c69861`.

Status values:

- `PASS`: verified by automated check, UI/API test, or real smoke.
- `DEGRADED_ACCEPTED`: expected degraded behavior that is productized and documented.
- `NOT_READY`: not observed, backend-required, or explicitly out of V1.0 scope.

## 1. PASS

Code gates:

- `PASS` `npm run check` passes.
- `PASS` Boundary checks pass:
  - no `/api/v1/knowledge` in product code;
  - no direct `fetch` in `src/features`;
  - route strings only in `src/shared/api/dataServiceClient.ts`;
  - `artifact_ref` is never parsed as a filesystem path.
- `PASS` API adapter tests cover RC2 evidence source resolution.
- `PASS` UI smoke tests cover trace 404 fallback, sourceRef disabled citation, graph community overview, and node-scoped neighbors.

RC3/RC6 real smoke gates:

- `PASS` Workspace create/list/get/archive cleanup.
- `PASS` Source create/list/get.
- `PASS` Workspace build start/status visible.
- `PASS` Workspace query answer visible.
- `PASS` Non-traceable `sourceRef` citation disabled.
- `PASS` Trace 404 fallback keeps answer/evidence visible.
- `PASS` Session create/ingest/build/query.
- `PASS` Graph community overview.
- `PASS` No unscoped `graph.neighbors` request.
- `PASS` Node/entity scoped neighbors when `node_id` / `entity_id` is available.
- `PASS` Feedback submit success or stable local failure.

Documentation gates:

- `PASS` `answer-evidence-contract.md` matches implemented `AnswerEvidence`.
- `PASS` `api-adapter-contract.md` matches implemented DTOs and route-shape boundary.
- `PASS` `graph-context-contract.md` documents node/entity-scoped neighbors.
- `PASS` `feature-route-matrix.md` marks future/unsupported capabilities clearly.
- `PASS` `v1_0_current_gap_analysis.md` and `.drawio` are synchronized.
- `PASS` `v1_0_integration_readiness_report.md` includes RC3/RC6 results.
- `PASS` `data_service_real_route_alignment.md` includes actual route deviations.
- `PASS` `v1_0_e2e_smoke_plan.md` includes RC3/RC6 smoke matrix.

## 2. DEGRADED_ACCEPTED

- `DEGRADED_ACCEPTED` Source trace fallback: RC3 and RC6 minimal text registry `source_id` returned 404 from `sources.trace`; V1.0 accepts drawer-local trace unavailable state.
- `DEGRADED_ACCEPTED` Workspace query evidence: RC3 real query returned llmwiki/sourceRef evidence; V1.0 shows it as display-only metadata unless it exactly matches a registry source id.
- `DEGRADED_ACCEPTED` Session query no-evidence: RC3 real session query returned no evidence items; V1.0 shows explicit no-evidence state.

## 3. NOT_READY

- `NOT_READY` Source trace integration: RC6 confirmed registry `source_id` trace still returns 404. Backend must return trace for registry source ids before declaring source trace integration ready.
- `NOT_READY` Real session query with evidence. `fixtures/adapter/session-query-with-evidence.json` is an adapter fixture, not an RC3/RC6 backend pass.
- `NOT_READY` Real workspace query hit with registry source id. `fixtures/adapter/query-hit-source-registry-id.json` is an adapter fixture, not an RC3/RC6 backend pass.
- `NOT_READY` Source preview.
- `NOT_READY` Precise citation backjump.
- `NOT_READY` Multi-format ingestion.
- `NOT_READY` Assessment.
- `NOT_READY` Quality governance console.
- `NOT_READY` Graph editing/governance.
- `NOT_READY` Cloud sync/collaboration.

## 4. Fixture Gates

Real RC3/RC6 fixtures exist or are refreshed:

- `PASS` `fixtures/real/workspaces-list.json`
- `PASS` `fixtures/real/query-hit-source-slug.json`
- `PASS` `fixtures/real/source-trace-404.json`
- `PASS` `fixtures/real/source-trace.json`
- `PASS` `fixtures/real/graph-community-with-node-id.json`
- `PASS` `fixtures/real/graph-neighbors-node-scoped.json`
- `PASS` `fixtures/real/session-query-no-evidence.json`

Adapter-only fixtures retained for contract coverage:

- `PASS` `fixtures/adapter/query-hit-source-registry-id.json`
- `PASS` `fixtures/adapter/session-query-with-evidence.json`
- `PASS` `fixtures/adapter/graph-community-without-node-id.json`

Fixtures must not contain local absolute paths, cache paths, artifact physical paths, sensitive filenames, or private content.

## 5. No False Green

Do not declare:

- source trace integration ready;
- source preview ready;
- precise citation backjump ready;
- multi-format ingestion ready;
- assessment ready;
- quality governance console ready;
- graph editing/governance ready;
- cloud sync/collaboration ready.
