# Tasks - harnessOS

## Phase 0: 底座与骨架 (Foundation & Skeleton)

**目标**: 把"能跑起来的空壳"搭好

### 验收条件
- [ ] 仓库结构落地：`apps/core/agents/tools/skills/execution/devplane` 目录就位
- [ ] 运行链路：`POST /v1/runs` 完成从用户输入到流式返回的最小闭环
- [ ] 文件链路：`POST /v1/uploads` 上传文件后能在 `GET /v1/artifacts/{id}` 取回
- [ ] Agent 内核：`lead_orchestrator` 能调用 1 个 dummy tool 并输出结构化结果
- [ ] 状态管理：`session_id`/`run_id`/`artifact_id`/`tool_call_id` 全部贯通
- [ ] 观测：每次 run 有 `trace_id`、日志、错误码
- [ ] CI：lint、unit test、smoke test 全绿
- [ ] 文档：`README + 本地启动手册 + .env.example` 完成

### 任务清单
- [ ] 完善 `core/schemas/` - 实现所有 12 个核心类型
- [ ] 完善 `apps/api/` - 实现 `/v1/runs` 端点
- [ ] 实现 `lead_orchestrator` 基础版（调用 dummy tool）
- [ ] 实现 `workspace_ls` / `workspace_read_file` / `artifact_save` 工具
- [ ] 搭建 CI pipeline（lint + unit + smoke）

---

## Phase 1: 核心 MVP (Core MVP)

**目标**: 把"会议 + 面试 + 知识库"三条主链路跑通

### 验收条件
- [ ] 会议链路：上传会议材料或转写文本后，能输出摘要、action items、待跟进项，并生成邮件草稿
- [ ] 面试链路：输入 JD + 候选人背景后，能生成模拟面试、追问、评分、改进建议
- [ ] 知识库链路：对已入库文档提问时，回答必须带引用来源和片段定位
- [ ] E2E 场景：至少 3 个端到端场景全自动回归通过
- [ ] 质量门槛：20 个人工评测样例里，核心任务完成率 ≥ 80%
- [ ] 工件链路：摘要、评分报告、邮件草稿都能作为 artifact 落库和回看
- [ ] 失败恢复：tool 调用失败能重试；run 失败能看到明确失败位置
- [ ] 文档：用户使用文档、开发者本地调试文档完成

### 任务清单
- [ ] 实现 `meeting_analyst` agent
- [ ] 实现 `interview_coach` agent
- [ ] 实现 `kb_curator` agent
- [ ] 实现 `kb_ingest` / `kb_search` / `transcript_parse` / `score_answer` / `draft_email` 工具
- [ ] 编写 10 个 skill manifests
- [ ] 实现会议纪要模板 `meeting_minutes_v1`
- [ ] 实现面试评分模板 `interview_scorecard_v1`
- [ ] 实现知识综述模板 `knowledge_brief_v1`

---

## Phase 0.5-0.6: 协议优先控制面 (Protocol-First Control Plane)

**目标**: 把 CLI 直连 runtime 的原型升级为项目自有 Gateway 协议边界，为后续 Web/API/业务工作流共用同一语义打底

### 验收条件
- [x] Headless CLI：终端可直接运行 `python3 -m harnessOS.cli.main run "你好"` 并获得模型回复
- [x] 项目自有协议模型：具备 `RpcRequest` / `RpcResponse` / `RpcError` / `GatewayEvent` / `TurnResult`
- [x] Gateway session 生命周期：支持 `initialize` / `session.start` / `turn.start` / `session.close` / `health.ping`
- [x] Gateway resume/interrupt：支持 `session.resume` / `session.events` / `turn.continue` / `turn.interrupt`
- [x] 事件归一化：turn 事件输出为项目自有 `turn.started` / `item.delta` / `turn.completed` / `turn.failed`
- [x] HTTP 入口：FastAPI 暴露 `/v1/runs`、`/v1/runs/stream`、`/v1/sessions/{session_id}/events`
- [x] Phase 0.6 RPC/session 查询：支持 `/v1/rpc`、`session.list`、`session.read`、`session.transcript`
- [x] Phase 0.6 stdio JSONL：支持 `python3 -m apps.gateway.stdio_server`
- [x] Phase 0.6 Runtime 后端：`GatewayRuntimePool` 支持 OpenHarness `RuntimeBundle` 优先与 SimpleRuntime fallback
- [x] Phase 0.6 错误码：统一 `SESSION_NOT_FOUND`、`METHOD_NOT_FOUND`、`INVALID_PARAMS`、`RUNTIME_ERROR` 等协议错误码
- [x] 旧 gateway 去 ohmo 化：`apps/gateway` 不再依赖 `ohmo.*` / channel bus
- [x] 测试覆盖：gateway 协议 happy path、unknown session、事件归一化

