# ResearchNotebook

ResearchNotebook is the independent frontend application layer for a source-grounded personal knowledge workspace. It integrates with the local `data_service` backend through `/api/workspaces/...` target routes only.

## Current Status

V1.0 is a source-grounded personal knowledge MVP release candidate.

Current declaration:

- V1.0 M0-M4 is integration-smoke-ready.
- Source-level evidence metadata is supported.
- Trace-unavailable fallback is supported.
- Read-only graph context and lightweight feedback are supported.

Accepted degraded / not ready:

- source trace integration is not ready; RC6 confirmed registry `source_id` trace still returns 404;
- source preview is not ready;
- precise citation backjump is not ready;
- multi-format ingestion is not ready;
- assessment is not ready;
- quality governance console is not ready;
- graph editing/governance is not ready;
- cloud sync/collaboration is not ready.

## Local Setup

```bash
npm install
npm run dev
```

The app can run as a frontend shell without a backend, but integration smoke expects local `data_service`.

Default local backend:

```text
http://127.0.0.1:8003
```

Override the backend URL with:

```bash
VITE_DATA_SERVICE_BASE_URL=http://127.0.0.1:8003 npm run dev
RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8003 npm run smoke:release
```

## Verification

```bash
npm run check
npm run smoke:release
```

`npm run smoke:release` runs the current V1.0 release candidate smoke against a running local `data_service`. The legacy alias `npm run smoke:rc1` is retained for compatibility and runs the same script.

## Boundary Rules

- Do not call `/api/v1/knowledge/*` from ResearchNotebook.
- Do not fetch directly from feature modules.
- Keep route strings inside `src/shared/api/dataServiceClient.ts`.
- Do not parse `artifact_ref` as a filesystem path.
- Do not claim source preview, precise citation backjump, multi-format ingestion, assessment, graph editing, cloud sync/collaboration, or quality governance console as V1.0-ready.

## Active Docs

Start with:

- `docs/design/V1.0/v1_0_current_gap_analysis.md`
- `docs/design/V1.0/v1_0_current_gap_analysis.drawio`
- `docs/design/V1.0/v1_0_rc4_final_readiness_report.md`
- `docs/design/V1.0/v1_0_rc7_release_handoff.md`
- `docs/design/V1.0/v1_0_rc6_source_trace_resmoke_report.md`
- `docs/design/V1.0/v1_0_release_checklist.md`
- `docs/design/V1.0/v1_0_integration_readiness_report.md`
- `docs/design/V1.0/data_service_real_route_alignment.md`
- `docs/design/V1.0/feature-route-matrix.md`
