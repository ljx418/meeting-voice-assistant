# V3.6 Workflow Runtime Contract

文档状态：V3.6 complete baseline 已冻结；V3.6/V4.0 preflight hardening complete。

## 1. Contract Goal

V3.6 Workflow Runtime Contract 定义 V4.0 UI、V3.5 SDK/BFF/hooks 和 harnessOS Core 之间的流水线事实源。

本合同不定义 UI layout，不实现 Workflow Studio，不实现 AgentTalkWindow。

V3.6-J 已用平台中立 dummy pipeline 验证这些合同可以端到端组合：Template / Version / Draft、WorkflowInstance、StationRun、Artifact lineage、Approval、QualityEvaluation、Board、Business Context 和 WorkflowPatch 均可通过 Gateway RPC / `/v1/rpc` 形成同一条 workflow fact chain。

Preflight hardening 后，合同额外锁定：workflow-bound approval 只能通过 `approval.respond` 继续，高风险 patch 需要后续正式审批流而不能直接 apply，Board/status 不返回跨 scope job，business event 订阅需要 `business_events.read`，EventBridge follow mode 必须能轮询新增事件，subscription token 绑定 allowed origins，business event idempotency marker 必须与 context update 原子应用。

## 2. Core Objects

### WorkflowTemplate

```json
{
  "workflow_template_id": "wf_video_storyboard",
  "app_id": "reference_app",
  "name": "Video Storyboard Workflow",
  "description": "",
  "status": "draft | published | archived",
  "version": "0.1.0",
  "latest_draft_id": "wfd_xxx",
  "latest_published_version_id": "wfv_xxx",
  "stations": [],
  "edges": [],
  "artifact_contracts": [],
  "quality_contracts": [],
  "approval_points": [],
  "metadata": {}
}
```

规则：

- draft 可以修改。
- WorkflowTemplate 是逻辑身份。
- WorkflowDraft 是可编辑草稿。
- WorkflowVersion 是已发布不可变快照。
- published version 不可被静默修改。
- draft 修改不影响 published version。
- archive 不删除历史记录。

### WorkflowVersion

```json
{
  "workflow_version_id": "wfv_xxx",
  "workflow_template_id": "wf_xxx",
  "version": "0.1.0",
  "published_at": "2026-05-13T00:00:00Z",
  "snapshot": {},
  "trace_id": "trace_xxx",
  "metadata": {}
}
```

### WorkflowDraft

```json
{
  "workflow_draft_id": "wfd_xxx",
  "workflow_template_id": "wf_xxx",
  "base_version": "0.1.0",
  "base_version_id": "wfv_xxx",
  "status": "editable | published | archived",
  "revision": 1,
  "draft": {},
  "updated_at": "2026-05-13T00:00:00Z",
  "metadata": {}
}
```

### WorkflowInstance

```json
{
  "workflow_instance_id": "wfi_xxx",
  "workflow_template_id": "wf_xxx",
  "workflow_version": "0.1.0",
  "session_id": "sess_xxx",
  "thread_id": "thread_xxx",
  "app_id": "reference_app",
  "project_id": "demo",
  "workspace_id": "local",
  "status": "created | running | paused | waiting_approval | blocked | completed | failed | cancelled",
  "current_station_ids": [],
  "job_ids": [],
  "artifact_ids": [],
  "trace_id": "trace_xxx",
  "metadata": {}
}
```

`blocked` 表示可人工处理或等待外部补救，`failed` 表示执行失败。

### Station

```json
{
  "station_id": "station_script",
  "name": "Script Writer",
  "role": "writer",
  "agent_ref": "agent.writer",
  "skill_refs": ["generic.write"],
  "connector_refs": [],
  "input_contracts": [],
  "output_contracts": [],
  "approval_required": false,
  "quality_policy": {},
  "metadata": {}
}
```

### WorkflowEdge

```json
{
  "edge_id": "edge_script_review",
  "from_station_id": "station_script",
  "to_station_id": "station_review",
  "condition": {},
  "order": 1,
  "metadata": {}
}
```

