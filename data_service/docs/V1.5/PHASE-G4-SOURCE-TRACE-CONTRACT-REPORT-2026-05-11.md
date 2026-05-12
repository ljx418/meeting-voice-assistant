# PhaseG4 Source Trace Contract Report

日期：2026-05-11

## 目标

PhaseG4 进入 trace 能力的接口语义设计阶段。本阶段只固化 Source Trace 目标 contract、矩阵状态和漂移测试，不新增 MCP tool、HTTP route 或 CLI command。

## 变更

- 新增 `docs/V1.5/source-trace-contract.md`：
  - 固化当前 HTTP 入口 `POST /api/v1/knowledge/source/trace`。
  - 明确 planned MCP 入口 `knowledge_source_trace`。
  - 明确 planned CLI 入口 `knowledge trace source --workspace <workspace> --source-id <source_id>`。
  - 固化当前响应顶层字段：`workspace / source_id / source / distill / llmwiki / graphrag / trace_summary`。
  - 固化 distill、llmwiki、graphrag 和 trace_summary 子字段集合。
- 更新接口矩阵和控制台 contract 文案，标记 trace 为 PhaseG4 target contract documented。
- 新增 drift tests：
  - 确认当前只有 HTTP `/knowledge/source/trace` route。
  - 确认 MCP registry 未新增 `knowledge_source_trace`。
  - 确认 CLI parser 未新增 `trace` command。
  - 确认文档、矩阵和前端 contract 同步记录 planned trace 入口。
  - 确认 HTTP trace 响应字段集合保持稳定。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py::test_phaseg4_source_trace_target_contract_documents_current_surface backend/tests/test_data_service_api.py::test_phaseg4_source_trace_response_shape_stays_stable -q`：2 passed。
- `npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：25 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：109 passed。
- Draw.io XML 校验：通过。

## 对外能力检查

- 不新增 `knowledge_source_trace` MCP tool。
- 不新增 `knowledge trace source` CLI command。
- 不新增 HTTP route。
- 不改变当前 `/api/v1/knowledge/source/trace` 响应字段集合。

## 下一步

进入 PhaseG5：建议抽取 `source_trace_contract.py` shared serializer，让当前 HTTP 入口先走内部 contract helper；如后续开放 MCP / CLI trace，再复用同一 helper。
