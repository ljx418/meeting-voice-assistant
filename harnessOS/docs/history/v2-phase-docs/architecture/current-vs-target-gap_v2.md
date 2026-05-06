# harnessOS 当前架构与目标架构差异

配套 draw.io 图：`docs/architecture/current-vs-target-gap_v2.drawio`

## 1. 文档口径

本文档用于说明 harnessOS 当前事实基线、目标架构、差距、路线阶段和验收情况。为避免团队误读，本文采用三段式口径：

- **Fact Baseline**：只记录已真实落地、可验收、可回归的能力。
- **Target Architecture**：只记录目标形态和架构原则，不代表当前已完成。
- **Gap & Roadmap**：记录还差什么、先做什么、每阶段如何验收。

当前统一阶段命名：

- **产品/架构基线版本**：Baseline v1.5-E
- **当前主验收阶段**：Phase 4-B1 Meeting Artifact Lineage Acceptance 已完成
- **延期保留能力**：Phase 4-B2 Remote ComfyUI / Render Manifest Scaffold
- **当前开发阶段**：Phase 5-D Cross-domain MCP Workflow Stabilization 已完成当前集成 MVP；Phase 5-A DomainPack 2.0 Assembly Kernel / Knowledge-primary Connector Stub、Phase 5-B Memory & Session Intelligence 与 Phase 5-C Connector Execution Runtime 已完成当前 MVP

## 2. Fact Baseline

当前 harnessOS 已不再是单一会议助手，而是进入 **Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform** 的平台化收敛阶段。

当前已真实落地的能力如下：

| 能力域 | 状态 | 事实边界 |
| --- | --- | --- |
| CLI / Headless | 已完成 | 普通 CLI、`--oh` TUI、`python3 -m cli.main run` 可用。 |
| API / Gateway | 已完成 MVP | FastAPI `/v1/runs`、SSE、`/v1/rpc`、stdio JSONL 可用。 |
| Session / Turn 生命周期 | 已完成 MVP | `session.start`、`turn.start`、完成/失败/中断、session 查询和 transcript replay 可用。 |
| Meeting 场景 | 已完成 Phase 1 MVP | 可通过自然语言音频路径触发会议音频分析，生成 transcript、analysis、result、minutes。 |
| Artifact Registry | 已完成 MVP | 会议/视频规划产物可登记为 artifact，并通过 `artifact.list/get/read/register` 查询读取；当前用户态主验收是 Meeting `transcript -> analysis -> result -> minutes` lineage。Video Studio asset/render manifest 只作为延期 scaffold 回归。 |
| Lead Orchestrator | 已完成 MVP | `meeting.workflow`、`knowledge.workflow`、`video.workflow` 已通过 DomainWorkflow Registry 路由。 |
| Trace / Approval / Policy / Retry | 已完成 MVP | turn、workflow、artifact、approval、retry、job 等关键链路可追踪、审批和重试。 |
| Secret Hygiene | 已完成 MVP | 常见 API key、token、Authorization 在持久化边界脱敏。 |
| Persistence Hardening | 已完成 MVP | 本地 JSON/JSONL 写入加锁和原子替换，降低并发写风险。 |
| API Lifecycle | 已完成 | FastAPI route 使用 app-scoped GatewayService DI，不再持有模块级 `_gateway`。 |
| Core Protocol / Store | 已完成 MVP | `Session / Thread / Turn / Item / Job / Artifact / Approval / Trace / Retry / Connector` 对象和 SQLite Store 已落地。 |
| Pack Visibility & Manifest | 已完成 MVP | meeting、knowledge、video_studio 是 active pack；investment、interview 是 stub pack；尚未完整驱动 skill/policy bundle 装配。 |
| Job / Background Worker | 已完成 MVP | workflow 可创建 job 并关联 turn、trace、artifact；本地 in-process worker、job.events、failure_context 和 cancel 终态语义已落地。 |
| Tool Execution Guard | 已完成 MVP | builtin tools 与 Core engine tool loop 可在执行前阻断未审批高风险工具。 |
| Runtime Adapter Boundary | 已完成 MVP | Gateway 通过 RuntimeHandle / RuntimeAdapter 管理 SimpleRuntime 和 OpenHarness Runtime。 |
| Core-native Session/Event Store | 已完成 MVP | `session.list/read/events/transcript` 优先从 Core records 查询或重建，legacy JSON/JSONL 兼容回退。 |
| Adapter-level Governance Injection | 已完成 MVP | Simple/OpenHarness adapter 默认路径注入 policy evaluator、approval checker、trace context 和 tool metadata。 |
| Connector Execution Runtime | 已完成当前 MVP | connector submit/poll/cancel/collect 已接入 Core job/events/artifact；data_service_mcp 和 funasr_mcp 支持 gated stdio execution；Knowledge lifecycle 与 FunASR smoke 均通过真实 E2E。 |
| Cross-domain MCP Workflow | 已完成当前集成 MVP | Meeting workflow 可通过 `funasr_mcp` 转写，Meeting -> Knowledge runner 已跑通真实 `audio -> transcript -> minutes -> knowledge import/build/query`，并形成 33 条 artifact lineage。 |

