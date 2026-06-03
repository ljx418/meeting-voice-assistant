# V6-4 Test Matrix

文档状态：V6-4 test matrix / pre-implementation audit input。本文定义实现后必须覆盖的测试，不实现代码。

## 1. Focused Tests To Add

```text
tests/test_v6_4_controlled_executor_runtime.py
tests/test_v6_4_action_allowlist.py
tests/test_v6_4_approved_api_boundary.py
tests/test_v6_4_service_account_boundary.py
tests/test_v6_4_idempotency_kill_switch.py
tests/test_v6_4_artifact_quality_append_only.py
tests/test_v6_4_evidence_audit_integration.py
tests/test_v6_4_no_false_green.py
```

## 2. Workflow Instance Start

Must test:

```text
workflow_start_user_confirmed_allowed
workflow_start_missing_user_confirmation_denied
workflow_start_missing_human_authorization_denied
workflow_start_wrong_tenant_denied
workflow_start_idempotent_duplicate_returns_prior_runtime_result_ref
workflow_start_kill_switch_denied_before_mutation
workflow_start_records_incident_timeline_ref
```

## 3. Station Rerun

Must test:

```text
station_rerun_user_confirmed_allowed
station_rerun_source_agent_denied
station_rerun_old_attempt_retained
station_rerun_new_attempt_created
station_rerun_downstream_stale_marked
station_rerun_failed_attempt_remains_recoverable
station_rerun_idempotent_duplicate_returns_prior_runtime_result_ref
```

## 4. Artifact Write

Must test:

```text
artifact_write_requires_approval_gate
artifact_write_medium_risk_minimum
artifact_write_appends_new_version
artifact_write_never_overwrites_prior_version_silently
artifact_write_raw_artifact_content_denied
artifact_write_correction_appends_or_retracts_ref
artifact_write_records_producer_attempt_ref
```

## 5. Quality Evaluation Create

Must test:

```text
quality_evaluation_requires_approval_gate
quality_evaluation_medium_risk_minimum
quality_evaluation_appends_new_evaluation
quality_evaluation_never_overwrites_previous_score
quality_evaluation_correction_keeps_prior_score
quality_evaluation_records_quality_rule_ref_target_ref_evaluation_ref
```

## 6. Approved API Boundary

Must test:

```text
approved_api_without_human_authorization_denied
approved_api_with_expired_human_authorization_denied
approved_api_human_authorization_ref_expired_before_execution_denied
approved_api_wrong_tenant_denied
approved_api_wrong_workspace_denied
approved_api_source_agent_denied
approved_api_records_api_client_service_account_and_human_authorization_refs
approved_api_rate_limit_or_quota_denial_audited
```

## 7. Service Account Boundary

Must test:

```text
execution_envelope_actor_type_conditional_fields
service_account_without_human_authorization_denied
service_account_expired_authorization_denied
service_account_wrong_operation_denied
service_account_as_agent_executor_denied
service_account_records_human_authorization_ref
service_account_not_admin_override
```

## 8. Excluded Actions

Must test denial:

```text
business.event.emit
context.update
workflow.template.publish
approval.respond
connector.call
external_llm.call
```

## 9. Audit / Redaction

Must test:

```text
allow_path_records_v6_3_audit_event
deny_path_records_denial_audit_event
execution_evidence_contains_required_refs
runtime_report_projection_readonly
evidence_chain_projection_readonly
no_raw_secret_prompt_artifact_content_in_evidence_logs_html_json
```

## 10. Regression Commands

```text
./.venv/bin/python -m pytest tests/test_v6_4_*.py -q
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V6.x/v6_current_gap_analysis.drawio
```
