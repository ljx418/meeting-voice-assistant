# V5-7B Pre-Implementation Audit

文档状态：V5-7B implementation readiness audit。本文只用于判断是否可以进入 limited production controlled executor runtime slice，不实现 runtime。

## 1. Scope Boundary

V5-7B 只能在 V5-7A design gate 通过且记录 human high-risk proceed decision 后进入实现。

V5-7B 当前不得实现或允许：

```text
source=agent durable mutation
autonomous workflow editing
unrestricted Agent execution
unrestricted connector.call
unrestricted external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
raw production credential access
direct WorkflowStore / WorkflowDraft / WorkflowVersion / StationRun write
```

V5-7B 未来最多只能声明：

```text
V5-7B complete: limited production controlled executor runtime slice ready for review.
```

不得声明：

```text
production controlled executor ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
full multi-Agent orchestration ready
complete Workflow Studio ready
production-ready external app support
```

## 2. Entry Gate Checklist

| Gate | Required Evidence | Current Status | Audit Decision |
| --- | --- | --- | --- |
| V5-7A design gate passes | `v5_7a_production_controlled_executor_design_gate_completion_note.md` and evidence package | present | pass |
| Human high-risk proceed decision | explicit user decision recorded in completion/audit note | missing | block |
| V5-1 tenant boundary external review accepted | V5-1 completion note, tests, and external acceptance decision | present_for_review | block_until_external_review_accepted |
| V5-2 credential boundary external review accepted | V5-2 completion note, tests, and external acceptance decision | present_for_review | block_until_external_review_accepted |
| V5-3 audit export external review accepted | V5-3 completion note, tests, and external acceptance decision | present_for_review | block_until_external_review_accepted |
| V5-4A safety gate external review accepted | V5-4A completion note, tests, and external acceptance decision | present_for_review | block_until_external_review_accepted |
| V5-4C dev/local bridge external review accepted | V5-4C completion note, tests, and external acceptance decision | present_for_review | block_until_external_review_accepted |
| V5-6 product console / manual confirmation external review accepted | V5-6 completion note, tests, and external acceptance decision | present_for_review | block_until_external_review_accepted |
| V5-5 external app boundary external review accepted, if source is external app | V5-5 completion note, tests, and external acceptance decision | conditional | block_external_app_source_until_review |
| No False Green scan passes | V5 claim guard and focused scan | present_for_review | needs_current_scan |

Current Go / No-Go:

```text
NO-GO for implementation.
Reason: human high-risk proceed decision is not recorded, and stage acceptance dependencies still require external review confirmation.
```

## 3. Initial Runtime Action Acceptance Matrix

### workflow.instance.start

| Area | Required Acceptance |
| --- | --- |
| Actor/source | `actor_type=human_user` or `service_account_with_human_authorization`; `source=product_console` or `approved_api` only |
| Confirmation | `user_confirmed=true` required |
| Tenant scope | tenant / workspace / app / workflow instance ownership validated |
| Approval gate | conditional; required if risk flags or policy matrix marks high-risk context |
| Idempotency | idempotency key required; duplicate key returns prior execution reference |
| Rollback/manual recovery | cancel before external effect or mark instance failed with evidence |
| Audit evidence | ExecutionEvidenceContract emitted with correlation_id/request_id |
| Incident timeline | start event recorded |
| Stop condition | source=agent, missing confirmation, scope bypass, missing evidence |

### station.rerun

| Area | Required Acceptance |
| --- | --- |
| Actor/source | human or service account with human authorization only |
| Confirmation | `user_confirmed=true` required |
| Tenant scope | station and station run must belong to same tenant/workspace/instance |
| Approval gate | conditional; required for high-risk station, credentialed station, or external side effect |
| Idempotency | idempotency key required |
| Attempt history | old attempt retained; new attempt created |
| Downstream stale | downstream outputs marked stale until recomputed |
| Rollback/manual recovery | failed rerun leaves old attempt visible and recoverable |
| Audit evidence | old_attempt_ref, new_attempt_ref, runtime_result_ref recorded |
| Incident timeline | rerun event recorded |
| Stop condition | source=agent rerun, old attempt overwritten, downstream stale missing |

### artifact.write

| Area | Required Acceptance |
| --- | --- |
| Actor/source | human or service account with human authorization only |
| Confirmation | `user_confirmed=true` required |
| Risk | medium minimum |
| Approval gate | required |
| Tenant scope | artifact target belongs to current tenant/workspace/instance |
| Credential boundary | credential refs only; no raw secret |
| Versioning | append new artifact version; never overwrite prior artifact silently |
| Rollback/manual recovery | retract artifact ref or append correction artifact |
| Idempotency | idempotency key required |
| Audit evidence | input refs, output artifact ref, producer attempt ref recorded |
| Incident timeline | artifact write event recorded |
| Stop condition | raw artifact content in evidence/log/HTML/JSON, overwrite without prior version |

### quality.evaluation.create

| Area | Required Acceptance |
| --- | --- |
| Actor/source | human or service account with human authorization only |
| Confirmation | `user_confirmed=true` required |
| Risk | medium minimum |
| Approval gate | required |
| Tenant scope | quality target station/artifact belongs to current tenant/workspace/instance |
| Versioning | append evaluation; never overwrite previous score silently |
| Rollback/manual recovery | append correction evaluation while retaining prior score |
| Idempotency | idempotency key required |
| Audit evidence | quality_rule_ref, target_ref, evaluation_ref recorded |
| Incident timeline | quality evaluation event recorded |
| Stop condition | previous score removed, missing policy decision, missing audit evidence |

