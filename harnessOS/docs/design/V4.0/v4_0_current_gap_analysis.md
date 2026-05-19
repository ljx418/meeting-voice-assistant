# V4.0 Current Gap Analysis

文档状态：V4.0-E complete at integration baseline；V3.6 complete baseline 与 V3.6/V4.0 preflight hardening 已完成，Workflow Console read-only MVP、AgentTalkWindow preparation shell、低代码 Workflow Studio Shell、真实 BFF read/event data bridge、Quality / Approval / Context operation panels，以及 Reference Workflow Console component-level + BFF integration E2E 已完成。  
配套图：`v4_0_current_gap_analysis.drawio`。

本文与 `v4_0_current_gap_analysis.drawio` 是 V4.0 后续规划、验收和与用户交互时的核心维护文件。两者必须同步更新：本文承载文字合同，drawio 承载同一套架构演进、差距矩阵、阶段路线图和 V4.0 gate。

## 1. 文档定位

本文只描述 V4.0 **Workflow Console / Workflow Studio / AgentTalkWindow 前置产品层** 的当前差距、目标架构和阶段影响范围。V3.5 与 V3.6 已完成项只作为 V4.0 的起点基线，不再进入本文主叙事作为待办。

V4.0 不是继续重构 Core，也不是重新实现 V3.6 Workflow Runtime。它要补的是把已经冻结的后端事实源产品化为可视化、可交互、可嵌入的工作流操作面：

```text
V3.5 Application Adaptation Layer
  -> V3.6 Workflow Runtime Layer
  -> V4.0 Workflow Console / Studio / AgentTalkWindow
```

因此，V4.0 gap 不应被描述成以下几类问题：

- 不是 V3.5 SDK / BFF / hooks 的继续堆叠。
- 不是 V3.6 runtime / board / patch / quality 的重新实现。
- 不是 Meeting / Knowledge / Video 真实业务迁移。
- 不是 Core 大重构。
- 不是 production multi-tenant control plane。
- 不是完整分布式 workflow engine。

V4.0 要回答的问题是：

> V3.6 已经把工作流变成可运行、可追踪、可审批、可评价、可修改的一等对象后，产品 UI 如何在不绕过协议、不固化 mock schema 的前提下，把这些能力变成 Workflow Console、Workflow Studio 和 AgentTalkWindow 前置体验。

## 2. 当前状态

当前 harnessOS 已冻结以下基线：

- V3.5 complete at dev/local Application Adaptation Layer level。
- V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development。
- V3.6/V4.0 preflight hardening complete。

当前事实：

- V3.5 已完成 SDK、BFF、React hooks、EventBridge、Embed Contract、Pack/Connector template、Reference App 和 capability token / scope guard。
- V3.6 已完成 WorkflowTemplate / WorkflowVersion / WorkflowDraft、WorkflowInstance、Station、StationRun、ArtifactContract、QualityEvaluation、Pipeline Board API、Business Event Bridge / Workflow Context、WorkflowPatch 和平台中立 Dummy Pipeline E2E。
- V3.6-J 已验证 runtime E2E 与 editing E2E 分离：V1 completed instance 与 V1 version snapshot 不受 V2 patch/publish 影响，patched V2 可被 runtime 消费。
- V3.6 preflight 已补齐 session/memory scope guard、workflow-bound legacy approval guard、high-risk workflow patch governance、Board/status job scope double-check、business EventBridge channel permissions、EventBridge follow mode、subscription origin binding、business event atomic idempotency、duplicate binding guard、platform startup neutrality 和 V4.0 protocol naming。
- 当前回归证据来自 V3.6 gap 文档：V3.6 focused tests `86 passed`；V3.5 focused tests `146 passed`；full pytest `443 passed, 3 skipped`；TypeScript SDK `23 passed`；drawio XML validation passed。
- V4.0-0 已新增 UI contract map、mock-to-real checklist、event contract map、frontend stack decision 和 Stitch prototype mapping。
- V4.0-A2 已补齐 Real Data Bridge：内置 `/bff/*` structured routes、BFF frontend DTO redaction、instance-scoped station/artifact ownership guard、BFF EventBridge proxy、真实 V3.6 dummy pipeline fixture 到 board/status/output/artifact metadata/lineage 的集成测试。

当前 V4.0 产品层实现事实：