### 已完成
- [x] 新增 `apps/gateway/protocol.py`
- [x] 重写 `apps/gateway/runtime.py` 为 `GatewayRuntimePool`
- [x] 重写 `apps/gateway/service.py` 为本地 JSON-RPC 风格 `GatewayService`
- [x] 新增 `harness run` console script 配置
- [x] 新增 `tests/test_gateway_protocol.py`
- [x] 修复 artifact 工具 import 时写入父目录的问题
- [x] 过滤 MiniMax/OpenAI-compatible 非流式响应里的 `<think>...</think>`
- [x] 新增 `apps/gateway/storage.py`，保存 session snapshot 与 events.jsonl
- [x] 新增 `apps/api/routers/runs.py`，接入 Gateway service
- [x] 新增 `tests/test_api_runs.py`
- [x] 修复 FastAPI app 初始化与 `.env` 额外变量兼容问题

### 下一步
- [x] 将 `GatewayRuntimePool` 从 SimpleRuntime agent 池升级为 OpenHarness `RuntimeBundle` 优先、SimpleRuntime fallback
- [x] 将 `turn.continue` 接入 OpenHarness `continue_pending` 能力；SimpleRuntime 返回明确 no-pending 状态
- [x] 增加 transcript replay 与 session.list/session.read
- [x] 转入 Phase 0.7：真实运行中取消、headless CLI 回归测试、真实模型 smoke test 标记

---

## Phase 0.7: 控制面收口与进入业务编排前置 (Control Plane Closure)

**目标**: 在进入 meeting/interview/knowledge 业务链路前，把 Gateway 的取消、回归测试和真实模型验证边界收稳

### 验收条件
- [x] 真实取消：`turn.interrupt` 能取消正在执行的 RuntimeBundle turn，或在当前 OpenHarness 不支持 cancel 时由 Gateway task wrapper 取消 stream task
- [x] 中断事件：取消后 event log 中出现 `turn.interrupted`，session snapshot 状态为 `interrupted`
- [x] Headless CLI 回归：`python3 -m cli.main run "你好"`、`--json`、错误 API key fallback 均有自动化覆盖
- [x] 真实模型 smoke 标记：提供可跳过的 `@pytest.mark.smoke_model` 或等价环境变量门控测试，不在默认 CI 中强制联网
- [x] RPC 兼容：`/v1/rpc` 与 stdio JSONL 对 `initialize`、`session.start`、`turn.start`、`session.transcript` 行为一致
- [x] 文档同步：本地启动、端口冲突、HTTP/RPC/stdio 验收步骤保持一致

### 任务清单
- [x] 为 Gateway turn stream 增加 task handle/active turn registry
- [x] 将 `turn.interrupt` 接入 active task cancellation，并将取消转成 `turn.interrupted` 事件
- [x] 新增 `tests/test_cli_headless.py`，覆盖 text/json/demo fallback
- [x] 新增真实模型 smoke 测试文件，默认 skip，只有显式环境变量开启
- [x] 补充 `/v1/rpc` 与 stdio JSONL 的同构协议测试
- [x] 更新 README 或本地启动手册中的端口冲突与 8010 验收建议

---

## Phase 2: 生产化与治理 (Production & Governance)

**目标**: 从"能用"走到"可控"

### 验收条件
- [ ] 权限：所有写入、发送、发布类 tool 默认需要 approval
- [ ] 审计：每个 tool_call 都有输入摘要、调用人、时间、结果状态、artifact 引用
- [ ] 隔离：不同用户/不同 session 的数据与 artifact 不串线
- [ ] 恢复：session resume、run retry、run cancel 全可用
- [ ] 安全：secrets 不进入 prompt、不落日志、不进入 artifact 明文
- [ ] 观测：trace、metrics、error dashboard 可用
- [ ] 测试：30+ 条 E2E 回归场景全绿
- [ ] 文档：运维手册、权限策略说明、审计字段说明完成

