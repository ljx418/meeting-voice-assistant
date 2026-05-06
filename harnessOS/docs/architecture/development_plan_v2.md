# harnessOS V2.0 Development Plan

## 1. 当前阶段判断

当前统一阶段口径：

- **产品/架构基线版本**：Baseline v1.5-E
- **当前主验收阶段**：Phase 4-B1 Meeting Artifact Lineage Acceptance 已完成
- **延期保留能力**：Phase 4-B2 Remote ComfyUI / Render Manifest Scaffold
- **当前开发阶段**：Phase 5-D Cross-domain MCP Workflow Stabilization 已完成当前集成 MVP；下一阶段进入 Phase 6 Productization / Open Source / Commercial Readiness，或在 Phase 5-D 上继续补超时、取消、重试和可发布文档

Phase 1 和 Phase 2 已完成 MVP 验收。

已完成范围：

- Phase 1：Meeting MCP、真实音频会议分析、会议产物登记、Lead Orchestrator、DomainWorkflow Registry、KnowledgeWorkflow MVP。
- Phase 2：Trace/Audit、Approval、Policy Rules、Retry/Resume、Secret Hygiene、Persistence Hardening。
- Phase 3-A：API App Lifecycle，FastAPI route 模块级 `_gateway` 已移除，GatewayService 支持 app-scoped DI。
- Baseline v1.5-E：Core protocol/store 基础、Pack Visibility & Manifest MVP、Job Record & Tracking MVP、Tool Execution Guard MVP、Runtime Adapter Boundary MVP。
- Roadmap Phase 3-B：Core-native Session/Event Store MVP，`session.list/read/events/transcript` 已优先从 Core records 查询或重建。
- Roadmap Phase 3-C：Background Job Worker MVP，Core 已具备本地 in-process worker、job events、failure_context 和 cancel 终态语义。
- Roadmap Phase 3-D：Adapter-level Governance Injection MVP，Simple/OpenHarness Runtime Adapter 默认路径已注入 policy evaluator、approval checker、trace context 和 tool metadata。
- Roadmap Phase 3-E：Pack Assembly MVP，meeting/knowledge 由 pack manifest 装配，`pack.list/get` 返回 assembly 状态。
- Roadmap Phase 3-F：Connector Registry MVP，Meeting MCP 注册为 `meeting_voice_mcp`，`connector.list/get/health` 可查询健康与能力。
- Phase 4-A：Video Studio Pack MVP，`video.workflow` 可生成 brief/script/storyboard/shot_list 四类规划 artifact。
- Phase 4-B0：Domain Pack Workflow Loader，meeting/knowledge/video workflow 实现已从 Gateway 下沉到对应 Domain Pack；Meeting MCP client/service 已迁入 `packs/meeting/connector.py`，Gateway 只保留 workflow 注册、选择、装配和旧导入兼容面。
- Phase 4-B1：Artifact Lineage Query MVP，Core ArtifactRecord 已保存 `parent_ids`，Gateway 新增 `artifact.lineage` / `core.artifact.lineage` 查询。
- Phase 4-B2：Remote ComfyUI / Render Manifest Scaffold 已预留，`remote_comfyui` connector 和 Video Studio render manifest 只作为延期脚手架保留，不进入当前验收主线。
- Phase 4-C：Core-native RPC Router，Gateway RPC 已迁入注册式 `RpcRouter`，`method.list` 可枚举 method metadata，`initialize.capabilities` 由 registry 生成，并覆盖 compat alias 与稳定错误码回归。
- Phase 4-D：Tool-level Approval Automation，工具执行层命中高风险策略时可自动创建 approval request，拒绝后 retry 被阻断，批准后的 turn approval id 可放行原工具执行。
- V2.0 Target Architecture：已采纳 `docs/design/V2.0/harnessos_architecture_master_spec_v2.md`，并新增 `docs/architecture/harnessos_target_architecture_v2.md`。

因此当前开发不继续推进 ComfyUI 执行适配器。进入 **Phase 5-A Pack DSL / Skill / Policy Bundle Assembly** 前，已先执行 **Review Cleanup Gate** 的 2026-04-30 清理批次，集中关闭审批绕过、OpenHarness 工具治理、artifact 越权读取、session 路径穿越、retry 并发重放和持久化脱敏等 P0 问题。完整用户/租户授权、Pack DSL governed context、connector execution runtime 等架构债已明确延期到 Phase 5-A/5-C/6。Phase 1/2 后续只允许做回归、修复和验收补强。

## 2. 开发总目标

V2.0 的开发目标是把当前 Gateway-centered assistant 迁移为：

> Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform

核心原则：

- Core 不写死业务逻辑。
- 业务能力通过 Domain Pack 装配；业务逻辑不得写回 Core 或 Gateway。
- Runtime 通过 Adapter 隔离。
- 长任务进入 Job Worker。
- Tool、Job、Artifact、Retry 都必须进入 policy/approval/trace 治理链路。
- 每个阶段完成后必须同步测试文件、验收文档和架构图。

## 3. Phase 3 开发计划

### Roadmap Phase 3-B：Core-native Session/Event Store

目标：把旧 Gateway snapshot/events 从主运行数据源降级为兼容层，让 session、thread、turn、item、trace 查询和写入以 Core Store 为准。

状态：已完成 MVP。

交付物：

- CoreAppService 提供 session/event 的主写入和主查询路径。
- GatewaySessionStore 只作为 legacy compatibility 和 import source。
- `session.list/read/events/transcript` 至少有 Core-native 查询路径。
- 保留 legacy JSON/JSONL 读取能力，不删除旧数据。
- `session.list/read/events/transcript` 已优先使用 Core-native 查询路径，legacy JSON/JSONL 仅在 Core 记录缺失时回退。

验收标准：

- 普通 `你好` 产生 session/thread/turn/items，并可通过 Core RPC 查询。
- `session.events` 和 transcript 能从 Core records 重建。
- 旧 JSON/JSONL fixture 可导入或兼容读取。
- 会议真实音频分析不回归。

### Roadmap Phase 3-C：Background Job Worker

目标：把同步 Job MVP 升级为真正长任务服务。

当前状态：已完成 MVP。实现范围是本地 in-process background worker 和完整 job event/failure/cancel 语义，不包含分布式队列或多 worker 调度。

交付物：

- Job 状态机：`queued / running / completed / failed / cancelled`。
- `job.create/get/list/cancel` 支持后台任务记录与状态更新。
- `job.events` 查询接口。
- Meeting workflow 可作为后台 job 执行候选；若仍同步执行，也必须写入完整 job event。

验收标准：

- 真实会议音频创建 job，状态可查询，完成后关联 transcript/minutes/analysis/result artifacts。
- cancel 对 queued/running/completed 的行为有明确结果。
- job failure 能记录 `failure_context`。
- 验收后清理外部会议产物和 `.harnessos` 验收记录。

