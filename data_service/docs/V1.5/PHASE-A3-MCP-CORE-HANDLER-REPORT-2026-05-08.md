# V1.5 PhaseA3：Core MCP Handler 模块化报告

日期：2026-05-08

## 目标

完成 V1.5-PhaseA 的第三步：把基础 `knowledge_ingest` / `knowledge_query` MCP tool schema 和 handler 从 `mcp_stdio.py` 中拆出，继续压缩 stdio 入口职责，同时保持 legacy tool 与 V2 envelope tool 兼容。

## 本阶段变更

- 新增 `backend/data_service/mcp_core_tools.py`。
- `mcp_stdio.py` 改为通过 `CORE_TOOL_SPECS` 注册基础 ingest/query 工具。
- `mcp_stdio.py` 改为通过 `handle_core_tool(...)` 分发基础 ingest/query MCP 调用。
- 保留 `knowledge_ingest`、`knowledge_query` 的旧输出。
- 保留 `knowledge_ingest_v2`、`knowledge_query_v2` 对 legacy tool 的 envelope 包装路径。

## 验收结果

### 自动化回归

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_stdio.py backend/data_service/mcp_core_tools.py backend/data_service/mcp_quality_tools.py backend/data_service/mcp_session_tools.py
```

结果：通过。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：

```text
16 passed
```

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

```text
94 passed
```

说明：组合回归首次运行时 `test_data_service_mcp_session_lifecycle_ingest_build_and_delete` 出现一次异步构建状态 `blocked`，该用例单独复跑通过；随后组合回归复跑为 94 passed。

### 出门验证

通过 MCP handler 直接执行：

```text
knowledge_ingest
-> knowledge_query
-> knowledge_query_v2
```

结果摘要：

```json
{
  "ingest_engines": ["llmwiki", "graphrag"],
  "ingest_statuses": ["success", "indexed"],
  "query_mode": "hybrid",
  "query_hit_count": 3,
  "v2_status": "ok",
  "v2_query_hit_count": 6
}
```

## 当前边界

PhaseA 已完成 Session、Quality 和 Core 三类 handler 模块化。`mcp_stdio.py` 当前仍承载 workspace/source/build lifecycle 细节。下一步 PhaseA4 应拆分 workspace/source/build handlers，并评估共享 envelope/error/helper 模块是否应独立。
