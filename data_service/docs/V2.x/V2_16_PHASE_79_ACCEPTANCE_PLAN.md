# V2.16 Phase 79 验收计划：Workbench v2 View Model

## 1. 验收目标

验证 Workbench v2 能让用户不读 raw JSON 也能理解 provider、runtime、risk、blocker 和 evidence 状态。

## 2. 必测断言

- `review_workbench_v2.json` 存在。
- `review_workbench_v2.html` 存在。
- `review_workbench_v2.mmd` 存在。
- `sections` 包含：
  - provider_matrix
  - semantic_coverage
  - runtime_profiles
  - risk_lanes
  - blocker_board
- HTML 不含 raw script。
- Mermaid node id 全部来自 payload nodes。
- public payload 不泄露绝对路径。

## 3. 三端验收

HTTP / MCP / CLI 需比较：

- `schema_version`
- `workbench_id`
- `summary`
- section ids
- blocker count
- artifact refs

## 4. 打回条件

- HTML/Mermaid 生成 payload 中没有的新事实。
- blocker 被隐藏。
- 视图泄露绝对路径或 secret。
- 只生成 HTML 不落盘 JSON。
