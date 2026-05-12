# PhaseF9 前端规则网格重生成报告

日期：2026-05-10

## 背景

用户反馈当前前端页面“板块大小不一，很丑”，要求继续使用前端设计 skill 重新生成一版。基于 `web-design-engineer` 与 `impeccable /layout` 的检查，本阶段从局部修补转为重排 Explore 工作台骨架。

## 设计决策

- 单一工作台宽度：页面 header 与主内容统一收敛到 1480px。
- 规则网格：Explore 工作台使用 12 列 grid，不再依赖 flex 自然换行。
- 主次关系：GraphRAG 主图占满第一行；Query 与 Summary 等高并排；Wiki Pages 单独占满下一行。
- 视觉层级：GraphRAG 侧栏使用同一 surface、同一 border、同一 8px radius，避免块状随机感。
- 移动端：保持单列堆叠，避免桌面网格强行压缩。

## 修改内容

1. `frontend/src/pages/KnowledgePage.vue`
   - 新增 regenerated workbench layout CSS。
   - `page-header` 与 `page-stack` 统一最大宽度到 1480px。
   - `page-stack--explore` 改为 12 列规则网格。
   - GraphRAG 主卡片固定为首行大工作区。
   - Query 与 LLMWiki Summary 设为等高并排板块。
   - LLMWiki Pages 独占一行，避免与主图竞争。
   - GraphRAG 右侧 detail、queue、diagnostics 使用统一 surface 和边框。

## 出门验证

- `npm run build`：通过，生成最新静态控制台产物。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：23 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：104 passed。
- Playwright 桌面截图：`docs/V1.5/frontend-acceptance/data_service_phasef9_regenerated_desktop.png`。
- Playwright 移动截图：`docs/V1.5/frontend-acceptance/data_service_phasef9_regenerated_mobile.png`。
- 对外入口扫描：未发现新增 MCP tool、HTTP route 或 CLI 参数。

## 对外能力检查

本阶段仅修改前端布局 CSS 和静态构建产物。未新增 MCP tool、HTTP route 或 CLI 参数，未改变数据服务 contract。

## 当前结论

Explore 页面已从自然高度堆叠改为规则工作台网格。桌面端板块宽度和高度更稳定，移动端仍保持单列可读。后续如果继续提升视觉质量，应继续处理全局 header 信息密度和 surface token，而不是再堆叠更多卡片。
