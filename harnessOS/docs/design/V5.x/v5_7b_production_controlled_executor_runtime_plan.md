# V5-7B Production Controlled Executor Runtime Plan

文档状态：V5-7B planning package。本文是 production controlled executor runtime slice 的候选实现计划，默认 blocked。

## Entry Conditions

V5-7B cannot start until all conditions are met:

```text
V5-7A design gate passes
human high-risk proceed decision is recorded
V5-1 tenant boundary external review accepted
V5-2 credential boundary external review accepted
V5-3 audit export external review accepted
V5-4A safety gate external review accepted
V5-4C dev/local bridge external review accepted
V5-6 product console / manual confirmation UX external review accepted
No False Green claim scan passes
```

If the production action comes from an external app, V5-7B also requires:

```text
V5-5 external app onboarding boundary external review accepted
tenant-bound app registration external review accepted
domain verification and origin allowlist external review accepted
quota / rate limit denial evidence external review accepted
offboarding revocation evidence external review accepted
```

## Stage Goal

V5-7B would implement a limited production controlled executor runtime slice:

```text
execute limited allowed actions only
enforce tenant scope
enforce credential refs
enforce policy and approval gates
enforce idempotency
record execution evidence
support timeout and kill switch
support rollback descriptor and manual recovery
export audit package
record incident timeline
```

Allowed future claim, only after implementation and validation:

```text
V5-7B complete: limited production controlled executor runtime slice ready for review.
```

## Initial Allowed Action Candidate Set

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

Initial actor / source restrictions:

```text
actor_type=human_user
actor_type=service_account_with_human_authorization
source=product_console
source=approved_api
```

V5-7B must not initially allow:

```text
source=agent direct durable mutation
autonomous workflow editing
unrestricted Agent execution
business.event.emit
context.update
workflow.template.publish
approval.respond
unrestricted connector.call
unrestricted external_llm.call
```

## Required Runtime Evidence

```text
execution_id
operation
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
source
user_confirmed
human_authorization_ref
approval_id
policy_decision
capability_decision
credential_decision_ref
sandbox_input_ref
runtime_result_ref
idempotency_key
rollback_descriptor_ref
kill_switch_decision_ref
timeout_policy_ref
correlation_id
request_id
redaction_status
created_at
```

Operation-specific target refs must be enforced:

```text
workflow.instance.start requires workflow_instance_id
station.rerun requires station_id and station_run_id
artifact.write requires artifact_id or output artifact target
quality.evaluation.create requires quality_evaluation_id or target station/artifact ref
```

Required approved_api tests:

```text
approved_api_without_human_authorization_denied
approved_api_with_expired_human_authorization_denied
approved_api_wrong_tenant_denied
approved_api_wrong_workspace_denied
approved_api_source_agent_denied
approved_api_records_api_client_service_account_and_human_authorization_refs
```

Required service account tests:

```text
service_account_without_human_authorization_denied
service_account_expired_authorization_denied
service_account_wrong_operation_denied
service_account_as_agent_executor_denied
service_account_records_human_authorization_ref
```

## Real Data Acceptance

V5-7B must use real production-like test data or a clearly isolated staging fixture:

```text
tenant-bound workspace fixture
credential reference fixture without raw secret exposure
real workflow instance fixture
real artifact refs
real audit export package
real incident timeline event
```

If a production dependency is unavailable, the case must be marked BLOCKED or staging_only, not PASS.

## Stop Conditions

```text
missing human high-risk proceed decision
source=agent can execute durable mutation
raw secret appears in runtime input, logs, evidence, HTML, or JSON
approved_api bypasses human authorization
service_account_with_human_authorization is treated as Agent executor
tenant or app scope bypass is possible
high-risk action executes without approval gate
idempotency missing
rollback descriptor missing
audit evidence missing
incident timeline missing
claim scan detects production controlled executor ready
actor_type=agent executes durable mutation
source=agent executes durable mutation
unrestricted Agent execution is accepted
```

## No False Green

V5-7B may only prove:

```text
V5-7B complete: limited production controlled executor runtime slice ready for review.
```

It must not prove production controlled executor ready, controlled executor ready, Agent executor ready, autonomous workflow editing ready, full multi-Agent orchestration ready, complete Workflow Studio ready, or production-ready external app support.
