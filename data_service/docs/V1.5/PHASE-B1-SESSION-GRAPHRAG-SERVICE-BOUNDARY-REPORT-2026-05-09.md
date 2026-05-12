# PhaseB1 Session GraphRAG Service Boundary 阶段报告

日期：2026-05-09

## 目标

PhaseB 的方向是将 session graph build/query/community/neighbor 从 `data_service` 下沉到 `app.graphrag.service`。本子阶段先完成读写侧图谱能力的服务边界抽取，让 `data_service` 保持 MCP/session lifecycle 编排层定位。

## 本阶段改动

- 新增 `backend/app/graphrag/service/session_graph_service.py`。
- 新增 `SessionGraphService`，承载：
  - session graph materialization
  - graph snapshot 裁剪
  - graph neighbors
  - community summary
  - session query
  - actor summary
  - graph stats / session summary
- `backend/data_service/session_service.py` 改为委托 `SessionGraphService`：
  - 继续保留 session create/get/list/close/delete。
  - 继续保留 structured ingest、operation 文件和 build operation 编排。
  - 不再本地承载 session graph 构建、社区、查询和 actor summary 算法实现。
- `backend/app/graphrag/service/__init__.py` 导出 session graph service contract。
- `backend/tests/test_data_service_mcp.py` 新增 GraphRAG service 边界 contract 测试。

## 出门验证

编译检查：

```bash
backend/.venv/bin/python -m py_compile backend/app/graphrag/service/session_graph_service.py backend/data_service/session_service.py backend/data_service/mcp_session_tools.py
```

结果：通过。

MCP 专项回归：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：20 passed。

组合回归：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：98 passed。

## 验收覆盖

- 3 speaker / 10 turn session E2E 仍通过。
- session graph snapshot 仍包含 actor、unit、topic、entity、source。
- actor summary 保留 `source_refs`。
- session query 能返回 session graph 命中。
- disposed session graph 返回稳定 disposed payload。
- A/B session scope 不串扰。
- 新增边界测试直接验证 `SessionGraphService` 可独立构建 graph，并保留 actor decision 与 source_refs。

## 当前边界

- `data_service`：MCP tool handler、session lifecycle、ingest、operation status、workspace 持久化编排。
- `app.graphrag.service`：session graph materialization、snapshot、neighbors、community、query、actor summary。

## 下一步

- PhaseB2：继续把 session distill / relation extraction 的正式 schema 与 GraphRAG service 边界收敛，减少 `SessionKnowledgeService` 内启发式抽取逻辑。
- 保持每个子阶段完成后运行端到端出门验证，并同步 `current-vs-target-gap.md` 与 drawio。
