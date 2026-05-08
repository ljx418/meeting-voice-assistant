# harnessOS V3.0 Design Docs

文档状态：V3.0 design entrypoint。

## Source of Truth

Codex 实现 V3.0 时必须以 `v3_development_plan_multi_app_core.md` 为准。其他文档只能辅助理解，不得覆盖 ACTIVE PLAN 的阶段顺序和验收边界。

## Documents

| 文件 | 状态 | 用途 |
| --- | --- | --- |
| `v3_development_plan_multi_app_core.md` | ACTIVE PLAN | 当前 V3.0-PhaseA 到 V3.0-PhaseE 的实现 source of truth。 |
| `v3_phasea_multi_app_core_readiness.md` | FROZEN PHASEA BASELINE | V3.0-PhaseA 详细实施文件；2026-05-06 完成验收后转为冻结基线。 |
| `v3_phasea_multi_app_core_readiness_acceptance.md` | FROZEN PHASEA ACCEPTANCE | V3.0-PhaseA 辅助验收基线与证据记录模板；后续只做证据追加和缺陷修正说明。 |
| `v3_phaseb_pack_connector_registry.md` | ACTIVE PHASEB IMPLEMENTATION | V3.0-PhaseB 详细实施文件；用于展开 PackAssemblyResult、ConnectorRegistry 与 Connector Security Model 的实施边界。 |
| `v3_current_gap_analysis.md` | CODE FACTS / GAP AUDIT | 当前代码事实、缺口和阻塞项审计。 |
| `v3_evolution_direction.md` | V3.x+ FUTURE BLUEPRINT | 低代码、Memory、Feedback、Workflow Library 等远期方向。 |
| `v3_old_vs_new_plan_comparison.md` | DECISION RECORD | 旧 V3.0 蓝图与当前 active plan 的取舍记录。 |
| `../architecture/video-flow-plane-call-relations_v3.md` | ARCHITECTURE EXPLANATION | Video Flow 在六大平面上的调用关系、职责分层和 V4 目标支撑分析。 |

## Active Route

- V3.0-PhaseA Multi-App Core Readiness
- V3.0-PhaseB Pack Assembly + Connector Registry
- V3.0-PhaseC Job / Artifact / Governance Hardening
- V3.0-PhaseD Meeting Reference Pack Validation
- V3.0-PhaseE Knowledge Reference Pack Validation

## Numbering Rule

- 架构平面统一使用 `Plane-1` 到 `Plane-6`。
- 当前开发阶段统一使用 `V3.0-PhaseA` 到 `V3.0-PhaseE`。
- 当前阶段切片统一使用 `V3.0-PhaseX-Xn`，例如 `V3.0-PhaseB-B2`。
- 验收项统一使用 `V3.0-PhaseX-ACnn`，例如 `V3.0-PhaseC-AC04`。
- `P0/P1/P2` 只表示阻塞级别或优先级，不表示架构平面。

## Implementation Rule

如果 future blueprint 与 ACTIVE PLAN 存在冲突，按 ACTIVE PLAN 执行。低代码工作流、Core Memory、Feedback Optimization Loop、Workflow Library、Interview、Investment、Video Studio 均不进入当前 V3.0-PhaseA 到 V3.0-PhaseE 验收范围。

补充规则：

- 当前 V3.0 的主交付物是 Multi-App Core、Pack Assembly、Connector Registry、Governed Runtime Adapter，而不是把 Meeting / Knowledge 做成平台内置业务。
- Meeting / Knowledge 在 V3.0 中是 reference packs / validation samples，用于验证平台抽象是否足够通用。
- 新增业务若仍需要修改 Core 或 Gateway 业务逻辑，视为 V3.0 平台边界未达标，而不是“正常扩展方式”。

## Phase Freeze Rule

- 已完成并重新验收通过的阶段，必须从“活动实施文件”转为“冻结基线”。
- 冻结阶段后续只允许三类变更：
  - 缺陷修复
  - 验收证据追加
  - 与实际实现一致的文档校正
- 若后续需求想改变已完成阶段的合同、DoD、验收边界，必须在后续 Phase 或新的切片中显式承接，不能直接覆写已完成阶段定义。
