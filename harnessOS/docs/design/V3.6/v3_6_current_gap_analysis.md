# V3.6 Current Gap Analysis

文档状态：V3.6 complete baseline 已冻结；V3.6/V4.0 preflight hardening complete，V4.0-0 正式开发仍暂停，下一步先以本文和同名 drawio 作为 V4.0 baseline 审计入口。  
配套图：`v3_6_current_gap_analysis.drawio`。

本文与 `v3_6_current_gap_analysis.drawio` 是 V3.6 后续规划、验收和与用户交互时的核心维护文件。两者必须同步更新：本文承载文字合同，drawio 承载同一套架构演进、差距矩阵、阶段路线图和 V4.0 gate。

## 1. 文档定位

本文只描述 V3.6 **Workflow Runtime Contract & Pipeline Operating Model** 的当前差距、目标架构和阶段影响范围。V3.5 已完成项只作为 V3.6 的起点基线，不再进入本文主叙事作为待办。

V3.6 不是继续扩展 SDK/BFF，也不是直接进入 V4.0 UI。它要补的是 V4.0 正式 UI 所依赖的后端事实源：

```text
V3.5 Application Adaptation Layer
  -> V3.6 Workflow Runtime Layer
  -> V4.0 Workflow Studio / AgentTalkWindow
```

因此，V3.6 gap 不应被描述成以下几类问题：

- 不是 V3.5 SDK / BFF / hooks 的延续堆叠。
- 不是 Meeting / Knowledge / Video 业务迁移。
- 不是 Core 大重构。
- 不是低代码画布 UI。
- 不是完整 AgentTalkWindow。

V3.6 要回答的问题是：

> 外部业务 App 已经能接入 harnessOS 之后，如何把一个业务流程定义为可版本化、可运行、可追踪、可审批、可评价、可修改、可被 UI 重建的流水线。

## 2. 当前状态

当前 harnessOS 已冻结 V3.5 baseline：

- V3.5 complete at dev/local Application Adaptation Layer level。
- Completion evidence bundle 位于 `docs/design/V3.5/v3_5_completion_evidence_bundle.md`。
- SDK、BFF、hooks、EventBridge、Embed、Pack/Connector template、Reference App 已完成 dev/local 证明链路。
- V3.5 明确不声明 production-ready external app support、完整 AgentTalkWindow、完整 Workflow Studio、enterprise auth/OAuth/SSO ready 或 multi-tenant production control plane。

当前事实：

