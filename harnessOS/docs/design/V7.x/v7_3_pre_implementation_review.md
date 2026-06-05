# V7-3 Pre-Implementation Review

文档状态：V7-3 implementation readiness review package。本文用于在进入 V7-3 代码实现前冻结 PRD/spec 审计结论。

## 1. Current Decision

```text
current_stage: V7-3 Workflow Creation And Controlled Run Experience
decision: READY_FOR_EXTERNAL_AUDIT
implementation_allowed_before_external_audit: false
runtime_implementation_started: false
v7_4_final_acceptance_allowed: false
```

V7-3 当前可以进入外部审计和实现准备，但不得绕过本文、I/O 合同和真实数据验收计划直接编码。

## 2. Baseline

```text
V7-0 complete: V7 small studio and explainable TUI planning gate ready for review.
V7-1 complete: small studio production pilot control plane ready for review.
V7-2 complete: explainable Mission TUI pilot ready for review.
```

V7-2 的证据范围仍是：

```text
transcript_only=true
runtime_backed=false
```

V7-3 的目标是把 transcript-only Mission TUI 扩展为真实 create/run/review 链路，但只有在 real runtime evidence 成立时才能声明完成。

## 3. PRD Alignment

V7-3 必须覆盖 V7 PRD 主链路中的以下体验：

```text
用户打开 harness tui
 -> 输入自然语言目标
 -> Mission TUI 捕获 IntentCaptured
 -> 生成 WorkflowSpec 和 Diff
 -> 展示 Workflow Blueprint / Drawio link
 -> 展示 Available Actions 和 Forbidden Action Reasons
 -> 用户确认运行
 -> Controlled Runtime 执行
 -> Runtime Report 展示 station 状态
 -> Artifact / Quality / Evidence Chain 可查看
 -> Review Console 给出失败解释或 repair proposal
```

V7-3 不覆盖：

```text
complete Workflow Studio
arbitrary workflow creation
Agent executor
autonomous workflow editing
production controlled executor ready
production-ready external app support
full multi-Agent orchestration
```

## 4. Implementation Scope

允许实现：

```text
Natural-language goal parsing for the local Markdown technical document workflow only.
WorkflowSpec / Diff generation for the supported workflow.
Workflow Blueprint / Drawio generation from WorkflowSpec.
User-confirmed run handoff.
Reuse of V4-U5E local Markdown scanner and LLM provider workflow.
Reuse of V6 controlled runtime boundaries for user_confirmed evidence.
Runtime Report / Quality / Evidence Chain generation.
Read-only Review Console handoff evidence.
V7-3 evidence package and HTML report.
```

禁止实现：

```text
Generic natural-language workflow builder.
Agent direct durable mutation.
source=agent workflow.instance.start / station.rerun.
connector.call or external_llm.call as unrestricted production actions.
Hidden mutation forms in HTML reports.
Browser direct /v1/rpc or /v1/events/subscribe.
Production GA or full Web Studio productization.
```

## 5. Required Contracts Before Coding

V7-3 代码实现前必须接受：

```text
docs/design/V7.x/v7_3_io_contracts_and_schemas.md
docs/design/V7.x/v7_3_real_data_acceptance_plan.md
docs/design/V7.x/v7_3_workflow_creation_run_experience_plan.md
docs/design/V7.x/v7_acceptance_gate_matrix.md
```

这些文档必须共同证明：

```text
Input/output fields are explicit.
WorkflowSpec / Drawio / Report / Evidence are not runtime truth.
User confirmation is required before durable mutation.
fallback_demo_only and BLOCKED cannot be counted as runtime-backed PASS.
No False Green and redaction rules are testable.
```

## 6. PR Slices

| Slice | Purpose | Exit Evidence |
| --- | --- | --- |
| V7-3-PR1 Mission TUI runtime bridge | Extend `harness tui` from transcript-only to supported runtime-backed flow with explicit confirmation | TUI transcript, state DTO, source=agent denial |
| V7-3-PR2 WorkflowSpec / Diff / Blueprint | Generate supported local-doc workflow spec, diff and Drawio | workflow.json, workflow.yaml, workflow.drawio |
| V7-3-PR3 Controlled run handoff | Run user-confirmed local Markdown workflow through governed boundary | local-document-workflow-result.json, user_confirmed evidence |
| V7-3-PR4 Reports and Evidence | Generate Runtime Report, artifacts, quality and Evidence Chain | workflow_board.html, artifacts.html, quality.html, evidence.html |
| V7-3-PR5 Acceptance package | Generate V7-3 HTML dashboard, scans and completion note | index.html, acceptance-data.json, claims-scan.md, redaction-scan.md |

## 7. Stop Conditions

停止并回到规划审计：

```text
Natural-language parser expands beyond local Markdown workflow without PRD update.
User confirmation is bypassed.
source=agent can execute durable mutation.
Provider key missing but result is marked real_runtime PASS.
Fallback/demo summary is written as LLM-backed summary.
Raw prompt, raw file content, token, secret, signed URL or connector payload leaks.
WorkflowSpec / Drawio / HTML Report / Evidence Chain becomes runtime truth.
V7-4 starts before V7-3 evidence package exists.
```

## 8. Audit Conclusion

```text
Spec Drift Evaluation: LOW if V7-3 remains limited to the local Markdown workflow.
False Green Evaluation: MEDIUM until provider-backed runtime evidence is produced.
Next Stage Audit: external ChatGPT audit must review this document, I/O contracts and real-data acceptance plan.
Proceed Decision: proceed to V7-3 implementation only after external audit has no critical or major open issue.
```

