# harnessOS 当前架构与目标架构差异

配套 draw.io 图：`docs/architecture/current-vs-target-gap.drawio`

## 1. 总体差异

当前项目处在 Core v1.5-E Runtime Adapter 收敛完成阶段：已经有可运行的普通 CLI、`--oh` TUI、`harness run`/`python3 -m cli.main run` headless 调用、FastAPI `/v1/runs`/SSE、`/v1/rpc`、stdio JSONL、基础 schema、基础 tools，以及从 OpenHarness 迁移来的 hooks、permissions、MCP、swarm 等代码。`apps/gateway` 已完成第一轮去 ohmo 化，具备项目自有协议模型、session/turn 生命周期、snapshot/event log、session 查询、transcript replay、active turn cancellation、artifact registry、TraceStore、ApprovalStore、PolicyEvaluator、RetryStore、Secret Masker、locked local persistence、Lead Orchestrator、DomainWorkflow Registry、Pack Registry、Job Service MVP、Tool Policy Middleware MVP、Runtime Adapter handle/protocol MVP 和 CLI/smoke 回归基线。FastAPI API 层已移除 route 模块级 `_gateway` 单例，改为 `app.state.gateway_service` + dependency injection，并支持 `create_app(gateway_service=...)` 注入。Core v1.5-A 新增 `core.protocol`、`core.stores` 和 `CoreAppService`，已具备 `Session / Thread / Turn / Item / Job / Artifact / Approval / Trace / Retry / Connector` 模型与 `CoreSQLiteStore` 基础 CRUD/legacy import。现有 Gateway 执行链路已通过 `CoreAppService` 写入 Core SQLite，其中 `session.start/session.close`、`turn.started/item.delta/turn.completed/turn.failed/turn.interrupted`、artifact/trace/approval/retry/job 均已进入 Core-native mutation/conversion path；`GatewayRuntimePool` 与 `GatewayService` 不再暴露 `CoreRuntimeRecorder`。查询面包括 `session.get`、`thread.list`、`turn.get`、`turn.items`、`core.artifact.list`、`core.trace.list`、`core.approval.list`、`core.retry.list`、`core.job.list`、`job.list/get/cancel`、`pack.list`、`pack.get`。执行面新增 `tools.policy_guard`，builtin tools 和 Core engine tool loop 可在工具真实执行前阻断未审批写入/发送/发布类工具；Gateway session 已通过 `RuntimeHandle` + `RuntimeAdapter` 启停 Simple/OpenHarness runtime，上层不再直接创建 runtime 对象。

会议领域服务已经在相邻项目 `meeting-voice-assistant` 中完成 MCP Phase1：提供 `meeting_process_file`、`meeting_analyze_text`、`meeting_build_minutes`、`meeting://agent-guide`、`meeting_process_recording` prompt，并支持无 Python `mcp` 包的 JSON-RPC stdio fallback。harnessOS 已通过 `meeting.*` Gateway RPC、`turn.start(domain=meeting)` 和普通聊天/headless 音频路径自动识别接入该服务，并使用 `/Users/Zhuanz/Desktop/workspace/音频资料` 下真实音频完成自动验收。会议 workflow 现在通过 Lead Orchestrator/Workflow Registry 进入，并会把 `transcript`、`analysis`、`result`、`minutes` 登记为 harnessOS artifact，通过 `artifact.list/get/read/register` 暴露。针对较长音频导致 MCP stdio 单行 JSON 响应超过默认 `readline()` 限制的情况，Gateway 已把 Meeting MCP stdio 读取上限提高到 128MB；针对下游分析器 chunk/limit 限制，也已增加“只转写 -> 压缩转写分析 -> 生成纪要”的降级路径，避免把底层异常直接暴露给用户。知识场景已有 KnowledgeWorkflow MVP，可通过显式 `domain=knowledge` 或知识关键词进入检索链路。

目标架构已升级为 **V2.0 Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform**：CLI/Web/Headless/Bot client 通过统一协议进入，Core 负责 `Session / Thread / Turn / Item`、Runtime Adapter、Store、Artifact、Trace、Approval、Policy、Retry、Job、Connector 和 Domain Pack。Phase 1/2/3-A 与 Core v1.5-A/B/C/D/E 已证明 Gateway、工作流、治理 primitives、pack 可见性、job 记录、工具执行治理和 runtime adapter 边界可以运行；下一阶段要继续把旧 Gateway session/event stores、background Job Worker、pack-owned assembly、Connector Registry 和 adapter-level governance injection 收敛为 Core-native 服务，并允许破坏旧 Gateway method 命名和响应结构。

V2.0 已确认的目标决策：

- Core 优先，大重构。
- SQLite 优先，legacy `.harnessos` JSON/JSONL 双读/导入迁移。
- 正式引入 `Session / Thread / Turn / Item`。
- meeting/knowledge 已迁移为 manifest-backed active Domain Pack。
- investment/interview/video_studio 第一阶段已做 manifest stub。
- 会议真实音频仍是第一阶段端到端验收主场景。
- `docs/design/V2.0/harnessos_architecture_master_spec.md` 作为目标架构主干，`docs/architecture/harnessos_target_architecture_v2.md` 作为落地版目标架构说明。
- V2.0 是目标，不代表当前代码已完成；当前代码基线仍是 Core v1.5-E。

## 1.1 V2.0 设计质量判断

V2.0 master spec 质量较高，适合采纳为正式目标架构，原因是它明确了 Core、Protocol App Server、Runtime Adapter、Domain Pack、Connector/Tool Plane 和 Store Layer 的边界，并坚持 Core 不带业务、Runtime 可替换、治理深入执行层、重要对象可追踪。它和当前 Core v1.5-E 方向一致，不需要推翻已完成工作。

但该设计仍是总体蓝图，不是接口冻结规格。当前已识别的设计缺陷是：

