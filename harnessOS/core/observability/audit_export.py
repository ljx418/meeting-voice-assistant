"""V5.3 observability and audit export primitives.

This module implements a focused dev/local core slice for audit events,
retention/export packages, metrics, alerting, and incident timelines. It does
not add production audit export routes, Agent executor authority, or runtime
mutation paths.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


FORBIDDEN_KEYS = {
    "authorization",
    "bearer",
    "capability_token",
    "subscription_token",
    "secret",
    "api_key",
    "apikey",
    "raw prompt",
    "raw_prompt",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "upstream signed url",
    "upstream_signed_url",
}

FORBIDDEN_TEXT = (
    "authorization:",
    "bearer ",
    "capability_token",
    "subscription_token",
    "raw prompt",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "upstream signed url",
    "upstream_signed_url",
)

READ_ONLY_ACTIONS = ("view", "export", "open_evidence")
AUDIT_EXPORT_MUTATIONS = {"audit.export.create"}


class AuditExportError(ValueError):
    """Stable V5.3 observability/audit-export denial."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        """Return a redacted error shape."""
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class ObservabilityEvent:
    """Tenant-bound observability event with redacted metadata."""

    event_id: str
    event_type: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    actor_type: str
    actor_id: str
    request_id: str
    correlation_id: str
    operation: str
    target_refs: dict[str, str]
    policy_decision: str
    source_refs: dict[str, str]
    redaction_status: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)
    user_confirmed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted event DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class AuditRetentionPolicy:
    """Tenant-bound audit retention/export policy."""

    retention_policy_id: str
    tenant_id: str
    workspace_id: str
    evidence_type: str
    retention_days: int
    legal_hold: bool
    export_allowed: bool
    redaction_required: bool
    owner_stage: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return policy DTO."""
        return asdict(self)


@dataclass(frozen=True)
class AuditExportPackage:
    """Read-only audit export package."""

    export_id: str
    tenant_id: str
    workspace_id: str
    requested_by: str
    request_id: str
    correlation_id: str
    time_range: dict[str, str]
    retention_policy_id: str
    included_event_refs: tuple[str, ...]
    included_evidence_refs: tuple[str, ...]
    event_count: int
    redaction_status: str
    checksum: str
    created_at: str
    readonly: bool = True
    allowed_actions: tuple[str, ...] = READ_ONLY_ACTIONS

    def to_dict(self) -> dict[str, Any]:
        """Return export DTO."""
        data = asdict(self)
        data["included_event_refs"] = list(self.included_event_refs)
        data["included_evidence_refs"] = list(self.included_evidence_refs)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


@dataclass(frozen=True)
class MetricRecord:
    """Read-only metric output linked to redacted source refs."""

    metric_id: str
    metric_name: str
    value: float
    tenant_id: str
    workspace_id: str
    source_refs: dict[str, str]
    labels: dict[str, str]
    request_id: str
    correlation_id: str
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return metric DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class AlertRule:
    """Read-only alerting rule."""

    rule_id: str
    metric_name: str
    threshold: float
    severity: str
    owner_stage: str
    source_refs: dict[str, str]