## 3. Frozen Decisions

以下决策为团队冻结口径：

1. CLI / Web / Bot / Automation 必须统一走协议层。
2. Core 不承载具体业务逻辑。
3. 新业务必须以 Domain Pack 接入。
4. Runtime 必须通过 Adapter 使用，不能直接绑定 OpenHarness 内部对象。
5. SQLite 是当前主存储收敛方向，legacy JSON/JSONL 仅做兼容与导入。
6. 高风险动作必须进入 Policy / Approval / Trace / Retry。
7. 长任务默认进入 Job Service。
8. 重要结果必须 Artifact 化。
9. Gateway 不承载业务 workflow。
10. 新需求必须先归类到 Core / Pack / Connector / Runtime Adapter / Client。

## 4. 当前架构边界

```text
CLI / TUI / Headless
        |
FastAPI / SSE / JSON-RPC / stdio JSONL
        |
apps.gateway
        |
Lead Orchestrator + DomainWorkflow Registry
        |
Runtime Adapter + Tool Registry + Policy Middleware
        |
OpenHarness Runtime / SimpleRuntime / Meeting MCP / Native Tools
        |
Core SQLite Store + legacy JSON/JSONL compatibility
```

| 层 | 应负责 | 不应负责 |
| --- | --- | --- |
| Gateway | transport、auth、serialization、stream proxy、client experience binding | 继续新增业务 workflow 逻辑 |
| Core | protocol objects、session/thread/turn、policy、approval、job、artifact、workflow orchestration | 前端渲染、页面逻辑、具体业务规则 |
| Runtime Adapter | 封装 OpenHarness / SimpleRuntime，统一执行接口 | 对外协议定义、业务装配 |
| Pack | domain workflow、subagent、skill、connector、policy bundle | 平台通用逻辑 |
| Connector | 本地 MCP / 本地服务 / 原生工具 / 外部接口的接入 | 业务编排 |
| Store | 状态持久化与查询 | 业务判断 |

平台链路规则：

```text
Turn -> may create Job -> emits Items -> produces Artifacts -> all bound to Trace
```

## 5. Target Architecture

目标架构统一采用 V2.0 六大平面。旧 drawio 中的 L1-L5 五层目标图已废弃，不再作为正式目标架构口径。

```text
Client / Gateway Plane
  CLI / Web / Bot / Automation

Protocol App Server Plane
  JSON-RPC / SSE / stdio JSONL / Web Gateway

Harness Core Plane
  Session / Thread / Turn / Item
  Workflow / SubAgent / Tool / Skill / Connector Registry
  Policy / Approval / Retry / Trace / Secret Hygiene
  Job Service / Artifact Service

Runtime Adapter Plane
  OpenHarness Adapter
  SimpleRuntime Adapter
  Future DeepAgents Adapter

Domain Pack Plane
  Meeting / Knowledge / Investment / Interview / Video Studio

Connector / Tool / Store Plane
  Local MCP Servers / Native Tools / File Tools / Browser / External APIs
  SQLite first, future pluggable stores
```

目标原则：

