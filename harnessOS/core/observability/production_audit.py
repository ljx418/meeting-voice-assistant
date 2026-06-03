"""V6.3 production pilot observability and audit export helpers.

This module packages V5.3 observability primitives into V6.3 review-scoped
audit exports, metrics, alerts, and incident timelines. It does not add
runtime mutation routes or production SIEM integration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from core.auth.tenant_boundary import IdentityContext
from core.observability.audit_export import (
    AlertEvent,
    AlertRule,
    AlertRuleEngine,
    AuditExportError,
    AuditExportPackage,
    AuditExportService,
    AuditRetentionPolicy,
    IncidentTimelineBuilder,
    IncidentTimelineEntry,
    MetricRecord,
    MetricsEmitter,
    ObservabilityEvent,
    SecurityEventLog,
)


RUNTIME_MUTATION_ACTIONS = {"Apply", "Publish", "Approve", "Reject", "Execute", "Run"}


@dataclass(frozen=True)
class ProductionAuditExportPackage:
    """V6.3 read-only append-only audit export wrapper."""

    package: AuditExportPackage
    append_only: bool
    immutable: bool
    runtime_truth_constructed: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = self.package.to_dict()
        data["append_only"] = self.append_only
        data["immutable"] = self.immutable
        data["runtime_truth_constructed"] = self.runtime_truth_constructed
        return data


class ProductionAuditService:
    """V6.3 production pilot audit service."""

    def __init__(self) -> None:
        self.log = SecurityEventLog()
        self.export_service = AuditExportService()
        self.metrics = MetricsEmitter()
        self.alerts = AlertRuleEngine()
        self.timelines = IncidentTimelineBuilder()

    def record_production_event(
        self,
        context: IdentityContext,
        *,
        event_type: str,
        operation: str,
        target_refs: Mapping[str, str],
        policy_decision: str,
        source_refs: Mapping[str, str],
        metadata: Mapping[str, Any] | None = None,
        user_confirmed: bool = False,
    ) -> ObservabilityEvent:
        """Record a V6.3 event and require full identity/correlation coverage."""
        event = self.log.record_event(
            context,
            event_type=event_type,
            operation=operation,
            target_refs=target_refs,
            policy_decision=policy_decision,
            source_refs=source_refs,
            metadata=metadata,
            user_confirmed=user_confirmed,
        )
        require_event_coverage(event)
        return event

    def create_production_export(
        self,
        context: IdentityContext,
        *,
        events: Sequence[ObservabilityEvent],
        retention_policy: AuditRetentionPolicy,
        requested_by: str,
        source: str,
        user_confirmed: bool,
        time_range: Mapping[str, str],
    ) -> ProductionAuditExportPackage:
        """Create a V6.3 read-only append-only audit export package."""
        for event in events:
            require_event_coverage(event)
        package = self.export_service.create_export_package(
            context,
            events=events,
            retention_policy=retention_policy,
            requested_by=requested_by,
            source=source,
            user_confirmed=user_confirmed,
            time_range=time_range,
        )
        data = package.to_dict()
        if not data.get("readonly"):
            raise AuditExportError("AUDIT_EXPORT_READONLY_REQUIRED", "Audit export must be read-only.", reason="readonly_required")
        if RUNTIME_MUTATION_ACTIONS.intersection(set(data.get("allowed_actions", []))):
            raise AuditExportError("AUDIT_EXPORT_ACTION_DENIED", "Audit export cannot expose runtime mutation actions.", reason="runtime_action_denied")
        return ProductionAuditExportPackage(package=package, append_only=True, immutable=True)

    def emit_readonly_metric(
        self,
        context: IdentityContext,
        *,
        metric_name: str,
        value: float,
        source_refs: Mapping[str, str],
        labels: Mapping[str, str] | None = None,
    ) -> MetricRecord:
        metric = self.metrics.emit_metric(context, metric_name=metric_name, value=value, source_refs=source_refs, labels=labels)
        if not metric.readonly:
            raise AuditExportError("AUDIT_METRIC_READONLY_REQUIRED", "Metric must be read-only.", reason="readonly_required")
        return metric

    def evaluate_readonly_alert(
        self,
        context: IdentityContext,
        *,
        rule: AlertRule,
        metric: MetricRecord,
        event_refs: Sequence[str],
    ) -> AlertEvent | None:
        alert = self.alerts.evaluate(context, rule=rule, metric=metric, event_refs=event_refs)
        if alert is not None and not alert.readonly:
            raise AuditExportError("AUDIT_ALERT_READONLY_REQUIRED", "Alert must be read-only.", reason="readonly_required")
        return alert

    def build_readonly_timeline(
        self,
        context: IdentityContext,
        *,
        incident_id: str,
        events: Sequence[ObservabilityEvent],
        severity: str,
    ) -> list[IncidentTimelineEntry]:
        timeline = self.timelines.build(context, incident_id=incident_id, events=events, severity=severity)
        for entry in timeline:
            data = entry.to_dict()
            if not data.get("readonly"):
                raise AuditExportError("AUDIT_TIMELINE_READONLY_REQUIRED", "Incident timeline must be read-only.", reason="readonly_required")
            if RUNTIME_MUTATION_ACTIONS.intersection(set(data.get("allowed_actions", []))):
                raise AuditExportError("AUDIT_TIMELINE_ACTION_DENIED", "Incident timeline cannot expose runtime mutation actions.", reason="runtime_action_denied")
        return timeline


def require_event_coverage(event: ObservabilityEvent) -> None:
    """Validate V6.3 required identity and correlation fields."""
    data = event.to_dict()
    required = [
        "tenant_id",
        "workspace_id",
        "project_id",
        "app_id",
        "actor_type",
        "actor_id",
        "request_id",
        "correlation_id",
        "operation",
        "target_refs",
        "source_refs",
        "policy_decision",
        "redaction_status",
    ]
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise AuditExportError("AUDIT_EVENT_COVERAGE_REQUIRED", "Observability event is missing required V6.3 fields.", reason="missing_required_field", resource=missing[0])


def assert_no_runtime_truth(data: Mapping[str, Any]) -> None:
    """Reject audit/read-model data that exposes runtime mutation actions."""
    text = str(data)
    if any(action in text for action in RUNTIME_MUTATION_ACTIONS):
        raise AuditExportError("AUDIT_RUNTIME_TRUTH_DENIED", "Audit read models cannot expose runtime mutation actions.", reason="runtime_truth_action")


def to_redacted_dict(value: Any) -> dict[str, Any]:
    """Return a dataclass/dto dictionary for evidence scripts."""
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError(f"Unsupported value type: {type(value)!r}")
