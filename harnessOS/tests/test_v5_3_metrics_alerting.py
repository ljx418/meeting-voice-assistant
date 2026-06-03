from __future__ import annotations

from core.observability.audit_export import AlertRule, AlertRuleEngine, MetricsEmitter
from tests.v5_3_observability_support import make_context, make_provider_invocation_event


def test_metrics_and_alerts_are_read_only_and_link_redacted_refs() -> None:
    context = make_context()
    event = make_provider_invocation_event(context)
    metric = MetricsEmitter().emit_metric(
        context,
        metric_name="audit_export.denied.count",
        value=3,
        source_refs={"event_ref": event.event_id},
        labels={"owner_stage": "V5-3", "category": "security"},
    )
    alert = AlertRuleEngine().evaluate(
        context,
        rule=AlertRule(
            rule_id="rule_audit_denial",
            metric_name="audit_export.denied.count",
            threshold=1,
            severity="warning",
            owner_stage="V5-3",
            source_refs={"test_matrix": "docs/design/V5.x/v5_3_test_matrix.md"},
        ),
        metric=metric,
        event_refs=[event.event_id],
    )

    assert metric.readonly is True
    assert metric.redaction_status == "redacted"
    assert alert is not None
    alert_data = alert.to_dict()
    assert alert_data["readonly"] is True
    assert alert_data["event_refs"] == [event.event_id]
    assert alert_data["redaction_status"] == "redacted"