- 协议优先，客户端只改变 transport，不改变核心语义。
- Core 不带业务，业务通过 Pack 接入。
- Pack 是可装配业务能力发布单元，不只是目录或 manifest。
- Connector 通过 registry + config ref 装载，不在 Core / Pack 中硬编码本机路径。
- Runtime 可替换，OpenHarness 必须隔离在 Runtime Adapter 后。
- 治理深入 turn / tool / job / artifact / retry。
- Session、Thread、Turn、Item、Job、Artifact、Approval、Trace、Retry、Connector 都是一级对象。

## 6. Gap & Roadmap

| 方向 | 当前状态 | 目标状态 | 差距 |
| --- | --- | --- | --- |
| 协议层 | `/v1/runs`、SSE、`/v1/rpc`、stdio JSONL 可用；GatewayService 仍承担集中 method 分发 | Codex-style App Server 级协议边界 | method registry、capability registry、compat alias、event/error code 尚未正式冻结。 |
| Store | Core SQLite 已引入，session/event 查询 Core 优先 | Core Store 成为主路径，legacy 仅兼容导入 | 仍需继续移除 Gateway store 主路径依赖。 |
| Job | 本地 in-process worker、job events、failure_context、cancel 终态语义已完成 MVP | 长任务统一进入 Job Service，未来可扩展进度、resume 和外部 worker | 仍缺可恢复 resume、细粒度 progress 和多 worker 调度；分布式队列当前非目标。 |
| Pack | manifest 可见，meeting/knowledge/video_studio active；Phase 3-E/4-A 已让 assembly 驱动 meeting/knowledge/video workflow 注册；Phase 4-B0 已把 meeting/knowledge/video workflow 实现迁入 pack | Pack 驱动 workflow / connector / skill / policy 装配 | Pack Assembly 与 pack-owned workflow MVP 已完成；后续需补 workflow DSL、skill/policy bundle 完整装配。 |
| Connector | Meeting MCP 已注册为 `meeting_voice_mcp`；Remote ComfyUI 已注册为 `remote_comfyui` descriptor 但延期启用；支持 `connector.list/get/health` 与 Core connectors 持久化 | Connector Registry 管理 MCP、健康检查、配置引用 | 当前主验收只验证 Meeting MCP；`remote_comfyui` 默认 `not_configured`，不执行远程任务。 |
| Runtime Adapter | Gateway 已通过 adapter 调用 runtime，并已完成 adapter-level governance injection MVP | Adapter 默认注入 policy、approval、trace、tool metadata | 已完成 MVP；后续仍需工具层自动 approval request 和更完整治理事件。 |
| 治理 | preflight、approval、retry、tool guard MVP 已完成；artifact lineage 查询已完成 MVP | turn/tool/job/artifact/retry 全链路一致治理 | 工具层自动创建 approval、job/artifact lineage 治理仍需补齐。 |
| 多业务迁移 | meeting/knowledge 已落地；video_studio 已完成规划型 MVP 且 workflow 实现已迁入 pack；Meeting artifact lineage 是当前用户态验收主线；investment/interview 仍为 stub | investment、interview、video_studio 可独立 pack 装配 | Video Studio 继续作为 pack 边界回归，不承接当前用户态验收；后续再补真实 remote render execution、specialist crew 和 approval gate。 |

## 6.1 剩余开发路线

