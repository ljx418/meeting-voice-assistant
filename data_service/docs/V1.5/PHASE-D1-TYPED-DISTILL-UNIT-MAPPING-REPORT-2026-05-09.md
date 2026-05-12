# PhaseD1 Typed Distill Unit Mapping Report

日期：2026-05-09

## 目标

在不破坏旧 `DistilledUnitKind`、LLMWiki、GraphRAG 和外部调用方的前提下，引入 typed distill units v1.2 兼容层，为后续 retrieval、quality、会议/学习/代码理解适配器提供更稳定的语义 contract。

## 本阶段完成

- `DataService.DISTILL_SCHEMA_VERSION` 升级为 `1.2`。
- 新增 `DataService.TYPED_DISTILL_UNIT_SCHEMA_VERSION == "typed-distill-unit-1.2"`。
- 新增 legacy kind 到 typed unit type 的映射：
  - `topic_candidate -> concept`
  - `conclusion -> claim`
  - `step -> workflow`
  - `note -> meeting_summary`
  - `risk -> risk`
  - `example -> example`
  - `fact_candidate -> fact`
  - `entity_candidate -> entity_evidence`
  - `relation_candidate -> relation_evidence`
- distill source record、distilled_units.jsonl、engine handoff、distill bundle、source profile、provenance summary 均携带 `typed_unit` 或 `typed_unit_type_counts`。
- 保留旧 `kind` 字段，GraphRAG materializer 和 LLMWiki adapter 仍按旧兼容路径消费，避免一次性迁移风险。

## 出门验证

```bash
backend/.venv/bin/python -m py_compile backend/data_service/service.py backend/tests/test_data_service.py
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py -q
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

- Data Service 专项回归：`68 passed`
- Data Service/API/MCP 组合回归：`100 passed`

## 验收结论

PhaseD1 通过。当前实现已经把 typed unit contract 放进 distill 产物和 engine handoff，但没有强行改造下游引擎内部 schema，符合最小粒度和兼容迁移原则。

## 下一阶段

PhaseD2 建议继续做 typed unit consumer hardening：

- 为 `read_distill_bundle` 增加 typed unit type filter。
- 在 boundary audit 中显式报告 typed unit contract。
- 让 GraphRAG staging / query diagnostics 展示 typed unit 分布。
- 增加会议 turns 与代码分析 JSON fixture 的 typed unit 覆盖。
