# GraphRAG 图谱质量面板阶段报告

日期：2026-05-06

## 结论

`Phase 5.1：GraphRAG 图谱质量面板` 第一版已完成。

当前实现已经把图谱质量问题从“人工看图判断”升级为“后端生成诊断对象，前端可直接审核并带入质量反馈”。下一阶段不再继续扩入口，而是围绕真实知识库做低信号 source 回归抽查，并继续把 GraphRAG quality plan 适配下沉到 `app.graphrag.service` owner 边界。

## 已实现内容

- `backend/data_service/service.py`
  - `get_graph_snapshot()` 会返回 `quality_diagnostics`
  - `quality_diagnostics.schema_version` 为 `1.0`
  - 诊断类型覆盖：
    - `top_communities`
    - `weak_communities`
    - `isolated_nodes`
    - `low_value_nodes`
  - 每个诊断项包含 `id / title / name / reason / severity / target_type / metrics / feedback_target`
  - `feedback_target` 可直接转换为质量反馈对象

- `frontend/src/api/dataService.ts`
  - `KnowledgeGraphResponse` 新增可选字段 `quality_diagnostics`

- `frontend/src/pages/KnowledgePage.vue`
  - GraphRAG 区域新增 diagnostics 面板
  - 展示 Top Communities、Weak Communities、Isolated Nodes、Low Value Nodes
  - 点击诊断项可定位图节点或社区
  - 快捷动作可带入：
    - `needs_review`
    - `mark_noise`
    - `merge_suggest`
    - `rename_suggest`

## 验收结果

- 图谱诊断定向测试：`3 passed`
- Data Service/API 回归：`75 passed`
- 前端构建：`npm run build` 通过

本次未重新跑 MCP 全量回归；Phase 4 MCP 真实链路仍作为历史回归基线保留。

## 当前限制

- 诊断排序和阈值目前是第一版启发式规则，需要用真实知识库继续校准。
- `quality_diagnostics` 当前由 Data Service 在 graph snapshot 读时附加；后续应继续把 graph quality plan 的适配边界下沉到 `app.graphrag.service`。
- 本地截图验收时如果 API key 缺失，前端只能看到空数据状态，无法完整判断真实图谱质量面板效果。

## 下一阶段

1. `Phase 5.2` Workspace & Source Manager
- 补工作区创建/选择、目录绑定、导入式 source 和 source 台账
- 前端展示 source 收录状态、失败原因和低信号标记
- HTTP API 对齐 MCP lifecycle 的 workspace/source 能力

2. `Phase 5.3` Refresh Operation UI
- 接入异步 build queue
- 展示首次刷新、增量刷新、阶段进度、取消、重试和失败诊断

3. `Phase 5.4` Source Distill Trace
- 按 source 展示原始文件、distill units、LLMWiki 页面和 GraphRAG 节点/社区的可追溯流水线

4. GraphRAG owner 边界下沉
- 把 Graph snapshot/query 的治理适配继续从 `data_service` 读时层收回 `app.graphrag.service`
- 保持 `data_service` 只做编排、contract staging、统一入口和 MCP/API 边界