| 阶段 | 目标 | 主要交付 | 验收底线 |
| --- | --- | --- | --- |
| Phase 4-C Core-native RPC Router | 协议分发收敛到 Core/App Server 风格 method registry | method registry、capability registry、compat alias、统一错误码 | `/v1/rpc`、stdio JSONL、Headless CLI 兼容；Meeting lineage 脚本通过 |
| Phase 4-D Tool-level Approval Automation | 工具执行层自动创建 approval request | tool invocation -> policy -> approval -> trace -> retry 闭环 | 写文件类 tool 返回 approval id；批准后可 retry；Meeting 不误拦截 |
| Phase 5-A DomainPack 2.0 Assembly Kernel | Pack 从 manifest 可见升级为可装配、可查询、可治理的业务单元 | Typed DAG workflow templates、Pack-owned agents、data_service MCP connector contract/stub、blocked/degraded reason | `pack.get(domain=knowledge)` 展示 DAG、agents、connector requirement 和 tool contract；缺依赖返回可解释 blocked/degraded |
| Phase 5-B Memory & Session Intelligence | 强化 Harness Core 记忆和长会话能力 | session summary、long-context compression、artifact-backed memory refs | 长会话可总结；Meeting 追问可引用前序 transcript/minutes |
| Phase 5-C Connector Execution Runtime | Connector 从 descriptor/health 升级为可执行 runtime | submit/poll/cancel/collect、connector job events、artifact collect、gated MCP stdio execution | 已完成当前 MVP：轻量 connector lifecycle 通过；data_service_mcp 真实 E2E 通过；ComfyUI 未配置不影响主线 |
| Phase 5-D Cross-domain MCP Workflow Stabilization | 双域 MCP 工作流稳定化 | FunASR MCP 真实调用、Meeting workflow 转写接入、Meeting -> Knowledge E2E | 已完成当前集成 MVP：一条 HarnessOS 命令跑通 audio -> transcript -> minutes -> knowledge import/build/query；后续补超时、取消、retryable failure 和产品化入口 |
| Phase 6 Productization / Open Source / Commercial Readiness | 进入可发布、可扩展、可维护状态 | API versioning、extension examples、release flow、多租户/secret scope | 新开发者 30 分钟内跑通 smoke + Meeting lineage acceptance |

当前主要风险：

| 风险 | 影响 | 缓解方向 |
| --- | --- | --- |
| Gateway 与 Core/Pack 职责重叠 | 后续功能可能继续写回 Gateway | Phase 4-B0 已迁出 meeting/knowledge/video workflow 和 Meeting MCP client/service；Gateway 仅保留旧导入兼容面，后续继续把 session/event/job/connector/pack 装配迁入 Core。 |
| Pack 只是 manifest | 多业务迁移时仍可能写死业务逻辑 | Roadmap Phase 3-E 已完成代码层 Pack Assembly MVP，Phase 4-B0 已完成 knowledge/video pack-owned workflow；Phase 5-A 升级为 DomainPack 2.0 Assembly Kernel，补 Typed DAG、Pack-owned agents、data_service MCP connector contract/stub。 |
| Job worker 仍是本地 in-process MVP | 长音频、回测、视频生成已有本地 worker 基础，但还不是分布式队列或多 worker 调度 | Phase 4 前继续以本地优先为主；分布式调度仍是非目标。 |
| Connector 未完全执行化 | 远程视频工具仍未执行化；connector 超时、取消、retryable failure 和 server interrupted recovery 仍需补强 | Roadmap Phase 3-F 已建立 Connector Registry MVP；Phase 4-B2 已延期保留 `remote_comfyui` descriptor；Phase 5-C 已完成 connector submit/poll/cancel/collect 与 data_service_mcp 真实 E2E；Phase 5-D 已接入 FunASR MCP 和 Meeting -> Knowledge。 |
| 治理注入不完整 | adapter 默认路径已注入治理上下文，但工具层自动 approval request 尚未完成 | 后续治理增强阶段补齐 tool/job/artifact 全链路自动审批与审计。 |

### 6.2 data_service MCP Contract / Connector Stub

Phase 5-A 对 `meeting-voice-assistant/backend/data_service` 采用 Contract + Connector Stub；Phase 5-C 已补齐 gated stdio execution 和真实外部 Harness 验收：

