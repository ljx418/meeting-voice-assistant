# V4.0 Current Gap Analysis

文档状态：V4.0-Z complete；V4.0 final audit package ready for review。当前基于 V4.0-G governed editing hardening、V4.0-H canvas-to-runtime patch bridge、V4.0-I stateful Agent assistant baseline、V4.0-J AgentTalk governance baseline、V4.0-K Agent action handoff baseline、V4.0-L handoff lifecycle baseline、V4.0-M operation evidence baseline、V4.0-N canvas editing readiness baseline、V4.0-O governed canvas proposal workflow baseline、V4.0-P AgentTalkWindow interaction E2E baseline、V4.0-Q Controlled Executor Design Gate、V4.0-R Production Readiness Preflight、V4.0-S Production Auth / Tenant Boundary Follow-up Design、V4.0-T Production Token Lifecycle Follow-up Design、V4.0-U Production Secret Management Follow-up Design、V4.0-V Production Observability / Audit Retention Follow-up Design、V4.0-W External App Production Onboarding Follow-up Design、V4.0-X Production Readiness Consolidation Gate、V4.0-Y Controlled Executor Implementation Gate 和 V4.0-Z Final Audit / Release Gate。V3.6 complete baseline 与 V3.6/V4.0 preflight hardening 已完成，Workflow Console read-only MVP、AgentTalkWindow preparation shell、低代码 Workflow Studio Shell、真实 BFF read/event data bridge、Quality / Approval / Context operation panels、Reference Workflow Console component-level + BFF integration E2E、Playwright browser smoke baseline、governed patch apply/reject/publish editing hardening、canvas / Inspector intent 到 WorkflowPatch proposal 的桥接、BFF/UI 层 stateful Agent assistant baseline、Agent action proposal governance、Agent action handoff to user-confirmed operation panels、Agent handoff lifecycle / audit / recovery hardening、user-confirmed operation evidence / governance review baseline、canvas editing readiness baseline、governed canvas proposal workflow baseline、AgentTalkWindow interaction E2E baseline、Controlled Executor Design Gate、Production Readiness Preflight、Auth / Tenant Boundary Design、Token Lifecycle Design、Secret Management Design、Observability / Audit Retention Design、External App Onboarding Design、Production Readiness Consolidation Gate、Controlled Executor Implementation Gate 和 Final Audit / Release Gate 均已完成。最终允许声明为 `V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.`。

当前仍不能声明：

```text
不能声明 executor
不能声明完整 AgentTalkWindow
不能声明完整低代码编辑器
不能声明 enterprise auth
不能声明 OAuth/SSO
不能声明多租户控制台
不能声明 production-ready external app support
```
配套图：`v4_0_current_gap_analysis.drawio`。

本文与 `v4_0_current_gap_analysis.drawio` 是 V4.0 历史规划、验收和与用户交互时的核心维护文件。两者承载 V4.0 架构演进、差距矩阵、阶段路线图和 V4.0 gate。V4.1 之后的前向 V4.x gap 不再以本文为主，应改用 `docs/design/V4.x/v4_x_headless_current_gap_analysis.md` 和 `docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio`。

## 0. V4.x Headless-first 后续路线审计补充

V4.0 gap 文档仍是 V4.0 Workflow Console / Workflow Studio / AgentTalkWindow 前置产品层的历史事实记录。V4.1 完成后，后续 V4.x 主线已从完整 Web 低代码 Studio first 调整为：

```text
Headless Workflow Core
+ TUI / Command Palette
+ Drawio Workflow Visualization
+ HTML Runtime Reports
+ Thin Web Console
```

新的前向 gap source 是：

```text
docs/design/V4.x/v4_x_headless_current_gap_analysis.md
```

当前前向差距：

- 尚未实现 canonical `WorkflowSpec` schema / validator。
- 尚未实现真实 TUI / Command Palette。
- 尚未实现 Drawio renderer。
- 尚未实现 HTML report generator。
- 尚未实现通用 user-confirmed workflow start。
- 尚未实现通用 user-confirmed station rerun、attempt history 或 downstream stale propagation。
- 尚未实现 controlled execution runtime、Agent executor、真实串行/并行多 Agent runtime 或长时工程任务看板。
- Thin Web Console 只能作为 BFF-only 观察与受限用户确认入口，不再承担完整 Web 低代码 Studio 主线。

因此，本文中的 V4.0 Web Studio / AgentTalkWindow / controlled executor design gate 结论不能声明为 V4.x 已具备完整 Web Studio、Agent executor、controlled executor 或 production-ready external app support。V4.2-A 只允许推进 Headless Interaction Pivot；通用执行能力必须延后到 V4.2-B/C 单独审计和实现。

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
- 当前 Z 阶段新增 Final Audit / Release Gate：T/U/V/W 分别补齐 token lifecycle、secret management、observability / audit retention、external app onboarding 的机器可读设计合同；X 聚合 R/S/T/U/V/W 的 production readiness blockers；Y 固化 controlled executor implementation gate；Z 聚合 V4.0 final audit package 和 No False Green 结论。
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
- 已有 governed Workflow Editing hardening：patch proposal/diff 展示、高风险 patch 默认拒绝直接 apply，并支持用户显式确认的 apply/reject/publish。
- 已有 AgentTalkWindow preparation shell：fixture-first event timeline、patch proposal/diff 摘要、approval.required notice、只读 context.business summary 和 embed boundary tests。
- 已有 V4.0-D operation panels：QualityPanel 只读展示 `quality.evaluation.get/list` DTO；ApprovalPanel 通过用户显式点击调用 workflow-bound `approval.respond`；ContextPanel 通过 path-based set 受控写入 `context.business` 并可发送具体 `business.*` event。

当前仍未完成：

