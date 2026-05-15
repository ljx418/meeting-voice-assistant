# V3.6 Acceptance Plan

文档状态：V3.6 complete baseline 已冻结；V3.6/V4.0 preflight hardening complete。

## 1. Baseline

V3.6 启动基线：

- V3.5 已完成 dev/local Application Adaptation Layer。
- V3.6 只把 workflow runtime 和 pipeline operating model 作为新增验收范围。
- V4.0 正式 UI 开发必须以 V3.6-J gate 为后端基线。

V3.6/V4.0 preflight hardening 已补充为 V4.0-0 前置验收：

- `session.close` / `session.resume` direct Gateway RPC 和 `/v1/rpc` 均拒绝跨 scope session。
- `memory.get` 校验 memory record scope 和外部 memory capability；legacy memory without scope 只能 admin/internal 处理或要求 backfill。
- workflow-bound approval 拒绝 legacy `approval.approve/reject`；`approval.respond` 是唯一 continuation path。
- `requires_approval=true` 的 high-risk workflow patch apply 返回 `WORKFLOW_ACTION_FORBIDDEN`，不修改 draft revision，不把 patch 标为 applied。
- `workflow.board.get` / `workflow.instance.status` 返回 job summary 前校验 JobRecord scope。
- business EventBridge channel 需要 `business_events.read`，live SSE 与 cursor replay 均执行 capability check。
- `/v1/events/subscribe` follow mode 必须能轮询新增事件，不能只输出 heartbeat；subscription token 必须绑定 token allowed origins。
- `business.event.emit` 的 idempotency marker 与 context update 必须原子应用；context update 失败不得消耗 event_id。
- `business.event.bind` 必须拒绝重复 `binding_id`，不能覆盖旧 binding。
- platform Gateway 启动路径不在模块顶层 hard import Meeting/Knowledge/Video workflow。
- V4.0 drawio 协议名对齐 V3.6 冻结 API，不再使用未冻结的 `workflow.invoke/observe/review`。

## 2. Phase Acceptance

| 阶段 | 验收项 |
| --- | --- |
| V3.6-0 | V3.6 文档集、integration contract、current gap drawio 存在；V4.0 gate 同步；独立 workflow runtime contract inventory 和 schema draft 存在；planned methods 不进入默认 callable surface；不声明 runtime 已实现。 |
| V3.6-A | WorkflowTemplate / WorkflowVersion / WorkflowDraft / WorkflowInstance / Station / WorkflowEdge / StationRun / ArtifactContract / QualityContract / QualityEvaluation / WorkflowAction / WorkflowPatch / WorkflowContext / BusinessEvent / PipelineBoard schema 可测试；object schema 为 `schema_status=contract`、`stable_for_ui=false`；planned methods 仍不进入 runtime callable surface。 |
| V3.6-B | Template/draft/version service 可用；scope 唯一性、revision conflict、explicit version publish、published draft lock、archive idempotency、capability、trace redaction、no runtime execution 均有测试。 |
| V3.6-C | dummy workflow 至少两个 station 可运行；`max_steps` deterministic mode 可观察中间状态；StationRun 绑定真实 JobRecord、最小 artifact metadata 和 trace；pause/resume/cancel/rerun 可用；不触发 approval、quality、board、business event 或 patch。 |
| V3.6-D | approval point 进入 `waiting_approval`；pre-execution approval 前不创建 Job/Artifact、不执行 downstream station；`approval.required` 可通过 EventBridge 观察；`approval.respond` approve 后按 execution mode 继续，reject 后 blocked；cancel waiting workflow 后 late approval 返回 `WORKFLOW_APPROVAL_INACTIVE`；workflow side-effect marker 可恢复已批准但未应用的 side effect。 |
| V3.6-E | ArtifactContract 增加 contract_id/cardinality/kind_match_policy；duplicate contract_id 在同一 station 内返回 `WORKFLOW_ARTIFACT_CONTRACT_INVALID`；exact kind mismatch 返回 `WORKFLOW_ARTIFACT_KIND_MISMATCH`；StationRun 记录 input_bindings/output_bindings；artifact metadata 使用 workflow/artifact_contract/lineage namespace；parent_ids 来自 input bindings 并按 first-seen order 去重；artifact.lineage 可还原 station A -> B；station.rerun 生成新 artifact 且不产生 false parent edge；artifact registration failure 返回 `WORKFLOW_ARTIFACT_REGISTRATION_FAILED`；artifact.read blocking policy 不变。 |
| V3.6-F | QualityEvaluation 可绑定 artifact / station_run；rule/manual/llm_placeholder evaluator MVP 可用；rule evaluator 可追溯 QualityContract/rubric_id；score/status validation、auto_attach、attach idempotency、不同目标改绑拒绝、scope validation、artifact.read policy regression、trace/record redaction、no workflow state mutation 均有测试；quality live EventBridge streaming 和 Board API 仍不声明 ready。 |
| V3.6-G | `workflow.board.get` 可返回 station、job、artifact、approval、quality、trace summary；`workflow.instance.status` 可返回 instance 运行摘要；`station.output.list` 可返回 station output artifact summary；按 scope 过滤并做 redaction；不修改 QualityEvaluation，不实现 business event 或 workflow patch。 |
| V3.6-H | business event 可通过 binding 写入 `context.business`；`workflow.context.get/update` 支持 revision conflict；`business.event.emit` 支持 event_id/idempotency_key；`business.event.received` 和 `workflow.context.updated` 进入 EventBridge；不跨 scope；不绕过 approval/runtime；不修改 Board API 或 QualityEvaluation。 |
| V3.6-I | patch propose/diff/apply/reject 可用；apply 只影响 draft；patch state machine、repeated action idempotency、atomic apply、resulting draft validation、agent apply denied、risk_flags、workflow_patch EventBridge、scope/capability、redaction 和 no runtime creep 均有测试；publish after apply 继续使用 `workflow.template.publish`。 |
| V3.6-J | 平台中立 dummy pipeline E2E 完成 create/publish/start/station/artifact/approval/quality/board/business/patch/complete 全链路；Runtime E2E 与 Editing E2E 分离；V1 instance/snapshot 不受 V2 patch/publish 影响；patched V2 可被 runtime 消费；EventBridge live 覆盖 approval/business/context/patch；scope isolation、external auth smoke、redaction 和 no dependency 均有测试。 |

