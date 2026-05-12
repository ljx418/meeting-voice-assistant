# PhaseB2 Session Relation Extractor 阶段报告

日期：2026-05-09

## 目标

PhaseB1 已将 session graph build/query/community/neighbor 下沉到 `app.graphrag.service`。PhaseB2 继续把 session distill / relation extraction 的启发式规则从 `data_service` 移出，让 `data_service` 只负责 session source payload 读取和 operation 编排。

## 本阶段改动

- 新增 `backend/app/graphrag/service/session_relation_extractor.py`。
- 新增 `SessionRelationExtractor`，承载：
  - session unit classification
  - topic extraction
  - entity extraction
  - actor relation generation
  - unit/source/topic/entity relation generation
  - source-to-source relation
  - entity co-occurrence relation
- `backend/data_service/session_service.py` 的 `_distill_session` 改为：
  - 读取 `sessions/{session_id}/sources.json`。
  - 读取每个 session source 的 records。
  - 将 source payload 交给 `SessionRelationExtractor.extract(...)`。
- `backend/app/graphrag/service/__init__.py` 导出 `SessionRelationExtractor`。
- `backend/tests/test_data_service_mcp.py` 新增 relation extractor boundary contract 测试。

## 出门验证

编译检查：

```bash
backend/.venv/bin/python -m py_compile backend/app/graphrag/service/session_relation_extractor.py backend/app/graphrag/service/session_graph_service.py backend/data_service/session_service.py backend/data_service/mcp_session_tools.py
```

结果：通过。

MCP 专项回归：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：21 passed。

组合回归：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：99 passed。

## 验收覆盖

- relation extractor 可独立生成 decision/task/risk units。
- actor relation 覆盖 `actor_proposed_decision`、`actor_accepted_task`、`actor_raised_risk`。
- source relation 覆盖 `source_related_to_source`。
- unit source_refs 保留 `record_id`。
- 既有 3 speaker / 10 turn session E2E 仍通过。
- A/B session scope 仍不串扰。
- actor summary source_refs 仍保留。

## 当前边界

- `data_service`：MCP tool handler、session lifecycle、source payload 读取、operation status、workspace 持久化编排。
- `app.graphrag.service.SessionRelationExtractor`：session record 到 units/relations/actors/source_nodes 的抽取。
- `app.graphrag.service.SessionGraphService`：session graph materialization、snapshot、neighbors、community、query、actor summary。

## 下一步

PhaseB 核心服务边界已收敛。下一阶段建议进入 PhaseC Contract Hardening：

- 外部 payload 默认使用 opaque `artifact_ref`。
- 真实 path 只作为 debug / console 字段暴露。
- 收敛 blocked / failed / disposed error code。
- 增加 no-internal-path contract 测试。
