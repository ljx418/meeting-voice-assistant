# PhaseG6 Source Trace Schema Migration Report

日期：2026-05-11

## 目标

PhaseG6 补齐 Source Trace request / response schema 示例、HTTP 兼容窗口和 MCP / CLI 迁移说明。本阶段仍不新增 MCP tool、CLI command 或 HTTP route。

## 变更

- 更新 `docs/V1.5/source-trace-contract.md`：
  - 补充当前 HTTP request schema 示例。
  - 补充目标 MCP request schema 示例。
  - 补充目标 CLI 参数示例。
  - 补充 response schema 示例。
  - 明确迁移窗口 Stage 1-4。
- 新增 drift test：
  - 确认 schema 示例记录 `workspace` 和目标 `workspace_id`。
  - 确认 CLI 目标示例记录 `data_service trace source --workspace-id ...`。
  - 确认文档明确 `source_trace_payload` 是后续 MCP / CLI 复用的唯一 serializer。
  - 确认 `limit` contract 与代码常量一致：1-50，默认 12。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py::test_phaseg6_source_trace_schema_examples_document_shared_contract -q`：1 passed。
- `npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：25 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：111 passed。
- Draw.io XML 校验：通过。

## 对外能力检查

- 不新增 `knowledge_source_trace` MCP tool。
- 不新增 `knowledge trace source` CLI command。
- 不新增 HTTP route。
- 不改变当前 `/api/v1/knowledge/source/trace` 响应字段集合。

## 下一步

进入 PhaseG7：建议选择下一个最小能力组做 interface convergence，优先评估 Quality / Low Signal Audit 是否需要 shared contract helper，并继续保持 MCP-first 与最小粒度边界。
