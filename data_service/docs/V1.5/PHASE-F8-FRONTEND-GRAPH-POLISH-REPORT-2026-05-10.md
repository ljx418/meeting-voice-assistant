# PhaseF8 前端 GraphRAG 页面可读性优化报告

日期：2026-05-10

## 背景

PhaseF7 已修复社区图不可见问题。随后使用 `web-design-engineer` 与 `impeccable /audit` 对 `/knowledge/?view=graph` 做前端检视，发现主要问题集中在图谱区域视觉遮挡、移动端画布空间、右侧信息优先级和 toast 遮挡。

## 优化内容

1. `frontend/src/components/GraphCommunityView.vue`
   - 将社区 chips 从图谱画布内浮层移到画布上方的社区条，避免遮挡节点和边。
   - 将图谱画布独立为 `graph-canvas-wrap`，工具栏、SVG、错误态和空态只作用于画布区域。
   - 移动端降低图谱高度区间，隐藏画布内操作提示条，减少视觉遮挡。

2. `frontend/src/pages/KnowledgePage.vue`
   - GraphRAG 右侧信息顺序调整为：选中社区/节点详情 -> 社区队列 -> 图谱质量诊断。
   - 图谱质量诊断改为折叠面板，默认不与主图和社区详情竞争注意力。
   - 新增 `graphDiagnosticCount`，折叠标题展示诊断总数。
   - 成功 toast 自动消失时间缩短到 1.6 秒，错误 toast 保持较长可读时间。
   - 移动端 toast 改为顶部窄条，并通过更短成功态时长避免遮挡主要内容。

## 出门验证

- `npm run build`：通过，生成最新静态控制台产物。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：23 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：104 passed。
- Playwright 桌面截图：`docs/V1.5/frontend-acceptance/data_service_phasef8_graph_polish_desktop_v2.png`。
- Playwright 移动截图：`docs/V1.5/frontend-acceptance/data_service_phasef8_graph_polish_mobile_v2.png`。
- 对外入口扫描：未发现新增 MCP tool、HTTP route 或 CLI 参数。

## 对外能力检查

本阶段只修改前端布局、视觉层级、toast 行为和静态构建产物。未新增 MCP tool、HTTP route 或 CLI 参数，未改变既有 `/graph`、`/source/trace` 或 MCP contract。

## 当前结论

GraphRAG 页面已从“图可见但控件遮挡”推进到“图谱优先、社区详情优先、治理诊断折叠”的服务治理控制台形态。后续前端优化可继续收敛全局 header 操作密度与暗色 surface token。
