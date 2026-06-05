# V9-2 Controlled Agent Executor Runtime Implementation Spec

文档状态：V9-2 implementation-readiness spec / planned only。

## 1. Boundary

V9-2 只实现受控 Agent execution runtime slice，不证明完整 Agent executor、production controlled executor 或 autonomous workflow editing。

Allowed claim:

```text
V9-2 complete: controlled Agent execution runtime slice ready for review.
```

Forbidden claims:

```text
Agent executor ready
controlled executor ready
production controlled executor ready
autonomous workflow editing ready
```

## 2. Minimum Runtime Contracts

Required contracts before implementation:

```text
AgentExecutionEnvelope
AgentExecutionPolicy
HumanAuthorizationRef
CapabilityResolverDecision
ApprovalGateDecision
KillSwitchDecision
TimeoutPolicy
RollbackDescriptor
ExecutionEvidence
```

Durable mutation invariant:

```text
source=agent default durable mutation is always denied.
Durable mutation is denied unless user_confirmed=true OR human_authorization_ref is valid.
High-risk durable mutation additionally requires ApprovalGateDecision.
```

## 3. Action Allowlist

Initial action set:

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

Excluded actions:

```text
connector.call
external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
git.commit
git.push
production.deploy
```

## 4. State Transition

```text
EnvelopeReceived
 -> PolicyLoaded
 -> CapabilityEvaluated
 -> HumanAuthorizationValidated
 -> ApprovalGateEvaluated
 -> KillSwitchChecked
 -> IdempotencyChecked
 -> RuntimeActionStarted
 -> RuntimeActionCompleted
 -> EvidenceRecorded
```

Failure states:

```text
DeniedByPolicy
DeniedMissingHumanAuthorization
DeniedSourceAgentMutation
DeniedApprovalGate
DeniedKillSwitch
TimedOut
RollbackOrCorrectionRequired
EvidenceRejected
```

## 5. Persistence Model

Append-only records:

```text
execution_envelope
capability_decision
human_authorization_validation
approval_gate_decision
kill_switch_decision
runtime_result
execution_evidence
incident_timeline_event
```

Forbidden persistence:

```text
raw credential
raw prompt
raw file content
raw artifact content
raw provider payload
raw connector payload
```

## 6. E2E Fixture

Fixture must include:

```text
tenant_id
workspace_id
project_id
app_id
human_actor_id
agent_id
station_id
workflow_instance_id
station_run_id
human_authorization_ref
operation_hash
capability_decision_ref
approval_gate_ref
idempotency_key
correlation_id
request_id
```

## 7. Acceptance Tests

```text
controlled_executor_requires_policy_decision
durable_mutation_requires_user_confirmation_or_human_authorization_ref
source_agent_default_durable_mutation_denied
workflow_instance_start_idempotent_duplicate_returns_prior_ref
station_rerun_retains_old_attempt_and_marks_downstream_stale
artifact_write_append_only
quality_evaluation_append_only
approval_gate_required_for_medium_or_high_risk_mutation
kill_switch_checked_before_runtime_action
timeout_records_incident_and_marks_failed
execution_evidence_uses_redacted_refs_only
```

## 8. Stop Conditions

```text
source=agent mutates runtime directly.
durable mutation runs without user_confirmed=true OR valid human_authorization_ref.
approval gate is treated as replacement for human authorization.
artifact.write overwrites prior artifact silently.
quality.evaluation.create overwrites prior score silently.
raw secret / raw prompt / raw artifact content appears in evidence.
```
