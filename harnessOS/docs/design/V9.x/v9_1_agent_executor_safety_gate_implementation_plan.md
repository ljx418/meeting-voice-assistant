# V9-1 Agent Executor Safety Gate Implementation Plan

文档状态：V9-1 implementation plan draft / runtime implementation still NO-GO。

## 1. Boundary

V9-1 implementation, when approved, only implements safety gate validation and contract enforcement. It does not create Agent executor routes, runtime workers, or Executed runtime path.

Current implementation-readiness inputs:

```text
docs/design/V9.x/schemas/agent_execution_policy.schema.json
docs/design/V9.x/schemas/agent_execution_envelope.schema.json
docs/design/V9.x/schemas/human_authorization_ref.schema.json
docs/design/V9.x/schemas/capability_resolver_decision.schema.json
docs/design/V9.x/schemas/execution_evidence.schema.json
docs/design/V9.x/fixtures/schema-negative/source_agent_durable_mutation.json
docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json
```

Allowed stage claim after evidence:

```text
V9-1 complete: Agent executor safety gate ready for review.
```

## 2. Implementation Scope

Implementable objects:

```text
AgentExecutionPolicy parser / validator
AgentExecutionEnvelope parser / validator
CapabilityResolver deny-by-default engine
HumanAuthorizationRef reference validator hook
ApprovalGateDecision contract validator
KillSwitchDecision contract validator
TimeoutPolicy contract validator
RollbackDescriptor contract validator
ExecutionEvidence redaction validator
```

Non-implementable in V9-1:

```text
executor runtime worker
production executor route
source=agent durable mutation
automatic workflow editing
controlled executor action execution
```

## 3. State Boundary

V9-1 may reach:

```text
Proposed
CapabilityEvaluated
AwaitingUserConfirmation
AwaitingApprovalGate
KillSwitchChecked
ReadyForControlledRuntime
```

V9-1 must not reach:

```text
Executed
RuntimeActionStarted
RuntimeActionCompleted
```

`ReadyForControlledRuntime` is a V9-2 handoff boundary, not runtime execution.

## 4. Test Fixtures

```text
agent_execution_policy_valid
agent_execution_envelope_valid
source_agent_mutation_denied
missing_capability_decision_denied
missing_human_authorization_for_mutation_denied
high_risk_missing_approval_gate_denied
raw_secret_in_envelope_denied
ready_for_controlled_runtime_does_not_execute
```

Implementation-readiness audit must prove these fixtures parse and the negative fixtures are expected to fail validation once the validator exists.

## 5. Evidence Package

Required evidence:

```text
v9_1_contract_validation_report.json
v9_1_negative_test_results.json
v9_1_no_false_green_scan.json
v9_1_redaction_scan.json
v9_1_external_audit_decision.md
```

## 6. Stop Conditions

```text
Agent executor route is added.
runtime worker implementation starts.
source=agent durable mutation is allowed.
V9-1 completion is described as Agent executor ready.
```
