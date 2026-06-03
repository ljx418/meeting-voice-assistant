# Historical V5-4E Production Controlled Executor Runtime Plan

文档状态：historical / superseded。Production controlled executor runtime slice 已移动到 V5-7B，且必须在 V5-7A design gate 通过和高风险人工 proceed decision 记录后才允许进入。本文不再是当前控制计划，仅保留历史审计上下文。

## Entry Conditions

V5-4E cannot start until all conditions are met:

```text
V5-4D design gate passes
human high-risk proceed decision is recorded
V5-1 tenant boundary accepted
V5-2 credential boundary accepted
V5-3 audit export accepted
V5-4A safety gate accepted
V5-4C dev/local bridge accepted
No False Green claim scan passes
```

## Stage Goal

V5-4E would implement a limited production controlled executor runtime slice:

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
V5-4E complete: limited production controlled executor runtime slice ready for review.
```

## Initial Allowed Action Candidate Set

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

V5-4E must not initially allow:

```text
source=agent direct durable mutation
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
app_id
actor_type
actor_id
source
user_confirmed
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

## Real Data Acceptance

V5-4E must use real production-like test data or a clearly isolated staging fixture:

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
tenant or app scope bypass is possible
high-risk action executes without approval gate
idempotency missing
rollback descriptor missing
audit evidence missing
incident timeline missing
claim scan detects production controlled executor ready
```

## No False Green

V5-4E may only prove a limited production controlled executor runtime slice. It must not prove unrestricted Agent executor, autonomous workflow editing, full multi-Agent orchestration, complete Workflow Studio, or production-ready external app support.
