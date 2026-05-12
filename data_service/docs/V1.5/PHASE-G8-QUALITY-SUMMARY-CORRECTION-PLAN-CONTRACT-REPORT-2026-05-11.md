# PhaseG8 Quality Summary / Correction Plan Contract Report

日期：2026-05-11

## 阶段目标

PhaseG8 继续沿 Interface Convergence 主线收敛 quality 能力组。本阶段目标是固化 Quality Summary / Correction Plan 的当前 contract，补充 drift tests，避免后续误把 planned HTTP / CLI 入口提前打开。

## 已完成内容

- 新增 `docs/V1.5/quality-contract.md`，明确 `knowledge_quality_summary` 与 `knowledge_correction_plan` 的 MCP request / response 稳定字段。
- 明确当前公开入口：MCP 为主入口，HTTP 保留既有 `/api/v1/knowledge/quality/corrections/plan` 兼容入口，`/api/v1/knowledge/quality/summary` 未开放。
- 明确 CLI `quality` 命令仍为 planned，不在本阶段新增。
- 新增 PhaseG8 drift tests，覆盖 MCP registry schema、V2 alias、HTTP route 集合、CLI parser 和 E2E response shape。
- 同步更新 `docs/V1.5/interface-convergence-matrix.md`、`docs/V1.5/current-vs-target-gap.md`、`docs/V1.5/current-vs-target-gap.drawio` 与 V1.5 roadmap。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI command。
- `knowledge_quality_summary` 稳定顶层字段保持 `workspace / quality / quality_feedback / quality_correction_rules / quality_correction_plan`。
- `knowledge_correction_plan` 稳定顶层字段保持 `schema_version / workspace / generated_at / source_rule_count / actions / summary / notes`。

## 出门验证

- `cd frontend && npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：`27 passed`。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：`114 passed`。
- drawio XML 校验：通过。