- Protocol App Server 已具备 JSON-RPC / HTTP / SSE/EventSource / stdio 等基础入口。
- V3.5 已有 method/event/error schema registry、capability token、`approval.respond`、`events.subscribe`、Python SDK、TypeScript SDK、React hooks、Full BFF template。
- Core 已有 Session、Turn、Job、Artifact、Trace、Approval、Policy、Scope 等平台对象。
- Pack / Connector template 和 reference app 已证明“不改 Core 接入新 app”的 dev/local 路径。
- EventBridge 已支持 browser-friendly EventSource、signed subscription URL、fetch stream、cursor replay 和 channel filtering。
- V3.6-0 已新增独立 workflow runtime contract namespace：`workflow_method_inventory.py`、`workflow_event_inventory.py`、`workflow_error_inventory.py`。
- V3.6-0 已新增 workflow runtime schema draft：`workflow_methods.py`、`workflow_events.py`、`workflow_objects.py`、`workflow_errors.py`。
- V3.6-A 已新增 `core/workflows/models.py`，冻结 workflow object contract models。
- V3.6-A 已将 `workflow_objects.py` 升级为模型驱动 contract schema：`schema_status=contract`、`stable_for_ui=false`。
- V3.6-A 已新增 `WorkflowEdge`，并验证 edge 引用的 station_id 必须存在。
- V3.6-A 已明确 Template / Draft / Version 关系：Template 是逻辑身份，Draft 是可编辑草稿，Version 是不可变发布快照。
- V3.6-A 已补强 `WorkflowInstance`、`StationRun`、`ArtifactContract`、`QualityContract`、`WorkflowAction`、`WorkflowPatch`、`BusinessEvent`、`PipelineBoard` 的对象边界。
- V3.6-B 已新增 dev/local `WorkflowStore` / `WorkflowRepository` 和 `InMemoryWorkflowStore`，GatewayService 可注入 workflow store。
- V3.6-B 已实现 `workflow.template.create/get/list/update_draft/publish/archive`、`workflow.draft.save`、`workflow.version.get/list`。
- V3.6-B 已固定 template id 唯一性范围为 `app_id + project_id + workspace_id + workflow_template_id`。
- V3.6-B 已固定 draft revision/conflict、publish explicit version、published draft lock、update-after-publish fork、archive idempotency 和 scope/capability 语义。
- V3.6-C 已实现 `workflow.instance.start/get/list/status/pause/resume/cancel/retry`、`station.run.get/list`、`station.rerun`。
- V3.6-C 已引入 deterministic execution mode：`max_steps=1` 可只执行一个 station，保留 running 中间态，后续通过 pause/resume/cancel 测状态机。
- V3.6-C 的 start 基于 immutable `WorkflowVersion.snapshot`；draft 修改不会影响正在运行的 instance。
- V3.6-C 的 StationRun 已绑定真实 `JobRecord`、最小 output artifact metadata 和 trace；Station B 的 input_artifact_ids 可消费 Station A output。
- V3.6-D 已实现 workflow-bound pre-execution approval point：approval-required station 先进入 `waiting_approval`，approval 前不创建 Job/Artifact，不执行 downstream station。
- V3.6-D 已复用 `approval.respond` 作为唯一 continuation path：approve 执行当前 station 并按 execution mode 继续，reject 将 workflow 置为 `blocked`。
- V3.6-D 已增加 workflow side-effect marker：`pending/applying/applied/failed`，支持 approved decision 缺失 side effect 后恢复，避免 repeated approve 永久 no-op 卡住 workflow。
- V3.6-D 已支持 waiting workflow cancel：StationRun 置为 cancelled，approval binding 标记 inactive，late approval 返回 `WORKFLOW_APPROVAL_INACTIVE` 且不改写 approval decision。
- V3.6-D 已让 approval.required 通过 EventBridge approval channel 可观察，event.data.workflow_binding 携带 workflow_instance_id / station_run_id。
- V3.6-D 仍明确不创建 QualityEvaluation、不实现 Board API、不实现 business event 和 patch。
- V3.6-E 已实现 ArtifactContract 字段补强：`contract_id`、`cardinality`、`kind_match_policy`，并保持 ArtifactContract 只描述 station input/output 期望 artifact，不覆盖 Artifact Registry 主合同。
- V3.6-E 已固定 `contract_id` 唯一性范围为单个 Station；同一 station 内重复返回 `WORKFLOW_ARTIFACT_CONTRACT_INVALID`，不同 station 可以复用相同 contract_id。
- V3.6-E MVP 支持 `kind_match_policy=exact`，要求 `artifact.kind == contract.artifact_kind`；kind mismatch 返回 `WORKFLOW_ARTIFACT_KIND_MISMATCH`。`compatible` 只按显式 compatible metadata 判断，不作为默认 fallback。
- V3.6-E 已实现 StationRun `input_bindings` / `output_bindings`，并保持扁平 `input_artifact_ids` / `output_artifact_ids` 与 bindings 一致。
- V3.6-E 已将 workflow artifact metadata 收口到 `metadata.workflow`、`metadata.artifact_contract`、`metadata.lineage`，用户 metadata 放入 `metadata.user`，不得覆盖系统 namespace。
- V3.6-E 已实现 input validation MVP：只检查 artifact exists、scope、artifact kind、required binding、schema_ref/metadata，不调用 `artifact.read`，不读取 media/binary/large/external-only 内容。
- V3.6-E 已实现 output parent_ids 由 input bindings 推导，按 first-seen order 去重；cross-scope parent 会被拒绝，`artifact.lineage` 不跨 scope traversal。
- V3.6-E 已实现 station rerun artifact history：rerun 新建 artifact，`attempt` / `rerun_of_station_run_id` 放入 `metadata.workflow`，默认不把旧 output artifact 作为新 artifact parent。
- V3.6-E 已明确 connector_result 只能作为 evidence/extra node，不能替代 station output artifact；只有 output contract 明确允许 connector_result kind 时才可作为 output。
- V3.6-E 已覆盖 artifact registration failure atomicity：registration 失败时返回 `WORKFLOW_ARTIFACT_REGISTRATION_FAILED`，StationRun 不会被标记 completed，failure_context 做 secret redaction。
- V3.6-E 不新增 Python/TypeScript SDK default wrappers，不新增 workflow-specific lineage RPC，继续复用 `artifact.lineage`。
- V3.6-F 已实现 QualityEvaluation MVP：`quality.evaluation.create/get/list/attach` 进入 callable method list，`sdk_exposure=workflow_runtime`，不进入 Python/TypeScript SDK default wrappers。
- V3.6/V4.0 preflight hardening 已完成：`session.close` / `session.resume`、`memory.get`、Board/status job 读取、business EventBridge channel、workflow-bound legacy approval、high-risk workflow patch apply 均已补 scope/capability/governance guard。
- Workflow patch governance 已收紧：`requires_approval=true` 的 patch 不能直接 apply，返回 `WORKFLOW_ACTION_FORBIDDEN`；draft revision 不变，patch 不标记 applied，trace 做 redaction。后续如需高风险 patch 审批流，必须另设正式 workflow patch approval flow。
- Workflow-bound approval 只能通过 `approval.respond` 继续；legacy `approval.approve/reject` 对 standalone approval 保持兼容，但对 workflow-bound approval 返回 `WORKFLOW_ACTION_FORBIDDEN`，不会只改 approval status 导致 workflow 卡死。
- Platform startup neutrality 已加防回归：Gateway 平台启动路径不再在模块顶层 hard import Meeting/Knowledge/Video workflow；legacy business workflow 只通过 lazy-load / pack descriptor 路径进入。
- Reference App frontend 默认使用 BFF structured helper，不再用 TypeScript SDK `baseUrl="/bff"` 形成 `/bff/v1/rpc` 误路径。
- V4.0 drawio 已对齐冻结协议名：使用 `workflow.board.get`、`workflow.instance.status`、`station.output.list`、`workflow.patch.*`、`workflow.template.publish`、`approval.respond`、`business.event.*`、`workflow.context.*`、`artifact.lineage`、`quality.evaluation.*`，不再展示未冻结的 `workflow.invoke/observe/review`。
- V3.6-F 已实现 rule/manual/llm_placeholder evaluator 边界：rule evaluator 必须追溯 QualityContract / rubric_id，manual evaluator 可使用 caller-provided rubric_id，llm_placeholder 不调用真实 LLM。
- V3.6-F 已实现 score/status validation：score 必须在 0.0 到 1.0，rule evaluator 按 QualityContract.threshold 计算 passed/failed，invalid score/status 返回 `QUALITY_EVALUATION_INVALID`。
- V3.6-F 已实现 attach 语义：`auto_attach` 可直接绑定，重复 attach 同一 station_run/artifact 返回 idempotent success，改绑不同 target 返回 `QUALITY_EVALUATION_ALREADY_ATTACHED`。
- V3.6-F 已实现 binding validation：workflow、station_run、artifact 必须存在且同 scope；artifact 默认必须属于 station output，input artifact evaluation 需要显式 `allow_input_artifact=true`。
- V3.6-F 保持 artifact content boundary：evaluator 不调用 `artifact.read`，不读取 media/binary/large/external-only 内容，artifact.read blocking policy 不回退。
- V3.6-F 保持 no runtime state mutation：failed quality evaluation 不改变 WorkflowInstance.status 或 StationRun.status，不触发 approval、rerun、board、business event 或 patch。
- V3.6-F 已实现 trace/record redaction：QualityEvaluation record、trace、issues/suggestions/metadata 不泄露 capability token、subscription token、Authorization、secret、raw artifact content 或 raw trace payload。
- V3.6-F 只声明 quality trace 证据，不声明 live quality EventBridge streaming ready。
- V3.6-F 已冻结为 `V3.6-F complete: Quality evaluation MVP ready`，冻结证据见 `v3_6_f_completion_note.md`。
- V3.6-G 已实现 Pipeline Board Data API：`workflow.board.get`、`workflow.instance.status`、`station.output.list`。
- V3.6-G Board API 返回 station/job/artifact/approval/quality/trace summary，按 scope 过滤并做 redaction。
- V3.6-G 只消费 V3.6-F QualityEvaluation，不修改 QualityEvaluation，不实现 business event，不实现 workflow patch，不声明 V3.6 complete 或 V4.0 ready。
- V3.6-H 已实现 Business Event Bridge / Workflow Context：`business.event.emit`、`business.event.bind`、`workflow.context.get`、`workflow.context.update`。
- V3.6-H 已固定 WorkflowContext 分区：`system`、`business`、`runtime`、`metadata`；外部 update 和 business event binding 只能写 `context.business`。
- V3.6-H 已支持 shallow merge 与 `context.business.*` path set；`expected_revision` stale 返回 `WORKFLOW_CONTEXT_CONFLICT`。
- V3.6-H 已定义 `BusinessEventBinding`，MVP 仅支持 `mode=set`，`target_path` 必须位于 `context.business.*`，`payload_path` 只能从 `event.payload.*` 取值。
- V3.6-H 已实现 business event idempotency：重复 `event_id` / `idempotency_key` 不重复应用 context update。
- V3.6-H 已实现 live EventBridge：`business.event.received` 进入 business channel，`workflow.context.updated` 进入 workflow_context channel；event envelope 带 scope、workflow_instance_id 和 context_revision。
- V3.6-H 已验证 no approval/runtime bypass：business event 和 context update 不能修改 WorkflowInstance.status、StationRun.status、Approval status，不能调用 `approval.respond`、`station.rerun` 或 `workflow.patch.apply`。
- V3.6-H 不修改 V3.6-G Board API 合同，不实现 workflow patch，不创建 QualityEvaluation，不实现 V3.6-J dummy pipeline E2E。
- V3.6-I 已实现 Safe Workflow Patch Contract：`workflow.patch.propose`、`workflow.patch.diff`、`workflow.patch.apply`、`workflow.patch.reject`。
- V3.6-I 已固定 patch 状态机：`proposed -> applied`、`proposed -> rejected`；repeated same action idempotent，conflicting transition 返回 `WORKFLOW_PATCH_CONFLICT`。
- V3.6-I patch 绑定 `workflow_template_id`、`workflow_draft_id`、`base_revision`、`base_version_id`、`operation`、`proposed_by`、`actor_type`、`actor_id`；apply 校验 current draft revision 等于 patch base revision，MVP 不做 rebase。
- V3.6-I `workflow.patch.apply` 只修改 WorkflowDraft.draft，不修改 WorkflowVersion.snapshot；apply 成功后 draft revision 递增并记录 `applied_revision` / `resulting_draft_revision`。
- V3.6-I 已实现 controlled operation payload schema、resulting draft validation、invalid rollback、remove_station edge guard、update_edge station reference guard，以及 UI-only / token / raw payload field rejection。
- V3.6-I 已固定 agent editing boundary：`actor_type=agent` 只能 propose/diff，即使具备 capability 也不能 apply；apply 必须由 user/system caller 执行。
- V3.6-I diff 返回 redacted summary、risk_flags 和 requires_approval；I 阶段不自动创建 approval、不进入 waiting_approval、不调用 `approval.respond`。
- V3.6-I 已实现 live EventBridge patch events：`workflow.patch.proposed`、`workflow.patch.applied`、`workflow.patch.rejected` 进入 workflow_patch channel。
- V3.6-I 不启动 WorkflowInstance、不创建 StationRun/Job/Artifact/QualityEvaluation、不触发 business.event、不修改 WorkflowContext、不修改 Board API 合同。
- V3.6-J 已实现平台中立 Dummy Pipeline E2E：create/publish/start/station/artifact lineage/approval/quality/board/business context/patch/publish V2/complete 全链路通过。
- V3.6-J Runtime E2E 与 Editing E2E 已分离：V1 completed instance 和 V1 `WorkflowVersion.snapshot` 不受 V2 patch/publish 影响；patched V2 instance 至少可运行一个 station。
- V3.6-J live SSE 覆盖 `approval.required`、`business.event.received`、`workflow.context.updated`、`workflow.patch.proposed`、`workflow.patch.applied`；`quality.evaluated` 仍为 trace-only，不作为 V3.6-J live EventBridge 出门条件。
- V3.6-J 已覆盖 `reference_app/demo_a/local` 与 `reference_app/demo_b/local` scope isolation、外部 `/v1/rpc` capability smoke、redaction 和 no business dependency。
- V3.6/V4.0 preflight hardening 第二轮已补齐 EventBridge 与 business event 原子性风险：`/v1/events/subscribe` follow mode 可轮询新增事件，不再只输出 heartbeat；subscription token 绑定 token allowed origins；business event idempotency marker 与 context update 原子应用，失败不会消耗 event_id；重复 `binding_id` 会返回稳定 `BUSINESS_EVENT_BINDING_INVALID`。
- 当前回归证据：V3.6 focused tests `86 passed`；V3.5 focused tests `146 passed`；full pytest `443 passed, 3 skipped`；TypeScript SDK `23 passed`；drawio XML validation passed。

