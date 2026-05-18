# ResearchNotebook V1.0 Current Gap Analysis

文档状态：V1.0-RC1 integration smoke complete；source trace remains accepted degraded / unresolved backend alignment item。
配套图：`v1_0_current_gap_analysis.drawio`。

本文与 `v1_0_current_gap_analysis.drawio` 是 V1.0 后续规划、验收和与用户交互时的核心维护文件。两者必须同步更新：本文承载文字合同，drawio 承载同一套架构演进、差距矩阵、阶段路线图和 V1.1/V1.2/V2.0 gate。

## 1. 文档定位

本文只描述 ResearchNotebook V1.0 **Source-grounded Personal Knowledge Workspace** 的当前差距、目标架构和阶段影响范围。已有 `data_service` 能力只作为 V1.0 的后端起点基线，不进入本文作为前端待办。

V1.0 不是继续扩展 `data_service` 治理台，也不是直接实现后续多格式摄入和 Assessment Studio。它要补的是个人知识库产品 UI 所依赖的前端事实源和交互链路：

```text
data_service V1.6 backend baseline
  -> ResearchNotebook V1.0 application layer
  -> V1.1 source preview / evidence navigation
  -> V1.2 multi-format ingestion capability
  -> V2.0 Assessment Studio
```

因此，V1.0 gap 不应被描述成以下几类问题：

- 不是 `data_service` parser / indexer / retriever 的前端实现。
- 不是 `/knowledge` governance console 的换皮。
- 不是 Obsidian vault filesystem 的复刻。
- 不是完整 NotebookLM 的复刻。
- 不是 JSON/PPT/video/audio 全量摄入。
- 不是 interview assessment / mastery profile。

V1.0 要回答的问题是：

> 基于现有 `data_service` target routes，如何把 source import、build、ask、citation、trace/provenance 和 session workbench 做成一个可用的个人知识库产品体验。

## 2. 当前状态

当前 ResearchNotebook 已完成 V1.0-M0 到 M4 的 API-adapter-ready implementation：

- 已建立 `docs/design/V1.0/development-plan-draft.md`。
- 已建立 `docs/design/V1.0/data-service-baseline-integration-notes.md`。
- 已建立 `docs/design/V1.0/feature-route-matrix.md`。
- 已建立 `docs/design/V1.0/source-intermediate-model.md`。
- 已建立 `docs/design/V1.0/api-adapter-contract.md`。
- 已建立 `docs/design/V1.0/answer-evidence-contract.md`。
- 已建立 `docs/design/V1.0/operation-polling-contract.md`。
- 已建立 `docs/design/V1.0/error-state-model.md`。
- 已建立 `docs/design/V1.0/mock-data-policy.md`。
- 已建立 `docs/design/V1.0/source-library-information-architecture.md`。
- 已建立 `docs/design/V1.0/v1_0_e2e_smoke_plan.md`。
- 已建立 `docs/design/V1.0/graph-context-contract.md`。
- 已建立 `docs/design/V1.0/lightweight-feedback-contract.md`。
- 已建立 `docs/roadmap/multi-format-ingestion-contract.md`。
- 已建立 `docs/roadmap/assessment-service-contract.md`。
- 已读取 Stitch 项目 `5501162743214630907`，确认核心屏幕为工作区主页、AI 研究工作台和 Workspace Flow。
- 已确认设计系统：light mode、Roboto Flex、Google Blue、280px sidebar、fluid canvas。

当前 `data_service` V1.6 backend baseline 可提供：

- workspace lifecycle；
- source lifecycle；
- build lifecycle；
- workspace query / distill；
- graph read surfaces；
- session lifecycle / ingest / query / build；
- quality feedback / correction rules / correction plan；
- stable `artifact_ref`。

当前 ResearchNotebook 已完成：

- 前端 scaffold / AppShell / Stitch tokens；
- `dataServiceClient.ts` typed adapter 与 normalized errors；
- Workspace Home；
- Source Library；
- workspace build / workspace ask with evidence；
- Source Trace / Provenance Drawer；
- Session Workbench；
- read-only Graph Context；
- Lightweight Feedback。

RC1 真实 `data_service` smoke 已完成：

- workspace create/list/get：pass；
- source create/list/get：pass；
- workspace build/query：pass；
- session create/ingest/build/query：pass，其中 session query no-evidence 为接受降级；
- graph community：pass；
- feedback submit：pass；
- source trace：degraded，当前 minimal text source 返回 404，需要后续确认后端 source_id / trace contract。

当前缺口已经从：

```text
ResearchNotebook 是否应该修改 data_service /knowledge console
```

转为：

```text
如何基于 data_service target routes 做出 NotebookLM-like 的 source-grounded 个人知识库产品体验
```

## 3. 架构演进口径

ResearchNotebook V1.0 在整体架构中的位置是新的 **Application Layer**。它位于产品交互和 `data_service` target APIs 之间：

