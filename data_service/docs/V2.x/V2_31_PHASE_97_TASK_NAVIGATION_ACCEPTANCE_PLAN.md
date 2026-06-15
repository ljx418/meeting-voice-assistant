# V2.31 Phase 97 验收计划：Task-Aware Navigation Index

阶段：V2.31 / Phase 97
目标：验证 task-aware navigation index 是否能用真实仓库生成可读、可追踪、可被 Agent 消费的任务导航候选。

## 1. 必须通过的自动化验收

- Focused tests：task taxonomy、index build、query build、artifact readback。
- HTTP/MCP/CLI smoke：至少覆盖 build/read/query。
- Artifact inspection：`navigation_index.json` 和 `task_queries/{task_id}.json` 存在并可读。
- Redaction：public payload 无绝对路径、secret、traceback。
- PRD/spec review：不得提前实现 Phase 98+。

## 2. data_service 真实任务

必须至少验收 5 个任务：

1. 新增 MCP tool 并同步 HTTP/CLI。
2. 修改 codebase snapshot。
3. 新增 architecture report 字段。
4. 修改 provider adapter。
5. 调整 quality governance。

每个任务必须满足：

- 返回 task_id。
- 返回 task_type。
- matched candidates 非空。
- 每个 candidate 有 evidence 或 needs_review。
- artifact_refs 非空。

## 3. HarnessOS 真实任务

必须至少验收 3 个任务：

1. 修改 workflow dispatch。
2. 新增 station/agent descriptor。
3. 审查 mission TUI entrypoint。

允许输出 structured blocker，但不允许 mock-only 或伪造 accepted relation。

## 4. False-Green Rejection

以下情况不得通过：

- candidate 只有 token overlap，没有 needs_review。
- public payload 泄露本机绝对路径。
- 缺失 surfaces/symbols 时静默返回空成功。
- HarnessOS 路径缺失但仍标 accepted。
- Phase 97 输出 relationship graph 或 impact analysis，造成阶段越界。

## 5. 出门条件

- Focused tests 通过。
- data_service 真实任务通过。
- HarnessOS 任务返回 accepted candidates 或 blocker。
- 无 fatal/major PRD 偏差。
- Acceptance audit 落盘。
