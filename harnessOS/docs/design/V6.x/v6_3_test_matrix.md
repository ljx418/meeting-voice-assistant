# V6-3 Observability / Audit Test Matrix

文档状态：V6-3 implementation-ready test matrix。

## Contract Tests

```text
test_v6_3_export_includes_v6_1_and_v6_2_events
test_v6_3_export_is_readonly_append_only_immutable
test_v6_3_source_agent_export_denied
test_v6_3_export_requires_user_confirmation
test_v6_3_event_correlation_coverage
test_v6_3_metric_alert_are_read_only
test_v6_3_incident_timeline_is_read_only
test_v6_3_raw_secret_and_raw_prompt_rejected
test_v6_3_no_runtime_truth_actions
```

## E2E Evidence Scenarios

```text
V6-1 identity event
V6-2 provider lifecycle event
V6-2 provider invocation event
confirmed audit export package
agent export denial
metric signal
alert decision
incident timeline with failure / retry / kill_switch / rollback refs
```

## Regression

```text
./.venv/bin/python -m pytest tests/test_v6_3_observability_audit.py -q
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V6.x/v6_current_gap_analysis.drawio
```

## Stop Conditions

```text
Audit Export becomes runtime mutation panel
source=agent can export audit package
metrics / alerts / timeline write runtime truth
raw secret / raw prompt / raw payload appears
forbidden claim scan fails
```