当前缺口已经从：

```text
外部 App 如何接入 harnessOS Core
```

转为：

```text
接入后，业务流水线如何成为 harnessOS 的一等运行对象
```

## 3. 架构演进口径

V3.6 在整体架构中的位置是新的 **Workflow Runtime Layer**。它位于 V3.5 Application Adaptation Layer 与 Harness Core 之间：

```text
Plane-0 V4.0 Future UI
  Workflow Studio / AgentTalkWindow / Station Board / Quality Panel

Plane-1 V3.5 Application Adaptation Layer
  SDK / BFF / React Hooks / EventBridge / Embed Contract

Plane-2 V3.6 Workflow Runtime Layer
  Template / Version / Instance / Station / StationRun / Board / Patch / Quality / Context

Plane-3 Harness Core
  Session / Turn / Job / Artifact / Approval / Trace / Policy / Scope

Plane-4 Runtime Adapter & Governance
  execution boundary / policy / approval / secret hygiene / trace

Plane-5 Domain Packs
  domain workflows / skills / artifact kinds / policy bundles

Plane-6 Connectors / Tools / Stores
  MCP / stdio / HTTP connectors / local stores / external services
```

| 阶段 | 已解决 / 目标 | 对下一阶段的意义 |
| --- | --- | --- |
| V3.5 baseline | 外部 App 可以通过 SDK/BFF/hooks/EventBridge 接入 harnessOS。 | 为 V3.6 API 提供消费层。 |
| V3.6 target | Workflow runtime objects 成为一等对象。 | 为 V4.0 UI 提供后端事实源。 |
| V4.0 target | Workflow Studio / AgentTalkWindow / Station Board 消费 V3.6。 | 不再依赖 mock schema 或 UI 专用旁路。 |

V3.6 完成后，V4.0 正式 UI 调用链应为：

```text
Workflow Studio / AgentTalkWindow
  -> V3.5 SDK / BFF / Hooks / EventBridge
  -> V3.6 Workflow Runtime APIs
  -> Core Job / Artifact / Approval / Trace / Policy
  -> Pack / Connector
```

## 4. 目标状态

V3.6 完成后，harnessOS 应具备以下目标状态：

- WorkflowTemplate / WorkflowVersion 是可发布、可归档、可追踪的工作流模板事实源。
- WorkflowDraft 是可编辑草稿，修改 draft 不影响已发布版本。
- WorkflowInstance 表示一次工作流运行，并绑定 scope、session、thread、job、artifact、trace。
- Station / StationRun 成为一等对象，能表达每个工位的运行状态、输入、输出、失败、审批和质量结果。
- StationRun 可绑定 Job / Artifact / Trace，不再需要 UI 或业务层拼接这些关系。
- ArtifactContract 描述 station input/output 的 artifact kind、schema、preview policy、large file policy。
- Artifact lineage 能还原 station input/output 和 rerun 历史。
- Approval point 复用 `approval.respond`，进入 `waiting_approval` 后由 EventBridge 发出 `approval.required`。
- QualityEvaluation 可绑定 artifact / station_run，提供 score、issues、suggestions，并保持 rule/manual/llm_placeholder evaluator MVP、attach idempotency、redaction 和 no state mutation 边界。
- Pipeline Board API 可重建完整流水线看板，不依赖 UI 私有状态。
- Business event 可受控进入 workflow context，并写 trace / EventBridge event。
- WorkflowPatch 支持 Agent propose、diff、apply to draft、publish new version，但不能静默修改 published workflow。
- 平台中立 dummy pipeline E2E 能证明 V3.6 能力不依赖 Meeting / Knowledge / Video / external MCP。

## 5. 核心差距

| 差距 | 当前状态 | V3.6 目标 | 阶段 |
| --- | --- | --- | --- |
| Workflow contract | WorkflowTemplate / WorkflowVersion / WorkflowDraft 对象合同已冻结，template/draft/version service 已实现。 | 后续继续让 approval/quality/board/patch 消费同一 published version。 | V3.6-D 到 V3.6-I |
| Runtime instance | WorkflowInstance start/get/list/status/pause/resume/cancel/retry 已实现 MVP，approval 与 quality 侧向事实已可绑定。 | 后续接入 board、business context 和 patch。 | V3.6-G 到 V3.6-I |
| Station model | Station / WorkflowEdge / StationRun 对象合同已冻结，StationRun 已能运行并绑定 job/artifact/trace。 | 后续补 approval waiting、lineage、quality。 | V3.6-D/E/F |
| Job binding | StationRun.job_id 已对应真实 JobRecord，job metadata 记录 workflow/station refs。 | 后续让 board API 统一消费。 | V3.6-G |
| Artifact binding | V3.6-E 已实现 ArtifactContract、input/output bindings、namespaced metadata、parent lineage 和 rerun artifact history。 | 已被 QualityEvaluation MVP 消费；后续由 Board API 和 dummy pipeline E2E 继续消费。 | V3.6-E/F 已完成，V3.6-G/J 继续消费 |
| Approval point | 已实现 workflow-bound pre-execution approval point，`approval.respond` approve/reject 可推进或阻断 workflow，并带 side-effect recovery marker。 | 后续由 Board API 和 dummy pipeline E2E 消费审批状态。 | V3.6-D 已完成，V3.6-G/J 继续消费 |
| Quality evaluation | V3.6-F 已实现 QualityEvaluation MVP，支持 create/get/list/attach、rule/manual/llm_placeholder evaluator、auto_attach、scope validation、trace redaction 和 no runtime state mutation。 | 后续由 Board API 和 dummy pipeline E2E 消费，不在 F 阶段声明 live quality EventBridge streaming。 | V3.6-F 已完成，V3.6-G/J 继续消费 |
| Board API | V3.6-G 已实现 `workflow.board.get`、`workflow.instance.status`、`station.output.list`，用于聚合 station/job/artifact/approval/quality/trace summary。 | Board Data API ready；仍不等于 full pipeline operating model。 | V3.6-G 已完成 |
| Business event / Context | V3.6-H 已实现 `business.event.emit`、`business.event.bind`、`workflow.context.get/update`；只允许写 `context.business`，支持 idempotency、revision conflict、live EventBridge 和 redaction。 | Business Event Bridge / Workflow Context ready；后续 dummy pipeline E2E 继续消费。 | V3.6-H 已完成，V3.6-J 继续消费 |
| Patch contract | V3.6-I 已实现 propose/diff/apply/reject；patch 只能作用于 draft，agent 不能 apply，published version snapshot 不被修改。 | Safe workflow patch contract ready；后续 dummy pipeline E2E 继续消费。 | V3.6-I 已完成，V3.6-J 继续消费 |
| V4.0 gate | V3.6-J dummy pipeline E2E 与 preflight hardening 已通过，V3.6 可作为 V4.0 正式开发后端 gate。 | V4.0 具备进入正式开发计划的条件，但本轮仍暂停 V4.0-0 实施；仍不能声明 Workflow Studio / AgentTalkWindow ready。 | V3.6-J + preflight 已完成 |

## 6. 开发计划摘要