### 任务清单
- [ ] 实现 `approval_request` + `PolicyService`
- [ ] 实现审计日志（tool_call 完整记录）
- [ ] 实现多租户数据隔离
- [ ] 实现 session resume / run retry / run cancel
- [ ] 实现 `scheduler_assistant` agent
- [ ] 实现 `memory_writer` agent
- [ ] 搭建 `devplane/` - CLI / TUI / commands / hooks
- [ ] 搭建 observability dashboard

---

## Phase 5-C: Connector Execution Runtime - FunASR / Data Service MCP 增量

**目标**: 将 FunASR 从纯 HTTP 微服务补齐为 MCP stdio connector，使后续 ASR 调用可以通过 harnessOS connector 边界执行。

### 验收条件
- [x] `meeting-voice-assistant/backend/funasr_service` 新增 `funasr_service.mcp_stdio`
- [x] MCP tools 暴露 `funasr_health` 与 `funasr_recognize_file`
- [x] MCP resource 暴露 `funasr://capabilities`
- [x] `funasr_recognize_file` 通过 HTTP proxy 调用现有 FunASR `/recognize`
- [x] harnessOS Connector Registry 注册 `funasr_mcp`
- [x] 默认测试不依赖真实 FunASR 模型或 8001 服务
- [x] ConnectorExecutionRuntime 接入 gated MCP stdio client，默认仍保持 connector stub
- [x] data_service_mcp 通过持久 MCP stdio session 完成真实 Knowledge lifecycle E2E
- [ ] Phase 5-D 后续增量：FunASR MCP 真实 stdio 调用接入 Meeting workflow

## Phase 5-D: Cross-domain MCP Workflow Stabilization

**目标**: 用 MCP connector 串起 Meeting 与 Knowledge 双域工作流

### 验收条件
- [ ] Knowledge MCP smoke 固化：依赖检查 + `create -> import -> build -> query -> feedback -> review -> plan -> archive`
- [ ] FunASR MCP 真实调用：`funasr_health -> funasr_recognize_file`
- [ ] Meeting workflow 支持通过 `funasr_mcp` 执行转写
- [ ] Meeting -> Knowledge E2E：`audio -> transcript -> minutes -> knowledge import/build/query`
- [ ] 全链路 artifact lineage 可追踪 audio、transcript、minutes、knowledge source、build operation、query result
- [ ] 默认测试不依赖真实 FunASR 模型或 data_service server

### 任务清单
- [ ] 固化 `scripts/e2e_data_service_mcp_validation.py` 为显式集成验收脚本
- [ ] 新增 FunASR MCP 显式集成验收脚本
- [ ] Meeting Pack 转写路径接入 `funasr_mcp`
- [ ] 新增 cross-domain workflow runner
- [ ] 更新验收文档和故障排查说明

---

## Phase 3: 多代理与自动化 (Multi-Agent & Automation)

**目标**: 从单体助手变成可分工的 agent 系统

### 验收条件
- [ ] 子代理：`meeting-analyst / interview-coach / kb-curator / scheduler-assistant` 已接入主编排
- [ ] 分工：主编排能根据任务类型自动路由到合适 subagent
- [ ] 长任务：背景任务、轮询、取消、继续运行可用
- [ ] 长上下文：长会话自动总结，不因上下文爆炸而失败
- [ ] 并发：10 个并发 session 下，核心功能不崩
- [ ] 质量门槛：50 个分解型任务样例，完成率 ≥ 85%
- [ ] 文档：agent registry、handoff 规则、background job 说明完成

### 任务清单
- [ ] 实现 subagent registry
- [ ] 实现 intent router 混合模式（Keyword/LLM）
- [ ] 实现 `JobService`（后台任务、重试、取消、轮询）
- [ ] 实现长会话自动 summarization
- [ ] 并发测试与优化
- [ ] 编写 agent handoff 规则文档

---

## Phase 4: 本地视频工作流接入 (Local Video Workflow)

**目标**: 把"AI 短剧量产"的执行面接进来

