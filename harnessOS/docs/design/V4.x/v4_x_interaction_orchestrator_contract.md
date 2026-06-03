# V4.x Interaction Orchestrator Contract

文档状态：V4-U2 交互编排合同。

## 1. 目的

Interaction Orchestrator 统一接收 Mission Console、Agent Builder、Thin Web Console、HTML Report 和未来业务 Head 的用户意图。

它不直接写 runtime，不替代 governed BFF / WorkflowPatch / Runtime API。

## 2. Core DTOs

### InteractionIntent

```json
{
  "intent_id": "intent_001",
  "source": "mission_console",
  "actor_type": "human",
  "operation": "workflow.create",
  "natural_language_goal": "递归总结 Desktop/技术分享 下的 Markdown 文件",
  "target_refs": {
    "workflow_spec_id": "spec_local_markdown_summary"
  },
  "requested_action": "generate_spec"
}
```

Allowed source:

```text
mission_console
tui
thin_web_console
html_report
agent
future_business_app
```

### InteractionStateProjection

```json
{
  "workflow_state": "DiffReady",
  "station_states": [],
  "evidence_state": "EvidenceRecorded",
  "available_actions": [],
  "blocked_actions": [],
  "source_refs": []
}
```

### AvailableActionDTO

```json
{
  "action_id": "confirm_apply",
  "operation": "workflow.patch.apply",
  "requires_user_confirmation": true,
  "agent_executable": false,
  "risk_flags": ["draft_mutation"],
  "policy_decision": "user_confirmed_only"
}
```

## 3. Rules

1. `source=agent` cannot execute mutation。
2. Standard guard sentence: source=agent cannot execute mutation。
3. Durable mutation requires `user_confirmed=true`。
4. HTML Report and Drawio can only request read-only views or handoff。
5. EventBridge only triggers refresh。
6. All mutation handoff must preserve `operation`, `source`, `actor_type`, `risk_flags`, and `policy_decision`。
7. Orchestrator must not create hidden runtime truth from report payloads。

## 4. Operation Policy

| operation | allowed for source=agent | minimum policy |
| --- | --- | --- |
| workflow.spec.generate | yes | proposal_only |
| workflow.patch.propose | yes | proposal_only |
| workflow.patch.apply | no | user_confirmed_only |
| workflow.template.publish | no | user_confirmed_only |
| workflow.instance.start | no | user_confirmed_only |
| station.rerun | no | user_confirmed_only |
| approval.respond | no | user_confirmed_only |
| context.update | no | user_confirmed_only |
| evidence.show | yes | read_only |
