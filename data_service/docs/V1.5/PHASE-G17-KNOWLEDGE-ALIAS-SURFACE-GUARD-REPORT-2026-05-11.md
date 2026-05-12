# PhaseG17 Knowledge Alias Surface Guard Report

日期：2026-05-11

## 背景

PhaseG16 已声明 `knowledge = data_service.__main__:knowledge_main` console script。复查后发现如果 `knowledge_main` 直接复用完整 `data_service` parser，会隐式开放 `knowledge ingest/query/distill/boundary/graphrag-execute` 等入口，偏离“不要一次性扩大公开面”的阶段计划。

## 变更范围

- `backend/data_service/__main__.py`
  - 抽取 `_add_quality_parser`，让 `data_service` 和 `knowledge` 共享 quality 子命令定义。
  - 新增 `_build_knowledge_parser`，当前只挂载 `quality` 顶层命令。
  - `knowledge_main` 改为使用 `_build_knowledge_parser`，不再复用完整 `data_service` parser。
- `backend/tests/test_data_service_api.py`
  - 新增 PhaseG17 测试，验证 `knowledge` 顶层 choices 严格等于 `{"quality"}`。
- `backend/tests/test_data_service_mcp.py`
  - 更新 drift test，验证文档和 parser 都未隐式开放更多 `knowledge *` alias。

## 对外能力检查

- MCP：未新增 tool。
- HTTP：未新增 route。
- CLI：`knowledge` console script 当前只开放 `quality` 能力组；`data_service` 兼容 CLI 不变。

## 出门验证

- PhaseG17 API 专项：通过，`23 passed`。
- MCP 专项回归：通过，`30 passed`。
- frontend `npm run build`：通过。
- Data Service/API/MCP 组合回归：通过，`124 passed`。
- drawio XML 校验：通过。
