from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v6_8_product_console import (
    V68ProductConsoleError,
    V68Panel,
    build_manual_confirmation,
    build_product_console_state,
    browser_route_decision,
    render_product_console_html,
    scan_rendered_html,
    validate_product_console_state,
)


FORBIDDEN_COPY = (
    "自动应用",
    "自动发布",
    "Agent 已执行",
    "Agent 已发布",
    "production-ready external app support",
    "complete Workflow Studio ready",
)


def make_context(actor_type: str = "human_user") -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v6_8",
        workspace_id="workspace_v6_8",
        project_id="project_v6_8",
        app_id="app_v6_8",
        actor_type=actor_type,
        actor_id="user_v6_8" if actor_type == "human_user" else "agent_v6_8",
        user_id="user_v6_8" if actor_type == "human_user" else None,
        agent_id="agent_v6_8" if actor_type == "agent" else None,
        session_id="session_v6_8" if actor_type == "agent" else None,
        request_id="request_v6_8",
        correlation_id="correlation_v6_8",
    )


def make_confirmation(context: IdentityContext | None = None):
    context = context or make_context()
    return build_manual_confirmation(
        context,
        operation="station.rerun",
        target_refs={"workflow_instance_id": "workflow-instance-v6-8", "station_id": "station-v6-8"},
        risk_flags=["medium_risk", "user_confirmation_required"],
        policy_decision_ref="policy-decision://v6-8/manual-confirmation",
        expires_at="2999-01-01T00:00:00+00:00",
    )


def make_state():
    context = make_context()
    confirmation = make_confirmation(context)
    return build_product_console_state(
        context,
        runtime_report={
            "workflow_instance_id": "workflow-instance-v6-8",
            "status": "running",
            "attempts": [{"attempt_id": "attempt-v6-8-1"}],
            "artifact_lineage": [{"artifact_id": "artifact-v6-8"}],
            "incident_timeline": [{"event_type": "worker_started"}],
        },
        evidence_review={
            "evidence_scope": "repo_backed_pilot_runtime_slice",
            "scenario_count": 10,
            "claim_violations": [],
            "redaction_status": "PASS",
        },
        audit_export={
            "audit_export_ref": "audit-export://v6-8/product-console",
            "authorized_view": True,
            "immutable_or_append_only": True,
        },
        external_app_admin={
            "app_id": "app_v6_8",
            "registration_status": "registered",
            "offboarding_revoked_credentials": True,
        },
        manual_confirmation=confirmation,
        browser_network_log=[
            "GET /bff/v6/runtime-report",
            "GET /bff/v6/evidence-review",
            "GET /bff/v6/audit-export",
            "GET /bff/v6/external-app-admin",
            "POST /bff/v6/manual-confirmation",
        ],
        source_refs={
            "runtime_report": "docs/design/V6.x/evidence/v6-7-distributed-runtime/acceptance-data.json",
            "evidence_review": "docs/design/V6.x/evidence/v6-7-distributed-runtime/result-summary.md",
            "audit_export": "docs/design/V6.x/evidence/v6-3-observability-audit/acceptance-data.json",
            "external_app_admin": "docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json",
        },
    )


def test_runtime_report_readonly_no_hidden_form() -> None:
    state = make_state()
    html = render_product_console_html(state)
    scan = scan_rendered_html(html)
    runtime_panel = next(panel for panel in state.panels if panel.panel_id == "runtime_report")

    assert runtime_panel.readonly is True
    assert runtime_panel.hidden_mutation_form_present is False
    assert scan["hidden_form_present"] is False
    assert scan["status"] == "PASS"


def test_evidence_review_readonly_no_execute_buttons() -> None:
    state = make_state()
    html = render_product_console_html(state)
    evidence_panel = next(panel for panel in state.panels if panel.panel_id == "evidence_review")
    scan = scan_rendered_html(html)

    assert evidence_panel.readonly is True
    assert set(evidence_panel.allowed_actions) == {"view", "export", "open_handoff"}
    assert scan["execution_button_hits"] == []


def test_audit_export_access_requires_authorized_view() -> None:
    state = make_state()
    audit_panel = next(panel for panel in state.panels if panel.panel_id == "audit_export")

    assert audit_panel.readonly is True
    assert audit_panel.data["authorized_view"] is True
    assert audit_panel.data["immutable_or_append_only"] is True