已验收：

- 定向回归：`tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py` 为 27 passed。
- 真实音频验收：本机 TED 音频样本成功生成会议纪要，job `job_703ecb999341` 关联四类 artifact。
- `job.events(job_703ecb999341)` 返回 `job.queued -> job.started -> job.completed`。
- 验收后已清理 `meeting_aa91f008` 外部产物和本地 `.harnessos` 验收记录。

### Roadmap Phase 3-D：Adapter-level Governance Injection

目标：把治理能力注入 Runtime Adapter 默认路径，避免只在 Gateway 或部分工具层生效。

当前状态：已完成 MVP。实现范围是 adapter 默认路径的治理上下文注入和执行层阻断，不包含工具层自动创建 approval request。

交付物：

- Runtime Adapter 在 Simple/OpenHarness invoke、stream、continue_pending 默认路径注入 policy evaluator、approval checker、trace context。
- Tool metadata 默认携带 session/turn/trace/policy 上下文，并保留 OpenHarness 既有 metadata。
- 未审批高风险 tool 在 adapter 默认路径中也会被阻断。

验收标准：

- builtin tools 和 Core engine tool loop 仍可阻断未审批写入。
- OpenHarness RuntimeBundle 路径的 tool metadata 可被 policy middleware 读取。
- 只读工具不误拦截。
- 会议真实音频不被误判为写入类高风险动作。

已验收：

- 定向回归：`tests/test_runtime_adapter.py tests/test_tool_policy_middleware.py` 为 11 passed。
- 阶段相关回归：runtime adapter、tool policy、gateway、policy、approval、trace、meeting、Core Store 相关 58 tests passed。
- 真实音频验收：本机 TED 音频样本成功生成会议纪要，session `sess_4fe9d283c297`，turn `turn_4c38dbc1178f`，trace `trace_39830f4e47e3`，job `job_552cbf52c163`，meeting output `meeting_d1c6cc48`，并登记四类 artifact。
- 验收后已清理 `meeting_d1c6cc48` 外部产物和本地 `.harnessos` 验收记录。

### Roadmap Phase 3-E：Pack Assembly MVP

目标：让 pack manifest 不只可见，还能驱动 workflow、connector、skill、policy bundle 注册。

当前状态：已完成 MVP。

交付物：

- Pack manifest schema 明确 workflow、connector、skill、policy、artifact kind 字段。
- meeting/knowledge 从 manifest 完成可运行装配。
- investment/interview/video_studio 保持 stub，但字段结构与真实 pack 一致。
- `pack.get` 能返回装配状态和缺失依赖。

验收标准：

- `pack.list/get` 显示五个 pack 及 assembly 状态。
- meeting workflow 由 pack assembly 注册后仍能处理真实音频。
- 禁用或缺失 connector 时返回可解释错误。

已实现：

- `PackAssemblyResult` 与 pack assembly view。
- meeting/knowledge 由 active pack manifest 装配并注册现有 workflow。
- investment/interview/video_studio 保持 stub，并返回 assembly 状态。
- `pack.list/get` 返回 assembly 状态、registered workflows 和 missing dependencies。
- active pack 缺失 connector 时，显式 domain 调用返回可解释失败。
- 定向自动化回归：`tests/test_pack_registry.py tests/test_lead_orchestrator.py tests/test_gateway_protocol.py tests/test_meeting_turn_workflow.py` 为 28 passed。
- 真实音频验收：启动同级 `meeting-voice-assistant` 的 FunASR service 后，`tests/test_meeting_audio_acceptance.py tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance` 为 2 passed。

### Roadmap Phase 3-F：Connector Registry MVP

目标：把 Meeting MCP 从硬编码相邻项目路径升级为 connector 管理对象。

当前状态：已完成 MVP。

交付物：

- ConnectorRecord 可记录 connector id、kind、domain、capabilities、health、config_ref。
- Meeting MCP 作为 `meeting_voice_mcp` connector 注册。
- `connector.list/get/health` RPC 或 Core query path。
- connector secret/config 不进入明文日志。

验收标准：

- `connector.list` 能看到 Meeting MCP。
- `connector.health` 能区分可用、不可用和缺依赖。
- 会议真实音频通过 connector registry 找到 Meeting MCP。

已实现：

- 新增 Gateway `ConnectorRegistry`，默认注册 `meeting_voice_mcp`。
- Core SQLite 新增 connectors 表，`CoreAppService` 支持 connector 保存、读取和过滤列表。
- Gateway 新增 `connector.list`、`connector.get`、`connector.health` RPC。
- `initialize.capabilities.connectors=true`。
- Meeting workflow 默认路径执行前通过 connector registry 校验 Meeting MCP 依赖。
- connector 返回 `config_ref=HARNESS_MEETING_MCP_*`，不返回密钥类配置。
- 定向自动化回归：`tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_pack_registry.py tests/test_meeting_gateway.py tests/test_meeting_turn_workflow.py -k 'not phase1b_real_audio_turn_start_acceptance'` 为 40 passed。

## 4. Phase 4 开发计划

Phase 4 才进入新业务域扩展，优先选择 AI Video Studio Pack 或 Investment Pack 之一，不并行展开。

默认顺序：

1. Video Studio Pack MVP：brief -> script -> storyboard -> shot list artifact。当前已完成 MVP。
2. Domain Pack Workflow Loader：把业务 workflow 实现从 Gateway 迁入 pack。当前已完成 B0。
3. Artifact Lineage Query：Meeting transcript -> analysis -> result -> minutes 的用户态 lineage 可查询；Video Studio brief -> script -> storyboard -> shot_list 保留自动化覆盖。当前已完成 B1。
4. Remote ComfyUI / Render Manifest Scaffold：script -> storyboard -> shot_list -> asset_plan -> render_output 的代码级脚手架已延期保留，不作为当前用户态验收。
5. Specialist crew：Studio Lead、Director、Script、Storyboard、Editing、QA/Publish。
6. Publish/render 前强制 approval。

已实现的 Phase 4-A 范围：

- `video_studio` pack 从 `stub` 提升为 `active`。
- 新增 `video.workflow`，由 pack assembly 注册到 Lead Orchestrator。
- 用户可通过 `turn.start(domain=video_studio)` 或视频/脚本/分镜关键词触发 workflow。
- workflow 生成 `brief`、`script`、`storyboard`、`shot_list` 四类规划产物，并登记为 harnessOS artifacts。
- workflow 执行进入 Core job，完成后 job 关联四类 artifact。
- 当前不接入 ComfyUI、不生成视频资产、不做批处理或发布审批。

已实现的 Phase 4-B0 范围：

