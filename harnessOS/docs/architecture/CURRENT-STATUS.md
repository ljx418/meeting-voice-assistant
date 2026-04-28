# harnessOS 架构文档

## 一、当前项目状态 (Core v1.5-E Runtime Adapter 收敛 MVP 已完成)

更新时间：2026-04-28

当前 harnessOS 自身已经完成 Phase 0.7 控制面收口：CLI/headless、FastAPI `/v1/runs`/SSE、`/v1/rpc`、stdio JSONL、session/turn 生命周期、RuntimeBundle 优先与 SimpleRuntime fallback 都可用。

Phase 1 的会议场景已完成 Headless/RPC、聊天自动编排、会议产物登记和通用工作流编排 MVP：harnessOS 现在可以通过 `meeting.*` Gateway RPC、`turn.start(domain=meeting)` 或普通聊天/headless 输入中的会议音频路径启动相邻项目 `meeting-voice-assistant` 的 Meeting MCP server。会议 workflow 已从 `GatewayRuntimePool` 硬编码特例迁移为 `meeting.workflow`，由 Lead Orchestrator 和 DomainWorkflow Registry 统一路由。会议产出的 `transcript`、`analysis`、`result`、`minutes` 已能登记为 harnessOS artifact，并通过 `artifact.list/get/read/register` 查询和读取。针对较长真实音频，Meeting MCP stdio 读取上限已提高到 128MB，并保留“只转写 -> 压缩转写分析 -> 生成纪要”的降级路径。知识场景已有 `knowledge.workflow` MVP。面试场景本阶段暂缓，并通过测试避免面试音频误触发会议 workflow。

Phase 2-A 已完成 Trace/Audit MVP：Gateway 现在会为 `turn.start` 生成 `trace_id`，将 `turn.started`、`item.delta`、`tool.*`、`turn.completed/failed` 等事件同步写入 TraceStore，并提供 `trace.list`、`trace.get` RPC。Artifact 的 `register/list/get/read` 操作也会写入 trace。会议 workflow 的 `turn.completed` trace 记录可关联 `meeting.workflow` 以及 `analysis/minutes/result/transcript` artifact id；知识 workflow 的完成事件也会关联 `knowledge.workflow`。

Phase 2-B 已完成 Approval Coordinator MVP：Gateway 现在提供 `approval.request`、`approval.list`、`approval.get`、`approval.approve`、`approval.reject` RPC。审批记录包含 `approval_id`、`trace_id`、`session_id`、`turn_id`、`risk_level`、`action`、`status`、`request_summary`、`decision_reason`、`created_at`、`decided_at` 和 `metadata`。审批创建、批准、拒绝都会写入 TraceStore，可通过同一 `trace_id` 串起审批生命周期。

Phase 2-C 已完成 Policy Rules MVP：Gateway 新增 `PolicyEvaluator` 与 `policy.evaluate` RPC，并在 `turn.start` 执行 workflow/model 之前做策略预检。明确的写入、保存文件、创建文件、删除、发送、发布类请求会先生成 pending approval，并写入 trace；读取、检索、会议分析和会议纪要生成不触发审批。

Phase 2-D 已完成 Retry/Resume MVP：Gateway 新增 `RetryStore` 与 `turn.retry` RPC。被 policy gate 拦截的原始 turn 会保存为 retry context，pending/rejected approval 不能 retry；approval 通过后可用 `approval_id` 或原 `turn_id` 触发重试，重试 turn 会带上 `retry_of_turn_id`、`approval_id` 和新的 `trace_id`，并跳过本次 policy gate 继续执行原动作。重复 retry 会被拒绝，避免同一审批动作重复执行。

Phase 2-E 已完成 Secret Hygiene MVP：Gateway 新增统一脱敏工具，对 `sk-*`、`Authorization: Bearer ...`、`api_key/token/secret/password` 等常见敏感字段做 mask。脱敏已接入 session event log、TraceStore、ApprovalStore、RetryStore、ArtifactRegistry metadata 和 `artifact.read` 返回内容。当前目标是避免 prompt/log/trace/artifact 读取面泄露明文密钥；外部原始 artifact 文件本身不会被就地改写。

Phase 2-F 已完成 Architecture Hardening MVP：把本阶段架构复查中发现的 P0 “本地 JSON 文件存储无锁、无事务”作为设计输入，新增统一本地持久化工具，提供 `.lock` 文件互斥、JSON list 读改写临界区、JSONL 追加锁和原子替换写入。当前已覆盖 session snapshot/events、TraceStore、ApprovalStore、RetryStore、ArtifactRegistry。并发写测试覆盖 approval/retry/artifact，相关回归为 54 passed。

Phase 3-A 已完成 App Lifecycle MVP：FastAPI route 不再持有模块级 `_gateway = GatewayService()` 单例，`GatewayService` 改为应用生命周期内的 `app.state.gateway_service`，并通过 dependency injection 注入到 `/v1/runs`、SSE、session 查询和 `/v1/rpc`。`create_app(gateway_service=...)` 已支持测试和部署侧注入同一个 GatewayService 实例，避免测试/运行时隐式共享模块全局状态。相关回归为 57 passed。

Core v1.5-A 已完成：新增 `core.protocol`、`core.stores` 与 `CoreAppService` 基础层，定义 `SessionRecord`、`ThreadRecord`、`TurnRecord`、`ItemRecord`、`JobRecord`、`ArtifactRecord`、`ApprovalRecord`、`TraceRecord`、`RetryRecord`、`ConnectorRecord`，并新增 `CoreSQLiteStore`。当前 Store 支持 session/thread/turn/item/job/artifact/trace/approval/retry 的 SQLite CRUD 与过滤查询，并支持将 legacy Gateway session snapshot/events 保守导入为 Core session/thread/turn/items。现有 Gateway 执行链路已通过 `CoreAppService` 写入 Core SQLite：`session.start/session.close` 已改为 Core-native session mutation，`turn.started/item.delta/turn.completed/turn.failed/turn.interrupted` 已改为 Core-native thread/turn/item mutation，会议 workflow 返回的 artifact records、artifact RPC trace、policy approval/retry context 也已通过 CoreAppService 原生转换为 Core artifact/trace/approval/retry records。`GatewayRuntimePool` 与 `GatewayService` 不再暴露 `CoreRuntimeRecorder` 运行时依赖；旧 Gateway stores 只作为兼容 runtime source 保留。查询面包括 `session.get`、`thread.list`、`turn.get`、`turn.items`、`core.artifact.list`、`core.trace.list`、`core.approval.list`、`core.retry.list`。

