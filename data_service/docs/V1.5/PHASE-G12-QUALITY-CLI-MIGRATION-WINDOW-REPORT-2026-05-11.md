# PhaseG12 Quality CLI Migration Window Report

日期：2026-05-11

## 阶段目标

PhaseG12 继续沿 Interface Convergence 主线收敛 quality 能力组。本阶段目标是固化 Quality CLI planned 入口迁移窗口，明确目标命令形态、阶段边界和测试护栏，但不开放新的 CLI `quality` 子命令。

## 已完成内容

- 扩展 `docs/V1.5/quality-contract.md`：
  - 新增 PhaseG12 Quality CLI planned 迁移窗口。
  - 明确目标 `data_service quality ...` 命令形态。
  - 明确 Stage 1-4 迁移窗口。
  - 明确未来 CLI 必须复用 `data_service.quality_contract` helper 或现有 MCP handler。
- 新增 PhaseG12 CLI drift test：
  - 验证当前 `data_service` CLI 命令集合仍只有 `ingest / summary / distill / boundary / graphrag-execute / query`。
  - 验证 `quality` 子命令未提前开放。
  - 验证 quality contract 文档包含目标命令形态和 Stage 1-4 迁移窗口。
- 同步更新 `docs/V1.5/interface-convergence-matrix.md`、`docs/V1.5/current-vs-target-gap.md`、`docs/V1.5/current-vs-target-gap.drawio` 与 V1.5 roadmap。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI command。
- 当前 `data_service` CLI 已开放命令集合保持不变。
- CLI `quality` 仍为 planned。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：通过，`30 passed`。
- `cd frontend && npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：通过，`119 passed`。
- drawio XML 校验：通过。