- 新增 `packs/meeting/workflow.py`，默认 runtime/orchestrator 已改为使用 Meeting pack workflow。
- 新增 `packs/meeting/connector.py`，承载 Meeting MCP stdio client 与 `MeetingGatewayService`；`apps/gateway/meeting.py` 仅保留旧导入兼容导出。
- 新增 `packs/knowledge/workflow.py`，承载 `knowledge.workflow` 的领域路由、ingest/search 调用和 sources 提取逻辑。
- 新增 `packs/video_studio/workflow.py`，承载 `video.workflow` 的 brief/script/storyboard/shot_list 生成和 artifact 登记逻辑。
- `apps/gateway/workflows.py` 不再包含 meeting/knowledge/video 业务实现，只保留 `WorkflowContext`、`WorkflowRegistry`、`LeadOrchestrator`、DomainWorkflow adapter 和默认 workflow 工厂。
- 当前仍是静态 pack workflow factory MVP，尚未实现通用 workflow DSL、动态插件加载或 skill/policy bundle 自动装配。
- 定向自动化回归：`tests/test_lead_orchestrator.py tests/test_pack_registry.py tests/test_gateway_protocol.py::test_video_studio_workflow_registers_planning_artifacts tests/test_gateway_stdio.py::test_stdio_server_workflow_list` 为 10 passed。

已实现的 Phase 4-B1 范围：

- `CoreAppService.record_gateway_artifact` 会从 artifact metadata 中解析 `source_artifact_id` / `parent_artifact_ids` 并写入 Core `ArtifactRecord.parent_ids`。
- `core.artifact.list` 支持按 `session_id` / `turn_id` 查询，便于按一次工作流执行收敛产物。
- Gateway 新增 `artifact.lineage` 与 `core.artifact.lineage` RPC，返回 `artifacts`、`edges`、`roots`、`leaves` 和 `count`。
- Meeting workflow 当前可形成 `transcript -> analysis -> result -> minutes` 的用户态验收链路。
- `video.workflow` 仍保留 `brief -> script -> storyboard -> shot_list` 的规划产物链路，用作代码级回归覆盖。
- 当前不代表 ComfyUI assets/render output 已接入；资产、渲染输出、局部重跑属于延期能力。
- 定向自动化回归：`tests/test_meeting_turn_workflow.py::test_turn_start_meeting_registers_artifacts tests/test_gateway_protocol.py::test_video_studio_workflow_registers_planning_artifacts tests/test_core_v15_protocol_store.py tests/test_artifact_gateway.py` 为 13 passed。

延期保留的 Phase 4-B2 scaffold 范围：

- 新增 `ComfyUIConfig`，通过 `HARNESS_COMFYUI_BASE_URL` 描述远程 ComfyUI 服务地址。
- Connector Registry 注册 `remote_comfyui`，默认 `not_configured`，配置后为 `configured`；当前不主动发起网络调用。
- `video_studio` pack 声明 `remote_comfyui` connector，并新增 `render_output` artifact kind。
- `video.workflow` 生成 `asset_plan` 与 `render_output` manifest artifact，形成 `brief -> script -> storyboard -> shot_list -> asset_plan -> render_output` 可查询链路。
- 当前 `render_output` 是 `planned_not_rendered` manifest，不代表远程 ComfyUI 已执行；真实远程任务提交、轮询、取消和结果采集延期到后续远程 Connector 阶段。
- 该 scaffold 只保留自动化回归，当前用户态验收不启动 ComfyUI、不访问远程工作站、不验证视频渲染。

## 5. 剩余开发计划

### Phase 4-C：Core-native RPC Router

目标：把当前 `GatewayService.handle_rpc` 的集中 method 分发逐步收敛为 Core/App Server 风格的 RPC router，让协议能力可注册、可枚举、可测试，而不是继续在 Gateway service 中堆叠 if/else 分发。

当前状态：已完成 MVP。

修改意图：

- 降低 GatewayService 的职责密度，让 Gateway 回到 transport-facing facade，而不是继续承担协议目录、业务方法分发和错误处理的混合职责。
- 为 CLI、HTTP `/v1/rpc`、stdio JSONL、未来 Web / Bot / Automation 提供同一套 Core-native method registry。
- 让 `initialize.capabilities`、method metadata、错误码和兼容 alias 有单一来源，避免新增方法时漏改多个入口。
- 为后续低代码页面和 Domain Pack 装配提供可发现的协议能力清单。

修改范围：

- 新增或抽离 RPC method registry / handler registry。
- 将现有 `initialize`、`session.*`、`turn.*`、`artifact.*`、`job.*`、`approval.*`、`trace.*`、`pack.*`、`connector.*` 分批迁入注册式 handler。
- 保留 GatewayService 的外部调用面，保证 `/v1/rpc`、stdio JSONL、CLI 不换协议。
- 增加 method metadata、capability mapping、compat alias 和统一错误码测试。

非目标：

- 不重写 FastAPI、stdio server 或 CLI transport。
- 不删除现有兼容方法名。
- 不引入新业务 workflow。
- 不把 OpenHarness / DeepAgents 内部对象暴露为产品协议。

交付物：

- 建立 method registry / handler registry，覆盖 `initialize`、`session.*`、`turn.*`、`artifact.*`、`job.*`、`pack.*`、`connector.*` 等现有方法。
- 明确 capability registry、method metadata、compat alias 和统一错误码。
- 保持 `/v1/rpc`、stdio JSONL、Headless CLI 的现有行为兼容。
- 保留 GatewayService 作为 transport-facing facade，但不再把业务协议分发继续写死在单个方法里。

验收标准：

- 能通过自动化测试证明 `initialize.capabilities` 与 method registry 一致。
- 能通过自动化测试证明未知 method 返回 `METHOD_NOT_FOUND` 或等价稳定错误码。
- 能通过自动化测试证明缺参、参数类型错误、handler 异常分别返回稳定错误码，不泄露内部堆栈。
- `/v1/rpc`、stdio JSONL、Headless CLI 对已有核心方法保持兼容。
- `scripts/e2e_meeting_validation.sh` 仍返回 `transcript -> analysis -> result -> minutes` lineage。
- 新增方法时可只通过 registry 注册并被 capability/method list 发现。

已实现：

- 新增 `apps/gateway/rpc_router.py`，提供 `RpcRouter`、`RpcMethodSpec`、method metadata、capability registry 和 alias metadata。
- `GatewayService.handle_rpc` 保持外部入口不变，内部 `_dispatch` 改为通过 `RpcRouter.dispatch` 分发。
- 新增 `method.list` RPC，可返回已注册方法、capability、compat alias 和 count。
- `initialize.capabilities` 改为由 method registry 生成，并保留 `headless`、`stdio_jsonl` transport capabilities。
- `artifact.lineage` 明确标记为 `core.artifact.lineage` 的兼容 alias。
- 新增缺参、未知方法、handler 异常的稳定错误码回归。

