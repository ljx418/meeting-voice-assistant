# ResearchNotebook V1.0 Current Gap Analysis

文档状态：V1.0-RC8 remote sync complete；V1.1-RC2 live experience smoke passed；V1.0 release status unchanged。
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

RC3 真实 `data_service` smoke 已完成：

- workspace create/list/get：pass；
- source create/list/get：pass；
- workspace build/query：pass；
- session create/ingest/build/query：pass，其中 session query no-evidence 为接受降级；
- graph community：pass；
- feedback submit：pass；
- source trace：RC3/RC6 曾对 minimal text registry `source_id` trace 返回 404；V1.1-RC4 backend fix 后 registry source trace 已返回 HTTP 200，fallback 仍用于 unsupported/failing trace case。
- graph neighbors：RC3 真实后端 community 返回 members，node-scoped neighbors 成功。

RC5 release packaging / repository hygiene 已完成：

- 推荐 smoke 命令统一为 `npm run smoke:release`；
- `npm run smoke:rc1` 保留为 legacy alias；
- release smoke 脚本使用 `rn-release-<timestamp>` workspace prefix；
- README 已收口 V1.0 定位、本地启动、默认 `data_service` base URL、accepted degraded states 和禁止声明能力；
- release checklist 已三态化为 `PASS` / `DEGRADED_ACCEPTED` / `NOT_READY`；
- fixture 已拆分为 `fixtures/real/` 和 `fixtures/adapter/`，adapter-only fixture 不作为真实后端通过项；
- `.gitignore` 已覆盖本地 workspace、临时 smoke 产物和常规构建/测试输出。

RC6 source trace contract re-smoke 已完成：

- `npm run check` 通过；
- 本地 `data_service` 在 `http://127.0.0.1:8003` healthy；
- `npm run smoke:release` 完整通过 workspace/source/build/query/session/graph/feedback/cleanup 链路；
- registry source id `src_2003ad3198c69861` 的 `sources.trace` 仍返回 `404 Unknown source_id`；
- source trace integration 仍为 `NOT_READY`；
- trace-unavailable fallback 继续作为 V1.0 accepted degraded state；
- 已新增 `v1_0_rc6_source_trace_resmoke_report.md` 记录结果。

V1.1-RC4 source trace re-smoke 已完成：

- `npm run smoke:v1.1-rc4-trace` 已执行；
- source create/list/get 返回 registry source id `src_cce80f0ca6dad217`；
- workspace query evidence mapping 观察到 registry source id；
- direct `sources.trace` 对同一 registry source id 返回 HTTP 200；
- source trace integration 对 RC4 smoke 覆盖的 registry source_id-backed sources 进入受限 PASS；
- trace-unavailable fallback 继续作为 unsupported/failing trace case 的 accepted degraded state。

RC7 final repository sync / release handoff 已完成：

- 未新增功能，未进入 M5+；
- 未复跑 `smoke:release`，沿用 RC6 真实 smoke 证据；
- 已新增 `v1_0_rc7_release_handoff.md`；
- 已完成 path hygiene：无本地绝对路径、`cache_path`、`artifact_path`、`physical_path`；
- `npm run check` 通过；
- 当前交付口径为 repository handoff complete。

RC8 scoped commit / remote sync 已完成：

- `research-notebook/` scoped 范围已提交并推送到现有上层远端；
- `npm run check` 通过；
- RC8 完成时 `research-notebook/` 无待提交变更；此后 V1.1-A / V1.1-BE 相关文档与前端 shell 变更进入当前 working tree；
- source trace integration 已对 RC4 smoke 覆盖的 registry source_id-backed sources 进入受限 PASS；
- trace-unavailable fallback 对 unsupported/failing trace case 仍为 `DEGRADED_ACCEPTED`。

V1.1-A Contract Discovery / Disabled Shell 已完成：