- 没有完整 Workflow Studio 可视化编辑器：V4.0-H 已把节点库 click/drag、连线 proposal 和 Inspector 输入转换为 patch proposal；但仍不声明完整低代码画布编辑 ready。
- 没有完整 AgentTalkWindow 状态机；V4.0-I 只完成 BFF/UI 层 stateful Agent assistant baseline，V4.0-J 增加 action proposal governance，V4.0-K 增加 handoff 到用户确认 operation panels，V4.0-L 补强 handoff lifecycle / audit / recovery，V4.0-M 补强用户确认操作证据链和治理审计，V4.0-P 补齐交互 E2E，V4.0-Q 只完成 controlled executor design gate，V4.0-R 只完成 production readiness preflight，V4.0-S 只完成 production auth / tenant boundary follow-up design；Agent 仍不能自动 apply/reject/publish/approval.respond/context.update/business.event.emit/start workflow/rerun station。
- UI 已通过 BFF 消费 V3.6 Board / status / output / artifact metadata / lineage 的真实读链路；Approval respond、context update 和 business event 已进入 V4.0-D operation panels；Patch apply/publish 与 Quality create/attach 仍不暴露。
- 已完成 V4.0 Reference Workflow Console component-level + BFF integration E2E、V4.0-F Playwright 浏览器级 smoke、V4.0-G governed patch apply/reject/publish editing hardening、V4.0-H Canvas-to-runtime bridge、V4.0-I AgentTalk stateful assistant baseline、V4.0-J AgentTalk governance baseline、V4.0-K Agent action handoff baseline、V4.0-L Agent handoff lifecycle baseline、V4.0-M operation evidence / governance review baseline 和 V4.0-N canvas editing readiness baseline。
- 没有 production-ready external app support、OAuth/SSO implementation、多租户控制台、production secret manager、production observability platform、production audit export、controlled executor implementation 或分布式调度。

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
| Workflow editing UI | 已完成 governed `workflow.patch.apply/reject` 和 `workflow.template.publish` BFF/UI/browser smoke；Apply / Reject / Publish 均要求用户显式确认，`source=agent` 被拒绝，高风险 patch 默认不能 apply。V4.0-H 已新增 NodeAddIntent / EdgeAddIntent / InspectorUpdateIntent 到 proposal 的桥接。 | 画布/Inspector 只生成 WorkflowPatch proposal，Apply 后才通过 G path 修改 draft；不直接写 runtime。 | V4.0-H complete |
| Agent editing boundary | V4.0-I 已实现 BFF/UI 层 AgentTalkSession / AgentMessage / AgentSuggestion / AgentActionIntent baseline；V4.0-J/K/L/M 已完成 action proposal、handoff、lifecycle 和 evidence；V4.0-N/O/P 已完成 canvas proposal workflow 和 AgentTalk interaction E2E；V4.0-Q/Y 已完成 executor 设计门禁和 implementation gate；deterministic suggestions 不调用外部 LLM/MCP/connector；`source=agent` 可 propose patch/action proposal/handoff，但不能直接 apply/reject/publish/approval.respond/context.update/business.event.emit/start workflow/rerun station。 | 后续如果实现 executor，必须另行立项并通过 Q/Y gate、approval gate、sandbox boundary、rollback / kill switch 和 production readiness blockers。 | V4.0-Z complete |
| Quality / Approval / Context panels | 已完成 Quality read-only、workflow-bound approval.respond、context.business update、business.event.emit 操作面板。 | 后续继续作为 H 阶段 canvas/inspector patch bridge 的事实刷新面板，不扩展 Quality create/attach。 | V4.0-D complete |
| Reference console E2E | 已完成平台中立 runtime fixture、BusinessEventBinding、seeded patch diff、approval side-effect、context update、EventBridge refresh truth、DTO redaction、scope/ownership guard 和 frontend real DTO render tests。 | 已通过 V4.0-F 补最小 browser-level smoke，但仍不声明 full browser E2E。 | V4.0-E complete at integration baseline |
| Browser smoke | 已完成 Playwright 浏览器级 smoke；component-level + BFF integration E2E 继续通过。 | 已验证 build 后 Vite preview、同一 test BFF / V3.6 runtime fixture、open console、select instance、render board、approval respond、context update、可控 EventBridge refresh、no direct `/v1/*`、无 Demo / Fixture fallback 和 DOM redaction。 | V4.0-F complete |
| Editing browser smoke | 已完成 Playwright governed editing smoke；保留 V4.0-F browser smoke。 | 已验证 render Patch Diff、用户确认 Apply to Draft、用户确认 Publish New Version、BFF apply/publish route、version refresh、fake event payload 不被采信、no direct `/v1/*` 和 DOM redaction。 | V4.0-G complete |
| Production readiness | V3.5/V3.6 均为 dev/local baseline；V4.0-R/S/T/U/V/W 已登记 production readiness、auth/tenant、token、secret、observability/audit 和 external app onboarding gaps；V4.0-X 已聚合 blockers。 | 当前只能声明 production readiness design gates ready for implementation review，不能声明 enterprise auth、OAuth/SSO、tenant control plane 或 production-ready。 | V4.0-Z complete |

## 6. 开发计划摘要

### 6.1 当前开发阶段

当前项目处于 **V4.0-Z Final Audit / Release Gate complete**。V3.6 后端 gate 已完成，V4.0 已有画布优先 Workflow Studio Shell、真实 BFF read/event data bridge、AgentTalkWindow preparation shell、Quality / Approval / Context 操作面板、平台中立 Reference Workflow Console component-level + BFF integration E2E、Playwright browser smoke baseline、用户显式确认的 patch apply/reject/publish editing hardening、canvas / Inspector 到 patch proposal 的桥接、BFF/UI 层 AgentTalk stateful baseline、可治理 action proposal queue、handoff 到用户确认 operation panels 的安全交接、handoff lifecycle / audit / recovery hardening、user-confirmed operation evidence / governance review baseline、canvas editing readiness baseline、governed canvas proposal workflow baseline、AgentTalkWindow interaction E2E baseline、controlled executor design gate、production readiness preflight、production auth / tenant boundary follow-up design、token lifecycle design、secret management design、observability / audit retention design、external app onboarding design、production readiness consolidation gate、controlled executor implementation gate 和 final audit package。最终允许声明：`V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.`。当前仍不声明完整 AgentTalkWindow、Agent executor、controlled executor、完整 Workflow Studio ready、enterprise auth、OAuth/SSO、多租户控制台或 production-ready external app support。

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
- `apps/workflow-console/` 已将 Patch preparation panel 升级为 governed editing panel，展示 patch diff、risk_flags、requires_approval，并通过用户显式确认执行 Apply to Draft、Reject Patch 和 Publish New Version；高风险 patch 默认不能 apply。
- `apps/workflow-console/` 已新增 AgentTalk preparation shell，展示 demo/trace_only source 标识事件、patch 建议、approval notice、只读 context.business summary 和非突变 allowed_actions。
- `apps/api/routers/bff.py` 已新增 V4.0-D operation panel structured routes：instance-scoped quality list/get、approval list/respond、context get/update、business event emit；所有 response 转为 redacted frontend DTO，不透传 raw Gateway response。
- `apps/workflow-console/` 已新增 QualityPanel、ApprovalPanel、ContextPanel，并接入 `useWorkflowConsoleData` real hook；Quality 保持 read-only，approval.respond 只能由用户显式点击触发，context update 只能写 `business.*`。
- `tests/v4_0_reference_support.py` 已新增平台中立 V4.0-E fixture：生成 WorkflowTemplate / WorkflowVersion / WorkflowInstance / StationRun / Job / Artifact / Approval / QualityEvaluation / WorkflowContext / BusinessEventBinding / seeded WorkflowPatch。
- V4.0-E 已验证：`business.event.emit -> BusinessEventBinding -> context.business` 更新；seeded patch diff 来自 V3.6 patch repository；workflow-bound `approval.respond` 会推动 waiting_approval station 继续；EventBridge 事件只触发 refresh，不采信 payload 中伪造状态。
- V4.0-R 新增 production readiness preflight：auth/SSO/OAuth、multi-tenant isolation、capability token lifecycle、secret management、audit retention、observability/metrics/alerting、rate limit/abuse control、data residency/export/deletion、external app onboarding 和 incident recovery 均登记为 open production gaps。
- V4.0-Q 已完成 implementation baseline：policy matrix、capability profile、approval gate design、sandbox boundary、rollback / kill switch design、future executor evidence contract、event truth guard 和 claim guard 均只作为设计门禁存在，不新增 executor route、worker、runtime service 或 frontend execute client。
- V4.0-R 已完成 implementation baseline：production readiness gap register、auth/tenant boundary、token lifecycle gap、secret hygiene、observability/audit gap、external app boundary、forbidden route scan 和 claim guard 均只作为 preflight 存在，不新增 production auth、OAuth/SSO、tenant admin、token rotate/revoke、quota、audit export 或 production onboarding route。
- V4.0-S 已完成 implementation baseline：identity matrix、tenant isolation matrix、service account / agent identity design、OAuth / SSO gap contract、capability token binding design、runtime boundary、forbidden route scan 和 claim guard 均只作为设计门禁存在，不新增 OAuth/SSO/OIDC/SAML/callback、tenant admin、token rotate/revoke、production auth middleware 或 production onboarding route。
- V4.0-H 已完成：`CanvasPatchIntent / NodeAddIntent / EdgeAddIntent / InspectorUpdateIntent`、统一 BFF proposal route、Node / Edge / Inspector proposal UI、H focused tests 和 browser smoke 已通过。
- V4.0-I 已完成 implementation baseline：AgentTalkSession / AgentMessage / AgentSuggestion / AgentActionIntent 均为 BFF/UI 层对象，不进入 V3.6 runtime contract；deterministic suggestions 不调用外部 LLM / MCP / connector；Agent 面板不暴露 Apply / Reject / Publish / Approve / Reject 等突变动作。

