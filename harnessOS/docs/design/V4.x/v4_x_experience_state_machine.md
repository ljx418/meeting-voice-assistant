# V4.x Experience State Machine

文档状态：V4-U1 体验状态机合同。

## 1. 目的

Experience State Machine 用于统一 Mission Console、Workflow Blueprint、Runtime Report、Review Console 和 Evidence Chain 的状态表达。

它不是 runtime truth，不写 WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun。

## 2. Workflow-level States

| state_id | label | available_actions | blocked_actions | requires_user_confirmation | evidence_required | risk_level |
| --- | --- | --- | --- | --- | --- | --- |
| Idle | 空闲 | capture_intent | apply,publish,run,rerun | false | false | low |
| IntentCaptured | 已捕获目标 | generate_spec,explain | apply,publish,run,rerun | false | false | low |
| SpecDrafted | 已生成草案 | validate_schema,show_blueprint | publish,run,rerun | false | false | low |
| SchemaValidated | Schema 已验证 | show_diff,show_blueprint | publish,run,rerun | false | false | low |
| DiffReady | Diff 就绪 | confirm_apply,explain_risk | publish,run,rerun | true | true | medium |
| AwaitingConfirmation | 等待用户确认 | confirm,cancel | auto_apply,auto_run | true | true | medium |
| DraftApplied | 已应用到草稿 | publish,show_blueprint | run,rerun | true | true | medium |
| Published | 已发布版本 | run,show_report | rerun | true | true | medium |
| Running | 运行中 | show_status,show_report | apply,publish | false | true | medium |
| Failed | 失败 | explain_failure,repair_proposal,request_rerun | auto_rerun | true | true | high |
| Recoverable | 可恢复 | confirm_rerun,repair_proposal | auto_rerun | true | true | high |
| Completed | 已完成 | show_artifacts,show_quality,show_evidence | apply,publish | false | true | low |
| Reviewed | 已复盘 | archive,show_evidence | apply,publish,run,rerun | false | true | low |

## 3. Station-level States

| state_id | label | available_actions | blocked_actions | requires_user_confirmation | evidence_required | risk_level |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | 待运行 | show_inputs | rerun | false | false | low |
| Ready | 就绪 | run_with_workflow | direct_run_without_workflow | true | true | medium |
| Running | 运行中 | show_trace | apply,publish,rerun | false | true | medium |
| Completed | 已完成 | show_outputs,show_quality | rerun_without_confirmation | true | true | low |
| Failed | 失败 | explain_failure,request_rerun | auto_rerun | true | true | high |
| Stale | 下游过期 | show_stale_reason,confirm_continue | auto_continue | true | true | medium |
| RerunRequested | 已请求重跑 | confirm_rerun,cancel | auto_rerun | true | true | high |
| Rerunning | 重跑中 | show_attempt_history | apply,publish | false | true | medium |

## 4. Evidence-level States

| state_id | label | available_actions | blocked_actions | requires_user_confirmation | evidence_required | risk_level |
| --- | --- | --- | --- | --- | --- | --- |
| NoEvidence | 无证据 | wait_for_operation | review | false | false | low |
| EvidencePending | 证据待写入 | refresh | execute | false | false | medium |
| EvidenceRecorded | 证据已记录 | show_evidence | execute,approve,reject | false | true | low |
| ReviewReady | 可复盘 | review,export | apply,publish,run,rerun | false | true | low |
| Reviewed | 已复盘 | archive | apply,publish,run,rerun | false | true | low |

## 5. Cross-head Visibility

所有状态必须可被以下 Head 引用同一 label：

```text
Mission Console
Workflow Blueprint
Runtime Report
Review Console
Evidence Chain
TUI
Drawio
HTML Report
Thin Web Console
```