- V4.0-A 已新增 `apps/workflow-console/` React + Vite + TypeScript 控制台。
- Workflow Console 通过 BFF structured client 封装 `/bff/*` 路径，不直接调用 `/v1/rpc` 或 `/v1/events/subscribe`。
- Console 默认进入 real mode，通过 `useWorkflowConsoleData` 消费 BFF read/event DTO；只有显式 `VITE_HARNESSOS_DEMO_MODE=true` 时才使用 demo fixture，并显示 `Demo / Fixture` 标签。
- Console 可展示真实 BFF board/status/station/artifact/approval/quality/trace/event feed，并通过 BFF integration tests 与 render tests 验证敏感字段 redaction。
- 页面已从普通 Dashboard 改造为画布优先的低代码 Workflow Studio Shell：顶部栏、左侧「节点库」、中央无限拖拽画布、右侧「节点配置 / Agent 助手」、底部运行观察面板。
- Stitch 原型视觉已同步为最新浅色高保真工作台：浅色 SaaS 背景、蓝紫色点缀、白色节点卡片、清晰连线和浅色点阵无限画布。
- 画布层级已调整为 ComfyUI-like workbench：画布铺满主工作区并作为底层一等公民，节点库、Agent 工作流助手 / Inspector、画布工具条和底部运行面板都是浮在画布上的可折叠操作面板。
- 中央画布已具备浅色无限点阵网格背景、VideoStudio 多节点工作流、分镜生成 warning 节点、节点连线、背景拖拽平移、节点拖拽、缩放、适配画布和左右折叠后画布扩展。
- 右侧区域已从 Inspector 优先改为 Agent 工作流助手优先：展示自然语言生成工作流、优化分镜节点、三张建议卡片、Patch Proposal / Diff 和“等待用户确认 / 应用到草稿（后续阶段）”语义。
- 窄屏响应式已修正：顶部栏保持紧凑，左右面板默认折叠为浮动入口，画布继续作为主要工作台可见。
- 已有 Workflow Editing / Patch preparation shell：patch proposal/diff 展示、高风险 patch 风险展示和禁止静默 apply；当前 UI 不暴露 apply/reject/publish 执行动作。
- 已有 AgentTalkWindow preparation shell：fixture-first event timeline、patch proposal/diff 摘要、approval.required notice、只读 context.business summary 和 embed boundary tests。
- 已有 V4.0-D operation panels：QualityPanel 只读展示 `quality.evaluation.get/list` DTO；ApprovalPanel 通过用户显式点击调用 workflow-bound `approval.respond`；ContextPanel 通过 path-based set 受控写入 `context.business` 并可发送具体 `business.*` event。

当前仍未完成：

- 没有完整 Workflow Studio 可视化编辑器：尚未实现真实节点拖入、连线落库、Inspector 写回、Patch apply/publish 端到端。
- 没有完整 AgentTalkWindow 状态机。
- UI 已通过 BFF 消费 V3.6 Board / status / output / artifact metadata / lineage 的真实读链路；Approval respond、context update 和 business event 已进入 V4.0-D operation panels；Patch apply/publish 与 Quality create/attach 仍不暴露。
- 已完成 V4.0 Reference Workflow Console component-level + BFF integration E2E；尚未引入 Playwright/Cypress 浏览器级 smoke。
- 没有 production-ready external app support、OAuth/SSO、多租户控制台或分布式调度。

## 3. 架构演进口径

V4.0 必须沿用 V3.6 结束后的 **七平面正式基线**。此前“六大平面”只允许作为产品能力聚合视图，不能替代正式架构，也不能用于新增 UI 专用后端旁路。

```text
Plane-0 Product UI / Workflow Studio / AgentTalkWindow
  Workflow Canvas / Station Board / Artifact Board / Quality Panel / Approval Panel / Context Panel

Plane-1 Application Adaptation Layer
  V3.5 SDK / BFF / hooks / EventBridge / Embed Contract

Plane-2 Workflow Runtime Layer
  V3.6 workflow runtime RPC / board / patch / quality / context APIs
  WorkflowTemplate / WorkflowInstance / Station / StationRun / Board / Patch / Quality / Context

Plane-3 Harness Core
  Session / Turn / Job / Artifact / Approval / Trace / Policy / Scope / Memory / Retry

Plane-4 Runtime Adapter & Governance
  runtime adapters / governed execution / policy / approval / secret hygiene / trace

Plane-5 Domain Pack / Descriptor Plane
  app descriptors / workflow descriptors / agent descriptors / skill descriptors / quality descriptors
  domain packs / policy bundles / artifact kinds

Plane-6 Connector / Tool / Store / Asset Plane
  MCP / stdio / HTTP connectors / model APIs / media engines / search / storage / external asset services
```

