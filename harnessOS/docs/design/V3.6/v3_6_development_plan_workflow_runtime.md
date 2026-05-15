# V3.6 Workflow Runtime Development Plan

文档状态：V3.6 complete baseline 已冻结；V3.6/V4.0 preflight hardening complete。  
执行范围：本计划用于后续代码实施；V3.6-0 已创建 contract inventory 和 schema draft，V3.6-A 已冻结 workflow object contract models，V3.6-B 已实现 template/draft/version service，V3.6-C 已实现 deterministic dummy workflow runtime MVP，V3.6-D 已实现 workflow-bound pre-execution approval point，V3.6-E 已实现 Station artifact contract / lineage binding，V3.6-F 已实现 QualityEvaluation MVP，V3.6-G 已实现 Pipeline Board Data API，V3.6-H 已实现 Business Event Bridge / Workflow Context，V3.6-I 已实现 Safe Workflow Patch Contract，V3.6-J 已实现 Dummy Pipeline E2E / V4.0 Gate；V3.6/V4.0 preflight hardening 已补齐 V4.0-0 前必须修复的 scope/capability/governance/EventBridge follow/subscription origin/business event atomicity/startup neutrality/doc alignment 风险。

## 1. Goal

V3.6 的目标是建立 **Workflow Runtime Contract & Pipeline Operating Model**，让“工作流流水线”成为 harnessOS 可运行、可追踪、可审批、可评价、可被 UI 消费的一等对象。

V3.6 解决的问题是：

```text
外部业务 App 接入 harnessOS 后，如何定义、运行、追踪、重跑、评价和修改一个业务流水线工作流。
```

## 2. Scope

包含：

- WorkflowTemplate / WorkflowVersion / WorkflowDraft。
- WorkflowInstance 生命周期。
- Station / StationRun。
- ArtifactContract / QualityContract / QualityEvaluation。
- Approval point / Policy integration。
- Pipeline Board Data API。
- Business Event Bridge / Workflow Context。
- WorkflowPatch / Agent editing contract。
- Platform-neutral dummy pipeline E2E。

不包含：

- 完整 Workflow Studio UI。
- 完整 AgentTalkWindow。
- 复杂低代码画布。
- Video Studio 真实业务工作流。
- Interview / Investment 正式业务扩展。
- Core 大重构。
- 分布式 workflow engine。

## 3. Impacted Files And Future Directories

文档阶段新增或更新：

- `docs/design/V3.6/00_README.md`
- `docs/design/V3.6/v3_6_starting_baseline.md`
- `docs/design/V3.6/v3_6_architecture_baseline.md`
- `docs/design/V3.6/v3_6_current_gap_analysis.md`
- `docs/design/V3.6/v3_6_current_gap_analysis.drawio`
- `docs/design/V3.6/v3_6_development_plan_workflow_runtime.md`
- `docs/design/V3.6/v3_6_workflow_contract.md`
- `docs/design/V3.6/v3_6_acceptance_plan.md`
- `docs/design/V3.6/v3_6_project_introduction_baseline.md`
- `docs/integration/workflow_runtime_contract.md`

后续代码实施建议目录：

```text
core/workflows/
  models.py              # V3.6-A complete
  store.py               # V3.6-B complete
  templates.py           # V3.6-B Gateway service methods live in apps/gateway/service.py
  instances.py
  stations.py
  actions.py
  patches.py
  board.py
  quality.py
  events.py
```

后续协议实施可能涉及：

- `apps/gateway/service.py`
- `apps/gateway/rpc_router.py`
- `core/protocol/contracts/`
- `core/protocol/schemas/`
- `sdk/python/harnessos_client/`
- `sdk/typescript/`
- `templates/bff/`
- `examples/reference_app/`

## 4. Phase Plan And PR Slices

### V3.6-0 Baseline / Contract Inventory

状态：已完成 targeted implementation and focused regression。

PR slices：

- `V3.6-0-PR1`：新增 V3.6 文档集和 current gap drawio。
- `V3.6-0-PR2`：新增 `docs/integration/workflow_runtime_contract.md`。
- `V3.6-0-PR3`：同步 V4.0 文档中的 V3.6 gate 说明。
- `V3.6-0-PR4`：新增独立 workflow runtime contract inventory。
- `V3.6-0-PR5`：新增 workflow methods/events/objects/errors schema draft。
- `V3.6-0-PR6`：新增 `tests/test_v3_6_workflow_contract.py`。

