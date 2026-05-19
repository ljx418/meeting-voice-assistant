# harnessOS V4.0 Workflow Studio / Low-code UI Development Baseline

文档状态：V4.0 前端低代码平台开发审查基线；当前已完成 Workflow Studio low-code shell refresh 和 V4.0-E Reference Workflow Console integration baseline。  
适用范围：基于 Stitch 原型图 `https://stitch.withgoogle.com/projects/10240451325799222489` 进入 V4.0 Workflow Console / Workflow Studio / low-code UI 的开发规划与审查。  
当前结论：项目已经支撑并实现了一版 V4.0 Workflow Console / low-code UI shell，并通过 component-level + BFF integration E2E 连接 V3.6 runtime fixture；但不能声明 Workflow Studio ready 或 low-code platform complete。

当前进展、阶段状态、核心差距和图形化路线图以 `v4_0_current_gap_analysis.md` 与 `v4_0_current_gap_analysis.drawio` 为最高优先级维护入口。本文只作为 Stitch 原型到 V4.0 UI 开发的补充基线。

## 1. Current Conclusion

当前 harnessOS **已经可以展示基于 Stitch 原型和 PRD v0.2 方向的 V4.0 前端低代码 Workflow Studio Shell**，并已完成 Reference Workflow Console 的 integration baseline：BFF structured routes、V3.6 runtime fixture、BusinessEventBinding、seeded patch diff、approval side-effect、context update、EventBridge refresh truth 与 DTO redaction 均有测试覆盖。

当前可以声明：

```text
V4.0 Workflow Studio page prototype / Shell complete.
V4.0 dev/local Workflow Console integration baseline ready.
```

当前不能声明：

```text
Workflow Studio ready
Low-code platform complete
AgentTalkWindow ready
Production-ready external app support
Distributed workflow engine ready
```

原因是：V3.6 已提供 Workflow Runtime Contract、Pipeline Board API、Patch、Approval、Quality、Business Context、Artifact Lineage 等后端事实源；前端产品层已实现画布优先 shell、节点库、运行观察面板和 Agent preparation shell，但尚未实现真实节点拖入、连线写回、Inspector patch 写回、完整 AgentTalkWindow 或生产级外部接入。

## 2. Current Project Baseline

### 2.1 V3.5 Baseline: Application Adaptation Layer

V3.5 已完成 dev/local Application Adaptation Layer，提供外部 UI / BFF / SDK 接入 harnessOS Core 的能力。

已具备：

- Protocol Schema Registry
- Error Registry
- Capability Token MVP
- Browser Event Bridge
- Python SDK MVP
- TypeScript SDK Core Client
- React Hooks
- Full BFF Template
- Pack / Connector Template
- Embed Contract
- Platform-neutral Reference App

当前意义：

```text
业务 UI 可以通过 BFF / SDK / EventBridge 接入 harnessOS。
```

限制：

```text
不是 production-ready external app support。
不是完整 AgentTalkWindow。
不是完整 Workflow Studio。
```

相关文档：

- `docs/design/V3.5/v3_5_current_gap_analysis.md`
- `docs/design/V3.5/v3_5_completion_evidence_bundle.md`
- `docs/design/V3.5/v3_5_sdk_plan.md`
- `docs/design/V3.5/v3_5_bff_template_plan.md`
- `docs/design/V3.5/v3_5_embed_contract_plan.md`

### 2.2 V3.6 Baseline: Workflow Runtime Contract & Pipeline Operating Model

V3.6 已完成后端 workflow runtime / pipeline operating model，可作为 V4.0 UI 的事实源。

已具备：

- `WorkflowTemplate`
- `WorkflowDraft`
- `WorkflowVersion`
- `WorkflowInstance`
- `Station`
- `StationRun`
- `WorkflowEdge`
- `ArtifactContract`
- `QualityContract`
- `QualityEvaluation`
- `WorkflowPatch`
- `WorkflowContext`
- `BusinessEvent`
- `PipelineBoard`

已实现能力：

- workflow template / draft / version service
- deterministic dummy workflow runtime
- station pre-execution approval point
- artifact contract / lineage binding
- quality evaluation MVP
- pipeline board data API
- business event bridge / workflow context
- safe workflow patch contract
- dummy pipeline E2E
- V3.6/V4.0 preflight hardening

关键 API：