已验收：

- 编译检查：`PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 -m compileall apps/gateway/service.py apps/gateway/rpc_router.py` 通过。
- 定向回归：`tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py tests/test_gateway_stdio.py tests/test_cli_headless.py` 为 27 passed。
- 阶段相关回归：`tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py tests/test_gateway_stdio.py tests/test_cli_headless.py tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_artifact_gateway.py tests/test_trace_gateway.py tests/test_approval_gateway.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_lead_orchestrator.py tests/test_pack_registry.py tests/test_core_v15_protocol_store.py tests/test_acceptance_scripts.py` 为 85 passed。

### Phase 4-D：Tool-level Approval Automation

目标：把当前“高风险工具可被阻断”的执行层 MVP 升级为“工具层自动创建 approval request，并能通过 retry/resume 继续执行”的闭环治理。

当前状态：已完成 MVP。

修改意图：

- 当前系统已经能阻断高风险工具，但治理闭环还不完整；Phase 4-D 要让工具执行层自己创建 approval request，避免只靠入口 preflight。
- 让 Agent 可以安全地尝试更复杂的工具任务，高风险动作进入审批，低风险读取任务继续顺畅执行。
- 把 tool invocation、policy evaluation、approval、retry、trace 串成可审计链路，满足真实工作流落地要求。

修改范围：

- 在 Tool Execution Guard / Runtime Adapter 默认路径中加入 approval request 自动创建逻辑。
- 将 pending approval id 写入 tool result、trace event、retry context。
- 补齐 approval 通过后的 retry/resume 行为，避免重复执行和丢失原始工具参数。
- 增加只读工具、Meeting 分析、知识检索的误拦截回归。

非目标：

- 不实现复杂组织审批流、多人审批或 SLA。
- 不改变已有 `approval.request/list/get/approve/reject` 的协议语义。
- 不允许审批通过前执行真实写入、删除、发送、发布类动作。
- 不把所有工具都强制审批；只对策略命中的高风险工具触发。

交付物：

- Tool invocation 进入 policy evaluation 后，未审批高风险动作自动创建 approval request。
- approval、trace、retry、tool metadata 之间建立稳定引用关系。
- 读类工具和 Meeting 分析路径不触发审批。

验收标准：

- 写文件类 tool 在执行层返回 pending approval id，审批前不执行真实写入。
- 删除、发送、发布类高风险 tool 有同类自动审批行为。
- approval 通过后可通过 `turn.retry` 或等价流程继续原动作，并防止同一 approval 重复执行。
- approval 拒绝后 retry 被明确拒绝，错误信息可解释。
- trace 中能串起 `tool invocation -> policy -> approval -> retry -> completion/blocked`。
- 只读工具、Meeting 音频分析和 `artifact.read/list` 不触发审批。

已实现：

- `tools.policy_guard` 支持 `approval_requester`，高风险工具阻断时可自动创建 approval request，并在阻断消息中返回 approval id。
- `RuntimeGovernanceContext` 新增 `user_input`、`approval_id`、`approval_requester`，默认 runtime adapter 工具路径可拿到当前 session/turn/trace 和 retry 上下文。
- `GatewayRuntimePool` 新增工具层 approval requester，自动写入 ApprovalStore、TraceStore、Core approval/trace records 和 RetryStore/Core retry records。
- Core engine tool loop 在阻断高风险工具时返回包含 approval、retry_context 和 policy 的 tool result metadata。
- `turn.retry` 继续复用已有 approval 状态检查：rejected approval 返回 `INVALID_PARAMS`，approved approval 通过 `approval_id` 注入工具 metadata 后可放行工具执行。

已验收：

- 编译检查：`PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 -m compileall tools/policy_guard.py tools/__init__.py core/runtime_adapter/adapters.py core/engine/query.py core/engine/messages.py apps/gateway/runtime.py` 通过。
- 定向回归：`tests/test_tool_policy_middleware.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py` 为 15 passed。
- 阶段相关回归：`tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py tests/test_gateway_stdio.py tests/test_cli_headless.py tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_artifact_gateway.py tests/test_trace_gateway.py tests/test_approval_gateway.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_tool_policy_middleware.py tests/test_runtime_adapter.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_lead_orchestrator.py tests/test_pack_registry.py tests/test_core_v15_protocol_store.py tests/test_acceptance_scripts.py` 为 98 passed。

### Review Cleanup Gate：代码检视集中清理

目标：在继续新增 Phase 5-A 能力前，先把本轮全项目代码检视发现的安全闭环、架构边界和功能一致性问题收敛到可验收状态。

当前状态：2026-04-30 清理批次已完成；后续大阶段完成后继续更新本门禁。

修改意图：

- 防止在审批、OpenHarness 工具执行、artifact 读取、session/resource 边界尚未闭环时继续扩展 Pack DSL。
- 把代码检视意见变成持续维护的工程门禁，而不是一次性报告。
- 要求每次大阶段完成后更新检视清单，并在测试前进行二次代码检视。

修改范围：

- 新增并维护 `docs/architecture/code-review-cleanup-checklist_v2.md`。
- 新增并维护 `docs/architecture/code-review-cleanup-checklist_v2.drawio`。
- 将 P0/P1 问题安排到 Phase 5-A 前集中清理。
- 清理后先做 Second Review Gate，再并行执行 Phase 1 到当前阶段验收。

验收标准：

- P0 问题已关闭，或在清单中记录明确延期原因、风险和目标阶段。
- 清理代码通过二次检视，确认没有引入新的 P0/P1 问题。
- Phase 1 到当前阶段的并行验收测试通过。
- Meeting lineage 用户态验收通过，或明确记录为本地服务/fixture 环境阻塞。
- `current-vs-target-gap_v2.drawio` 和 `code-review-cleanup-checklist_v2.drawio` 均为合法 XML。

已验收：