- JSON-RPC method、event、error code、状态机和兼容策略未冻结。
- Pack manifest 缺 workflow/skill/connector/policy bundle 的装配语义、版本兼容、冲突处理和启停机制。
- Job Worker 缺 create/run/progress/events/cancel/resume/failure_context 的完整状态机。
- 治理链路缺执行顺序定义，尤其是 turn/tool/job/artifact/retry 之间的 policy、approval、trace 绑定规则。
- Runtime Adapter 目标接口比当前 MVP 更大，需要渐进扩展，不能直接推翻 `RuntimeHandle`。
- 多租户只是字段预留，仍缺 user/tenant 权限隔离、artifact 访问边界、connector secret scope 和 pack scope。
- 顶层目录重组风险较高，短期不做大搬迁，先用 service facade 和 adapter 收敛边界。

## 2. 分层差异

| 层级 | 当前状态 | 目标状态 | 关键差距 |
| --- | --- | --- | --- |
| 用户入口 | 普通 CLI、`--oh` TUI、headless `run`、REST、SSE、`/v1/rpc`、stdio JSONL 可用 | CLI、Web、Headless Test、未来 IM/Bot 共用协议语义 | Web 产品入口与 Bot 尚未接入 |
| 协议边界 | `apps/gateway` 具备 `RpcRequest` / `RpcResponse` / `GatewayEvent` 和 initialize/session/turn/artifact/trace/approval/policy/retry/pack/job 方法，含 session.list/read/transcript、artifact.list/read、trace.list/get、approval.request/list/get/approve/reject、policy.evaluate、turn.retry、pack.list/get、job.list/get/cancel；FastAPI 入口已使用 app-scoped GatewayService DI；Core 查询面已通过 `CoreAppService` 覆盖 session/thread/turn/items/artifact/trace/approval/retry/job，session/turn/item/artifact/trace/approval/retry/job 已进入 Core-native mutation/conversion path | V2.0 Core-native App Server，包含 session/thread/turn/item/artifact/trace/approval/policy/retry/job/pack/workflow/connector 方法 | Job 仍是同步记录型 MVP；Pack 仍是 manifest MVP；Connector Registry 未一级化；旧 Gateway 方法允许破坏性升级 |
| Runtime Adapter | `core.runtime_adapter` 已提供 `RuntimeHandle`、`RuntimeAdapter`、`SimpleRuntimeAdapter`、`OpenHarnessRuntimeAdapter`；`GatewayRuntimePool` 通过 adapter start/invoke/stream/continue/close 管理 session，并保留 snapshot、events、transcript、active turn cancellation、policy preflight 和 retry context 续跑 | V2.0 Runtime Adapter Protocol，OpenHarness/SimpleRuntime/DeepAgents 只是实现，上层 Core 不暴露内部对象 | 已完成 adapter 边界 MVP；仍缺 adapter 级 tool metadata/approval coordinator 注入、统一事件规范、通用失败 workflow retry 和真正异步 Job worker |
| Runtime 内核 | Deep Agents 优先、SimpleRuntime 降级，OpenHarness TUI 可用 | build_runtime、RuntimeBundle、QueryEngine、ToolRegistry、MCP、Hooks、Permissions 稳定接入 | 需要统一 OpenHarness/Deep Agents 接入边界 |
| 编排层 | Lead Orchestrator MVP、DomainWorkflow Registry、Pack Registry、MeetingDomainWorkflow、KnowledgeWorkflow 已接入；`workflow.list` 可查看注册 workflow 与 pack 元数据；`pack.list/get` 可查看五个 pack | V2.0 Domain Pack + Workflow Engine + Intent Router + SubAgent Registry + Skill Registry | pack 已可见，但 workflow/skill/connector/policy 仍未完全由 pack 装配 |
| 执行与治理 | workspace/kb/artifact 基础工具；部分 hooks/permissions/MCP 代码已迁移；Meeting MCP 产物已登记为 artifacts；Trace/Approval/Policy/Retry/Secret/Persistence/Job/Tool Policy MVP 已完成；artifact/trace/approval/retry/job 已通过 CoreAppService 写入 Core SQLite | V2.0 Store abstraction、Job Worker、Tool Policy Middleware、Connector Registry、Artifact lineage | 旧治理 Store 仍作为兼容 runtime 源；tool policy 仍未自动生成 approval；Job 仍非后台队列；Connector/Pack 装配仍未一级化 |

## 3. 最重要的架构缺口

1. **协议缺口**  
   项目自有协议层已完成本地 service、FastAPI `/v1/runs`/SSE、`/v1/rpc`、stdio JSONL、artifact RPC、trace RPC、approval RPC、policy RPC、turn.retry、Secret Hygiene、统一错误码第一版和 app lifecycle Gateway DI。下一步应补多 worker 状态一致性和 job 方法。

2. **会话缺口**  
   当前已有 `session.start -> turn.start -> turn.completed -> session.close` 生命周期，以及 snapshot resume、event log、session.list/read、transcript replay 和 policy-blocked turn retry。下一步需要强化通用失败 workflow retry 和更完整的恢复语义。

3. **业务缺口**  
   当前已经具备显式 `meeting.*` RPC、`turn.start(domain=meeting)`、会议音频路径自动路由、Workflow Registry、Pack Registry 和 KnowledgeWorkflow MVP；普通聊天/headless 可以直接触发真实音频会议分析，`pack.list/get` 已可看到 meeting、knowledge、investment、interview、video_studio。目标仍需要 SubAgent Registry、LLM intent router、workflow DSL 和更完整的 pack-owned assembly。interview workflow 本阶段暂缓。

4. **治理缺口**  
   artifact registry、trace/audit、approval、policy preflight、retry context、secret hygiene 已具备最小登记、读取、查询、拦截、续跑和脱敏能力；artifact/trace/approval/retry 已通过 CoreAppService 写入 Core SQLite。job service、完整 DLP、connector governance 仍未形成产品级服务。目标架构把它们作为 first-class primitives。

