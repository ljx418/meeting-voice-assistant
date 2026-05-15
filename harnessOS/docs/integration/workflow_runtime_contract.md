# Workflow Runtime Integration Contract

文档状态：V3.6 complete baseline 已冻结；V3.6/V4.0 preflight hardening complete。

## 1. Purpose

This document describes the planned V3.6 Workflow Runtime surface that V3.5 SDKs, BFF templates, React hooks, and future V4.0 UI should consume.

V3.6 is not a UI layer. It exposes workflow runtime facts through protocol APIs and events.

V3.6-J has validated the integration contract with a platform-neutral dummy pipeline E2E. The verified chain creates and publishes V1, starts and completes a workflow instance through StationRun / Artifact / Approval / Quality / Board / Business Context, applies a safe patch to a draft, publishes V2, and starts a patched V2 instance without mutating the completed V1 instance or V1 version snapshot.

Preflight hardening additionally locks the V4.0 entry assumptions: high-risk patches return `WORKFLOW_ACTION_FORBIDDEN` until a formal patch approval flow exists, workflow-bound approvals use `approval.respond` only, Board/status job summaries are scope-checked, business EventBridge subscriptions require `business_events.read`, EventBridge follow mode polls newly created events, subscription tokens are origin-bound, and business event idempotency is applied atomically with context updates.

## 2. Integration Path

Recommended production path:

```text
Business UI / V4.0 UI
  -> BFF
  -> V3.5 SDK
  -> V3.6 Workflow Runtime RPC
  -> Core Job / Artifact / Approval / Trace
```

Dev/direct path:

```text
Business UI
  -> TypeScript SDK
  -> V3.6 Workflow Runtime RPC
```

Dev/direct remains limited to restricted capability tokens or explicit dev mode.

## 3. Planned Methods

Workflow template:

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

Workflow runtime:

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

Board, quality, context, patch:

```text
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

Publish semantics are intentionally centralized in `workflow.template.publish`. `workflow.version.get` and `workflow.version.list` are read-only version history methods; V3.6 does not define `workflow.version.publish`.

## 4. Current Object Contract Status

V3.6-A has contract models in `core/workflows/models.py` and object schemas in `core/protocol/schemas/workflow_objects.py`.

Current contract objects:

- WorkflowTemplate / WorkflowDraft / WorkflowVersion.
- WorkflowInstance.
- Station / WorkflowEdge / StationRun.
- ArtifactContract.
- QualityContract / QualityEvaluation.
- WorkflowAction / WorkflowPatch.
- WorkflowContext / BusinessEvent.
- PipelineBoard.

V3.6-B callable methods:

- `workflow.template.create/get/list/update_draft/publish/archive`
- `workflow.draft.save`
- `workflow.version.get/list`

These methods are exposed as `sdk_exposure=workflow_runtime`, not SDK default wrappers.

V3.6-E artifact binding status:

- ArtifactContract includes `contract_id`, `cardinality`, and `kind_match_policy`.
- `contract_id` is unique within one Station; duplicates return `WORKFLOW_ARTIFACT_CONTRACT_INVALID`. Different stations may reuse the same contract id.
- The MVP supports exact kind matching. `kind_match_policy=exact` requires `artifact.kind == contract.artifact_kind`; mismatch returns `WORKFLOW_ARTIFACT_KIND_MISMATCH`.
- StationRun includes `input_bindings` and `output_bindings`; flat artifact id lists remain index views.
- Artifact metadata uses `workflow`, `artifact_contract`, and `lineage` namespaces.
- Parent ids are derived only from input bindings / flat input artifact ids, deduped in first-seen order, and must remain in scope.
- `connector_result` can be evidence, but cannot replace a station output artifact unless the output contract explicitly allows `connector_result`.
- Artifact registration failure returns `WORKFLOW_ARTIFACT_REGISTRATION_FAILED`; StationRun must not be completed without output artifacts.
- `artifact.lineage` can reconstruct station input/output parent edges without introducing a custom workflow lineage RPC.
- `artifact.read` policy is unchanged; metadata/read_metadata is the default workflow runtime consumption path.

V3.6-F quality evaluation status:

- `quality.evaluation.create/get/list/attach` are callable runtime methods with `sdk_exposure=workflow_runtime`, not SDK default wrappers.
- `quality.evaluation.get/list` require `quality.read`; `quality.evaluation.create/attach` require `quality.write`.
- QualityContract describes rubric/evaluator policy. QualityEvaluation records one evaluation result.
- rule evaluator must resolve QualityContract / rubric_id; missing rubric returns `QUALITY_EVALUATION_INVALID`.
- manual evaluator can accept caller-provided rubric_id and explicit status.
- llm_placeholder only records evaluator_type and returns `manual_required`; it does not call a real LLM or external service.
- `create(auto_attach=true)` can bind the evaluation to a station run / artifact.
- `attach` is idempotent for the same target and returns `QUALITY_EVALUATION_ALREADY_ATTACHED` for a different target.
- Evaluation MVP does not mutate WorkflowInstance.status or StationRun.status and does not trigger approval, rerun, board, business event, or patch behavior.
- Evaluation MVP does not call `artifact.read`; artifact metadata and supplied score/issues/threshold are the only inputs.
- `quality.evaluation.created/attached` are trace-only in V3.6-F. Live quality EventBridge streaming is not declared ready.

Important integration constraints:

- Object schemas are `schema_status=contract` and `stable_for_ui=false`.
- B 阶段 template/draft/version methods are `runtime_handler=true`; C/D/E runtime/station/artifact-binding behavior is implemented; F quality evaluation behavior is implemented; G board/status/output methods are the current runtime summary surface; business/patch methods remain planned until later phases.
- WorkflowEdge references must point to existing stations in the same template.
- WorkflowVersion is an immutable published snapshot.
- WorkflowDraft has `status` and `revision`; save/update/publish can use `expected_revision`.
- WorkflowPatch can only target `draft`.
- PipelineBoard is a redacted summary surface, not a raw trace payload surface.

V3.6-G board API status:

- `workflow.board.get` returns station/job/artifact/approval/quality/trace summary for a workflow instance.
- `workflow.instance.status` returns instance state, current station ids, station run counts, job status counts, artifact count, and quality evaluation count.
- `station.output.list` returns station output artifact summaries.
- Board and output responses are read-only and do not mutate QualityEvaluation or workflow runtime records.
- Board and output responses must not include raw trace payload, raw artifact content, tokens, subscription tokens, Authorization headers, or raw connector payload.
- Board API is not business event support, workflow patch support, or V3.6 completion.

## 5. Scope And Auth

Every method must be scoped by:

```json
{
  "app_id": "reference_app",
  "project_id": "demo",
  "workspace_id": "local"
}
```

Rules:

- External access must pass through V3.5 capability token and scope checks.
- `scope_mode=all` must not be accepted for write operations.
- Board and trace summary responses must be redacted.
- Approval must use `approval.respond`; integrations must not expose `approval.approve` / `approval.reject`.

## 6. Events

V3.6 events must be available through V3.5 EventBridge:

```text
workflow.instance.started
workflow.instance.completed
station.run.started
station.run.waiting_approval
station.run.completed
quality.evaluated
workflow.patch.proposed
workflow.patch.applied
workflow.context.updated
business.event.received
```

All events must include scope and stable references to workflow instance, station run, artifact, approval, quality evaluation, or patch where applicable.

## 7. V4.0 Dependency

V4.0 Workflow Studio / AgentTalkWindow formal development should not depend on mock-only backend state. It should use:

- `workflow.board.get` for board reconstruction.
- EventBridge for runtime updates.
- `workflow.patch.*` for agent editing.
- `quality.evaluation.*` for quality panel facts.
- Artifact lineage for station input/output relationships.