## 3. Exit Standard

V3.6 完成后必须满足：

1. WorkflowTemplate / WorkflowVersion schema 冻结。
2. WorkflowInstance 可创建、启动、暂停、恢复、取消。
3. Station / StationRun 是一等对象。
4. StationRun 可绑定 Job / Artifact / Trace。
5. dummy workflow 至少两个 station 可跑通。
6. approval point 可触发 `approval.required`，并通过 `approval.respond` 继续。
7. QualityEvaluation 可绑定 artifact / station_run。
8. Pipeline Board API 可返回 station、job、artifact、approval、quality、trace summary。
9. Business event 可进入 workflow context update，并写 trace。
10. WorkflowPatch 支持 propose / diff / apply to draft / publish version。
11. Agent 不能静默修改 published workflow。
12. 所有能力受 app/project/workspace scope、policy、approval、trace 约束。
13. 有平台中立 dummy pipeline E2E，不依赖 Meeting / Knowledge / Video / external MCP。
14. V3.5 回归继续绿灯。
15. 全量回归继续绿灯。

通过后可声明：

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

## 4. Required Tests

后续代码阶段新增或等价覆盖：

- `tests/test_v3_6_workflow_contract.py`
- `tests/test_v3_6_workflow_template_service.py`
- `tests/test_v3_6_workflow_runtime.py`
- `tests/test_v3_6_workflow_runtime.py`
- `tests/test_v3_6_workflow_approval.py`
- `tests/test_v3_6_artifact_lineage_binding.py`
- `tests/test_v3_6_quality_evaluation.py`
- `tests/test_v3_6_pipeline_board_api.py`
- `tests/test_v3_6_business_event_bridge.py`
- `tests/test_v3_6_workflow_patch.py`
- `tests/test_v3_6_dummy_pipeline_e2e.py`

回归命令：

```bash
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
```

## 5. No False Green Rule

- 只完成 V3.6-0 contract inventory 时，不得声明 workflow runtime ready。
- 只完成 V3.6-A object contract schema 时，只能声明 `V3.6-A complete: Workflow contract schema ready`。
- 只完成 V3.6-B template/draft/version service 时，只能声明 `V3.6-B complete: Versioned workflow template service ready`。
- 只完成 V3.6-C runtime MVP 时，只能声明 `V3.6-C complete: Dummy workflow runtime MVP ready`。
- 只完成 V3.6-D approval point 时，只能声明 `V3.6-D complete: Workflow approval point ready`。
- 只完成 V3.6-E artifact contract / lineage binding 时，只能声明 `V3.6-E complete: Station artifact contract and lineage binding ready`。
- 只完成 V3.6-F quality evaluation MVP 时，只能声明 `V3.6-F complete: Quality evaluation MVP ready`。
- 只完成 V3.6-G board API 时，只能声明 `V3.6-G complete: Pipeline Board Data API ready`。
- 只完成 V3.6-H business event/context 时，只能声明 `V3.6-H complete: Business Event Bridge and Workflow Context ready`。
- 只完成 V3.6-I workflow patch contract 时，只能声明 `V3.6-I complete: Safe workflow patch contract ready`。
- V3.6-C 只提供最小 artifact metadata，不得声明 artifact lineage binding complete。
- V3.6-E 不得声明 QualityEvaluation、Pipeline Board API、business event、workflow patch、full pipeline operating model 或 V3.6 complete ready。
- V3.6-F 不得声明 Pipeline Board API、quality live EventBridge streaming、business event、workflow patch、full pipeline operating model 或 V3.6 complete ready。
- V3.6-G 不得声明 business event、workflow patch、dummy pipeline E2E、full pipeline operating model、V3.6 complete 或 V4.0 ready。
- V3.6-H 不得声明 workflow patch、dummy pipeline E2E、full pipeline operating model、V3.6 complete 或 V4.0 ready。
- V3.6-I 不得声明 dummy pipeline E2E、full pipeline operating model、V3.6 complete 或 V4.0 ready。
- V3.6-J 通过后可以声明 V3.6 complete，但仍不得声明 V4.0 complete、Workflow Studio ready、AgentTalkWindow ready、production workflow automation ready 或 distributed workflow engine ready。
- 未冻结 WorkflowTemplate / WorkflowVersion schema，不得进入 V4.0 正式 UI 主开发。
- 未实现 StationRun 与 Job / Artifact / Trace 绑定，不得声明 pipeline operating model ready。
- V3.6-D 只证明 workflow-bound approval point，不得声明 artifact lineage、quality、board、business event、patch 或 full pipeline operating model ready。
- 未实现 Pipeline Board API，不得声明 Workflow Studio 可消费后端事实源。
- 未通过 dummy pipeline E2E，不得声明 V3.6 complete。
- 未通过 V3.5 回归，不得声明 V3.6 出门。
