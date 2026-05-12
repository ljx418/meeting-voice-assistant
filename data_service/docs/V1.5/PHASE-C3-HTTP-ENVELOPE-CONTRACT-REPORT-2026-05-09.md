# PhaseC3 HTTP Envelope Contract Convergence Report

日期：2026-05-09

## 目标

将 HTTP lifecycle API 的 envelope / blocked 响应收敛到 MCP 已固化的外部契约，避免 MCP 与 HTTP 在 path 暴露、artifact 引用和错误模型上继续分叉。

## 本阶段完成

- `backend/app/api/v1/data_service.py` 的 `_envelope` 复用 `data_service.mcp_common.envelope`。
- `backend/app/api/v1/data_service.py` 的 `_blocked` 复用 `data_service.mcp_common.blocked`。
- `backend/data_service/mcp_common.py` 扩展 path-like key：`bound_paths`、`roots`、`files` 进入 `debug_paths`，公共层仅保留稳定 ID、状态、摘要和 opaque artifact ref。
- `backend/tests/test_data_service_api.py` 增加 API contract 断言：workspace lifecycle、source lifecycle、directory scan、build lifecycle 响应公共层不出现内部 path key。
- API unknown operation blocked 响应稳定携带 `data.error.code == "unknown_operation_id"`。

## 出门验证

```bash
backend/.venv/bin/python -m py_compile backend/app/api/v1/data_service.py backend/data_service/mcp_common.py backend/tests/test_data_service_api.py
backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py -q
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

- API 专项回归：`10 passed`
- Data Service/API/MCP 组合回归：`100 passed`

## 验收结论

PhaseC3 通过。HTTP lifecycle envelope 已与 MCP external payload hardening / error code contract 共享同一实现，符合 MCP-first、最小公开契约和内部 workspace layout 不作为稳定 API 的方向。

## 下一阶段

进入 PhaseD Typed Distill Units v1.2：

- 新增 typed semantic unit mapping。
- 保持旧 `DistilledUnitKind` 兼容。
- 覆盖 decision / task / risk / requirement / fact / evidence / entity_evidence / relation_evidence / meeting_summary / architecture_note。
- 验收要求：会议 turns 与代码分析 JSON fixture 均产出 typed units；Wiki / Graph / Retrieval / Quality 可消费新旧 schema。