V4.0 正式调用链应为：

```text
Workflow Console / Studio / AgentTalkWindow
  -> V3.5 SDK / BFF / hooks / EventBridge / Embed
  -> V3.6 Workflow Runtime APIs
  -> Core Job / Artifact / Approval / Trace / Policy
  -> Pack / Connector
```

禁止的新形态：

```text
Workflow Studio UI
  -> direct Core Store
  -> hidden workflow-specific backend bypass
  -> mock schema promoted to runtime contract
```

## 4. 目标状态

V4.0 完成后，harnessOS 应具备以下目标状态：

- Workflow Console 可只读展示完整 pipeline state：workflow instance、stations、station runs、jobs、artifacts、approvals、quality evaluations、trace summary 和 current station。
- Workflow Studio 可通过受控 patch 合同编辑 draft，并通过 `workflow.template.publish` 发布新 version。
- AgentTalkWindow 前置 shell 可围绕当前 workflow instance 展示事件、审批、质量、patch 建议和上下文变更，但不声明完整 AgentTalkWindow。
- Quality / Approval / Context Panels 可消费 V3.6 的 QualityEvaluation、`approval.respond`、Business Event / Workflow Context，不写入 UI 私有状态到 runtime 内部对象。
- Reference Workflow Console E2E 可证明 UI + BFF + SDK/hooks + V3.6 runtime 的平台中立链路，不依赖 Meeting / Knowledge / Video / external MCP。
- V4.0 UI 只消费 Plane-1 / Plane-2 协议面，不直接读取 Core Store，不绕过 scope/capability/governance。

## 5. 核心差距

| 差距 | 当前状态 | V4.0 目标 | 阶段 |
| --- | --- | --- | --- |
| V4.0 baseline | V3.5/V3.6 baseline 已冻结；V4.0 gap 文件对、contract map、No False Green 边界和 mock-to-real 检查已补齐。 | 进入 V4.0-A 前保持 gap md/drawio、UI contract map、event map 与测试同步。 | V4.0-0 已完成 |
| Workflow Console / Studio shell | V4.0-A/C 之上已实现 React/Vite 低代码 Workflow Studio Shell：节点库、Stitch 最新浅色高保真视觉、ComfyUI-like 底层工作台画布、VideoStudio 多节点画布、分镜 warning、Agent 工作流助手、Patch/Diff 用户确认、Inspector、底部运行面板、redaction tests；V4.0-A2 已接真实 BFF read data。 | 后续实现节点拖入、连线编辑、Inspector patch 写回。 | V4.0-A2 complete |
| Live event UI | BFF EventBridge proxy 已支持 SSE id/event/data、Last-Event-ID/cursor、auth failure precheck、upstream token hiding；UI 事件只触发 refresh / 展示，不从 payload 自建 runtime state；quality live event 仍非出门条件。 | 后续把更多操作面板与事件刷新联动，但仍以 `workflow.board.get` / `workflow.instance.status` 为事实源。 | V4.0-A2 complete |
| Workflow editing UI | 当前页面只展示 patch proposal/diff 和风险提示，不暴露 apply/reject/publish 动作；保持 C 阶段 preparation 边界。 | 后续在 V4.0-D/E 或独立 editing phase 中接真实 BFF E2E，并扩展为完整 Studio 画布编辑。 | Shell 已完成；真实编辑待后续 |
| Agent editing boundary | V4.0-C 已实现 AgentTalk preparation shell，只展示 patch propose/diff，不 apply/reject/publish。 | 后续如需完整 AgentTalkWindow，需要新的状态机与真实 BFF/runtime E2E。 | V4.0-C 已完成 |
| Quality / Approval / Context panels | V3.6 后端能力已完成；尚无产品化面板。 | 面板消费 QualityEvaluation、approval.respond、workflow.context.*、business.event.*。 | V4.0-D |
| Reference console E2E | 已完成平台中立 runtime fixture、BusinessEventBinding、seeded patch diff、approval side-effect、context update、EventBridge refresh truth、DTO redaction、scope/ownership guard 和 frontend real DTO render tests。 | 下一步如需升级声明，需要补 browser-level smoke 或完整浏览器自动化。 | V4.0-E complete at integration baseline |
| Production readiness | V3.5/V3.6 均为 dev/local baseline。 | V4.0-E 后仍只能声明 dev/local Workflow Console baseline，不能声明 production-ready。 | 全阶段 |

