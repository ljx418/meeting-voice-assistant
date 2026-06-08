# V2.16 Phase 80 验收计划：Large-Project Abstraction Advisor

## 1. 验收目标

验证大型项目抽象 advisor 可以泛化解释项目结构和 blocker，而不是只对单个项目写规则。

## 2. 必测断言

- `abstraction_advisor.json` 存在。
- `pattern_adapters.json` 存在。
- `blockers.jsonl` 存在。
- `generic_adapter_count > 0`。
- accepted pattern 有 `evidence_refs`。
- blocker 有 `reason`、`missing_evidence`、`next_actions`。
- artifact 中不得包含 `harnessos-only`、`project_specific_override` 等硬编码信号。

## 3. 真实数据验收

- 当前 data_service 仓库必须通过。
- HarnessOS 或替代大项目若环境可读，则执行 advisor；若不可读，必须记录 structured environment blocker，不能伪造通过。

## 4. 打回条件

- document claim 被伪装成 code fact。
- weak hint 被标 accepted。
- 为单一项目硬编码 pattern。