当前需要继续推进的是：

- V4.0-Z 后应进入 implementation review，而不是继续扩大 V4.0 完成声明。
- 后续 production implementation 必须逐项关闭 R/S/T/U/V/W/X blockers，并分别立项 auth/tenant、token lifecycle、secret management、observability/audit、external app onboarding。
- 后续 controlled executor implementation 必须重新审计 Q/Y policy matrix、capability、approval gate、sandbox、rollback、kill switch 和 audit evidence。

### 6.2 阶段路线图

| 阶段 | 目标 | 主要交付 | 完成后可声明 |
| --- | --- | --- | --- |
| V4.0-0 | Baseline & UI Contract Sync | V4.0 gap 文件对、contract map、mock-to-real 检查、No False Green 边界、Stitch 原型到 V3.6 API 映射。 | 已完成：V4.0 implementation baseline and UI contract map ready。 |
| V4.0-A | Workflow Console Read-only MVP | Station Board、Artifact Board、Approval/Quality/Trace summary，只读消费 board/status/output/EventBridge。 | 已完成：Workflow Console read-only MVP ready。 |
| V4.0-A2 | Real Data Bridge | BFF structured routes、frontend DTO redaction、真实 V3.6 dummy pipeline fixture 到 UI data hook、BFF EventBridge proxy。 | 已完成：Workflow Studio shell connected to real BFF read/event data。 |
| V4.0-B | Workflow Editing MVP | Patch proposal、diff view、draft apply、publish flow；高风险 patch 不绕过 governance。 | 重新收窄为 preparation shell：当前 UI 只展示 propose/diff/risk，不暴露 apply/reject/publish。 |
| V4.0-C | AgentTalkWindow Preparation | 基于 Embed Contract / EventBridge / approval / context / patch 的前置 shell。 | 已完成：AgentTalkWindow preparation shell ready。 |
| V4.0-D | Quality / Approval / Context Panels | QualityEvaluation panel、approval.respond panel、workflow context panel、business event display。 | 已完成：Quality read-only, workflow approval response, and business context operation panels ready for dev/local Workflow Studio。 |
| V4.0-E | Reference Workflow Console E2E | 平台中立 workflow console E2E；UI + BFF + SDK/hooks + V3.6 runtime 全链路。 | 已完成 component-level + BFF integration E2E；browser smoke 已在 V4.0-F 补齐。 |
| V4.0-F | Browser Smoke Baseline | 用 Playwright 验证当前 integration baseline 在 build 后 Vite preview 中可打开、可操作、可刷新。 | 已完成：dev/local Workflow Console browser smoke baseline ready。 |
| V4.0-G | Editing hardening | 用户显式确认的 patch apply/reject/publish BFF/UI/browser smoke；高风险 patch 默认拒绝；Agent 不可自动 apply/publish。 | 已完成：governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console。 |
| V4.0-H | Canvas-to-runtime bridge | Node drag / edge proposal / Inspector dirty state 生成 WorkflowPatch proposal；不直接写 Store / Draft / WorkflowEdge。 | 已完成：canvas-to-runtime patch bridge ready for dev/local Workflow Console。 |
| V4.0-I | AgentTalkWindow Stateful Assistant | BFF/UI 层 session/message/suggestion baseline；non-executable action intents；source=agent 只允许 propose patch。 | 已完成：governed stateful Agent assistant baseline ready for dev/local Workflow Console。 |
| V4.0-J | AgentTalk Governance | BFF/UI 层 action proposal queue；display/navigation/proposal/forbidden policy guard；redacted audit baseline；无 executor。 | 已完成：AgentTalk governance and controlled action proposal baseline ready。 |
| V4.0-K | Agent Action Handoff | AgentActionProposal 安全交接到 Editing / Approval / Context operation panels；handoff route 只创建 DTO，最终执行仍需用户显式确认。 | 已完成：Agent action handoff to user-confirmed operation panels ready。 |
| V4.0-L | Agent Handoff Lifecycle | AgentActionHandoff repository、lifecycle、lazy expiration、URL recovery、append-only audit、stale/blocked guard；仍不是 executor。 | 已完成：Agent handoff lifecycle, audit, and recovery baseline ready。 |
| V4.0-M | Operation Evidence / Governance Review | 把用户确认后的 patch / publish / approval / context / business event 操作沉淀为可审计 evidence chain 和只读治理审计面板。 | 已完成：user-confirmed operation evidence and governance review baseline ready。 |
| V4.0-N | Canvas Editing Readiness | 在 H 的 proposal bridge 之上补 controlled 节点库 catalog、CanvasDraftProjection、Inspector form mapping、edge validation、draft refresh 和 layout boundary；仍通过 patch 写 draft。 | 已完成：canvas editing readiness baseline ready for dev/local Workflow Console。 |
| V4.0-O | Governed Canvas Proposal Workflow | 在 N 之上补 patch queue、projection freshness、catalog versioning、Inspector/edge validation、proposal apply race hardening、fixture isolation 和风险声明审计。 | 已完成：governed canvas proposal workflow ready for expanded dev/local Workflow Console validation。 |
| V4.0-P | AgentTalkWindow Interaction E2E | 在 I/J/K/L/M/O 之上补 Agent 面板交互闭环：解释、建议、handoff、evidence review、事件刷新；仍不引入 autonomous executor。 | 已完成：AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation。 |
| V4.0-Q | Controlled Executor Design Gate | 只做受控执行器设计门禁：policy、approval、capability、sandbox、audit、rollback、kill switch；不实现真实 executor。 | 已完成：controlled executor design gate ready for review；不声明 executor ready。 |
| V4.0-R | Production Readiness Preflight | production path 预检：auth/SSO/multi-tenant/control plane/observability/security hardening 的差距清单和验收计划。 | 已完成：production readiness preflight ready for review；不声明 production-ready。 |
| V4.0-S | Production Auth / Tenant Boundary Follow-up Design | 基于 R gap register 选择 Auth / Tenant Boundary 方向做设计收敛：identity matrix、tenant isolation、service account / agent identity、OAuth / SSO gap、capability token binding。 | 已完成：production auth and tenant boundary follow-up design ready for review；不声明 enterprise auth、OAuth/SSO 或 tenant control plane ready。 |
| V4.0-T | Production Token Lifecycle Follow-up Design | 细化 issuance、expiration、rotation、revocation、origin/audience/scope binding、emergency revoke 和 token audit。 | 已完成：production token lifecycle follow-up design ready for review；不实现 token lifecycle runtime。 |
| V4.0-U | Production Secret Management Follow-up Design | 细化 capability token、subscription token、connector secret、external LLM key、signed URL 和 raw prompt redaction / sandbox boundary。 | 已完成：production secret management follow-up design ready for review；不实现 production secret manager。 |
| V4.0-V | Production Observability / Audit Retention Follow-up Design | 细化 trace/evidence retention、audit export gap、security audit log、correlation/idempotency coverage、metrics/alerting 和 error taxonomy。 | 已完成：production observability and audit retention follow-up design ready for review；不实现 audit export 或 observability platform。 |
| V4.0-W | External App Production Onboarding Follow-up Design | 细化 app registration、domain verification、tenant provisioning、service account lifecycle、quota/rate limit、offboarding 和 support runbook。 | 已完成：external app production onboarding follow-up design ready for review；不实现 production onboarding。 |
| V4.0-X | Production Readiness Consolidation Gate | 聚合 R/S/T/U/V/W production readiness blockers。 | 已完成：production readiness consolidation gate ready for implementation review；不声明 production-ready。 |
| V4.0-Y | Controlled Executor Implementation Gate | 基于 Q/X 固化 executor implementation 前置门禁和 source=agent 非执行边界。 | 已完成：controlled executor implementation gate ready for review；不实现 controlled executor。 |
| V4.0-Z | Final Audit / Release Gate | 聚合 V4.0-O 到 V4.0-Z 的最终审计包、allowed final claim 和 forbidden claims。 | 已完成：V4.0 final audit package ready for review；允许 V4.0 complete 的审计口径，但不声明 production-ready 或 executor ready。 |

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
| Apply | 使用 `workflow.patch.apply` 只修改 draft。 | 已在 V4.0-G 通过 BFF structured route 和用户显式确认接入；高风险 patch 默认拒绝。 |
| Publish | 使用 `workflow.template.publish` 发布新 version。 | 已在 V4.0-G 通过 BFF structured route 和用户显式确认接入；必须带 version string 与 expected draft revision。 |
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

