# V6-5 Test Matrix

文档状态：V6-5 detailed planning / test matrix。本文定义 V6-5 实现前测试矩阵。

## 1. Focused Tests

```text
tests/test_v6_5_agent_execution_intent.py
tests/test_v6_5_agent_capability_decision.py
tests/test_v6_5_agent_handoff.py
tests/test_v6_5_minimax_intent_invocation.py
tests/test_v6_5_agent_mutation_denial.py
tests/test_v6_5_no_false_green.py
```

## 2. Required Cases

```text
minimax_key_missing_blocks_v6_5_pass
minimax_real_invocation_records_provider_model_config_source
minimax_invocation_redacts_raw_prompt_and_raw_payload
agent_intent_for_workflow_start_creates_handoff
agent_intent_for_station_rerun_creates_handoff
agent_intent_for_artifact_write_requires_approval_gate
agent_intent_for_quality_evaluation_requires_approval_gate
agent_intent_for_excluded_operation_denied
agent_malformed_intent_parse_failed
source_agent_controlled_executor_mutation_denied
handoff_without_human_confirmation_blocked
human_confirmed_handoff_can_create_v6_4_request
no_false_green_claim_scan_passes
```

## 3. Regression Tests

```text
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V6.x/v6_current_gap_analysis.drawio
```

## 4. Stop Conditions

Stop V6-5 implementation if:

```text
MiniMax invocation cannot be evidenced
raw credential / raw prompt / raw artifact content leaks
source=agent durable mutation succeeds
handoff bypasses human confirmation
No False Green claim scan fails
```