@dataclass(frozen=True)
class AlertEvent:
    """Alert output linked to redacted event or metric refs."""

    alert_id: str
    rule_id: str
    metric_ref: str
    event_refs: tuple[str, ...]
    tenant_id: str
    workspace_id: str
    severity: str
    status: str
    request_id: str
    correlation_id: str
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return alert DTO."""
        data = asdict(self)
        data["event_refs"] = list(self.event_refs)
        return mask_value(data)


@dataclass(frozen=True)
class IncidentTimelineEntry:
    """Read-only incident timeline entry."""

    timeline_entry_id: str
    incident_id: str
    tenant_id: str
    workspace_id: str
    correlation_id: str
    event_ref: str
    evidence_ref: str
    operation: str
    severity: str
    summary: str
    created_at: str
    redaction_status: str
    readonly: bool = True
    allowed_actions: tuple[str, ...] = READ_ONLY_ACTIONS

    def to_dict(self) -> dict[str, Any]:
        """Return timeline DTO."""
        data = asdict(self)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


class SecurityEventLog:
    """In-memory security event log for focused V5.3 validation."""

    def __init__(self) -> None:
        self.events: list[ObservabilityEvent] = []

    def record_event(
        self,
        context: IdentityContext,
        *,
        event_type: str,
        operation: str,
        target_refs: Mapping[str, str],
        policy_decision: str,
        source_refs: Mapping[str, str] | None = None,
        metadata: Mapping[str, Any] | None = None,
        user_confirmed: bool = False,
    ) -> ObservabilityEvent:
        """Record a redacted event and reject raw payload fields."""
        _reject_sensitive_mapping(target_refs, resource="target_refs")
        _reject_sensitive_mapping(source_refs or {}, resource="source_refs")
        _reject_sensitive_mapping(metadata or {}, resource="metadata")
        event = ObservabilityEvent(
            event_id=f"obs_event_{uuid4().hex}",
            event_type=_required_text(event_type, "event_type"),
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            actor_type=context.actor_type,
            actor_id=context.actor_id,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            operation=_required_text(operation, "operation"),
            target_refs=dict(target_refs),
            policy_decision=_required_text(policy_decision, "policy_decision"),
            source_refs=dict(source_refs or {}),
            redaction_status="redacted",
            created_at=_now(),
            metadata=dict(mask_value(metadata or {})),
            user_confirmed=user_confirmed,
        )
        self.events.append(event)
        return event


class AuditExportService:
    """Create read-only audit export packages from redacted events."""

    def create_export_package(
        self,
        context: IdentityContext,
        *,
        events: Sequence[ObservabilityEvent],
        retention_policy: AuditRetentionPolicy,
        requested_by: str,
        source: str,
        user_confirmed: bool,
        time_range: Mapping[str, str],
    ) -> AuditExportPackage:
        """Create an audit export package with confirmation and scope guards."""
        if source == "agent" or context.actor_type == "agent":
            raise AuditExportError("AUDIT_EXPORT_AGENT_DENIED", "Agent source cannot export audit packages.", reason="agent_export_denied")
        if not user_confirmed:
            raise AuditExportError("AUDIT_EXPORT_CONFIRMATION_REQUIRED", "Audit export requires user_confirmed=true.", reason="missing_user_confirmation")
        if not retention_policy.export_allowed:
            raise AuditExportError("AUDIT_EXPORT_POLICY_DENIED", "Retention policy does not allow export.", reason="export_not_allowed")
        if not retention_policy.redaction_required:
            raise AuditExportError("AUDIT_EXPORT_REDACTION_REQUIRED", "Audit export requires redaction.", reason="redaction_required")
        _require_policy_scope(context, retention_policy)
        for event in events:
            _require_event_scope(context, event)
        redacted_events = [event.to_dict() for event in events]
        checksum = hashlib.sha256(json.dumps(redacted_events, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        return AuditExportPackage(
            export_id=f"audit_export_{uuid4().hex}",
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            requested_by=_required_text(requested_by, "requested_by"),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            time_range=dict(time_range),
            retention_policy_id=retention_policy.retention_policy_id,
            included_event_refs=tuple(event.event_id for event in events),
            included_evidence_refs=tuple(_evidence_ref(event) for event in events),
            event_count=len(events),
            redaction_status="redacted",
            checksum=checksum,
            created_at=_now(),
        )


class MetricsEmitter:
    """Create read-only metrics from redacted observability sources."""

    def emit_metric(
        self,
        context: IdentityContext,
        *,
        metric_name: str,
        value: float,
        source_refs: Mapping[str, str],
        labels: Mapping[str, str] | None = None,
    ) -> MetricRecord:
        """Emit a metric without storing sensitive values."""
        _reject_sensitive_mapping(source_refs, resource="source_refs")
        _reject_sensitive_mapping(labels or {}, resource="labels")
        return MetricRecord(
            metric_id=f"metric_{uuid4().hex}",
            metric_name=_required_text(metric_name, "metric_name"),
            value=float(value),
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            source_refs=dict(source_refs),
            labels=dict(labels or {}),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            redaction_status="redacted",
        )


class AlertRuleEngine:
    """Evaluate read-only alert rules from metrics."""

    def evaluate(
        self,
        context: IdentityContext,
        *,
        rule: AlertRule,
        metric: MetricRecord,
        event_refs: Sequence[str],
    ) -> AlertEvent | None:
        """Return an alert event when the metric crosses the rule threshold."""
        _require_metric_scope(context, metric)
        _reject_sensitive_mapping(rule.source_refs, resource="rule.source_refs")
        if metric.metric_name != rule.metric_name or metric.value < rule.threshold:
            return None
        return AlertEvent(
            alert_id=f"alert_{uuid4().hex}",
            rule_id=rule.rule_id,
            metric_ref=metric.metric_id,
            event_refs=tuple(event_refs),
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            severity=rule.severity,
            status="triggered",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            redaction_status="redacted",
        )


class IncidentTimelineBuilder:
    """Build read-only incident timelines from observability events."""

    def build(
        self,
        context: IdentityContext,
        *,
        incident_id: str,
        events: Sequence[ObservabilityEvent],
        severity: str,
    ) -> list[IncidentTimelineEntry]:
        """Build a sorted read-only timeline for one correlation chain."""
        entries: list[IncidentTimelineEntry] = []
        for event in sorted(events, key=lambda item: item.created_at):
            _require_event_scope(context, event)
            entries.append(
                IncidentTimelineEntry(
                    timeline_entry_id=f"timeline_{uuid4().hex}",
                    incident_id=_required_text(incident_id, "incident_id"),
                    tenant_id=context.tenant_id,
                    workspace_id=context.workspace_id,
                    correlation_id=event.correlation_id,
                    event_ref=event.event_id,
                    evidence_ref=_evidence_ref(event),
                    operation=event.operation,
                    severity=severity,
                    summary=f"{event.event_type}: {event.operation}",
                    created_at=event.created_at,
                    redaction_status="redacted",
                )
            )
        return entries


def _reject_sensitive_mapping(data: Mapping[str, Any], *, resource: str) -> None:
    for key, value in data.items():
        lowered_key = str(key).strip().lower()
        normalized_key = lowered_key.replace("-", "_")
        if lowered_key in FORBIDDEN_KEYS or normalized_key in FORBIDDEN_KEYS or "token" in lowered_key or "secret" in lowered_key or "raw_" in lowered_key:
            raise AuditExportError("AUDIT_REDACTION_DENIED", "Sensitive fields are not allowed in observability outputs.", reason="sensitive_field", resource=f"{resource}.{key}")
        if isinstance(value, Mapping):
            _reject_sensitive_mapping(value, resource=f"{resource}.{key}")
        elif isinstance(value, str):
            lowered_value = value.lower()
            if any(pattern in lowered_value for pattern in FORBIDDEN_TEXT) or "sk-" in lowered_value or "api_key=" in lowered_value or "secret=" in lowered_value:
                raise AuditExportError("AUDIT_REDACTION_DENIED", "Sensitive values are not allowed in observability outputs.", reason="sensitive_value", resource=f"{resource}.{key}")
        elif isinstance(value, list | tuple):
            for index, item in enumerate(value):
                if isinstance(item, Mapping):
                    _reject_sensitive_mapping(item, resource=f"{resource}.{key}[{index}]")
                elif isinstance(item, str):
                    lowered_item = item.lower()
                    if any(pattern in lowered_item for pattern in FORBIDDEN_TEXT) or "sk-" in lowered_item:
                        raise AuditExportError("AUDIT_REDACTION_DENIED", "Sensitive values are not allowed in observability outputs.", reason="sensitive_value", resource=f"{resource}.{key}[{index}]")


def _required_text(value: str, resource: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuditExportError("AUDIT_FIELD_REQUIRED", f"{resource} is required.", reason="missing_required_field", resource=resource)
    return value.strip()


def _require_policy_scope(context: IdentityContext, policy: AuditRetentionPolicy) -> None:
    if policy.tenant_id != context.tenant_id or policy.workspace_id != context.workspace_id:
        raise AuditExportError("AUDIT_EXPORT_SCOPE_DENIED", "Retention policy is outside actor scope.", reason="scope_mismatch", resource=policy.retention_policy_id)


def _require_event_scope(context: IdentityContext, event: ObservabilityEvent) -> None:
    if event.tenant_id != context.tenant_id or event.workspace_id != context.workspace_id or event.project_id != context.project_id or event.app_id != context.app_id:
        raise AuditExportError("AUDIT_EXPORT_SCOPE_DENIED", "Event is outside actor scope.", reason="scope_mismatch", resource=event.event_id)


def _require_metric_scope(context: IdentityContext, metric: MetricRecord) -> None:
    if metric.tenant_id != context.tenant_id or metric.workspace_id != context.workspace_id:
        raise AuditExportError("AUDIT_EXPORT_SCOPE_DENIED", "Metric is outside actor scope.", reason="scope_mismatch", resource=metric.metric_id)


def _evidence_ref(event: ObservabilityEvent) -> str:
    return event.source_refs.get("evidence_ref") or f"evidence://{event.correlation_id}/{event.event_id}"


def _now() -> str:
    return datetime.now(UTC).isoformat()
