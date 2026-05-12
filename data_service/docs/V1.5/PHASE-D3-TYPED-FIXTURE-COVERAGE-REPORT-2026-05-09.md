# PhaseD3 Typed Fixture Coverage Report

日期：2026-05-09

## 目标

补齐 typed distill units 在上层适配输入上的端到端覆盖，验证会议 turns 与代码分析 JSON 都能进入 typed unit contract，同时保持旧 `kind` 兼容路径。

## 本阶段完成

- 新增会议 turns fixture 覆盖：
  - `meeting_summary`
  - `risk`
  - `claim`
  - `entity_evidence`
- 新增代码分析 JSON fixture 覆盖：
  - `architecture_note`
  - `code_symbol`
  - `code_dependency`
  - `code_call_edge`
- 代码结构化输入会生成兼容旧 kind 的 unit：
  - `architecture_note` 使用旧 `note`
  - `code_symbol` 使用旧 `entity_candidate`
  - `code_dependency` / `code_call_edge` 使用旧 `relation_candidate`
- `typed_unit.provenance.typed_unit_type` override 只作用于 typed contract，不破坏旧 GraphRAG / LLMWiki 消费路径。
- `distill/schema.json` 的 `typed_unit_types` 已包含代码 typed 类型。

## 出门验证

```bash
backend/.venv/bin/python -m py_compile backend/data_service/service.py backend/tests/test_data_service.py
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py::test_data_service_typed_units_cover_meeting_turns_fixture backend/tests/test_data_service.py::test_data_service_typed_units_cover_code_analysis_fixture -q
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py -q
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

- 新增 fixture：`2 passed`
- Data Service 专项回归：`70 passed`
- Data Service/API/MCP 组合回归：`102 passed`

## 验收结论

PhaseD3 通过。typed unit contract 已覆盖会议 turns 和代码分析 JSON 两类上层适配输入，并通过旧 kind 保持现有引擎兼容。

## 下一阶段

PhaseE 建议进入格式扩展：

- docx extractor
- yaml/yml structured parser
- source import / scan / distill / LLMWiki / GraphRAG 端到端验收
