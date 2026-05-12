# PhaseG13 Quality CLI Read-only Preview Report

日期：2026-05-11

## 背景

PhaseG13 继续沿 Interface Convergence 主线推进 quality 能力组。PhaseG12 已固化 Quality CLI planned 迁移窗口，本阶段进入 Stage 2，只开放只读 CLI preview，不开放写入型治理命令。

## 变更范围

- `backend/data_service/quality_contract.py`
  - 新增 `quality_summary_payload`。
  - 新增 `quality_correction_plan_preview_payload`。
  - 继续复用 `quality_feedback_list_payload` 与 `quality_correction_rules_payload`。
- `backend/data_service/__main__.py`
  - 新增 `data_service quality summary`。
  - 新增 `data_service quality correction-plan`，支持 `--rebuild`。
  - 新增 `data_service quality feedback-list`。
  - 新增 `data_service quality rules`。
  - `--workspace-id` 作为 `--workspace` 的兼容别名，当前仍解析为本地 workspace directory。
- `backend/tests/test_data_service_api.py`
  - 新增 PhaseG13 CLI read-only preview 端到端测试，验证四个只读命令均复用 shared helper。
- `backend/tests/test_data_service_mcp.py`
  - 更新 quality CLI drift tests，确认只读 CLI preview 已开放，写入型命令未开放。

## 对外能力检查

- MCP：未新增 tool，现有 `knowledge_quality_*` / `knowledge_correction_*` 保持不变。
- HTTP：未新增 route，现有 `/api/v1/knowledge/quality/*` 兼容入口保持不变。
- CLI：新增只读 preview 子命令 `summary / correction-plan / feedback-list / rules`。
- CLI 写入型命令仍不开放：`feedback / rules-build / review`。

## 出门验证

- PhaseG13 API 专项：通过，`19 passed`。
- MCP 专项回归：通过，`30 passed`。
- frontend `npm run build`：通过。
- Data Service/API/MCP 组合回归：通过，`120 passed`。
- drawio XML 校验：通过。