Core v1.5-B 已完成 Pack System MVP：新增 `core.packs` 和仓库级 `packs/` manifest，当前可加载 meeting、knowledge、investment、interview、video_studio 五个 pack。meeting/knowledge 是 active pack，分别声明 `meeting.workflow` 和 `knowledge.workflow`；investment/interview/video_studio 是 manifest stub，用于后续资产管理/面试助手/AI 视频工作室迁移。Gateway 新增 `pack.list`、`pack.get` RPC，`initialize.capabilities.packs=true`，`workflow.list` 会返回 workflow 对应的 pack name/version/status。当前 pack 仍是 manifest/查询/可见性 MVP，尚未驱动 connector、skill、policy bundle 和 workflow DSL 的完整装配。

Core v1.5-B 阶段验收已完成：Pack/Gateway 相关定向回归为 22 passed；阶段相关完整回归为 70 passed；`current-vs-target-gap.drawio` 通过 XML 校验。真实音频用户态验收命令 `python3 -m cli.main run --json '请分析 /Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3，生成会议纪要'` 已通过，生成 session `sess_62d7269e6d9f`、turn `turn_d0cc73ce6ac6`、trace `trace_4c46943461ab`、meeting output `meeting_c5c47fc9`，随后已按阶段验收要求清理外部会议产物和本地 `.harnessos` 验收记录，避免冗余空间和幂等性干扰。

Core v1.5-C 已完成 Job Service MVP：复用 Core `JobRecord` 和 SQLite jobs 表，新增 `CoreAppService.start_job/update_job/cancel_job/get_job/list_jobs`。Gateway 在命中 DomainWorkflow 时会创建 Core job，workflow 执行结束后更新为 `completed` 或 `failed`，并把 `job_id`/`job` 写入 `turn.completed.data`。Gateway 新增 `job.list`、`job.get`、`job.cancel` 和 `core.job.list` RPC，`initialize.capabilities.jobs=true`。当前实现是“同步执行 + job 记录/查询/取消状态”的 MVP，不是后台 worker 队列；会议真实音频仍按现有 CLI 同步返回，但已经可以在 Core SQLite 中形成 job/artifact/trace 关联。

Core v1.5-C 阶段验收已完成：定向回归为 36 passed，阶段相关完整回归为 72 passed，`current-vs-target-gap.drawio` 通过 XML 校验。真实音频用户态验收命令 `python3 -m cli.main run --json '请分析 /Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3，生成会议纪要'` 已通过，生成 session `sess_3b81600b8244`、turn `turn_d815946c90a9`、trace `trace_c8334f2e46cd`、job `job_c3f8541207ed`、meeting output `meeting_1400e111`，job 状态为 `completed` 并关联四个会议 artifact。验收后已清理外部会议产物和本地 `.harnessos` 验收记录。

Core v1.5-D 已完成 Tool Policy Middleware MVP：新增 `tools.policy_guard`，在 builtin LangChain tools 外层执行 `PolicyEvaluator.evaluate_tool`；`workspace_write_file`、`kb_ingest`、`artifact_save` 等写入型工具在没有 `approved=True` 或已批准 `approval_id` 时不会执行真实函数。Gateway 创建默认 agent 时会把 `PolicyEvaluator` 和 ApprovalStore checker 注入 builtin tools。Core engine `_execute_tool_call` 也会从 `tool_metadata.policy_evaluator` 读取执行层策略，在 `tool.execute(...)` 前阻断高风险工具。当前实现是执行层阻断 MVP，尚未在工具层自动创建 approval request，也尚未把 OpenHarness TUI runtime 默认注入 policy evaluator；下一步仍需把所有 runtime adapter 的 tool_metadata 和 approval coordinator 完整打通。

Core v1.5-D 阶段验收已完成：定向回归为 20 passed，阶段相关完整回归为 77 passed，`current-vs-target-gap.drawio` 通过 XML 校验。真实音频用户态验收已再次通过，生成 session `sess_1b200a488e38`、turn `turn_0b4a804cc51d`、trace `trace_0ed74dc2c3f5`、job `job_741a70df5a79`、meeting output `meeting_338e1a81`，说明会议 MCP 读/分析路径没有被工具策略误拦截；验收后已清理外部会议产物和本地 `.harnessos` 验收记录。

Core v1.5-E 已完成 Runtime Adapter 收敛 MVP：新增 `RuntimeHandle`、`RuntimeAdapter`、`SimpleRuntimeAdapter` 和 `OpenHarnessRuntimeAdapter`。`GatewayRuntimePool` 不再直接创建 SimpleAgent 或 OpenHarness RuntimeBundle，而是通过 adapter `start/invoke/stream/continue_pending/close` 管理运行时，并在 `RuntimeSession` 中保留 `handle` 和 `adapter` 作为运行时边界。Simple runtime、fake agent 测试注入和 OpenHarness bundle streaming/continue 路径均保持兼容。当前实现已把上层调用边界收敛到 Core adapter，但 adapter 级 `tool_metadata`、approval coordinator 自动注入、Core-native session/event store 替换和后台 job worker 仍留给下一阶段。

Core v1.5-E 阶段验收已完成：定向回归为 20 passed，阶段相关完整回归为 81 passed，`current-vs-target-gap.drawio` 通过 XML 校验。真实音频用户态验收已再次通过，生成 session `sess_577589d07dcb`、turn `turn_d0a38326db77`、trace `trace_fb768bc3be1e`、job `job_e881abee5217`、meeting output `meeting_ebdc8357`，并登记 `analysis=art_dd5dbdea9a22`、`minutes=art_407f47e707e0`、`result=art_2c8dc8a53d6d`、`transcript=art_4d391af72d7c` 四个 artifact。验收后已清理外部会议产物和本地 `.harnessos` 验收记录，SQLite 对应记录计数为 0。

### 架构转向：V2.0 目标架构已采纳

`docs/design/V2.0/harnessos_architecture_master_spec.md` 已被采纳为下一版正式目标架构主干。该设计与当前 Core v1.5-E 方向一致，但定位更明确：harnessOS 的最终目标不是单一助手，也不只是当前 Gateway/Workflow 集合，而是 **Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform**。

V2.0 设计质量较高，适合作为目标架构基线；但它仍是总体蓝图，不是接口冻结规格。后续实现前必须补齐 JSON-RPC method/event/error 规范、Pack 装配语义、Job Worker 状态机、治理执行顺序、Connector/Secret scope 与多租户安全模型。当前策略是保留 Core v1.5-E 代码与验收基线，采用渐进迁移，不立即执行大规模目录搬迁。

从下一阶段开始，harnessOS 不再按“继续扩展会议助手”推进，而是升级为 **协议优先、可治理、可扩展、可迁移的 Agent Harness Core / OS-like App Server**。目标形态是：

