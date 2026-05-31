# V1.8-0 Scope Rebase / Weak Frontend Acceptance Debt

日期：2026-05-30

## 结论

V1.7 人工 UX 验收按产品策略跳过，状态为 `SKIPPED_BY_STRATEGY`。V1.8 直接进入 Agent-led capability validation。

## 范围变化

| 项 | 原计划 | 新计划 |
| --- | --- | --- |
| V1.7 出门 | 人工 UX 验收后 final sync | 人工 UX 验收跳过，记录 accepted debt |
| 前端定位 | PRD MVP 可操作体验 | weak frontend shell |
| 能力验证主体 | 浏览器人工路径 | Agent / workflow / backend contract |
| 验收重点 | 用户体验质量 | Agent 编排能力和真实数据结果 |

## 接受债务

- 普通用户 UX 不声明 ready。
- 前端可读性只保持最低可用。
- UI polish 延后。
- 交互深度由 Agent workflow 承担。

## 停止规则

如果后续阶段试图把 Agent smoke 写成人工 UX ready，必须停止。

## 风险评估

- UX 体验风险：HIGH accepted。
- 规格漂移风险：MEDIUM。
- 虚假验收风险：MEDIUM。