- 代码检视清单已落盘到 `docs/architecture/code-review-cleanup-checklist_v2.md` 和 `docs/architecture/code-review-cleanup-checklist_v2.drawio`。
- 二次检视结论：修改代码未发现残留 P0/P1；retry reservation、snapshot masking、OpenHarness approval propagation、source-turn retry binding、cross-session approval rejection 未发现 P0/P1 测试缺口。
- 编译检查通过：`tools/policy_guard.py`、`apps/gateway/runtime.py`、`apps/gateway/artifacts.py`、`apps/gateway/storage.py`、`core/services/app_service.py`、`core/runtime_adapter/adapters.py`、`core/engine/query.py`、`openharness/engine/query.py`。
- Draw.io XML 校验通过：`current-vs-target-gap_v2.drawio` 与 `code-review-cleanup-checklist_v2.drawio`。
- 阶段并行验收：Control Plane 32 passed；Meeting/Artifact/Workflow 25 passed；Governance 33 passed；Core/Runtime/Pack 22 passed。
- HarnessOS `tests/` 主测试线通过：113 passed，1 skipped。
- Meeting real-audio lineage 用户态验收通过：`ASR_FUNASR_ENDPOINT=http://127.0.0.1:8001 scripts/e2e_meeting_validation.sh`，生成 `session_id=sess_0297614b55d7`、`turn_id=turn_38600f25256d`、`job_id=job_e4aa869ec7e1`，并形成 `transcript=art_7047472d8050 -> analysis=art_797dc6b7f92e -> result=art_e0e8cc73a25a -> minutes=art_552939a8fc5f`。
- 环境说明：完整仓库 `pytest` 会收集 `examples/` 外部框架样例并因依赖/运行时不匹配失败，不作为本阶段 HarnessOS 验收线；默认 `fixtures/audio_samples/sample_ted_talk.mp3` 尚不存在，本次用户态 Meeting 验收使用配置的本机音频目录。

### Phase 5-A：DomainPack 2.0 Assembly Kernel / Knowledge-primary Connector Stub

当前状态：已完成 MVP。

目标：让 Domain Pack 不只声明 workflow，而是成为可高质量装配、可查询、可治理、可扩展的业务流水线发布单元。本阶段以 Knowledge Pack 为主样板，采用 Contract + Connector Stub 方式对接 `meeting-voice-assistant/backend/data_service` 的 MCP 生命周期工具。

阶段定位：

- 当前主线不继续扩展会议助手自身，而是把 harnessOS 推进为 V3.0 的 DomainPack 2.0 基座。
- Phase 5-A 的第一目标是建立 DomainPack 2.0 Assembly Kernel，让 Pack manifest/DSL 成为业务能力的发现、装配、Agent 管理和治理入口。
- Gateway/Core 仍负责协议、治理、Store、Job、Artifact、Trace、Approval、Policy、Retry 等平台边界；业务 workflow、skills、connector refs、policy bundle refs 和 artifact schema 归属 Domain Pack。
- Knowledge Pack 是主验收样板；Video Studio 验证多 Agent / pipeline 形态；Meeting 验证真实链路不回归。

修改意图：

- 当前 Pack 已经能承载 workflow module，但仍偏静态工厂；Phase 5-A 要让 Pack 成为可配置、可组装、可迁移的业务单元。
- 为未来低代码编排和 DomainPack 直接编排打基础，让工作流、Agent、技能、策略、连接器和产物 schema 可以从 manifest/DSL 被发现和装配。
- 约束新业务不再回流 Gateway/Core，而是通过 Pack DSL 和 bundle 进入平台。
- DSL 不能绕过 Core 的 policy、approval、trace、job、artifact 边界。
- Phase 5-A 先冻结 data_service MCP tool contract 与 connector stub；Phase 5-C 已补齐真实 MCP client execution 和外部 Harness E2E；Phase 5-D 已补齐 FunASR MCP 与 Meeting -> Knowledge 跨域编排的当前集成 MVP。

修改范围：

- 扩展 pack manifest schema，增加 workflow DSL、skill refs、policy bundle refs、connector refs、artifact schema refs。
- 增加 Pack-owned Agent 声明：`agent_id`、`role`、`goal`、`model_policy`、`tool_refs`、`skill_refs`、`memory_scope`、`handoff_targets`。
- 引入 Typed DAG MVP：支持 node、edge、dependencies、inputs、outputs、artifact refs；节点类型限定为 `agent`、`skill`、`tool`、`connector`、`artifact`、`approval`、`evaluation`。
- 为 Knowledge Pack 提供主样板 DSL，声明 `data_service_mcp` connector contract 和知识库生命周期 pipeline。
- 为 Video Studio 提供多 Agent pipeline 样板；Meeting 保持现有真实 workflow 不回归。
- `pack.list/get` 展示装配状态、缺失依赖、blocked reason、版本信息。
- Pack assembly 对缺失 connector、缺失 policy bundle、版本不兼容给出可解释失败。
- 显式 domain 调用遇到 blocked pack 时返回可解释失败，而不是静默 fallback 到普通模型回复。

最小 manifest/DSL 字段：

- `manifest_schema_version`：Pack manifest schema 版本；不兼容时不得静默装配。
- `workflow_dsl`：描述 workflow 入口、步骤、输入输出和 artifact 链路。
- `workflow_templates`：DomainPack 2.0 的 Typed DAG 模板集合，作为后续低代码和 Pack 发布的统一模型。
- `agents`：Pack-owned Agent / role 定义。
- `skills` / `skill_refs`：声明 Pack 依赖的技能。
- `policy_bundles`：声明 Pack 执行时必须套用的治理策略集合。
- `connectors` / `connector_refs`：声明 Pack 依赖的外部连接器。
- `connector_capabilities`：声明 connector 必须提供的 MCP tools / resources / health 能力。
- `artifact_kinds` / `artifact_schemas`：声明 Pack 产出的 artifact 类型、schema 和 lineage 关系。
- `memory_scopes`：声明 workflow / agent 可读写的 memory 范围。
- `evaluation_rules`：声明产物或节点的质量评审规则。

执行顺序：

1. 扩展 pack manifest schema，保持旧 manifest 可兼容加载。
2. 建立 DomainPack 2.0 Assembly Kernel：输出 `assembled / blocked / degraded / stub` 状态、`missing_dependencies`、`blocked_reason`、`next_actions`。
3. 为 Knowledge Pack 增加 `data_service_mcp` connector stub 和 Typed DAG workflow template。
4. 为 Video Studio 增加 Pack-owned agents 与多 Agent DAG 模板。
5. 扩展协议查询面：`pack.list` / `pack.get` 展示 DAG、agents、skill refs、policy bundle refs、connector refs、artifact schemas、assembly status、missing dependencies 和 blocked reason。
6. 新增 Agent 查询面：`pack.agents`、`agent.list`、`agent.get`，第一阶段只做 registry/metadata/fake execution 测试，不做完整 agent runtime lifecycle。
7. 保持显式 domain 调用的可解释失败：缺 connector、缺 policy bundle 或 schema 版本不兼容时，`turn.start(domain=...)` 返回明确 blocked 原因。
8. 下一步做实 DSL 执行上下文：assembly 结果需要进入 workflow governed context，而不是只作为查询展示字段。

data_service MCP Contract + Connector Stub：