5. **兼容风险**  
   仓库中同时存在 `openharness.*` 和 `harnessOS.openharness.*` 兼容路径。此前 TUI 无输出就是同一事件类被双模块加载导致的 `isinstance` 失败。后续应逐步收敛命名空间。

6. **平台化缺口**  
   Core v1.5-B 已把 meeting/knowledge 抽成 manifest-backed active pack，并把 investment/interview/video_studio 作为 stub pack 挂载。剩余差距是 pack 目前只提供 manifest、查询和 workflow 元数据关联，尚未拥有 workflow/skill/connector/policy bundle 的完整装配能力。

## 4. 建议推进顺序

1. 已完成：项目自有协议模型、headless CLI、Gateway session/turn 最小闭环、基础事件归一化。
2. 已完成：`session.resume`、`session.events`、`turn.continue`、`turn.interrupt`、snapshot、event log、FastAPI `/v1/runs` 与 SSE。
3. 已完成：`GatewayRuntimePool` 支持 OpenHarness `RuntimeBundle` 优先与 SimpleRuntime fallback。
4. 已完成：transcript replay、session.list/session.read、stdio JSONL server。
5. 已完成：真实运行中取消、headless CLI 回归测试、真实模型 smoke 标记、RPC/stdio 同构测试。
6. 已完成：`meeting.*` Gateway RPC 接入 Meeting MCP，并用 `/Users/Zhuanz/Desktop/workspace/音频资料` 真实音频完成验收。
7. 已完成：`turn.start(domain=meeting)` 和普通会议音频路径自动进入 meeting workflow，聊天/headless 验收 session 为 `meeting_8e8d3499`。
8. 已完成：将 minutes/transcript/analysis/result 纳入 harnessOS Artifact Registry，并通过 `artifact.register/list/get/read` Gateway RPC 暴露。
9. 已完成：通用 Lead Orchestrator、DomainWorkflow Registry、MeetingDomainWorkflow 和 KnowledgeWorkflow MVP。
10. 已完成：Phase 2-A Trace/Audit MVP，提供 `trace.list/get`、turn trace_id、artifact 操作 trace、meeting workflow artifact trace 链路。
11. 已完成：Phase 2-B Approval Coordinator MVP，提供 `approval.request/list/get/approve/reject` 和审批 trace 链路。
12. 已完成：Phase 2-C Policy Rules MVP，提供 `policy.evaluate`，并在 `turn.start` 前对写入、删除、发送、发布类请求生成 pending approval。
13. 已完成：Phase 2-D Retry/Resume MVP，提供 `turn.retry`，并支持 approval 通过后按 retry context 续跑原动作。
14. 已完成：Phase 2-E Secret Hygiene MVP，常见密钥不会进入 session event log、trace、approval、retry 和 artifact read/register metadata 明文。
15. 已完成：Phase 2-F Architecture Hardening MVP，缓解本地 JSON 无锁/半写风险，并发写回归为 54 passed。
16. 已完成：Phase 3-A App Lifecycle MVP，移除 FastAPI route 模块级 `_gateway`，GatewayService 改为 app.state + Depends 注入；API 相关回归为 57 passed。
17. 已完成：Core v1.5 文档先行。
18. 已完成：Core v1.5-A Protocol + SQLite Store 基础层，新增 Core protocol models、CoreSQLiteStore、legacy Gateway session import、session/turn/item/artifact/trace/approval/retry native mutation/conversion。
19. 已完成：现有 `turn.start` 会写入 Core session/thread/turn/items/trace，并可通过 `session.get`、`thread.list`、`turn.get`、`turn.items`、`core.trace.list` 查询。
20. 已完成：会议 workflow 返回的 artifact records 已写入 Core artifacts，并可通过 `core.artifact.list` 查询。
21. 已完成：policy gate 创建的 approval/retry context 已写入 Core approval/retry/trace，并可通过 `core.approval.list`、`core.retry.list` 查询。
22. 已完成：新增 `CoreAppService`，Gateway runtime/service 已通过服务层访问 Core Store 与 Core-native 写入门面。
23. 已完成：`session.start/session.close` 的 Core 写入已从 compatibility recorder 切到 `CoreAppService.record_runtime_session` 原生 mutation。
24. 已完成：`turn.started/item.delta/turn.completed/turn.failed/turn.interrupted` 的 Core 写入已从 compatibility recorder 切到 `CoreAppService.record_gateway_event` 原生 thread/turn/item mutation。
25. 已完成：artifact/trace/approval/retry 写入已从 compatibility recorder 切到 `CoreAppService` 原生转换与保存。
26. 已完成：`GatewayRuntimePool` 与 `GatewayService` 已移除 `CoreRuntimeRecorder` 运行时依赖。
27. 已完成：Core v1.5-B Domain Pack 迁移 MVP，新增 PackRegistry、五个 manifest、`pack.list/get`，`workflow.list` 关联 pack 元数据。
28. 已完成：Core v1.5-C Job Service MVP，DomainWorkflow 执行创建 Core job，完成后关联 artifact ids，并提供 `job.list/get/cancel`。
29. 已完成：Core v1.5-D Tool Policy Middleware MVP，builtin tools 与 Core engine tool loop 在执行前阻断未审批高风险工具。
30. 已完成：Core v1.5-E Runtime Adapter 收敛 MVP，新增 RuntimeHandle/RuntimeAdapter、SimpleRuntimeAdapter、OpenHarnessRuntimeAdapter，并让 Gateway 通过 adapter 启停和调用 runtime。
31. 已完成：采纳 V2.0 master spec 作为目标架构主干，新增 `harnessos_target_architecture_v2.md`。
32. 下一阶段：从 Phase 3-B 继续执行，依次完成 Core-native Session/Event Store、Background Job Worker、Adapter-level Governance Injection、Pack Assembly MVP 和 Connector Registry MVP。