验收：

- V3.6 文档存在并与 V3.5 风格一致。
- 明确 V3.6 不等于 V4.0 UI。
- 明确 V3.6 基于 V3.5 适配层，不回写 V3.5。
- V3.6 planned methods/events/errors 位于独立 `workflow_*` inventory namespace。
- V3.6 method schema draft 均为 `runtime_handler=false`，不进入默认 callable surface。
- V3.6-0 object schema draft 在 V3.6-A 已升级为 `schema_status=contract`、`stable_for_ui=false`。
- 默认全量测试继续绿灯。
- V3.5 focused tests 继续绿灯。

### V3.6-A Workflow Contract Schema

PR slices：

- `V3.6-A-PR1`：新增 `core/workflows/models.py` workflow runtime contract models。
- `V3.6-A-PR2`：将 `workflow_objects.py` 从 draft object schema 升级为模型驱动 contract schema。
- `V3.6-A-PR3`：新增 schema/object behavior contract tests。

验收：

- WorkflowTemplate / WorkflowVersion / WorkflowDraft / WorkflowInstance schema 可测试。
- WorkflowEdge 可测试，且 edge 引用的 station_id 必须存在。
- Station / StationRun / ArtifactContract / QualityContract / QualityEvaluation schema 可测试。
- WorkflowAction / WorkflowPatch schema 可测试。
- WorkflowTemplate 是逻辑身份；WorkflowDraft 是可编辑草稿；WorkflowVersion 是不可变发布快照。
- WorkflowInstance status 包含 `waiting_approval` 和 `blocked`；`blocked` 表示可人工处理，`failed` 表示执行失败。
- StationRun 包含 `attempt`、`rerun_of_station_run_id`、`failure_context`、`started_at`、`completed_at`，并可绑定 job/artifact/trace。
- ArtifactContract 只描述 station input/output 期望 artifact，不包含 raw content/path/storage backend。
- QualityContract 描述 rubric/evaluator policy；QualityEvaluation 描述某次评估结果。
- WorkflowAction 是 runtime 操作；WorkflowPatch 是 draft-only 结构变更。
- BusinessEvent 必须使用具体 `business.*` namespace，但不新增 Meeting/Knowledge/Video canonical events。
- PipelineBoard 只返回 UI 可消费 summary，不包含 raw trace payload 或 secret。
- 对象包含 scope 或可通过 instance 追溯 scope。
- 不依赖 Meeting / Knowledge / Video 业务。
- 不引入 UI 字段。
- 不 import GatewayService / RuntimeAdapter / Core Store 内部实现。
- V3.6 planned methods 仍为 `runtime_handler=false`，不进入默认 callable method list，也不进入 Python/TS SDK default surface。

### V3.6-B Workflow Template / Draft / Version Service

PR slices：

- `V3.6-B-PR1`：新增 WorkflowStore / WorkflowRepository / InMemoryWorkflowStore。
- `V3.6-B-PR2`：实现 template create/get/list。
- `V3.6-B-PR3`：实现 update_draft / draft.save / revision conflict。
- `V3.6-B-PR4`：实现 publish / version get/list / archive。
- `V3.6-B-PR5`：接入 scope、capability、trace redaction、method metadata tests。

规划 RPC：

```text
workflow.template.create
workflow.template.get
workflow.template.list
workflow.template.update_draft
workflow.template.publish
workflow.template.archive
workflow.draft.save
workflow.version.get
workflow.version.list
```

验收：

- 可创建 draft。
- template id 唯一性范围为 app/project/workspace/template_id。
- update_draft/save 支持 revision conflict。
- 可发布 version。
- publish 必须显式传 version；重复 version 返回 conflict。
- 已发布版本不可被直接 update。
- 已发布 draft 不可编辑；update_draft after publish fork 新 draft。
- 更新 draft 不影响已发布 version。
- archive 不删除历史记录，重复 archive idempotent。
- 所有操作写 trace。
- 所有操作受 scope 约束。
- B 阶段不触发 runtime execution，不创建 WorkflowInstance/StationRun/Job/Artifact/Approval。