```text
workflow.template.create/get/list/update_draft/publish/archive
workflow.version.get/list
workflow.instance.start/get/list/status/pause/resume/cancel/retry
station.run.get/list
station.output.list
station.rerun
workflow.board.get
quality.evaluation.create/get/list/attach
business.event.emit
workflow.context.get/update
business.event.bind
workflow.patch.propose/diff/apply/reject
artifact.lineage
approval.respond
events.subscribe
```

当前意义：

```text
V4.0 UI 不需要从 mock schema 起步，可以消费 V3.6 API。
```

限制：

```text
不是完整 UI。
不是分布式 workflow engine。
不是生产自动化引擎。
```

相关文档：

- `docs/design/V3.6/v3_6_current_gap_analysis.md`
- `docs/design/V3.6/v3_6_workflow_contract.md`
- `docs/design/V3.6/v3_6_j_completion_note.md`
- `docs/design/V3.6/v3_6_preflight_hardening_note.md`
- `docs/integration/workflow_runtime_contract.md`

### 2.3 Current Frontend Baseline

当前已有传统前端目录：

```text
apps/web/
  index.html
  package.json
  src/App.vue
  src/pages/HomePage.vue
  src/router/index.ts
```

`apps/web` 当前状态：

- Vue 3 + Vite 极简骨架。
- 只有 HomePage。
- 不作为当前 V4.0 Workflow Studio 主实现入口。

当前 V4.0 主实现目录：

```text
apps/workflow-console/
```

`apps/workflow-console` 当前状态：

- React + Vite + TypeScript。
- BFF-only workflow console client。
- 低代码 Workflow Studio Shell：
  - 顶部栏。
  - 左侧「节点库」。
  - ComfyUI-like 底层工作台画布。
  - 右侧默认展开的「Agent 工作流助手」。
  - 节点配置 / Patch Diff tabs。
  - 底部运行观察面板。
- Stitch 最新浅色高保真视觉：
  - 浅色 SaaS 工作台背景。
  - 中央白色点阵无限画布。
  - 蓝紫色主按钮与状态点缀。
  - 白色卡片式节点与清晰连线。
- 画布已支持：
  - 铺满主工作区并位于浮层面板之后。
  - 浅色无限点阵网格背景。
  - VideoStudio 示例多节点工作流。
  - 分镜生成 warning 节点。
  - 背景拖拽平移。
  - 节点拖动。
  - 节点连线。
  - 缩放。
  - 适配画布。
  - 左右折叠后画布扩展。
  - 窄屏下顶部栏保持紧凑，左右面板默认折叠为浮动入口，画布仍是主工作台。
- 已通过 `npm test`、`npm run build` 和 V4.0 Python contract tests。
- `v4_0_workflow_studio_agent_copilot_prd.md` 已作为后续前端体验验收基线，重点验收 Agent 自然语言工作流助手、Patch/Diff 和用户确认机制。

当前限制：

- 节点库拖拽尚未创建 runtime Station。
- 画布节点位置仍是 UI-only transient state。
- 连线展示尚未写回 WorkflowEdge。
- Inspector 字段只读/disabled。
- Patch 面板只展示 proposal/diff/risk，不执行 apply/reject/publish。

另有 Reference App：

```text
examples/reference_app/frontend/
```

当前状态：

- 用于 V3.5 reference app smoke
- 平台中立
- 默认通过 BFF
- 不等同于正式 V4.0 产品前端

重要技术决策点：

```text
V3.5 已实现 TypeScript SDK + React hooks。
apps/web 当前是 Vue。
```

V4.0 前端技术栈决策已经落地：

```text
V4.0 Workflow Studio 主实现采用 React + TypeScript，并放在 apps/workflow-console/。
apps/web 暂不承载 Workflow Studio 主开发。
```

## 3. Stitch Prototype Integration Status

Stitch 原型项目：

```text
https://stitch.withgoogle.com/projects/10240451325799222489
```

当前 MCP 配置状态：

- Stitch MCP 已配置
- API key 已写入 Codex MCP 配置
- 本地需要通过 `127.0.0.1:10808` 代理访问 Stitch API
- 当前会话未热加载 Stitch MCP tools
- 重启 Codex 后应可使用 Stitch MCP 拉取 screen code / image / build site

当前可以做：

```text
Stitch prototype -> V4.0 UI contract mapping
Stitch screen -> frontend page/component breakdown
Stitch HTML/image -> implementation reference
```

当前不能直接跳过：

```text
不能直接把 Stitch 原型当作真实 runtime schema。
不能让 UI mock schema 反向定义 V3.6 workflow contract。
不能新增 UI-only backend bypass。
```