## 4.1 整体开发计划

| 阶段 | 目标 | 当前状态 | 下一步验收重点 |
| --- | --- | --- | --- |
| Phase 0 控制面骨架 | 建立 CLI/headless/API/RPC/stdio 的最小运行闭环 | 已完成主要能力 | 继续保持 CLI、Gateway、stdio 回归全绿 |
| Phase 1 会议 MCP MVP | 接入真实会议转写、分析、纪要能力 | 已完成 `meeting.*`、`turn.start(domain=meeting)`、自然语言音频路径自动编排 | 每次验收继续使用 `/Users/Zhuanz/Desktop/workspace/音频资料` 真实音频 |
| Phase 1-C Artifact Store | 将 transcript/analysis/result/minutes 从外部路径登记为 harnessOS artifact | 已完成最小闭环 | `artifact.*` 可 list/read/register；会议结果返回 artifact id |
| Phase 1-D 通用编排 | 将 MeetingWorkflow 特例升级为 Lead Orchestrator + DomainWorkflow Registry | 已完成 MVP | 会议不回归；KnowledgeWorkflow 可路由；普通聊天不误路由 |
| Phase 2-A Trace/Audit MVP | 建立 session/turn/workflow/tool/artifact 的 trace 链路 | 已完成 | 会议分析、普通聊天、artifact.read 都能按 trace 查询 |
| Phase 2-B Approval Coordinator | 建立 approval 状态机与 Gateway RPC | 已完成 | 审批记录可查询，审批生命周期可追踪 |
| Phase 2-C Policy Rules | 写文件、发送、发布类操作默认审批 | 已完成 MVP | 写文件类 turn 默认生成 approval request；只读请求不触发 |
| Phase 2-D Retry/Resume | 失败 turn/workflow 可恢复 | 已完成 MVP | 模拟失败后 retry 成功，批准后可继续原动作，会议/知识 workflow 不回归 |
| Phase 2-E Secret Hygiene | prompt/log/artifact/trace 脱敏 | 已完成 MVP | `sk-*`、token、Authorization 不进入持久化日志、trace、approval、retry 和 artifact read 明文 |
| Core v1.5 文档先行 | 将目标架构改为本地优先 Agent OS / App Server Core | 已完成 | 文档、测试计划、drawio 一致，并随阶段开发持续更新 |
| Core v1.5-A Protocol + Store | Session/Thread/Turn/Item + SQLite Store | 已完成 | 已完成模型、SQLite CRUD、CoreAppService、legacy session import、session/turn/item/artifact/trace/approval/retry native mutation/conversion、移除 Gateway 运行时 recorder 依赖和 Core 查询 RPC |
| Core v1.5-B Pack System | meeting/knowledge 迁移为真实 pack；三类未来业务做 stub | 已完成 MVP | `pack.list/get` 可见 5 个 pack；meeting/knowledge 真实可运行；后续补 pack-owned assembly |
| Core v1.5-C Job Service | 长任务一级化 | 已完成 MVP | 真实会议音频分析创建 job，并关联 artifacts/trace/items；后台 worker 队列后续补 |
| Core v1.5-D Tool Policy Middleware | 工具执行层审批拦截 | 已完成 MVP | builtin tools / Core engine loop 中写/删/发/发布类工具未审批不得执行 |
| Core v1.5-E Runtime Adapter 收敛 | OpenHarness/SimpleRuntime 上层统一 | 已完成 MVP | Gateway 通过 `RuntimeHandle`/`RuntimeAdapter` 使用 Simple/OpenHarness；后续补 adapter 级治理注入与 Core-native store |
| V2.0 目标架构采纳 | 将正式目标架构升级为 Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform | 已完成文档基线 | `harnessos_target_architecture_v2.md`、CURRENT、gap、drawio 和验收文档一致 |
| Phase 3-B Core-native Session/Event Store | Core Store 成为 session/event 主路径，legacy Gateway stores 降级为兼容层 | 下一阶段 | `session.events/transcript` 可从 Core records 重建；真实会议音频不回归 |
| Phase 3-C Background Job Worker | 同步 Job MVP 升级为后台长任务服务 | 未开始 | job 状态机、job.events、cancel/failure_context 可用 |
| Phase 3-D Adapter-level Governance Injection | Runtime Adapter 默认注入 policy/approval/trace/tool metadata | 未开始 | OpenHarness/Simple 默认路径未审批高风险工具不得执行 |
| Phase 3-E Pack Assembly MVP | pack manifest 驱动 workflow/connector/skill/policy bundle 注册 | 未开始 | meeting/knowledge 由 pack assembly 注册并可真实运行 |
| Phase 3-F Connector Registry MVP | Meeting MCP 升级为 connector 管理对象 | 未开始 | `connector.list/get/health` 可发现并验证 Meeting MCP |

Phase 1/2 完成判断：

- Phase 1 已完成 MVP：Meeting MCP、真实音频会议分析、会议产物登记、Lead Orchestrator、DomainWorkflow Registry、KnowledgeWorkflow MVP 均已验收；Interview 暂缓，不作为 Phase 1 阻塞项。
- Phase 2 已完成 MVP：Trace/Audit、Approval、Policy Rules、Retry/Resume、Secret Hygiene、Persistence Hardening 均已验收。
- Phase 3-A 已完成：API App Lifecycle 和 GatewayService DI 已验收。
- 后续开发从 Phase 3-B 继续，不再把 Phase 1/2 作为主线开发阶段。

Core v1.5-E 阶段验收记录：