### 6.1 当前开发阶段

当前项目处于 **V3.6-J Dummy Pipeline E2E / V4.0 Gate 已完成** 的阶段。当前已经具备 deterministic dummy workflow runtime MVP、workflow-bound pre-execution approval gate、StationRun input/output artifact binding、QualityEvaluation MVP、Board Data API、可受控写入 `context.business` 的 business event/context layer、Safe Workflow Patch Contract，以及平台中立 dummy pipeline E2E。

这意味着 V3.6 已经达到 dev/local Workflow Runtime Contract & Pipeline Operating Model 出门标准，可以作为 V4.0 正式开发的后端 gate。它仍不是 V4.0 UI、完整 AgentTalkWindow、production workflow automation 或 distributed workflow engine。

当前已经完成的是：

- V3.6 文档目录已建立。
- V3.6 已被定位为 Workflow Runtime Contract & Pipeline Operating Model。
- V3.6 已明确位于 V3.5 Application Adaptation Layer 与 V4.0 Workflow Studio 之间。
- V3.6 已明确是 V4.0 正式开发 gate。
- V4.0 文档已同步：正式 UI 主开发必须以 V3.6-J gate 作为后端基线。
- V3.6 独立 contract inventory 已建立，所有 entry 标记 `family=workflow_runtime`、`introduced_in=V3.6`。
- V3.6 method schema 已建立；B 阶段 template/draft/version、C 阶段 runtime/station、F 阶段 quality methods、G 阶段 board/status/output methods、H 阶段 business/context methods、I 阶段 patch methods 均为 `runtime_handler=true`，并保持 `sdk_exposure=workflow_runtime`。
- V3.6 object schema 已由 `core/workflows/models.py` 驱动，所有对象均为 `schema_status=contract`、`stable_for_ui=false`。
- V3.6-A 合同测试已覆盖 inventory/schema consistency、SDK surface exclusion、event namespace、error uniqueness、dependency boundary、object roundtrip、edge 引用、draft/version immutability、StationRun binding、Patch draft-only、BusinessEvent namespace、UI/secret 字段阻断。
- V3.6-D 验证结果：`tests/test_v3_6_workflow_approval.py` 7 passed。
- V3.6-E 验证结果：`tests/test_v3_6_artifact_lineage_binding.py` 7 passed。
- V3.6-F 冻结验证结果：`tests/test_v3_6_quality_evaluation.py` 8 passed；阶段 focused 结果已被后续 V3.6 full focused 回归覆盖。
- 当前 V3.6/V4.0 preflight hardening 验证结果：V3.6 focused `86 passed`；V3.5 focused `146 passed`；full pytest `443 passed, 3 skipped`；TypeScript SDK `23 passed`；drawio XML validation passed。
- V3.6-G 验证入口：`tests/test_v3_6_pipeline_board_api.py`，覆盖 board/status/output summary、scope/capability、redaction 和 no business/patch creep。
- V3.6-H 验证入口：`tests/test_v3_6_business_event_bridge.py`，覆盖 concrete `business.*` event、context get/update、expected_revision conflict、binding apply、event idempotency、no approval/runtime bypass、EventBridge SSE、capability、redaction 和 no patch/quality/board mutation creep。
- V3.6-I 验证入口：`tests/test_v3_6_workflow_patch.py`，覆盖 patch state machine、repeated apply/reject、concurrent apply、stale conflict、invalid rollback、operation payload validation、agent apply denied、risk flags、EventBridge SSE、capability、redaction 和 no runtime creep。
- V3.6-J 验证入口：`tests/test_v3_6_dummy_pipeline_e2e.py`，覆盖 runtime E2E、business context E2E、patch E2E、scope isolation、external auth smoke、redaction 和 no dependency。
- V4.0 设计入口已同步到 V3.6-J 通过后的状态：`docs/design/V4.0/00_README.md` 和 `docs/design/V4.0/v4_target_architecture_workflow_console.md` 现在以 V3.5/V3.6 complete baseline 为正式开发起点。

当前需要继续推进的是：

- 基于 V3.6-J 后端 gate 进入 V4.0 Workflow Console / Studio / AgentTalkWindow 产品层开发计划。
- V4.0-0：Baseline & UI Contract Sync，锁定 UI 只能消费 V3.6 API。
- V4.0-A：Workflow Console Read-only MVP，消费 Board / status / station output / EventBridge。
- V4.0-B：Workflow Editing MVP，消费 WorkflowPatch / draft / publish 合同。
- V4.0-C：AgentTalkWindow Preparation，基于 Embed Contract、EventBridge、approval/context/patch 做前置 shell。
- V4.0-D：Quality / Approval / Context Panels，产品化质量、审批和上下文面板。
- V4.0-E：Reference Workflow Console E2E，用平台中立 workflow 验证 UI + BFF + SDK + V3.6 runtime。

### 6.2 阶段路线图

| 阶段 | 目标 | 主要交付 | 完成后可声明 |
| --- | --- | --- | --- |
| V3.6-0 | Baseline / Contract Inventory | 文档、目录、integration contract、V4.0 gate、独立 workflow inventory/schema draft、contract tests。 | V3.6 implementation ready。 |
| V3.6-A | Workflow Contract Schema | WorkflowTemplate、WorkflowVersion、WorkflowDraft、WorkflowInstance、Station、WorkflowEdge、StationRun、ArtifactContract、QualityContract、QualityEvaluation、WorkflowAction、WorkflowPatch、WorkflowContext、BusinessEvent、PipelineBoard contract models。 | Workflow contract schema ready。 |
| V3.6-B | Workflow Template / Draft / Version Service | template create/get/list/update_draft/publish/archive，draft.save，version get/list，revision/conflict，archive idempotency，trace redaction，capability tests。 | Versioned workflow template service ready。 |
| V3.6-C | Workflow Runtime MVP | instance start/get/list/status/pause/resume/cancel/retry，station run get/list/rerun，max_steps deterministic mode，两站 dummy workflow，真实 JobRecord 和最小 artifact metadata 绑定。 | Dummy workflow runtime MVP ready。 |
| V3.6-D | Approval Point / Policy Integration | pre-execution waiting_approval、approval.required EventBridge、approval.respond side-effect marker、approve/reject continuation、cancel inactive 和 late approval guard。 | Workflow approval point ready。 |
| V3.6-E | Artifact Contract / Lineage Binding | ArtifactContract 字段补强；StationRun input/output bindings；namespaced metadata；parent lineage；rerun artifact history；artifact.read policy regression。 | Station artifact contract and lineage binding ready。 |
| V3.6-F | Quality Evaluation MVP | `quality.evaluation.create/get/list/attach`；rule/manual/llm_placeholder evaluator；score/status validation；auto_attach；attach idempotency；scope validation；trace redaction；no workflow state mutation。 | Quality evaluation MVP ready。 |
| V3.6-G | Pipeline Board Data API | workflow.board.get，workflow.instance.status，station.output.list，station/job/artifact/approval/quality/trace summary，scope filtering，redaction，no quality mutation。 | Pipeline Board Data API ready。 |
| V3.6-H | Business Event Bridge / Workflow Context | business.event.emit，workflow.context.get/update，business.event.bind，context.business-only write，idempotency，revision conflict，EventBridge SSE，redaction。 | Business Event Bridge and Workflow Context ready。 |
| V3.6-I | Workflow Patch / Agent Editing Contract | patch propose/diff/apply/reject，draft-only apply，state machine，risk flags，agent apply denied，EventBridge patch events。 | Safe workflow patch contract ready。 |
| V3.6-J | Dummy Pipeline E2E / V4.0 Gate | create/publish/start/station/artifact/approval/quality/board/business/patch/complete 全链路。 | 已完成，V3.6 complete for V4.0 development。 |

### 6.3 V3.6-0 具体计划