### 6.8 V4.0-E 完成范围

V4.0-E 是 V4.0 dev/local 出门 E2E，不是 production readiness。本阶段已完成 component-level + BFF integration E2E；browser smoke 已在 V4.0-F 补齐。

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
| Browser smoke | open console / select instance / approve / context update / event refresh。 | 已后续补齐：V4.0-F Playwright browser smoke 通过；仍不是 full browser E2E。 |

V4.0-E 完成后已声明：

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

### 6.9 V4.0-F 完成范围

V4.0-F 是 Browser Smoke Baseline，不是完整 browser E2E，也不是完整 Workflow Studio。本阶段固定使用 Playwright，基于 `npm run build` 后的 Vite preview，验证当前 component-level + BFF integration E2E 在真实浏览器中可打开、可操作、可刷新。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Browser harness | 启动 build 后的 Workflow Console Vite preview 和 test BFF / V3.6 runtime fixture server。 | 已完成：固定 Playwright；`VITE_HARNESSOS_DEMO_MODE=false`；real mode 禁止 silent fallback demoData，DOM 不显示 Demo / Fixture。 |
| Open console | 浏览器打开 Workflow Console，等待真实数据加载。 | 已完成。 |
| Select instance | 选择 workflow instance 后刷新 board/status/outputs。 | 已完成。 |
| Render board | station、artifact、approval、quality、trace summary 可见。 | 已完成。 |
| Approval action | ApprovalPanel 用户显式点击后调用 workflow-bound `approval.respond`，刷新后 workflow/station 继续。 | 已完成。 |
| Context update | ContextPanel 只能写入 `context.business`，刷新后可见。 | 已完成。 |
| EventBridge refresh | 通过 test harness 可控触发 SSE event；event 只触发 refresh，不从 event payload 自建 runtime truth；fake status payload 不被 UI 采信。 | 已完成。 |
| No direct `/v1/*` | Browser network 不直接请求 `/v1/rpc` 或 `/v1/events/subscribe`；BFF 内部调用允许。 | 已完成。 |
| DOM redaction | DOM 不包含 token、Authorization、subscription token、raw trace/artifact/connector payload。 | 已完成。 |
| No editing action | UI 不暴露 patch apply/reject/publish 或误导性自动应用文案。 | 已完成。 |
| Stable selectors | Playwright 主要使用 `data-testid`：`workflow-console`、`workflow-instance-selector`、`station-board`、`station-card`、`artifact-panel`、`approval-panel`、`approval-approve-button`、`quality-panel`、`context-panel`、`context-update-button`、`event-feed`。 | 已完成。 |

V4.0-F 完成后当前允许声明：

```text
V4.0 dev/local Workflow Console browser smoke baseline ready.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full browser E2E ready
```

### 6.10 V4.0-G 完成范围

