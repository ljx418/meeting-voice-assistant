# V4.0-Q Controlled Executor Design Gate Plan

文档状态：V4.0-Q implemented as design gate. 本阶段只交付受控执行器设计门禁，不实现 controlled executor，不新增 Agent execute route，不新增 executor runtime，不允许 Agent 自动执行 mutation。

允许完成声明：

```text
V4.0-Q complete: controlled executor design gate ready for review.
```

禁止完成声明：

```text
controlled executor ready
Agent executor ready
autonomous workflow editing ready
complete AgentTalkWindow ready
complete Workflow Studio ready
production-ready external app support
full low-code canvas editing ready
```

## 1. Implementation Summary

V4.0-Q 在 V4.0-P AgentTalkWindow interaction E2E baseline 之上，只建立 controlled executor 的审计门禁：

- 机器可读 policy matrix 覆盖 future executor 可能触达的 mutation / side effect action。
- capability profile 明确 `executor.*` 在 Q 阶段全部 inactive。
- approval gate 只定义 future high-risk 条件，不创建 approval request。
- sandbox boundary 明确 future executor 只能消费 redacted BFF DTO，不能访问 raw payload 或 direct runtime store。
- rollback / kill switch 只定义设计项，不新增 admin route。
- evidence contract 只定义 future executor evidence 字段，不创建真实 executor evidence。
- EventBridge 继续只触发 refresh，不承载 executor truth。
- claim guard 防止把 design gate 误写成 executor ready。

## 2. PR Slices

### Q-PR1 No Implementation Guard

新增测试扫描 BFF 和 Workflow Console client，确认没有新增 `/execute`、`/run`、`/agent/execute`、`/kill-switch`、`/rollback`、`/admin-override` 可调用 route。`executor.dry_run` 只能出现在设计合同中，不能成为 route、client method、worker 或 runtime service。

### Q-PR2 Policy Matrix

新增机器可读设计合同 `v4_0_q_controlled_executor_design_gate_contract.json`。该合同是设计审计输入，不作为运行时配置读取。

Policy classification：

| Action | Classification |
| --- | --- |
| workflow.patch.apply | user_confirmed_only |
| workflow.patch.reject | user_confirmed_only |
| workflow.template.publish | approval_gated_future |
| approval.respond | user_confirmed_only |
| workflow.context.update | user_confirmed_only |
| business.event.emit | user_confirmed_only |
| workflow.instance.start | approval_gated_future |
| station.rerun | approval_gated_future |
| connector.call | never_executor |
| external_llm.call | never_executor |
| artifact.write | approval_gated_future |
| quality.evaluation.create | approval_gated_future |

`approval_gated_future` 在 Q 阶段不可执行。`never_executor` 永远不能进入 executor allowlist。

### Q-PR3 Capability Profile

设计合同允许描述以下 capability，但 Q 阶段不启用 executor capability：

- agent.propose
- agent.handoff
- agent.explain
- agent.navigate
- executor.dry_run
- executor.user_confirmed_execute
- executor.approval_gated_execute
- executor.admin_override

`executor.*` 全部 `active_in_q=false`。即使请求体或 capability token 声称有 `executor.*`，`source=agent` 仍不能执行 apply、publish、approval.respond、context.update 或 business.event.emit。

### Q-PR4 Approval Gate Design

Q 阶段只定义 future approval gate，不创建 approval request，不调用 approval.respond，不让 approval gated future action 可执行。

高风险条件至少包含：

- requires_approval=true
- high risk_flags
- external side effect
- connector mutation
- publish workflow
- context mutation
- business event emit
- artifact write
- quality score mutation

### Q-PR5 Sandbox Boundary

future executor 即使启用，也只能访问 redacted BFF DTO。Q 阶段不新增 raw payload access path。

禁止访问：

- capability_token
- subscription_token
- Authorization
- Bearer
- secret
- raw_trace_payload
- raw_artifact_content
- raw_connector_payload
- raw prompt
- upstream signed URL
- direct WorkflowStore write
- direct WorkflowDraft write
- direct WorkflowVersion write
- direct StationRun write

### Q-PR6 Rollback And Kill Switch Design

只定义：

- per-agent kill switch
- per-workspace kill switch
- capability revocation
- operation timeout
- idempotency key
- rollback descriptor
- manual recovery path
- audit retention

不新增 POST `/kill-switch`、POST `/rollback` 或 POST `/admin-override`。

### Q-PR7 Evidence And Audit Contract

future executor evidence 至少包含：

- proposal_id
- handoff_id
- user_confirmed
- approval_id
- capability_decision
- policy_decision
- runtime_result_ref
- correlation_id
- idempotency_key
- redaction_status
- created_at
- created_by

Q 阶段不创建真实 executor evidence。

### Q-PR8 Event Truth Guard

EventBridge 只触发 refresh。UI 不得从 event payload 构造 executor truth、agent action truth、patch truth、approval truth、evidence truth、board/status truth 或 context truth。

### Q-PR9 Documentation And Claim Guard

同步 V4.0 README、current gap、audit report、drawio、Q plan、Q completion note 和 Q pre-review。claim guard 扫描设计内容、源码、UI copy、completion note，防止 No False Green 回归。

## 3. Test Plan

新增或扩展：

```text
tests/test_v4_0_controlled_executor_design_gate.py
tests/test_v4_0_executor_policy_matrix.py
tests/test_v4_0_executor_capability_profile.py
tests/test_v4_0_executor_approval_gate.py
tests/test_v4_0_executor_sandbox_boundary.py
tests/test_v4_0_executor_evidence_contract.py
tests/test_v4_0_executor_claim_guard.py
apps/workflow-console/src/__tests__/executorDesignGate.test.tsx
apps/workflow-console/src/__tests__/executorNoFalseGreen.test.tsx
```

Browser smoke 不新增新的 executor 场景。现有 e2e 只用于回归 Workflow Console，不触发 execute、Agent apply、Agent publish、Agent approval.respond、Agent context.update、Agent business.event.emit、connector call 或 external LLM call。

## 4. Risk Controls

- 不新增 executor route、worker、runtime service 或 frontend execute client。
- 不把 policy matrix / capability profile / approval gate / sandbox boundary 写入 V3.6 runtime contract。
- `source=agent` 继续只能 propose / handoff / explain / navigate。
- Apply / Reject / Publish / approval.respond / context.update / business.event.emit 继续复用用户显式确认路径。
- `executor.*` capability remains inactive。
- EventBridge payload 不能构造 truth。
- raw payload、secret、token、signed URL 不得进入 DTO、DOM、error 或 event payload。
- Q 完成后只能声明 design gate ready for review。

## 5. Completion Evidence Format

Completion note 必须记录：

- allowed claim
- forbidden claims
- actual files changed
- tests added
- docs updated
- policy matrix result
- capability profile result
- approval gate result
- sandbox boundary result
- rollback and kill switch result
- evidence and audit contract result
- claim guard result
- validation command results
- No False Green statement