V3.6-0 要完成的不是运行时功能，而是防止后续实现从口头约定开始。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| 文档目录 | 新增 `docs/design/V3.6/`。 | 已建立。 |
| 核心维护文件 | `v3_6_current_gap_analysis.md` 与同名 drawio 必须同步。 | 已建立，需后续持续同步。 |
| Integration contract | 新增 `docs/integration/workflow_runtime_contract.md`。 | 已建立。 |
| V4.0 gate | V4.0 文档明确正式开发依赖 V3.6-J。 | 已同步。 |
| Contract inventory | 后续建议补 `core/protocol/contracts/` 中 workflow/station/quality/patch method/event/error inventory。 | 已完成，位于独立 `workflow_*_inventory.py` 文件。 |
| Schema draft | 后续建议补 `core/protocol/schemas/` 中 workflow methods/events/objects/errors draft。 | 已完成；B methods 已转 implemented，其余 planned methods 仍 `runtime_handler=false`。 |
| Tests | 后续新增 `tests/test_v3_6_workflow_contract.py` 等入口。 | 已完成并扩展到 V3.6-J + preflight hardening；V3.6 focused 86 passed。 |

V3.6-0 完成后只能声明：

```text
V3.6 implementation ready
```

不能声明：

```text
workflow runtime ready
Workflow Studio ready
AgentTalkWindow ready
V3.6 complete
```

### 6.4 V3.6-A 具体计划与完成情况

V3.6-A 要完成的是对象合同冻结，不是 service 和 runtime handler。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Contract models | 新增 `core/workflows/models.py`，只定义协议合同，不访问 store、不注册 handler。 | 已完成。 |
| WorkflowEdge | `edge_id/from_station_id/to_station_id/condition/order/metadata`，edge station 引用必须存在。 | 已完成并有测试。 |
| Template/Draft/Version | Template 逻辑身份；Draft 可编辑；Version 不可变发布快照；Template 记录 latest draft/version 引用。 | 已完成并有测试。 |
| WorkflowInstance status | 增加 `waiting_approval`、`blocked`；blocked 与 failed 区分。 | 已完成。 |
| StationRun | 增加 attempt、rerun_of_station_run_id、failure_context、started_at、completed_at；可绑定 job/artifact/trace。 | 已完成并有测试。 |
| ArtifactContract | 只描述 station input/output 期望 artifact；不包含 raw content/path/storage backend。 | 已完成并有测试。 |
| Quality split | QualityContract 描述 rubric/evaluator policy；QualityEvaluation 描述某次结果；evaluator_type 为 rule/manual/llm_placeholder。 | 已完成并有测试。 |
| Action/Patch split | WorkflowAction 是 runtime 操作；WorkflowPatch 是 draft-only 结构变更。 | 已完成并有测试。 |
| BusinessEvent | 必须使用具体 `business.*` namespace；不新增 Meeting/Knowledge/Video canonical event。 | 已完成并有测试。 |
| PipelineBoard | 只返回 UI summary；不含 raw trace payload、token 或 raw connector failure。 | 已完成并有测试。 |
| Schema registry | `workflow_objects.py` 升级为 `schema_status=contract`、`stable_for_ui=false`。 | 已完成。 |

V3.6-A 完成后只能声明：

```text
V3.6-A complete: Workflow contract schema ready.
```

不能声明：

```text
workflow runtime ready
workflow template service ready
dummy workflow runnable
Pipeline Board API ready
V3.6 complete
V4.0 ready
```

### 6.5 V3.6-B 具体计划与完成情况

V3.6-B 要完成的是 template/draft/version service，不是 workflow runtime execution。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Store / Repository | 新增 WorkflowStore / WorkflowRepository，测试使用 InMemoryWorkflowStore。 | 已完成，B 阶段为 dev/local in-memory。 |
| Template uniqueness | `app_id/project_id/workspace_id/workflow_template_id` 范围唯一；跨 scope 同名允许。 | 已完成并有测试。 |
| Draft save | `update_draft` 按 template latest draft；`draft.save` 按 draft id。 | 已完成。 |
| Revision conflict | Draft revision 从 1 开始；expected_revision stale 返回 `WORKFLOW_DRAFT_CONFLICT`。 | 已完成并有并发测试。 |
| Publish | publish 必须显式传 version；重复 version 返回 `WORKFLOW_VERSION_CONFLICT`；snapshot deep-copy immutable。 | 已完成并有测试。 |
| Published draft | 被发布 draft 标记为 published，不可编辑；后续 update_draft fork 新 editable draft。 | 已完成并有测试。 |
| Archive | archive idempotent；默认 list 不含 archived；include_archived 才返回；archived 禁止 update/publish。 | 已完成并有测试。 |
| Method metadata | B methods `implemented/runtime_handler=true/sdk_exposure=workflow_runtime`；后续 runtime methods 仍 planned。 | 已完成并有测试。 |
| Capability mapping | read/write/publish 分别要求 workflows.read/workflows.write/workflow_versions.publish。 | 已完成并有外部 auth 测试。 |
| Trace redaction | create/update/save/publish/archive 写 trace，trace 不暴露 token-like 字段。 | 已完成并有测试。 |
| No runtime execution | publish 不创建 WorkflowInstance/StationRun/Job/Artifact/Approval。 | 已完成并有测试。 |

V3.6-B 完成后只能声明：

```text
V3.6-B complete: Versioned workflow template service ready.
```

不能声明：

```text
workflow runtime ready
dummy workflow runnable
Pipeline Board API ready
V3.6 complete
V4.0 ready
```

### 6.6 V3.6-C 具体计划与完成情况

V3.6-C 要完成的是 deterministic dummy workflow runtime MVP，不是完整 Pipeline Operating Model。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Published version source | `workflow.instance.start` 必须基于 `WorkflowVersion.snapshot`，不能读取 current draft。 | 已完成并有测试。 |
| Deterministic execution | 支持 `max_steps`；`max_steps=1` 只执行一个 station，保留中间态。 | 已完成并有测试。 |
| Instance lifecycle | 支持 start/get/list/status/pause/resume/cancel/retry。 | 已完成；retry 为最小边界。 |
| State machine | pause only running；resume only paused；cancel created/running/paused；cancelled idempotent；completed cancel 返回 `WORKFLOW_INVALID_STATE`。 | 已完成并有测试。 |
| StationRun | 支持 get/list/rerun；rerun 新建 StationRun，attempt+1，记录 rerun_of_station_run_id。 | 已完成并有测试。 |
| Job binding | StationRun.job_id 对应真实 JobRecord；job metadata 包含 workflow/station refs。 | 已完成并有 job.get 测试。 |
| Minimal artifact metadata | station output 注册为 metadata-only artifact；Station B input_artifact_ids 消费 Station A output。 | 已完成并有 artifact.read_metadata 测试。 |
| Unsupported graph | C 阶段只支持线性 workflow；branch/cycle/condition 返回 `WORKFLOW_RUNTIME_UNSUPPORTED`。 | 已完成并有测试。 |
| Capability mapping | workflows.read/workflows.execute/stations.read/stations.execute 分别控制对应方法。 | 已完成并有外部 auth 测试。 |
| No runtime creep | 不触发 approval、quality、board、business event、patch。 | 已完成并有测试。 |

V3.6-C 完成后只能声明：

```text
V3.6-C complete: Dummy workflow runtime MVP ready.
```

不能声明：

```text
approval point ready
artifact lineage binding complete
quality evaluation ready
Pipeline Board API ready
V3.6 complete
V4.0 ready
```

### 6.7 V3.6-D 具体计划与完成情况

