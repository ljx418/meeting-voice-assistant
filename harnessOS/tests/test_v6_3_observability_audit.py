from __future__ import annotations

import pytest

from core.auth.tenant_boundary import IdentityContext
from core.observability.audit_export import AlertRule, AuditExportError, AuditRetentionPolicy
from core.observability.production_audit import ProductionAuditService, assert_no_runtime_truth


def context(*, actor_type: str = "human_user") -> IdentityContext:
    kwargs = {"user_id": "user_v6"} if actor_type == "human_user" else {}
    if actor_type == "agent":
        kwargs = {"agent_id": "agent_v6", "session_id": "agent_session_v6"}
    return IdentityContext(
        tenant_id="tenant_alpha",
        workspace_id="workspace_docs",
        project_id="project_v6",
        app_id="app_workflow",
        actor_type=actor_type,
        actor_id="actor_v6",
        request_id="req_v6_3",
        correlation_id="corr_v6_3",
        **kwargs,
    )


def policy(ctx: IdentityContext) -> AuditRetentionPolicy:
    return AuditRetentionPolicy(
        retention_policy_id="retention_v6_3",
        tenant_id=ctx.tenant_id,
        workspace_id=ctx.workspace_id,
        evidence_type="production_pilot",
        retention_days=90,
        legal_hold=False,
        export_allowed=True,
        redaction_required=True,
        owner_stage="V6-3",
    )


def events(service: ProductionAuditService, ctx: IdentityContext):
    identity_event = service.record_production_event(
        ctx,
        event_type="identity.scope.allowed",
        operation="report.open",
        target_refs={"workflow_instance_id": "wfi_v6_1"},
        policy_decision="allow",
        source_refs={"evidence_ref": "evidence://v6-1/identity"},
        metadata={"stage": "V6-1"},
    )
    provider_event = service.record_production_event(
        ctx,
        event_type="provider.invocation.recorded",
        operation="provider.invoke",
        target_refs={"provider_profile_id": "provider_profile_minimax_v6", "credential_lease_id": "lease_v6_2"},
        policy_decision="allow",
        source_refs={"evidence_ref": "evidence://v6-2/provider", "runtime_result_ref": "runtime://v6-2/provider-smoke"},
        metadata={"stage": "V6-2", "provider": "minimax", "model_ref": "MiniMax-M2.1"},
    )
    return [identity_event, provider_event]


def test_v6_3_export_includes_v6_1_and_v6_2_events() -> None:
    service = ProductionAuditService()
    ctx = context()
    package = service.create_production_export(
        ctx,
        events=events(service, ctx),
        retention_policy=policy(ctx),
        requested_by=ctx.actor_id,
        source="user",
        user_confirmed=True,
        time_range={"from": "2026-06-01T00:00:00Z", "to": "2026-06-02T00:00:00Z"},
    ).to_dict()

    assert package["event_count"] == 2
    assert package["readonly"] is True
    assert package["append_only"] is True
    assert package["immutable"] is True
    assert package["runtime_truth_constructed"] is False
    assert set(package["allowed_actions"]) == {"view", "export", "open_evidence"}


def test_v6_3_source_agent_export_denied() -> None:
    service = ProductionAuditService()
    ctx = context(actor_type="agent")
    with pytest.raises(AuditExportError) as exc:
        service.create_production_export(
            ctx,
            events=[],
            retention_policy=policy(ctx),
            requested_by=ctx.actor_id,
            source="agent",
            user_confirmed=True,
            time_range={"from": "2026-06-01T00:00:00Z", "to": "2026-06-02T00:00:00Z"},
        )
    assert exc.value.code == "AUDIT_EXPORT_AGENT_DENIED"


def test_v6_3_export_requires_user_confirmation() -> None:
    service = ProductionAuditService()
    ctx = context()
    with pytest.raises(AuditExportError) as exc:
        service.create_production_export(
            ctx,
            events=events(service, ctx),
            retention_policy=policy(ctx),
            requested_by=ctx.actor_id,
            source="user",
            user_confirmed=False,
            time_range={"from": "2026-06-01T00:00:00Z", "to": "2026-06-02T00:00:00Z"},
        )
    assert exc.value.code == "AUDIT_EXPORT_CONFIRMATION_REQUIRED"


def test_v6_3_event_correlation_coverage() -> None:
    service = ProductionAuditService()
    ctx = context()
    event = events(service, ctx)[0].to_dict()
    for field in ("tenant_id", "workspace_id", "project_id", "app_id", "actor_id", "request_id", "correlation_id"):
        assert event[field]


def test_v6_3_metric_alert_are_read_only() -> None:
    service = ProductionAuditService()
    ctx = context()
    event_list = events(service, ctx)
    metric = service.emit_readonly_metric(
        ctx,
        metric_name="audit_export.event_count",
        value=2,
        source_refs={"audit_export_ref": "audit_export://v6-3"},
        labels={"stage": "V6-3"},
    )
    alert = service.evaluate_readonly_alert(
        ctx,
        rule=AlertRule(rule_id="rule_v6_3", metric_name="audit_export.event_count", threshold=1, severity="warning", owner_stage="V6-3", source_refs={}),
        metric=metric,
        event_refs=[event.event_id for event in event_list],
    )

    assert metric.readonly is True
    assert alert is not None
    assert alert.readonly is True


def test_v6_3_incident_timeline_is_read_only_and_no_runtime_actions() -> None:
    service = ProductionAuditService()
    ctx = context()
    timeline = service.build_readonly_timeline(ctx, incident_id="incident_v6_3", events=events(service, ctx), severity="warning")
    assert timeline
    for entry in timeline:
        data = entry.to_dict()
        assert data["readonly"] is True
        assert set(data["allowed_actions"]) == {"view", "export", "open_evidence"}
        assert_no_runtime_truth(data)


def test_v6_3_raw_secret_and_raw_prompt_rejected() -> None:
    service = ProductionAuditService()
    ctx = context()
    with pytest.raises(AuditExportError) as exc:
        service.record_production_event(
            ctx,
            event_type="provider.invocation.recorded",
            operation="provider.invoke",
            target_refs={"provider_profile_id": "provider_profile_minimax_v6"},
            policy_decision="allow",
            source_refs={"evidence_ref": "evidence://v6-2/provider"},
            metadata={"raw_prompt": "do not store"},
        )
    assert exc.value.code == "AUDIT_REDACTION_DENIED"
