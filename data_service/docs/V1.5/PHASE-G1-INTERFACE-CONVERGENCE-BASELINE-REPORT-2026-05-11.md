# PhaseG1 Interface Convergence Baseline Report

日期：2026-05-11

## 目标

进入 PhaseG 接口语义统一。PhaseG1 先建立 MCP / CLI / HTTP 的契约矩阵、迁移文档和测试护栏，不执行破坏性接口迁移。

## 变更

- 新增 `docs/V1.5/interface-convergence-matrix.md`，固化当前三入口能力矩阵。
- 控制台 MCP Contract 增加 Interface Matrix，只读展示 MCP / HTTP / CLI 覆盖情况。
- 新增 contract drift 测试，覆盖：
  - MCP registry 与前端 MCP contract 一致。
  - HTTP route 快照包含当前核心 `/api/v1/knowledge/*` 入口。
  - CLI parser 快照包含当前 `ingest / summary / distill / boundary / graphrag-execute / query`。
  - PhaseG1 文档覆盖 workspace/source/build/query/distill/graph/trace/quality/session 能力分组。
- 修复 `knowledge_build_cancel` 对运行中 build 的即时返回和后台 worker 覆盖竞态：取消请求现在稳定返回 `cancelled`，runtime 在关键阶段复查取消状态，避免对外 contract 短暂暴露 `running` 或被后续完成态覆盖。

## 出门验证

- `npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：24 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：105 passed。
- Playwright 前端验收截图：已归档。
  - `docs/V1.5/frontend-acceptance/data_service_phaseg1_interface_matrix_desktop.png`
  - `docs/V1.5/frontend-acceptance/data_service_phaseg1_interface_matrix_mobile.png`
- Draw.io XML 校验：通过。

## 对外能力检查

- 不新增 MCP tool、HTTP route 或 CLI command。
- 不修改现有 MCP / HTTP / CLI 响应形态。
- `data_service` CLI 和 `/api/v1/knowledge/*` 继续作为兼容入口。
- MCP 是默认主入口，CLI / HTTP 后续按迁移窗口逐步对齐。

## 下一步

进入 PhaseG2：选择一个最小能力组做目标语义 shim，建议优先从 query 或 distill 开始，因为它们已有 CLI / HTTP 兼容入口和可回归样例。