规则：

- `from_station_id` 与 `to_station_id` 必须引用同一 template 内存在的 station。
- V3.6-A 只校验引用完整性；cycle 检测留给 runtime MVP。

### StationRun

```json
{
  "station_run_id": "sr_xxx",
  "workflow_instance_id": "wfi_xxx",
  "station_id": "station_script",
  "status": "queued | running | waiting_approval | completed | failed | cancelled",
  "attempt": 1,
  "rerun_of_station_run_id": null,
  "job_id": "job_xxx",
  "input_bindings": {
    "script_input": ["artifact_script_v1"]
  },
  "output_bindings": {
    "minutes_output": ["artifact_minutes_v1"]
  },
  "input_artifact_ids": [],
  "output_artifact_ids": [],
  "quality_evaluation_ids": [],
  "failure_context": {},
  "trace_id": "trace_xxx",
  "started_at": "2026-05-13T00:00:00Z",
  "completed_at": "2026-05-13T00:01:00Z",
  "metadata": {}
}
```

StationRun 必须可绑定 job、artifact、trace。rerun 创建新的 StationRun，不覆盖历史 run 或历史 artifact。

### ArtifactContract

```json
{
  "contract_id": "artifact_contract_script",
  "artifact_kind": "script",
  "direction": "input | output",
  "required": true,
  "cardinality": "one | many",
  "kind_match_policy": "exact | compatible",
  "schema_ref": "schema://generic-script",
  "metadata_schema": {},
  "preview_policy": {},
  "large_file_policy_ref": "artifact.read.default",
  "metadata": {}
}
```

ArtifactContract 只描述 station input/output 期望 artifact，不覆盖 Artifact Registry 主合同，也不包含 raw content、local path、storage backend、capability token、subscription token、Authorization 或 raw trace payload。

V3.6-E 绑定规则：

- 同一 station 内 `contract_id` 必须唯一。
- duplicate `contract_id` 在同一 station 内返回 `WORKFLOW_ARTIFACT_CONTRACT_INVALID`；不同 station 可以复用相同 `contract_id`。
- MVP 支持 `kind_match_policy=exact`，要求 `artifact.kind == contract.artifact_kind`；kind mismatch 返回 `WORKFLOW_ARTIFACT_KIND_MISMATCH`。`compatible` 只在显式 compatible metadata 存在时判断，不作为默认 fallback。
- `StationRun.input_bindings` / `StationRun.output_bindings` 是 contract_id 到 artifact_ids 的正式绑定。
- `input_artifact_ids` / `output_artifact_ids` 是 bindings 的扁平索引视图。
- workflow artifact metadata 必须使用 `metadata.workflow`、`metadata.artifact_contract`、`metadata.lineage` namespace。
- 用户 metadata 必须放入 `metadata.user`，不能覆盖系统 namespace。
- output artifact `parent_ids` 只能来自 input bindings / input_artifact_ids，按 first-seen order 去重并保持稳定顺序；cross-scope parent 必须被拒绝。
- station rerun 生成新 artifact，不覆盖旧 artifact；rerun relation 通过 `metadata.workflow.rerun_of_station_run_id` 表达，不默认生成旧 output -> 新 output parent edge。
- connector_result 可以作为 evidence/extra node，但不能替代 station output artifact；只有 output contract 显式允许 connector_result kind 时，connector_result 才能作为 output。
- artifact registration failure 返回 `WORKFLOW_ARTIFACT_REGISTRATION_FAILED`，StationRun 不得进入 completed，failure_context 必须 redacted。
- V3.6-E 不新增 workflow-specific lineage RPC，不新增 SDK default wrappers，继续复用 `artifact.lineage`。

### QualityContract

```json
{
  "contract_id": "quality_contract_script",
  "rubric_id": "rubric_script",
  "evaluator_type": "rule | manual | llm_placeholder",
  "required": false,
  "blocking": false,
  "threshold": 0.8,
  "policy": {},
  "metadata": {}
}
```

