# Security and Quality Regression Fix Report - 2026-04-30

## 背景

本轮基于四个独立审查视角完成修复回归：安全性、代码风格、架构与实现偏差、功能与当前实现偏差。

## 已修复

- 移除仓库对 `backend/app/.env` 和 `.DS_Store` 的跟踪，新增 `backend/app/.env.example`，真实密钥不再进入版本控制。
- `/api/v1/knowledge/*` 增加 data_service workspace allowlist；ingest source path 增加 source allowlist，阻止任意绝对路径读写。
- CORS 默认从 `*` 收紧到本地前端 origin，可通过 `CORS_ALLOW_ORIGINS` 配置。
- MCP stdio 不再用 tool call 修改全局 workspace；每次调用独立解析并校验 workspace/source path。
- 前端 Markdown 预览不再裸渲染 `marked.parse()` 结果，增加 HTML 净化，移除 script、危险事件属性和 `javascript:` URL。
- LLMWiki query 现在消费 approved quality plan，和 read page、GraphRAG query 行为保持一致。
- Graph policy 修复 community rename/suppress、merge 到已存在 canonical 节点时的去重、edge 重写和 stats 语义。
- `/summary` 读路径不再无条件重写 summary 或隐式生成 correction plan，降低读接口副作用。
- correction plan impact 补 `summary.total_matches`，使 MCP 测试契约与实际 payload 对齐。
- LLMWiki ingest 默认不再自动落盘改写 markdown；MCP 不再暴露落盘改写工具，读时治理避免 revoke 后无法回滚。

## 回归结果

```text
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
73 passed, 3 skipped

npx vite build
passed
```

`npm run build` 当前仍失败在既有 Node 24 + `vue-tsc` 兼容问题：

```text
Search string not found: "/supportedTSExtensions = .*(?=;)/"
Node.js v24.14.0
```

## 剩余注意项

- 已提交过的真实 API Key 仍必须在服务商侧吊销并轮换；仅从 git 跟踪移除不能撤销历史泄漏。
- `DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS` / `DATA_SERVICE_ALLOWED_SOURCE_ROOTS` 应在生产或共享环境中显式配置为最小目录集合。
- `DATA_SERVICE_REQUIRE_API_KEY=true` 后，调用方需要通过 `X-API-Key` 提供 API Key。
