# V1.6 Target HTTP Routes Plan

更新时间：2026-05-12

## Baseline

V1.5 target HTTP currently exposes exactly 3 routes:

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

These routes are the V1.6 starting point. No other target HTTP route should be treated as open until a V1.6 phase implements and accepts it.

## Route Opening Policy

- Open routes by capability group.
- Define contract before implementation.
- Reuse shared helpers or existing MCP handlers.
- Preserve `/api/v1/knowledge/*` compatibility routes.
- Use stable IDs, never internal paths, as external contract.

## Candidate Route Groups

| group | status | acceptance requirement |
| --- | --- | --- |
| workspace lifecycle write | planned | create/archive contract, envelope tests, compatibility retention |
| source lifecycle write | planned | import/remove/list contract, `source_id` stability, artifact refs |
| build lifecycle write | planned | start/status/cancel contract, `operation_id` lifecycle |
| graph advanced | planned | target HTTP route contracts for graph advanced surfaces where not yet open; V1.6 does not add existing MCP graph tools |
| quality write | planned | non-destructive governance contract and shared helper reuse |
| session | planned | target HTTP routes and cross-surface Session GraphRAG public contract; V1.6 does not add existing MCP session tools |

## Non Goals

- Do not expose raw workspace directory layout.
- Do not make target HTTP a mirror of every internal method.
- Do not remove compatibility HTTP during V1.6 route opening.
- Do not open graph advanced, quality write and session routes in the same uncontrolled slice.
