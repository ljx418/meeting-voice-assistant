# PhaseG10 Quality HTTP Shared Helper Report

日期：2026-05-11

## 阶段目标

PhaseG10 继续沿 Interface Convergence 主线收敛 quality 能力组。本阶段目标是把现有 Quality HTTP feedback / rules / review 兼容入口迁移到 `data_service.quality_contract` shared helper，减少 API 层重复组装 payload，同时保持所有对外响应字段不变。

## 已完成内容

- 扩展 `backend/data_service/quality_contract.py`：
  - `record_quality_feedback_payload`
  - `quality_feedback_list_payload`
  - `quality_correction_rules_payload`
  - `quality_correction_rules_build_payload`
  - `quality_correction_rule_review_payload`
- 更新 `backend/app/api/v1/data_service.py`：
  - `/quality/feedback` 复用 `record_quality_feedback_payload`。
  - `/quality/feedback/list` 复用 `quality_feedback_list_payload`。
  - `/quality/corrections` 复用 `quality_correction_rules_payload`。
  - `/quality/corrections/build` 复用 `quality_correction_rules_build_payload`。
  - `/quality/corrections/review` 复用 `quality_correction_rule_review_payload`。
- 新增 PhaseG10 API drift test，验证上述 HTTP route 确实调用 shared helper，且 CLI `quality` 未提前开放。
- 同步更新 `docs/V1.5/quality-contract.md`、`docs/V1.5/interface-convergence-matrix.md`、`docs/V1.5/current-vs-target-gap.md`、`docs/V1.5/current-vs-target-gap.drawio` 与 V1.5 roadmap。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI command。
- Quality HTTP feedback / rules / review 响应字段保持不变。
- API 层只负责 request parsing、workspace resolve 和 HTTP error mapping，不再重新组装 feedback / rules / review payload。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q`：`17 passed`。
- `cd frontend && npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：`29 passed`。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：`117 passed`。
- drawio XML 校验：通过。
