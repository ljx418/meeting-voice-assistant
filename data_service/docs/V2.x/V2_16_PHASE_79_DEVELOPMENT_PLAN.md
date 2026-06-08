# V2.16 Phase 79 开发计划：Workbench v2 View Model

## 1. 阶段定位

Phase 79 在 V2.15 workbench 基础上生成更适合人类审查的 Workbench v2。它整合 provider matrix、semantic facts、runtime profiles、risk lanes 和 blocker board。

## 2. In Scope

- 生成 `workbench_v2/review_workbench_v2.json`。
- 生成 HTML 和 Mermaid 视图。
- 展示 provider matrix、semantic coverage、runtime profile readiness、risk lanes、blockers。
- HTML/Mermaid 只能从 persisted payload 渲染。
- HTTP / MCP / CLI build/read/view。

## 3. Out of Scope

- 前端编辑器。
- 新事实抽取。
- 隐藏 blocker。
- 生成 payload 中不存在的新节点。

## 4. 出门条件

- payload、HTML、Mermaid 均落盘。
- HTML 不含 `<script>`。
- Mermaid node id 来自 payload。
- blocker / needs_review 可见。
- HTTP / MCP / CLI parity 通过。
