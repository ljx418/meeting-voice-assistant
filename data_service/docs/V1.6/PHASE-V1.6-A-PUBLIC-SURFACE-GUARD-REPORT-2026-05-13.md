# Phase V1.6-A Public Surface Guard Report

更新时间：2026-05-13

## 1. Scope

V1.6-A 是 V1.6 的第一个实现阶段。本阶段只做 public surface guard、机器可读基线、自动化扫描、回归门禁、报告和必要文档同步。

本阶段不新增业务能力，不新增 MCP tool、HTTP route、CLI command 或 CLI subcommand，不修改 target HTTP allowlist，不修改 `/api/v1/knowledge/*` compatibility routes。

## 2. Baseline

V1.5 accepted baseline：

- MCP tool count：`40`
- CLI top-level commands：`build / graph / quality / query / source / trace / workspace`
- target HTTP allowlist：
  - `POST /api/workspaces/{workspace_id}/query`
  - `POST /api/workspaces/{workspace_id}/distill`
  - `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- compatibility HTTP：`/api/v1/knowledge/*` retained
- `/knowledge` remains service governance console
- MCP graph/session tools already exist in the V1.5 baseline

Machine-readable baseline：

- `docs/V1.6/public-surface-baseline.json`

## 3. Guard Implementation

Implemented in `backend/tests/test_public_surface_guard.py`：

- MCP registry guard：reads `all_tool_specs()`, normalizes tool set, checks count and set diff.
- CLI parser guard：reads `knowledge ...` parser, normalizes top-level and nested command inventory.
- HTTP route inventory guard：scans only `/api/v1/knowledge/*` and `/api/workspaces/*`, ignores docs/openapi/static/frontend routes and generated HEAD/OPTIONS.
- Boundary guard：scans production imports under `backend/data_service`, `backend/app/graphrag/service`, and `backend/app/llmwiki`.
- Target HTTP contract smoke check：query/distill/source trace target HTTP still match legacy compatibility payloads.

## 4. Public Surface Scan Result

### MCP

- baseline count：`40`
- current count：`40`
- diff：none
- new tools：none

MCP graph/session tools are part of the V1.5 baseline. V1.6-A does not add graph/session MCP tools.

### CLI

- baseline top-level commands：`build / graph / quality / query / source / trace / workspace`
- current top-level commands：`build / graph / quality / query / source / trace / workspace`
- top-level diff：none
- nested command diff：none
- new commands：none

### HTTP

- compatibility baseline：`/api/v1/knowledge/*`
- compatibility current：retained
- compatibility route diff：none
- target HTTP baseline/current：
  - `POST /api/workspaces/{workspace_id}/query`
  - `POST /api/workspaces/{workspace_id}/distill`
  - `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- target HTTP diff：none
- new routes：none

## 5. Boundary Scan Result

- upper-layer production dependency：none
- scanned production roots：
  - `backend/data_service`
  - `backend/app/graphrag/service`
  - `backend/app/llmwiki`
- stable external ID rule preserved：`workspace_id` / `source_id` / `session_id` / `operation_id` / `artifact_ref`
- internal path/layout remains debug/console-only and non-contract
- `/knowledge` remains service governance console
- V1.6-B/C/D/E/F planned capabilities are documented only, not implemented in V1.6-A

## 6. Regression Result

- MCP registry guard：`5 passed`
- API regression：`34 passed`
- MCP regression：`32 passed`
- combined data_service/API/MCP regression：`137 passed`
- combined with public surface guard：`142 passed`
- CLI parser / command scan：passed as part of public surface guard
- HTTP route inventory guard：passed as part of public surface guard
- Boundary guard：passed as part of public surface guard
- frontend `npm run build`：not touched
- drawio XML validation：passed (`drawio xml ok`)

Notes：

- `python3` initially lacked `pytest`; Python 3.13 user-site `pytest` and `pytest-asyncio` were installed to run the regression suite.
- Python 3.9 pytest was not used for final regression because `test_data_service_api.py` imports `tomllib`.

## 7. Documentation Sync

Updated V1.6 documents：

- `docs/V1.6/README.md`
- `docs/V1.6/public-surface-baseline.json`
- `docs/V1.6/target-architecture.md`
- `docs/V1.6/development-plan.md`
- `docs/V1.6/acceptance-plan.md`
- `docs/V1.6/current-vs-target-gap.md`
- `docs/V1.6/current-vs-target-gap.drawio`
- `docs/V1.6/public-surface-baseline.md`
- `docs/V1.6/interface-convergence-plan.md`
- `docs/V1.6/target-http-routes-plan.md`

Documentation sync result：

- V1.6-A marked completed.
- V1.6-A described as guard-only, with no business capability added.
- MCP graph/session tools clarified as existing V1.5 baseline tools.
- V1.6-C described as graph advanced target HTTP / CLI minimal surfaces where not yet open.
- V1.6-D described as cross-surface Session GraphRAG public contract convergence.
- V1.6-B/C/D/E/F remain planned / candidate, not implemented.

## 8. Blocking Issues

none

## 9. Final Decision

accepted

V1.6-A Public Surface Guard is accepted. The surface is frozen against the V1.5 baseline, the contracts are guarded, and V1.6 can proceed to the next planned slice.

## 10. Next Phase Recommendation

Next phase：`V1.6-B1 Workspace Target HTTP`

Do not enter full V1.6-B all at once. Before V1.6-B1 implementation, run public surface guard as the pre-flight gate.
