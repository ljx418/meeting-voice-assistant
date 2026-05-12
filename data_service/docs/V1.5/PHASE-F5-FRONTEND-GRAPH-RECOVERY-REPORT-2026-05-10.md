# PhaseF5 Frontend Graph Recovery Report

日期：2026-05-10

## 目标

修复控制台中“社区图不可见 / 难以找到”的前端问题，并改善 `/knowledge` 的 Explore 工作台可读性。

## 已完成

- Header 的 `GraphRAG` 按钮改为显式打开 Explore 工作台并定位到 `graph-panel`。
- Explore 工作台调整为 GraphRAG 社区图优先，社区图从查询面板之后移到首屏主体。
- GraphRAG 区块新增刷新按钮、加载状态、空态说明和社区图状态文本。
- `loadGraph` 增加错误 toast，避免加载失败时静默。
- 社区图画布高度和背景视觉优化，提升桌面与移动视口的可读性。
- 保持 PhaseF4 的 MCP Debugger 本地预检能力不变。

## 出门验证

```bash
npm run build
```

结果：通过；生成：

- `backend/app/static/knowledge_console/index.html`
- `backend/app/static/knowledge_console/assets/index-C2kZploL.css`
- `backend/app/static/knowledge_console/assets/index-CuxdupBh.js`

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
- 本阶段只调整前端工作台交互、布局和社区图可读性。

## 下一步

进入前端验收阶段，使用桌面和移动视口截图检查社区图入口、首屏可见性、空态和基础响应式布局。