## 4. Target Project Baseline

V4.0 目标不是单纯实现一个页面，而是把 V3.6 workflow runtime 产品化为前端低代码操作台。

目标形态：

```text
V4.0 Workflow Console / Studio
  -> 通过 V3.5 BFF / SDK / EventBridge
  -> 消费 V3.6 Workflow Runtime Contract
  -> 展示、运行、审批、评估、编辑 workflow pipeline
```

目标架构采用 V3.6 完成后的正式七平面基线：

```text
Plane-0 Product UI / Workflow Studio / AgentTalkWindow
  -> Plane-1 Application Adaptation Layer
  -> Plane-2 Workflow Runtime Layer
  -> Plane-3 Harness Core
  -> Plane-4 Runtime Adapter & Governance
  -> Plane-5 Domain Pack / Descriptor Plane
  -> Plane-6 Connector / Tool / Store / Asset Plane
```

其中 V4.0 前端只直接消费 Plane-1 / Plane-2 暴露的协议面，不直接读取 Plane-3 之后的内部 store 或 runtime 对象。此前六块能力域只能作为产品讲解视图，不能替代七平面正式基线。

目标 UI 能力：

- Workflow Console 首页
- Workflow Template / Version 列表
- Pipeline Board
- Station Board
- Artifact Panel
- Quality Panel
- Approval Panel
- Trace Summary Panel
- Business Context Panel
- Patch / Diff / Publish Panel
- Event Stream
- AgentTalkWindow 前置 shell

目标后端消费方式：

```text
只通过 V3.6 API / V3.5 adaptation layer。
不直接读 WorkflowStore。
不直接读 ArtifactRegistry。
不直接调用 Gateway 内部对象。
不新增 UI 专用后端旁路。
```

## 5. Stitch Prototype To V4.0 API Mapping

| UI 区域 | 后端 API |
|---|---|
| Workflow list | `workflow.template.list` |
| Workflow detail | `workflow.template.get` |
| Version selector | `workflow.version.list/get` |
| Start workflow | `workflow.instance.start`，仅 dev/demo bootstrap；普通 UI 不默认暴露 |
| Instance status | `workflow.instance.status` |
| Pipeline board | `workflow.board.get` |
| Station run list | `station.run.list` |
| Station output | `station.output.list` |
| Artifact detail | `artifact.read_metadata` |
| Artifact lineage | `artifact.lineage` |
| Approval panel | `approval.respond` |
| Quality panel | `quality.evaluation.list/get/create/attach` |
| Business context | `workflow.context.get/update` |
| Business event action | `business.event.emit` |
| Patch proposal | `workflow.patch.propose` |
| Patch diff | `workflow.patch.diff` |
| Apply patch | `workflow.patch.apply`，当前 shell 不暴露 |
| Reject patch | `workflow.patch.reject`，当前 shell 不暴露 |
| Publish version | `workflow.template.publish`，当前 shell 仅 disabled 占位 |
| Event stream | `events.subscribe` via BFF EventBridge proxy；UI 不直接调用 `/v1/events/subscribe` |
| Debug trace summary | `trace.list/get` or board redacted trace summary |

## 6. V4.0 Development Plan

### V4.0-0: Baseline & UI Contract Sync

目标：把 Stitch 原型图转成 V4.0 UI contract，不写大规模业务代码。

交付物：

```text
docs/design/V4.0/v4_0_ui_contract_mapping.md
docs/design/V4.0/v4_0_stitch_prototype_mapping.md
docs/design/V4.0/v4_0_frontend_development_plan.md
docs/design/V4.0/v4_0_acceptance_plan.md
docs/design/V4.0/v4_0_current_gap_analysis.md
```

任务：

- 拉取 Stitch 原型 screen code / image
- 拆解页面结构
- 定义 component map
- 定义 API map
- 明确 UI state model
- 明确哪些是 read-only MVP，哪些属于 editing MVP
- 确认前端技术栈：React or Vue
- 建立 mock-to-real contract check
- 明确 No False Green 边界

验收标准：

- 每个 Stitch 页面都有对应 UI contract
- 每个按钮 / 面板 / 状态都有 API 映射或明确标记 future
- 不引入 UI-only backend API
- 不修改 V3.6 runtime contract
- V4.0 不声明 Studio ready

### V4.0-A: Workflow Console Read-only MVP / Canvas Shell

目标：实现只读流水线控制台，先把后端事实源展示出来，并以画布优先的 Workflow Studio Shell 承载。