V4.0-G 是 Editing Hardening，不是完整 Workflow Studio。本阶段开放的是受治理的 patch apply/reject/publish 闭环，而不是画布节点拖入、连线落库或 Inspector 直接写 draft。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Patch list | UI 从真实 BFF / V3.6 patch repository 获取 selected instance 绑定 patch，不使用 demoData 作为 editing 证据。 | 已完成。 |
| Patch apply | Apply to Draft 必须用户显式确认；BFF 校验 `user_confirmed=true` 和 `source=editing_panel/workflow_console`。 | 已完成。 |
| High-risk governance | `requires_approval=true` 的 patch 默认不能 apply；V4.0-G 不新增复杂 approval flow。 | 已完成。 |
| Patch reject | Reject Patch 必须用户显式确认；repeated reject idempotent，applied patch reject conflict。 | 已完成。 |
| Publish | Publish New Version 必须带 version string 和 expected draft revision；发布新 immutable WorkflowVersion snapshot。 | 已完成。 |
| Ownership | `patch_id` 必须属于 route template；patch draft 必须是 template latest draft；instance-bound patch 必须匹配 selected instance。 | 已完成。 |
| Event refresh | patch/publish 事件只触发 refresh；UI 不从 event payload 自建 draft/version truth。 | 已完成。 |
| Browser editing smoke | Playwright 覆盖 render Patch Diff、Apply、Publish、version refresh、fake event payload 不被采信、no direct `/v1/*`、DOM redaction。 | 已完成。 |
| Canvas boundary | Node drag 不创建 Station；Edge drag 不写 WorkflowEdge；Inspector form 不直接写 draft。 | 已保持。 |

V4.0-G 完成后当前允许声明：

```text
V4.0-G complete: governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full low-code canvas editing ready
```

### 6.11 V4.0-H 完成范围

V4.0-H 是 Canvas-to-runtime Bridge，不是完整 Workflow Studio。本阶段开放的是节点库、画布连线和 Inspector 输入到 WorkflowPatch proposal 的受控桥接，而不是直接创建 Station、直接写 WorkflowEdge 或直接修改 WorkflowDraft。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| NodeAddIntent | 节点库 click/drag 只能生成 `add_station` proposal 和 ghost proposal state。 | 已完成。 |
| EdgeAddIntent | 连线 proposal 使用 `operation=update_edge` + `edge_patch.action=add/remove/update`，不新增 arbitrary `add_edge` RPC surface。 | 已完成。 |
| InspectorUpdateIntent | Inspector 输入只进入 local dirty state，点击 `生成 Patch` 后才调用 BFF proposal route。 | 已完成。 |
| Unified proposal route | 统一使用 `POST /bff/workflows/{workflow_template_id}/patches`。 | 已完成。 |
| Payload validation | proposal payload 拒绝 UI layout fields、token、Authorization、raw trace/artifact/connector payload。 | 已完成。 |
| Governance reuse | Apply / Reject / Publish 继续复用 V4.0-G governed routes，仍要求用户显式确认。 | 已完成。 |
| Browser canvas smoke | Playwright 覆盖 Node proposal、Inspector proposal、no direct `/v1/*`、DOM redaction 和 no automation copy。 | 已完成。 |

V4.0-H 完成后当前允许声明：

```text
V4.0-H complete: canvas-to-runtime patch bridge ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full low-code canvas editing ready
```

### 6.12 V4.0-I 完成范围

V4.0-I 是 AgentTalkWindow Stateful Assistant baseline，不是完整 AgentTalkWindow，也不是自治工作流编辑器。本阶段新增的是 BFF/UI 层 Agent session/message/suggestion/action intent 基线，继续复用 V4.0-G/H 的 patch governance。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Agent state model | `AgentTalkSession` / `AgentMessage` / `AgentSuggestion` / `AgentActionIntent` 只能存在于 BFF/UI 层。 | 已完成；不写 V3.6 WorkflowTemplate / WorkflowDraft / WorkflowVersion / StationRun。 |
| Deterministic assistant | 不调用外部 LLM、external MCP、connector 或自由 executor。 | 已完成；使用 rule/fixture-backed suggestions。 |
| Non-executable intents | 只允许 explain、summarize、suggest patch、show diff、show approval notice、show context summary、navigate to editing panel。 | 已完成；forbidden intents 被 BFF 拒绝。 |
| Agent patch governance | `source=agent` 可以 propose patch，但不能 apply/reject/publish。 | 已完成；apply/publish 仍必须走 V4.0-G editing panel 的 user-confirmed route。 |
| Capability / ownership | Agent routes 校验 `agent_talk.*` / `agent_suggestions.*` capability、scope 和 instance ownership。 | 已完成。 |
| Event refresh truth | Agent timeline 只把 live event 作为 refresh/display signal，不从 event payload 构造 summary truth。 | 已完成。 |
| UI restrictions | Agent panel 不显示 Apply Patch / Reject Patch / Publish Version / Approve / Reject，不出现自动应用/自动发布等文案。 | 已完成。 |
| Browser smoke | Playwright 覆盖打开 Agent assistant、输入“帮我优化当前节点”、出现 suggestion、查看 Diff、无突变请求、无 `/v1/*` 直连、DOM redaction。 | 已完成。 |

V4.0-I 完成后当前允许声明：

```text
V4.0-I complete: governed stateful Agent assistant baseline ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete AgentTalkWindow ready
complete Workflow Studio ready
production-ready external app support
autonomous workflow editing ready
enterprise auth/OAuth/SSO ready
```

### 6.13 V4.0-J 实施范围

V4.0-J 是 AgentTalk Governance & Controlled Executor Preparation，不是 controlled executor ready。本阶段新增的是 Agent action proposal queue、action policy guard 和 redacted audit baseline。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| AgentActionProposal | BFF/UI 层对象，记录 proposal_id、session_id、workflow refs、intent_type、risk、policy_decision、lifecycle。 | 已完成。 |
| Policy guard | display_only / navigation / proposal_only / forbidden 分类。 | 已完成。 |
| BFF routes | 只允许 list/create/get/dismiss action proposals，不新增 execute/run/apply route。 | 已完成。 |
| UI queue | Agent 面板展示 proposal queue，只允许查看详情、查看 Diff、跳转面板、忽略建议。 | 已完成。 |
| Audit / redaction | 写 redacted BFF audit，不记录 raw prompt、raw trace payload、raw artifact content、token 或 upstream signed URL。 | 已完成。 |

V4.0-J 完成后当前最多声明：

```text
V4.0-J complete: AgentTalk governance and controlled action proposal baseline ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete AgentTalkWindow ready
complete Workflow Studio ready
autonomous workflow editing ready
controlled executor ready
production-ready external app support
enterprise auth/OAuth/SSO ready
```

### 6.14 V4.0-K 实施范围

V4.0-K 是 Agent Action Handoff to User-Confirmed Operation Panels，不是 Agent executor，也不是 autonomous workflow editing。本阶段新增的是 AgentActionProposal 到 Editing / Approval / Context operation panels 的安全交接。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| AgentActionHandoff | BFF/UI 层对象，包含 handoff_id、proposal_id、workflow refs、target_panel、target_resource、suggested_form_prefill、expires_at、status。 | 已完成。 |
| BFF routes | `POST /agent/action-proposals/{proposal_id}/handoff` 和 `GET /agent/action-handoffs/{handoff_id}` 只创建 / 读取 DTO，不执行 mutation。 | 已完成。 |
| Panel handoff | Agent proposal card 可跳转 Editing / Approval / Context panels；面板显示“来自 Agent 建议”。 | 已完成。 |
| User confirmation guard | 最终执行仍由 operation panels 触发；handoff flow 携带 user_confirmed、source、proposal_id、handoff_id；`source=agent` 被拒绝。 | 已完成。 |
| Redaction / audit | Handoff DTO、audit、error response、DOM 不泄露 token、Authorization、raw trace/artifact/connector payload。 | 已完成。 |

