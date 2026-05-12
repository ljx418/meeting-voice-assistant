# PhaseF7 前端社区图可见性修复报告

日期：2026-05-10

## 背景

用户反馈 `/knowledge` 仍显示“GraphRAG 社区 暂无匹配社区”，并且社区图不可见。排查结果确认后端 `/graph` 已返回真实图谱数据，当前默认 workspace 有 147 nodes、366 edges、49 communities；问题集中在前端工作台切换和图谱可见性。

## 根因

`?view=graph` 或 GraphRAG 入口已经能进入 Explore，但页面初始化的 `loadDistill()` 会自动调用 source 选择链路。该链路会把 `activeWorkbench` 切换到 Sources，导致 Explore 的社区图在完成加载后被隐藏。用户看到的是 Source Trace 的 source 级社区空态，而不是主 GraphRAG 社区图。

## 修复内容

1. `frontend/src/pages/KnowledgePage.vue`
   - `?view=graph` 和 `#graph-panel` 直接以 Explore 作为初始工作台。
   - GraphRAG 入口显式调用 `openGraphPanel()`，进入 Explore 并主动补拉图谱。
   - `loadDistill()` 初始化时只设置默认 `selectedDistillSourceId`，不再自动触发 `selectDistillSource()`，避免初始化阶段隐式切换到 Sources。
   - `refreshAll()` 改为 `Promise.allSettled()`，避免某个治理数据请求失败影响图谱加载。
   - `activeWorkbench` 切到 Explore 时，如果图谱为空会自动补拉 `/graph`。

2. `frontend/src/components/GraphCommunityView.vue`
   - 新增 `communities` prop 和 `select-community` 事件。
   - 在图谱画布内增加社区概览层，直接展示前 8 个社区的标题、实体数和关系数。
   - 该层作为可见性兜底：即使 D3 布局尚未稳定，用户也能在 GraphRAG 面板内看到社区存在，并可点击选中社区。

## 出门验证

- `npm run build`：通过，生成最新静态控制台产物。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：23 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：104 passed。
- Playwright 截图验收：`docs/V1.5/frontend-acceptance/data_service_phasef7_graph_visible_fixed.png`。
  - 页面保持在 Explore / GraphRAG Communities。
  - 图谱画布可见节点和连线。
  - 社区概览层可见。
  - 统计显示 147 nodes、366 edges、49 communities。

## 对外能力检查

本阶段未新增 MCP tool、HTTP route 或 CLI 参数。修复只涉及前端状态流、图谱加载兜底和可视化层，不改变外部契约。

## 当前结论

社区图不可见问题已修复。后续继续 PhaseF/G 时，应把图谱入口、`?view=graph`、Source Trace fallback 和前端截图验收作为固定回归项。