功能：

- workflow instance status
- pipeline board
- station run status
- job summary
- artifact summary
- approval summary
- quality summary
- trace summary
- event stream
- left node library shell
- draggable workflow canvas shell
- right inspector shell
- bottom run panel

API：

```text
workflow.board.get
workflow.instance.status
station.output.list
artifact.read_metadata
artifact.lineage
events.subscribe
```

验收标准：

- 可以展示完整 dummy pipeline state
- 画布背景可拖拽平移。
- 工作流节点可拖动。
- 画布缩放与适配视图可用。
- 左右面板折叠后画布面积扩大。
- 画布是工作台的一等公民，不是嵌在三栏布局中的中间卡片。
- 窄屏 viewport 下不能把顶部栏退化成纵向表单，也不能让侧栏覆盖整个画布。
- 不直接读 store
- 不新增后端旁路
- 不修改 workflow runtime
- board 数据 redacted
- event stream 可更新 UI
- scope isolation 生效

### V4.0-B: Workflow Editing MVP

目标：基于 V3.6 WorkflowPatch 实现受控编辑。当前 shell 阶段只展示 propose/diff/risk，不暴露 apply/reject/publish 执行动作。

功能：

- propose patch
- view diff
- show risk flags
- prevent high-risk direct apply where governance forbids

Future editing functions:

- apply patch
- reject patch
- publish new version

API：

```text
workflow.patch.propose
workflow.patch.diff
workflow.version.get/list
```

Future editing API:

```text
workflow.patch.apply
workflow.patch.reject
workflow.template.publish
```

验收标准：

- current shell only shows diff/risk and does not apply patch
- future patch apply 只修改 draft
- published version 不被静默修改
- agent 只能 propose/diff
- apply 后 draft revision 递增
- publish 后生成新 version
- V1 completed instance 不受 V2 patch 影响
- high-risk patch 按 governance 策略拒绝或提示

### V4.0-C: AgentTalkWindow Preparation

目标：实现 AgentTalkWindow 前置 shell，但不声明完整 AgentTalkWindow。

功能：

- EmbedBootstrap
- event stream display
- approval-required state
- patch proposal card
- artifact card
- quality summary card
- read-only context summary

API：

```text
events.subscribe
workflow.patch.propose
workflow.patch.diff
workflow.context.get
```

Future operation API:

```text
approval.respond
business.event.emit
workflow.context.update
```

验收标准：

- 不实现完整 AgentTalkWindow 状态机
- 不绕过 BFF / SDK / EventBridge
- 不持有长期广权限 token
- 不直接调用 Core internal
- Agent 不自动 apply patch / publish version / respond approval / update context / emit business event

### V4.0-D: Quality / Approval / Context Panels

目标：产品化质量评估、审批、上下文操作面板。

功能：

- Quality evaluation list/detail
- Manual quality input
- Approval approve/reject via `approval.respond`
- Context read/update
- Business event emit
- Redacted trace summary

API：

```text
quality.evaluation.*
approval.respond
workflow.context.*
business.event.*
trace.list/get
```

验收标准：

- failed quality 不直接修改 workflow state
- approval.respond 是唯一 workflow-bound continuation path
- context update 只能写 `context.business`
- 不修改 board contract
- 所有敏感信息 redacted

### V4.0-E: Reference Workflow Console E2E

目标：用平台中立 workflow 完成 UI + BFF + SDK + V3.6 runtime 端到端验收。

E2E 流程：

```text
1. list workflow template
2. publish or select version
3. start workflow instance
4. view running board
5. observe station A/B/C
6. inspect artifact lineage
7. handle approval.required
8. create/list quality evaluation
9. update business context
10. propose patch
11. view diff
12. apply patch
13. publish V2
14. start V2 instance
15. verify V1 immutable
```

验收标准：

- 不依赖 Meeting / Knowledge / Video
- 不依赖 data_service / voice_service / funasr
- 不调用 external MCP
- 不使用 mock-only backend state
- 不跨 scope 泄露数据
- V3.5 / V3.6 focused tests 继续绿灯
- frontend build/test 通过

## 7. Recommended Frontend Technical Route

### Option A: New React Frontend

优点：

- 可直接复用 V3.5 TS SDK / React hooks
- 更适合承接 Stitch 生成的 HTML/React 风格代码
- 更快做 Workflow Console MVP

缺点：

- 与当前 `apps/web` Vue 骨架不一致
- 需要建立新的 frontend app 或迁移 apps/web

