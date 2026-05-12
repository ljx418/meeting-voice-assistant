# PhaseG5 Source Trace Shared Contract Report

日期：2026-05-11

## 目标

PhaseG5 将 Source Trace 当前 HTTP 实现背后的 payload 组装逻辑抽为 shared contract helper。本阶段只让现有 HTTP `/api/v1/knowledge/source/trace` 复用同一个 serializer，不新增 MCP tool、CLI command 或 HTTP route。

## 变更

- 新增 `backend/data_service/source_trace_contract.py`：
  - `source_trace_payload(service, source_id, limit=12)` 统一生成 Source Trace payload。
  - 固化 `source_id` 与 `limit` normalization。
  - 保持响应顶层字段：`workspace / source_id / source / distill / llmwiki / graphrag / trace_summary`。
  - 保持 distill、llmwiki、graphrag 和 trace_summary 子字段集合。
- 更新 HTTP route：
  - `POST /api/v1/knowledge/source/trace` 改为调用 `source_trace_payload`。
  - API 层不再持有 Source Trace payload 组装逻辑。
- 新增 contract test：
  - 确认 HTTP response 与 shared helper 输出完全一致。
  - 确认仍未新增 `knowledge_source_trace` MCP tool。
  - 确认仍未新增 CLI `trace` command。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py::test_phaseg4_source_trace_response_shape_stays_stable backend/tests/test_data_service_api.py::test_phaseg5_source_trace_http_uses_shared_contract_helper -q`：2 passed。
- `npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：25 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：110 passed。
- Draw.io XML 校验：通过。

## 对外能力检查

- 不新增 `knowledge_source_trace` MCP tool。
- 不新增 `knowledge trace source` CLI command。
- 不新增 HTTP route。
- 不改变当前 `/api/v1/knowledge/source/trace` 响应字段集合。

## 下一步

进入 PhaseG6：在不立即开放新入口的前提下，补充 Source Trace contract 文档中的 request / response schema 示例与迁移说明；如后续决定开放 MCP / CLI trace，应直接复用 `source_trace_payload`。
