# HarnessOS V4 目标架构与交互模型

## 1. 架构总览

新的 V4 架构不再是简单链路：

```text
WorkflowSpec -> BFF -> Runtime -> Reports
```

而应引入体验中间层：

```text
Heads
  -> Interaction Orchestrator
  -> Experience State Machine
  -> Policy / Capability / Registry / Report Schema
  -> governed BFF / WorkflowPatch
  -> WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun
  -> Artifact / QualityEvaluation / OperationEvidence
  -> Drawio / HTML / TUI / Thin Web projections
```

## 2. 多 Head 层

支持多种入口：

```text
Mission Console / TUI
Agent Builder
Thin Web Console
HTML Runtime Report
Drawio Visualization
Future Business App Head
```

这些 Head 不是事实源，必须消费同一套后端 runtime 和 report projection。

## 3. Interaction Orchestrator

职责：

```text
接收用户意图。
映射为 InteractionIntent。
查询当前 Experience State。
返回 available_actions。
执行 confirmation gate。
调用 Agent Policy Layer。
将合法操作转交 governed BFF / WorkflowPatch / Runtime API。
```

它不直接写 runtime。

### 核心对象

```text
InteractionIntent
InteractionStateProjection
AvailableActionDTO
HandoffRequest
ConfirmationRequest
```

## 4. Experience State Machine

### Workflow-level state

```text
Idle
IntentCaptured
SpecDrafted
SchemaValidated
DiffReady
AwaitingConfirmation
DraftApplied
Published
RunReady
Running
Blocked
Failed
Recoverable
RerunRequested
Rerunning
Completed
Reviewed
Archived
```

### Station-level state

```text
Pending
Ready
Running
Completed
Failed
WaitingApproval
NeedsInput
Stale
Recoverable
RerunRequested
Rerunning
Skipped
```

### Evidence-level state

```text
NoEvidence
EvidencePending
EvidenceRecorded
ReviewReady
Reviewed
Disputed
Archived
```

### 每个状态必须包含

```text
state_id
label
description
available_actions
blocked_actions
requires_user_confirmation
risk_level
evidence_required
visible_in_tui
visible_in_html
visible_in_drawio
visible_in_thin_web
```

## 5. Agent Policy Layer

集中管理以下规则：

```text
source=agent cannot execute mutation
durable mutation requires user_confirmed=true
EventBridge only triggers refresh
HTML Report is read-only
Drawio is visualization only
WorkflowSpec cannot directly mutate runtime truth
no token / raw payload leakage
high-risk operations require approval or explicit block
```

输出：

```text
AgentPolicyDecision:
  operation
  source
  actor_type
  allowed
  requires_user_confirmation
  reason
  risk_flags
  policy_decision
  evidence_required
```

## 6. Runtime Capability Matrix

用于反虚假验收。

字段：

```text
capability_id
target_type
supports_run
supports_rerun
supports_attempt_history
supports_downstream_stale
supports_artifact_write
supports_quality_eval
supports_evidence
supports_timeout
supports_kill_switch
agent_executable
requires_user_confirmation
status: supported | partial | planned | unsupported
stage_owner
```

示例：

| Capability | Status | Notes |
|---|---|---|
| V4.1 local Markdown workflow | supported | dev/local MVP |
| generic station rerun | supported/partial by V4.2-C | not production runtime |
| Agent executor | unsupported | forbidden claim |
| production auth | planned | post V4 |
| full Web Studio | planned | not current mainline |

## 7. WorkflowSpec Registry

职责：

```text
管理 WorkflowSpec hash。
管理 schema version。
管理 compatibility check。
记录 generated_by。
记录 validated_at。
关联 draft/version/instance refs。
```

字段：

```text
spec_id
spec_hash
schema_version
source
created_by
generated_by
validated_at
linked_draft_id
linked_version_id
compatibility_status
```

## 8. Report Schema

统一 HTML / Drawio / TUI / Thin Web 的数据投影。

### WorkflowReportSchema

```text
report_id
workflow_spec_ref
workflow_version_ref
workflow_instance_ref
generated_at
source_refs
stations[]
artifacts[]
quality[]
evidence[]
available_actions[]
redaction_status
```

### StationReportSchema

```text
station_id
station_run_id
state
attempt_count
latest_attempt_id
input_artifact_refs
output_artifact_refs
quality_status
error_summary
available_actions
```

### EvidenceReportSchema

```text
proposal_id
handoff_id
user_confirmed
operation_type
runtime_result_ref
risk_flags
policy_decision
correlation_id
redaction_status
review_status
```

## 9. 统一体验表达

同一状态应在不同 Head 中一致表达：

| State | TUI | Drawio | HTML Report | Thin Web |
|---|---|---|---|---|
| AwaitingConfirmation | 文本提示确认 | 节点黄色边框 | banner 提示 | 确认按钮 |
| Running | 状态行实时刷新 | 蓝色运行标识 | Run board | 只读状态 |
| Failed | 错误摘要 | 红色节点 | Error panel | 重跑 handoff |
| Recoverable | 修复建议 | 橙色状态 | Rerun block | 用户确认重跑 |
| Reviewed | 审计完成 | 绿色勾选 | Evidence summary | 只读复盘 |

## 10. 与七平面的关系

七平面仍保留：

```text
七平面回答：事实源在哪里，谁有权修改，治理边界在哪里。
Headless 多 Head 回答：用户通过哪些入口定义、查看、运行、审计工作流。
Interaction Orchestrator 回答：多入口如何共享同一体验状态和动作语义。
```