### V3.6-C Workflow Runtime MVP

PR slices：

- `V3.6-C-PR1`：实现 workflow instance start/get/list。
- `V3.6-C-PR2`：实现 pause/resume/cancel/retry。
- `V3.6-C-PR3`：实现 station run get/list/rerun。
- `V3.6-C-PR4`：实现两站 dummy workflow runtime。

规划 RPC：

```text
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
```

验收：

- dummy workflow 至少两个 station。
- station A 生成 artifact。
- station B 消费 station A artifact。
- StationRun 绑定 job / artifact / trace。
- workflow instance 状态可查询。
- `max_steps=1` deterministic mode 可观察 running/paused/cancelled 中间态。
- pause / resume / cancel 可用并遵守状态机。
- cancel 后不继续执行后续 station。
- station.rerun 可重跑指定 station。
- station.rerun 生成新 StationRun、Job、Artifact，不覆盖历史 run 或历史 artifact。
- C 阶段只注册最小 artifact metadata，不声明 artifact lineage complete。
- C 阶段不触发 approval、quality、board、business event 或 patch。

### V3.6-D Approval Point / Policy Integration

状态：已完成 targeted implementation and tests。

PR slices：

- `V3.6-D-PR1`：Station 支持 `approval_required` 和 approval point。
- `V3.6-D-PR2`：StationRun 支持 `waiting_approval`。
- `V3.6-D-PR3`：复用 `approval.respond` resume/stop workflow。
- `V3.6-D-PR4`：补 policy、trace、scope tests。

验收：

- station 可声明 approval point。
- 执行到审批 station 时进入 `waiting_approval`。
- 生成 approval request。
- EventBridge 可看到 `approval.required`。
- `approval.respond approve` 后 station 继续。
- `approval.respond reject` 后按策略进入 blocked/failed/cancelled。
- approval 过程写 trace。
- 不新增默认 `approval.approve/reject` 入口。

已落地补强：

- approval 前不创建 Job/Artifact，不执行 downstream station。
- approval metadata 带 `workflow_binding` 和 `workflow_side_effect_status=pending/applying/applied/failed`。
- approved decision 缺失 side effect 时 repeated approve 可恢复执行。
- cancel waiting workflow 会将 workflow-bound approval 标记 inactive，late approval 返回 `WORKFLOW_APPROVAL_INACTIVE` 且不改写 decision。
- `max_steps=1` / step mode 下 approve 只执行当前 approval station，不无条件跑完整 workflow。
- `approval.required` 可通过 EventBridge approval channel 观察，workflow binding 放在 `event.data.workflow_binding`。

### V3.6-E Artifact Contract / Lineage Binding

状态：已完成 targeted implementation and tests。

PR slices：

- `V3.6-E-PR1`：补强 ArtifactContract：contract_id、cardinality、kind_match_policy，并阻断 raw content/path/storage/token/raw trace 字段。
- `V3.6-E-PR2`：StationRun 增加 input_bindings/output_bindings，扁平 input_artifact_ids/output_artifact_ids 与 bindings 保持一致。
- `V3.6-E-PR3`：artifact metadata 改为 `workflow` / `artifact_contract` / `lineage` namespace，用户 metadata 放入 `user`，不得覆盖系统 namespace。
- `V3.6-E-PR4`：duplicate contract_id 返回 `WORKFLOW_ARTIFACT_CONTRACT_INVALID`；exact kind mismatch 返回 `WORKFLOW_ARTIFACT_KIND_MISMATCH`；compatible 不作为默认 fallback。
- `V3.6-E-PR5`：output parent_ids 来自 input bindings，按 first-seen order 去重；artifact.lineage 支持 station A -> B；rerun 生成新 artifact 且不默认把旧 output 作为 parent。
- `V3.6-E-PR6`：artifact registration failure 返回 `WORKFLOW_ARTIFACT_REGISTRATION_FAILED`，StationRun 不进入 completed，failure_context redacted。
- `V3.6-E-PR7`：connector_result 不替代 station output、artifact.read blocking regression、no SDK wrapper / no workflow lineage RPC / no runtime creep tests。

验收：

