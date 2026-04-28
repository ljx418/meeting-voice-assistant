# harnessOS V2.0 Development Plan

## 1. 当前阶段判断

Phase 1 和 Phase 2 已完成 MVP 验收。

已完成范围：

- Phase 1：Meeting MCP、真实音频会议分析、会议产物登记、Lead Orchestrator、DomainWorkflow Registry、KnowledgeWorkflow MVP。
- Phase 2：Trace/Audit、Approval、Policy Rules、Retry/Resume、Secret Hygiene、Persistence Hardening。
- Phase 3-A：API App Lifecycle，FastAPI route 模块级 `_gateway` 已移除，GatewayService 支持 app-scoped DI。
- Core v1.5-A~E：Core protocol/store 基础、Pack Registry、Job Service 同步 MVP、Tool Policy Middleware、Runtime Adapter 收敛。
- V2.0 Target Architecture：已采纳 `docs/design/V2.0/harnessos_architecture_master_spec.md`，并新增 `docs/architecture/harnessos_target_architecture_v2.md`。

因此后续开发从 **Phase 3-B** 继续，不再回到 Phase 1/2 追加主线能力。Phase 1/2 后续只允许做回归、修复和验收补强。

## 2. 开发总目标

V2.0 的开发目标是把当前 Gateway-centered assistant 迁移为：

> Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform

核心原则：

- Core 不写死业务逻辑。
- 业务能力通过 Domain Pack 装配。
- Runtime 通过 Adapter 隔离。
- 长任务进入 Job Worker。
- Tool、Job、Artifact、Retry 都必须进入 policy/approval/trace 治理链路。
- 每个阶段完成后必须同步测试文件、验收文档和架构图。

## 3. Phase 3 开发计划

### Phase 3-B：Core-native Session/Event Store

目标：把旧 Gateway snapshot/events 从主运行数据源降级为兼容层，让 session、thread、turn、item、trace 查询和写入以 Core Store 为准。

交付物：

- CoreAppService 提供 session/event 的主写入和主查询路径。
- GatewaySessionStore 只作为 legacy compatibility 和 import source。
- `session.list/read/events/transcript` 至少有 Core-native 查询路径。
- 保留 legacy JSON/JSONL 读取能力，不删除旧数据。

验收标准：

- 普通 `你好` 产生 session/thread/turn/items，并可通过 Core RPC 查询。
- `session.events` 和 transcript 能从 Core records 重建。
- 旧 JSON/JSONL fixture 可导入或兼容读取。
- 会议真实音频分析不回归。

### Phase 3-C：Background Job Worker

目标：把同步 Job MVP 升级为真正长任务服务。

交付物：

- Job 状态机：`queued / running / completed / failed / cancelled`。
- `job.create/get/list/cancel` 支持后台任务记录与状态更新。
- `job.events` 或等价事件查询接口。
- Meeting workflow 可作为后台 job 执行候选；若仍同步执行，也必须写入完整 job event。

验收标准：

- 真实会议音频创建 job，状态可查询，完成后关联 transcript/minutes/analysis/result artifacts。
- cancel 对 queued/running/completed 的行为有明确结果。
- job failure 能记录 `failure_context`。
- 验收后清理外部会议产物和 `.harnessos` 验收记录。

### Phase 3-D：Adapter-level Governance Injection

目标：把治理能力注入 Runtime Adapter 默认路径，避免只在 Gateway 或部分工具层生效。

交付物：

- Runtime Adapter 创建 OpenHarness/Simple runtime 时注入 policy evaluator、approval checker、trace context。
- Tool metadata 默认携带 session/turn/trace/policy 上下文。
- 未审批高风险 tool 在 adapter 默认路径中也会被阻断。

验收标准：

- builtin tools 和 Core engine tool loop 仍可阻断未审批写入。
- OpenHarness RuntimeBundle 路径的 tool metadata 可被 policy middleware 读取。
- 只读工具不误拦截。
- 会议真实音频不被误判为写入类高风险动作。

### Phase 3-E：Pack Assembly MVP

目标：让 pack manifest 不只可见，还能驱动 workflow、connector、skill、policy bundle 注册。

交付物：

- Pack manifest schema 明确 workflow、connector、skill、policy、artifact kind 字段。
- meeting/knowledge 从 manifest 完成可运行装配。
- investment/interview/video_studio 保持 stub，但字段结构与真实 pack 一致。
- `pack.get` 能返回装配状态和缺失依赖。

验收标准：

- `pack.list/get` 显示五个 pack 及 assembly 状态。
- meeting workflow 由 pack assembly 注册后仍能处理真实音频。
- 禁用或缺失 connector 时返回可解释错误。

### Phase 3-F：Connector Registry MVP

目标：把 Meeting MCP 从硬编码相邻项目路径升级为 connector 管理对象。

交付物：

- ConnectorRecord 可记录 connector id、kind、domain、capabilities、health、config_ref。
- Meeting MCP 作为 `meeting_voice_mcp` connector 注册。
- `connector.list/get/health` RPC 或 Core query path。
- connector secret/config 不进入明文日志。

验收标准：

- `connector.list` 能看到 Meeting MCP。
- `connector.health` 能区分可用、不可用和缺依赖。
- 会议真实音频通过 connector registry 找到 Meeting MCP。

## 4. Phase 4 开发计划

Phase 4 才进入新业务域扩展，优先选择 AI Video Studio Pack 或 Investment Pack 之一，不并行展开。

默认顺序：

1. Video Studio Pack MVP：brief -> script -> storyboard -> shot list artifact。
2. Artifact lineage：script -> storyboard -> assets -> render output。
3. Specialist crew：Studio Lead、Director、Script、Storyboard、Editing、QA/Publish。
4. Publish/render 前强制 approval。

Phase 4 开始前必须满足：

- Phase 3-B~3-F 全部完成。
- Pack Assembly 可运行。
- Connector Registry 可发现本地服务。
- Background Job Worker 可承载长任务。

## 5. 每阶段强制同步规则

每完成一个阶段，必须同步更新：

- `docs/architecture/CURRENT-STATUS.md`
- `docs/architecture/current-vs-target-gap.md`
- `docs/architecture/current-vs-target-gap.drawio`
- `docs/architecture/development_plan_v2.md`
- `docs/test-acceptance-plan.md`
- `docs/acceptance-test-cases.md`

每阶段必须执行：

- 阶段定向自动化测试。
- 阶段相关完整回归。
- `xmllint --noout docs/architecture/current-vs-target-gap.drawio`。
- 使用 `/Users/Zhuanz/Desktop/workspace/音频资料` 下真实音频完成会议端到端验收。
- 验收后清理外部会议产物和本地 `.harnessos` 验收记录。