- V1.1 文档迁移到 `docs/design/V1.1/`；
- 已新增 capability manifest、source preview、evidence navigation 合同草案；
- adapter 暴露 V1.1 DTO / wrapper shell；
- V1.1-A 完成时 Source Preview drawer 只显示 capability missing / unsupported；该状态已被后续 V1.1-B frontend integration superseded；
- Precise Citation Backjump 仍为 `NOT_READY`。

V1.1-BE backend contract enablement 已在本地 `data_service` 工作区完成：

- `GET /api/workspaces/{workspace_id}/capabilities` 后端合同已加入；
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview` source-level preview 后端合同已加入；
- preview route 使用 registry `source_id`，不接受 `artifact_ref`、llmwiki slug 或 page ref 作为 source id；
- 后端聚焦测试已通过，sanitized fixtures 已保存；
- 该 backend contract 已被 V1.1-B frontend integration 消费。

V1.1-B Source-Level Preview frontend integration 已完成：

- `capabilities.get(workspaceId)` 已接入真实 target route；
- `sources.preview(workspaceId, sourceId)` 已接入真实 target route；
- Source Preview Drawer 已支持 source-level preview、安全文本渲染、unsupported / unavailable / schema mismatch 状态；
- real data_service smoke 已通过 text source-level preview；
- Source Preview 可声明为 data_service-supported text source 的 source-level integration ready；
- 这不改变 V1.0 release 声明，也不代表 source trace integration ready。

V1.1-C Unit-Level Source Navigation 已推进完成：

- V1.1-C-A disabled shell 已完成；
- V1.1-C-BE DocumentUnit backend contract 已完成；
- V1.1-C frontend unit outline、unit detail 和分页已接入；
- real data_service HTTP smoke 已通过 text source；
- Unit-Level Source Navigation 可声明为 data_service-supported text source integration-ready。

V1.1-D EvidenceSpan frontend and browser-smoked path 已完成：

- V1.1-D-BE EvidenceSpan backend contract 已完成；
- workspace citation -> Source Preview Drawer -> unit detail -> EvidenceSpan detail -> safe text highlight 路径已实现；
- mocked/API-adapter UI smoke 已通过；
- real data_service HTTP smoke 已通过；
- real browser visual smoke 已通过；
- RC2 live experience smoke 已通过；
- precise evidence navigation 只能声明为 data_service-supported text-source workspace query citations carrying `source_id + unit_id + evidence_id` 的受限路径 ready。

### 2.1 `v1_0_current_gap_analysis.drawio` 当前表达的状态

当前 drawio 不是“待开发功能列表”，而是 V1.0 的发布状态图。它表达的是：

```text
V1.0-M0 到 M4 主链路已完成
  -> RC3 已做真实 data_service smoke
  -> RC5 已完成 release packaging / repository hygiene
  -> RC6 已重跑 source trace contract smoke
  -> RC7 已完成 final repository handoff
  -> RC8 已完成 scoped remote sync
  -> V1.1-BE 已完成 source-level preview 后端合同启用
  -> V1.1-B 已完成 source-level preview 前端集成
  -> V1.1-C 已完成 unit navigation text source integration
  -> V1.1-D 已完成 EvidenceSpan HTTP + browser visual smoke
  -> V1.1-RC2 live experience smoke passed
  -> 当前包可作为 V1.0 release candidate repository handoff
  -> source trace integration 已对 RC4 registry source_id-backed text path 进入受限 PASS
