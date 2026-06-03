# V4.x Headless 当前差距分析

文档状态：V4-U9 最终人工验收与 V5 移交包完成后的 V4.x gap 文档；UX-01 到 UX-12 全部有可审计证据，但仍不能声明生产级或无限制多 Agent 编排。

本文是 V4.1 之后的 V4.x 前向主工作文档。V4.0 的 gap 文档和 drawio 图现在只作为历史参考，不再作为 V4.x 后续开发的主线依据。

配套图：

```text
docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
```

历史参考：

```text
docs/design/V4.0/v4_0_current_gap_analysis.md
docs/design/V4.0/v4_0_current_gap_analysis.drawio
```

当前允许基线：

```text
V4-U5A complete: scenario evidence archive ready for review.
V4-U5B complete: experience state projection read-model ready for shared workflow heads.
V4-U5C complete: Mission Console closed loop ready for dev/local validation.
V4-U5D complete: Review Console and Evidence Chain baseline ready for review.
V4-U5E complete: real LLM-backed local technical document workflow ready for dev/local validation.
V4-U5 complete: unified scenario path acceptance package ready for V4-U6 gate review.
V4-U6 complete: V4 unified dev/local experience baseline ready for review.
V4-U7 complete: real provider-backed multi-agent scenario evidence ready for review.
V4-U8 complete: V4 dev/local closure package ready for human acceptance.
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
```

当前仍禁止声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 0. V4.x Unified Experience Rebaseline

V4.x 后续不再继续把完整 Web 低代码 Studio 当作当前主线，而是收敛为：

```text
Headless Workflow Core
+ Mission Console
+ Workflow Blueprint
+ Runtime Report
+ Review Console
+ Evidence Chain
```

这次调整不是废弃 V4.1-V4.6，而是把已经完成的 dev/local 能力统一到一条用户体验主线：

```text
用户说目标
 -> Mission Console 捕获意图
 -> 生成 WorkflowSpec / Diff
 -> Workflow Blueprint 理解结构
 -> 用户确认
 -> Runtime Report 观察运行
 -> Review Console 做局部重跑 / 修复 / 确认
 -> Evidence Chain 审计复盘
```

新增中间层：

| 模块 | 状态 | 作用 |
| --- | --- | --- |
| Interaction Orchestrator | 绿色【新增】【V4-U2】 | 统一多 Head 用户意图、可用动作和 handoff。 |
| Experience State Machine | 绿色【新增】【V4-U1】 | 统一 Mission Console、Blueprint、Report、Review、Evidence 的状态语义。 |
| Agent Policy Layer | 绿色【新增】【V4-U2】 | 集中约束 source=agent 不能执行 mutation。 |
| Runtime Capability Matrix | 绿色【新增】【V4-U3】 | 明确 supported / partial / planned / unsupported，防止虚假验收。 |
| Report Schema | 绿色【新增】【V4-U3】 | 统一 Drawio、HTML、TUI、Thin Web 的只读投影。 |
| WorkflowSpec Registry | 绿色【新增】【V4-U2】 | 管理 WorkflowSpec hash、schema version 和 runtime refs，但不替代 runtime truth。 |

当前收口阶段：

| 阶段 | 状态 | 目标 |
| --- | --- | --- |
| V4-U5C Mission Console Closed Loop | 绿色【新增】 | Mission Console 已形成 dev/local 闭环证据。 |
| V4-U5D Review Console And Evidence Chain | 绿色【新增】 | Review Console handoff 与 Evidence Chain 只读审计已归档。 |
| V4-U5E Real LLM Local Document Workflow | 绿色【新增】 | 已真实读取本地 Markdown 并调用 LLM 生成总结。 |
| V4-U5 Scenario Path Acceptance Package | 绿色【新增】 | UX-01 到 UX-12 reality-check 已形成 U6 输入包。 |
| V4-U6 Unified Experience Gate | 绿色【新增】 | 已完成，之前接受 UX-08 / UX-09 / UX-10 PARTIAL 风险。 |
| V4-U7 Real Multi-Agent Runtime Evidence | 绿色【新增】 | 已补齐 UX-08 / UX-09 / UX-10 provider-backed dev/local 运行证据。 |
| V4-U8 V4 Closure Manual Acceptance | 绿色【新增】 | 已生成 dev/local 收口包和人工验收代理报告。 |
| V4-U9 Final Human Acceptance And V5 Handoff | 绿色【新增】 | 已生成最终人工验收 HTML、PRD 规格复核、false-green 审计和 V5 planning brief。 |

