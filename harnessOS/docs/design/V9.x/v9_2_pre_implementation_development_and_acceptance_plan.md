# V9-2 Pre-Implementation Development And Acceptance Plan

Document status: V9-2 implementation-readiness closure plan / no runtime implementation.

## Current Baseline

```text
V9-1 limited Safety Gate implementation: PASS
V9-1 internal independent audit: PASS
V9-2 controlled executor runtime implementation: NO-GO
```

V9-2 is a high-risk runtime stage. This plan closes readiness, evidence structure, fixture coverage, and PRD alignment before any runtime code is allowed.

## Scope

Allowed before human proceed decision:

```text
V9-2 PRD and architecture review
controlled executor action allowlist review
HumanAuthorizationRef validator dependency review
ExecutionEvidence and runtime result fixture design
idempotency / timeout / rollback fixture design
No False Green and redaction guard review
internal readiness audit package
human high-risk decision preparation
```

Blocked before human proceed decision:

```text
runtime executor route
runtime worker
controlled executor action execution
WorkflowStore / StationRun / Artifact writes
source=agent durable mutation
V9-3 runtime implementation
V9-4 runtime implementation
V9-8 final acceptance
```

## Acceptance Checklist

V9-2 implementation may only be requested after all are true:

```text
V9-1 Safety Gate evidence PASS.
V9-1 internal independent audit PASS.
V9-2 action allowlist accepted.
Excluded actions hard-denied in plan.
Durable mutation invariant accepted: user_confirmed=true OR valid human_authorization_ref.
source=agent default durable mutation remains denied.
HumanAuthorizationRef contract accepted.
ExecutionEvidence schema accepted.
V9-2 fixture package parses.
No False Green scan PASS.
Redaction scan PASS.
drawio XML valid.
human high-risk proceed decision is recorded for V9-2 runtime implementation.
```

## Planned Runtime Acceptance After Approval

If and only if V9-2 receives separate high-risk approval, runtime acceptance must prove:

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
timeout_records_incident_and_marks_failed
execution_evidence_uses_redacted_refs_only
```

## Stop Conditions

Stop and do not proceed if:

```text
V9-2 runtime starts without human high-risk proceed decision.
source=agent durable mutation is allowed.
durable mutation runs without user_confirmed=true OR valid human_authorization_ref.
approval gate replaces human authorization.
artifact.write overwrites previous artifact silently.
quality.evaluation.create overwrites prior score silently.
raw secret / raw prompt / raw artifact content appears in evidence.
V9-2 is described as Agent executor ready, controlled executor ready, or production controlled executor ready.
```

## Internal Audit Opinion

V9-2 can proceed only to implementation-readiness closure now. Runtime implementation remains blocked until a new human high-risk proceed decision is recorded.