- **Harness Core**：协议对象、运行时适配、治理、Store、Job、Artifact、Trace、Approval、Policy、Retry。
- **Protocol App Server**：CLI、Web、Headless、Bot、stdio JSONL、SSE 共享同一套 Core-native RPC 语义。
- **Domain Packs**：会议、知识、投资、面试、AI 视频工作室等业务能力通过 pack 挂载，Core 不写死业务逻辑。
- **Gateway Clients**：前端和自动化客户端只通过协议访问 Core，不直接调用业务 service。

已确认的下一阶段决策：

- Core 优先，而不是优先新增视频/投资/面试业务功能。
- 接受大重构，允许破坏旧 Gateway method 命名和响应结构。
- SQLite 作为下一阶段默认 Store，保留 `.harnessos` JSON/JSONL legacy 双读/导入迁移。
- 正式引入 `Session / Thread / Turn / Item` 对象模型。
- meeting/knowledge 已迁移为 manifest-backed Domain Pack；investment/interview/video_studio 已做 manifest stub。
- 验收主场景继续使用 `/Users/Zhuanz/Desktop/workspace/音频资料` 下真实音频验证 Meeting Pack。
- V2.0 目标架构文档详见 `docs/architecture/harnessos_target_architecture_v2.md`。
- V2.0 开发计划详见 `docs/architecture/development_plan_v2.md`；后续从 Phase 3-B 继续执行。

当前阶段判断：

- Phase 1 已完成 MVP：Meeting MCP、真实音频会议分析、会议产物登记、Lead Orchestrator、DomainWorkflow Registry、KnowledgeWorkflow MVP 均已验收；Interview 暂缓，不再作为 Phase 1 阻塞项。
- Phase 2 已完成 MVP：Trace、Approval、Policy、Retry、Secret Hygiene、Persistence Hardening 均已验收。
- Phase 3-A 已完成：API App Lifecycle 和 GatewayService DI 已验收。
- 后续主线从 **Phase 3-B Core-native Session/Event Store** 开始。

### 1.1 当前实现的目录结构

```
harnessOS/
├── cli/                           # ✅ CLI 交互入口 (Phase 0 完成)
│   ├── __init__.py
│   ├── main.py                    # CLI 主入口，支持 REPL / --oh / run
│   ├── session.py                 # 会话管理
│   └── renderer.py                # 输出渲染
│
├── core/                          # 核心模块
│   ├── config/                    # ✅ 配置管理
│   │   └── __init__.py           # Pydantic Settings
│   │
│   ├── schemas/                   # ✅ 核心 Schema (Phase 0 完成)
│   │   └── __init__.py           # Message, ToolCall, AgentRequest 等 12 个类型
│   │
│   ├── orchestration/             # ✅ 编排层 (Phase 0 占位)
│   │   ├── intent_router.py      # IntentRouter (关键词路由)
│   │   └── workflow_dispatcher.py
│   │
│   ├── runtime_adapter/          # ✅ Runtime 适配器
│   │   ├── __init__.py           # 自动降级: Deep Agents → Simple Runtime
│   │   └── simple_runtime.py     # 简化运行时 (mock 模式)
│   │
│   ├── middleware/
│   │   └── hooks/                # ⬅️ 从 OpenHarness 迁移
│   │       ├── events.py
│   │       ├── executor.py
│   │       ├── hot_reload.py
│   │       ├── loader.py
│   │       ├── schemas.py
│   │       └── types.py
│   │
│   └── policies/
│       └── permissions/           # ⬅️ 从 OpenHarness 迁移
│           ├── checker.py
│           └── modes.py
│
├── tools/                         # ✅ 工具集 (Phase 0 完成)
│   ├── __init__.py               # get_builtin_tools()
│   ├── base.py                   # Tool 基类
│   ├── workspace.py              # workspace_ls/read/write
│   ├── knowledge.py              # kb_search/ingest
│   ├── artifact.py               # artifact_save/list/get
│   ├── openharness_base.py       # ⬅️ OpenHarness BaseTool
│   └── openharness_tools.py      # ⬅️ OpenHarness 工具注册表
│
├── agents/                        # Agent 定义
│   └── swarm/                    # ⬅️ 从 OpenHarness 迁移 (多代理)
│       ├── team_lifecycle.py
│       ├── lockfile.py
│       ├── mailbox.py
│       ├── permission_sync.py
│       ├── registry.py
│       ├── subprocess_backend.py
│       └── worktree.py
│
├── execution/                     # 执行平面
│   └── mcp/                      # ⬅️ 从 OpenHarness 迁移
│       ├── client.py
│       ├── config.py
│       └── types.py
│
├── apps/                          # 应用层
│   ├── api/                      # ✅ FastAPI 应用与 /v1 协议入口
│   │   ├── __init__.py           # ✅ Phase 3-A app lifecycle + GatewayService 注入
│   │   ├── dependencies.py       # ✅ Phase 3-A FastAPI dependency provider
│   │   └── routers/
│   │       ├── agents.py
│   │       ├── health.py
│   │       └── routing.py
│   │
│   ├── web/                     # ✅ Vue 3 前端 (Phase 0 骨架)
│   │   └── src/
│   │       ├── components/
│   │       ├── pages/
│   │       ├── router/
│   │       ├── stores/
│   │       └── api/
│   │
│   └── gateway/                  # ✅ 项目自有本地 Gateway 协议边界
│       ├── artifacts.py          # ✅ Artifact Registry + artifact RPC 支撑
│       ├── bridge.py
│       ├── config.py
│       ├── meeting.py            # ✅ Meeting MCP client + turn workflow
│       ├── models.py
│       ├── persistence.py         # ✅ Phase 2-F locked + atomic local persistence
│       ├── policies.py           # ✅ Phase 2-C 策略预检与工具风险分类
│       ├── protocol.py
│       ├── retries.py            # ✅ Phase 2-D retry context store
│       ├── secrets.py            # ✅ Phase 2-E persistence boundary masking
│       ├── router.py
│       ├── runtime.py
│       ├── service.py
│       ├── stdio_server.py
│       └── workflows.py          # ✅ Lead Orchestrator + DomainWorkflow Registry
│
├── devplane/                      # 开发者控制面
│   └── commands/                 # ⬅️ 从 OpenHarness 迁移
│       └── registry.py
│
├── docs/
│   ├── api/                      # ✅ API 设计文档
│   ├── architecture/             # ✅ 架构文档
│   └── design/                  # ⬅️ OpenHarness 设计文档
│
└── artifacts/                    # 工件存储目录
```

### 1.2 当前实现的组件

