# V3.6 Starting Baseline

文档状态：V3.6 complete baseline。  
来源：V3.5 completion evidence、V4.0 target architecture、当前 V3.6-J Dummy Pipeline E2E / V4.0 Gate baseline。

## 1. Current Planning Conclusion

V3.6 已完成 **Workflow Runtime Contract & Pipeline Operating Model** 阶段。当前结论是：V3.6-J 已提供 V4.0 Workflow Studio / AgentTalkWindow 正式开发所需的 dev/local 后端事实源。

V3.6 的重点不是继续扩展 SDK/BFF，也不是直接做 UI，而是把以下对象定义为平台可运行事实源：

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
- Pipeline Board API
- Business Event Bridge

## 2. Usable Baseline From V3.5

V3.6 可以假定以下能力可用：

| 能力 | V3.6 使用方式 |
| --- | --- |
| V3.5 SDK / BFF / Hooks | 后续 V4.0 UI 通过适配层消费 V3.6 API。 |
| EventBridge | workflow/station/quality/patch/business events 后续进入同一事件通道。 |
| Capability Token / Scope | workflow runtime 所有写入、查询和事件必须绑定 `app_id/project_id/workspace_id`。 |
| Job / Artifact / Trace | StationRun 必须绑定 job、input/output artifacts 和 trace。 |
| Approval | V3.6 复用 `approval.respond`，不新增 `approval.approve/reject` 默认入口。 |
| Pack / Connector | Workflow runtime 可引用 pack/connector，但 V3.6 dummy pipeline 不依赖 Meeting/Knowledge/Video/external MCP。 |

## 3. Runtime Capabilities Completed For V4.0 Gate

当前 V3.6-J 已关闭进入 V4.0 正式开发前的后端 gate：

- WorkflowInstance 生命周期 runtime 已具备 MVP，并由 dummy pipeline E2E 覆盖完整出门链路。
- WorkflowPatch / Agent editing contract 已在 V3.6-I 落地；approval point 与 `approval.respond` 的 workflow resume/reject 语义已在 V3.6-D 落地，QualityEvaluation MVP 已在 V3.6-F 落地，Pipeline Board Data API 已在 V3.6-G 落地。
- StationRun artifact contract / lineage binding 语义已在 V3.6-E 落地；Board API 和 dummy pipeline E2E 已消费这些绑定。
- Approval point 与 policy/trace 的流水线语义已具备 MVP。
- ArtifactContract 与 lineage binding 已具备 MVP。
- QualityEvaluation evaluator / service 已具备 MVP；Board API 已消费 quality summary。
- Pipeline Board Data API 与 Business Event Bridge / Workflow Context 已具备 MVP。
- Business event 到 workflow context 的受控路径已在 V3.6-H 落地，并由 dummy pipeline E2E 验证。
- WorkflowPatch / Agent editing contract 已具备 MVP，并由 dummy pipeline E2E 验证 patch apply / publish V2。
- 平台中立 dummy pipeline E2E 已通过。

## 4. Boundary

V3.6 不做：

- 完整 Workflow Studio UI。
- 完整 AgentTalkWindow。
- 复杂低代码画布。
- Video Studio 真实业务流。
- Interview / Investment 正式业务扩展。
- Core 大重构。
- 分布式 workflow engine。
- production multi-tenant control plane。

V4.0 正式开发可以启动，但必须消费 V3.6 后端事实源；任何 UI Spike 都不能固化 mock schema，也不能新增 UI 专用后端旁路。
