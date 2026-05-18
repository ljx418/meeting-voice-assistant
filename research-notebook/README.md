# ResearchNotebook

ResearchNotebook is the independent frontend application layer for a source-grounded personal knowledge workspace. It integrates with the local `data_service` backend through `/api/workspaces/...` target routes only.

## Current Status

V1.0-RC1 is integration-smoke ready for:

- Workspace Home;
- Source Library;
- Workspace Build;
- Workspace Ask with Evidence;
- Session Workbench;
- Read-only Graph Community context;
- Lightweight Feedback.

Accepted RC1 degraded states:

- source trace returns unavailable for the current minimal text-source smoke;
- session query may return no evidence;
- graph neighbors require a selected `node_id` / `entity_id`, so graph community is the RC1 graph smoke surface.

## Commands

```bash
npm install
npm run check
npm run smoke:rc1
```

`npm run smoke:rc1` expects a local `data_service` backend, defaulting to:

```text
http://127.0.0.1:8003
```

## Boundary Rules

- Do not call `/api/v1/knowledge/*` from ResearchNotebook.
- Do not fetch directly from feature modules.
- Keep route strings inside `src/shared/api/dataServiceClient.ts`.
- Do not parse `artifact_ref` as a filesystem path.
- Do not claim source preview, precise citation backjump, multi-format ingestion, assessment, graph editing, or quality governance console as V1.0-ready.

## Active Docs

Start with:

- `docs/design/V1.0/v1_0_current_gap_analysis.md`
- `docs/design/V1.0/v1_0_current_gap_analysis.drawio`
- `docs/design/V1.0/v1_0_integration_readiness_report.md`
- `docs/design/V1.0/data_service_real_route_alignment.md`
