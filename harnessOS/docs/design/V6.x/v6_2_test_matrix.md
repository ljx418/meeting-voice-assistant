# V6-2 Credential / Provider Test Matrix

文档状态：V6-2 implementation-ready test matrix。

## Contract Tests

```text
test_v6_2_lease_is_tenant_app_audience_operation_bound
test_v6_2_valid_invocation_records_redacted_refs
test_v6_2_expired_lease_denied
test_v6_2_wrong_audience_denied
test_v6_2_wrong_operation_denied
test_v6_2_revoked_credential_denied
test_v6_2_emergency_revoke_blocks_invocation
test_v6_2_model_mismatch_denied
test_v6_2_capability_mismatch_denied
test_v6_2_raw_secret_and_raw_prompt_rejected
test_v6_2_source_agent_lifecycle_mutation_denied
```

## E2E Evidence Scenarios

```text
fixture: tenant_alpha / workspace_docs / project_v6 / app_workflow
provider: minimax fixture profile
model_ref: MiniMax-M2.1
credential_ref: env://MINIMAX_API_KEY
lease audience: llm_provider:minimax
lease operation: provider.invoke
valid invocation: PASS
expired lease: DENY
wrong audience: DENY
wrong operation: DENY
revoked credential: DENY
```

## Regression

```text
./.venv/bin/python -m pytest tests/test_v6_2_credential_provider.py -q
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V6.x/v6_current_gap_analysis.drawio
```

## Stop Conditions

```text
raw secret appears in evidence
raw prompt appears in evidence
lease lacks tenant/app/audience/operation binding
revoked credential invocation is allowed
expired lease invocation is allowed
source=agent can mutate credential lifecycle
```
