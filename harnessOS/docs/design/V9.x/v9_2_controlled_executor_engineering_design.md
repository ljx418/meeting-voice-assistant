# V9-2 Controlled Executor Engineering Design

文档状态：V9-2 engineering design / planned only。

## 1. Service Boundary

`ControlledExecutorService` executes only allowlisted actions after policy, authorization, approval, kill switch, idempotency and redaction checks.

Initial action set:

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

Excluded actions hard-denied:

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

## 2. Execution Pipeline

```text
parse envelope
load policy
evaluate capability
validate HumanAuthorizationRef or user_confirmed
evaluate approval gate if medium/high risk
check kill switch
check idempotency
start action
record runtime result
record execution evidence
append incident timeline when denied/failed
```

## 3. HumanAuthorizationRef Validator

Validator must check:

```text
exists
not expired
not revoked
operation_hash matches operation + target_refs + scope
tenant/workspace/project/app match
source and actor_type allowed
audit_ref exists
redaction PASS
```

## 4. Persistence And Migration

Append-only logical records:

```text
execution_envelope
capability_decision
human_authorization_validation
approval_gate_decision
kill_switch_decision
idempotency_record
runtime_result
execution_evidence
incident_timeline_event
```

Migration requirements:

```text
tenant/workspace/project/app indexed.
operation and idempotency_key indexed.
audit_ref indexed.
previous attempt records retained.
artifact and quality writes append only.
```

## 5. Runtime Evidence

Every completed or denied action records:

```text
execution_envelope_id
operation
decision_chain_refs
runtime_result_ref
human_authorization_ref or user_confirmed
approval_gate_ref when required
rollback_descriptor_ref
redaction_status
incident_timeline_ref when denied/failed
```

## 6. E2E Acceptance

```text
workflow_instance_start_success_with_human_authorization_ref
station_rerun_success_with_user_confirmed
artifact_write_appends_new_version
quality_evaluation_appends_new_score
source_agent_mutation_denied
expired_human_authorization_ref_denied
wrong_tenant_human_authorization_ref_denied
kill_switch_denied_blocks_action
idempotency_duplicate_returns_prior_runtime_result_ref
```
