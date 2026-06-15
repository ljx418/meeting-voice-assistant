# V2.23 Phase 89 Governance Feedback Loop Acceptance Plan

## 1. 验收结论规则

Phase 89 只有在以下条件全部满足时才能 accepted：

- feedback -> rule -> approve -> overlay 可完整跑通。
- revoke 后 overlay 不再应用该 rule。
- missing target feedback 被拒绝。
- source artifact hash before/after 不变。
- HTTP/MCP/CLI stable fields 一致。
- 真实 `data_service` repo E2E 通过。
- full regression 通过。

## 2. Focused Tests

必须新增并通过：

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_23_platform_governance.py -q
```

测试点：

1. 对真实 platform panel 记录 feedback。
2. build rules 生成 draft rule。
3. approve 后 overlay report 出现 `applied_rules`。
4. revoke 后 overlay report 不再应用该 rule。
5. 原始 console artifact hash 不变。
6. 不存在 target 被拒绝。

## 3. 三端契约验收

HTTP/MCP/CLI 必须一致：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `feedback_count`
- `rule_count`
- `approved_rule_count`
- `applied_rule_count`
- `artifact_refs` count
- warnings/unresolved count

## 4. 真实仓库 E2E

真实输入：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

E2E 流程：

1. 导入当前 repo。
2. build console。
3. record feedback for `platform_panel:overview`。
4. build rules。
5. approve rule。
6. read overlay。
7. revoke rule。
8. read overlay again。
9. verify source artifact hash unchanged。
10. redaction scan。

## 5. 回归验收

必须执行：

```bash
npm run build
PYTHONPATH=backend python3 -m pytest backend/tests -q
git diff --check -- .
```

## 6. False-Green Rejection

以下情况必须判定失败：

- feedback target 不存在但被接受。
- approve 后 overlay 没有 applied rule。
- revoke 后 overlay 仍应用 rule。
- 任何源 artifact 被治理流程改写。
- skipped test 被写成 passed。
- mock-only 数据替代真实 repo E2E。