| 组件 | 状态 | 说明 |
|------|------|------|
| CLI 交互 | ✅ 完成 | REPL、`--oh` TUI、`run` headless 均可用 |
| Headless CLI | ✅ 完成 | `python3 -m harnessOS.cli.main run "你好"` 可直接获得回复 |
| Core Schemas | ✅ 完成 | 12 个核心类型 |
| Intent Router | ✅ 占位 | 关键词路由，待升级 LLM |
| API Gateway | ✅ Phase 0.6 完成 | FastAPI `/v1/runs`、SSE、session 查询、`/v1/rpc` |
| Gateway Protocol | ✅ Phase 0.6 完成 | RpcRequest/RpcResponse/GatewayEvent + initialize/session.*、turn.* |
| Web Frontend | ✅ 骨架 | Vue 3 项目结构 |
| Tools | ✅ 基础 | workspace/kb/artifact |
| Hooks System | ⬅️ 已迁移 | OpenHarness hooks |
| Permissions | ⬅️ 已迁移 | OpenHarness permissions |
| MCP Client | ⬅️ 已迁移 | OpenHarness mcp |
| Gateway | ✅ 已改造 | 已去 ohmo 化，当前为本地 JSON-RPC 风格 Gateway service + stdio JSONL |
| Swarm | ⬅️ 已迁移 | OpenHarness multi-agent |
| Meeting MCP 外部服务 | ✅ 已验收 | `meeting-voice-assistant` 已提供会议转写、分析、纪要、agent guide |
| Meeting Gateway RPC | ✅ 已完成 | `meeting.capabilities`、`meeting.analyze_text`、`meeting.process_recording`、`meeting.process_audio_dir` |
| Meeting Turn Workflow | ✅ 已完成 | `turn.start(domain=meeting)` 和普通会议音频路径自动进入 Meeting MCP |
| Meeting Long Audio Fallback | ✅ 已完成 | Meeting MCP stdio 读取上限提高到 128MB；下游分析器触发 chunk/limit 限制时，自动重试只转写并使用压缩转写完成分析 |
| Artifact Gateway RPC | ✅ 已完成 | `artifact.register`、`artifact.list`、`artifact.get`、`artifact.read` |
| Trace Gateway RPC | ✅ Phase 2-A 完成 | `trace.list`、`trace.get`，turn/artifact/meeting workflow 可审计 |
| Approval Gateway RPC | ✅ Phase 2-B 完成 | `approval.request/list/get/approve/reject`，pending/approved/rejected 状态可追踪 |
| Policy Gateway RPC | ✅ Phase 2-C 完成 | `policy.evaluate`，写/发/发布类风险识别；`turn.start` 写入类预检生成 pending approval |
| Retry Gateway RPC | ✅ Phase 2-D 完成 | `turn.retry`，approval 通过后按 retry context 继续执行原动作 |
| Secret Hygiene | ✅ Phase 2-E 完成 | session events、trace、approval、retry、artifact read/register metadata 脱敏 |
| Persistence Hardening | ✅ Phase 2-F 完成 | 本地 JSON/JSONL 写入加锁，JSON snapshot 原子替换，并发写回归 |
| API App Lifecycle | ✅ Phase 3-A 完成 | GatewayService 放入 FastAPI app.state；route 通过 Depends 获取；`create_app(gateway_service=...)` 支持注入 |
| Meeting Artifact Registration | ✅ 已验收 | 真实音频会议分析后自动登记 transcript/analysis/result/minutes |
| Lead Orchestrator | ✅ MVP 已完成 | `workflow.list` 可查看 meeting/knowledge workflow，`turn.start` 统一先走 orchestrator |
| DomainWorkflow Registry | ✅ MVP 已完成 | 已注册 `meeting.workflow` 与 `knowledge.workflow` |
| 领域智能体编排 | 🔄 部分完成 | meeting/knowledge workflow MVP 已接入；多代理分派、LLM intent router、workflow DSL 仍待做，面试 workflow 暂缓 |

### 1.3 当前架构图 (现状)

