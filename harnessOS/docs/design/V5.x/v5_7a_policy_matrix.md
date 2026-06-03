# V5-7A Production Controlled Executor Policy Matrix

文档状态：V5-7A design contract。本文只定义 production controlled executor 设计门禁，不实现 runtime。

## P0 Boundary

```text
no production executor route
no production runtime worker
no Agent direct durable mutation
no unrestricted connector.call
no unrestricted external_llm.call
no production credential raw secret access
no direct WorkflowStore / WorkflowDraft / WorkflowVersion / StationRun write
no autonomous workflow editing
```

## Candidate Action Matrix

| Action | Risk Level | Requires User Confirmation | Requires Approval Gate | Rollback Strategy | Idempotency Required | Audit Required | Incident Timeline Required | V5-7A Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `workflow.instance.start` | medium | yes | conditional | cancel_or_mark_failed_before_external_effect | yes | yes | yes | design_only |
| `station.rerun` | medium | yes | conditional | preserve_old_attempt_and_mark_downstream_stale | yes | yes | yes | design_only |
| `artifact.write` | medium | yes | yes | append_new_version_or_retract_artifact_ref | yes | yes | yes | design_only |
| `quality.evaluation.create` | medium | yes | yes | append_correction_evaluation_and_keep_prior_score | yes | yes | yes | design_only |

## Excluded Actions

The following actions remain excluded from any initial production runtime:

| Action | Exclusion Reason | Future Review Required |
| --- | --- | --- |
| `connector.call` | external side effect and credential exposure risk | separate approval policy, credential boundary, incident response review |
| `external_llm.call` | provider billing, prompt/data boundary, credential exposure risk | separate approval policy, credential boundary, prompt redaction review |
| `business.event.emit` | external business side effect | separate incident response and rollback review |
| `context.update` | durable context mutation risk | separate context governance review |
| `workflow.template.publish` | workflow production behavior change | publish approval and version rollback review |
| `approval.respond` | governance decision mutation | separate approval actor policy review |

## Actor And Source Policy

V5-7A may define a future action envelope for:

```text
actor_type=human_user
actor_type=service_account_with_human_authorization
source=product_console
source=approved_api
```

V5-7A must deny:

```text
source=agent direct durable mutation
autonomous workflow editing
unrestricted Agent execution
```

## No False Green

This policy matrix does not prove production controlled executor ready, controlled executor ready, Agent executor ready, autonomous workflow editing ready, production-ready external app support, distributed multi-Agent runtime ready, or complete Workflow Studio ready.

