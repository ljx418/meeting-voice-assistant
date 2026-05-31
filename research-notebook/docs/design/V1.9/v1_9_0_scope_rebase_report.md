# V1.9-0 Scope Rebase Report

日期：2026-05-30

## 当前基线

| 项 | 状态 |
| --- | --- |
| V1.8-RC Agent-led PRD Smoke | AGENT_CAPABILITY_SMOKE_READY |
| V1.8 普通用户 UX ready | NOT_READY |
| V1.8 人工内容质量终审 | NOT_READY |
| Research contract smoke | PASS_LIMITED_CONTRACT_SMOKE |
| Conflict labeling | CONTRACT_ONLY |

## V1.9 进入条件

- V1.8-RC report 存在。
- `npm run check` 可通过。
- V1.9 不把 Agent-led smoke 扩大为普通用户 UX ready。

## 风险评估

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 只推进 Research / conflict / acceptance package |
| 虚假验收 | MEDIUM-HIGH | 自动 smoke 不替代人工质量判断 |
| Research 变成通用问答 | HIGH 候选 | smoke 覆盖无来源拒答和资料外拒答 |

## 决策

V1.9 可以进入 V1.9-A Research Quality smoke。