## 4. Real Or Staging Fixture Plan

V5-7B implementation must use real production-like data or an isolated staging fixture. A fixture is acceptable only if it includes:

```text
tenant_id
workspace_id
app_id
human actor
service account with human authorization
workflow_instance_id
station_id
station_run_id
artifact_id
credential_ref without raw secret
audit_export_package_id
incident_timeline_id
idempotency_key
correlation_id
request_id
```

Fixture requirements:

```text
cross-tenant request denied
wrong workspace request denied
wrong app request denied
wrong workflow instance denied
unknown credential ref denied
raw secret never present
source=agent denied
```

If a production dependency is unavailable, the related case must be marked:

```text
BLOCKED
```

or:

```text
staging_only
```

It must not be marked production PASS.

## 5. approved_api Boundary

`approved_api` is high-risk and must not bypass product console confirmation.

Minimum requirements before implementation:

```text
tenant-bound API client identity
service account binding
human authorization record
allowed source explicitly equals approved_api
user_confirmed equivalent recorded as human_authorization_ref
capability scope restricted to initial action set
rate limit and quota policy checked
audit evidence records API client, service account, and human authorization refs
```

Stop conditions:

```text
approved_api can start/rerun/write/evaluate without human authorization
approved_api accepts source=agent
approved_api accepts raw credential
approved_api bypasses tenant/app/workspace scope
```

Required approved_api test matrix:

```text
approved_api_without_human_authorization_denied
approved_api_with_expired_human_authorization_denied
approved_api_wrong_tenant_denied
approved_api_wrong_workspace_denied
approved_api_source_agent_denied
approved_api_records_api_client_service_account_and_human_authorization_refs
```

## 6. Service Account With Human Authorization Boundary

`service_account_with_human_authorization` requires:

```text
service_account_id
tenant_id
workspace_id
human_authorization_ref
authorization_subject_actor_id
authorization_created_at
authorization_expires_at
allowed_operations
policy_decision
audit_ref
```

It must not be treated as:

```text
Agent executor identity
autonomous executor identity
production admin override
```

Required service account test matrix:

```text
service_account_without_human_authorization_denied
service_account_expired_authorization_denied
service_account_wrong_operation_denied
service_account_as_agent_executor_denied
service_account_records_human_authorization_ref
```

## 7. Runtime Evidence Requirements

Every accepted action must emit an execution evidence record with:

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
incident_timeline_ref
audit_export_ref
correlation_id
request_id
redaction_status
created_at
```

Operation-specific target refs must be validated:

```text
workflow.instance.start requires workflow_instance_id
station.rerun requires station_id and station_run_id
artifact.write requires artifact_id or output artifact target
quality.evaluation.create requires quality_evaluation_id or target station/artifact ref
```

Execution envelope schema alignment:

```text
v5_7a_execution_envelope.schema.json must require minLength on target_refs properties.
v5_7a_execution_envelope.schema.json must enforce the same operation-specific target_refs as execution evidence.
```

Evidence must not include:

```text
capability_token
subscription_token
Authorization
Bearer
secret
raw_trace_payload
raw_artifact_content
raw_connector_payload
raw prompt
upstream signed URL
raw credential
```

## 8. Required Test Matrix Before Implementation

V5-7B must add focused tests before or with implementation:

```text
tests/test_v5_7b_entry_gate.py
tests/test_v5_7b_tenant_scope_guard.py
tests/test_v5_7b_actor_source_policy.py
tests/test_v5_7b_workflow_start.py
tests/test_v5_7b_station_rerun.py
tests/test_v5_7b_artifact_write.py
tests/test_v5_7b_quality_evaluation_create.py
tests/test_v5_7b_idempotency.py
tests/test_v5_7b_rollback_descriptor.py
tests/test_v5_7b_kill_switch_timeout.py
tests/test_v5_7b_execution_evidence.py
tests/test_v5_7b_incident_timeline.py
tests/test_v5_7b_audit_export.py
tests/test_v5_7b_redaction.py
tests/test_v5_7b_no_false_green.py
```

Required regression commands:

```text
./.venv/bin/python -m pytest tests/test_v5_7b_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V5.x/v5_current_gap_analysis.drawio
```

## 9. No False Green Review

Before implementation, scan must reject any claim outside allowed No False Green context:

```text
production controlled executor ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
distributed multi-Agent runtime ready
full multi-Agent orchestration ready
complete Workflow Studio ready
production-ready external app support
生产级受控执行器已完成
生产级Agent执行器已完成
分布式多Agent运行时已完成
```

`ready for review` must not be summarized as `ready`.

## 10. Audit Opinion

Current decision:

```text
CONDITIONAL GO for limited staging runtime slice.
NO-GO remains for production executor route, production runtime worker, source=agent durable mutation, and V5-8 implementation.
```

Updated reasons:

```text
human high-risk proceed decision is recorded for touching runtime code
focused per-action implementation test matrix is implemented
isolated staging fixture is implemented as Python in-memory runtime state
approved_api boundary has focused tests
service_account_with_human_authorization boundary has focused tests
kill switch / timeout / incident timeline refs are recorded in focused evidence
dependency external review remains deferred
production route / worker remains forbidden
```

Allowed next work:

```text
V5-7B planning refinement
V5-7B test matrix finalization
V5-7B staging fixture design
V5-7B limited staging runtime validation
external ChatGPT audit
```

Blocked work:

```text
production executor route
production runtime worker
source=agent durable mutation
V5-8 implementation
```
