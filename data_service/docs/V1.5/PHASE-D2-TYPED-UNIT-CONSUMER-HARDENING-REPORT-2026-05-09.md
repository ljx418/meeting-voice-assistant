# PhaseD2 Typed Unit Consumer Hardening Report

日期：2026-05-09

## 目标

在 PhaseD1 已引入 `typed_unit` 兼容字段后，补齐服务消费侧能力：调用方可以按 typed unit type 过滤，治理输出可以看到 typed contract 和类型分布。

## 本阶段完成

- `DataService.read_distill_bundle()` 新增 `typed_unit_type` 参数。
- `backend/data_service/__main__.py` 的 `distill` 命令新增 `--typed-type`。
- `/api/v1/knowledge/distill` 请求模型新增 `typed_unit_type`。
- distill filters 回显 `typed_unit_type`。
- `read_boundary_audit()` 的 `contracts.typed_unit_contract` 展示：
  - typed unit schema version
  - typed unit types
  - legacy kind -> typed type mapping
  - typed unit type counts
  - compatible consumers
- quality summary 的 `quality.distill` 展示 `typed_unit_schema_version` 与 `typed_unit_type_counts`。
- engine handoff 顶层增加 typed unit schema/version 与 typed distribution。

## 出门验证

```bash
backend/.venv/bin/python -m py_compile backend/data_service/service.py backend/data_service/__main__.py backend/app/api/v1/data_service.py backend/tests/test_data_service.py backend/tests/test_data_service_api.py
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py -q
backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

- Data Service 专项回归：`68 passed`
- API 专项回归：`10 passed`
- Data Service/API/MCP 组合回归：`100 passed`

## 验收结论

PhaseD2 通过。typed unit 已不仅是写入字段，而是进入 CLI / HTTP / preview / boundary / quality 的消费面，同时旧 `kind` filter 与旧下游引擎路径保持兼容。

## 下一阶段

PhaseD3 建议补 typed fixture 覆盖：

- 会议 turns fixture 验证 meeting_summary / risk / claim / entity_evidence。
- 代码分析 JSON fixture 验证 architecture_note / code_symbol / code_dependency / code_call_edge 的映射策略。
- GraphRAG / Quality 对 typed 分布做更细粒度诊断。