V3.6-D 要完成的是 workflow approval point，不是 artifact lineage、quality、board、business event 或 patch。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Pre-execution approval | `approval_required=true` station 在 approval 前只创建 `StationRun(status=waiting_approval)` 和 approval request；不得创建 Job/Artifact，不得执行 downstream station。 | 已完成并有测试。 |
| Workflow binding | approval metadata 必须包含 `workflow_binding`：workflow_instance_id、station_run_id、station_id、workflow_template_id、workflow_version_id、resume_strategy、reject_strategy、active、side-effect marker。 | 已完成并有测试。 |
| `approval.respond` continuation | standalone approval 保持 V3.5 行为；只有存在 `workflow_binding` 时触发 workflow side effect。 | 已完成并有测试。 |
| Side-effect marker | `workflow_side_effect_status=pending/applying/applied/failed`，pending/failed -> applying 需要原子保护，approved decision 缺失 side effect 可恢复。 | 已完成并有 recovery / concurrency 测试。 |
| Approve behavior | approve 后才执行当前 station，填充 job_id，生成 station output artifact；auto mode 可继续到下一个 wait point / completion，step mode 不无条件跑完整 workflow。 | 已完成并有测试。 |
| Reject behavior | MVP 默认 reject strategy：WorkflowInstance.status=blocked，StationRun.status=failed，failure_context.reason=approval_rejected。 | 已完成并有测试。 |
| Cancel waiting approval | cancel waiting workflow 后 WorkflowInstance/StationRun 变 cancelled，approval binding active=false，late approval 返回 `WORKFLOW_APPROVAL_INACTIVE` 且不改写 approval status。 | 已完成并有测试。 |
| EventBridge | approval.required 可通过 approval channel 观察，event.data.workflow_binding 携带 workflow refs。 | 已完成并有 SSE schema 测试。 |
| Capability | workflow-bound `approval.respond` 仍只要求 approvals capability；不额外要求 workflows.execute；scope mismatch 返回 SCOPE_MISMATCH。 | 已完成并有外部 auth 测试。 |
| Secret hygiene | approval metadata、reason、failure_context、trace、event data 不泄露 bearer/subscription token、Authorization、secret、raw connector payload。 | 已完成并有测试。 |
| No runtime creep | 不创建 QualityEvaluation；不实现 board/business/patch；不声明 artifact lineage complete；不新增 approval.approve/reject 默认入口。 | 已完成并有测试。 |

V3.6-D 完成后只能声明：

```text
V3.6-D complete: Workflow approval point ready.
```

不能声明：

```text
artifact lineage complete
quality evaluation ready
Pipeline Board API ready
business event ready
workflow patch ready
V3.6 complete
V4.0 ready
```

### 6.8 V3.6-E 具体计划与完成情况

V3.6-E 要完成的是 Station artifact contract / lineage binding，不是 QualityEvaluation、Pipeline Board API、business event 或 workflow patch。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| ArtifactContract 字段 | 增加 `contract_id`、`cardinality`、`kind_match_policy`；同一 station 内 contract_id 唯一，重复返回 `WORKFLOW_ARTIFACT_CONTRACT_INVALID`；不同 station 可复用同名 contract_id。 | 已完成并有测试。 |
| Contract 边界 | ArtifactContract 只描述 station input/output 期望 artifact，不包含 raw content、local path、storage backend、token、Authorization、raw trace payload。 | 已完成并有对象合同测试。 |
| Binding 结构 | StationRun 增加 `input_bindings` / `output_bindings`，扁平 artifact ids 作为 bindings 的索引视图。 | 已完成并有一致性测试。 |
| Metadata namespace | 系统字段放入 `metadata.workflow`、`metadata.artifact_contract`、`metadata.lineage`；用户 metadata 放入 `metadata.user`，不得覆盖系统 namespace。 | 已完成并有覆盖测试。 |
| Kind match policy | MVP 支持 `exact`，要求 `artifact.kind == contract.artifact_kind`；kind mismatch 返回 `WORKFLOW_ARTIFACT_KIND_MISMATCH`；`compatible` 不作为默认 fallback。 | 已完成并有测试。 |
| Input validation MVP | 只验证 exists、scope、artifact kind、required binding、schema_ref/metadata；不调用 `artifact.read`。 | 已完成并有 no-read / missing / kind mismatch / cross-scope 测试。 |
| Parent IDs | output artifact parent_ids 来自 input bindings，按 first-seen order 去重；parent artifact 必须同 scope。 | 已完成并有 lineage 测试。 |
| Rerun history | `station.rerun` 生成新 artifact，不覆盖旧 artifact；`attempt` / `rerun_of_station_run_id` 记录在 `metadata.workflow`；默认不产生旧 output -> 新 output 的 false parent edge。 | 已完成并有测试。 |
| Connector result 边界 | connector_result 只能作为额外 evidence/lineage node，不能替代 station output artifact，除非 output contract 明确允许该 kind。 | 已完成边界测试；E 阶段未引入 connector runtime。 |
| Atomicity / failure | artifact registration 失败时返回 `WORKFLOW_ARTIFACT_REGISTRATION_FAILED`，StationRun 不标记 completed，Job 置 failed，failure_context redacted。 | 已完成并有 failure simulation 测试。 |
| Artifact read policy | V3.6-E 不改变 `artifact.read` blocking policy；metadata/read_metadata 是默认消费方式。 | 已完成 media/binary/external-only/large regression。 |
| SDK / method surface | 不新增 Python/TypeScript SDK default wrappers；不新增 workflow-specific lineage RPC；继续复用 `artifact.lineage`。 | 已完成并有回归。 |
| No runtime creep | 不创建 QualityEvaluation；不实现 board/business/patch；不依赖 Meeting/Knowledge/Video/data_service/voice_service/funasr/external MCP；不新增 workflow lineage RPC。 | 已完成并有测试。 |

V3.6-E 完成后只能声明：

```text
V3.6-E complete: Station artifact contract and lineage binding ready.
```

不能声明：

```text
quality evaluation ready
Pipeline Board API ready
business event ready
workflow patch ready
V3.6 complete
V4.0 ready
```

### 6.9 V3.6-F 具体计划与完成情况

V3.6-F 要完成的是 Quality Evaluation MVP，不是 Pipeline Board API、business event、workflow patch 或 full pipeline operating model。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| QualityContract / QualityEvaluation binding | QualityContract 描述 rubric/evaluator policy；QualityEvaluation 描述某次评估结果；rule evaluator 必须追溯 QualityContract / rubric_id。 | 已完成并有测试；missing rubric 返回 `QUALITY_EVALUATION_INVALID`。 |
| Evaluator boundary | rule/manual/llm_placeholder 可用；llm_placeholder 只记录 evaluator_type，不调用真实 LLM。 | 已完成并有 no external call 边界测试。 |
| Score / status validation | score 必须在 0.0 到 1.0；rule evaluator 根据 threshold 计算 passed/failed；manual evaluator 可显式提交 status。 | 已完成并有 invalid score/status 测试。 |
| Attach semantics | create 支持 `auto_attach`；attach 同一 target idempotent；改绑不同 target 返回 `QUALITY_EVALUATION_ALREADY_ATTACHED`。 | 已完成并有测试。 |
| Binding validation | workflow instance、station run、artifact 必须存在且同 scope；artifact 默认属于 station output；input artifact evaluation 需要 `allow_input_artifact=true`。 | 已完成并有 scope / not found / input artifact 测试。 |
| No content read | evaluator 只使用 metadata、supplied score、issue count 和 rubric threshold；不调用 `artifact.read`。 | 已完成并有 monkeypatch 防读测试。 |
| No workflow state mutation | failed evaluation 不改变 WorkflowInstance.status 或 StationRun.status，不触发 approval/rerun/board/business/patch。 | 已完成并有 no runtime creep 测试。 |
| Trace / record redaction | QualityEvaluation record、trace、issues、suggestions、metadata 不泄露 token、Authorization、secret、raw artifact content。 | 已完成并有测试。 |
| Method metadata / capability | quality methods 为 `implemented/runtime_handler=true/sdk_exposure=workflow_runtime`；read/write capability 分别控制 get/list 与 create/attach。 | 已完成并有 external auth 测试。 |
| Event boundary | quality.evaluation.created / attached 在 F 阶段只写 trace，不声明 live quality EventBridge streaming ready。 | 已固定为文档边界。 |
| SDK surface | 不新增 Python/TypeScript SDK default wrappers。 | 已完成并有合同测试。 |

V3.6-F 完成后只能声明：

```text
V3.6-F complete: Quality evaluation MVP ready.
```

不能声明：

```text
Pipeline Board API ready
business event ready
workflow patch ready
V3.6 complete
V4.0 ready
```

### 6.10 V3.6-G 具体计划与完成情况

