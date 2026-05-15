# Phase V1.6-B1 Workspace Target HTTP Report

更新时间：2026-05-13

## 1. Scope

V1.6-B1 只开放 workspace lifecycle 的最小 target HTTP surface。

本阶段实现：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`

本阶段不处理 source/build/graph/session/quality target HTTP，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不修改 `/api/v1/knowledge/*` compatibility routes。

## 2. Baseline

V1.5 accepted baseline remains immutable：

- MCP tool count：`40`
- CLI top-level commands：`build / graph / quality / query / source / trace / workspace`
- target HTTP baseline：exactly 3 routes
  - `POST /api/workspaces/{workspace_id}/query`
  - `POST /api/workspaces/{workspace_id}/distill`
  - `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- compatibility HTTP：`/api/v1/knowledge/*` retained
- `/knowledge` remains service governance console

V1.6-A Public Surface Guard：accepted。

## 3. Phase Overlay

B1 uses phase overlay instead of modifying the V1.5 baseline.

Overlay file：

- `docs/V1.6/public-surface-overlays/v1_6_b1.json`

Allowed target HTTP additions：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`

Allowed MCP tool additions：none。

Allowed CLI command additions：none。

Allowed compatibility HTTP additions：none。

## 4. Implemented Routes

### `POST /api/workspaces`

Creates or registers a managed workspace by reusing existing workspace lifecycle helpers.

Contract notes：

- request：`name`, optional `owner`, optional `tags`
- `bound_paths` is unsupported in B1 target HTTP and rejected by request validation
- synchronous operation; no fake `operation_id`
- default response uses stable metadata only

### `GET /api/workspaces`

Lists managed workspaces.

Contract notes：

- query：`owner`, `tag`, `limit`
- response contains stable workspace item list
- default response does not expose filesystem path/layout

### `GET /api/workspaces/{workspace_id}`

Describes one managed workspace.

Contract notes：

- unknown `workspace_id` returns HTTP 404 with normalized error detail
- response contains stable workspace metadata and summary/source/engine/quality overview
- default response does not expose filesystem path/layout

### `POST /api/workspaces/{workspace_id}/archive`

Soft archives one managed workspace.

Contract notes：

- request：optional `reason`
- non-destructive; does not delete data or artifacts
- repeated archive follows existing lifecycle semantics and returns archived state
- synchronous operation; no fake `operation_id`

## 5. Contract Summary

Stable external fields：

- `workspace_id`
- envelope `status`
- envelope `operation_id` as optional and `null` for sync workspace create/archive
- `artifact_ref`
- normalized error detail for unknown workspace and validation failures

Default target HTTP responses do not expose:

- `workspace_path`
- `root_path`
- `filesystem_path`
- `artifact_physical_path`
- `workspace_layout`
- `artifact_layout`
- `internal_path`
- `bound_paths`
- `debug_paths`

Compatibility routes remain retained and usable.

## 6. Public Surface Scan Result

### MCP

- baseline count：`40`
- current count：`40`
- diff：none
- new MCP tools：none

### CLI

- baseline top-level commands：`build / graph / quality / query / source / trace / workspace`
- current top-level commands：`build / graph / quality / query / source / trace / workspace`
- top-level diff：none
- nested command diff：none
- new CLI commands/subcommands：none

### HTTP

Target HTTP baseline：3 routes.

B1 allowed additions：4 routes.

Current target HTTP surface：7 routes.

Current route inventory：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`
- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

Diff from V1.5 target baseline：exactly B1 overlay.

Diff from expected current surface：none.

New non-B1 HTTP routes：none.

Compatibility HTTP route diff：none.

## 7. Focused Tests

Focused test file：

- `backend/tests/test_target_http_workspace.py`

Coverage：

- workspace create/list/describe/archive
- unknown workspace
- repeated archive
- archived workspace write behavior remains blocked through existing lifecycle rules
- default response no internal path/layout leakage
- compatibility workspace routes retained
- target/compat workspace lifecycle semantic parity
- `bound_paths` unsupported in B1 target HTTP
- auth/security smoke

## 8. Regression Results

- public surface guard：`5 passed`
- B1 focused tests：`5 passed`
- API regression：`34 passed`
- MCP regression：`32 passed`
- combined data_service/API/MCP regression：`137 passed`
- combined with public surface guard and B1 focused tests：`147 passed`
- frontend `npm run build`：not touched
- drawio XML validation：passed (`drawio xml ok`)

## 9. Documentation Sync

Updated documents：

- `docs/V1.6/README.md`
- `docs/V1.6/development-plan.md`
- `docs/V1.6/acceptance-plan.md`
- `docs/V1.6/current-vs-target-gap.md`
- `docs/V1.6/current-vs-target-gap.drawio`
- `docs/V1.6/target-architecture.md`
- `docs/V1.6/target-http-routes-plan.md`
- `docs/V1.6/interface-convergence-plan.md`
- `docs/V1.6/public-surface-baseline.md`

Added：

- `docs/V1.6/public-surface-overlays/v1_6_b1.json`
- `docs/V1.6/PHASE-V1.6-B1-WORKSPACE-TARGET-HTTP-REPORT-2026-05-13.md`

Documentation sync result：

- V1.5 public surface baseline remains immutable.
- B1 additions are recorded as phase overlay / allowed additions.
- source/build target HTTP remain planned.
- graph/session/quality target HTTP remain planned.
- V1.6-C/D/E/F remain planned / candidate.
- MCP graph/session tools remain V1.5 baseline tools, not V1.6-B1 additions.
- `/knowledge` remains service governance console.

## 10. Blocking Issues

none

## 11. Final Decision

accepted

V1.6-B1 Workspace Target HTTP is accepted.

## 12. Next Phase Recommendation

Next phase：`V1.6-B2 Source Target HTTP`

Do not open source/build target HTTP all at once. Before B2 implementation, run public surface guard as the pre-flight gate.