### 验收条件
- [ ] 编排：输入一个短剧 brief，能产出脚本、分镜、镜头清单
- [ ] 任务流：能启动本地视频工作流任务，并持续轮询状态
- [ ] 工件流：script → storyboard → assets → render output 的 artifact lineage 可追踪
- [ ] 重试：单个镜头或单个 render step 失败时支持局部重跑
- [ ] 批量：至少连续完成 3 个短剧任务的批处理
- [ ] 审批：发布前或最终 render 前有人工确认点
- [ ] 文档：本地视频适配器接入手册完成

### 任务清单
- [ ] 实现 `media_orchestrator` agent
- [ ] 实现 `launch_media_job` / `poll_media_job` / `cancel_media_job` / `collect_media_outputs` / `register_asset` 工具
- [ ] 实现 `short_drama_script_v1` 模板
- [ ] 实现 `storyboard-v1` / `render-recovery` skills
- [ ] 实现 artifact lineage 追踪
- [ ] 实现批处理模式
- [ ] 编写本地视频适配器接入手册

---

## Phase 5: 开源与商用就绪 (Open Source & Production Ready)

**目标**: 从"项目"变成"产品 + 平台"

### 验收条件
- [ ] API 稳定性：对外 API 版本化，核心 schema 冻结到 `v1alpha` 或 `v1beta`
- [ ] 可扩展性：tools、skills、plugins 至少各有 2 个第三方扩展示例
- [ ] 开发体验：新开发者可在 30 分钟内本地跑通 smoke test
- [ ] 法务准备：LICENSE、贡献协议、隐私与遥测说明齐全
- [ ] 发布流程：tag、changelog、release note、CI 发布流水线可用
- [ ] 文档：架构文档、扩展开发文档、部署文档完成
- [ ] 商用准备：多租户策略、审计策略、计费/限流接口预留完成

### 任务清单
- [ ] API 版本化 + schema 冻结
- [ ] 编写扩展开发指南 + 2+ 示例
- [ ] 编写 CONTRIBUTING.md + CLA
- [ ] 搭建 release pipeline
- [ ] 完成架构文档 + 部署文档

---

## 当前活动剩余开发计划（V3）

当前活动路线以以下文档为准：

- `docs/design/V3.0/v3_development_plan_multi_app_core.md`
- `docs/design/V3.0/v3_current_gap_analysis.md`
- `docs/design/V3.0/CURRENT-STATUS_v3.md`
- `docs/design/V3.0/test-acceptance-plan_v3.md`

已完成并进入基线的内容：

- [x] Meeting / Knowledge / Video workflow 已从 Gateway 迁入 Domain Pack。
- [x] Meeting MCP connector/service 已迁入 `packs/meeting/connector.py`。
- [x] Meeting artifact lineage 用户态验收脚本已作为当前回归基线。
- [x] Phase 4-B2 Remote ComfyUI scaffold 延期保留，不作为当前主验收线。
- [x] Phase 4-C Core-native RPC Router 已完成 method registry、capability registry、compat alias 和稳定错误码回归。
- [x] Phase 4-D Tool-level Approval Automation 已完成工具执行层自动 approval request、拒绝阻断 retry、批准后工具执行回归。
- [x] Phase 5-A Pack DSL / Skill / Policy Bundle Assembly 已完成 DomainPack 2.0 Assembly Kernel、Knowledge data_service_mcp Contract Stub、Pack-owned agents 查询面和 Typed DAG 回归。
- [x] Phase 5-B Memory & Session Intelligence 已完成 Core-native memory records、session summary、artifact-backed memory refs、memory RPC 和 turn memory context MVP。
- [x] Phase 5-C Connector Execution Runtime 已完成 connector submit/poll/cancel/collect、Core job/events/artifact、data_service_mcp gated stdio execution 和 Knowledge lifecycle 持久 MCP session MVP。
- [x] V2 历史 Phase 5-D 已完成当前集成 MVP 级别的 FunASR MCP 真实调用、Meeting workflow MCP 转写、Meeting -> Knowledge 跨域 runner 和一次真实 FunASR/data_service 验收。

当前剩余开发顺序：