- harnessOS 侧声明 `data_service_mcp` connector ref、capability contract、health/assembly 展示和 blocked/degraded 语义。
- `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 显式开启真实 MCP stdio tool call；默认仍为 contract stub。
- Knowledge lifecycle runner 在真实 stdio 模式下复用同一 MCP server 进程，保证 data_service build queue 可在 `knowledge_build_start -> knowledge_build_status` 之间保留状态。
- Knowledge Pack 是主样板，`pack.get(domain=knowledge)` 必须展示知识库生命周期 Typed DAG、Pack-owned agents、connector requirement 和 tool contract。
- 外部 Agent 调用说明已落在 `/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/docs/data_service/MCP-EXTERNAL-AGENT-GUIDE.md`，并加入 `/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/docs/data_service/README.md` 文档入口。
- 后续 Knowledge 工作流执行必须通过 `data_service_mcp` lifecycle tools 和 v2 envelope tools 创建、导入、构建、查询、反馈、归档知识库；不得由 harnessOS 直接写 `workspace/row`、GraphRAG、llmwiki 或 quality 产物目录。
- 业务依赖关系固定为：Meeting Pack 使用 `funasr_mcp` / `funasr_service` 承载语音转写；Knowledge Pack 使用 `data_service_mcp` / `data_service` 承载 GraphRAG + llmwiki 知识库。
- 真实验收已通过：`HarnessOSRealDataServiceAcceptance4` 返回 `status=ok`、`workspace_id=harnessosrealdataserviceacceptance4`、`operation_id=op_fb639a7aee3c`、`warnings=[]`。
- Phase 5-D 真实验收已通过：FunASR MCP smoke 返回 `status=ok`、connector job `job_db4b4114eab3`、artifact `art_5f24f94bfbdc`；Data Service MCP smoke 返回 `status=ok`、workspace `harnessos-real-data-service-phase5d`、operation `op_7df6de70eb14`；Meeting -> Knowledge smoke 返回 `status=ok`、session `sess_333527af725f`、meeting session `meeting_cceef461`、workspace `harnessos-meeting-knowledge-phase5d-retry`、artifact lineage count `33`。
- 环境前置：相邻项目 data_service venv 必须完整安装 `backend/requirements.txt`。

另一个 Codex 终端需要在 data_service MCP server 实现的 tools：

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

统一返回字段：

```json
{
  "workspace_id": "string",
  "operation_id": "string|null",
  "status": "ok|queued|running|completed|failed|cancelled|blocked",
  "warnings": [],
  "artifact_refs": [],
  "next_actions": [],
  "data": {}
}
```

安全与兼容要求：

- workspace 必须位于 `DATA_SERVICE_WORKSPACE_ROOT` allowlist 下。
- source path 必须经过 allowlist、大小上限、sha256 去重和 symlink 防绕过。
- build 是长任务，`knowledge_build_start` 返回 `operation_id`，`knowledge_build_status` 轮询。
- 保留现有 `knowledge_ingest`、`knowledge_query`、`knowledge_quality_*` MCP tools 兼容性。

## 7. Roadmap Acceptance Matrix

状态定义：

- **已完成**：默认路径可继续作为主架构迭代。
- **已完成 MVP**：能力存在但不是目标终态。
- **部分完成**：已有局部能力或兼容层，但不是默认路径。
- **未开始**：尚无可验收实现。

| 阶段 | 状态 | 验收标准 | 自动化验证 | 用户态验证 | 文档同步 |
| --- | --- | --- | --- | --- | --- |
| Phase 0 控制面骨架 | 已完成 | CLI/headless/API/RPC/stdio 最小闭环可用 | gateway、api、cli 基础回归 | `python3 -m cli.main run "你好"` | 当前状态、架构图 |
| Phase 1 Meeting MCP MVP | 已完成 MVP | 真实会议音频可生成 transcript/analysis/result/minutes | meeting gateway/workflow/audio tests | 会议音频分析命令成功返回纪要 | 验收用例、gap、drawio |
| Phase 1-C Artifact Store | 已完成 MVP | 会议四类产物登记为 artifact，可 list/read | artifact + meeting workflow tests | 读取 minutes artifact 成功 | artifact 说明和用例 |
| Phase 1-D Workflow Registry | 已完成 MVP | meeting/knowledge workflow 可路由，普通聊天不误路由 | lead orchestrator + meeting tests | 普通聊天与会议音频路径都可用 | workflow 状态 |
| Phase 2-A Trace/Audit | 已完成 MVP | chat、meeting、artifact read 可查询 trace | trace gateway tests | trace.get 可查到 turn/workflow/artifact | trace 验收记录 |
| Phase 2-B Approval | 已完成 MVP | approval 生命周期可创建、批准、拒绝、查询 | approval gateway tests | approval.request/approve 可用 | approval 验收记录 |
| Phase 2-C Policy Rules | 已完成 MVP | 写/删/发/发布类请求默认生成 approval，只读不触发 | policy approval tests | 写文件请求被阻断并返回 approval_id | policy 验收记录 |
| Phase 2-D Retry/Resume | 已完成 MVP | approval 通过后可 `turn.retry` 续跑，重复 retry 被拒绝 | retry resume tests | approved retry 成功 | retry 验收记录 |
| Phase 2-E Secret Hygiene | 已完成 MVP | 常见密钥不进入持久化明文 | secret hygiene tests | artifact/read/trace 不返回明文 key | secret 验收记录 |
| Phase 2-F Persistence Hardening | 已完成 MVP | 本地 JSON/JSONL 写入有锁和原子替换 | persistence concurrency tests | 无手工必测 | persistence 风险记录 |
| Phase 3-A App Lifecycle | 已完成 | FastAPI route 使用 app-scoped GatewayService DI | api/gateway regression | `/v1/runs` 与 `/v1/rpc` 共用注入服务 | CURRENT/gap/drawio |
| Baseline v1.5-E | 已完成 MVP | Core model/store、pack 可见性、job 记录、tool guard、runtime adapter 边界均可回归 | core/store/pack/job/tool/runtime tests | 会议音频链路不回归 | baseline 文档 |
| Roadmap Phase 3-B Session/Event Store | 已完成 MVP | `session.list/read/events/transcript` Core records 优先，legacy 兼容回退 | 26 项定向回归；83 项阶段回归 | 真实音频 CLI 验收生成 job 与四类 artifact | 本文档、drawio、测试文档 |
| Roadmap Phase 3-C Background Job Worker | 已完成 MVP | 本地 in-process worker、job 状态机、job.events、cancel、failure_context 可用 | 27 项定向回归 | 真实音频 CLI 验收生成 job；`job.events` 返回 queued/started/completed；验收后清理产物 | 本文档、drawio、测试文档 |
| Roadmap Phase 3-D Adapter Governance | 已完成 MVP | Simple/OpenHarness 默认路径注入 policy/approval/trace/tool metadata | 11 项定向回归；58 项阶段相关回归 | 真实音频 CLI 验收通过，会议不误拦截；验收后清理产物 | 本文档、drawio、测试文档 |
| Roadmap Phase 3-E Pack Assembly | 已完成 MVP | pack manifest 驱动 workflow/connector/skill/policy 装配 | 项目自身回归 90 passed；真实音频验收 2 passed；drawio XML 校验通过 | meeting/knowledge 由 assembly 注册；缺 connector 返回可解释错误；真实音频验收通过 | 本文档、测试文档、开发计划 |
| Roadmap Phase 3-F Connector Registry | 已完成 MVP | Meeting MCP 作为 connector 注册，支持 list/get/health | 40 项定向回归；connector stdio 验证通过 | 缺依赖时返回可解释错误；可用时会议音频成功 | 本文档、测试文档、开发计划 |
| Phase 4-A Video Studio Pack MVP | 已完成 MVP | brief -> script -> storyboard -> shot_list artifact | pack/orchestrator/gateway 定向回归 | `turn.start(domain=video_studio)` 生成四类规划 artifact | 本文档、测试文档、开发计划 |
| Phase 4-B0 Domain Pack Workflow Loader | 已完成 MVP | knowledge/video workflow 实现迁入 pack，Gateway 只保留注册和装配 | 10 项定向回归 | workflow.list 和 video/knowledge route 不回归 | 本文档、测试文档、开发计划 |
| Phase 4-B1 Artifact Lineage Query | 已完成 MVP | Core 保存 parent_ids；`artifact.lineage` 返回产物图 | 13 项定向回归 | Meeting `transcript -> analysis -> result -> minutes` 可查询 | 本文档、测试文档、开发计划 |
| Phase 4-B2 Remote ComfyUI / Render Manifest Scaffold | 延期保留 | `remote_comfyui` connector 和 render manifest 只作为未来远程执行边界预留 | scaffold 自动化回归 | 当前用户态不验收 ComfyUI；Meeting lineage 仍是主验收线 | 本文档、测试文档、开发计划 |
| Phase 4-C Core-native RPC Router | 已完成 MVP | `RpcRouter`、`method.list`、registry capabilities、compat alias、稳定错误码 | 85 项阶段相关回归 | RPC/stdio/headless 兼容；method registry 可枚举；未知方法/缺参/handler failure 错误码稳定 | 本文档、测试文档、开发计划 |
| Phase 4-D Tool-level Approval Automation | 已完成 MVP | 工具层 approval requester、tool result approval metadata、retry/trace/Core records 绑定 | 98 项阶段相关回归 | 写文件 tool 返回 approval id；reject 阻断 retry；approved approval id 放行工具执行 | 本文档、测试文档、开发计划 |
| Phase 5-A DomainPack 2.0 / Knowledge-primary Connector Stub | 已完成 MVP | Typed DAG、Pack-owned agents、data_service MCP contract/stub、connector capability 装配 | 42 项 Phase 5-A 定向回归；HarnessOS `tests/` 主线 125 passed、1 skipped；真实音频依赖启动 FunASR 后 2 passed | `pack.get(domain=knowledge)` 展示 DAG、agents、connector tool contract 和 blocked/degraded reason；`agent.list/get` 可查 Pack-owned agents；显式 blocked domain 返回可解释失败 | 本文档、测试文档、开发计划 |
| Phase 5-B Memory & Session Intelligence | 已完成 MVP | session summary 与 artifact-backed memory refs | 本地默认回归 128 passed、1 skipped、2 deselected；真实音频依赖启动 FunASR 后 2 passed | `memory.list/get/summary/extract_from_artifacts` 可用；普通 turn 可注入 session memory；Meeting artifact refs 可复用前序产物；retry/approval 重放保持原始输入 | 本文档、测试文档、开发计划 |
| Phase 5-C Connector Execution Runtime | 已完成当前 MVP | connector submit/poll/cancel/collect；FunASR MCP contract/descriptor；data_service gated stdio MCP client；Knowledge lifecycle 持久 MCP session | FunASR MCP/Gateway connector 回归；Knowledge fake MCP 回归；真实 data_service E2E | `funasr_mcp` 可发现、可 stub submit；`data_service_mcp` 可在 `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 下完成真实 `create -> import -> build -> query -> feedback -> review -> plan -> archive` | 本文档、drawio、测试文档 |
| Phase 5-D Cross-domain MCP Workflow Stabilization | 已完成当前集成 MVP | FunASR MCP 真实调用；Meeting workflow 转写接入；Meeting -> Knowledge E2E；跨域 artifact lineage | 定向 2 passed；默认本地 133 passed、1 skipped、2 deselected；真实 FunASR/Data Service/Cross-domain smoke 通过 | 一条 HarnessOS 命令已跑通 audio -> transcription -> meeting minutes -> knowledge import/build/query；仍需产品化入口、超时/取消/retry hardening | 本文档、测试文档、开发计划 |
| Phase 6 Productization / Open Source / Commercial Readiness | 未开始 | API versioning、扩展示例、发布和治理文档 | 待补 | 新开发者可跑通 smoke + Meeting lineage acceptance | 后续同步 |