## 6. 开发计划摘要

### 6.1 当前开发阶段

当前项目处于 **V4.0-E complete at integration baseline**。V3.6 后端 gate 已完成，V4.0 已有画布优先 Workflow Studio Shell、真实 BFF read/event data bridge、Patch preparation shell、AgentTalkWindow preparation shell、Quality / Approval / Context 操作面板，以及平台中立 Reference Workflow Console component-level + BFF integration E2E。由于尚未补 Playwright/Cypress 浏览器级 smoke，当前只声明 integration baseline，不声明完整 Workflow Studio ready。

当前已经完成的是：

- V3.5 Application Adaptation Layer 已冻结。
- V3.6 Workflow Runtime Contract & Pipeline Operating Model 已冻结。
- V3.6/V4.0 preflight hardening 已完成。
- V4.0 正式七平面目标架构已同步。
- Stitch 原型相关的 V4.0 low-code baseline 已迁移到 `docs/design/V4.0/`。
- 本文和同名 drawio 被建立为 V4.0 后续最高优先级维护文件。
- V4.0 UI contract map、mock-to-real checklist、event contract map、frontend stack decision、Stitch prototype mapping 已建立。
- V4.0-0 文档对齐测试与前端防绕过扫描测试已建立并通过。
- `apps/workflow-console/` 已建立，包含 React/Vite app、BFF-only client、画布优先的低代码 Workflow Studio 页面、read-only station board、artifact/approval/quality/trace/event panels 和 redaction render tests。
- `apps/api/routers/bff.py` 已新增 V4.0-A2 BFF structured routes：`/bff/workflows`、`/bff/instances`、`/bff/instances/{id}/status`、`/bff/instances/{id}/board`、station output、artifact metadata/lineage 和 `/bff/events/subscribe`。
- `apps/workflow-console/src/hooks/useWorkflowConsoleData.ts` 已新增 real data hook：默认 real mode，显式 demo/dev mode 才使用 fixture；real mode API error 显示 error state，不自动 fallback demoData。
- `apps/workflow-console/` 已新增 Stitch 最新浅色高保真 + ComfyUI-like 工作台画布：画布铺满主区域作为底层，面板浮在其上；画布底层可平移，VideoStudio 工作流节点可拖动，连线随节点位置更新，左右面板折叠后画布扩展。
- `apps/workflow-console/` 已按 `v4_0_workflow_studio_agent_copilot_prd.md` 增强 Agent 工作流助手：自然语言生成工作流示例、自然语言优化节点示例、三张建议卡片、Patch Proposal / Diff 和用户确认边界。
- `apps/workflow-console/` 已新增 Patch preparation panel，展示 patch diff、risk_flags、requires_approval；当前不暴露 apply/reject/publish 执行动作，高风险 patch 只能展示风险，不能静默 apply。
- `apps/workflow-console/` 已新增 AgentTalk preparation shell，展示 demo/trace_only source 标识事件、patch 建议、approval notice、只读 context.business summary 和非突变 allowed_actions。
- `apps/api/routers/bff.py` 已新增 V4.0-D operation panel structured routes：instance-scoped quality list/get、approval list/respond、context get/update、business event emit；所有 response 转为 redacted frontend DTO，不透传 raw Gateway response。
- `apps/workflow-console/` 已新增 QualityPanel、ApprovalPanel、ContextPanel，并接入 `useWorkflowConsoleData` real hook；Quality 保持 read-only，approval.respond 只能由用户显式点击触发，context update 只能写 `business.*`。
- `tests/v4_0_reference_support.py` 已新增平台中立 V4.0-E fixture：生成 WorkflowTemplate / WorkflowVersion / WorkflowInstance / StationRun / Job / Artifact / Approval / QualityEvaluation / WorkflowContext / BusinessEventBinding / seeded WorkflowPatch。
- V4.0-E 已验证：`business.event.emit -> BusinessEventBinding -> context.business` 更新；seeded patch diff 来自 V3.6 patch repository；workflow-bound `approval.respond` 会推动 waiting_approval station 继续；EventBridge 事件只触发 refresh，不采信 payload 中伪造状态。
- V4.0-E 定向验证已通过：`tests/test_v4_0_*.py` 47 passed；`apps/workflow-console npm test` 17 passed；`apps/workflow-console npm run build` passed；full pytest 488 passed, 3 skipped。