最新 reality-check：

```text
PASS: 12
PARTIAL: 0
FAIL: 0
BLOCKED: 0
allow_enter_v4_u6: true
requires_human_proceed_decision: false
```

V4-U7 后的重点证据：

```text
UX-08 串行多 Agent 视频工作流：real_runtime PASS，provider-backed dev/local station artifacts、rerun、downstream stale。
UX-09 并行罗马广场讨论：real_runtime PASS，provider-backed persona artifacts、synthesis、attribution、contradiction review。
UX-10 长时工程任务工作流：real_runtime PASS，provider-backed 11-stage artifacts、code_review rerun、downstream stale。
```

UX-12 当前状态：

```text
UX-12 真实 LLM 本地技术文档解析：real_runtime PASS。
证据包含 LocalFolderReadAuthorization、实际 Markdown 读取、provider/model/provider_config_source、LLM-backed artifacts、quality_report 和 Evidence Chain。
```

## 1. 为什么 V4.x 文档里不再把七平面放在主叙事中心

结论：七平面没有废弃。它仍然是底层事实源、协议边界和治理边界。变化的是 V4.x 的产品主线从“完整 Web 低代码 Studio”转向“Headless Core + 多 Head 输出”。

V4.0 的问题是：

```text
V3.6 已有 workflow runtime 后，怎样把它产品化成 Workflow Console / Workflow Studio / AgentTalkWindow。
```

所以 V4.0 必须重点讲七平面：

```text
Plane-0 Product UI
Plane-1 Application Adaptation Layer
Plane-2 Workflow Runtime Layer
Plane-3 Harness Core
Plane-4 Runtime Adapter & Governance
Plane-5 Domain Pack / Descriptor Plane
Plane-6 Connector / Tool / Store / Asset Plane
```

V4.x 现在的问题变成：

```text
怎样让同一套工作流事实源被 Mission Console、Workflow Blueprint、Runtime Report、Review Console、Evidence Chain、TUI、Drawio、HTML Report、Thin Web Console 和未来业务 App 复用。
```

因此 V4.x 文档主叙事切换为 Unified Headless Experience，但七平面仍是约束层：

```text
Headless 多 Head 和 Unified Experience 是产品交互形态。
七平面是底层架构和治理边界。
两者不是互斥关系。
```

## 2. 架构平面涂色规则

后续每个阶段结束后同步更新 gap 文档时，必须重新应用以下涂色规则：

```text
灰色【旧有不用改】：已经存在，并且当前 V4.x 阶段不需要改动。
黄色【旧有需改】：已经存在，但为了 V4.x 目标体验需要扩展、收敛或重构。
绿色【新增】：V4.x Headless-first 路线新增的组件、输出物或交互入口。
红色【禁止误报】：不得声明完成的能力或禁止路径。
```

黄色和绿色模块必须在标题下方加粗标明负责阶段，例如：

```text
【V4.2-A】
【V4.2-C】
【V4.3】
【V4.4】
【V4.5】
【V4.6】
```

如果一个模块是后续阶段才会处理，不能只写“需改动”，必须写清楚它不是当前阶段的交付范围。

## 3. 新旧架构区别

