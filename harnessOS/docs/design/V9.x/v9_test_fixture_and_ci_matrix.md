# V9 Test Fixture And CI Matrix

文档状态：V9 P0 test fixture plan / required before stage implementation。

## 1. Test Case Contract

Every V9 test case must specify:

```text
test_id
owner_stage
input_fixture
expected_output
expected_denied_state
expected_evidence_record
expected_audit_ref
expected_redaction_behavior
expected_rollback_or_correction_behavior
ci_command
blocking_severity
```

Current P0 fixture roots:

```text
docs/design/V9.x/fixtures/schema-negative/
docs/design/V9.x/fixtures/evidence/
```

## 2. Required Negative Fixtures

```text
source_agent_durable_mutation
expired_human_authorization_ref
wrong_tenant_human_authorization_ref
raw_secret_in_evidence
fan_in_missing_attribution
retry_overwrites_old_attempt
auto_commit_without_human_approval
auto_push_without_release_gate
auto_deploy_without_production_gate
terminal_workspace_escape
terminal_symlink_escape
studio_direct_runtime_write
studio_hidden_mutation_form
v9_8_with_planning_docs_only
```

## 3. CI Gates

Planned commands:

```text
python -m json.tool docs/design/V9.x/schemas/*.schema.json
python -m json.tool docs/design/V9.x/fixtures/schema-negative/*.json
python -m json.tool docs/design/V9.x/fixtures/evidence/*.json
xmllint --noout docs/design/V9.x/v9_current_gap_analysis.drawio
rg -in "<forbidden-claim-regex>" docs/design/V9.x
python -m pytest tests/test_v9_contracts_*.py -q
python -m pytest tests/test_v9_evidence_package_*.py -q
python -m pytest tests/test_v9_no_false_green_*.py -q
```

## 4. Blocking Severity

```text
P0 blocks stage implementation.
P1 blocks stage completion.
P2 requires documented proceed decision.
```

## 5. Acceptance Rule

No V9 implementation stage may start until its fixtures and CI commands are listed and accepted. No V9 stage may complete if a P0/P1 fixture fails.

## 6. Front-Stage Fixture-To-Test Matrix

| Stage | Fixture | Expected Result |
| --- | --- | --- |
| V9-1 | `schema-negative/source_agent_durable_mutation.json` | rejected by envelope validator and CapabilityResolver |
| V9-1 | `fixtures/evidence/v9_1_contract_freeze_sample.json` | accepted only as contract_freeze, not runtime evidence |
| V9-2 | `schema-negative/expired_human_authorization_ref.json` | rejected by HumanAuthorizationRef validator |
| V9-2 | `schema-negative/raw_secret_in_evidence.json` | rejected by evidence schema and redaction scan |
| V9-3 | `schema-negative/artifact_lineage_missing_producer_attempt.json` | rejected by artifact lineage schema |
| V9-4 | coding workflow no-auto-deploy fixture | must deny deploy and record evidence; fixture still required before implementation |
| V9-8 | `fixtures/evidence/v9_8_reject_planning_only_sample.json` | final validator returns BLOCKED, not PASS |