V4.0-K 完成后当前最多声明：

```text
V4.0-K complete: Agent action handoff to user-confirmed operation panels ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete AgentTalkWindow ready
complete Workflow Studio ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
production-ready external app support
enterprise auth/OAuth/SSO ready
```

### 6.15 V4.0-L 实施范围

V4.0-L 是 Agent Handoff Lifecycle / Audit / Recovery Hardening，不是 Agent executor，也不是 autonomous workflow editing。本阶段在 V4.0-K handoff baseline 之上补强状态机、repository 边界、URL recovery、stale/expired/blocked guard 和审计查询。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Repository / store | 新增 `AgentHandoffRepository` / `InMemoryAgentHandoffStore`；BFF 不直接操作裸 dict；dev/local only。 | 已完成。 |
| Lifecycle | 固定 `active/opened/used_for_user_confirmed_action/dismissed/expired/stale/blocked`；terminal 状态不可回到 active/opened；repeated open/dismiss 幂等。 | 已完成。 |
| Lazy expiration | 每次 get/list/open/use 前检查 `expires_at`；expired handoff 不可执行 operation。 | 已完成。 |
| Recovery | 支持 `?handoff_id=...` 页面恢复，自动打开目标 panel，但不自动执行 mutation。 | 已完成。 |
| Stale / blocked guard | Editing / Approval / Context handoff 按 patch、draft revision、approval、workflow binding、context revision 等状态标记 stale/blocked。 | 已完成。 |
| Audit query | 新增 handoff list 与 audit read route；audit append-only，只返回 redacted summary。 | 已完成。 |
| UI guard | Agent proposal queue 和 operation panels 展示 handoff 状态；expired/stale/blocked/used/dismissed 禁用确认按钮。 | 已完成。 |

V4.0-L 完成后当前最多声明：

```text
V4.0-L complete: Agent handoff lifecycle, audit, and recovery baseline ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete AgentTalkWindow ready
complete Workflow Studio ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
production-ready external app support
enterprise auth/OAuth/SSO ready
```

### 6.16 V4.0-M 实施范围

V4.0-M 是 Operation Evidence / Governance Review Baseline，不是 Agent executor，也不是 controlled executor。本阶段在 V4.0-K/L 的 proposal -> handoff -> user-confirmed operation 链路之上，补齐用户确认操作后的 evidence chain 和只读治理审计视图。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Evidence contract | 新增 `OperationEvidenceRecord`、`OperationEvidenceChain`、`GovernanceReviewSummary`、`OperationRuntimeResultRef`。 | 已完成。 |
| Repository / store | 新增 `AgentOperationEvidenceRepository` / `InMemoryAgentOperationEvidenceStore`；append-only dev/local only。 | 已完成。 |
| Evidence creation hook | 用户确认后的 patch apply/reject、publish、approval.respond、context.update、business.event.emit 创建 evidence。 | 已完成。 |
| Read-only BFF routes | 新增 operation evidence list/get 与 governance review route。 | 已完成。 |
| Governance Review Panel | 新增只读“治理审计”面板，展示建议来源、handoff 状态、用户确认、执行结果、风险、策略和 runtime result ref。 | 已完成。 |
| Redaction | Evidence DTO、audit、DOM、error response 不泄露 token、Authorization、raw trace/artifact/connector payload 或 raw prompt。 | 已完成。 |

V4.0-N 完成后曾允许声明：

```text
V4.0-N complete: canvas editing readiness baseline ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete AgentTalkWindow ready
complete Workflow Studio ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
production-ready external app support
enterprise auth/OAuth/SSO ready
```

### 6.17 V4.0-P 后风险细化

V4.0-P 已收敛 AgentTalkWindow interaction E2E 的 read model、只读 explain/summarize、proposal/handoff、evidence review、event truth 和 redaction 边界。V4.0-Q 的主要风险转为 controlled executor 设计门禁被误写成 executor 实现，必须避免把 design gate 升级为 autonomous execution 或 production-ready support。

| 风险 ID | 风险 | 严重度 | 概率 | V4.0-Q 控制措施 |
| --- | --- | --- | --- | --- |
| Q-R1 | Controlled Executor Design Gate 被误写成 executor ready 或 Agent executor ready。 | critical | medium | Q 阶段只产出设计门禁、policy matrix 和测试计划；不得新增 execution route。 |
| Q-R2 | Agent action proposal/handoff 被扩展为自动执行路径。 | critical | medium | 继续要求用户显式确认；source=agent 仍不能 apply/publish/respond/update/emit/start/rerun。 |
| Q-R3 | Approval / capability / sandbox / rollback / kill switch 设计不完整。 | high | medium | Q 必须先审计 policy、approval gate、capability profile、sandbox、rollback、kill switch 和 evidence chain。 |
| Q-R4 | EventBridge payload 被当作 executor truth。 | high | medium | EventBridge 仍只触发 refresh；executor 设计也必须以 BFF/runtime DTO 为 truth。 |
| Q-R5 | Redaction 或 raw prompt/raw connector payload 进入 executor proposal/evidence。 | high | medium | DTO/DOM/error/event/source scan 继续覆盖 token、Authorization、raw payload 和 raw prompt。 |
| Q-R6 | 文档过度声明 complete Workflow Studio、complete AgentTalkWindow、controlled executor ready 或 production-ready。 | medium | high | claim guard 扩展到 Q plan/completion note 和 source copy。 |

完整 P 阶段完成证据见 `v4_0_p_agenttalk_window_interaction_e2e_completion_note.md`。

### 6.18 V4.0-P 后未来阶段

以下阶段原本是 V4.0-P 之后的开发计划；当前已推进到 V4.0-Z final audit gate。它们仍然只是设计门禁和审计门禁，不代表 production-ready 或 executor-ready。