| 层面 | 旧 V4.0 主线 | 新 V4.x 主线 | 状态 |
| --- | --- | --- | --- |
| 产品主线 | 完整 Web Workflow Console / Studio / AgentTalkWindow 前置体验 | Headless Core + Mission Console + Blueprint + Runtime Report + Review Console + Evidence Chain | 黄色【旧有需改】【V4-U0】 |
| UI 定位 | Web Studio 是主要交互载体 | Mission Console 是主入口，Thin Web Console 是观察和受限确认入口 | 黄色【旧有需改】【V4-U4】 |
| 架构边界 | 七平面作为主架构图 | 七平面作为底层治理和事实源边界 | 灰色【旧有不用改】 |
| 工作流定义 | WorkflowDraft / WorkflowVersion 直接作为主要设计对象 | 新增 WorkflowSpec 作为便携定义和审查文件 | 绿色【新增】【V4.2-A】 |
| 可视化 | Web Canvas / Board | Workflow Blueprint / Drawio、Runtime Report / HTML、Evidence Chain | 绿色【新增】【V4-U3】 |
| 操作入口 | Web 面板和 BFF operation panels | Mission Console + Review Console + governed handoff | 绿色【新增】【V4-U2/V4-U4】 |
| 持久变更 | user_confirmed 的 governed BFF / patch path | 继续走 governed BFF / patch path | 灰色【旧有不用改】 |
| Agent 权限 | propose / explain / handoff / navigate | 仍只能 propose / explain / handoff / navigate | 灰色【旧有不用改】 |
| 通用运行时 | V4.0 只做 design gate，不实现 controlled executor | V4.2-B 已完成实现门禁；V4.2-C 才允许最小受控运行时实现 | 黄色【旧有需改】【V4.2-C】 |
| 生产能力 | 只做 production readiness design gates | 仍非 production-ready | 红色【禁止误报】 |

## 4. 当前目标架构

V4.x 当前目标架构是：

```text
绿色【新增】【V4-U4】Mission Console / TUI
  -> 绿色【新增】【V4-U2】Interaction Orchestrator / Agent Policy Layer
  -> 绿色【新增】【V4-U5B】ExperienceStateProjection / TUI state timeline
  -> 绿色【新增】【V4.2-A】WorkflowSpec
  -> 灰色【旧有不用改】governed BFF / WorkflowPatch proposal
  -> 灰色【旧有不用改】WorkflowDraft / WorkflowVersion
  -> 绿色【新增】【V4.2-C】WorkflowInstance / StationRun controlled runtime MVP
  -> 绿色【新增】【V4.2-A】Artifact / QualityEvaluation / OperationEvidence evidence export
  -> 绿色【新增】【V4-U3】Workflow Blueprint / Runtime Report
  -> 黄色【旧有需改】【V4-U5D】Review Console / Evidence Chain
```

解释：

1. 绿色【新增】【V4.2-A】`WorkflowSpec` 是便携式工作流定义和审查文件，可生成 `workflow.yaml`、`workflow.json` 和 `workflow.schema.json`。
2. 灰色【旧有不用改】`WorkflowDraft`、`WorkflowVersion`、`WorkflowPatch` 仍是后端设计事实源和治理修改路径。
3. 绿色【新增】【V4.2-C】`WorkflowInstance`、`StationRun` 已具备 dev/local 受控 start、rerun、attempt history、downstream stale propagation 的最小 MVP 包装。该包装仍不是 Agent executor 或 production runtime。
4. 绿色【新增】【V4.2-A】`Artifact`、`QualityEvaluation`、`OperationEvidence` 已导出给 Drawio / HTML / TUI 的 evidence package。
5. 绿色【新增】【V4-U2】Interaction Orchestrator 统一多 Head 意图，但不直接写 runtime。
6. 绿色【新增】【V4-U5B】ExperienceStateProjection 统一状态标签、可用动作、stale reason 和 source refs，但不保存 runtime truth。
7. 绿色【新增】【V4-U3】Workflow Blueprint / Runtime Report / Evidence Chain 是只读投影。
8. 灰色【旧有不用改】Agent 只能 propose / explain / handoff / navigate，不能 apply / publish / run / rerun / approval.respond / context.update / connector execute。

## 5. 七平面与 Headless 架构的对应关系