建议目录：

```text
apps/workflow-console/
  package.json
  src/
    app/
    components/
    features/workflows/
    features/board/
    features/approvals/
    features/quality/
    features/patches/
    features/context/
```

### Option B: Continue Vue

优点：

- 延续 `apps/web`
- 保持当前仓库前端骨架

缺点：

- 现有 React hooks 不能直接复用
- 需要新增 Vue composables
- Stitch 代码实现可能需要转换

建议目录：

```text
apps/web/src/
  pages/WorkflowConsole.vue
  components/workflow/
  composables/useWorkflowBoard.ts
  composables/useWorkflowEvents.ts
```

### Recommendation

如果目标是快速基于 Stitch 原型落地，推荐：

```text
新建 React workflow-console app，复用 TS SDK / React hooks。
apps/web 暂时保留为历史 Vue shell。
```

## 8. Risks

### 8.1 Prototype Pollutes Protocol

风险：

```text
Stitch UI 里可能有 mock 字段或临时交互，不应反向定义 runtime schema。
```

控制：

```text
所有 UI 数据必须映射到 V3.6 API。
不能新增 UI-only backend bypass。
```

### 8.2 Workflow Studio Scope Too Large

风险：

```text
直接做完整低代码平台会过重，容易绕过 V3.6 backend contract。
```

控制：

```text
先做 read-only console，再做 patch editing。
```

### 8.3 React / Vue Stack Mismatch

风险：

```text
V3.5 hooks 是 React，apps/web 是 Vue。
```

控制：

```text
V4.0-0 必须先冻结 frontend stack。
```

### 8.4 EventSource / Auth

风险：

```text
浏览器原生 EventSource 不能设置 Authorization header。
```

控制：

```text
生产路径使用 BFF proxy。
dev/direct 才允许受限 token。
```

### 8.5 Stitch MCP Network Dependency

风险：

```text
Stitch API 需要本机代理，当前通过 127.0.0.1:10808 才可访问。
```

控制：

```text
将 Stitch 作为设计输入工具，不作为 runtime dependency。
```

## 9. Test Plan

### V4.0-0

- contract mapping completeness test
- no UI-only API names test
- V4.0 docs protocol alignment test
- Stitch prototype asset import smoke

### V4.0-A

- Workflow Console render board test
- EventBridge UI update test
- board redaction test
- scope isolation UI test
- no direct store import test

### V4.0-B

- patch propose/diff/apply UI test
- high-risk patch guard test
- publish V2 test
- V1 immutable test

### V4.0-C

- embed bootstrap test
- event card render test
- approval required state test
- no token leak test

### V4.0-D

- quality panel test
- approval.respond panel test
- context update test
- business event emit test

### V4.0-E

- full UI + BFF + SDK + V3.6 dummy pipeline E2E
- frontend build
- V3.5 focused regression
- V3.6 focused regression
- full pytest

## 10. Exit Criteria

V4.0 完成前，至少必须满足：

```text
1. UI 只消费 V3.6 API / V3.5 adaptation layer。
2. Workflow Console 可展示完整 dummy pipeline。
3. Station/job/artifact/approval/quality/trace summary 可重建。
4. EventBridge 可驱动 UI 更新。
5. WorkflowPatch 可完成 propose/diff/apply/publish。
6. Approval 只能通过 approval.respond。
7. Context update 只能写 context.business。
8. Artifact lineage 可在 UI 中查看。
9. 所有敏感字段 redacted。
10. 不依赖 Meeting / Knowledge / Video / external MCP。
11. V3.5/V3.6 回归继续绿灯。
12. 前端 build/test 通过。
```

通过后可声明：

```text
V4.0 Workflow Console / Studio MVP ready at dev/local level.
```

仍不能声明：

```text
Production-ready low-code platform
Enterprise Workflow Studio
Complete AgentTalkWindow
Distributed workflow engine
Production external app support
```

## 11. Recommended Next Step

建议下一步先执行：

```text
V4.0-0 Baseline & UI Contract Sync
```

第一批任务：

1. 用 Stitch MCP 拉取项目 `10240451325799222489` 的 screens。
2. 生成 `v4_0_stitch_prototype_mapping.md`。
3. 为每个 screen 建立：
   - 页面用途
   - 组件清单
   - 状态清单
   - 事件清单
   - API 映射
   - 不可实现 / future 标记
4. 决定 React / Vue 技术路线。
5. 输出 V4.0-A 只读 Workflow Console MVP 的实现切片。
