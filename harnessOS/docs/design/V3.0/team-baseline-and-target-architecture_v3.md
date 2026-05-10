# Team Baseline and Target Architecture V3.0

文档状态：V3.0 CLOSEOUT TEAM BASELINE。V2 团队基线文档已归档到 `docs/history/v2-phase-docs/architecture/team-baseline-and-target-architecture_v2.md`。

## 1. 当前团队口径

- `docs/design/V3.0/v3_development_plan_multi_app_core.md` 是当前活动实施计划。
- `docs/design/V3.0/v3_evolution_direction.md` 仅作为 V3.x+ 远期蓝图。
- `docs/design/V3.0/v3_current_gap_analysis.md` 是代码事实和缺口审计。
- `docs/design/V3.0/v3_old_vs_new_plan_comparison.md` 是架构决策记录。

## 2. 当前工程顺序

1. V3.0-PhaseA Multi-App Core Readiness。
2. V3.0-PhaseB Pack Assembly + Connector Registry。
3. V3.0-PhaseC Job / Artifact / Governance Hardening。
4. V3.0-PhaseD Meeting Pack E2E Migration。
5. V3.0-PhaseE Knowledge Pack E2E Migration。

## 3. 团队协作规则

- 新 app 先写 AppProfile，再接 Pack/Connector。
- 新 connector 必须进 ConnectorRegistry，并声明 security descriptor。
- 新 workflow 必须来自 Pack manifest，不写 Gateway special case。
- 新 artifact kind 必须登记 schema、read policy 和 lineage。
- 新高风险 tool 必须声明 policy/approval 规则。

## 4. Deferred

低代码画布、Core Memory、Feedback Optimization、Workflow Library 暂不进入当前 V3.0 验收。相关讨论保留在远期蓝图，不作为当前开发任务。
