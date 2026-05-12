# PhaseG31.1 Doc Path Regression Unblock Report

日期：2026-05-12

## 1. Scope

PhaseG31.1 只解除 V1.5 文档整理后的回归阻塞，不新增能力、不扩展公开面、不进入 V1.6-B/C/D/E/F 实现。

本阶段未新增：

- MCP tool
- HTTP route
- CLI command
- target HTTP route
- graph / session / quality / lifecycle 能力

## 2. Root Cause

V1.5 canonical contract docs 已迁移到 `docs/V1.5/`，但部分 regression tests 仍硬编码读取旧路径 `docs/data_service/*.md`，导致 FileNotFoundError。

受影响旧路径：

- `docs/data_service/source-trace-contract.md`
- `docs/data_service/target-http-routes-contract.md`
- `docs/data_service/graph-cli-contract.md`
- `docs/data_service/interface-convergence-matrix.md`
- `docs/data_service/quality-contract.md`

当前 canonical V1.5 路径：

- `docs/V1.5/source-trace-contract.md`
- `docs/V1.5/target-http-routes-contract.md`
- `docs/V1.5/graph-cli-contract.md`
- `docs/V1.5/interface-convergence-matrix.md`
- `docs/V1.5/quality-contract.md`

## 3. Changes

测试路径修复：

- `backend/tests/test_data_service_api.py`
  - 新增 `V15_DOCS_ROOT = Path("docs/V1.5")`。
  - 将 Source Trace、target HTTP、graph CLI、interface matrix contract 文档读取改为 `docs/V1.5`。
- `backend/tests/test_data_service_mcp.py`
  - 新增 `V15_DOCS_ROOT = Path("docs/V1.5")`。
  - 将 Interface Matrix、Quality contract、Graph CLI contract 文档读取改为 `docs/V1.5`。

V1.6 文档措辞修正：

- 明确 MCP graph/session tools already exist in the V1.5 baseline。
- 明确 V1.6 does not add existing MCP graph/session tools as new MCP tools。
- 明确 V1.6-C focuses on graph advanced target HTTP / CLI minimal surfaces where not yet open。
- 明确 V1.6-D focuses on cross-surface Session GraphRAG public contract convergence。
- planned 能力仍保持 planned，未写成 implemented。

## 4. Regression Results

- API regression：`34 passed`。
- MCP regression：`32 passed`。
- Combined data_service/API/MCP regression：`137 passed`。
- Frontend `npm run build`：not touched in PhaseG31.1。
- Drawio XML validation：not touched in PhaseG31.1。

## 5. Public Surface Scan

MCP registry：

- Tool count：`40`。
- New MCP tools：none。

CLI parser：

- Top-level commands：`build / graph / quality / query / source / trace / workspace`。
- New CLI commands：none。

HTTP route inventory：

target HTTP remains exactly:

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

Compatibility HTTP:

- `/api/v1/knowledge/*` compatibility routes retained。

## 6. Final Status

PhaseG31.1 closure result：accepted。

The V1.5 status can move from `blocked-by-doc-path-regression` back to `accepted`。

PhaseG31.1 did not add product capability or expand public surface. It only updated regression tests to read the canonical V1.5 contract docs and clarified V1.6 planning language.
