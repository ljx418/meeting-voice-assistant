# Phase 3 阶段验收报告

验收日期：2026-04-29

## 结论

`Phase 3：GraphRAG 职责收口` 已完成阶段性验收。`app.graphrag` 已成为默认 graph execution owner；`data_service` 保留 ingest 编排、contract staging、summary/API/CLI/MCP 和统一查询入口，不再直接承载 graph query model、community assembly 或 compat materializer 实现。

## 代码边界

已完成：

- 默认 `graphrag_execution_owner` 切换为 `app.graphrag`
- CLI `data_service ingest` 默认使用 `--graphrag-owner app.graphrag`
- HTTP `/api/v1/knowledge/ingest` 默认使用 `app.graphrag`
- `GraphRAGWorkspaceAdapter` 不再直接导入 `GraphCompatMaterializer`
- graph state 物化统一通过 `app.graphrag.service.materialize_workspace_graph_state`
- `app.graphrag` runner 在 GraphRAG CLI 不可用或执行失败时，会使用 compat materializer 完成 graph state，保证本地验收仍可 indexed
- `graph_query_model` 与 `community_snapshot_assembly` 在 boundary audit 中归属 `app.graphrag.service`

## 验收命令与结果

自动化回归：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- `53 passed in 12.75s`
- 仅出现既有 `urllib3` LibreSSL warning

真实知识库端到端：

```bash
cd backend
python3 -m data_service ingest \
  --workspace /tmp/data-service-phase3-final-owner-summary-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

结果：

- 86 sources
- `llmwiki: success`
- `graphrag: indexed`
- 248 distilled units
- graph execution owner: `app.graphrag`
- compat state: 85 entities / 76 themes / 131 relationships
- payload source: `app.graphrag.bridge`

Boundary audit：

- `graph_index_execution`: `current_owner=app.graphrag`, `target_owner=app.graphrag`, `status=done`
- `graph_query_model`: `current_owner=app.graphrag.service`, `status=done`
- `community_snapshot_assembly`: `current_owner=app.graphrag.service`, `status=done`
- `data_service.owns_now`: `workspace_layout / distill_contract / summary_generation / unified_query_entry / graph_ingest_orchestration`

## 保留事项

- 当前环境中的 GraphRAG native CLI 增强验收未通过：`/usr/local/bin/graphrag` 指向已不存在的 `/tmp/graphrag_patched.py`。2026-04-29 已补 preflight，runner 现在明确返回 `graphrag_cli_broken` 与 `cli_health`，并使用 `app_graphrag_compat_materializer` 完成本地图谱 state。这不影响 Phase 3 的 owner 边界，但后续如果要启用完整 Microsoft GraphRAG CLI，应修复本地 CLI shim 或重新安装 GraphRAG CLI。
- LLMWiki 页面标题自然度、topic 聚合和 `/knowledge` 产品化继续进入后续质量阶段。