当前需要继续推进的是：

- V4.0-E：Reference Workflow Console E2E。

### 6.2 阶段路线图

| 阶段 | 目标 | 主要交付 | 完成后可声明 |
| --- | --- | --- | --- |
| V4.0-0 | Baseline & UI Contract Sync | V4.0 gap 文件对、contract map、mock-to-real 检查、No False Green 边界、Stitch 原型到 V3.6 API 映射。 | 已完成：V4.0 implementation baseline and UI contract map ready。 |
| V4.0-A | Workflow Console Read-only MVP | Station Board、Artifact Board、Approval/Quality/Trace summary，只读消费 board/status/output/EventBridge。 | 已完成：Workflow Console read-only MVP ready。 |
| V4.0-A2 | Real Data Bridge | BFF structured routes、frontend DTO redaction、真实 V3.6 dummy pipeline fixture 到 UI data hook、BFF EventBridge proxy。 | 已完成：Workflow Studio shell connected to real BFF read/event data。 |
| V4.0-B | Workflow Editing MVP | Patch proposal、diff view、draft apply、publish flow；高风险 patch 不绕过 governance。 | 重新收窄为 preparation shell：当前 UI 只展示 propose/diff/risk，不暴露 apply/reject/publish。 |
| V4.0-C | AgentTalkWindow Preparation | 基于 Embed Contract / EventBridge / approval / context / patch 的前置 shell。 | 已完成：AgentTalkWindow preparation shell ready。 |
| V4.0-D | Quality / Approval / Context Panels | QualityEvaluation panel、approval.respond panel、workflow context panel、business event display。 | 已完成：Quality read-only, workflow approval response, and business context operation panels ready for dev/local Workflow Studio。 |
| V4.0-E | Reference Workflow Console E2E | 平台中立 workflow console E2E；UI + BFF + SDK/hooks + V3.6 runtime 全链路。 | 已完成 component-level + BFF integration E2E；未完成 browser smoke，因此声明为 integration baseline。 |

### 6.3 V4.0-0 具体计划

V4.0-0 要完成的是产品层开发前的合同同步，不是 UI 功能实现。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| 核心维护文件 | `v4_0_current_gap_analysis.md` 与同名 drawio 必须同步。 | 已完成。 |
| Contract map | 明确 Stitch / Workflow Studio 原型中的每个区域消费哪个 V3.6 API。 | 已完成，见 `v4_0_ui_contract_map.md` 和 `v4_0_stitch_prototype_mapping.md`。 |
| Mock-to-real check | 所有 mock schema 必须标注对应真实 API 或保留为 UI-only transient state。 | 已完成，见 `v4_0_mock_to_real_contract_checklist.md`。 |
| Seven-plane baseline | 所有 V4.0 文档和图必须使用七平面正式基线。 | 已同步，需持续维护。 |
| No bypass rule | UI 不得直接读 Core Store，不得新增 UI 专用后端旁路。 | 已写入文档并由测试锁定。 |
| Test entry | 新增 V4.0 contract doc alignment / frontend source scan / no direct Core calls 测试。 | 已完成。 |

V4.0-0 完成后只能声明：

```text
V4.0-0 complete: V4.0 implementation baseline and UI contract map ready.
```

不能声明：

```text
Workflow Console ready
Workflow Studio ready
AgentTalkWindow ready
V4.0 complete
production-ready external app support
```

### 6.4 V4.0-A 具体计划

