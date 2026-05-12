# PhaseG2 Query Contract Shim Report

日期：2026-05-11

## 目标

PhaseG2 选择 query 作为接口语义统一的最小能力组。在不新增 MCP tool、HTTP route 或 CLI command 的前提下，消除 MCP / HTTP / CLI 三入口各自手写 query 响应结构的漂移风险。

## 变更

- 新增 `backend/data_service/query_contract.py`：
  - `run_query_contract(...)` 作为 query 能力的内部 shared service contract。
  - `query_response_payload(...)` 固化 `mode / query / answer / hits / engine_payloads` 输出结构。
  - `normalize_query_mode(...)` 同时接受 `QueryMode` 枚举和字符串值。
  - `normalize_query_top_k(...)` 固化 `top_k` 的 1-50 范围。
- `knowledge_query` MCP handler 改为调用 shared query contract。
- `/api/v1/knowledge/query` HTTP route 改为调用 shared query contract。
- `data_service query` CLI 改为调用 shared query contract。
- 新增端到端 contract 测试：同一个 workspace 下 MCP / HTTP / CLI query 输出字段、mode、query、answer、hit title 和 engine payload keys 必须一致。

## 出门验证

- `npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：25 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：106 passed。
- Draw.io XML 校验：通过。

## 对外能力检查

- 不新增 MCP tool、HTTP route 或 CLI command。
- 不改变 query 响应字段集合：仍为 `mode / query / answer / hits / engine_payloads`。
- 仅将重复序列化逻辑迁移到内部 helper。
- 保持 `knowledge_query`、`knowledge_query_v2`、`/api/v1/knowledge/query` 和 `data_service query` 兼容。

## 下一步

进入 PhaseG3：建议对 distill 复用同一模式，抽取 `distill_contract.py`，让 HTTP / CLI 先共享 distill preview payload；MCP 入口仍先停留在 planned 状态，不新增公开 tool。