| 七平面 | V4.x 中的作用 | 状态 |
| --- | --- | --- |
| Plane-0 Product UI / Workflow Studio / AgentTalkWindow | 降级为 Thin Web Console / Reference UI；新增 Mission Console、Blueprint、Runtime Report、Review Console、Evidence Chain | 黄色【旧有需改】【V4-U4】 + 绿色【新增】【V4-U1-U5】 |
| Plane-1 Application Adaptation Layer | BFF、SDK、hooks、EventBridge 继续保留；新增 Interaction Orchestrator、WorkflowSpec adapter 与 Report projection | 灰色【旧有不用改】 + 绿色【新增】【V4-U2/V4-U3】 |
| Plane-2 Workflow Runtime Layer | Draft / Version / Patch 保留；Instance / StationRun 已新增 V4.2-C dev/local controlled runtime wrapper | 灰色【旧有不用改】 + 绿色【新增】【V4.2-C】 |
| Plane-3 Harness Core | Job、Artifact、Approval、Trace、Policy、Scope 保留；Evidence export package 已在 V4.2-A 基于 V4.1 local workflow path 生成 | 灰色【旧有不用改】 + 绿色【新增】【V4.2-A】 |
| Plane-4 Runtime Adapter & Governance | 既有 governance gate 保留；controlled runtime baseline 已完成 dev/local MVP | 灰色【旧有不用改】 + 绿色【新增】【V4.2-C】 |
| Plane-5 Domain Pack / Descriptor | Local Knowledge descriptor 保留；AgentDescriptor / Persona / Engineering stage 后续扩展 | 灰色【旧有不用改】 + 黄色【旧有需改】【V4.3-V4.5】 |
| Plane-6 Connector / Tool / Store / Asset | secret / token hygiene 保留；dev/local artifact sandbox 已纳入 V4.2-C 验收，policy-controlled connector/model invocation 仍是后续扩展 | 灰色【旧有不用改】 + 绿色【新增】【V4.2-C】 + 黄色【旧有需改】【V4.3+】 |

简化理解：

```text
七平面回答：事实源在哪里，谁有权修改，治理边界在哪里。
Headless 架构回答：用户通过哪些入口定义、查看、运行、审计工作流。
```

## 6. 当前已支持能力

【旧有】当前已支持到 dev/local 级别：

1. V4.1 本地递归 Markdown 总结工作流。
2. fixture-backed 本地文件夹授权、调试扫描、Markdown 解析。
3. 子文件夹总结、总览总结、质量报告、Artifact 查看、Evidence 查看。
4. V4.1 local workflow path 上的 proposal-first governance 和 user-confirmed operation。
5. Workflow Console 的 BFF-only 浏览器边界。
6. Headless-first 路线文档。
7. V4.2-A WorkflowSpec YAML/JSON/schema。
8. V4.2-A TUI transcript / command contract evidence。
9. V4.2-A Drawio workflow/status/artifact lineage 输出。
10. V4.2-A 只读 HTML reports 和 Thin Web Console 观察入口。
11. V4.2-A exported runtime/evidence package，来源为 V4.1 local workflow path。
12. V4.2-B controlled runtime design gate contract、acceptance、audit 和 completion note。
13. V4.2-C BFF-only controlled runtime start / rerun / continue wrapper。
14. V4.2-C attempt history、downstream stale、runtime evidence、timeout baseline、kill switch baseline。
15. V4.2-C controlled-runtime evidence package、Drawio 和 HTML reports。
16. V4.3 串行多 Agent 视频工作流 deterministic dev/local MVP。
17. V4.4 并行多 Agent 罗马广场讨论 deterministic dev/local MVP。
18. V4.5 长时工程任务 deterministic dev/local MVP。
19. V4-U7 provider-backed UX-08 / UX-09 / UX-10 real_runtime evidence。
20. V4-U8 manual acceptance proxy and closure package。
21. V4-U9 final human acceptance and V5 handoff package。
22. V4.6 governed Agent Workflow Builder UX dev/local baseline。
23. V4-U5A/UX-12 scenario evidence archive。
24. V4-U5B ExperienceStateProjection、AvailableAction resolver、state transition validator、TUI state timeline。

【需改动】当前还不支持：

