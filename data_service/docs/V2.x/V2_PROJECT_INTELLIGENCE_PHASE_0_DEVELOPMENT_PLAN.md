# V2 Phase 0 Development Plan: Preparation and Audit Closure

## Summary

Phase 0 不开发业务代码。目标是把 V2 后续开发的输入、边界、门禁和真实数据验收标准固定下来，确认是否可以进入 PR1：Codebase Registry + Artifact Foundation。

## Inputs

- `docs/V2.x/V2_PROJECT_BASELINE.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PRD.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_DEVELOPMENT_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_REMAINING_GOVERNANCE_PLAN.md`
- 当前 `data_service` repo 作为真实数据验收样例。

## Work Items

1. 检查当前工作区状态，识别与 V2 无关的既有变更。
2. 检查现有 HTTP router 注册点、MCP tool registry、CLI parser 入口。
3. 确认 PR1 只新增 V2 code assets 模块和最小注册点，不修改 V1 source registry。
4. 明确 PR1 的真实数据验收命令和风险门禁。
5. 产出 Phase 0 验收计划和审计报告。

## Architecture Boundaries

PR1 允许新增：

- `backend/data_service/code_assets/`
- `backend/data_service/mcp_code_tools.py`
- `backend/app/api/v1/code_assets.py`
- `backend/tests/test_v2_codebase_registry*.py`

PR1 只允许最小修改：

- `backend/app/api/__init__.py`
- `backend/data_service/mcp_tool_registry.py`
- `backend/data_service/mcp_dispatcher.py`
- `backend/data_service/__main__.py`

PR1 禁止：

- 将 codebase asset 写入 source registry。
- 扩大 `backend/app/api/v1/data_service.py`。
- 扩大 `backend/data_service/service.py`。
- 变更 V1 workspace/source/build/query/quality 语义。

## Exit Criteria

- Phase 0 审计报告没有未闭环 `fatal` / `major`。
- PR1 的接口、文件范围、真实数据验收方式已明确。
- 当前工作区风险已被隔离或明确阻塞。