- 定向回归：`tests/test_runtime_adapter.py tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py tests/test_cli_headless.py` 为 20 passed。
- 阶段完整回归：包含 API、persistence、secret、retry、policy、approval、trace、gateway、stdio、meeting、CLI、orchestrator、Core Store、Pack、Tool Policy、Runtime Adapter 的 81 tests passed。
- Draw.io：`xmllint --noout docs/architecture/current-vs-target-gap.drawio` 通过。
- 真实音频验收：`/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3` 生成 job `job_e881abee5217`、meeting output `meeting_ebdc8357` 和四个 artifact；验收后已清理外部会议产物与本地 `.harnessos` 验收记录。

## 4.2 Phase 1-C 开发完成记录

目标：把会议 MCP 产物从“外部文件路径”提升为 harnessOS 自有 artifact 对象，让后续聊天、Web、审计、知识整理和治理能力都能围绕 artifact id 工作。

开发范围：

| 模块 | 开发内容 | 产出 |
| --- | --- | --- |
| Artifact 数据模型 | 定义 artifact id、session_id、turn_id、domain、kind、mime、path、size、created_at、metadata | 已完成 |
| Artifact Registry/Store | 实现登记外部文件、读取文本/JSON、按 session/domain 列表查询 | 已完成：`apps/gateway/artifacts.py` |
| Gateway RPC | 新增 `artifact.register`、`artifact.list`、`artifact.get`、`artifact.read` | 已完成 |
| MeetingWorkflow 回写 | 会议分析完成后自动登记 transcript、analysis、result、minutes | 已完成：`turn.completed.data.meeting.artifacts` 包含 path + artifact_id |
| 兼容层 | 保留现有 `minutes_path` 和 artifacts path 返回 | 已完成 |
| 测试与验收 | 单测 fake artifacts；真实音频验收 artifacts 可读 | 已完成 |

非目标：

- 不做 Web UI。
- 不做 approval/policy 强治理。
- 不接面试 workflow。
- 不把外部 Meeting MCP 的输出目录迁移到 harnessOS 内部，只先登记和读取。

已验收结果：

1. 使用 `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_How to tune your inner voice  Rhonda Ross Daniel A.mp3` 触发会议分析。
2. 验收 session：`sess_a08b1f628ce2`；meeting session：`meeting_c4dc4073`。
3. 已登记 artifact：`analysis=art_9c1eb1071d60`、`minutes=art_c27fa88d8d93`、`result=art_abd235cc9239`、`transcript=art_69cdc30584b0`。
4. `artifact.list(session_id=sess_a08b1f628ce2)` 返回 4 个会议产物。
5. `artifact.read(artifact_id=art_c27fa88d8d93)` 能读回 `minutes.md`。
6. 既有 `meeting.*`、`turn.start(domain=meeting)`、普通聊天/headless 会议音频路径用例不回归。
7. drawio 当前架构与目标差异、测试文件、手工验收步骤已同步更新。

## 4.3 Phase 1-D 开发完成记录

目标：将当前嵌在 `GatewayRuntimePool` 前置判断中的 `MeetingWorkflow` 抽象为通用编排能力，为会议、知识和后续更多领域 workflow 提供统一入口。

开发范围：

| 模块 | 开发内容 | 产出 |
| --- | --- | --- |
| DomainWorkflow 接口 | 定义 `should_handle`、`run`、domain metadata、priority | 已完成 |
| DomainWorkflow Registry | 注册 meeting、knowledge 等 workflow | 已完成 |
| Lead Orchestrator | 从 `turn.start` 输入中判断显式 domain、关键词、路径、上下文 | 已完成 MVP |
| Meeting workflow 迁移 | 把现有 MeetingWorkflow 注册到 registry | 已完成，会议能力不回归 |
| Knowledge workflow MVP | 接入现有 `kb_ingest` / `kb_search` 能力 | 已完成 MVP |
| 测试与验收 | 路由、误路由、会议真实音频、知识基础链路 | 已完成 |

已验收结果：

1. 会议真实音频分析继续通过，artifact id 仍存在。
2. 显式 `domain=meeting`、普通会议音频路径都通过 `meeting.workflow` 路由。
3. 普通“你好”不被误路由。
4. 显式 `domain=knowledge` 和知识关键词请求能进入 `knowledge.workflow`。
5. 面试关键词仍不触发会议 workflow。
6. `workflow.list` 返回 `meeting` 和 `knowledge` 两个 workflow。
7. 架构图、测试用例、手工验收说明已同步更新。

真实音频回归：

- Gateway session：`sess_2858157d522e`
- Meeting session：`meeting_882541b5`
- Minutes artifact：`art_3b24d8ee4fe2`
- Workflow：`meeting.workflow`

## 4.4 Phase 2 开发计划与当前进展

目标：从“可编排”进入“可治理”，补齐 trace/audit、approval/policy、retry/resume 和安全边界。开发顺序先做可观测链路，再做审批拦截，避免审批与重试缺少可审计依据。

开发范围与交付物：

| 子阶段 | 开发内容 | 产出 | 非目标 |
| --- | --- | --- | --- |
| Phase 2-A Trace/Audit MVP | 为 session/turn/workflow/artifact 生成 trace_id；记录事件摘要与关联 id | `apps/gateway/traces.py`、`trace.list/get` RPC、trace JSONL/store、测试 | 不做 metrics dashboard |
| Phase 2-B Approval Coordinator MVP | 定义 approval request、decision、状态机、持久化 | ✅ 已完成：`approval.request/list/get/approve/reject` RPC、审批测试 | 不接复杂权限系统 |
| Phase 2-C Policy Rules MVP | 定义工具风险级别；写文件/发送/发布类操作默认需审批 | ✅ 已完成：policy evaluator、`policy.evaluate`、turn 预检 approval gate、手工审批用例 | 不做租户级策略 UI；批准后续跑已进入 Phase 2-D |
| Phase 2-D Retry/Resume MVP | 保存可重试上下文并支持批准后续跑 | ✅ 已完成：`turn.retry` RPC、policy-blocked context、pending 阻断、approved 续跑、防重复 retry | 不做后台 job 队列，不做完整 workflow.retry |
| Phase 2-E Secret Hygiene | trace/log/artifact 写入前脱敏 | ✅ 已完成：secret masker、持久化边界脱敏、脱敏回归测试 | 不做完整 DLP，不改写外部原始 artifact 文件 |