```
┌─────────────────────────────────────────────────────────────┐
│  用户层                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐   │
│  │  CLI    │  │ Headless│  │  Web    │  │  API         │   │
│  │  REPL   │  │ run     │  │ skeleton│  │ skeleton     │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬───────┘   │
└───────┼────────────┼────────────┼────────────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│  Project Gateway / Protocol Boundary                       │
│  ┌──────────────────────────────────────────────────┐      │
│  │ initialize / health.ping / session.start          │      │
│  │ turn.start / meeting.* / session.close            │      │
│  │ GatewayEvent: turn.started/item.delta/completed   │      │
│  └──────────────────────────────────────────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Runtime Pool                                                │
│  ┌──────────────────────────────────────────────────┐       │
│  │ GatewayRuntimePool: session_id -> RuntimeSession   │       │
│  │ MeetingWorkflow: domain=meeting / audio path route │       │
│  │ OpenHarness RuntimeBundle 优先 + SimpleRuntime fallback │ │
│  └──────────────────────────────────────────────────┘       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Runtime Adapter (降级)                                      │
│  ┌──────────────────────────────────────────────────┐      │
│  │ SimpleRuntime (mock 模式)                         │      │
│  │ - 无 API Key 时降级运行                            │      │
│  │ - 支持 hello/workspace/kb/artifact 工具          │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 Phase 1-C 已完成能力

Phase 1-C 已完成 **Artifact Store 与会议产物登记** 的最小闭环，把外部 Meeting MCP 生成的 transcript、analysis、result、minutes 从“路径字符串”提升为 harnessOS 可查询、可读取的 artifact 对象。

开发重点：

- 已定义 artifact record：`artifact_id`、`session_id`、`turn_id`、`domain`、`kind`、`path`、`mime`、`size`、`created_at`、`metadata`。
- 已实现 artifact registry/store：支持登记外部文件、按 session/domain/kind 查询、读取文本或 JSON。
- 已新增 Gateway RPC：`artifact.register`、`artifact.list`、`artifact.get`、`artifact.read`。
- MeetingWorkflow 完成后已自动登记 `transcript`、`analysis`、`result`、`minutes`。
- `turn.completed.data.meeting.artifacts` 保留原始 path，同时新增 harnessOS `artifact_id`。
- 已继续使用 `/Users/Zhuanz/Desktop/workspace/音频资料` 下真实音频作为阶段验收输入。

验收条件：

- 真实音频会议分析后至少登记 4 个 artifact：已通过。
- `artifact.list(session_id)` 能列出本轮会议产物：已通过。
- `artifact.read(minutes_artifact_id)` 返回非空 markdown：已通过。
- `artifact.read(analysis_artifact_id)` 返回可解析 JSON：已通过。
- Phase1-B 的 `meeting.*`、`turn.start(domain=meeting)`、普通聊天/headless 自动会议分析全部不回归：已通过。
- 面试 workflow 仍暂缓，不纳入 Phase 1-C：已保持。

本轮真实音频验收：

- Gateway session：`sess_a08b1f628ce2`
- Meeting session：`meeting_c4dc4073`
- Minutes artifact：`art_c27fa88d8d93`
- Analysis artifact：`art_9c1eb1071d60`

### 1.5 Phase 1-D 已完成能力

Phase 1-D 已完成 **Lead Orchestrator 与 DomainWorkflow Registry** 的 MVP：

- 已抽象 `DomainWorkflow` 接口，统一 meeting/knowledge 等 workflow 的 `should_handle` 与 `run`。
- 已建立 workflow registry，避免在 `GatewayRuntimePool` 内硬编码 meeting 特例。
- 已将现有 MeetingWorkflow 注册到 orchestrator，真实音频和 artifact id 验收不回归。
- 已增加 Knowledge workflow MVP：支持显式 `domain=knowledge` 和知识关键词路由。
- 已新增 `workflow.list`。
- 面试 workflow 继续暂缓，仅保留防误路由。

本轮真实音频验收：

- Gateway session：`sess_2858157d522e`
- Meeting session：`meeting_882541b5`
- Minutes artifact：`art_3b24d8ee4fe2`
- Workflow：`meeting.workflow`

### 1.6 下一阶段 Phase 2 开发目标、重点与验收

下一阶段聚焦 **生产化治理**：

| 子阶段 | 开发目标 | 开发重点 | 验收条件 |
| --- | --- | --- | --- |
| Phase 2-A Trace/Audit MVP | 让每次 session/turn/workflow/artifact 有统一 trace 记录 | ✅ 已完成：trace_id 生成、事件持久化、`trace.get/list` Gateway RPC、artifact 关联 | 普通聊天、会议分析、artifact.read 都能查到 trace 链路 |
| Phase 2-B Approval Coordinator MVP | 建立人审请求与决策状态机 | ✅ 已完成：`approval.request/list/get/approve/reject`、pending/approved/rejected 状态、会话绑定 | 审批记录可查询，审批生命周期可追踪 |
| Phase 2-C Policy Rules MVP | 将写文件、发送、发布类操作接入默认审批 | ✅ 已完成：`PolicyEvaluator`、`policy.evaluate`、`turn.start` 预检审批 gate | 写文件类请求默认生成 approval request；只读请求不触发审批 |
| Phase 2-D Retry/Resume MVP | 让失败 turn/workflow 可恢复 | ✅ 已完成：`turn.retry`、policy-blocked context 保存、approval 通过后续跑、防重复 retry | 模拟失败后 retry 成功，会议/知识 workflow 不回归 |
| Phase 2-E Secret Hygiene | 防止密钥进入 prompt/log/artifact 明文 | ✅ 已完成：统一 secret masker、trace/event/approval/retry/artifact 持久化边界过滤 | 测试样例中的 `sk-*`、token、Authorization 不出现在 trace 与 artifact 明文 |

下一阶段不做：

- 不新增面试 workflow。
- 不做完整 Web 产品界面。
- 不做真正多租户鉴权，只保留 user/session 隔离字段和测试。
- 不做后台 Job Service 的完整实现；Job Service 放到 Phase 3，Phase 2 只预留 trace/approval 与 retry 所需字段。
- Trace 当前会保存事件详情和工具输出摘要；Phase 2-E 已做常见密钥脱敏，但完整 DLP 仍是后续增强项。
- Phase 2-D 已提供 policy-blocked turn 的批准后续跑；失败 workflow 的通用 retry 仍是后续增强项。

### 1.7 Phase 2-C 已完成能力

Phase 2-C 已完成 **Policy Rules MVP** 的最小闭环：

- 已新增 `apps/gateway/policies.py`，提供 `PolicyEvaluator` 与 `PolicyDecision`。
- 已新增 `policy.evaluate` RPC，可独立评估自然语言输入或具体工具名。
- `turn.start` 在 workflow/model 执行前做策略预检；写入、删除、发送、发布类请求默认生成 pending approval。
- 只读、检索、会议分析、会议纪要生成不触发审批。
- 策略触发的 approval 会关联 `trace_id/session_id/turn_id`，并写入 TraceStore。
- 自动化验收：Phase 2-C/2-B/2-A 组合测试为 10 passed；相关回归测试为 45 passed。
- 用户态验收：写入 `phase2c_policy_manual.txt` 的请求返回 `approval_id=appr_1532cf6d65fc`、`trace_id=trace_030c83793b25`，目标文件未创建。
- Draw.io 当前架构图与 current-vs-target-gap 已同步到 Phase 2-C。

### 1.8 Phase 2-D 已完成能力

Phase 2-D 已完成 **Retry/Resume MVP** 的最小闭环：

- 已新增 `apps/gateway/retries.py`，提供 `RetryStore` 和 retry context 持久化。
- Policy gate 触发 approval 时会同步保存原始 `input/domain/session_id/source_turn_id/trace_id/approval_id/policy`。
- 已新增 `turn.retry` RPC，支持通过 `approval_id` 或原 `turn_id` 查找 retry context。
- `turn.retry` 要求对应 approval 状态为 `approved`；pending/rejected 状态不能续跑。
- retry 执行时会跳过本次 policy gate，并在新 `turn.started` 中标记 `retry_of_turn_id` 和 `approval_id`。
- 同一个 retry context 只能消费一次，重复 retry 会返回错误，避免重复写入/重复发布。
- 自动化验收：Phase 2-D/2-C/2-B/2-A 组合测试为 12 passed；相关回归测试为 47 passed。
- Draw.io 当前架构图与 current-vs-target-gap 已同步到 Phase 2-D。

### 1.9 Phase 2-E 已完成能力

Phase 2-E 已完成 **Secret Hygiene MVP** 的最小闭环：

- 已新增 `apps/gateway/secrets.py`，提供 `mask_text` 与 `mask_value`。
- `GatewaySessionStore.append_event` 写入 `events.jsonl` 前会脱敏 event data。
- `TraceStore` 写入 trace metadata 和 input summary 前会脱敏。
- `ApprovalStore` 写入 request summary、metadata、decision reason 前会脱敏。
- `RetryStore` 写入 retry context input 和 policy metadata 前会脱敏。
- `ArtifactRegistry` 写入 metadata 和 `artifact.read` 返回内容前会脱敏。
- 自动化验收：Phase 2-E/2-D/2-C/2-B/2-A 组合测试为 15 passed；相关回归测试为 50 passed。
- Draw.io 当前架构图与 current-vs-target-gap 已同步到 Phase 2-E。

### 1.10 Phase 2-F 已完成能力

Phase 2-F 已完成 **Architecture Hardening MVP** 的最小闭环：

- 已新增 `apps/gateway/persistence.py`，提供 `file_lock`、`atomic_write_text`、`append_text_locked`、`read_json_locked`、`update_json_list_locked`。
- `ApprovalStore` 的 request/decision 已切换为加锁的 JSON list 读改写。
- `RetryStore` 的 context 创建/mark_retried 已切换为加锁的 JSON list 读改写。
- `ArtifactRegistry` 的 register 已切换为加锁的 JSON list 读改写。
- `TraceStore` 的 JSONL append/read 已加锁。
- `GatewaySessionStore` snapshot 写入已原子替换，event append 已加锁。
- 自动化验收：persistence/secret/retry/policy/approval/trace 组合测试为 19 passed；相关回归测试为 54 passed。

### 1.11 Phase 3-A 已完成能力

Phase 3-A 已完成 **App Lifecycle MVP** 的最小闭环：

- 已新增 `apps/api/dependencies.py`，统一提供 `get_gateway_service(request)`。
- `apps/api/__init__.py` 的 lifespan 会初始化 `app.state.gateway_service`，并支持 `create_app(gateway_service=...)` 注入。
- `apps/api/routers/runs.py` 已移除模块级 `_gateway`，`/v1/runs`、`/v1/runs/stream`、session 查询、transcript 和 `/v1/rpc` 都通过 FastAPI `Depends` 获取同一个 app-scoped `GatewayService`。
- 自动化验收：`tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_gateway_protocol.py` 为 15 passed。
- 相关回归验收：API、persistence、secret、retry、policy、approval、trace、Gateway protocol、stdio、meeting workflow、CLI headless、Lead Orchestrator 组合测试为 57 passed。

### 1.12 当前架构缺陷与风险

1. Gateway service 仍是单进程内存 runtime pool。本地 JSON 文件写入已在 Phase 2-F 加锁并原子替换，但它仍不是跨机器/多 worker 的生产级数据库。
2. Policy gate 目前在 `turn.start` 前置预检，尚未包住 OpenHarness ToolRegistry 的每一次工具执行。若未来模型通过底层工具直接执行未知写入工具，仍需要工具执行层 policy middleware。
3. `turn.retry` 主要覆盖 policy-blocked turn 的续跑，不是通用 workflow failure retry。会议 workflow 的长任务失败恢复、artifact 幂等登记和局部重跑仍需后续设计。
4. Secret Hygiene 是正则级 MVP，只覆盖常见密钥形态；不能替代完整 DLP，也不会改写外部原始 artifact 文件。
5. API 层模块级 `_gateway` 单例已在 Phase 3-A 移除；但多 worker 下每个 worker 仍会有独立 app-scoped `GatewayService`，要生产化仍需要外置 session/runtime registry 或限制单 worker。
6. 会议 workflow 与相邻项目 `meeting-voice-assistant` 的路径和本地服务耦合较强，缺少 connector 配置中心、健康检查和版本协商。
7. 当前 workflow routing 主要靠显式 domain 和关键词，缺少可解释的 LLM intent router/DSL，复杂多领域任务可能误路由或只能走 generic chat。
8. 仓库仍保留 OpenHarness 迁移代码、SimpleRuntime、Deep Agents/OpenHarness RuntimeBundle 多套路径，边界虽然可运行，但长期会增加命名空间、事件模型和权限体系不一致风险。
9. Pack System MVP 已完成 manifest 加载和协议查询；但业务执行仍由 `apps/gateway` 的 workflow 类注册，pack 尚未拥有完整 workflow/skill/connector/policy 装配权。
10. 当前协议只有 session/turn 的雏形，缺少 Thread/Item 作为 Web、多项目任务管理和产物流转的稳定语义骨架。

### 1.13 当前剩余缺口

- `turn.interrupt` 已接 active task cancellation，并持久化 `turn.interrupted`。
- Headless CLI 已有 text/json/demo fallback 自动化回归。
- 真实模型 smoke 已有显式环境变量门控，默认跳过。
- `/v1/rpc` 与 stdio JSONL 已有同构协议回归测试。
- 会议领域 MCP server 已在外部项目完成 Phase1 验收，具备 `meeting_process_file`、`meeting_build_minutes`、`meeting://agent-guide`。
- harnessOS 已提供 `meeting.*` RPC 并通过真实音频验收，显式 RPC session 为 `meeting_895b5d29`。
- harnessOS 已提供 `turn.start(domain=meeting)` 和普通聊天/headless 音频路径自动路由，用户态验收 session 为 `meeting_8e8d3499`。
- approval/trace/policy/retry/job 已成为 first-class Gateway 方法；Tool Policy Middleware 已能在 builtin tools 和 Core engine tool loop 执行前阻断高风险工具。
- 业务编排已接入 Lead Orchestrator、DomainWorkflow Registry 与 Pack Registry；SubAgent Registry、LLM intent router 和 workflow DSL 尚未接入。
- Meeting artifacts 当前已进入 harnessOS Artifact Registry，但仍缺权限、审计和 lineage 治理。
- interview workflow 本阶段暂缓，不作为 Phase 1 验收阻塞项。