## 8. 验收样本与路径策略

团队标准样本目录约定：

```text
fixtures/audio_samples/
```

团队标准验收命令约定：

```bash
python3 -m cli.main run --json \
'请分析 ./fixtures/audio_samples/sample_ted_talk.mp3，生成会议纪要'
```

团队共享验收脚本约定：

```text
scripts/e2e_meeting_validation.sh
```

在标准 fixture 和脚本落地前，可继续使用本机真实音频进行阶段验收，但个人路径只能记录为 local validation evidence，不作为团队基线路径。

当前 local validation evidence：

- Roadmap Phase 3-B 和 3-C 真实音频验收曾使用本机 TED 音频完成 CLI 端到端验证。
- 验收生成 job、meeting output 和 `analysis/result/transcript/minutes` 四类 artifact。
- 验收后已清理外部会议产物与本地 `.harnessos` 验收记录。

## 9. 扩展准入规则

任何新业务或新能力进入开发前，必须回答：

1. 它属于 Core、Pack、Connector、Runtime Adapter 还是 Client / Gateway？
2. 是否会产生重要结果，是否需要 Artifact 化？
3. 是否是长任务，是否必须进入 Job Service？
4. 是否包含写入、删除、发送、发布、交易或策略执行等高风险动作，是否需要 Policy / Approval / Trace？
5. 是否需要新 connector，是否具备 registry、config ref 和 health check？