QualityContract 描述 rubric / evaluator policy，不调用真实 LLM evaluator。

V3.6-F 规则：

- rule evaluator 必须能追溯到 QualityContract / rubric_id；找不到 rubric 返回 `QUALITY_EVALUATION_INVALID`。
- manual evaluator 可以使用 caller-provided rubric_id。
- llm_placeholder 只记录 evaluator_type，不调用真实 LLM 或外部服务。
- `blocking` 只作为合同字段保留，V3.6-F 不执行 blocking gate。

### QualityEvaluation

```json
{
  "evaluation_id": "qe_xxx",
  "workflow_instance_id": "wfi_xxx",
  "station_run_id": "sr_xxx",
  "artifact_id": "artifact_xxx",
  "rubric_id": "rubric_xxx",
  "evaluator_type": "rule | manual | llm_placeholder",
  "score": 0.9,
  "status": "passed | warning | failed | manual_required",
  "issues": [],
  "suggestions": [],
  "evaluator": "rule_evaluator",
  "created_at": "2026-05-13T00:00:00Z"
}
```

QualityEvaluation 描述某次评估结果，可绑定 artifact / station_run。

V3.6-F 绑定规则：

- `quality.evaluation.create` 支持 `auto_attach`。
- `quality.evaluation.attach` 将已有 evaluation_id 绑定到 station_run/artifact。
- 重复 attach 到同一 station_run/artifact 返回 idempotent success。
- 同一 evaluation 绑定到不同 station_run/artifact 返回 `QUALITY_EVALUATION_ALREADY_ATTACHED`。
- 绑定后不允许静默改绑。
- artifact 默认必须属于 station run `output_artifact_ids`；评估 input artifact 必须显式 `allow_input_artifact=true`。
- cross-scope workflow/station/artifact 返回 `SCOPE_MISMATCH`。
- StationRun.quality_evaluation_ids 是主绑定；artifact metadata 如需记录，只能写轻量 `metadata.quality.evaluation_ids` 引用。

V3.6-F evaluator 边界：

- score 必须在 0.0 到 1.0。
- rule evaluator 根据 QualityContract.threshold 计算 `passed` / `failed`。
- manual evaluator 可显式提交 `passed` / `warning` / `failed` / `manual_required`。
- `manual_required` 只用于未能自动判断或等待人工输入。
- invalid score/status 返回 `QUALITY_EVALUATION_INVALID`。
- evaluator MVP 只使用 artifact metadata、supplied score、issue count 和 rubric threshold，不调用 `artifact.read`，不读取 media/binary/large/external-only 内容。
- `quality.evaluation.created/attached` 在 V3.6-F 只写 trace，不声明 live quality EventBridge streaming ready。
- V3.6-F 不改变 WorkflowInstance.status 或 StationRun.status，不触发 approval、rerun、workflow patch、business event 或 board runtime。

### WorkflowAction

```json
{
  "action_id": "action_xxx",
  "workflow_instance_id": "wfi_xxx",
  "action_type": "pause | resume | cancel | rerun | update_context | attach_artifact",
  "station_run_id": "sr_xxx",
  "station_id": "station_script",
  "params": {},
  "metadata": {}
}
```

WorkflowAction 是 runtime 操作，不修改 workflow draft 结构。

### WorkflowPatch

```json
{
  "workflow_patch_id": "wfp_xxx",
  "workflow_template_id": "wf_xxx",
  "workflow_draft_id": "wfd_xxx",
  "base_revision": 1,
  "base_version_id": "wfv_xxx",
  "target": "draft",
  "operation": "add_station | remove_station | update_station_prompt | update_connector | update_artifact_contract | update_quality_rule | update_approval_point | update_edge",
  "payload": {},
  "diff": {},
  "proposed_by": "agent_1",
  "actor_type": "agent | user | system",
  "actor_id": "agent_1",
  "status": "proposed | applied | rejected",
  "applied_revision": null,
  "resulting_draft_revision": null,
  "risk_flags": [],
  "requires_approval": false,
  "trace_id": "trace_xxx",
  "metadata": {}
}
```