1. Agent executor 或 autonomous mutation。
2. 真实串行 / 并行 multi-Agent runtime。
3. 长时工程任务看板。
4. production auth、tenant control plane、production filesystem permissions、production external app support。
5. production-grade connector/model invocation policy。
6. production-grade Mission Console and Review Console multi-tenant hardening。
7. production-grade Evidence Chain retention / export。
8. production-grade real LLM provider lifecycle, quota, audit export, and secret rotation。
9. V5 production productization plan execution。

## 7. V4.2-A 修正后的范围

【已完成】V4.2-A 已交付：

1. `workflow.yaml`、`workflow.json`、`workflow.schema.json`。
2. 严格的 WorkflowSpec validation contract。
3. V4.1 local workflow 的 TUI transcript 和 command UX contract。
4. read/spec/report commands：create、diff、status、artifacts list、quality report、evidence show。
5. Drawio 输出：workflow topology、runtime status、artifact lineage。
6. HTML 报告：workflow board、artifacts、quality、evidence。
7. Thin Web Console 中打开生成的 HTML / Drawio / evidence package。
8. 从既有治理来源导出的 evidence package。

V4.2-A evidence package:

```text
docs/design/V4.2/evidence/headless-interaction/
```

【禁止误报】V4.2-A 不能声明：

1. generic controlled runtime。
2. generic workflow run implementation。
3. generic station rerun implementation。
4. controlled executor ready。
5. Agent executor ready。
6. full Web Workflow Studio ready。

## 8. V4.2-B/C 延后运行时范围

【已完成】V4.2-B 已完成：

1. 受控运行时实现前门禁。
2. 机器可读 contract。
3. V4.2-C 真实数据验收标准。
4. runtime evidence contract。
5. route / capability guard。
6. PRD / architecture / no-false-green audit。

【已完成】V4.2-C 已完成：

1. dev/local user-confirmed workflow start。
2. dev/local user-confirmed station rerun。
3. StationRun attempt history。
4. downstream stale propagation。
5. artifact read/write sandbox baseline。
6. runtime result evidence。
7. timeout baseline。
8. kill switch baseline。

【需改动】后续阶段才处理：

1. policy-controlled connector / model invocation 的生产化扩展。
2. multi-Agent workflow runtime。
3. long-running engineering workflow runtime。

必须继续保留：

```text
source=agent cannot execute mutation
user_confirmed=true required for durable mutation
high-risk actions remain approval-gated
EventBridge refresh-only
executor reads only redacted or approved inputs
```

## 9. 当前 Gap Register

