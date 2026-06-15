# V2.33 Phase 99 预实施审计：Change Impact & Test Selection

审计日期：2026-06-10
阶段：V2.33 / Phase 99
结论：**通过，可以进入 Phase 99 实现。**

## 1. 前置状态

Phase 97 accepted：

```text
docs/V2.x/V2_31_PHASE_97_TASK_NAVIGATION_ACCEPTANCE_AUDIT_REPORT.md
```

Phase 98 accepted：

```text
docs/V2.x/V2_32_PHASE_98_LIGHTWEIGHT_RELATIONSHIP_ACCEPTANCE_AUDIT_REPORT.md
```

## 2. PRD 对齐

Phase 99 对齐 V2.31-V2.36 PRD 的 Change Impact & Test Selection：

- 输入 task/file/symbol/capability。
- 输出影响范围、测试建议、风险和 blocker。
- 不做完整 runtime impact proof。

## 3. 架构边界

允许新增：

```text
backend/data_service/code_assets/coding_agent_navigation/impact_analysis.py
backend/data_service/code_assets/coding_agent_navigation/impact_persistence.py
```

禁止修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

禁止：

- 改写 Phase 97/98 artifacts。
- 把 import/static relation 写成 runtime impact。
- 用 token overlap 伪造 test selection evidence。

## 4. 风险审计

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| impact 被误读为 runtime guarantee | major | reason code 必须标 semantic limit |
| suggested_tests 无 evidence | major | 必须 needs_review 或 blocker |
| HarnessOS test 不可定位但伪通过 | major | 必须 structured blocker |
| major/fatal guardrail 被隐藏 | major | risk_items pinning |

## 5. 预实施结论

无 open fatal / major。可以进入 Phase 99 实现。