```text
Plane-0 Product Interaction Reference
  NotebookLM source-grounded ask / Obsidian workspace graph mental model

Plane-1 ResearchNotebook Product UI
  Home / Workspace / Ask with Evidence / Trace Drawer / Session Workbench

Plane-2 ResearchNotebook Application Layer
  routes / local UI state / query state / operation polling / error states

Plane-3 API Adapter Contract
  shared/api/dataServiceClient.ts / typed client / runtime validation

Plane-4 data_service Target APIs
  /api/workspaces/... workspace / source / build / query / session / graph / quality

Plane-5 data_service Knowledge Backend
  ingestion / indexing / retrieval / graph / artifact_ref / governance

Plane-6 Future Service Contracts
  capability manifest / DocumentUnit / EvidenceSpan / Assessment
```

| 阶段 | 已解决 / 目标 | 对下一阶段的意义 |
| --- | --- | --- |
| `data_service` V1.6 baseline | 本地知识治理与检索服务已具备 target routes。 | 为 ResearchNotebook V1.0 提供后端事实源。 |
| ResearchNotebook V1.0 target | source-grounded personal knowledge MVP。 | 为 V1.1 preview/evidence 和 V1.2 ingestion capability 提供产品壳。 |
| ResearchNotebook V2.0 target | Assessment Studio 基于技术文档生成面试题并评估掌握度。 | 依赖 V1.2 extraction/evidence contracts 和 V1.3-V1.5 assessment service contracts。 |

V1.0 正式产品调用链应为：

```text
ResearchNotebook UI
  -> shared/api/dataServiceClient.ts
  -> /api/workspaces/... target routes
  -> data_service workspace/source/build/query/session/graph/quality
  -> stable IDs / artifact_ref / source trace
```

## 4. 目标状态

V1.0 完成后，ResearchNotebook 应具备以下目标状态：

- Workspace Home 可列出、创建、进入 workspace。
- Source Library 可列出、导入、查看 source detail。
- Build UI 可启动、轮询、取消 workspace/session build。
- Ask UI 可对 workspace 提问。
- Answer UI 不是普通 chat，而是显示 source-level citation affordance。
- Citation 点击可打开 source trace/provenance drawer。
- 没有 precise locator 时，证据交互退化为 source-level evidence。
- Session Workbench 可创建 session、ingest snippet、session query。
- Graph Panel 可展示 read-only neighbors/community/query/session artifact context。
- Quality 只作为 lightweight feedback entry，不成为主产品面。
- Frontend 不依赖 raw path/cache path/artifact physical path。
- `/knowledge` 保持 `data_service` governance console。

## 5. 核心差距

| 差距 | 当前状态 | V1.0 目标 | 阶段 |
| --- | --- | --- | --- |
| App scaffold | 已实现 Vite React TS、AppShell、路由骨架。 | 继续保持可运行前端壳。 | M0 done |
| Design system | 已落地 Stitch tokens、sidebar、main canvas、状态组件、M2/M3/M4 产品样式。 | 后续按 M5+ 增量扩展。 | M0-M4 done |
| API adapter | 已实现 `dataServiceClient.ts` 唯一路由层、typed wrappers、normalized errors、adapter tests。 | 后续 route 扩展仍只进入 adapter。 | M1-M4 done |
| Workspace Home | 已实现 list/create/detail/archive、empty/backend/schema mismatch 状态。 | 真实后端联调后才能声明 integration ready。 | M1 done |
| Source Library | 已实现 source list/minimal import/remove/trace action 和 source 状态信息。 | 文件上传和格式能力仍由未来 capability manifest 驱动。 | M2 done |
| Build lifecycle | 已实现 workspace build 与 session build start/status/cancel，共用 polling hook。 | 不实现 source-level build route。 | M2/M3 done |
| Ask with Evidence | 已实现 workspace query mutation、answer rendering、source-level citation、no-evidence state。 | precise locator/backjump 仍为 M5 future backend phase。 | M2 done |
| Source Trace Drawer | 已实现 source trace/provenance drawer、loading/not found/unavailable/service unavailable 状态；RC1 minimal text source trace 返回 404。 | full source preview 不在 M2；trace unavailable 作为 V1.0 降级状态保留。 | M2 done / RC1 degraded |
| Session Workbench | 已实现 workspace-scoped session list/create/get/close、snippet ingest、session build、session query、evidence 和 trace drawer 复用。 | 真实后端联调后才能声明 integration ready；delete deferred。 | M3 done |
| Graph Context | 已实现 workspace neighbors/community 与 session graph context 只读面板；RC1 graph community pass，neighbors overview 因缺少 node_id/entity_id 降级。 | 不做任意 graph DSL、编辑、治理。 | M4 done / RC1 partial |
| Quality / Governance | 已实现 lightweight feedback；未暴露治理台和 correction rules CRUD。 | Quality 仍保持 secondary feedback entry。 | M4 done |
| Source Preview | V1.0 只能 source-level evidence。 | 完整 preview 依赖 `DocumentUnit` / capability manifest。 | M5 / future |
| Precise Citation Backjump | V1.0 不具备 page/slide/timestamp/json path contract。 | 基于 `EvidenceSpan` locators 精确回跳。 | M5 / future |
| Multi-format ingestion | V1.0 不声明 JSON/PPT/video/audio ready。 | capability manifest + parser contracts。 | M6 / V1.2 |
| Assessment Studio | 只有 roadmap，不是 V1.0 capability。 | Question / Assessment / Attempt / MasteryProfile service contracts。 | M7 / V2.0 |