def test_external_app_admin_does_not_construct_runtime_truth() -> None:
    state = make_state()
    panel = next(panel for panel in state.panels if panel.panel_id == "external_app_admin")

    assert panel.constructs_runtime_truth is False
    assert panel.data["constructs_runtime_truth"] is False
    assert set(panel.allowed_actions) <= {"view", "open_evidence"}


def test_manual_confirmation_records_human_authorization_ref() -> None:
    confirmation = make_confirmation()
    dto = confirmation.to_dict()

    assert dto["human_authorization_ref"].startswith("human-auth://v6-8/")
    assert dto["actor_id"] == "user_v6_8"
    assert dto["operation"] == "station.rerun"
    assert dto["target_refs"]["workflow_instance_id"] == "workflow-instance-v6-8"
    assert dto["executes_runtime_action"] is False
    assert dto["audit_ref"].startswith("audit://")


def test_source_agent_manual_confirmation_denied() -> None:
    with pytest.raises(V68ProductConsoleError) as excinfo:
        make_confirmation(make_context(actor_type="agent"))

    assert excinfo.value.reason == "source_agent_denied"


def test_browser_no_direct_internal_runtime_routes() -> None:
    assert browser_route_decision("GET /bff/v6/runtime-report")["policy_decision"] == "allow"
    assert browser_route_decision("/v1/internal/runtime")["policy_decision"] == "deny"
    assert browser_route_decision("/v1/internal/executor")["policy_decision"] == "deny"


def test_browser_no_direct_v1_rpc_and_events_subscribe() -> None:
    assert browser_route_decision("/v1/rpc")["denial_reason"] == "internal_route_denied"
    assert browser_route_decision("/v1/events/subscribe")["denial_reason"] == "internal_route_denied"


def test_ui_no_auto_apply_auto_publish_agent_executed_copy() -> None:
    html = render_product_console_html(make_state())
    scan = scan_rendered_html(html)

    for copy in FORBIDDEN_COPY:
        assert copy not in html
    assert scan["forbidden_copy_hits"] == []
    assert scan["status"] == "PASS"


def test_mutable_panel_or_execution_action_is_rejected() -> None:
    state = make_state()
    bad_panel = V68Panel(
        panel_id="evidence_review",
        title="证据链审查",
        readonly=True,
        allowed_actions=("view", "Execute"),
        source_refs={},
        data={},
    )
    bad_state = state.__class__(
        console_id=state.console_id,
        tenant_context=state.tenant_context,
        bff_route_allowlist=state.bff_route_allowlist,
        browser_network_log=state.browser_network_log,
        panels=(bad_panel,),
        manual_confirmation=state.manual_confirmation,
        full_workflow_studio_gate=state.full_workflow_studio_gate,
        global_assertions=state.global_assertions,
        source_refs=state.source_refs,
    )

    with pytest.raises(V68ProductConsoleError) as excinfo:
        validate_product_console_state(bad_state)

    assert excinfo.value.reason == "execution_action"


def test_v6_8_planning_docs_reference_required_named_cases() -> None:
    docs = [
        Path("docs/design/V6.x/v6_8_product_console_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_8_browser_safety_test_matrix.md"),
        Path("docs/design/V6.x/v6_8_manual_confirmation_ux_contract.md"),
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in docs)
    for case in [
        "runtime_report_readonly_no_hidden_form",
        "evidence_review_readonly_no_execute_buttons",
        "audit_export_access_requires_authorized_view",
        "external_app_admin_does_not_construct_runtime_truth",
        "manual_confirmation_records_human_authorization_ref",
        "browser_no_direct_internal_runtime_routes",
        "browser_no_direct_v1_rpc",
        "browser_no_direct_v1_events_subscribe",
        "ui_no_auto_apply_auto_publish_agent_executed_copy",
    ]:
        assert case in text


def test_product_console_state_serializes_without_sensitive_fields() -> None:
    serialized = json.dumps(make_state().to_dict(), ensure_ascii=False)
    for forbidden in ("raw_artifact_content", "raw_connector_payload", "raw prompt", "Bearer ", "sk-"):
        assert forbidden not in serialized