| 阶段 | 阶段定位 | 核心交付 | No False Green 边界 |
| --- | --- | --- | --- |
| V4.0-Q Controlled Executor Design Gate | 评估是否可以进入受控执行器实现。 | executor policy matrix、capability profile、approval gate、sandbox/rollback/kill-switch 设计、审计要求和验收计划。 | 只做设计门禁；不能声明 controlled executor ready 或 Agent executor ready。 |
| V4.0-R Production Readiness Preflight | 生产化前置差距审计。 | OAuth/SSO、多租户控制面、observability、security、secret management、production BFF deployment 的 gap 与验收计划。 | 已完成；只做 preflight；不能声明 production-ready external app support。 |
| V4.0-S Production Auth / Tenant Boundary Follow-up Design | auth / tenant boundary 设计门禁。 | identity matrix、tenant isolation matrix、service account / agent identity、OAuth / SSO gap contract、capability token binding。 | 已完成；只做 design gate；不能声明 enterprise auth、OAuth/SSO 或 tenant control plane ready。 |
| V4.0-T/U/V/W Production Follow-up Designs | token lifecycle、secret management、observability / audit retention、external app onboarding 设计门禁。 | 机器可读 follow-up contracts 和 route/claim guards。 | 已完成；不能声明 production-ready。 |
| V4.0-X/Y/Z Consolidation / Executor Gate / Final Audit | 聚合 production blockers、executor implementation blockers 和 final audit package。 | consolidation contract、executor implementation gate contract、final audit release gate contract。 | 已完成；不能声明 controlled executor ready、Agent executor ready 或 production-ready。 |

### 6.19 V4.0-R 后风险细化

V4.0-R 已把生产化风险显式登记为 open gaps，V4.0-S/T/U/V/W 已把 Auth / Tenant、Token Lifecycle、Secret Management、Observability / Audit Retention 和 External App Onboarding 方向细化为设计门禁，V4.0-X/Y/Z 已完成 consolidation、executor implementation gate 和 final audit。不能把 design gate 误写成 production-ready implementation。

| 风险 ID | 风险 | 严重度 | 概率 | V4.0-R 控制措施 |
| --- | --- | --- | --- | --- |
| R-R1 | Production Readiness Preflight 被误写成 production-ready external app support。 | critical | high | R 只产出 gap register、preflight contract 和 claim guard；不得新增 production route。 |
| R-R2 | dev/local scope guard 被误写成 production tenant isolation。 | critical | medium | 明确 tenant_id/user_id/service_account_id/agent_id 等仍为 open gaps。 |
| R-R3 | capability token lifecycle 被误写成 production-ready。 | high | medium | issuance/expiration/rotation/revocation/audit 全部登记为 gap，不新增 rotate/revoke route。 |
| R-R4 | V4.0-M operation evidence 被误写成 production audit export/retention。 | high | medium | completion note 明确 operation evidence 只是 dev/local baseline。 |
| R-R5 | V3.5 SDK/BFF/Embed 被误写成生产客户接入。 | critical | medium | external app onboarding gap 覆盖 app registration、domain verification、tenant provisioning、quota 和 offboarding。 |
| R-R6 | 文档或 UI copy 出现 enterprise auth ready / multi-tenant ready / production ready。 | medium | high | claim guard 扫描 docs/source/UI copy/completion note。 |

### 6.20 V4.0-S 后风险细化

V4.0-S 已把 auth / tenant boundary 风险细化为 identity matrix、tenant isolation matrix、service account / agent identity、OAuth / SSO gap contract 和 capability token binding design。后续阶段仍不能把这些设计门禁误写成 production auth implementation。

| 风险 ID | 风险 | 严重度 | 概率 | V4.0-S 控制措施 |
| --- | --- | --- | --- | --- |
| S-R1 | identity matrix 被误写成 enterprise auth ready。 | critical | high | 合同明确 `tenant_id/user_id/service_account_id` 是 production gap；claim guard 阻止 enterprise auth ready。 |
| S-R2 | OAuth / SSO gap contract 被误写成 OAuth ready 或 SSO ready。 | critical | medium | 每项 OAuth/SSO capability 只能是 `gap_only` 或 `planned_future`。 |
| S-R3 | tenant isolation design 被误写成 multi-tenant control plane ready。 | critical | high | isolation matrix 是 design_only，不新增 `/tenant/*` 或 `/admin/tenant/*` route。 |
| S-R4 | capability token binding 被误写成可绕过 user confirmation。 | high | medium | token binding 明确 `can_bypass_user_confirmation=false`，`source=agent` 仍不能 mutation。 |
| S-R5 | auth / tenant design 写入 V3.6 runtime contract。 | high | low | runtime boundary 明确不修改 WorkflowTemplate、WorkflowDraft、WorkflowVersion 或 StationRun。 |
| S-R6 | UI copy 出现生产认证或 OAuth/SSO 已接入误导文案。 | medium | high | frontend no-false-green test 扫描 production auth false-green copy。 |

V4.0-N 已补齐 V4.0-H 之后的 canvas editing readiness 和 V4.0-K/L/M 之后的审计闭环：

```text
AgentActionProposal
  -> AgentActionHandoff
  -> 用户显式确认
  -> Operation Panel 执行
  -> Runtime result
  -> OperationEvidence / GovernanceReview
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
apps/workflow-console/e2e/workflow-console-smoke.spec.ts
apps/workflow-console/e2e/workflow-editing-smoke.spec.ts
apps/workflow-console/e2e/workflow-canvas-bridge-smoke.spec.ts
apps/workflow-console/e2e/workflow-agent-talk-smoke.spec.ts
```

回归命令建议：

```bash
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
```

前端 package 必须持续执行：

```bash
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
```

V4.0-F 后还必须新增：

```bash
cd apps/workflow-console && npm run test:e2e
```

V4.0-G 后新增：

```text
tests/test_v4_0_editing_hardening_bff_routes.py
apps/workflow-console/src/__tests__/workflowEditingHardening.test.tsx
apps/workflow-console/e2e/workflow-editing-smoke.spec.ts
```

V4.0-H 后新增：

```text
tests/test_v4_0_canvas_runtime_bridge_bff.py
tests/test_v4_0_canvas_runtime_bridge_contract.py
tests/test_v4_0_canvas_runtime_bridge_redaction.py
apps/workflow-console/src/__tests__/canvasRuntimeBridge.test.tsx
apps/workflow-console/e2e/workflow-canvas-bridge-smoke.spec.ts
```

V4.0-I 阶段新增：

```text
tests/test_v4_0_agent_talk_stateful_bff.py
tests/test_v4_0_agent_talk_stateful_scope.py
tests/test_v4_0_agent_talk_stateful_redaction.py
tests/test_v4_0_agent_talk_patch_governance.py
apps/workflow-console/src/__tests__/agentTalkStateful.test.tsx
apps/workflow-console/e2e/workflow-agent-talk-smoke.spec.ts
```

V4.0-J 后新增：

```text
tests/test_v4_0_agent_action_proposals_bff.py
tests/test_v4_0_agent_action_policy_guard.py
tests/test_v4_0_agent_action_scope.py
tests/test_v4_0_agent_action_redaction.py
apps/workflow-console/src/__tests__/agentActionGovernance.test.tsx
apps/workflow-console/e2e/workflow-agent-governance-smoke.spec.ts
```

V4.0-K 后新增：

```text
tests/test_v4_0_agent_action_handoff_bff.py
tests/test_v4_0_agent_action_handoff_scope.py
tests/test_v4_0_agent_action_handoff_redaction.py
tests/test_v4_0_agent_action_handoff_user_confirmation.py
apps/workflow-console/src/__tests__/agentActionHandoff.test.tsx
apps/workflow-console/e2e/workflow-agent-handoff-smoke.spec.ts
```