```

图中 `当前开发阶段` 的含义是：

- 已完成 `smoke:release` 命名和脚本收口；
- 已完成 README / 文档索引 / release checklist 收口；
- 已完成 fixture 分层：`fixtures/real/` 和 `fixtures/adapter/`；
- 已完成 `PASS` / `DEGRADED_ACCEPTED` / `NOT_READY` 三态验收口径；
- RC7 未复跑 smoke，沿用 RC6 真实 smoke 证据；
- 已接受 unsupported/failing trace case 的 V1.0 降级行为；RC4 scoped registry source trace 已通过。

图中 `剩余差距` 的含义是：

- 不是 V1.0 release gate 的阻塞开发；
- 是后端 contract、V1.1+、V1.2+、V2.0 的后续工作入口；
- 当前 V1.0 声明边界是：**source trace integration 仅在 RC4 registry source_id-backed text path 内 ready，不能扩大成 all-source-type ready**。

### 2.2 RC5 的具体含义

`RC5` 是 `Release Candidate 5`，不是一个新功能 milestone。它代表 V1.0 已经从功能开发阶段进入发布候选包整理阶段。

RC5 做的事情只包括：

- 发布前仓库卫生；
- smoke 命令命名收口；
- README / onboarding 收口；
- fixture 语义分层；
- release checklist 三态化；
- gap markdown / drawio 同步；
- 确认哪些能力可以声明，哪些能力不能声明。

RC5 不代表：

- source trace integration 已完成；
- source preview 已完成；
- precise citation backjump 已完成；
- multi-format ingestion 已完成；
- assessment 已完成；
- quality governance console 已完成。

当前准确声明是：

```text
ResearchNotebook V1.0 release candidate package is repository-ready.
ResearchNotebook V1.0 M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with trace-unavailable fallback.
```

仍不能声明：

```text
source trace integration ready
source preview ready
precise citation backjump ready
multi-format ingestion ready
assessment ready
quality governance console ready
graph editing/governance ready
cloud sync/collaboration ready
```

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
| Workspace Home | 已实现 list/create/detail/archive、empty/backend/schema mismatch 状态；RC3 real smoke pass。 | 保持 release candidate readiness。 | M1 done / RC3 pass |
| Source Library | 已实现 source list/minimal import/remove/trace action 和 source 状态信息。 | 文件上传和格式能力仍由未来 capability manifest 驱动。 | M2 done |
| Build lifecycle | 已实现 workspace build 与 session build start/status/cancel，共用 polling hook。 | 不实现 source-level build route。 | M2/M3 done |
| Ask with Evidence | 已实现 workspace query mutation、answer rendering、source-level citation、no-evidence state。 | precise locator/backjump 仍为 M5 future backend phase。 | M2 done |
| Source Trace Drawer | 已实现 source trace/provenance drawer、loading/not found/unavailable/service unavailable 状态；RC3 minimal text trace 404 走 source detail metadata fallback。 | full source preview 不在 M2；trace unavailable 作为 V1.0 降级状态保留。 | M2 done / RC3 degraded accepted |
| Session Workbench | 已实现 workspace-scoped session list/create/get/close、snippet ingest、session build、session query、evidence 和 trace drawer 复用；RC3 real smoke pass，session query no-evidence accepted degraded。 | delete deferred；session query evidence 仍不能以 adapter fixture 伪装成 real backend pass。 | M3 done / RC3 pass with accepted degraded |
| Graph Context | 已实现 communities-first overview；RC3 confirmed community members can trigger node-scoped neighbors。 | 不做任意 graph DSL、编辑、治理；community 无 members 时显示选择提示。 | M4 done / RC3 pass |
| Quality / Governance | 已实现 lightweight feedback；未暴露治理台和 correction rules CRUD。 | Quality 仍保持 secondary feedback entry。 | M4 done |
| Source Preview | V1.0 只能 source-level evidence。 | 完整 preview 依赖 `DocumentUnit` / capability manifest。 | M5 / future |
| Precise Citation Backjump | V1.0 不具备 page/slide/timestamp/json path contract。 | 基于 `EvidenceSpan` locators 精确回跳。 | M5 / future |
| Multi-format ingestion | V1.0 不声明 JSON/PPT/video/audio ready。 | capability manifest + parser contracts。 | M6 / V1.2 |
| Assessment Studio | 只有 roadmap，不是 V1.0 capability。 | Question / Assessment / Attempt / MasteryProfile service contracts。 | M7 / V2.0 |

## 6. 开发计划摘要

### 6.1 当前开发阶段

当前项目处于 **V1.0-RC8 remote sync complete + V1.1-RC2 live experience smoke passed** 阶段。当前已经具备：

- ResearchNotebook 与 `data_service` 的职责边界；
- Stitch 原型和 design system 事实源；
- V1.0 route matrix；
- source intermediate model；
- multi-format ingestion roadmap；
- assessment service contract roadmap；
- V1.0 docs/design 文档集。
- 可运行前端壳、Workspace Home、Source Library、workspace build polling、Ask with Evidence、Source Trace Drawer、Session Workbench、Graph Context、Lightweight Feedback。

当前需要继续推进的是：

- V1.1-B Source Preview：data_service-supported text source integration-ready；
- V1.1-C Unit-Level Source Navigation：data_service-supported text source integration-ready；
- V1.1-D EvidenceSpan Highlight：browser-smoke-ready for data_service-supported text-source workspace query citations；
- V1.1-RC2：live experience smoke passed；
- source trace contract 已由 data_service backend fix 修复，并通过 `npm run smoke:v1.1-rc4-trace`；当前只能声明 RC4 scoped registry source trace ready；
- V1.1-BE preview route 成功仍不能等同于 all-source-type source trace integration ready；
- M5-M7：Post-MVP / Future Shell，不阻塞 V1.0 release。

### 6.1.1 V1.0 后续还剩多少开发内容

按当前状态，V1.0 **release gate 的产品开发已经完成 M0-M4**。后续剩余工作应分为三类：

| 类型 | 是否阻塞 V1.0 RC | 内容 | 估算工作量 |
| --- | --- | --- | --- |
| Release packaging closure | 已完成 | RC7 handoff 与 RC8 scoped remote sync 已完成。 | Done |
| Source trace contract alignment | 已完成 scoped fix；不代表全量 trace ready | 后端已让 RC4 registry `source_id` 的 `sources.trace` 稳定返回 trace/provenance；ResearchNotebook 已重跑 RC4 source trace smoke 并更新 fixtures/checklist。 | Done for RC4-covered registry text source |
| V1.1 Source Preview frontend integration | 不属于 V1.0 release gate | V1.1-B 已完成 source-level text preview integration smoke。 | Done for text source-level preview |
| V1.1-D EvidenceSpan frontend/browser path | 不属于 V1.0 release gate | Workspace citation -> preview drawer -> unit detail -> EvidenceSpan highlight path 已实现并通过 HTTP smoke、browser visual smoke 和 RC2 live smoke。 | Done for supported text-source workspace query path |
| V1.1+ product expansion | 不属于 V1.0 release gate | Source trace contract re-smoke、session precise navigation、V1.2 Multi-format、V2.0 Assessment。 | 大，依赖新 backend contracts |

因此，V1.0 当前剩余开发结论是：

```text
M0-M4：已完成，进入 release candidate。
RC5：已完成发布包/仓库卫生口径。
RC6：已重跑 source trace contract smoke；当时 trace 仍 404，保留 accepted degraded。
RC7：已完成 final repository handoff。
RC8：已完成 scoped commit / remote sync。
V1.1-RC4：data_service backend fix 后已重跑 source trace contract smoke；registry source_id direct trace 返回 HTTP 200，source trace integration 进入受限 PASS。
V1.0 内可选修正：后续只需要扩展 all-source-type / session trace smoke，不应把 RC4 结果扩大成全量 ready。
V1.1-BE：已完成 source-level preview backend contract enablement。
V1.1-B：已完成 source-level preview frontend integration and real data_service smoke for text source。
V1.1-D：EvidenceSpan frontend path 已完成 HTTP smoke、browser visual smoke 和 RC2 live smoke；precise evidence navigation 仅限 supported text-source workspace query path。
V1.1+ / V1.2+ / V2.0：仍有较多产品能力开发，不应混入 V1.0 发布声明。
```

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
