# V5-4A Policy Capability Matrix

文档状态：V5-4A core slice implemented for review。

## Required Classifications

```text
forbidden
proposal_only
handoff_only
user_confirmed_only
approval_gated_future
never_executor
```

## Candidate Operations

```text
workflow.patch.apply
workflow.template.publish
workflow.instance.start
station.rerun
approval.respond
context.update
business.event.emit
connector.call
external_llm.call
artifact.write
quality.evaluation.create
```

## Required Rules

```text
source=agent cannot execute durable mutation by default
never_executor operations cannot enter allowlist
approval_gated_future cannot execute in V5-4A
user_confirmed_only requires user_confirmed=true
```

## Implemented Classifications

```text
workflow.patch.apply -> user_confirmed_only
workflow.template.publish -> approval_gated_future
workflow.instance.start -> user_confirmed_only
station.rerun -> user_confirmed_only
approval.respond -> user_confirmed_only
context.update -> approval_gated_future
business.event.emit -> approval_gated_future
connector.call -> never_executor
external_llm.call -> never_executor
artifact.write -> approval_gated_future
quality.evaluation.create -> approval_gated_future
```

Every implemented matrix item keeps agent_executable=false and runtime_execution_allowed=false.
