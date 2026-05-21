# ResearchNotebook V1.0 Design Docs

文档状态：V1.0-RC8 remote sync complete；V1.1-RC2 live experience smoke passed；后续真实后端/前端变更仍需以 `v1_0_current_gap_analysis.md` 和同名 drawio 作为最优先维护入口。
当前目标：保持 M0-M4 release candidate repository handoff 状态；RC6 已确认 source trace contract 仍未修复。V1.1-B/C/D 可声明受限文本源 workspace query evidence navigation 路径已通过 smoke，但不改变 V1.0 release status，也不代表 source trace integration ready。

## Positioning

ResearchNotebook V1.0 的目标是建立 **Source-grounded Personal Knowledge Workspace**。它不是 `data_service` 的治理台换皮，也不是 Obsidian filesystem vault 的复刻，而是一个独立前端应用层：

```text
ResearchNotebook Product UI
  Home / Workspace Source Library / Ask with Evidence / Session Workbench
  -> ResearchNotebook Application Layer
      routes / state / interaction / source trace drawer / evidence affordance
  -> data_service Target HTTP APIs
      /api/workspaces/... workspace / source / build / query / session / graph / quality
  -> data_service Knowledge Backend
      ingestion / indexing / retrieval / graph / artifact_ref / governance
```

V1.0 的产品重心是 NotebookLM-like 的 source-grounded ask：

```text
source import -> build -> ask -> source-level citation -> source trace/provenance drawer
```

Obsidian 只作为 workspace、graph、backlink、local-first 心智模型参考；ResearchNotebook 不复制 Obsidian 的 filesystem coupling。

## Documents

| 文件 | 用途 |
| --- | --- |
| `v1_0_starting_baseline.md` | V1.0 起点基线、已有文档、Stitch 原型和 `data_service` 约束。 |
| `v1_0_architecture_baseline.md` | ResearchNotebook 前端层、`data_service` 服务层、证据链和未来路线的架构位置。 |
| `v1_0_current_gap_analysis.md` | 当前差距、目标架构、阶段路线图；与同名 drawio 作为核心维护文件。 |
| `v1_0_current_gap_analysis.drawio` | V1.0 当前差距、目标架构、优先级和 V1.1/V1.2/V2.0 gate 图；必须与 Markdown 同步。 |
| `v1_0_development_plan_personal_knowledge.md` | V1.0-M0 到 M7 的阶段计划、实施切片和验收口径。 |
| `v1_0_acceptance_plan.md` | V1.0 验收、No False Green 规则和不能提前声明的能力。 |

当前活跃文档：

| 文件 | 用途 |
| --- | --- |
| `data_service_real_route_alignment.md` | RC3/RC6 真实 data_service target route 对齐记录。 |
| `feature-route-matrix.md` | 功能到 target route / app-local / unsupported / future backend phase 的矩阵。 |
| `api-adapter-contract.md` | V1.0 DTO、typed wrappers、fallback validation 和 contract test 规则。 |
| `answer-evidence-contract.md` | Ask with Evidence 的 ViewModel、citation、trace drawer 和 no-evidence 行为。 |
| `operation-polling-contract.md` | workspace/session build 的 operation polling hook 语义。 |
| `error-state-model.md` | normalized backend errors 到页面/组件状态的映射。 |
| `graph-context-contract.md` | M4 read-only graph context DTO、wrapper、状态和禁止范围。 |
| `lightweight-feedback-contract.md` | M4 lightweight feedback DTO、wrapper、状态和禁止范围。 |
| `v1_0_e2e_smoke_plan.md` | V1.0 最小 smoke 路径与 RC3/RC6 real data_service smoke matrix。 |
| `v1_0_integration_readiness_report.md` | RC3/RC6 integration smoke 结果、降级项和最终声明边界。 |
| `v1_0_rc4_final_readiness_report.md` | RC4 最终文档收口、No False Green 和 release candidate 声明。 |
| `v1_0_release_checklist.md` | V1.0 release checklist，使用 `PASS` / `DEGRADED_ACCEPTED` / `NOT_READY` 三态。 |
| `v1_0_rc5_repository_hygiene_summary.md` | RC5 release packaging、命令命名、fixture 分层和仓库卫生记录。 |
| `v1_0_rc6_source_trace_resmoke_report.md` | RC6 source trace contract re-smoke 结果和 source trace integration 决策。 |
| `v1_0_rc7_release_handoff.md` | RC7 最终仓库交付状态、验证命令、降级项、禁止声明和后续路线。 |

V1.1 活跃文档入口：

| 文件 | 用途 |
| --- | --- |
| `../V1.1/00_README.md` | V1.1 Source Preview / Evidence Navigation 文档索引。 |
| `../V1.1/v1_1_current_gap_analysis.md` | V1.1-A / V1.1-BE / V1.1-B 到 V1.1-RC 的当前差距与阶段切片。 |
| `../V1.1/v1_1_current_gap_analysis.drawio` | V1.1 可视化 gap / roadmap 图。 |
| `../V1.1/capability-manifest-contract.md` | capability/version manifest 合同。 |
| `../V1.1/source-preview-contract.md` | source preview / DocumentUnit 合同。 |
| `../V1.1/evidence-navigation-contract.md` | EvidenceSpan / locator / precise navigation 合同。 |

