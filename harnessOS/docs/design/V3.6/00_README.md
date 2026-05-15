# harnessOS V3.6 Design Docs

文档状态：V3.6 complete baseline 已冻结；V3.6/V4.0 preflight hardening complete。V3.5 已冻结为 `V3.5 complete at dev/local Application Adaptation Layer level`；V3.6 当前已具备 dev/local template / draft / version service、deterministic dummy workflow runtime MVP、workflow-bound approval point、StationRun artifact contract / lineage binding、QualityEvaluation MVP、Pipeline Board Data API、Business Event Bridge / Workflow Context，Safe Workflow Patch Contract，以及平台中立 Dummy Pipeline E2E。正式 V4.0-0 开发仍需以 preflight 后的 gap 文档和 drawio 作为 baseline。

## Positioning

V3.6 的目标是建立 **Workflow Runtime Contract & Pipeline Operating Model**。它不是 V4.0 UI 主开发，而是让“工作流流水线”成为 harnessOS 可运行、可追踪、可审批、可评价、可被 UI 消费的一等对象。

```text
V4.0 Future UI / Workflow Studio / AgentTalkWindow
  -> V3.5 Application Adaptation Layer
      SDK / BFF / Hooks / EventBridge / Embed
  -> V3.6 Workflow Runtime Layer
      WorkflowTemplate / WorkflowInstance
      Station / StationRun
      ArtifactContract / QualityEvaluation
      WorkflowAction / WorkflowPatch
      Pipeline Board API / Business Event Bridge
  -> harnessOS Core
      Session / Turn / Job / Artifact / Approval / Trace / Policy
  -> Domain Packs / Connectors
```

V3.6 是 V4.0 正式开发的后端 gate。V3.6-J 与 preflight hardening 完成后，项目具备进入 V4.0 正式开发计划的条件；但本轮仍暂停 V4.0-0 实施，后续必须由明确任务启动，且不能固化 mock schema、不能绕过 V3.6 API。

## Documents

| 文件 | 用途 |
| --- | --- |
| `v3_6_starting_baseline.md` | V3.6 起点基线、V3.5 完成边界和进入条件。 |
| `v3_6_architecture_baseline.md` | V3.6 在 V3.5 与 V4.0 之间的架构位置、平面演进和边界。 |
| `v3_6_current_gap_analysis.md` | V3.6 当前差距、目标架构、阶段路线图；与同名 drawio 作为核心维护文件。 |
| `v3_6_current_gap_analysis.drawio` | V3.6 当前差距、目标架构和 V4.0 gate 图；必须与 `v3_6_current_gap_analysis.md` 同步。 |
| `v3_6_development_plan_workflow_runtime.md` | V3.6-0 到 V3.6-J 的阶段计划、PR 切片和验收口径。 |
| `v3_6_workflow_contract.md` | Workflow / Station / Artifact / Quality / Patch / Board 的规划合同。 |
| `v3_6_acceptance_plan.md` | V3.6 分阶段验收、最终出门标准和 No False Green 规则。 |
| `v3_6_project_introduction_baseline.md` | 面向团队沟通的 V3.6 项目介绍基线。 |
| `v3_6_f_completion_note.md` | V3.6-F Quality Evaluation MVP 冻结证据、测试结果和 No False Green 边界。 |
| `v3_6_h_completion_note.md` | V3.6-H Business Event Bridge / Workflow Context 冻结证据、测试结果和 No False Green 边界。 |
| `v3_6_i_completion_note.md` | V3.6-I Workflow Patch / Agent Editing Contract 冻结证据、测试结果和 No False Green 边界。 |
| `v3_6_j_completion_note.md` | V3.6-J Dummy Pipeline E2E / V4.0 Gate 冻结证据、测试结果和 V3.6 出门声明。 |
| `v3_6_preflight_hardening_note.md` | V3.6/V4.0 preflight hardening 冻结证据、测试结果和 No False Green 边界。 |

配套集成文档：

| 文件 | 用途 |
| --- | --- |
| `docs/integration/workflow_runtime_contract.md` | 面向 SDK/BFF/UI 的 V3.6 Workflow Runtime 集成合同草案。 |

## Baseline Rules

