# harnessOS V3.0 Design Docs

文档状态：V3.0 final closeout archive and baseline.

本目录是 V3.0 阶段设计、状态、差距、验收和架构图的统一收纳位置。V3.0 已进入 closeout 状态；后续只允许缺陷修复、验收证据追加和与实际实现一致的文档校正。V3.5 阶段计划在 `../V3.5/` 独立维护。

## Source of Truth

Codex 维护 V3.0 时必须以 `v3_development_plan_multi_app_core.md` 为准。其他文档只能辅助理解，不得覆盖 final closeout plan 的阶段顺序、冻结合同和验收边界。

以下三份文件同等重要，必须同步维护：

- `CURRENT-STATUS_v3.md`
- `current-vs-target-gap_v3.md`
- `current-vs-target-gap_v3.drawio`

## Documents

| 文件 | 状态 | 用途 |
| --- | --- | --- |
| `v3_development_plan_multi_app_core.md` | V3.0 FINAL CLOSEOUT PLAN | V3.0-PhaseA 到 V3.0-PhaseE 的完成状态、冻结合同和 V3.x+ 边界 source of truth。 |
| `CURRENT-STATUS_v3.md` | V3.0 FINAL CLOSEOUT STATUS | 当前实际实现、验收证据和 V3.x+ 后续边界。 |
| `current-vs-target-gap_v3.md` | V3.0 GAP / HANDOFF | 当前实现与 V3.0 目标架构差异，以及 V3.x+ handoff。 |
| `current-vs-target-gap_v3.drawio` | V3.0 GAP DIAGRAM | 与 gap/status 文档同等重要的图形化差距视图。 |
| `harnessos_target_architecture_v3.md` | TARGET ARCHITECTURE | V3.0 目标架构：Multi-App Core + Pack Assembly + Connector Registry + Governed Runtime Adapter。 |
| `project-progress-introduction_v3.md` | TEAM INTRODUCTION | 面向团队介绍当前项目实现、阶段状态和核心平台合同。 |
| `team-baseline-and-target-architecture_v3.md` | TEAM BASELINE | 团队基线和目标架构说明。 |
| `v3_phasea_multi_app_core_readiness.md` | FROZEN PHASEA BASELINE | V3.0-PhaseA 详细实施文件；2026-05-06 完成验收后转为冻结基线。 |
| `v3_phasea_multi_app_core_readiness_acceptance.md` | FROZEN PHASEA ACCEPTANCE | V3.0-PhaseA 辅助验收基线与证据记录模板。 |
| `v3_phaseb_pack_connector_registry.md` | COMPLETED PHASEB BASELINE | V3.0-PhaseB 详细实施文件；Pack / Connector 装配边界冻结基线。 |
| `code-review-cleanup-checklist_v3.md` / `.drawio` | REVIEW CLOSEOUT | V3.0 代码检视和清扫检查清单。 |
| `connector-execution-runtime-phase5c.md` | CONNECTOR RUNTIME HANDOFF | FunASR / Data Service MCP connector execution runtime 增量记录。 |
| `data-service-mcp-codex-handoff.md` | DATA SERVICE MCP HANDOFF | Knowledge reference pack 依赖的 data_service MCP handoff。 |
| `video-flow-plane-call-relations_v3.md` / `.drawio` | ARCHITECTURE EXAMPLE | Video Flow 在六大平面上的调用关系、职责分层和 V4 目标支撑分析。 |
| `acceptance-test-cases_v3.md` | ACCEPTANCE CASES | V3.0 阶段验收用例。 |
| `test-acceptance-plan_v3.md` | TEST PLAN | V3.0 测试验收入口和执行计划。 |
| `phase3-manual-acceptance_v3.md` | MANUAL ACCEPTANCE | V3.0 手工验收记录。 |
| `v3_current_gap_analysis.md` | DESIGN GAP AUDIT | V3.0 设计目录内的差距审计。 |
| `v3_evolution_direction.md` | V3.x+ FUTURE BLUEPRINT | 低代码、Memory、Feedback、Workflow Library 等远期方向。 |
| `v3_old_vs_new_plan_comparison.md` / `.drawio` | DECISION RECORD | 旧 V3.0 蓝图与当前 active plan 的取舍记录。 |
| `diagrams/` | ARCHITECTURE DIAGRAMS | V3.0 当前架构、目标架构、multi-app core、Knowledge Pack DAG、Video Studio Pack DAG 图。 |

## Active Route

- V3.0-PhaseA Multi-App Core Readiness
- V3.0-PhaseB Pack Assembly + Connector Registry
- V3.0-PhaseC Job / Artifact / Governance Hardening
- V3.0-PhaseD Meeting Reference Pack Validation
- V3.0-PhaseE Knowledge Reference Pack Validation

当前收官状态：

- V3.0-PhaseA：COMPLETED / FROZEN BASELINE（2026-05-06）
- V3.0-PhaseB：COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08）
- V3.0-PhaseC：COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08）
- V3.0-PhaseD：VALIDATION PASSED（Meeting Pack assembly、legacy facade equivalence、strict/resilience real-audio E2E passed）
- V3.0-PhaseE：VALIDATION PASSED（Knowledge Pack + migrated data_service MCP E2E passed）

## Numbering Rule

- 架构平面统一使用 `Plane-1` 到 `Plane-6`。
- 当前开发阶段统一使用 `V3.0-PhaseA` 到 `V3.0-PhaseE`。
- 当前阶段切片统一使用 `V3.0-PhaseX-Xn`，例如 `V3.0-PhaseB-B2`。
- 验收项统一使用 `V3.0-PhaseX-ACnn`，例如 `V3.0-PhaseC-AC04`。
- `P0/P1/P2` 只表示阻塞级别或优先级，不表示架构平面。

## Implementation Rule

如果 future blueprint 与 final closeout plan 存在冲突，按 final closeout plan 执行。低代码工作流、Core Memory、Feedback Optimization Loop、Workflow Library、Interview、Investment、Video Studio 均不进入当前 V3.0-PhaseA 到 V3.0-PhaseE 验收范围。

补充规则：

- 当前 V3.0 的主交付物是 Multi-App Core、Pack Assembly、Connector Registry、Governed Runtime Adapter，而不是把 Meeting / Knowledge 做成平台内置业务。
- Meeting / Knowledge 在 V3.0 中是 reference packs / validation samples，用于验证平台抽象是否足够通用。
- 新增业务若仍需要修改 Core 或 Gateway 业务逻辑，视为 V3.0 平台边界未达标，而不是“正常扩展方式”。
- 当前 harnessOS 已通过 `voice_service` 的 `funasr_mcp` stdio connector 完成真实音频转写与 Meeting lineage 验收，并已通过迁移后的 `/Users/Zhuanz/Desktop/workspace/data_service` stdio MCP 完成 Knowledge reference pack 验收；两个 sibling 项目仍作为 connector 边界外部依赖，不写入 Core/Gateway 业务逻辑。

## V3.5 Handoff

V3.5 阶段将在 `../V3.5/` 维护。V3.5 的定位是 Application Adaptation Layer，位于 Client/Product UI Layer 与 Protocol App Server Layer 之间。V3.5 不重构 Core、不重复验证 Meeting/Knowledge、不实现完整 Workflow Studio。