历史/计划文档：

| 文件 | 用途 |
| --- | --- |
| `development-plan-draft.md` | 早期 V1.0 开发计划草案，保留为背景材料。 |
| `v1_0_development_plan_personal_knowledge.md` | V1.0-M0 到 M7 的阶段计划、实施切片和验收口径。 |
| `v1_0_rc2_alignment_plan.md` | RC2 source trace / graph alignment 实施记录。 |
| `v1_0_rc3_release_readiness_plan.md` | RC3 real data_service re-smoke 计划。 |
| `data-service-baseline-integration-notes.md` | `data_service` baseline 集成理解与边界。 |
| `git_remote_sync_status.md` | ResearchNotebook 独立 Git 远端同步状态和阻塞项。 |
| `mock-data-policy.md` | M0 mock/static screen 的边界，防止 future shell 伪装成真实能力。 |
| `source-library-information-architecture.md` | Source Library 字段、状态和操作模型。 |
| `source-intermediate-model.md` | Source / DocumentUnit / EvidenceSpan / artifact_ref 中间模型。 |
| `docs/roadmap/multi-format-ingestion-contract.md` | `data_service` 多格式摄入合同路线。 |
| `docs/roadmap/assessment-service-contract.md` | `data_service` Assessment 合同路线。 |

## Baseline Rules

- `research-notebook` 是独立前端应用仓库。
- `data_service` 是独立本地知识治理与检索服务仓库。
- ResearchNotebook 只走 `/api/workspaces/...` target routes。
- 新功能不得使用 `/api/v1/knowledge/*`。
- 前端不得读取 raw filesystem path、cache path、artifact physical path。
- `shared/api/dataServiceClient.ts` 是唯一 API route shape 层。
- long-running build 必须使用 `operation_id` polling hook。
- `/knowledge` 仍是 backend governance console，不是产品 UI。
- V1.0 不声明 JSON/PPT/video/audio 全量 ingestion ready。
- V1.0 不声明 interview assessment、mastery profile、rich editor persistence、cloud sync 或 collaboration ready。
- Quality/Governance 在 V1.0 只能是轻量反馈入口，不得成为主体验。
- `v1_0_current_gap_analysis.md` 与 `v1_0_current_gap_analysis.drawio` 是 V1.0 核心维护文件，后续阶段变更必须同步更新。

## V1.0 Release Gate

1. `V1.0-M0` Scaffold / Design System / App Shell。
2. `V1.0-M1` API Adapter / Workspace Home。
3. `V1.0-M2` Source Library / Build / Ask with Evidence。
4. `V1.0-M3` Session Workbench / Session Ask with Evidence。
5. `V1.0-M4` Read-only Graph / Lightweight Feedback。

V1.0 release scope stops at M4. M0-M4 are the only release-blocking implementation milestones.

## Post-MVP / Future Shell Tracks

6. `V1.0-M5` Source Preview / Evidence Navigation。
7. `V1.0-M6` Multi-format Ingestion Foundation。
8. `V1.0-M7` Assessment Studio Future Shell。

M5-M7 may keep design notes, type drafts, disabled UI prototypes, or route placeholders, but they must not block V1.0 release and must not present future backend capabilities as ready.

M0-M4 mock/adapter tests 通过后可以声明：

```text
ResearchNotebook V1.0 release gate M0-M4 is API-adapter-ready.
```

RC3/RC6 真实 `data_service` smoke 通过后，当前可声明：

```text
ResearchNotebook V1.0 release candidate package is repository-ready.
ResearchNotebook V1.0 M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with trace-unavailable fallback.
```

RC6 已确认 registry `source_id` trace 仍返回 404。如果后端后续修复该 contract，需要重新执行 `npm run smoke:release` 并更新 `v1_0_release_checklist.md`、`v1_0_integration_readiness_report.md` 和 gap markdown/drawio，才能声明 source trace integration ready。

V1.0 完成后仍不能声明：

```text
source trace integration ready
source preview ready
precise citation backjump ready
JSON/PPT/video/audio ingestion ready
interview assessment ready
mastery profile ready
rich editor persistence ready
cloud sync ready
collaboration ready
data_service governance console replaced
```

## P0 Clarification Documents

M0-M4 implementation contracts must remain synchronized with the gap analysis:

| 文件 | 用途 |
| --- | --- |
| `api-adapter-contract.md` | V1.0 DTO、typed wrappers、fallback validation 和 contract test 规则。 |
| `answer-evidence-contract.md` | Ask with Evidence 的 ViewModel、citation、trace drawer 和 no-evidence 行为。 |
| `operation-polling-contract.md` | workspace/session build 的 operation polling hook 语义。 |
| `error-state-model.md` | normalized backend errors 到页面/组件状态的映射。 |
| `mock-data-policy.md` | M0 mock/static screen 的边界，防止 future shell 伪装成真实能力。 |
| `source-library-information-architecture.md` | Source Library 字段、状态和操作模型。 |
| `graph-context-contract.md` | Read-only graph context 合同。 |
| `lightweight-feedback-contract.md` | Lightweight feedback 合同。 |
| `v1_0_e2e_smoke_plan.md` | V1.0 最小 Playwright smoke 路径。 |