验收标准：

1. 普通聊天、会议真实音频分析、artifact 读取都能查到 trace，trace 中包含 session_id、turn_id、workflow_id、artifact_id。
2. 写文件/发送/发布类操作默认生成 approval request；pending/rejected 状态阻断执行，approved 后可通过 `turn.retry` 继续。
3. 每次 workflow/tool/artifact/approval 可追踪到同一 trace 链路。
4. 模拟失败的 turn 或 workflow 可以 retry 成功；retry 不重复登记错误 artifact。
5. Phase 1 的会议真实音频用例继续使用 `/Users/Zhuanz/Desktop/workspace/音频资料` 验收，不回归。
6. secrets 不进入 prompt、日志、trace 和 artifact 明文。

Phase 2-A 已完成记录：

1. 新增 `apps/gateway/traces.py`，提供 `TraceStore`、`trace_id` 生成、事件 trace 记录和查询。
2. `GatewayRuntimePool` 在 turn 执行时生成 `trace_id`，并同步记录 `turn.started`、`item.delta`、`tool.*`、`turn.completed/failed`。
3. `GatewayService` 新增 `trace.list`、`trace.get` RPC，并在 `turn.start` 结果顶层返回 `trace_id`。
4. `artifact.register/list/get/read` 会生成 artifact 操作 trace。
5. meeting workflow 的 `turn.completed` trace 记录能关联 `meeting.workflow` 和会议产物 artifact id；knowledge workflow 能关联 `knowledge.workflow`。
6. 用户态验收：`python3 -m cli.main run --json '你好'` 返回 `trace_f124c372d3f3`；`trace.get` 可通过 stdio JSONL 查询该 trace。
7. 自动化验收：`tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 38 passed。

Phase 2-A 剩余风险：

- 当前 trace metadata 会保留事件详情和 tool 输出摘要；Phase 2-E 已做常见密钥脱敏，但完整 DLP 和敏感文件扫描仍需后续增强。
- 当前 trace store 是本地 JSONL，适合单机开发与验收；后续生产部署需要可替换为数据库或集中日志系统。

Phase 2-B 已完成记录：

1. 新增 `apps/gateway/approvals.py`，提供 `ApprovalStore` 和 pending/approved/rejected 状态机。
2. `GatewayService` 新增 `approval.request`、`approval.list`、`approval.get`、`approval.approve`、`approval.reject` RPC。
3. 审批创建、批准、拒绝均写入 TraceStore，可通过同一 `trace_id` 查询 `approval.request` 和 `approval.approve/reject` 记录。
4. 自动化验收：`tests/test_approval_gateway.py tests/test_gateway_stdio.py tests/test_trace_gateway.py` 为 11 passed。
5. 回归验收：`tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 42 passed。
6. 用户态验收：通过 stdio JSONL 创建 `approval_id=appr_df10a7c3946c`，批准后 `trace.get(trace_manual_phase2b)` 可查到 `approval.request` 和 `approval.approve`。

Phase 2-B 历史剩余风险：

- Approval Coordinator 本身只管理审批生命周期；写入/发送/发布类操作的自动审批 gate 已在 Phase 2-C 以 Gateway turn 预检形式完成。
- 批准后继续执行原动作已由 Phase 2-D 的 `turn.retry` 最小闭环覆盖。

Phase 2-C 已完成记录：

1. 新增 `apps/gateway/policies.py`，提供 `PolicyEvaluator` 与 `PolicyDecision`。
2. `GatewayRuntimePool.stream_turn` 在 workflow/model 执行前做策略预检；写入、删除、发送、发布类请求会创建 pending approval 并停止继续执行。
3. `GatewayService` 新增 `policy.evaluate` RPC，可独立评估自然语言输入或具体工具名，例如 `workspace_write_file` 与 `workspace_read_file`。
4. 审批 gate 创建的 approval 会带上 `trace_id/session_id/turn_id` 和 policy metadata，并写入 TraceStore。
5. 自动化验收：`tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 10 passed。
6. 回归验收：`tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 45 passed。
7. 用户态验收：`python3 -m cli.main run --json '请在 workspace 下写入 phase2c_policy_manual.txt，内容为 hello'` 返回 `approval_id=appr_1532cf6d65fc`、`trace_id=trace_030c83793b25`，且未创建目标文件。
8. 用户态验收：stdio `policy.evaluate(workspace_write_file)` 返回 `requires_approval=true`、`action=workspace.write`。

Phase 2-C 剩余风险：

- 当前是 turn 预检 gate，不是 OpenHarness 底层 ToolRegistry 的最终执行拦截；后续如允许模型直接调用未知写入工具，需要在工具执行层再包一层 policy middleware。
- 仍需在 ToolRegistry 执行层做 defense in depth。

Phase 2-D 已完成记录：

1. 新增 `apps/gateway/retries.py`，提供 `RetryStore` 和 retry context 持久化。
2. Policy gate 创建 approval 时同步保存原始输入、domain、source turn、trace、approval 和 policy metadata。
3. `GatewayService` 新增 `turn.retry` RPC，支持通过 `approval_id` 或原 `turn_id` 查找 retry context。
4. `turn.retry` 会校验 approval 必须为 `approved`；pending/rejected 状态返回错误，不执行原动作。
5. retry 执行会跳过本次 policy gate，并在新 `turn.started` 中写入 `retry_of_turn_id` 和 `approval_id`。
6. 同一 retry context 只能消费一次，重复 retry 会返回错误，避免重复写入/发布。
7. 自动化验收：`tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 12 passed。
8. 回归验收：`tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 47 passed。