## 6. 开发计划摘要

### 6.1 当前开发阶段

当前项目处于 **V1.0-RC1 integration smoke complete** 阶段。当前已经具备：

- ResearchNotebook 与 `data_service` 的职责边界；
- Stitch 原型和 design system 事实源；
- V1.0 route matrix；
- source intermediate model；
- multi-format ingestion roadmap；
- assessment service contract roadmap；
- V1.0 docs/design 文档集。
- 可运行前端壳、Workspace Home、Source Library、workspace build polling、Ask with Evidence、Source Trace Drawer、Session Workbench、Graph Context、Lightweight Feedback。

当前需要继续推进的是：

- 解决或正式接受 RC1 source trace degraded 行为；
- 评估 Graph neighbors 是否需要 node selection 触发，而不是 overview 自动调用；
- M5-M7：Post-MVP / Future Shell，不阻塞 V1.0 release。

### 6.2 阶段路线图

| 阶段 | 目标 | 主要交付 | 完成后可声明 |
| --- | --- | --- | --- |
| M0 | Scaffold / Design System | Vite React TS、AppShell、Stitch tokens、health/version shell。 | Done：V1.0 frontend shell API-adapter-ready。 |
| M1 | API Adapter / Workspace Home | `dataServiceClient.ts`、workspace list/create/detail、error states。 | Done：Workspace Home API-adapter-ready。 |
| M2 | Source Library / Ask with Evidence | source lifecycle、workspace build polling、workspace query、source-level citations、trace drawer。 | Done：Source Library / Build / Ask-with-Evidence API-adapter-ready。 |
| M3 | Session Workbench | session lifecycle、session ingest/query/build、three-panel workbench。 | Done：Session Workbench API-adapter-ready。 |
| M4 | Graph / Lightweight Feedback | read-only graph context、feedback entry。 | Done：Graph Context / Lightweight Feedback API-adapter-ready。 |
| M5 | Source Preview / Evidence Navigation | `DocumentUnit`、`EvidenceSpan`、precise locator navigation。 | Post-MVP only；not V1.0 release blocking。 |
| M6 | Multi-format Ingestion Foundation | capability manifest、JSON/PPT/video/audio support states。 | Future backend phase；not V1.0 release blocking。 |
| M7 | Assessment Studio Future Shell | type drafts、route placeholders、UI prototype、no fake product capability。 | Future shell only；not V1.0 release blocking。 |

V1.0 release gate is M0-M4. M5-M7 may be documented or prototyped in disabled/future-shell form, but they must not block V1.0 release.

### 6.3 P0 Engineering Clarifications Before M2

M0-M1 can start while contracts are being finalized. M2-M3 must not start broad implementation until these documents exist:

- `api-adapter-contract.md`;
- `answer-evidence-contract.md`;
- `operation-polling-contract.md`;
- `error-state-model.md`;
- `mock-data-policy.md`;
- `source-library-information-architecture.md`;
- `v1_0_e2e_smoke_plan.md`.

## 7. V1.1 / V1.2 / V2.0 Gate

### V1.1 Gate

进入 V1.1 前必须具备：

- source preview backend contract；
- `DocumentUnit` contract；
- `EvidenceSpan` contract；
- source-level fallback 保持可用。

### V1.2 Gate

进入 V1.2 前必须具备：

- `data_service` capability manifest；
- JSON parser capability；
- PPT parser capability；
- video/audio transcription capability；
- partial/unsupported state contract。

### V2.0 Gate

进入 V2.0 Assessment Studio 前必须具备：

- evidence-backed question generation route；
- attempt scoring route；
- review source refs；
- mastery profile route；
- assessment 与 quality governance 的明确隔离。

## 8. No False Green

V1.0 可以声明：

```text
ResearchNotebook V1.0 source-grounded personal knowledge MVP ready.
```

V1.0 不能声明：

```text
JSON/PPT/video/audio ingestion ready
precise citation backjump ready
interview assessment ready
mastery profile ready
rich editor persistence ready
cloud sync ready
collaboration ready
correction apply ready
data_service governance console replaced
```

## 9. 后续维护规则

- 本文和 drawio 必须同步更新。
- 任何功能优先级变化必须先更新核心差距表和阶段路线图。
- 任何后端能力假设必须先更新 route matrix 或 roadmap contract。
- 任何 V1.0 ready 声明必须通过 acceptance plan 的 No False Green 检查。
