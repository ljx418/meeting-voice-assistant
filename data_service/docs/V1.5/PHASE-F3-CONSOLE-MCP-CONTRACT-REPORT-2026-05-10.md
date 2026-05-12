# PhaseF3 Console MCP Contract Report

日期：2026-05-10

## 目标

继续 PhaseF 控制台产品化，准备 MCP Debugger 入口，并把 tool / resource contract 在控制台中可视化，作为后续调试入口的稳定基线。

## 已完成

- `/knowledge` 新增 `MCP` 工作台页签。
- 新增 `frontend/src/data/mcpContract.ts`，固化当前 MCP tool / resource contract 快照。
- MCP 工作台展示：
  - 38 个 MCP tools 的分组、required fields、optional fields 和 stable / compat 状态。
  - 2 个 canonical resources 与 2 个 legacy resource URI 兼容入口。
  - 7 个 V2 envelope alias 到 legacy tool 的映射。
  - contract guard 快照，用于快速核对控制台展示的工具数量、资源数量和兼容面。
- 新增测试 `test_console_mcp_contract_snapshot_matches_registry`，确保控制台 MCP contract 快照与后端 `all_tool_specs()` / `RESOURCE_SPECS` 保持一致。
- 重新构建静态控制台产物。

## 出门验证

```bash
npm run build
```

结果：通过；生成：

- `backend/app/static/knowledge_console/index.html`
- `backend/app/static/knowledge_console/assets/index-COksoOpy.css`
- `backend/app/static/knowledge_console/assets/index-D-NVR5um.js`

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：`23 passed`。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：`104 passed`。仍有既有 `datetime.utcnow()` deprecation warnings，未在本阶段扩大处理范围。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI 参数。
- 本阶段只新增前端静态 contract 可视化与测试保护。
- 控制台快照与后端 MCP registry 一致性由自动化测试约束。

## 下一步

进入 PhaseF4：在不扩展公共后端契约的前提下，继续把 MCP Debugger 做成可执行调试面板，优先支持本地 schema 检查、示例 payload 生成和响应 envelope 预览。
