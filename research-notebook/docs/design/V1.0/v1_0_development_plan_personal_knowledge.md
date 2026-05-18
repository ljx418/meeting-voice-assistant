# ResearchNotebook V1.0 Personal Knowledge Development Plan

文档状态：V1.0 planning baseline。
执行范围：本计划用于后续代码实施；当前优先级以 `v1_0_current_gap_analysis.md` 和同名 drawio 为准。

## 1. Goal

V1.0 的目标是建立 **source-grounded personal knowledge MVP**：

```text
source import -> build -> ask -> source-level citation -> source trace/provenance drawer
```

V1.0 不是后端治理台，也不是完整 NotebookLM/Obsidian 复刻。

## 2. Scope

包含：

- AppShell / Design System；
- Workspace Home；
- Workspace Source Library；
- Source Import / Source Detail；
- Build Status；
- Ask with Evidence；
- Source Trace / Provenance Drawer；
- Session Workbench；
- Read-only Graph Context；
- Lightweight Feedback。

不包含：

- JSON/PPT/video/audio 全量 ingestion；
- interview assessment；
- mastery profile；
- rich editor persistence；
- cloud sync；
- collaboration；
- correction apply / execution；
- `/knowledge` 产品 UI 改造。

## 3. Impacted Files And Future Directories

文档阶段新增或更新：

- `docs/design/V1.0/00_README.md`
- `docs/design/V1.0/v1_0_starting_baseline.md`
- `docs/design/V1.0/v1_0_architecture_baseline.md`
- `docs/design/V1.0/v1_0_current_gap_analysis.md`
- `docs/design/V1.0/v1_0_current_gap_analysis.drawio`
- `docs/design/V1.0/v1_0_development_plan_personal_knowledge.md`
- `docs/design/V1.0/v1_0_acceptance_plan.md`

后续代码实施建议目录：

```text
src/
  app/
  features/
    workspaces/
    sources/
    build/
    query/
    sessions/
    graph/
    quality/
    assessment/          # V1.0 future shell only
  shared/
    api/
    components/
    design-system/
    hooks/
    types/
```

## 4. Phase Plan And PR Slices

### V1.0-M0 Scaffold / Design System / App Shell

PR slices:

- `V1.0-M0-PR1`：初始化 Vite React TypeScript。
- `V1.0-M0-PR2`：落地 Stitch design tokens。
- `V1.0-M0-PR3`：实现 AppShell、sidebar、main canvas、right panel shell。
- `V1.0-M0-PR4`：添加 health/version mismatch UI shell。

验收：

- dev server 可运行；
- build 通过；
- Home / Workbench shell 接近 Stitch 原型；
- 没有业务假数据被声明为真实能力。

### V1.0-M1 API Adapter / Workspace Home

PR slices:

- `V1.0-M1-PR1`：实现 `shared/api/dataServiceClient.ts`。
- `V1.0-M1-PR2`：实现 workspace list/create/detail wrappers。
- `V1.0-M1-PR3`：接入 TanStack Query。
- `V1.0-M1-PR4`：实现 loading/empty/error/version mismatch states。

验收：

- Home 使用 `GET /api/workspaces`；
- create 使用 `POST /api/workspaces`；
- 不调用 `/api/v1/knowledge/*`；
- 不暴露 raw path。

### V1.0-M2 Source Library / Build / Ask with Evidence

PR slices:

- `V1.0-M2-PR1`：source list/detail/import/remove。
- `V1.0-M2-PR2`：workspace build start/status/cancel 和 polling hook。
- `V1.0-M2-PR3`：workspace query。
- `V1.0-M2-PR4`：source-level citation affordance。
- `V1.0-M2-PR5`：source trace/provenance drawer。

验收：

- query result 不是普通 chat output；
- answer 至少显示 source-level evidence 或明确 no evidence state；
- citation click 通过 `source_id` 打开 trace/provenance drawer；
- 没有 precise locator 时退化到 source-level evidence。

### V1.0-M3 Session Workbench

PR slices:

- `V1.0-M3-PR1`：session create/list/detail/close；delete deferred。
- `V1.0-M3-PR2`：session ingest。
- `V1.0-M3-PR3`：session query。
- `V1.0-M3-PR4`：session build lifecycle。
- `V1.0-M3-PR5`：Workbench three-panel layout。

验收：

- session scoped ask 与 workspace ask 分离；
- session answer 复用 evidence/citation UI；
- active session 只存 `session_id`；
- operation polling 复用 M2 hook。

### V1.0-M4 Read-only Graph / Lightweight Feedback

PR slices:

- `V1.0-M4-PR1`：graph neighbors/community/session read-only panel。
- `V1.0-M4-PR2`：missing graph artifact state。
- `V1.0-M4-PR3`：quality feedback lightweight entry。
- `V1.0-M4-PR4`：Quality/Governance remains out of primary navigation；no correction rules CRUD UI。

验收：

- Graph 是上下文面板，不是任意 graph DSL/query builder；
- Quality 不成为主导航；
- 不暗示 correction apply 已存在。

## 5. Post-MVP / Future Shell Tracks

M5-M7 are not V1.0 release blockers. They may include documentation, type drafts, disabled UI prototypes, and route placeholders only.

### V1.0-M5 Source Preview / Evidence Navigation

状态：Post-MVP / dependent on backend contract。

目标：

- source preview shell；
- normalized `DocumentUnit`；
- normalized `EvidenceSpan`；
- precise citation navigation。

### V1.0-M6 Multi-format Ingestion Foundation

状态：Future backend phase。

目标：

- capability manifest；
- JSON/PPT/video/audio partial/full support states；
- no hard-coded frontend format truth。

### V1.0-M7 Assessment Studio Future Shell

状态：Future backend phase。

目标：

- `Question / Assessment / Attempt / MasteryProfile` type drafts；
- route placeholders；
- UI prototype；
- no production mock generation/scoring/mastery。

## 6. P0 Contracts Required Before M2/M3

M0-M1 can begin immediately. M2-M3 require the following contracts:

- `api-adapter-contract.md`;
- `answer-evidence-contract.md`;
- `operation-polling-contract.md`;
- `error-state-model.md`;
- `source-library-information-architecture.md`;
- `v1_0_e2e_smoke_plan.md`.
