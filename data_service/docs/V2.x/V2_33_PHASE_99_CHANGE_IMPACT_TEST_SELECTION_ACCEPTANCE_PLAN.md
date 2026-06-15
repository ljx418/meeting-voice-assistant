# V2.33 Phase 99 验收计划：Change Impact & Test Selection

阶段：V2.33 / Phase 99
目标：验证影响分析和测试选择能为 Coding Agent 提供可行动但不夸大的开发准备。

## 1. 自动化验收

新增测试：

```text
backend/tests/test_v2_33_change_impact_test_selection.py
```

必须覆盖：

- task -> impact build/read。
- test selection build/read。
- HTTP/MCP/CLI smoke。
- artifact disk inspection。
- suggested tests reason/evidence/needs_review。
- no absolute path leak。
- no runtime call claim。

## 2. data_service 真实任务

使用 Phase 97 的 5 个真实任务：

1. 新增 MCP tool 并同步 HTTP/CLI。
2. 修改 codebase snapshot。
3. 新增 architecture report 字段。
4. 修改 provider adapter。
5. 调整 quality governance。

每个任务必须：

- 返回 impact_id。
- impacted files/symbols/surfaces/docs/tests 至少一类非空，或 structured blocker。
- suggested_tests 非空，或 structured blocker。
- 每个 suggested test 有 reason 和 evidence_refs 或 needs_review。

## 3. HarnessOS 真实任务

使用 Phase 97 的 3 个 HarnessOS 任务：

1. 修改 workflow dispatch。
2. 新增 station/agent descriptor。
3. 审查 mission TUI entrypoint。

允许 blocker，但必须说明缺失证据类型，例如：

- `TEST_EVIDENCE_UNAVAILABLE`
- `DYNAMIC_IMPACT_UNRESOLVED`
- `RELATIONSHIP_EVIDENCE_UNAVAILABLE`

## 4. False-Green Rejection

以下情况不得通过：

- 无 impact artifact。
- suggested_tests 缺 reason。
- suggested_tests 缺 evidence 且未标 needs_review。
- import/static relation 被写成 runtime impact。
- HarnessOS 找不到测试却标 accepted。
- public payload 泄露绝对路径、secret、traceback。

## 5. 出门条件

- Focused tests 通过。
- data_service 真实任务验收通过。
- HarnessOS 真实任务 accepted 或 blocker。
- PRD/spec review 无 fatal/major。
- acceptance audit report 落盘。