- [x] V3.0-PhaseA：scope 默认过滤、迁移/回填、namespace isolation、默认主线和显式真实音频验收已完成，并已冻结为回归基线
- [ ] V3.0-PhaseB：已完成 PackAssemblyResult 正式合同、connector descriptor/security model、AppProfile pack_paths、registry-derived assembly 输入、app_profile_connector blocked 语义与 external pack target_version policy；剩余更细粒度 severity 分层和去硬编码退出门
- [x] V3.0-PhaseC：补齐 artifact read policy 冻结、job/artifact/runtime governance hardening
- [ ] V3.0-PhaseD：完成 Meeting Pack 真正以外部服务可复验的真实音频 E2E 与 legacy facade equivalence
- [ ] V3.0-PhaseE：完成 Knowledge Pack data_service_mcp E2E 与 data boundary 验收

---

## 当前进度

### 已完成
- [x] Phase 0 基础设施：仓库结构、API Gateway、后端框架
- [x] Phase 0 前端框架：apps/web/ 初始化
- [x] Phase 0 API 设计文档：docs/api/ 4 个文档
- [x] Phase 0.5 协议控制面：headless CLI + Gateway 协议模型 + session/turn 最小闭环
- [x] Phase 0.6 协议收口：RuntimeBundle 优先/fallback、session list/read/transcript、`/v1/rpc`、stdio JSONL
- [x] Phase 0.7 控制面收口：active turn cancellation、headless CLI 回归、真实模型 smoke 标记、RPC/stdio 同构
- [x] V2 Phase 4-B0/B1：Domain Pack workflow 迁移、Meeting connector 迁移、artifact lineage 查询与用户态验收基线
- [x] V2 Phase 4-C：Core-native RPC Router，`method.list`、registry capabilities、compat alias 和稳定错误码已完成
- [x] V2 Phase 4-D：Tool-level Approval Automation，工具执行层自动审批、reject 阻断 retry、approved approval id 放行工具执行已完成
- [x] V2 Phase 5-A：DomainPack 2.0 Assembly Kernel，Typed DAG、Pack-owned agents、data_service_mcp Contract Stub 和 blocked/degraded 语义已完成
- [x] V2 Phase 5-B：Memory & Session Intelligence，Core memory records、deterministic session summary、artifact refs 和 turn context 注入已完成
- [x] V2 Phase 5-C：Connector Execution Runtime，connector lifecycle、gated MCP stdio execution、Core job/events/artifact 和 Knowledge lifecycle 持久 MCP session 已完成当前 MVP
- [x] V2 Phase 5-D：Cross-domain MCP Workflow Stabilization，FunASR MCP stdio execution、Meeting workflow MCP 转写、Knowledge MCP stdio gate、Meeting -> Knowledge 跨域 runner 和真实跨域验收已完成当前集成 MVP

### 进行中
- [ ] V3.0-PhaseB 到 V3.0-PhaseE 当前主线：以 V3 active plan 收口 pack、governance、meeting、knowledge

### 待开始
- [ ] Phase 6：Productization / Open Source / Commercial Readiness

---

## 项目架构参考

### 架构图位置
- `docs/architecture/current-vs-target-gap_v2.drawio` - 当前与目标架构差距图
- `docs/architecture/diagrams/01_current_architecture_v2.drawio` - 当前架构图
- `docs/architecture/diagrams/02_target_architecture_v2.drawio` - 目标架构图
- `docs/history/architecture/reference-frameworks/deerflow-architecture.drawio` - DeerFlow 历史参考图
- `docs/history/architecture/reference-frameworks/deep-agents-architecture.drawio` - Deep Agents 历史参考图
- `docs/history/architecture/reference-frameworks/openharness-architecture.drawio` - OpenHarness 历史参考图

### API 设计文档
- `docs/api/unified-message-schema_v2.md` - 统一消息模式
- `docs/api/gateway-endpoints_v2.md` - API Gateway 端点
- `docs/api/orchestrator-interface_v2.md` - 编排器接口
- `docs/api/llm-provider-config_v2.md` - LLM 提供者配置

### 测试验收计划
- `docs/test-acceptance-plan_v2.md` - 完整测试验收计划

### 参考代码
- `examples/deer-flow/` - DeerFlow 代码
- `examples/deep-agents/` - Deep Agents 代码
- `examples/open-harness/` - OpenHarness 代码

---

## 备注
- 任务完成后标记为 `- [x]`，并更新 `COMPLETION_DATE`
- 预估耗时格式：`(预计 1 天)`、`(预计 2 小时)` 等
