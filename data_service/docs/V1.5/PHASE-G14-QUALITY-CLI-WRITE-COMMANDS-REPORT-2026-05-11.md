# PhaseG14 Quality CLI Write Commands Report

日期：2026-05-11

## 背景

PhaseG14 继续沿 Interface Convergence 主线推进 quality 能力组。PhaseG13 已开放 `data_service quality` 只读 preview，本阶段进入 Stage 3，开放写入型治理命令，同时保持 MCP-first 和 non-destructive governance。

## 变更范围

- `backend/data_service/__main__.py`
  - 新增 `data_service quality feedback`。
  - 新增 `data_service quality rules-build`。
  - 新增 `data_service quality review`。
  - `feedback` 支持 `--metadata-json`，仅接受 JSON object。
- `backend/tests/test_data_service_api.py`
  - 新增 PhaseG14 CLI write commands 端到端测试，验证三个写入命令均复用 shared helper。
- `backend/tests/test_data_service_mcp.py`
  - 更新 quality CLI drift tests，确认 Stage 2/3 CLI 命令均已开放并保持文档一致。

## 对外能力检查

- MCP：未新增 tool，现有 `knowledge_quality_*` / `knowledge_correction_*` 保持不变。
- HTTP：未新增 route，现有 `/api/v1/knowledge/quality/*` 兼容入口保持不变。
- CLI：新增写入型治理命令 `feedback / rules-build / review`。
- 写入语义：仍为 non-destructive governance，只记录 feedback、生成/审核 correction rules、刷新 approved correction plan，不直接改写 source。

## 出门验证

- PhaseG14 API 专项：通过，`20 passed`。
- MCP 专项回归：通过，`30 passed`。
- frontend `npm run build`：通过。
- Data Service/API/MCP 组合回归：通过，`121 passed`。
- drawio XML 校验：通过。