### 1.14 V2.0 Phase 3 后续开发目标

Core v1.5-A~E 已作为 V2.0 的当前落地点完成。后续不再以 Core v1.5 作为最终目标，而是从 Phase 3-B 开始继续向 V2.0 迁移：

| 模块 | 目标 | 第一阶段验收 |
| --- | --- | --- |
| Phase 3-B Core-native Session/Event Store | 旧 Gateway snapshot/events 降级为兼容层，Core Store 成为 session/event 主路径 | 普通 `你好` 与会议真实音频均写入 Core records；session.events/transcript 可从 Core records 重建 |
| Phase 3-C Background Job Worker | 同步 Job MVP 升级为 queued/running/completed/failed/cancelled 长任务服务 | 真实会议音频创建可查询 job，完成后关联四类 artifact，失败记录 failure_context |
| Phase 3-D Adapter-level Governance Injection | Runtime Adapter 默认注入 policy/approval/trace/tool metadata | OpenHarness/Simple 默认路径的高风险 tool 未审批不得执行，会议真实音频不误拦截 |
| Phase 3-E Pack Assembly MVP | pack manifest 驱动 workflow/connector/skill/policy bundle 注册 | meeting/knowledge 由 pack assembly 注册并可真实运行；stub pack 返回装配状态 |
| Phase 3-F Connector Registry MVP | Meeting MCP 从硬编码路径升级为 connector 管理对象 | `connector.list/get/health` 可发现 Meeting MCP，会议真实音频通过 connector registry 运行 |

Core v1.5-A 的完成定义：Core 对象模型、SQLite Store、CoreAppService 写入门面、Gateway 到 Core 的 session/turn/item/artifact/trace/approval/retry 写入链路和最小查询 RPC 全部可用；旧 Gateway stores 可保留为运行时兼容层，但不再作为 Core 写入抽象暴露给 Gateway runtime/service。

Core v1.5-A 已完成的代码基础：

