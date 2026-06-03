# V6-1 Identity / Tenant Test Matrix

文档状态：V6-1 implementation-ready test matrix。

## Contract Tests

```text
test_v6_1_staging_identity_provider_status
test_v6_1_valid_human_access_projects_identity_to_all_heads
test_v6_1_cross_tenant_denied
test_v6_1_wrong_workspace_denied
test_v6_1_wrong_project_denied
test_v6_1_wrong_app_denied
test_v6_1_service_account_missing_binding_denied
test_v6_1_service_account_wrong_operation_denied
test_v6_1_service_account_valid_operation_allowed
test_v6_1_source_agent_durable_mutation_denied
test_v6_1_evidence_redacts_sensitive_metadata
test_v6_1_no_false_green_claims
```

## E2E Evidence Scenarios

```text
real fixture: tenant_alpha / workspace_docs / project_v6 / app_workflow
human actor: user_1
service account actor: sa_report_reader
resource: workflow_instance wfi_v6_1
allowed operation: report.open
denied operation: workflow.instance.start from source=agent
staging IdP: staging_only unless real OIDC env is configured
```

## Regression

```text
./.venv/bin/python -m pytest tests/test_v6_1_identity_tenant.py -q
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V6.x/v6_current_gap_analysis.drawio
```

## Stop Conditions

```text
forbidden claim scan fails
staging fixture is claimed as enterprise auth ready
service account bypasses tenant boundary
source=agent can execute durable mutation
audit evidence leaks token / secret / raw payload
```
