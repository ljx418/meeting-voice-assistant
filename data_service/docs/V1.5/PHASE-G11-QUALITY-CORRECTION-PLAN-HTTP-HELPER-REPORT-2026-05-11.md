# PhaseG11 Quality Correction Plan HTTP Helper Report

日期：2026-05-11

## 阶段目标

PhaseG11 继续沿 Interface Convergence 主线收敛 quality 能力组。本阶段目标是把现有 HTTP `/api/v1/knowledge/quality/corrections/plan` 兼容入口迁移到 `data_service.quality_contract` shared helper，补齐 PhaseG10 后剩余的 quality HTTP 直连 service 调用。

## 已完成内容

- 扩展 `backend/data_service/quality_contract.py`：
  - 新增 `quality_correction_plan_payload(service)`。
- 更新 `backend/app/api/v1/data_service.py`：
  - `/quality/corrections/plan` 复用 `quality_correction_plan_payload`。
- 新增 PhaseG11 API drift test，验证 HTTP correction plan route 确实调用 shared helper，且 plan 稳定顶层字段不变。
- 同步更新 `docs/V1.5/quality-contract.md`、`docs/V1.5/interface-convergence-matrix.md`、`docs/V1.5/current-vs-target-gap.md`、`docs/V1.5/current-vs-target-gap.drawio` 与 V1.5 roadmap。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI command。
- HTTP `/quality/corrections/plan` 响应字段保持不变。
- `quality_correction_plan_payload` 继续保持既有 HTTP build 语义，不新增 `rebuild` 请求字段。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q`：`18 passed`。
- `cd frontend && npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：`29 passed`。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：`118 passed`。
- drawio XML 校验：通过。