## 10. 当前非目标

### Phase 5-D Connector Gap Update - FunASR MCP / Cross-domain MCP

- `funasr_mcp` connector descriptor 与 FunASR MCP stdio 服务入口已落地，解决 FunASR 只有 HTTP 服务、无法作为 MCP connector 发现的问题。
- `funasr_mcp` 默认仍通过 contract stub / legacy Meeting MCP 兼容路径避免 CI 依赖真实模型；显式 `HARNESS_FUNASR_MCP_EXECUTION=stdio` 时会走真实 MCP `tools/call`。
- Meeting 主链路仍使用 `meeting_voice_mcp` 做会议分析与 minutes 生成；`funasr_mcp` 定位为底层 ASR connector，已被 Meeting workflow 用于可配置转写。
- Cross-domain runner 已把 FunASR transcript artifact 与 Meeting minutes artifact 作为 Knowledge import 的上游 lineage，并通过 `data_service_mcp` 完成 source import、build、query 和质量工具链。

## 10. 当前非目标

- 不做分布式集群调度。
- 不做多租户 SaaS 平台。
- 不做复杂图形化编排器。
- 不同时推进 Investment 和 Video 两条业务线。
- 不在 Core 或 Gateway 中直接落业务逻辑。
- 不把 OpenHarness 内部对象直接暴露为产品协议。

