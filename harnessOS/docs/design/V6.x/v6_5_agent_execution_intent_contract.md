# V6-5 Agent Execution Intent Contract

文档状态：V6-5 detailed planning / contract input。本文定义 V6-5 DTO 合同，不授权 runtime implementation。

## 1. AgentExecutionIntent

Required fields:

```text
intent_id
agent_id
session_id
source=agent
operation
target_refs
requested_action_summary
rationale_ref
prompt_template_ref
provider_invocation_ref
created_at
correlation_id
redaction_status
```

Constraints:

```text
source must equal agent
operation must be in V6-4 initial action set or denied before handoff
target_refs must be operation-specific
requested_action_summary must not contain raw artifact content
provider_invocation_ref must point to redacted MiniMax evidence
```

## 2. AgentCapabilityDecision

Required fields:

```text
decision_id
intent_id
policy_decision
capability_decision
risk_flags
requires_user_confirmation
requires_approval_gate
denial_reason
created_at
```

Allowed `policy_decision` values:

```text
allow_handoff
deny
blocked_missing_provider_evidence
blocked_sensitive_payload
blocked_excluded_operation
blocked_missing_target_refs
```

## 3. AgentExecutionHandoff

Required fields:

```text
handoff_id
intent_id
operation
target_refs
status
requires_human_authorization=true
human_authorization_ref
approval_gate_decision_ref
created_at
```

Allowed `status` values:

```text
awaiting_human_confirmation
dismissed
human_confirmed
handed_off_to_controlled_executor
blocked
```

## 4. MiniMaxIntentInvocationEvidence

Required fields:

```text
provider=minimax
model_ref
provider_config_source
credential_ref=env://MINIMAX_API_KEY
prompt_template_ref
input_runtime_snapshot_ref
output_intent_ref
redaction_status
correlation_id
created_at
```

## 5. No False Green Boundary

These contracts do not grant Agent execution authority. They only support governed intent and handoff.