V4.0-A 要完成的是只读 Workflow Console MVP。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Board view | 使用 `workflow.board.get` 展示完整 pipeline summary。 | 已以 demo board read model 落地，并在低代码画布节点中展示。 |
| Instance status | 使用 `workflow.instance.status` 展示运行状态、current station 和统计。 | 已以 status header/counters 落地。 |
| Station output | 使用 `station.output.list` 展示 station output artifacts。 | 已以 station output/artifact panel 和节点卡片输出入口落地。 |
| EventBridge | 使用 BFF / hooks 订阅 workflow runtime events，刷新只读 console。 | 已建立 BFF EventSource client 与 event feed；当前为 read-only demo feed。 |
| Redaction | UI 不展示 raw trace payload、raw artifact content、token 或 Authorization。 | 已有 render tests 覆盖。 |
| No mutation | A 阶段不实现 patch apply、approval respond 或 context update。 | 已由 source scan / read-only tests 锁定。 |
| Demo bootstrap | `workflow.instance.start` 只允许 explicit dev/demo fixture；普通 Console UI 选择已有 instance。 | 已由 source scan 锁定，普通 UI 不调用。 |

V4.0-A 完成后只能声明：

```text
V4.0-A complete: Workflow Console read-only MVP ready.
```

不能声明：

```text
Workflow editing ready
AgentTalkWindow ready
V4.0 complete
```

### 6.5 V4.0-B 具体计划

V4.0-B 要完成的是受控 Workflow Editing MVP。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Patch proposal | 使用 `workflow.patch.propose` 生成 patch record。 | 已通过 BFF structured route shell 和 demo proposal 落地；当前以 preparation 展示为主。 |
| Diff view | 使用 `workflow.patch.diff` 展示 redacted summary、risk_flags、requires_approval。 | 已完成。 |
| Apply | 使用 `workflow.patch.apply` 只修改 draft。 | 当前页面不暴露 apply；真实 BFF E2E 留到后续 editing/operation phase。 |
| Publish | 使用 `workflow.template.publish` 发布新 version。 | 当前顶部保留 disabled 占位；真实 BFF E2E 留到后续 editing/operation phase。 |
| High-risk patch | `requires_approval=true` patch 当前必须被后端拒绝直接 apply，UI 只能展示风险或进入后续正式 approval flow。 | 已完成：高风险 patch disabled apply，并展示 risk_flags。 |
| No published mutation | UI 不得直接修改 WorkflowVersion.snapshot。 | 已由 source scan / editing tests 锁定。 |

当前页面完成后只能声明：

```text
V4.0 Workflow Studio page prototype / Shell complete.
```

不能声明：

```text
complete Workflow Studio ready
AgentTalkWindow ready
V4.0 complete
```

### 6.6 V4.0-C 具体计划

V4.0-C 要完成的是 AgentTalkWindow 前置 shell，不是完整 AgentTalkWindow。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Embed bootstrap | 复用 V3.5 EmbedDefinition / EmbedBootstrap 边界。 | 已完成：EmbedDefinition 不含 token/runtime URL；EmbedBootstrap 仅含 BFF-local `bff_eventsource_url`。 |
| Event surface | 展示 workflow events、approval.required、business/context/patch events。 | 已完成：事件带 `live/demo/trace_only` source；`quality.evaluated` 保持 trace-only。 |
| Agent proposal | Agent 只能 propose/diff patch，不得 apply。 | 已完成：AgentPatchProposalCard 只展示生成建议 / 查看 Diff / 前往编辑面板。 |
| Approval continuation | C 阶段只展示 approval.required notice，不调用 `approval.respond`。 | 已完成；真正 approve/reject 留到 V4.0-D。 |
| Context summary | C 阶段只读展示 redacted `context.business`。 | 已完成；`workflow.context.update` / `business.event.emit` 留到 V4.0-D。 |
| No workflow state machine | C 阶段不实现完整 AgentTalkWindow 状态机。 | 已由 source scan / render tests 锁定。 |

V4.0-C 完成后只能声明：

```text
V4.0-C complete: AgentTalkWindow preparation shell ready.
```

不能声明：

```text
complete AgentTalkWindow ready
Workflow Studio ready
V4.0 complete
```

### 6.7 V4.0-D 具体计划

