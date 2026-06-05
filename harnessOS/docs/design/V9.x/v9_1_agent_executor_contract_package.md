# V9-1 Agent Executor Contract Package

文档状态：V9-1 contract-freeze package / safety gate ready for external audit。

## 1. Stage Boundary

V9-1 只冻结 Agent executor safety gate 合同，不实现 runtime executor。

允许声明：

```text
V9-1 complete: Agent executor safety gate ready for review.
```

禁止声明：

```text
Agent executor ready
controlled executor ready
production controlled executor ready
autonomous workflow editing ready
full multi-Agent orchestration ready
```

## 2. Non-Negotiable Invariants

```text
AgentExecutionEnvelope is request evidence, not runtime truth.
source=agent default durable mutation is always denied.
Durable mutation is denied unless user_confirmed=true OR valid human_authorization_ref is present.
Every mutating action requires CapabilityResolver decision.
Every high-risk action requires ApprovalGateDecision.
Every runtime action checks KillSwitchDecision before execution.
Every action has timeout policy and idempotency key.
Every mutation has rollback or correction strategy.
Evidence must use redacted refs only.
```

## 3. AgentExecutionPolicy Contract

Required fields:

```text
policy_id
policy_version
tenant_id
workspace_id
project_id
app_id
agent_id
station_id
allowed_operations
denied_operations
risk_level_by_operation
requires_user_confirmation_by_operation
requires_approval_gate_by_operation
allowed_sources
denied_sources
credential_boundary_ref
evidence_policy_ref
created_at
```

Rules:

```text
additionalProperties=false
source=agent must not be in allowed_sources for durable mutation.
denied_operations must include unrestricted connector.call, unrestricted external_llm.call, git.push, production.deploy by default.
```

## 4. AgentExecutionEnvelope Contract

Required fields:

```text
execution_envelope_id
operation
source
actor_type
actor_id
agent_id
station_id
tenant_id
workspace_id
project_id
app_id
workflow_instance_id
station_run_id
target_refs
payload_refs
user_confirmed
human_authorization_ref
capability_decision_ref
approval_gate_ref
idempotency_key
timeout_policy_ref
kill_switch_policy_ref
rollback_descriptor_ref
correlation_id
request_id
audit_ref
created_at
```

Rules:

```text
additionalProperties=false
payload_refs are redacted refs only.
target_refs are operation-specific and non-empty.
raw prompt / raw file content / raw artifact content / raw provider payload / raw connector payload fields are forbidden.
```

## 5. CapabilityResolver Safety Matrix

| Operation class | Default result | Required before allow |
| --- | --- | --- |
| read model view | allow | actor scope and tenant/workspace refs |
| evidence.show | allow | authorized view and redaction policy |
| report.open | allow | authorized view and read-only report |
| artifact.write | deny | user confirmation OR human_authorization_ref, approval gate, rollback descriptor |
| quality.evaluation.create | deny | user confirmation OR human_authorization_ref, approval gate, append-only strategy |
| station.rerun | deny | user confirmation OR human_authorization_ref, attempt history, downstream stale strategy |
| workflow.instance.start | deny | user confirmation OR human_authorization_ref, idempotency key, policy allow |
| workflow.template.publish | deny | separate publish policy and human approval |
| connector.call | deny | separate connector policy and credential lease |
| external_llm.call | deny | separate provider policy and redacted prompt refs |
| git.commit | deny | coding workflow review and human authorization |
| git.push | deny | separate release gate and human authorization |
| production.deploy | deny | separate production deployment gate |

## 6. State Machine

```text
Proposed
 -> CapabilityEvaluated
 -> AwaitingUserConfirmation
 -> AwaitingApprovalGate
 -> KillSwitchChecked
 -> ReadyForControlledRuntime
 -> Executed
 -> EvidenceRecorded
```

Failure states:

```text
DeniedByPolicy
DeniedMissingUserConfirmation
DeniedSourceAgentMutation
DeniedApprovalGate
DeniedKillSwitch
TimedOut
RollbackRequired
EvidenceRejected
```

## 7. Decision DTO Contracts

ApprovalGateDecision required fields:

```text
approval_gate_ref
operation
risk_level
requires_human_approval
approved
approved_by
approved_at
denial_reason
correlation_id
audit_ref
```

KillSwitchDecision required fields:

```text
kill_switch_policy_ref
operation
checked_at
checked_by
allowed
denial_reason
correlation_id
audit_ref
```

TimeoutPolicy required fields:

```text
timeout_policy_ref
operation
max_runtime_seconds
on_timeout
incident_timeline_required
```

RollbackDescriptor required fields:

```text
rollback_descriptor_ref
operation
rollback_strategy
correction_artifact_required
previous_state_ref
created_at
```

ExecutionEvidence required fields:

```text
execution_evidence_ref
execution_envelope_id
operation
source
actor_type
agent_id
station_id
target_refs
capability_decision_ref
approval_gate_ref
runtime_result_ref
rollback_descriptor_ref
redaction_status
correlation_id
request_id
audit_ref
created_at
```

## 8. Negative Tests

```text
source_agent_workflow_instance_start_denied
source_agent_station_rerun_denied
durable_mutation_without_user_confirmation_or_human_authorization_denied
artifact_write_without_rollback_descriptor_denied
quality_evaluation_overwrite_previous_score_denied
connector_call_without_separate_policy_denied
external_llm_call_without_provider_policy_denied
git_push_without_release_gate_denied
production_deploy_without_production_gate_denied
raw_secret_in_execution_envelope_denied
raw_prompt_in_payload_refs_denied
kill_switch_denied_blocks_execution
timeout_marks_attempt_failed_and_records_incident
```

## 9. Acceptance Oracle

V9-1 can pass only if:

```text
AgentExecutionPolicy contract exists.
AgentExecutionEnvelope contract exists.
HumanAuthorizationRef contract exists and is referenced by durable mutation invariant.
CapabilityResolver safety matrix exists.
ApprovalGateDecision / KillSwitchDecision / TimeoutPolicy / RollbackDescriptor / ExecutionEvidence contracts exist.
Durable mutation invariant is present in PRD, architecture, development plan and gate matrix.
Negative test list exists.
No False Green scan PASS.
External audit accepts contract-freeze package.
```

V9-1 cannot pass if:

```text
Agent executor route exists.
Runtime worker implementation starts.
source=agent durable mutation is allowed.
Any positive claim says Agent executor ready.
```
