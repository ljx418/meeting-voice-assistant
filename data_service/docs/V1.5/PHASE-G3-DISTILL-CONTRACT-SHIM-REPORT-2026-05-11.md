# PhaseG3 Distill Contract Shim Report

日期：2026-05-11

## 目标

PhaseG3 选择 distill preview 作为接口语义统一的第二个最小能力组。在不新增 MCP distill tool、HTTP route 或 CLI command 的前提下，让 HTTP `/api/v1/knowledge/distill` 和 CLI `data_service distill` 共享同一个内部 payload contract。

## 变更

- 新增 `backend/data_service/distill_contract.py`：
  - `run_distill_contract(...)` 作为 distill preview 的内部 shared service contract。
  - 固化 `limit` 的 1-200 范围。
  - 统一 `kind`、`typed_unit_type`、`authority` 等可选文本过滤参数的空值处理。
  - 统一 `min_importance`、`min_source_weight`、`min_source_density` 的非负数处理。
- `/api/v1/knowledge/distill` HTTP route 改为调用 shared distill contract。
- `data_service distill` CLI 改为调用 shared distill contract。
- 新增端到端 contract 测试：同一个 workspace 下 HTTP / CLI distill 输出字段、filters、unit_id 列表和 source profile source_id 列表必须一致。

## 出门验证

- `npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py::test_phaseg3_distill_contract_shared_by_http_and_cli -q`：1 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：25 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：107 passed。
- Draw.io XML 校验：通过。

## 对外能力检查

- 不新增 MCP tool、HTTP route 或 CLI command。
- 不新增 `knowledge_distill_preview`；该 MCP tool 仍保持 planned。
- 不改变 distill preview 响应字段集合。
- 保持 `/api/v1/knowledge/distill` 和 `data_service distill` 兼容。

## 下一步

进入 PhaseG4：建议开始 trace 能力的接口语义设计，先写目标 contract 文档和 drift tests，暂不新增公开入口。
