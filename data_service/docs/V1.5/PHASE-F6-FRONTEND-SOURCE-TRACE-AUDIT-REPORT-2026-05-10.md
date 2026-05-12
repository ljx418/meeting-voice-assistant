# PhaseF6 Frontend Source Trace Audit Report

日期：2026-05-10

## 审计输入

用户反馈：当前仍显示 `GraphRAG 社区 暂无匹配社区`，并要求使用前端设计审计方法检查页面。

本阶段使用：

- `web-design-engineer`：审计工作台结构、GraphRAG 入口、Source Trace 的用户路径。
- `impeccable`：审计暗色控制台的可读性、空态文案、信息层级和响应式风险。

备注：当前环境没有名为 `awesome-design` 的 skill，已使用最接近的 `impeccable` 代替视觉审计。

## 发现

- `GraphRAG 社区 暂无匹配社区` 来自 Source Trace 的 source 级匹配社区列表，不是 Explore 主社区图。
- 当后端 source trace 没有返回直接匹配社区时，前端只显示空态，未展示全局 GraphRAG 社区候选，用户会误以为社区图不存在。
- 从 Source 台账直接进入追溯链路时，如果全局 graph state 尚未加载，前端没有主动补拉 `/graph`，导致可用 fallback 也为空。

## 已完成

- Source Trace 的 GraphRAG 社区列改为 `direct match + global fallback`：
  - 优先展示 source trace 返回的直接匹配社区。
  - 若直接匹配为空，则展示与匹配节点相关的全局社区。
  - 若仍为空，则展示当前全局 GraphRAG 社区候选。
- Source Trace 的空态文案从单一 `暂无匹配社区` 改为明确说明：
  - 未找到直接匹配社区。
  - 已展示相关全局社区或全局候选。
  - 若完全没有 GraphRAG 社区，则提示刷新图谱或重建知识库。
- Source Trace 的 GraphRAG 统计增加 `direct / visible communities`，避免用户把 source 级匹配数量误读为全局社区数量。
- 从 Source 进入追溯链路时，如果全局图谱尚未加载，会自动补拉一次既有 `/graph` 数据。

## 出门验证

```bash
npm run build
```

结果：通过；生成：

- `backend/app/static/knowledge_console/index.html`
- `backend/app/static/knowledge_console/assets/index-DxlODSiV.css`
- `backend/app/static/knowledge_console/assets/index-BxQRHB-3.js`

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：`23 passed`。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：`104 passed`。仍有既有 `datetime.utcnow()` deprecation warnings，未在本阶段扩大处理范围。

## 前端验收

```bash
/Users/Zhuanz/Library/Python/3.9/bin/playwright screenshot --viewport-size=1440,1100 'http://127.0.0.1:5175/knowledge/?scope=session&session_id=frontend_acceptance#graph-panel' /tmp/data_service_phasef6_graph_audit.png
```

截图已归档：

- `docs/V1.5/frontend-acceptance/data_service_phasef6_graph_audit.png`

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI 参数。
- 本阶段只复用既有 `/graph` 与 `/source/trace` 响应，修复前端 fallback、文案和加载路径。

## 下一步

继续 PhaseF7：在真实有数据 workspace 上做大图谱视觉验收，并继续 MCP Debugger 的 response / error envelope 预览。