V4.0-L 后新增：

```text
tests/test_v4_0_agent_handoff_repository.py
tests/test_v4_0_agent_handoff_lifecycle.py
tests/test_v4_0_agent_handoff_recovery.py
tests/test_v4_0_agent_handoff_audit.py
tests/test_v4_0_agent_handoff_stale_guards.py
apps/workflow-console/src/__tests__/agentHandoffLifecycle.test.tsx
apps/workflow-console/e2e/workflow-agent-handoff-recovery-smoke.spec.ts
```

V4.0-N 后新增：

```text
tests/test_v4_0_operation_evidence_bff.py
tests/test_v4_0_operation_evidence_correlation.py
tests/test_v4_0_operation_evidence_scope.py
tests/test_v4_0_operation_evidence_redaction.py
tests/test_v4_0_operation_evidence_idempotency.py
tests/test_v4_0_governance_review_panel.py
apps/workflow-console/src/__tests__/operationEvidence.test.tsx
apps/workflow-console/e2e/workflow-operation-evidence-smoke.spec.ts
tests/test_v4_0_canvas_editing_readiness_bff.py
tests/test_v4_0_canvas_editing_readiness_contract.py
tests/test_v4_0_canvas_editing_readiness_scope.py
tests/test_v4_0_canvas_editing_readiness_redaction.py
apps/workflow-console/src/__tests__/canvasEditingReadiness.test.tsx
apps/workflow-console/e2e/workflow-canvas-editing-readiness-smoke.spec.ts
```

V4.0-O 后新增：

```text
tests/test_v4_0_canvas_patch_queue_bff.py
tests/test_v4_0_canvas_projection_freshness.py
tests/test_v4_0_canvas_edge_contracts.py
tests/test_v4_0_inspector_mapping_v2.py
tests/test_v4_0_node_catalog_versioning.py
tests/test_v4_0_canvas_proposal_scope_redaction.py
tests/test_v4_0_claim_guard.py
apps/workflow-console/src/__tests__/canvasPatchQueue.test.tsx
apps/workflow-console/src/__tests__/canvasProjectionFreshness.test.tsx
apps/workflow-console/src/__tests__/inspectorMappingV2.test.tsx
apps/workflow-console/src/__tests__/nodeCatalogVersioning.test.tsx
apps/workflow-console/e2e/workflow-canvas-patch-queue-smoke.spec.ts
apps/workflow-console/e2e/workflow-inspector-mapping-smoke.spec.ts
apps/workflow-console/e2e/workflow-catalog-versioning-smoke.spec.ts
```

V4.0-P 后新增：

```text
tests/test_v4_0_agenttalk_interaction_e2e_bff.py
tests/test_v4_0_agenttalk_interaction_event_truth.py
tests/test_v4_0_agenttalk_interaction_redaction.py
tests/test_v4_0_agenttalk_interaction_scope.py
tests/test_v4_0_agenttalk_interaction_claim_guard.py
apps/workflow-console/src/__tests__/agentTalkInteractionE2E.test.tsx
apps/workflow-console/src/__tests__/agentTalkEventTruth.test.tsx
apps/workflow-console/src/__tests__/agentTalkEvidenceReview.test.tsx
apps/workflow-console/e2e/workflow-agenttalk-interaction-smoke.spec.ts
apps/workflow-console/e2e/workflow-agenttalk-event-truth-smoke.spec.ts
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
V4.0-F Browser Smoke Baseline
V4.0-G Editing Hardening
V4.0-H Canvas-to-runtime Bridge
V4.0-I AgentTalkWindow Stateful Assistant
V4.0-J AgentTalk Governance & Controlled Executor Preparation
V4.0-K Agent Action Handoff to User-Confirmed Operation Panels
V4.0-L Agent Handoff Lifecycle / Audit / Recovery Hardening
V4.0-M Operation Evidence / Governance Review
V4.0-N Canvas Editing Readiness
V4.0-O Governed Canvas Proposal Workflow
V4.0-P AgentTalkWindow Interaction E2E
V4.0-Q Controlled Executor Design Gate
```

其中 V4.0-E/F/G/H/I/J/K/L/M/N/O/P/Q 必须证明：

- UI 默认通过 BFF / SDK / hooks 调用 harnessOS。
- 不直接读 Core Store 或 WorkflowStore。
- 不新增 UI 专用后端旁路。
- 不依赖 Meeting / Knowledge / Video / external MCP。
- Board、Patch、Quality、Approval、Context、EventBridge、Canvas proposal、Agent suggestions、Agent action proposals、Agent action handoffs 和 operation evidence 均消费 V3.6/V4.0 BFF 合同。
- Scope isolation 和 redaction 通过。
- Browser smoke 证明 console 在真实浏览器中可打开、可操作、可刷新，且不直接调用 `/v1/rpc` 或 `/v1/events/subscribe`。
- Agent action proposal 只能进入 display/navigation/proposal/forbidden governance，不具备 executor / apply / publish / approval / context mutation 能力。
- Agent action handoff 只把建议交接到用户确认 operation panels，不是 executor。
- Agent handoff lifecycle、URL recovery、audit query 和 stale/expired/blocked guard 不产生 executor 行为。
- Operation evidence / governance review 是只读审计视图，不执行 mutation，也不把 EventBridge payload 当作 evidence truth。
- V4.0-O 的 patch queue、projection freshness、catalog versioning、Inspector/edge validation 和 fixture isolation 不得引入 UI-only mutation bypass。
- V4.0-Q 的 policy matrix、capability profile、approval gate、sandbox boundary、rollback / kill switch 和 future executor evidence 只是设计门禁，不得成为可调用 executor。
- V4.0-R 的 production readiness gap register 只是 preflight，不得新增 production auth、OAuth/SSO、tenant admin、token lifecycle、quota、audit export 或 onboarding route。
- V4.0-S 的 production auth / tenant boundary design 只是设计门禁，不得新增 OAuth/SSO/OIDC/SAML/callback、tenant admin、token lifecycle、production auth middleware、tenant control plane 或 onboarding route。
- V4.0-T/U/V/W/X/Y/Z 也必须继续复用 BFF / SDK / hooks / V3.6 runtime contract，不得新增 UI-only mutation bypass。

V4.0-Z 是 final audit / release gate；它只证明 governed dev/local Workflow Console and production readiness design gates ready for implementation review。

## 13. 出门声明

V4.0-Z 完成后可以声明：

```text
V4.0-Z complete: V4.0 final audit package ready for review.
V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.
```

仍不能声明：

```text
production-ready external app support
complete AgentTalkWindow
complete Workflow Studio
controlled executor ready
Agent executor ready
autonomous workflow editing ready
production-ready external app support
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
enterprise auth ready
multi-tenant control plane ready
OAuth ready
SSO ready
```