- `core/protocol/models.py`：新增 Core protocol record 模型和 `new_core_id`，并补齐 `TraceRecord`、`RetryRecord`。
- `core/stores/sqlite.py`：新增 `CoreSQLiteStore`，创建 `.harnessos/core.sqlite3` 兼容 schema。
- `core/stores/runtime_recorder.py`：保留为 legacy/历史兼容记录器，不再被 Gateway runtime/service 作为 Core 写入依赖。
- `core/services/app_service.py`：新增 `CoreAppService`，统一封装 Core Store 查询、Core-native session/turn/item/artifact/trace/approval/retry mutation。
- `apps/gateway/runtime.py`：`session.start/session.close` 通过 `CoreAppService.record_runtime_session` 走 Core-native session mutation；GatewayEvent 的 thread/turn/item 生命周期通过 `CoreAppService.record_gateway_event` 原生写入 Core；meeting artifact records、policy approval/retry context 通过 `CoreAppService` 原生转换为 Core records。
- `apps/gateway/service.py`：Core 查询 RPC 已改为通过 `CoreAppService` 读取：`session.get`、`thread.list`、`turn.get`、`turn.items`、`core.artifact.list`、`core.trace.list`、`core.approval.list`、`core.retry.list`；不再持有 `core_recorder`。
- 支持 session/thread/turn/item/job/artifact/trace/approval/retry 的保存、读取、列表过滤。
- 支持 legacy Gateway session snapshot/events 导入，不删除旧 JSON/JSONL。
- 自动化验收：`tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py` 为 17 passed；阶段相关完整回归为 66 passed。
- 用户态验收：`python3 -m cli.main run --json '请分析 /Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3，生成会议纪要'` 已成功生成会议纪要，并将 analysis/minutes/result/transcript 四个产物写入 Core artifacts。

Core v1.5-A 已完成，后续工作转入 Core v1.5-B/1.5-C：

- Core v1.5-B：已实现 Domain Pack Registry，迁移 meeting/knowledge，并新增 investment/interview/video_studio manifest stub。
- Core v1.5-C：已实现 Job Service MVP，让真实会议音频分析进入可查询 job 模型。
- Core v1.5-D：已实现 Tool Policy Middleware MVP，把审批从 turn preflight 下沉到 builtin tools 和 Core engine tool loop。
- Core v1.5-E：已完成 Runtime Adapter 收敛 MVP，后续把旧 Gateway stores 降级为 adapter 或被 Core-native service 替换。

V2.0 Phase 3 后续执行约束：

- 每个阶段完成后必须同步更新 `CURRENT-STATUS.md`、`current-vs-target-gap.md`、`current-vs-target-gap.drawio`、`development_plan_v2.md`、`test-acceptance-plan.md` 和 `acceptance-test-cases.md`。
- 每个阶段必须执行定向自动化测试、阶段相关完整回归、drawio XML 校验和真实会议音频端到端验收。
- 真实音频验收后必须清理外部会议产物和本地 `.harnessos` 验收记录。

---

## 二、目标架构 (Phase 1-5)

### 2.1 目标架构 - 五层结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│  L1 用户入口层                                                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │  CLI    │  │  Web App│  │ IM Bot  │  │  REST   │                 │
│  │ (dev)  │  │(product)│  │(future) │  │  API    │                 │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                 │
└───────┼────────────┼────────────┼────────────┼─────────────────────┘
        │            │            │            │
        └────────────┴─────┬──────┴────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  L2 API Gateway / BFF                                              │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │JSON-RPC   │ │  Auth    │ │ Tenant   │ │ Rate     │              │
│  │Server     │ │ Middleware│ │ Middleware│ │ Limiter  │              │
│  └─────┬──────┘ └──────────┘ └──────────┘ └──────────┘              │
│        │                                                              │
│  ┌─────┴──────────────────────────────────────────────────┐          │
│  │  Method Router: session.* / turn.* / artifact.* / approval.*     │
│  └──────────────────────────────────────────────────────────┘          │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  L3 Orchestrator                                                       │
│  ┌──────────────┐ ┌─────────────────┐ ┌───────────────┐                 │
│  │IntentRouter │ │ Workflow        │ │ SubAgent     │                 │
│  │(LLM-based) │ │ Dispatcher      │ │ Registry     │                 │
│  └──────────────┘ └─────────────────┘ └───────────────┘                 │
│                                                                      │
│  ┌──────────────┐ ┌─────────────────┐ ┌───────────────┐                 │
│  │Session      │ │ Policy         │ │ Job         │                 │
│  │Manager      │ │ Evaluator      │ │ Service     │                 │
│  └──────────────┘ └─────────────────┘ └───────────────┘                 │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  L4 Core Agent (Deep Agents 内核)                                      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐             │
│  │ AgentRuntime (create_deep_agent)                    │             │
│  └────────────────────────┬───────────────────────────┘             │
│                           │                                          │
│  ┌────────────────────────▼───────────────────────────┐             │
│  │ Middleware Stack                                        │             │
│  │ - TodoListMiddleware    - SkillsMiddleware            │             │
│  │ - FilesystemMiddleware  - SubAgentMiddleware         │             │
│  │ - MemoryMiddleware      - HumanInTheLoopMiddleware   │             │
│  │ - PermissionMiddleware (OpenHarness)               │             │
│  └────────────────────────┬───────────────────────────┘             │
│                           │                                          │
│  ┌────────────────────────▼───────────────────────────┐             │
│  │ Tool Registry                                        │             │
│  │ - Built-in: workspace_*, kb_*, artifact_*           │             │
│  │ - OpenHarness: bash, file_*, grep, glob            │             │
│  │ - Custom/MCP: meeting_* first, interview_* later    │             │
│  └──────────────────────────────────────────────────────┘             │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  L5 Execution Plane (DeerFlow 参考)                                    │
│                                                                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │Workspace   │ │ Artifact   │ │Knowledge   │ │ Sandbox    │          │
│  │Manager    │ │Store      │ │Graph       │ │(Docker/K8s)│          │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘          │
│                                                                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                       │
│  │ JobService │ │ MCP        │ │ Hook      │                       │
│  │(background)│ │Connectors  │ │Executor   │                       │
│  └────────────┘ └────────────┘ └────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 三框架集成关系

| 框架 | 角色 | 在架构中的位置 | 迁移状态 |
|------|------|----------------|----------|
| **Deep Agents** | 主内核 | L4 Core Agent | ⬅️ 参考代码 |
| **OpenHarness** | 控制面参考 | L4 Hooks/Permissions, L3 Commands | ✅ 已迁移 |
| **DeerFlow** | 执行面参考 | L5 Workspace/Artifact/Sandbox | ⬅️ 参考代码 |
| **Meeting MCP** | 外部领域能力 | L5 MCP Connectors / L3 meeting workflow | ✅ 外部服务已验收，harnessOS 接入待做 |

### 2.3 核心数据流