- harnessOS 侧声明 `data_service_mcp` connector ref、capability contract、health/assembly 展示和 blocked/degraded 语义。
- 本阶段不实现 harnessOS 到 `data_service.mcp_stdio` 的真实 MCP client，不管理外部 stdio 会话生命周期。
- data_service 外部 Agent 指南已落地：`/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/docs/data_service/MCP-EXTERNAL-AGENT-GUIDE.md`，入口已加入 `/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/docs/data_service/README.md`。
- 后续 Knowledge Pack 真实工作流必须使用该 MCP 指南定义的 lifecycle tools + v2 envelope tools，不直接读写 GraphRAG、llmwiki、quality 等内部产物目录。
- 当前领域 connector 分工固定为：Meeting 使用 `funasr_mcp` / `funasr_service` 完成语音转写；Knowledge 使用 `data_service_mcp` / `data_service` 完成 GraphRAG + llmwiki 知识库生命周期。
- data_service MCP server 已定义以下 tools：
  - `knowledge_workspace_create`
  - `knowledge_workspace_list`
  - `knowledge_workspace_describe`
  - `knowledge_source_import`
  - `knowledge_source_list`
  - `knowledge_source_remove`
  - `knowledge_build_start`
  - `knowledge_build_status`
  - `knowledge_build_cancel`
  - `knowledge_workspace_archive`
- 外部 Agent 新接入优先使用 v2 tools：`knowledge_query_v2`、`knowledge_quality_summary_v2`、`knowledge_quality_feedback_v2`、`knowledge_correction_rules_v2`、`knowledge_review_correction_rule_v2`、`knowledge_correction_plan_v2`。
- 统一返回字段：`workspace_id`、`operation_id`、`status`、`warnings`、`artifact_refs`、`next_actions`、`data`。
- 安全边界：workspace 必须位于 `DATA_SERVICE_WORKSPACE_ROOT` allowlist 下；source path 必须经过 allowlist、大小上限、sha256 去重和 symlink 防绕过；build 长任务必须通过 `operation_id` 轮询。
- 保留现有 `knowledge_ingest`、`knowledge_query`、`knowledge_quality_*` MCP tools 兼容性。

非目标：

- 不做完整图形化低代码 UI。
- 不一次性迁移所有历史 workflow 到 Typed DAG。
- 不实现复杂分布式 workflow engine。
- 不实现循环、复杂条件和真实局部重跑；并行只做 DSL 表达，不作为第一阶段执行要求。
- 不实现真实 data_service MCP client；真实 connector execution 延期到 Phase 5-C。
- 不允许 DSL 绕过 Core 的 policy、approval、trace、job、artifact 边界。
- 不在 Phase 5-A 完整实现多租户授权、远程 connector execution runtime 或产品级治理控制台；这些继续归入 Phase 5-C / Phase 6。

交付物：

- 扩展 pack manifest schema，增加 Typed DAG workflow templates、Pack-owned agents、skill refs、policy bundle refs、connector refs、connector capabilities、artifact schema refs、memory scopes 和 evaluation rules。
- Knowledge Pack 提供 `data_service_mcp` connector contract/stub 与知识库生命周期 DAG。
- Video Studio 提供多 Agent DAG 样板；Meeting 保持现有真实链路不回归。
- `pack.list/get` 展示装配结果、DAG、agents、缺失依赖和 blocked/degraded reason。
- `pack.agents`、`agent.list`、`agent.get` 展示 Pack-owned Agent registry。
- Pack assembly 对缺 connector、缺 policy bundle、schema version 不兼容给出稳定 blocked 结果。
- 显式 domain 调用对 blocked pack 返回可解释失败。

验收标准：

- `pack.get(domain=knowledge)` 能展示 Typed DAG、Pack-owned agents、`data_service_mcp` connector requirement、tool contract 和 blocked/degraded 状态。
- `agent.list` / `agent.get` 能查询 Knowledge / Video Studio 的 Pack-owned agents。
- 禁用 connector、缺少 connector capability 或缺少 policy bundle 时，显式 domain 调用返回可解释 blocked/degraded 状态。
- Pack manifest schema 有版本字段，版本不兼容时不会静默装配。
- Knowledge Pack 的 Typed DAG 和 data_service MCP contract 可被测试加载。
- Video Studio 多 Agent DAG 可被测试加载。
- Meeting lineage 用户态验收不回归。
- 默认开发测试线通过；真实音频验收在本地 FunASR 服务可用时通过。

已验收：

- Phase 5-A 定向回归：`tests/test_pack_registry.py tests/test_pack_execution.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py -q` 为 42 passed。
- HarnessOS `tests/` 主线：125 passed、1 skipped。
- 真实音频用户态验收：启动本地 FunASR 后，`tests/test_meeting_audio_acceptance.py tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance -q` 为 2 passed。
- Knowledge Pack 已展示 `data_service_mcp` Contract Stub、知识库生命周期 Typed DAG、Pack-owned agents、connector capabilities、policy bundle refs 和 artifact schemas。
- Video Studio 多 Agent DAG 可通过 `pack.plan` / `workflow.plan` 构建 deterministic plan；显式 blocked pack domain 调用返回可解释 `turn.failed`。

### Phase 5-B：Memory & Session Intelligence

当前状态：已完成 MVP。

目标：强化 Harness Core 内部记忆机制，提升长会话、多轮追问和 artifact-backed context 能力。

修改意图：

- 当前系统能记录 session、turn、artifact、trace，但还缺“可被 Agent 主动复用的记忆层”。
- Phase 5-B 要把会议纪要、转写、分析、用户反馈等产物转化为可查询的 session memory reference。
- 支持长会话压缩和多轮追问，减少重复分析，提升 Agent 框架本身的连续工作能力。

修改范围：

- 新增 session summary / memory reference 的 Core service 与存储模型。
- 支持从 artifact lineage 提取 memory refs，例如 transcript、analysis、minutes。
- turn.start 可在受控范围内读取当前 session 的 summary 和相关 artifact-backed memory。
- memory read/write 进入 trace，并继续使用 secret masking。

非目标：

- 不做跨用户全局记忆。
- 不默认把所有 artifact 内容长期注入 prompt。
- 不绕过 artifact 权限和 secret hygiene。
- 不引入外部向量数据库作为强依赖；如需检索，先保持本地优先和可选扩展。

交付物：

- 增加 session summary / long-context compression 的 Core service。
- 支持从 artifact lineage 中提取 memory reference，例如 transcript/minutes/analysis。
- 多轮 Meeting 追问可引用前序会议产物，而不是重新上传或重新分析。

验收标准：

- 长会话可生成、更新和查询 session summary。
- Meeting 会议分析后，用户追问“基于刚才会议纪要继续总结 action items”时可引用前序 transcript/minutes artifacts。
- memory refs 能记录来源 artifact id、session id、turn id 和摘要内容。
- memory 写入和读取进入 trace，敏感信息继续脱敏。
- 没有可用 memory 时，系统返回可解释的 fallback，而不是编造前序上下文。

已验收：