Phase 2-D 剩余风险：

- 当前 retry 主要覆盖 policy-blocked turn 的批准后续跑；任意失败 workflow 的通用 retry 仍需后续扩展。
- retry 仍依赖当前 agent/runtime 对原始输入的执行能力；真正工具级幂等需要在 ToolRegistry/ArtifactRegistry 层继续强化。

Phase 2-E 已完成记录：

1. 新增 `apps/gateway/secrets.py`，提供 `mask_text` 与 `mask_value`。
2. `GatewaySessionStore.append_event` 写入 `events.jsonl` 前会脱敏 event data。
3. `TraceStore` 写入 metadata 和 input summary 前会脱敏。
4. `ApprovalStore` 写入 request summary、metadata 和 decision reason 前会脱敏。
5. `RetryStore` 写入 retry input 和 policy metadata 前会脱敏。
6. `ArtifactRegistry` 写入 metadata 和 `artifact.read` 返回内容前会脱敏。
7. 自动化验收：`tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 15 passed。
8. 回归验收：`tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 50 passed。

Phase 2-E 剩余风险：

- 当前是正则级 secret masker，不能替代完整 DLP。
- 外部原始 artifact 文件不会被就地改写；只保证 Gateway 读取返回和 registry metadata 脱敏。
- SSE/HTTP 即时响应仍可能包含模型原始输出，当前重点是持久化和可查询产物不落明文。

Phase 2-F 已完成记录：

1. 新增 `apps/gateway/persistence.py`，提供本地文件锁、原子写和 JSON list 临界区更新。
2. `ApprovalStore`、`RetryStore`、`ArtifactRegistry` 的 JSON index 读改写已加锁，避免并发创建时丢记录。
3. `TraceStore` JSONL append/read 已加锁。
4. `GatewaySessionStore` snapshot 写入已切换为原子替换，event append 已加锁。
5. 自动化验收：`tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 19 passed。
6. 回归验收：`tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 54 passed。

Phase 2-F 剩余风险：

- 文件锁只适合单机本地开发和轻量使用，不是多机器一致性方案。
- API 多 worker 下 runtime pool 仍会状态分裂；需要外置 session/runtime registry 或限制单 worker。
- 仍需要 ToolRegistry 级 policy middleware，防止未来底层工具绕过 Gateway preflight。

Phase 3-A 已完成记录：