| 缺口 | 当前状态 | 目标状态 | 阶段 | 标记 |
| --- | --- | --- | --- | --- |
| WorkflowSpec schema | 已完成 V4.2-A evidence | strict schema + validator | V4.2-A | 绿色【新增】 |
| TUI / Command Palette | 已完成 transcript / command contract | 可用的本地 TUI contract | V4.2-A | 绿色【新增】 |
| Drawio renderer | 已完成 deterministic generated drawio files | deterministic generated drawio files | V4.2-A | 绿色【新增】 |
| HTML reports | 已完成 generated read-only reports | generated read-only reports | V4.2-A | 绿色【新增】 |
| Evidence package | 已从 V4.1 local workflow path 导出 | 从治理来源导出 package | V4.2-A | 绿色【新增】 |
| Controlled runtime design gate | 已完成 V4.2-B contract / acceptance / audit | implementation review ready | V4.2-B | 绿色【新增】 |
| Generic workflow start | 已完成 dev/local controlled runtime wrapper | user-confirmed runtime start | V4.2-C | 绿色【新增】 |
| Generic station rerun | 已完成 dev/local rerun + attempt history | rerun + attempt history | V4.2-C | 绿色【新增】 |
| Downstream stale propagation | 已完成 dev/local stale model | runtime stale propagation model | V4.2-C | 绿色【新增】 |
| Controlled runtime | 已完成 dev/local governed MVP | governed controlled runtime MVP | V4.2-C | 绿色【新增】 |
| Serial multi-Agent workflow | 已完成 provider-backed dev/local video workflow evidence | video workflow MVP + U7 evidence | V4.3 / V4-U7 | 绿色【新增】 |
| Parallel deliberation workflow | 已完成 provider-backed dev/local Roman forum evidence | Roman forum MVP + U7 evidence | V4.4 / V4-U7 | 绿色【新增】 |
| Long-running engineering workflow | 已完成 provider-backed dev/local engineering evidence | durable engineering task board + U7 evidence | V4.5 / V4-U7 | 绿色【新增】 |
| Agent workflow builder | 已完成 governed proposal / explain / handoff UX baseline | governed workflow builder UX | V4.6 | 绿色【新增】 |
| Unified experience state machine | 合同已新增 | multi-head shared state semantics | V4-U1 | 绿色【新增】 |
| Interaction Orchestrator | 合同已新增 | multi-head intent / action / handoff contract | V4-U2 | 绿色【新增】 |
| Shared report schema | 合同已新增 | Drawio / HTML / TUI / Thin Web shared projection | V4-U3 | 绿色【新增】 |
| Mission Console | PRD 与 transcript 已新增 | main command / natural language entry | V4-U4 | 绿色【新增】 |
| Scenario Evidence Archive | UX-01 到 UX-12 result-summary 已新增；UX-12 当前 real_runtime PASS | 可审计 evidence archive | V4-U5A / V4-U5E | 绿色【新增】 |
| Experience State Projection | 已新增 read-model helper 和 schema 严格性测试 | shared projection for all workflow heads | V4-U5B | 绿色【新增】 |
| Mission Console Closed Loop | transcript 已补 AwaitingConfirmation 和 user_confirmed 证据 | closed-loop dev/local path | V4-U5C | 绿色【新增】 |
| Review Console And Evidence Chain | Evidence report schema 已收紧为只读动作 | read-only evidence + user-confirmed handoff | V4-U5D | 绿色【新增】 |
| Unified scenario acceptance | V4-U7 reality-check 已显示 UX-01 到 UX-12 全部 PASS | scenario path acceptance package | V4-U7 | 绿色【新增】 |
| Manual acceptance package | V4-U8 已生成静态 HTML 和 machine-readable acceptance data | human acceptance proxy | V4-U8 | 绿色【新增】 |
| Final human acceptance and V5 handoff | V4-U9 已生成最终人工验收 HTML、PRD 规格复核和 V5 planning brief | final acceptance package | V4-U9 | 绿色【新增】 |
| Runtime Capability Matrix | 已新增 schema 和审计文档 | supported / partial / planned / unsupported 能力边界 | V4-U5A/U6 | 绿色【新增】 |
| WorkflowSpec Registry | 已新增 schema 和审计文档 | spec hash / runtime refs read model | V4-U5A/U6 | 绿色【新增】 |
| Production support | design gaps only | future production hardening | Post V4 | 红色【禁止误报】 |

## 10. 规格漂移和虚假验收评估

规格漂移风险：

```text
修正前：MEDIUM
修正后：LOW
```

原因：文档已经明确 V4 收口在 dev/local 体验证据、最终人工验收和 V5 planning handoff，不把 production hardening 回填到 V4。

虚假验收风险：

```text
当前：MEDIUM
```

原因：V4-U5E 已把 UX-12 从 BLOCKED 推进为 real_runtime PASS，V4-U7 已把 UX-08 / UX-09 / UX-10 从 deterministic-only PARTIAL 推进为 provider-backed real_runtime PASS。剩余风险主要是把 dev/local 场景证据误读为 Agent executor、production runtime 或 full multi-Agent orchestration。

继续推进条件：

```text
V4.1-V4.6 Headless-first dev/local 路线已完成，V4-U5 验收包已完成，V4-U6 统一体验收口门禁已完成，V4-U7 已补齐真实 provider-backed 多 Agent 场景证据，V4-U8 已生成可人工验收的 closure package，V4-U9 已生成最终人工验收与 V5 handoff package。下一阶段若进入 V5 production productization planning，必须继续保留 dev/local 边界，不能把它们写成 full multi-Agent orchestration。
```

停止条件：

```text
需要 generic controlled execution runtime
需要 Agent executor
需要 production auth
需要 full Web Studio 作为前置条件
Spec Drift Risk = HIGH
False Green Risk = HIGH
```