```
用户输入
    │
    ▼
┌─────────────────┐
│  L1: CLI/Web    │  用户交互入口
└────────┬────────┘
         │ stdio JSONL / WebSocket / HTTP+SSE
         ▼
┌─────────────────┐
│  L2: API Gateway │  认证 + 限流 + 路由
└────────┬────────┘
         │ JSON-RPC 调用
         ▼
┌─────────────────┐
│  L3: Orchestrator│ Intent路由 + Workflow编排
└────────┬────────┘
         │ turn.start / turn.continue
         ▼
┌─────────────────────────────┐
│  L4: Core Agent             │
│  (Deep Agents 内核)         │
│  ┌─────────────────────┐   │
│  │ Middleware Stack   │   │
│  └──────────┬─────────┘   │
│             │              │
│  ┌──────────▼─────────┐   │
│  │ Tool Registry      │   │
│  └──────────┬─────────┘   │
└──────────────┼────────────┘
               │ Tool Calls
               ▼
┌─────────────────────────────┐
│  L5: Execution Plane       │
│  ┌────────┐ ┌────────┐    │
│  │Workspace│ │Artifact │    │
│  └────────┘ └────────┘    │
│  ┌────────┐ ┌────────┐    │
│  │Knowledge│ │Sandbox │    │
│  └────────┘ └────────┘    │
└─────────────────────────────┘
```

---

## 三、模块详细设计

### 3.1 CLI 模块 (已实现)

```python
cli/
├── main.py           # python -m cli.main
├── session.py        # 会话管理，调用 SimpleRuntime
└── renderer.py       # 输出渲染
```

### 3.2 API 模块 (骨架)

```python
apps/api/
├── __init__.py       # FastAPI 应用
└── routers/
    ├── agents.py     # /v1/agents 端点
    ├── routing.py     # /v1/intent 端点
    └── health.py      # /health 端点
```

### 3.3 Orchestration 模块 (占位→完整)

```python
core/orchestration/
├── intent_router.py       # 关键词路由 → LLM 路由 (Phase 2)
├── workflow_dispatcher.py # 工作流编排器 (Phase 1)
└── session_manager.py     # 会话管理 (Phase 2)
```

### 3.4 Runtime Adapter 模块 (降级→完整)

```python
core/runtime_adapter/
├── __init__.py           # 自动降级逻辑
├── simple_runtime.py     # Mock 运行时 (当前)
└── deep_agents_runtime.py # Deep Agents 封装 (Phase 1)
```

### 3.5 Tools 模块 (基础→完整)

```python
tools/
├── base.py               # BaseTool 基类
├── workspace.py          # workspace_ls/read/write/mkdir
├── knowledge.py          # kb_search/ingest/list/get/delete
├── artifact.py          # artifact_save/list/get/delete
└── openharness_*.py    # OpenHarness 工具迁移
```

### 3.6 Agents 模块 (占位→完整)

```python
agents/
├── lead_orchestrator/   # 主控代理 (Phase 1)
├── meeting_analyst/       # 会议分析 (Phase 1)
├── interview_coach/        # 面试辅导 (Phase 1)
├── kb_curator/            # 知识库 (Phase 1)
└── swarm/                 # 多代理协作 (OpenHarness)
```

### 3.7 Execution 模块 (完整)

```python
execution/
├── workspace/            # Per-session workspace
├── artifacts/           # Artifact 存储
├── knowledge/            # Knowledge Graph
├── sandbox/              # Docker/K8s 沙箱
├── jobs/                 # 后台任务队列
└── mcp/                 # MCP 客户端
```

---

## 四、开发路线图

### Phase 0: 骨架 (✅ 完成)
- [x] CLI 交互入口
- [x] Core Schemas
- [x] API Gateway 骨架
- [x] 基础 Tools
- [x] OpenHarness 代码迁移

### Phase 1: Core MVP (✅ 会议优先路径完成)
- [x] Lead Orchestrator MVP
- [x] Meeting workflow 接入
- [x] Knowledge workflow MVP
- [x] Meeting MCP 真实音频 E2E 验收
- [x] Meeting artifacts 登记
- [ ] Interview workflow 暂缓
- [ ] Deep Agents 生产级边界收敛

### Phase 2: 生产化 (✅ MVP 完成)
- [x] Phase 2-A Trace/Audit MVP
- [x] Phase 2-B Approval Coordinator MVP
- [x] Phase 2-C Policy Rules MVP
- [x] Phase 2-D Retry/Resume MVP
- [x] Phase 2-E Secret Hygiene
- [x] Phase 2-F Persistence Hardening
- [ ] 多用户/session 隔离字段与测试：移入 V2.0 后续安全模型

### Phase 3: V2.0 Core Platform Hardening
- [x] Phase 3-A App Lifecycle + GatewayService DI
- [ ] Phase 3-B Core-native Session/Event Store
- [ ] Phase 3-C Background Job Worker
- [ ] Phase 3-D Adapter-level Governance Injection
- [ ] Phase 3-E Pack Assembly MVP
- [ ] Phase 3-F Connector Registry MVP

### Phase 4: Domain Pack Expansion
- [ ] Video Studio Pack MVP：brief -> script -> storyboard -> shot list
- [ ] Artifact lineage：script -> storyboard -> assets -> render output
- [ ] Specialist crew：Studio Lead / Director / Script / Storyboard / Editing / QA
- [ ] 发布或最终 render 前 approval gate

### Phase 5: 开源/商用
- [ ] API 版本化
- [ ] 扩展开发指南
- [ ] 发布流水线

---

## 五、关键文件索引

### 已实现
| 文件 | 作用 |
|------|------|
| `cli/main.py` | CLI 入口 |
| `cli/session.py` | 会话管理 |
| `cli/renderer.py` | 输出渲染 |
| `core/schemas/__init__.py` | 12 个核心类型 |
| `core/orchestration/intent_router.py` | 意图路由 |
| `core/runtime_adapter/simple_runtime.py` | 降级运行时 |
| `tools/*.py` | 工具实现 |

### 已迁移 (OpenHarness)
| 文件 | 作用 |
|------|------|
| `core/middleware/hooks/*` | Hook 系统 |
| `core/policies/permissions/*` | 权限检查 |
| `devplane/commands/*` | 命令注册 |
| `execution/mcp/*` | MCP 客户端 |
| `agents/swarm/*` | 多代理系统 |
| `apps/gateway/*` | 网关服务 |

### 待实现
| 文件 | 作用 | Phase |
|------|------|-------|
| `agents/lead_orchestrator/*` | 主控代理 | 1 |
| `agents/meeting_analyst/*` | 会议分析 | 1 |
| `agents/interview_coach/*` | 面试辅导 | 1 |
| `agents/kb_curator/*` | 知识库 | 1 |
| `core/runtime_adapter/deep_agents_runtime.py` | Deep Agents 封装 | 1 |
| `execution/artifacts/*` | 工件存储 | 1 |