1. `apps/api/routers/runs.py` 已移除 route 模块级 `_gateway = GatewayService()`。
2. 新增 `apps/api/dependencies.py`，通过 FastAPI `Request.app.state.gateway_service` 获取 app-scoped `GatewayService`。
3. `apps/api/__init__.py` 的 lifespan 会初始化 app-scoped GatewayService，并支持 `create_app(gateway_service=...)` 注入。
4. `/v1/runs`、`/v1/runs/stream`、session 查询、transcript 和 `/v1/rpc` 已共享同一个 app-scoped service。
5. 自动化验收：`tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_gateway_protocol.py` 为 15 passed。
6. 回归验收：`tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 57 passed。

Phase 3-A 剩余风险：

- app-scoped GatewayService 解决的是模块全局单例和测试注入问题，不等于多 worker 共享 runtime。
- 多 worker/多实例生产部署仍需要外置 session store、runtime registry 或显式单 worker 部署策略。

## 4.5 当前架构缺陷与优先级

| 优先级 | 缺陷 | 影响 | 建议 |
| --- | --- | --- | --- |
| P0 | 本地 JSON 文件存储无锁、无事务 | 多进程或并发写 session/trace/approval/retry/artifact index 时可能损坏或丢写 | 已在 Phase 2-F 加文件锁和原子写；生产仍需 SQLite/Postgres |
| P0 | API `_gateway` 是模块级单例 | uvicorn 多 worker 状态分裂；重启后内存 runtime 丢失 | Phase 3-A 已移除模块级单例并引入 app lifecycle；生产仍需外置 runtime/session registry |
| P0 | 缺 SQLite Core Store | 多项目、多客户端、Job 和 Thread/Item 查询无法稳定落地 | Core v1.5-A 已建立基础 SQLite Store、legacy import 和 session/turn/item/artifact/trace/approval/retry Core-native mutation/conversion；仍需 Core-native App Server 取代 Gateway runtime store |
| P0 | 缺 Thread/Item 对象模型 | Web、多项目任务管理和产物链路只能依赖 session events | Core v1.5-A 已新增模型并通过 CoreAppService 写入 turn/item；仍需 Core-native App Server |
| P0 | Domain Pack 仍是 manifest MVP | pack 可见但尚未完整驱动 workflow/skill/connector/policy 装配 | 后续在 Runtime Adapter/Workflow DSL 阶段补 pack-owned assembly |
| P0 | Job Service 仍是同步记录型 MVP | 会议、回测、视频等长任务仍会占用 turn.start，同步等待期间不可轮询进度 | 后续建立后台 worker、job.events、job.cancel 对运行中任务的真实取消 |
| P0 | Tool Policy Middleware 仍是 MVP | 已能阻断 builtin/Core engine 工具，但尚未自动创建 approval，也未覆盖所有 runtime adapter 默认注入 | Core v1.5-E 收敛 runtime adapter 与 tool_metadata，补自动 approval coordinator |
| P1 | Retry 只覆盖 policy-blocked turn | 任意 workflow 失败、会议长任务失败无法统一恢复 | 增加 workflow retry context、artifact 幂等 key、局部重跑 |
| P1 | Meeting connector 与本机路径/服务耦合 | 换机器或服务端口后验收不稳定 | 增加 MCP connector registry、health check、配置化音频验收目录 |
| P1 | Routing 仍偏关键词 | 多领域混合任务容易误路由 | 引入可解释 intent router 和 workflow DSL |
| P2 | Secret Hygiene 是 MVP | 复杂凭证、私钥块、文件内容扫描不足 | 扩展 DLP pattern、按 artifact kind 配置扫描策略 |
| P2 | OpenHarness/Deep Agents/SimpleRuntime 多路径并存 | 长期维护成本和事件/权限模型不一致 | Core v1.5-E 已收敛启动/调用边界；后续继续统一事件规范、tool metadata 和 approval coordinator 注入 |

测试计划：

| 类型 | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| 单元测试 | Trace store 与脱敏 | `pytest tests/test_trace_gateway.py tests/test_secret_hygiene.py` | trace 可写可读，敏感字段被 mask |
| 单元测试 | Approval 状态机 | `pytest tests/test_approval_gateway.py` | pending/approved/rejected 转换正确 |
| 集成测试 | Policy 拦截写文件 | `pytest tests/test_policy_approval.py` | 写文件生成审批，只读不审批 |
| 集成测试 | Retry/Resume | `pytest tests/test_retry_resume.py` | 失败 turn 可重试，session events 连续 |
| 回归测试 | Meeting workflow | `pytest tests/test_meeting_gateway.py tests/test_meeting_turn_workflow.py tests/test_meeting_audio_acceptance.py` | 真实音频会议分析、长音频读取、artifact id 不回归 |
| 协议测试 | RPC/stdio 同构 | `pytest tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py` | 新增 RPC 在服务和 stdio 下行为一致 |

手工验收步骤：

1. 运行普通聊天并查询 trace：
   ```bash
   python3 -m cli.main run --json '你好'
   ```
   预期：返回结果中包含 trace_id 或可通过 session/turn 查到 trace。

2. 运行会议真实音频并查询 trace/artifact：
   ```bash
   python3 -m cli.main run --json '请分析 /Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3，生成会议纪要'
   ```
   预期：会议分析完成，trace 能串起 `meeting.workflow`、`analysis/minutes/result/transcript` artifacts。

3. 触发写文件类操作：
   ```bash
   python3 -m cli.main run --json '请在 workspace 下写入一个 approval_test.txt，内容为 hello'
   ```
   预期：进入 pending approval，不直接写文件。

4. 拒绝审批：
   ```json
   {"id":"a1","method":"approval.reject","params":{"approval_id":"<approval_id>","reason":"manual rejection"}}
   ```
   预期：文件不存在，trace 记录 rejected。

5. 批准审批：
   ```json
   {"id":"a2","method":"approval.approve","params":{"approval_id":"<approval_id>"}}
   ```
   预期：操作继续或可重试后继续，文件写入，trace 记录 approved 和 tool result。

6. 验证脱敏：
   ```bash
   python3 -m cli.main run --json '请记录这个测试 token：sk-test-1234567890'
   ```
   预期：trace/log/artifact 中只能看到 masked token，不出现完整明文。

## 5. 当前架构图与目标架构图差别

| 主题 | 当前架构图应表达 | 目标架构图应表达 | 差距 |
| --- | --- | --- | --- |
| 领域能力 | meeting MCP 已通过 workflow registry 接入，knowledge workflow MVP 已接入 | meeting/knowledge/video 等均成为可治理 DomainWorkflow | 需要多代理分派、LLM intent router 和 workflow DSL |
| 智能体行为 | Lead Orchestrator 统一选择 meeting/knowledge/generic chat，meeting 返回 artifact id | workflow 可读取策略、调用工具、回写 artifacts、请求审批 | 需要 approval/policy/trace 治理 |
| 面试场景 | 暂缓，不进入本阶段验收 | 后续作为独立 workflow 接入 | 当前目标图需标注 later，避免 Phase1 误验收 |
| 工件治理 | 外部 meeting server 生成 transcript/analysis/minutes 文件，harnessOS 已登记 artifact id 并可读取 | harnessOS Artifact Store 统一登记、回看、审计 | 仍需 artifact 审计、权限和 lineage |
| 协议治理 | Gateway 有 session/turn/rpc/stdio | Gateway 有 artifact/approval/job/trace | artifact/approval/trace/job 仍待产品化 |

## 6. 本轮已落地文件

- `apps/gateway/protocol.py`：项目自有 RPC 和事件模型
- `apps/gateway/runtime.py`：`GatewayRuntimePool` 和事件归一化
- `apps/gateway/service.py`：本地 JSON-RPC 风格 Gateway service
- `cli/main.py`：新增 `run` headless 子命令
- `pyproject.toml`：新增 `harness` console script
- `tests/test_gateway_protocol.py`：协议与 session/turn 测试
- `apps/gateway/stdio_server.py`：stdio JSONL 协议入口
- `tests/test_gateway_stdio.py`：stdio JSONL 协议测试
- `apps/gateway/meeting.py`：Meeting MCP JSON-RPC client 和 meeting workflow facade
- `apps/gateway/artifacts.py`：Artifact Registry 和 artifact 文件登记/读取
- `apps/gateway/workflows.py`：DomainWorkflow、WorkflowRegistry、LeadOrchestrator、Meeting/Knowledge workflow
- `tests/test_meeting_turn_workflow.py`：meeting turn workflow、聊天自动路由、真实音频和面试防误路由测试
- `tests/test_artifact_gateway.py`：artifact registry 与 Gateway RPC 测试
- `tests/test_lead_orchestrator.py`：workflow registry、lead orchestrator、knowledge route 测试
- `tests/test_meeting_gateway.py`：Meeting Gateway 单元测试
- `tests/test_meeting_audio_acceptance.py`：真实音频验收测试

外部会议能力对应文件位于 `meeting-voice-assistant`：

- `backend/app/meeting_mcp/service.py`
- `backend/app/meeting_mcp/mcp_stdio.py`
- `backend/tests/test_meeting_mcp.py`
- `docs/meeting-mcp-phase1-acceptance.md`