V4.0-D 要完成的是 workflow operations panels。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Quality panel | 消费 `quality.evaluation.get/list` 和 board quality summary。 | 已完成：read-only panel，不调用 `quality.evaluation.create/attach`。 |
| Approval panel | 展示 pending approval，并通过 `approval.respond` 决策。 | 已完成：只允许显式用户点击；inactive approval disabled；不暴露 legacy `approval.approve/reject`。 |
| Context panel | 消费 `workflow.context.get/update`，只写 `context.business`。 | 已完成：path-based set，拒绝 system/runtime/status/approval 写入，支持 expected_revision。 |
| Business event panel | 使用 `business.event.emit` / EventBridge 展示上下文变更。 | 已完成：只接受具体 `business.*`，支持 idempotency，事件只触发刷新，不构造 runtime truth。 |
| Trace summary | 只展示 redacted trace summary，不显示 raw trace payload。 | 已完成：BFF DTO 和 render tests 锁定 token/raw payload redaction。 |

V4.0-D 完成后只能声明：

```text
V4.0-D complete: Quality read-only, workflow approval response, and business context operation panels ready for dev/local Workflow Studio.
```

不能声明：

```text
V4.0 complete
production-ready workflow automation
```

### 6.8 V4.0-E 具体计划

V4.0-E 是 V4.0 dev/local 出门 E2E，不是 production readiness。当前已完成 component-level + BFF integration E2E；因为未引入 Playwright/Cypress browser smoke，本阶段出门声明降级为 integration baseline。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Reference workflow console | 使用平台中立 workflow，不依赖 Meeting / Knowledge / Video / external MCP。 | 已完成：V4.0-E fixture 基于 V3.6 dummy pipeline 和 runtime repository，不依赖业务 pack 或 external MCP。 |
| UI + BFF + SDK/hooks | 前端默认走 BFF structured routes / hooks，不直接调用 Core Store。 | 已完成：BFF integration tests 覆盖 structured routes；frontend source scan 锁定 no direct `/v1/rpc` / `/v1/events/subscribe`。 |
| Runtime read-only | Console 能展示 V3.6 board/status/output。 | 已完成：BFF -> Gateway/V3.6 runtime -> frontend DTO 覆盖 board/status/output/artifact metadata/lineage。 |
| Seeded patch diff | E 阶段只允许展示 patch proposal/diff/risk，不允许 apply/publish。 | 已完成：seeded patch diff 来自 V3.6 patch repository，UI 通过 BFF PatchDiffDTO 渲染；禁止 `workflow.patch.apply/reject/publish`。 |
| Approval/quality/context | Console 能展示并操作 approval、quality 和 context。 | 已完成：workflow-bound approval side-effect、quality read-only、context.business update 和 business event binding 均有 E2E 测试。 |
| Scope isolation | 两个 project/workspace 的 UI 数据互不可见。 | 已完成：cross-scope 与 same-scope wrong-instance 对 approval/artifact/quality/context/event/patch 均有 denial tests。 |
| EventBridge refresh truth | EventBridge 只触发 refresh，不自建 runtime truth。 | 已完成：fake payload status 不被 UI 采信，刷新重新拉 board/status/context/approval。 |
| Redaction | UI、BFF response、event data 和 snapshots 不泄露 token/raw payload。 | 已完成：BoardDTO、InstanceStatusDTO、ApprovalDTO、QualityEvaluationDTO、ContextDTO、PatchDiffDTO、EventEnvelopeDTO redaction snapshot tests。 |
| Browser smoke | open console / select instance / approve / context update / event refresh。 | 未完成：当前为 component-level + BFF integration E2E，不是 full browser E2E。 |

V4.0-E 完成后可以声明：

```text
V4.0 dev/local Workflow Console integration baseline ready.
```

仍不能声明：

```text
production-ready external app support
complete AgentTalkWindow
complete Workflow Studio
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
```

## 7. 规划接口与对象影响范围

### 7.1 V4.0 UI 允许消费的 V3.6 RPC

```text
workflow.board.get
workflow.instance.status
station.output.list
workflow.patch.propose
workflow.patch.diff
workflow.patch.apply
workflow.patch.reject
workflow.template.publish
workflow.context.get
workflow.context.update
business.event.emit
business.event.bind
quality.evaluation.get
quality.evaluation.list
approval.respond
artifact.lineage
artifact.read_metadata
job.get
job.list
```

### 7.2 V4.0 UI 禁止依赖的路径