- 新增 Core-native `MemoryRecord`、SQLite `memory_records`、CoreAppService memory facade。
- Gateway 新增 `memory.list`、`memory.get`、`memory.summary`、`memory.extract_from_artifacts` 与 `core.memory.list` RPC。
- Runtime 普通 turn 可注入 compact session memory context；approved retry / approval continuation 保持原始输入，避免破坏审批绑定和幂等重放。
- Meeting workflow 完成后可从 artifact records 生成 `artifact_ref:*` memory refs；session summary 使用 deterministic summarizer，LLM 摘要继续保留为后续可选增强，不作为默认验收依赖。
- 默认本地回归：`python3 -m pytest tests -q -k 'not phase1b_real_audio_turn_start_acceptance and not phase1_meeting_acceptance_uses_workspace_audio_dir'` 为 128 passed、1 skipped、2 deselected。
- 真实音频用户态验收：启动本地 FunASR 后，`tests/test_meeting_audio_acceptance.py tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance -q` 为 2 passed。

### Phase 5-C：Connector Execution Runtime

目标：把 connector 从 descriptor/health 推进到可执行 runtime。Remote ComfyUI 仍为后续验证对象，不作为当前主线。

修改意图：

- 当前 Connector Registry 能发现服务和健康状态，但 connector 还没有统一的执行生命周期。
- Phase 5-C 要把 connector execution 纳入 Core job/events/artifact/trace，让外部服务调用和本地工具调用具备一致治理边界。
- 为未来 Remote ComfyUI、知识库服务、数据源、浏览器自动化等 connector 提供可迁移执行模型。

修改范围：

- 定义 connector execution interface：submit、poll、cancel、collect。
- 将 connector execution 绑定 Core job、job.events、failure_context、artifact collect。
- 选择一个轻量 connector 完成端到端验证，避免当前机器资源不足时阻塞主线。
- 新增 `funasr_mcp` 作为 Meeting/ASR 底层 connector，先完成 MCP contract、health 与 stubbed connector job 记录。
- Remote ComfyUI 保持 descriptor/scaffold，可在远程工作站可用后作为迁移验证对象启用。

非目标：

- 不把 Remote ComfyUI 作为默认验收路径。
- 不要求本机执行重型视频生成。
- 不引入分布式队列作为当前强依赖。
- 不允许 connector 返回的外部产物绕过 artifact registry。

交付物：

- 定义 connector job 的 submit/poll/cancel/collect 最小接口。
- 至少选择一个轻量 connector 完成 job lifecycle 验证。
- FunASR MCP stdio 入口位于 `meeting-voice-assistant/backend/funasr_service`，通过 HTTP proxy 调用既有 FunASR 服务。
- Remote ComfyUI connector 保持 `not_configured/configured` descriptor，真实执行等远程环境可用后再启用。

验收标准：

- 至少一个轻量 connector 可完成 submit -> poll -> collect 的 job lifecycle。
- connector execution job 能写入 Core job/events/artifacts。
- cancel 后 job 进入明确终态，failure_context 可查询。
- collect 的产物必须进入 artifact registry，并可参与 lineage 查询。
- `funasr_mcp` 可被 `connector.list/get/health` 发现，`connector.submit` 可记录 `funasr_recognize_file` job/artifact。
- 没有配置远程 ComfyUI 时，不影响 Meeting/Knowledge 主线验收和默认测试。

完成状态（2026-05-03 更新）：