WorkflowPatch 只能 target draft，不允许 target published version。V3.6-I 已固定：

- `proposed -> applied` 和 `proposed -> rejected` 是唯一状态迁移。
- repeated same action idempotent；conflicting action 返回 `WORKFLOW_PATCH_CONFLICT`。
- apply 必须校验 current draft revision 等于 `base_revision`，MVP 不做 rebase。
- apply 只修改 WorkflowDraft.draft，不修改 WorkflowVersion.snapshot。
- `actor_type=agent` 只能 propose/diff，不能 apply。
- diff 返回 redacted summary、risk_flags 和 requires_approval；I 阶段不自动创建 approval。

### BusinessEvent

```json
{
  "type": "business.example.selected",
  "payload": {},
  "scope": {},
  "workflow_instance_id": "wfi_xxx",
  "trace_id": "trace_xxx",
  "metadata": {}
}
```

BusinessEvent 必须使用具体 `business.*` namespace。`business.video.shot.selected` 只能作为业务 namespace 示例，不能成为 Core canonical event。

## 3. Planned RPC Surface

Template and version:

```text
workflow.template.create
workflow.template.get
workflow.template.list
workflow.template.update_draft
workflow.template.publish
workflow.template.archive
workflow.version.get
workflow.version.list
```

Runtime:

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

Board and quality:

```text
workflow.board.get
workflow.instance.status
station.output.list
quality.evaluation.create
quality.evaluation.get
quality.evaluation.list
quality.evaluation.attach
```

Business event and context:

```text
business.event.emit
workflow.context.get
workflow.context.update
business.event.bind
```

Patch:

```text
workflow.patch.propose
workflow.patch.diff
workflow.patch.apply
workflow.draft.save
workflow.patch.reject
```

发布语义统一由 `workflow.template.publish` 承担；`workflow.version.get/list` 只读版本历史，不新增 `workflow.version.publish`。

## 4. Event Contract

V3.6 should add canonical workflow events:

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

Rules:

- All events carry scope.
- All workflow runtime events include workflow references where applicable.
- Business events stay under `business.*` and do not introduce Meeting/Knowledge/Video canonical events.
- Events must be consumable through V3.5 EventBridge.

## 5. Board Response Shape

`workflow.board.get` returns enough data to rebuild a board without UI-specific storage:

```json
{
  "workflow_instance": {},
  "stations": [
    {
      "station": {},
      "runs": [],
      "status": "completed",
      "input_artifacts": [],
      "output_artifacts": [],
      "approvals": [],
      "quality": [],
      "trace_summary": {}
    }
  ],
  "current_station_ids": [],
  "jobs": [],
  "artifacts": [],
  "approvals": [],
  "quality_evaluations": []
}
```

The board response must not include raw tokens, subscription tokens, Authorization headers, raw connector failure payloads, or unredacted trace payloads.

V3.6-G rules:

- `workflow.board.get` is a read-only summary API.
- `workflow.instance.status` returns instance status, current station ids, station/job/artifact/quality counts, and status counts.
- `station.output.list` returns redacted output artifact summaries for a station or station run.
- Board responses are scoped by `app_id/project_id/workspace_id`.
- Board responses consume JobRecord, ArtifactRecord metadata, Approval records, QualityEvaluation records, and trace summaries.
- Board responses do not call `artifact.read` and do not return raw artifact content.
- Trace summary is redacted and does not include raw trace payload.
- V3.6-G does not mutate QualityEvaluation, WorkflowInstance, StationRun, Artifact, Job, Approval, or Trace records.
- V3.6-G does not implement business event, workflow patch, or live quality EventBridge streaming.

## 6. Forbidden Object Fields

V3.6-A object models must not define UI-only fields:

```text
x
y
position
canvas
panel
react_state
component
layout
```

They must also not define secret/raw payload fields:

```text
capability_token
subscription_token
authorization
secret
raw_trace_payload
```

UI layout belongs to V4.0 UI contracts. Secrets and raw traces belong behind redacted debug surfaces.
