# PhaseF4 Console MCP Debugger Precheck Report

日期：2026-05-10

## 目标

继续 PhaseF 控制台产品化，在不新增后端公共入口的前提下，把 MCP Debugger 从 contract 可视化推进到本地 payload 预检和 envelope 预览。

## 已完成

- `/knowledge` 的 MCP 工作台新增 `Local Debugger / Payload 预检` 面板。
- 支持按 MCP tool 选择调试目标，并自动生成示例 payload。
- 支持一键生成完整样例或只保留 required fields。
- 支持本地 JSON object 校验和 required field 缺失检查。
- 支持根据 selected tool 预览 MCP 调用 envelope：
  - selected tool name
  - arguments
  - expected response shape
  - local validation status
- 保持 PhaseF3 的 tool/resource contract 快照与后端 registry 一致性测试。
- 重新构建静态控制台产物。

## 出门验证

```bash
npm run build
```

结果：通过；生成：

- `backend/app/static/knowledge_console/index.html`
- `backend/app/static/knowledge_console/assets/index-CsHv13cx.css`
- `backend/app/static/knowledge_console/assets/index-EUeOMPEv.js`

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
- MCP Debugger 当前仅做前端本地 payload 预检和 envelope 预览，不执行真实 MCP call。
- 控制台 contract 快照仍由自动化测试约束，避免偏离后端 MCP registry。

## 下一步

进入 PhaseF5：继续 MCP Debugger，优先补齐本地响应样例、error envelope 场景预览和从 contract 视图跳转到调试视图的细节 polish。