- V3.5 是当前已冻结基线，不在 V3.6 中重新验收 SDK、BFF、hooks、templates、reference app。
- V3.6 新增工作面是 Workflow Runtime Layer，不是 Core 大重构。
- V3.6 不做完整 Workflow Studio，不做完整 AgentTalkWindow，不做复杂低代码画布。
- V3.6 不实现 Video Studio、Interview、Investment 等正式业务工作流。
- V3.6 不实现分布式 workflow engine 或 production multi-tenant control plane。
- V3.6 可以允许轻量 V4.0 UI Spike，但 Spike 只能使用 mock 或 V3.6 contract schema，不能作为正式 runtime API。
- `v3_6_current_gap_analysis.md` 与 `v3_6_current_gap_analysis.drawio` 是 V3.6 核心维护文件，后续阶段变更必须同步更新。
- V3.6-0 已新增独立 workflow runtime inventory/schema draft；这些 draft 不进入 V3.5 SDK default surface，也不进入默认 callable method list。
- V3.6-A 已新增 `core/workflows/models.py`，并将 workflow object schema 升级为 `schema_status=contract`、`stable_for_ui=false`。
- V3.6-B 已实现 versioned workflow template service；template/draft/version methods 进入 callable method list，但 `sdk_exposure=workflow_runtime`，不进入 Python/TypeScript SDK default wrappers。
- V3.6-C 已实现 dummy workflow runtime MVP；workflow instance 和 station run methods 进入 callable method list，支持 `max_steps` deterministic execution、pause/resume/cancel、station rerun、真实 JobRecord 和最小 artifact metadata 绑定。
- V3.6-D 已实现 pre-execution workflow approval point；approval-required station 会进入 `waiting_approval`，只创建 StationRun 和 approval request，不创建 Job/Artifact，不执行 downstream station；`approval.respond` approve/reject 是唯一 continuation path。
- V3.6-D 的 workflow-bound approval 带有 side-effect marker，可恢复 approved decision 后缺失 side effect 的状态；cancel waiting workflow 会将 approval binding 标记 inactive，late approval 不会恢复 workflow。
- V3.6-E 已实现 ArtifactContract 字段补强、StationRun input/output bindings、namespaced artifact metadata、parent lineage binding、rerun artifact history、registration failure stable error 和 artifact.read blocking policy regression。
- V3.6-F 已实现 QualityEvaluation MVP：`quality.evaluation.create/get/list/attach` 可用，rule/manual/llm_placeholder evaluator 边界固定，evaluation 可绑定 station_run/artifact，并保持 trace redaction、artifact read policy regression 和 no runtime state mutation。
- V3.6-F 已冻结为 `V3.6-F complete: Quality evaluation MVP ready`。
- V3.6-G 已实现 `workflow.board.get`、`workflow.instance.status`、`station.output.list`，返回 station/job/artifact/approval/quality/trace summary，并保持 scope filtering 与 redaction。
- V3.6-H 已实现 `workflow.context.get/update`、`business.event.bind/emit`，支持 context.business 更新、event idempotency、live EventBridge events、scope/capability guard 和 redaction。
- V3.6-I 已实现 `workflow.patch.propose/diff/apply/reject`，支持 draft-only apply、patch state machine、agent apply deny、risk flags、live workflow_patch EventBridge events、scope/capability guard 和 redaction。
- V3.6-J 已实现平台中立 Dummy Pipeline E2E，通过 Gateway RPC / `/v1/rpc` 串起 runtime、artifact lineage、approval、quality、board、business context、patch 和 V2 publish。
- V3.6/V4.0 preflight hardening 已完成：补齐 session/memory scope guard、workflow-bound legacy approval guard、high-risk workflow patch governance、Board/status job scope double-check、business EventBridge channel permissions、EventBridge follow mode、subscription origin binding、business event atomic idempotency、duplicate binding guard、platform startup neutrality、Reference App BFF structured path 和 V4.0 drawio protocol alignment。
- V3.6-J 已证明 V1 completed instance 与 V1 version snapshot 不受 V2 patch/publish 影响，patched V2 version 可被 runtime 消费。
- V3.6-J 完成后可以声明 `V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development`。

## Implementation Order

1. `V3.6-0` Baseline / Contract Inventory.
2. `V3.6-A` Workflow Contract Schema.
3. `V3.6-B` Workflow Template / Draft / Version Service.
4. `V3.6-C` Workflow Runtime MVP.
5. `V3.6-D` Approval Point / Policy Integration.
6. `V3.6-E` Artifact Contract / Lineage Binding.
7. `V3.6-F` Quality Evaluation MVP.
8. `V3.6-G` Pipeline Board Data API.
9. `V3.6-H` Business Event Bridge / Workflow Context.
10. `V3.6-I` Workflow Patch / Agent Editing Contract.
11. `V3.6-J` Dummy Pipeline E2E / V4.0 Gate.

V3.6 完成后可以声明：

```text
V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development.
```

V3.6 完成后仍不能声明：

```text
V4.0 complete
Workflow Studio ready
AgentTalkWindow ready
production workflow automation ready
distributed workflow engine ready
```