V3.6-G 完成的是 Pipeline Board Data API，不是 business event、workflow patch、dummy pipeline E2E 或完整 V4.0 UI backend。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| `workflow.board.get` | 返回 workflow instance、station、station run、job、artifact、approval、quality、trace summary。 | 已完成并有 `tests/test_v3_6_pipeline_board_api.py` 覆盖。 |
| `workflow.instance.status` | 返回 instance status、current_station_ids、station/job/artifact/quality count 与 status counts。 | 已完成。 |
| `station.output.list` | 返回指定 station 或 station_run 的 output artifact summary。 | 已完成。 |
| Scope filtering | board/status/output 都必须按 app/project/workspace scope 校验。 | 已完成，external `/v1/rpc` capability/scope tests 覆盖。 |
| Capability | `workflow.board.get` 需要 `board.read`；`station.output.list` 需要 `stations.read`；`workflow.instance.status` 需要 `workflows.read`。 | 已完成。 |
| Redaction | 不返回 raw trace payload、raw artifact content、token、subscription token、Authorization 或 raw connector payload。 | 已完成。 |
| Quality boundary | Board API 只消费 V3.6-F QualityEvaluation，不修改 evaluation，不触发 evaluator。 | 已完成。 |
| No runtime creep | 不实现 business.event.*，不实现 workflow.patch.*，不声明 live quality streaming。 | 已完成并有测试。 |

V3.6-G 完成后只能声明：

```text
V3.6-G complete: Pipeline Board Data API ready.
```

不能声明：

```text
business event ready
workflow patch ready
dummy pipeline E2E ready
V3.6 complete
V4.0 ready
```

### 6.11 V3.6-H 具体计划与完成情况

V3.6-H 完成的是 Business Event Bridge / Workflow Context，不是 workflow patch、dummy pipeline E2E 或完整 Workflow Studio backend。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| WorkflowContext 分区 | context 分为 `system`、`business`、`runtime`、`metadata`；外部 update / business event binding 只能写 `context.business`。 | 已完成并有测试。 |
| Context update 语义 | MVP 支持 shallow merge 与 optional path set；`path` 必须位于 `context.business.*`；不允许修改 workflow/station/approval 状态。 | 已完成并有 runtime bypass 测试。 |
| Revision / conflict | `workflow.context.update` 支持 `expected_revision`；stale revision 返回 `WORKFLOW_CONTEXT_CONFLICT`。 | 已完成。 |
| BusinessEventBinding | `binding_id`、`workflow_instance_id`、`event_type`、`target_path`、`payload_path`、`mode`、`enabled`；MVP 仅支持 `mode=set`。 | 已完成并有 binding validation 测试。 |
| Business event namespace | `business.event.emit` 只接受具体 `business.*` 类型；拒绝 `business.*` wildcard、`meeting.*`、`knowledge.*`、`video.*` 作为 core canonical event。 | 已完成并有测试。 |
| Idempotency | `business.event.emit` 支持 `event_id` / `idempotency_key`；重复 event 不重复应用 context update。 | 已完成并有测试。 |
| EventBridge | `business.event.received` 进入 business channel；`workflow.context.updated` 进入 workflow_context channel；event data 带 workflow_instance_id 和 context_revision。 | 已完成并有 SSE schema 测试。 |
| Capability / scope | `business.event.emit` 需要 `business_events.write`；`business.event.bind` 与 `workflow.context.update` 需要 `workflow_context.write`；`workflow.context.get` 需要 `workflow_context.read`；cross-scope 返回 `SCOPE_MISMATCH`。 | 已完成并有 external `/v1/rpc` 测试。 |
| Redaction | context values、business event payload、trace、EventBridge data 不泄露 capability token、subscription token、Authorization、secret、raw trace payload、raw connector payload 或 raw artifact content。 | 已完成并有测试。 |
| Board boundary | H 阶段不修改 `workflow.board.get` response shape；context 读取入口是 `workflow.context.get`。 | 已完成并有 no board mutation creep 测试。 |
| No runtime creep | 不实现 workflow.patch，不创建 QualityEvaluation，不实现 dummy pipeline E2E，不依赖 Meeting/Knowledge/Video/data_service/voice_service/funasr/external MCP。 | 已完成并有测试。 |

V3.6-H 完成后只能声明：

```text
V3.6-H complete: Business Event Bridge and Workflow Context ready.
```

不能声明：

```text
workflow patch ready
dummy pipeline E2E ready
V3.6 complete
V4.0 ready
Workflow Studio ready
AgentTalkWindow ready
```

### 6.12 V3.6-I 具体计划与完成情况

V3.6-I 完成的是 Safe Workflow Patch Contract，不是 dummy pipeline E2E、完整 Workflow Studio 或 AgentTalkWindow。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| Patch 状态机 | `proposed -> applied`、`proposed -> rejected`；repeated same action idempotent；conflicting action 返回 `WORKFLOW_PATCH_CONFLICT`。 | 已完成并有测试。 |
| Draft / revision binding | patch 记录 template、draft、base_revision、base_version_id、operation、actor；apply 校验 current draft revision 等于 base_revision，MVP 不做 rebase。 | 已完成并有 stale conflict 测试。 |
| Atomic apply | draft payload、draft revision、patch status、applied/resulting revision 在 WorkflowStore lock 内更新，避免 draft/patch 不一致。 | 已完成并有 concurrent apply single mutation 测试。 |
| Controlled payload schema | 不允许 arbitrary JSON patch；每个 operation 有受控 payload schema；unknown fields、UI-only fields、token/raw payload fields 被拒绝。 | 已完成并有测试。 |
| Resulting draft validation | apply 后重新 validate WorkflowTemplate、Station、WorkflowEdge、ArtifactContract、QualityContract；invalid result rollback，patch 不标 applied。 | 已完成并有 invalid rollback 测试。 |
| Draft-only / published immutable | apply 只修改 WorkflowDraft.draft，不修改 WorkflowVersion.snapshot；published draft apply 返回 `WORKFLOW_PUBLISHED_IMMUTABLE`；archived template 返回 `WORKFLOW_TEMPLATE_ARCHIVED`。 | 已完成并有测试。 |
| Agent boundary | `actor_type=agent` 只能 propose/diff，不能 apply；agent 即使有 capability 也返回 `WORKFLOW_ACTION_FORBIDDEN`。 | 已完成并有测试。 |
| Risk flags | diff 返回 `risk_flags` 和 `requires_approval`；高风险操作只标记风险，不自动创建 approval，不进入 waiting_approval。 | 已完成并有 no approval test。 |
| EventBridge | `workflow.patch.proposed/applied/rejected` 进入 workflow_patch channel，event data 带 template/draft/patch/operation/status/revision/risk refs。 | 已完成并有 SSE schema 测试。 |
| Capability / scope | propose/apply/reject 需要 `workflow_patches.write`，diff 需要 `workflow_patches.read`；cross-scope 返回 `SCOPE_MISMATCH`。 | 已完成并有 external auth 测试。 |
| No runtime creep | 不启动 WorkflowInstance，不创建 StationRun/Job/Artifact/QualityEvaluation，不触发 business.event，不修改 WorkflowContext，不修改 Board API。 | 已完成并有测试。 |

V3.6-I 完成后只能声明：

```text
V3.6-I complete: Safe workflow patch contract ready.
```

不能声明：

```text
dummy pipeline E2E ready
V3.6 complete
V4.0 ready
Workflow Studio ready
AgentTalkWindow ready
production workflow automation ready
```

### 6.13 V3.6-J 具体计划与完成情况

V3.6-J 完成的是 Dummy Pipeline E2E / V4.0 Gate。它不新增新的 patch、board、quality、business event 单点能力，而是通过 Gateway RPC / `/v1/rpc` 消费 V3.6-A 到 V3.6-I 已完成能力，证明 workflow runtime 可以作为 V4.0 正式开发的后端事实源。

