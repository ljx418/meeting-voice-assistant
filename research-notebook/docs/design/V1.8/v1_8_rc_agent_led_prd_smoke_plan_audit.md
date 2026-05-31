# V1.8-RC Agent-Led PRD Smoke Plan Audit

日期：2026-05-30

## 审计结论

`CONDITIONAL GO`

V1.8-RC 可以进入执行，但 RC 只能聚合和校验 V1.8-B/C/D/E 已完成的真实 data_service / provider smoke 证据，不得声明普通用户 UX ready。

## 前置验收

| 前置项 | 状态 |
| --- | --- |
| V1.8-B Agent Source Import | PASS_LIMITED |
| V1.8-C Agent Guide / QA / Citation | PASS_LIMITED |
| V1.8-D Agent Studio | PASS_LIMITED |
| V1.8-E Weak Frontend Shell | PASS_LIMITED |
| `npm run check` | PASS |

## RC 实现策略

1. 新增 `scripts/v1_8_rc_agent_prd_smoke.mjs`。
2. 校验 V1.8-B/C/D result fixtures 均为 `PASS_LIMITED`。
3. 校验 V1.8-E HTML 展示壳存在且脱敏。
4. 校验 raw_fixture_refs 存在。
5. 校验声明边界保留。
6. 生成 RC 聚合 fixture 和 RC report。

## 风险评估

| 风险 | 等级 | 是否阻塞 | 收敛措施 |
| --- | --- | --- | --- |
| 规格漂移 | MEDIUM | 否 | 完成声明限定为 Agent-led PRD MVP capability validation |
| 虚假验收 | MEDIUM-HIGH | 否 | RC 聚合不替代人工 UX / 内容质量验收 |
| provider 波动 | MEDIUM | 否 | B/C/D reports 已记录受限 smoke 与波动 |
| UX 债务 | HIGH accepted | 不阻塞 V1.8 | 保留 V1.x Final Human UX Acceptance |

## 审计意见

可以实现 `npm run smoke:v1.8-agent-prd`。

完成后必须执行：

```bash
npm run check
npm run smoke:v1.8-agent-prd
npm run smoke:v1.8-weak-frontend
```

如果全部通过，V1.8-RC 最多声明 Agent-led capability smoke-ready，不得声明普通用户 UX ready。