- station output artifact 进入 Artifact Registry。
- 同一 station 内 duplicate `contract_id` 被拒绝，不同 station 可复用同名 contract_id。
- StationRun 记录 contract_id -> artifact_ids 的 input/output bindings。
- artifact metadata 通过 namespaced `metadata.workflow`、`metadata.artifact_contract`、`metadata.lineage` 记录系统字段。
- `kind_match_policy=exact` 要求 artifact.kind 与 contract.artifact_kind 一致。
- artifact.lineage 可追踪 station input/output，parent ids 按 first-seen order 去重。
- 大文件仍遵守 artifact read blocking policy。
- station rerun 生成新 artifact，不覆盖历史产物，不产生 false parent edge。
- connector_result 不替代 station output artifact，除非 output contract 显式允许 connector_result kind。
- V3.6-E 不创建 QualityEvaluation，不实现 board/business/patch，不新增 workflow lineage RPC，也不新增 Python/TypeScript SDK default wrappers。

### V3.6-F Quality Evaluation MVP

状态：已完成 targeted implementation and tests。

PR slices：

- `V3.6-F-PR1`：实现 QualityEvaluation store/repository 与 `quality.evaluation.create/get/list/attach` RPC。
- `V3.6-F-PR2`：实现 rule evaluator，并要求可追溯到 QualityContract / rubric_id；missing rubric 返回 `QUALITY_EVALUATION_INVALID`。
- `V3.6-F-PR3`：实现 manual evaluator 与 llm_placeholder 边界；llm_placeholder 不调用真实 LLM。
- `V3.6-F-PR4`：实现 auto_attach、attach idempotency、不同目标改绑拒绝、StationRun.quality_evaluation_ids 绑定。
- `V3.6-F-PR5`：补 scope validation、artifact metadata-only boundary、trace/record redaction、method metadata/capability/no SDK default exposure tests。

规划 RPC：

```text
quality.evaluation.create
quality.evaluation.get
quality.evaluation.list
quality.evaluation.attach
```

验收：

- station output 可绑定 quality evaluation；input artifact evaluation 需要显式 `allow_input_artifact=true`。
- rule/manual/llm_placeholder evaluator MVP 可用，且不调用真实 LLM 或外部服务。
- score 必须在 0.0 到 1.0；rule evaluator 根据 QualityContract.threshold 计算 passed/failed；manual evaluator 可显式提交 status。
- `quality.evaluation.attach` 对同一 target 重复调用返回 idempotent success；对不同 target 返回 `QUALITY_EVALUATION_ALREADY_ATTACHED`。
- evaluation 写 trace，但 `quality.evaluation.created/attached` 在 V3.6-F 只作为 trace 证据，不声明 live quality EventBridge streaming ready。
- 不把完整 QualityEvaluation 写入 artifact metadata 根部；StationRun.quality_evaluation_ids 是主绑定。
- 不改变 WorkflowInstance.status 或 StationRun.status，不触发 approval、rerun、board、business event 或 workflow patch。
- 不调用 `artifact.read`，不读取 media/binary/large/external-only 内容，artifact.read blocking policy 不回退。

### V3.6-G Pipeline Board Data API

状态：已完成 targeted implementation and full regression。

PR slices：

- `V3.6-G-PR1`：实现 `workflow.board.get`。
- `V3.6-G-PR2`：实现 station output list 和 instance status。
- `V3.6-G-PR3`：实现 board trace summary redaction。
- `V3.6-G-PR4`：补 UI-consumable board API tests、scope/capability tests、no business/patch creep tests。

规划 RPC：

```text
workflow.board.get
workflow.instance.status
station.output.list
```

验收：

- 不依赖 UI 即可重建看板。
- board API 按 scope 过滤。
- board API 不返回敏感 token / raw trace payload。
- board API 可展示 station status、job status、artifact metadata、approval state、quality evaluation、trace summary。
- board API 消费 V3.6-F QualityEvaluation，但不修改 quality evaluation。
- board API 不调用 `artifact.read`，不返回 raw artifact content。
- V3.6-G 不实现 business.event.*，不实现 workflow.patch.*，不声明 V3.6 complete 或 V4.0 ready。

### V3.6-H Business Event Bridge / Workflow Context

状态：已完成 targeted implementation and focused regression。

PR slices：