## 11. 当前文档清单

### 当前主线文档

以下文档代表当前团队沟通、开发拆解和阶段验收的主线口径。

#### 架构、基线与计划

- `docs/design/V2.0/harnessos_baseline_v2.md`
- `docs/design/V2.0/harnessos_architecture_master_spec_v2.md`
- `docs/architecture/team-baseline-and-target-architecture_v2.md`
- `docs/architecture/harnessos_target_architecture_v2.md`
- `docs/architecture/CURRENT-STATUS_v2.md`
- `docs/architecture/current-vs-target-gap_v2.md`
- `docs/architecture/current-vs-target-gap_v2.drawio`
- `docs/architecture/development_plan_v2.md`

#### 架构图

- `docs/architecture/diagrams/01_current_architecture_v2.drawio`
- `docs/architecture/diagrams/02_target_architecture_v2.drawio`
- `docs/architecture/diagrams/03_three_framework_integration_v2.drawio`

#### 测试与验收文档

- `docs/test-acceptance-plan_v2.md`
- `docs/acceptance-test-cases_v2.md`

#### API 与接口文档

- `docs/api/gateway-endpoints_v2.md`
- `docs/api/llm-provider-config_v2.md`
- `docs/api/orchestrator-interface_v2.md`
- `docs/api/unified-message-schema_v2.md`

### 历史归档文档

以下文档只作为历史参考，不再作为当前开发计划、架构评审或阶段验收的主线依据。

#### V1.0 设计归档

- `docs/history/design/V1.0/00_INDEX.md`
- `docs/history/design/V1.0/01_OVERALL_ARCHITECTURE.md`
- `docs/history/design/V1.0/02_PHASE1_DETAILED_ARCHITECTURE.md`
- `docs/history/design/V1.0/03_PHASE2_DETAILED_ARCHITECTURE.md`
- `docs/history/design/V1.0/04_PHASE3_DETAILED_ARCHITECTURE.md`

#### 参考框架图归档

- `docs/history/architecture/reference-frameworks/deep-agents-architecture.drawio`
- `docs/history/architecture/reference-frameworks/deerflow-architecture.drawio`
- `docs/history/architecture/reference-frameworks/openharness-architecture.drawio`
- `docs/history/architecture/reference-frameworks/三种Harness的架构对比图.drawio`

#### 阶段报告归档

- `docs/history/reports/stage-acceptance-report-2026-04-25.md`