| 开发点 | 要求 | 当前状态 |
| --- | --- | --- |
| 前置条件 | 只能在 V3.6-I Safe Workflow Patch Contract ready 后启动；J 阶段是最终 gate，不继续补单点功能。 | 已满足。 |
| Runtime E2E | create template -> publish V1 -> start instance -> station A/B/C -> artifact lineage -> approval.respond -> quality -> board -> business context -> workflow completed。 | 已完成并有测试。 |
| Editing E2E | workflow.patch.propose -> diff -> apply to draft -> publish V2。 | 已完成并有测试。 |
| Version immutability | patch apply / publish V2 不改变已完成的 V1 workflow instance；V1 `WorkflowVersion.snapshot` 保持不变。 | 已完成并有测试。 |
| Patched V2 runtime | patched V2 instance 至少跑一个 station，证明 patch 产出的新 version 可被 runtime 消费。 | 已完成并有测试。 |
| EventBridge | live SSE 覆盖 `approval.required`、`business.event.received`、`workflow.context.updated`、`workflow.patch.proposed`、`workflow.patch.applied`。 | 已完成并有测试。 |
| Quality event boundary | `quality.evaluated` 仍为 trace-only，不作为 V3.6-J live EventBridge 出门条件。 | 已固定在 completion note。 |
| Board reconstruction | `workflow.board.get` 可重建 workflow_instance、stations、station_runs、jobs、artifacts、approvals、quality_evaluations、trace_summary、current_station_ids。 | 已完成并有测试。 |
| Scope isolation | 覆盖 `reference_app/demo_a/local` 与 `reference_app/demo_b/local`；cross-scope input/context/business/patch 均返回 `SCOPE_MISMATCH`。 | 已完成并有测试。 |
| External auth smoke | 最小 `/v1/rpc` capability smoke 覆盖代表性 read/write allow/deny。 | 已完成并有测试。 |
| No business dependency / UI creep | dummy pipeline 不依赖 Meeting / Knowledge / Video / data_service / voice_service / funasr / external MCP；不新增 UI-only backend API。 | 已完成并有测试。 |
| Redaction | trace/event/board/quality/failure_context/patch diff/expected fixture 不泄露 token、Authorization、secret、raw trace、raw connector、raw artifact content。 | 已完成并有测试。 |

V3.6-J 完成后可以声明：

```text
V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development.
```

仍不能声明：

```text
V4.0 complete
Workflow Studio ready
AgentTalkWindow ready
production workflow automation ready
distributed workflow engine ready
```

## 7. 规划接口与对象影响范围

### 7.1 对象合同

V3.6 需要冻结以下对象：

- WorkflowTemplate
- WorkflowVersion
- WorkflowDraft
- WorkflowInstance
- Station
- StationRun
- ArtifactContract
- QualityContract
- QualityEvaluation
- WorkflowAction
- WorkflowPatch

这些对象必须遵守：

- 有 scope 或可通过 workflow instance 追溯 scope。
- 不依赖 Meeting / Knowledge / Video 业务字段。
- 不包含 UI layout 私有状态。
- 不包含 token、subscription token 或 raw trace payload。

### 7.2 RPC 合同

V3.6 规划新增或冻结以下 RPC 面：

```text
workflow.template.create
workflow.template.get
workflow.template.list
workflow.template.update_draft
workflow.template.publish
workflow.template.archive
workflow.version.get
workflow.version.list
workflow.instance.start
workflow.instance.get
workflow.instance.list
workflow.instance.pause
workflow.instance.resume
workflow.instance.cancel
workflow.instance.retry
station.run.get
station.run.list
station.rerun
workflow.board.get
workflow.instance.status
station.output.list
quality.evaluation.create
quality.evaluation.get
quality.evaluation.list
quality.evaluation.attach
business.event.emit
workflow.context.get
workflow.context.update
business.event.bind
workflow.patch.propose
workflow.patch.diff
workflow.patch.apply
workflow.draft.save
workflow.patch.reject
```

发布语义统一由 `workflow.template.publish` 承担；`workflow.version.get/list` 只读版本历史，不新增 `workflow.version.publish`。

这些 RPC 必须进入 method inventory、schema registry、capability resolver 和 SDK/BFF surface 评估。已实现阶段只进入 `sdk_exposure=workflow_runtime`，不进入 V3.5 Python/TypeScript SDK default wrappers。

### 7.3 事件合同

V3.6 应新增 workflow / station / quality / patch / context 事件：

```text
workflow.template.created
workflow.template.published
workflow.instance.started
workflow.instance.paused
workflow.instance.resumed
workflow.instance.completed
workflow.instance.failed
workflow.instance.cancelled
station.run.started
station.run.waiting_approval
station.run.completed
station.run.failed
station.run.rerun_requested
quality.evaluated
workflow.patch.proposed
workflow.patch.applied
workflow.patch.rejected
workflow.context.updated
business.event.received
```

事件规则：

- 所有事件必须有 scope。
- station 事件必须有 workflow_instance_id 和 station_run_id。
- quality 事件必须能追溯 artifact_id 或 station_run_id。
- patch 事件必须能追溯 workflow_template_id / draft / trace。
- business event 只使用 `business.*` namespace，不新增 Meeting/Knowledge/Video canonical event。

## 8. P0 Blockers Before Formal V4.0

V3.6-J 已关闭 V4.0 正式开发前的后端 gate。进入 V4.0 前仍需把以下内容作为启动检查，而不是 V3.6 阻塞项：

- 使用 `v3_6_j_completion_note.md` 作为 V3.6 baseline evidence。
- 保持 V3.5 focused regression、V3.6 focused regression、full pytest、TypeScript SDK tests 全绿。
- V4.0 不得把 UI mock schema 固化为协议，也不得新增绕过 V3.6 API 的 UI 专用后端旁路。

## 9. P1 Improvements

以下问题可以与 V3.6 主线并行推进，但不应阻塞 V3.6-0/A 的启动：

- 为 workflow runtime methods 增加 SDK snapshot 和 TS/Python wrapper 规划。
- 为 board API 增加 frontend-oriented sample response fixture。
- 为 quality evaluator 预留 LLM evaluator plugin shape，但不实现真实 LLM evaluator。
- 为 business events 增加 pack-declared namespace 示例。
- 为 workflow patch 增加 diff 可视化 fixture。
- 为 V4.0 UI Spike 增加 mock-to-real contract 对齐检查。

## 10. 测试与验收入口

后续实现阶段必须新增或等价覆盖：

```text
tests/test_v3_6_workflow_contract.py
tests/test_v3_6_workflow_template_service.py
tests/test_v3_6_workflow_runtime.py
tests/test_v3_6_workflow_runtime.py
tests/test_v3_6_workflow_approval.py
tests/test_v3_6_artifact_lineage_binding.py
tests/test_v3_6_quality_evaluation.py
tests/test_v3_6_pipeline_board_api.py
tests/test_v3_6_business_event_bridge.py
tests/test_v3_6_workflow_patch.py
tests/test_v3_6_dummy_pipeline_e2e.py
```

回归命令：

```bash
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
```

V3.6-J 已通过；后续 V4.0 UI demo、mock board、mock AgentTalkWindow 仍必须消费或对齐 V3.6 API，不能新增 UI 专用后端旁路。

## 11. Non-Goals

V3.6 不做：

- 完整 Workflow Studio UI。
- 完整 AgentTalkWindow。
- 复杂低代码画布。
- Video Studio 真实业务流。
- Interview / Investment 正式业务扩展。
- Core 大重构。
- 分布式 workflow engine。
- production workflow automation。
- production multi-tenant control plane。
- enterprise auth/OAuth/SSO。

## 12. V4.0 Gate

V3.6-J 与 preflight hardening 已通过，项目具备进入 V4.0 主开发计划的后端条件；但本轮仍暂停 V4.0-0 实施，后续必须由明确任务启动。V4.0 主开发必须继续以以下 V3.6 后端事实源为 gate：

```text
WorkflowTemplate / WorkflowVersion
WorkflowInstance / Station / StationRun
Board API / Patch / Business Event / Quality Evaluation
Approval Point / Artifact Lineage / Dummy Pipeline E2E
```

V3.6-J 通过后仍允许 Spike，但 Spike 不再替代正式 V3.6 API：

```text
V4.0 UI Spike
```

Spike 允许：

- Workflow Studio wireframe。
- AgentTalkWindow shell。
- Station Board mock。
- Artifact Board mock。
- Quality Panel mock。
- Business Event mock。

Spike 禁止：

- 固化 mock schema 为正式协议。
- 新增 UI 专用后端旁路。
- 绕过 V3.6 API。
- 声明 Workflow Studio ready。
- 声明 AgentTalkWindow ready。

## 13. 出门声明

V3.6 完成后可以声明：

```text
V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development.
```

仍不能声明：

```text
V4.0 complete
Workflow Studio ready
AgentTalkWindow ready
production workflow automation ready
distributed workflow engine ready
```