- `V3.6-H-PR1`：实现 business event schema。
- `V3.6-H-PR2`：实现 workflow context get/update。
- `V3.6-H-PR3`：实现 business.event.emit/bind。
- `V3.6-H-PR4`：补 scope/policy/trace tests。

规划 RPC：

```text
business.event.emit
workflow.context.get
workflow.context.update
business.event.bind
```

验收：

- business event 能写入 workflow context。
- business event 不跨 scope。
- business event 进入 EventBridge。
- business event 不能绕过 approval / policy。
- 后续 Station 可以读取 updated context。
- 不新增业务专用 canonical event。
- 外部 update 和 binding 只能写 `context.business`，不能写 `context.system` 或修改 workflow/runtime/approval 状态。
- `business.event.received` 和 `workflow.context.updated` live SSE 可观察。
- V3.6-H 不实现 workflow.patch.*，不改变 V3.6-G Board API 合同。

### V3.6-I Workflow Patch / Agent Editing Contract

PR slices：

- `V3.6-I-PR1`：实现 patch model/store/schema、状态机和错误码。
- `V3.6-I-PR2`：实现 propose / diff。
- `V3.6-I-PR3`：实现 atomic apply / reject。
- `V3.6-I-PR4`：实现 risk_flags、agent boundary、EventBridge workflow_patch events。
- `V3.6-I-PR5`：补 agent cannot mutate published workflow、concurrent apply、invalid rollback、no runtime creep tests。

规划 RPC：

```text
workflow.patch.propose
workflow.patch.diff
workflow.patch.apply
workflow.draft.save
workflow.patch.reject
```

发布语义统一使用 `workflow.template.publish`；`workflow.version.get/list` 只读版本历史，不新增 `workflow.version.publish`。

验收：

- Patch proposal 可生成 redacted diff。
- Patch apply 只影响 draft，Published version snapshot 不变。
- repeated apply / reject idempotent，conflicting transition 返回 `WORKFLOW_PATCH_CONFLICT`。
- concurrent apply 同一个 patch 只递增一次 draft revision。
- resulting draft invalid 时 rollback，patch 不标 applied。
- Publish after apply 继续使用 `workflow.template.publish` 生成新 version。
- Patch 操作受 scope / capability / trace 约束。
- Patch live EventBridge events 可观察。
- Agent 不能 apply，不能静默修改 published workflow。
- V3.6-I 不启动 WorkflowInstance，不创建 StationRun/Job/Artifact/QualityEvaluation，不修改 WorkflowContext 或 Board API。

### V3.6-J Dummy Pipeline E2E / V4.0 Gate

状态：已完成 targeted implementation and focused regression。

PR slices：

- `V3.6-J-PR1`：新增 platform-neutral dummy pipeline fixture。
- `V3.6-J-PR2`：串起 template publish、instance start、station A/B/C、artifact lineage。
- `V3.6-J-PR3`：串起 approval、quality、board、business context、patch publish。
- `V3.6-J-PR4`：拆分 Runtime E2E 与 Editing E2E，验证 V1 snapshot / completed instance 不受 V2 patch/publish 影响。
- `V3.6-J-PR5`：补 scope isolation、external `/v1/rpc` capability smoke、redaction/no dependency 和 regression evidence。

验收：

- 不依赖 Meeting / Knowledge / Video / external MCP。
- 不改 Core/Gateway 默认 registry。
- 所有对象按 app/project/workspace scope 隔离。
- 所有关键动作写 trace。
- Artifact lineage 可还原 station input/output。
- Approval point 可触发 `approval.required` 并通过 `approval.respond` 推进 workflow。
- QualityEvaluation 可绑定 final station output artifact。
- Board API 可还原完整流水线状态。
- EventBridge live SSE 覆盖 `approval.required`、`business.event.received`、`workflow.context.updated`、`workflow.patch.proposed`、`workflow.patch.applied`。
- `quality.evaluated` 仍为 trace-only，不作为 V3.6-J live EventBridge 出门条件。
- Patch apply / publish V2 不改变已完成 V1 workflow instance 或 V1 `WorkflowVersion.snapshot`。
- Patched V2 version 至少可运行一个 station。
- 全量回归绿灯。

## 5. Required Test Files

后续实现阶段应新增或等价覆盖：

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

## 6. Regression Commands

```bash
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
```