```text
direct Core Store access
direct WorkflowStore access
legacy approval.approve/reject for workflow-bound approval
unfrozen workflow placeholder protocol names
UI-only backend route that mutates workflow runtime
mock schema promoted to protocol contract
meeting.* / knowledge.* as default V4.0 reference flow
```

### 7.3 事件合同

V4.0 UI 应优先消费以下 live events：

```text
approval.required
business.event.received
workflow.context.updated
workflow.patch.proposed
workflow.patch.applied
workflow.patch.rejected
```

V3.6-J 中 `quality.evaluated` 仍为 trace-only，不作为 V4.0-A/C 的 live EventBridge 出门条件。如 V4.0 需要 live quality event，必须先补 EVENT_SCHEMAS、SSE tests 和文档声明。

## 8. P0 Blockers Before V4.0 Implementation

V4.0-0 前必须完成：

- `v4_0_current_gap_analysis.md` 与同名 drawio 建立并同步。
- V4.0 README 将 gap 文件对标为最高优先级维护入口。
- V4.0 target architecture 与 gap 文件统一为七平面正式基线。
- Stitch 原型 / Workflow Studio UI 区块必须映射到 V3.6 API 或标注为 UI-only transient state。
- 文档不得再使用未冻结的 workflow placeholder protocol names。
- V4.0 UI 默认不能直接调用 `/v1/rpc` 或 `/v1/events/subscribe`，应通过 BFF / SDK / hooks。

## 9. P1 Improvements

以下内容可以与 V4.0 主线并行，但不应阻塞 V4.0-0：

- 为 Workflow Console 增加 board response fixture。
- 为 patch diff 增加可视化 fixture。
- 为 AgentTalkWindow 前置 shell 增加 event playback fixture。
- 为 Quality Panel 增加 score/issue/suggestion 展示样例。
- 为 Context Panel 增加 safe path update 示例。
- 为 future Video Flow V2.0 增加 domain pack descriptor 示例，但不作为 V4.0-E reference flow 出门条件。

## 10. 测试与验收入口

后续实现阶段应新增或等价覆盖：

```text
tests/test_v4_0_contract_doc_alignment.py
tests/test_v4_0_frontend_no_direct_core_calls.py
tests/test_v4_0_workflow_console_readonly.py
tests/test_v4_0_workflow_editing_mvp.py
tests/test_v4_0_agent_talk_window_preparation.py
tests/test_v4_0_quality_approval_context_panels.py
tests/test_v4_0_reference_workflow_console_e2e.py
tests/test_v4_0_reference_console_scope_isolation.py
tests/test_v4_0_reference_console_eventbridge_e2e.py
tests/test_v4_0_reference_console_operation_panels_e2e.py
tests/test_v4_0_reference_console_redaction.py
```

回归命令建议：

```bash
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
```

如果 V4.0 引入前端 package，还必须补：

```bash
npm test
npm run build
```

## 11. Non-Goals

V4.0 当前阶段不做：

- production-ready external app support。
- enterprise auth / OAuth / SSO。
- distributed workflow engine。
- GPU/media render orchestration。
- Video Studio 真实业务流作为默认验收。
- Interview / Investment 正式业务扩展。
- 完整 AgentTalkWindow。
- 完整低代码画布能力。
- 完整多租户商业化权限后台。

## 12. V4.0 Gate

V4.0 正式出门必须通过：

```text
V4.0-0 Baseline & UI Contract Sync
V4.0-A Workflow Console Read-only MVP
V4.0-B Workflow Editing MVP
V4.0-C AgentTalkWindow Preparation
V4.0-D Quality / Approval / Context Panels
V4.0-E Reference Workflow Console E2E
```

其中 V4.0-E 必须证明：

- UI 默认通过 BFF / SDK / hooks 调用 harnessOS。
- 不直接读 Core Store 或 WorkflowStore。
- 不新增 UI 专用后端旁路。
- 不依赖 Meeting / Knowledge / Video / external MCP。
- Board、Patch、Quality、Approval、Context、EventBridge 均消费 V3.6 合同。
- Scope isolation 和 redaction 通过。

## 13. 出门声明

V4.0-E 完成后可以声明：

```text
V4.0 dev/local Workflow Console integration baseline ready.
```

仍不能声明：

```text
production-ready external app support
complete AgentTalkWindow
complete Workflow Studio
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
```