- Phase 5-C 当前 MVP 已完成。
- `connector.submit/poll/cancel/collect` 已接入 Core job/events/artifact。
- `data_service_mcp` 默认保持 contract stub；显式设置 `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 时可执行真实 MCP stdio tool call。
- Knowledge lifecycle runner 已使用持久 MCP stdio session 跑通真实 data_service 端到端，避免 data_service build queue 因 MCP 进程退出丢失状态。
- 真实验收链路已通过：`create -> import -> build -> poll -> query_v2 -> feedback_v2 -> correction_rules_v2 -> review_v2 -> correction_plan_v2 -> archive`。
- 验收证据：`HarnessOSRealDataServiceAcceptance4` 返回 `status=ok`、`workspace_id=harnessosrealdataserviceacceptance4`、`operation_id=op_fb639a7aee3c`、`warnings=[]`。
- 环境前置：相邻项目 data_service venv 必须完整安装 `backend/requirements.txt`；缺少 `numpy`、`pandas` 等 GraphRAG 依赖会导致 build 阶段失败。
- `funasr_mcp` 仍默认 contract stub / legacy Meeting MCP 兼容路径；显式 stdio 调用与 Meeting workflow 接入已在 Phase 5-D 完成当前集成 MVP。

### Phase 5-D：Cross-domain MCP Workflow Stabilization

目标：把已验证的 Knowledge MCP 真实接入、FunASR MCP contract 和 Meeting Pack 编排合并为稳定的双域 MCP 工作流。阶段主线是 `audio -> transcription -> meeting minutes -> knowledge import/build/query`，所有跨项目能力都通过 MCP connector 调用。

修改意图：

- Knowledge MCP 真实 E2E 已通过，但仍需要固化为可重复 smoke/acceptance。
- FunASR MCP 目前已具备 server/connector contract，并已作为 Meeting workflow 的显式真实调用路径。
- Meeting 与 Knowledge 已通过 artifact lineage 和 connector job 完成真实串联，但仍保留产品化治理、超时、取消和重试增强空间。

修改范围：

- 固化 Knowledge MCP 验收脚本、依赖检查和文档入口。
- 为 `funasr_mcp` 增加显式 stdio 执行验收，覆盖 `funasr_health` 与 `funasr_recognize_file`。
- Meeting workflow 的转写步骤改为可配置 MCP 调用，保留旧路径兼容和 contract stub fallback。
- 新增跨域 runner/workflow：会议音频产物进入会议纪要，再作为 data_service source 导入知识库。
- 统一记录 connector execution lineage：`connector_id`、`tool`、`job_id`、`operation_id`、`envelope.status`、`artifact_id`。

非目标：

- 不把 FunASR 模型加载作为默认 CI 前置。
- 不让 harnessOS 直接写相邻项目的 FunASR、GraphRAG、LLMWiki、quality 或 workspace 内部产物目录。
- 不在本阶段完成产品级多租户授权和远程视频渲染。

交付物：

- Knowledge MCP smoke/acceptance 脚本与文档更新。
- FunASR MCP 真实 stdio smoke。
- Meeting workflow 可配置 FunASR MCP 调用路径。
- Meeting -> Knowledge 跨域 E2E runner。
- 端到端 artifact lineage：audio/transcript/minutes/source/build/query。

验收标准：

- 一条 HarnessOS 命令可跑通 `audio -> funasr_mcp transcription -> meeting minutes -> data_service_mcp import/build/query`。
- 默认测试仍不依赖真实 FunASR 模型、真实 data_service server 或外部网络。
- 显式集成验收必须通过环境变量开启，并在缺依赖时返回可解释 blocked/failed。
- 所有跨项目调用均通过 MCP connector，不能直接读写相邻项目内部产物目录。
- connector job、operation、artifact lineage 可追踪到每个关键阶段。

当前实现进展：

- `GatewayRuntimePool` 已复用同一套 `ConnectorExecutionRuntime`，供 RPC 和 DomainWorkflow 共享 connector job/artifact 记录。
- `funasr_mcp` 已具备 gated stdio execution 验收入口：`scripts/e2e_funasr_mcp_validation.py`，默认未设置 `HARNESS_FUNASR_MCP_EXECUTION=stdio` 时返回 blocked。
- Meeting workflow 已接入可配置 FunASR MCP 转写路径；启用 stdio 时先通过 `connector.submit(funasr_mcp, funasr_recognize_file)` 生成 transcript，再调用 Meeting MCP text analysis/minutes 兼容路径。
- `ConnectorExecutionRuntime.submit` 已支持 `parent_artifact_ids`，Knowledge MCP lifecycle runner 会把 connector result artifact 串入 Core lineage。
- 新增 `MeetingToKnowledgeMcpRunner` 和 `scripts/e2e_meeting_to_knowledge_mcp_validation.py`，用于 `audio -> transcript/minutes -> knowledge import/build/query` 跨域验收。
- `scripts/e2e_data_service_mcp_validation.py` 已增加真实 stdio gate，避免默认环境误触发相邻 data_service。
- 代码级回归已通过 fake MCP stdio 覆盖；真实 FunASR + 真实 data_service 用户态验收已通过，证据为 `scripts/e2e_meeting_to_knowledge_mcp_validation.py` 返回 `status=ok`、session `sess_333527af725f`、meeting session `meeting_cceef461`、workspace `harnessos-meeting-knowledge-phase5d-retry`、artifact lineage count `33`。

已验收：

- FunASR MCP 真实 smoke：`HARNESS_FUNASR_MCP_EXECUTION=stdio` 下通过 `funasr_health -> funasr_recognize_file`，返回 connector job `job_db4b4114eab3`、artifact `art_5f24f94bfbdc`。
- Data Service MCP 真实 smoke：`HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 下通过完整 Knowledge lifecycle，返回 workspace `harnessos-real-data-service-phase5d`、operation `op_7df6de70eb14`。
- Meeting -> Knowledge 真实跨域 smoke：`audio -> funasr_mcp transcript -> meeting minutes -> data_service_mcp import/build/query` 返回 `status=ok`，形成 33 条 artifact lineage。
- 修复真实验收暴露的 transcript artifact 缺口：Meeting text-analysis/minutes 兼容路径现在会为 FunASR 结果登记 transcript artifact，并把 `connector_id`、`connector_job_id`、`transcription_artifact_id`、`transcription_mode`、`transcription_tool` 写入 metadata。
- 定向回归：`tests/test_meeting_turn_workflow.py::test_turn_start_meeting_can_transcribe_with_funasr_mcp_stdio tests/test_gateway_protocol.py::test_meeting_to_knowledge_cross_domain_runner_links_lineage` 为 2 passed。
- 默认本地回归：`python3 -m pytest tests -q -k 'not phase1b_real_audio_turn_start_acceptance and not phase1_meeting_acceptance_uses_workspace_audio_dir'` 为 133 passed、1 skipped、2 deselected。

剩余边界：

- 默认 CI 仍不启动真实 FunASR 模型或 data_service server，真实服务验收必须显式设置环境变量。
- 当前 cross-domain runner 是后端验收 runner，不是产品化 UI/BFF。
- 超时、取消、retryable failure、server interrupted recovery 和 product-grade operation dashboard 仍应作为 Phase 5-D hardening 或 Phase 6 范围继续补强。

### Phase 6：Productization / Open Source / Commercial Readiness

目标：从内部平台原型进入可发布、可扩展、可维护状态。

修改意图：

- 当前项目已经形成平台内核雏形，但还缺对外发布、扩展开发、治理边界和长期维护规范。
- Phase 6 要把协议、扩展、部署、贡献、发布和安全说明补齐，让项目可以被团队外开发者理解和扩展。
- 为后续开源、商业化或多项目复用提供稳定交付基础。

修改范围：

- API versioning、schema freeze、compat policy。
- Extension examples：tool、skill、connector、pack。
- CONTRIBUTING、release flow、部署文档、运维文档。
- 多租户、审计、secret scope、connector scope 的正式治理模型。

非目标：

- 不在此阶段强推 SaaS 多租户产品化实现。
- 不把所有外部服务变成默认依赖。
- 不牺牲本地优先、协议优先和 Pack 边界。

交付物：

- API versioning 与 schema freeze。
- Extension examples：至少覆盖 tool、skill、connector、pack。
- CONTRIBUTING、release flow、部署文档、运维文档。
- 多租户、审计、secret scope、connector scope 的正式治理模型。

验收标准：

- 新开发者可在 30 分钟内跑通 smoke test 与 Meeting lineage acceptance。
- API/extension 文档足以支持第三方扩展开发。
- 至少提供 tool、skill、connector、pack 四类扩展示例。
- 默认测试与 smoke 通过，真实模型/外部服务验收继续使用显式环境变量门控。
- release note、版本号、兼容策略和升级说明可被审阅。

## 6. 每阶段强制同步规则

每完成一个阶段，必须同步更新：

- `docs/architecture/CURRENT-STATUS_v2.md`
- `docs/architecture/current-vs-target-gap_v2.md`
- `docs/architecture/current-vs-target-gap_v2.drawio`
- `docs/architecture/development_plan_v2.md`
- `docs/test-acceptance-plan_v2.md`
- `docs/acceptance-test-cases_v2.md`

每阶段必须执行：

- 阶段定向自动化测试。
- 阶段相关完整回归。
- `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio`。
- 使用团队标准样本目录 `fixtures/audio_samples/` 完成会议端到端验收；在标准 fixture 落地前，可使用本机真实音频作为 local validation evidence。
- 验收后清理外部会议产物和本地 `.harnessos` 验收记录。

## 7. 扩展准入规则

任何新业务或新能力进入开发前，必须回答：

- 属于 Core、Pack、Connector、Runtime Adapter 还是 Client / Gateway？
- 是否会产生重要结果，是否需要 Artifact 化？
- 是否是长任务，是否必须进入 Job Service？
- 是否包含写入、删除、发送、发布、交易或策略执行等高风险动作，是否需要 Policy / Approval / Trace？
- 是否需要新 connector，是否具备 registry、config ref 和 health check？
