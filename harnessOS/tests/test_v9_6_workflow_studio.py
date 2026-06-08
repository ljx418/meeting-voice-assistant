from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v9_6_workflow_studio import (
    V96StudioPanel,
    V96WorkflowStudioError,
    browser_route_decision,
    build_manual_confirmation,
    build_workflow_diff_proposal,
    build_workflow_studio_state,
    render_workflow_studio_html,
    scan_rendered_html,
    validate_workflow_studio_state,
)


OUT_DIR = Path("docs/design/V9.x/evidence/v9-6-workflow-studio")


def make_context(actor_type: str = "human_user") -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_6",
        workspace_id="workspace_v9_6",
        project_id="project_v9_6",
        app_id="app_v9_6",
        actor_type=actor_type,
        actor_id="user_v9_6_reviewer" if actor_type == "human_user" else "agent_v9_6",
        user_id="user_v9_6_reviewer" if actor_type == "human_user" else None,
        agent_id="agent_v9_6" if actor_type == "agent" else None,
        request_id="request_v9_6",
        correlation_id="correlation_v9_6",
    )


def make_state():
    context = make_context()
    proposal = build_workflow_diff_proposal(
        context,
        natural_language_goal="新增安全审查 Agent，并减少一个冗余审查工位。",
        workflow_spec_ref="workflow-spec://v9-6/test",
        target_refs={"workflow_id": "workflow-v9-6", "workflow_version_id": "workflow-version-v9-6"},
    )
    confirmation = build_manual_confirmation(context, proposal=proposal, expires_at="2999-01-01T00:00:00+00:00")
    return build_workflow_studio_state(
        context,
        workflow_graph={"nodes": ["intent", "architect", "security-review"], "edges": [["intent", "architect"], ["architect", "security-review"]]},
        station_agent_profiles=[
            {"station_id": "intent", "agent_id": "agent-intent", "role": "目标澄清"},
            {"station_id": "architect", "agent_id": "agent-architect", "role": "工作流架构"},
            {"station_id": "security-review", "agent_id": "agent-security", "role": "安全审查"},
        ],
        runtime_report={"status": "ready_for_review", "attempts": [{"attempt_id": "attempt-v9-6-1"}]},
        evidence_chain={"evidence_refs": ["evidence://v9-3", "evidence://v9-4", "evidence://v9-5"], "claim_scan": "PASS", "redaction_scan": "PASS"},
        artifact_lineage=[{"artifact_id": "artifact-v9-6", "producer_agent_id": "agent-architect", "producer_attempt_id": "attempt-v9-6-1"}],
        workflow_diff_proposal=proposal,
        manual_confirmation=confirmation,
        browser_network_log=[
            "GET /bff/v9/studio-state",
            "GET /bff/v9/runtime-report",
            "GET /bff/v9/evidence-chain",
            "GET /bff/v9/workflow-blueprint",
            "POST /bff/v9/workflow-diff-proposal",
            "POST /bff/v9/manual-confirmation",
            "POST /bff/v9/review-handoff",
        ],
        source_refs={
            "workflow_blueprint": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
            "agent_profiles": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/user-scenarios.json",
            "runtime_report": "docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
            "evidence_chain": "docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json",
            "artifact_lineage": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
        },
    )


def test_v9_6_studio_loads_workflow_graph_from_bff() -> None:
    state = make_state()
    blueprint = next(panel for panel in state.panels if panel.panel_id == "workflow_blueprint")

    assert "GET /bff/v9/studio-state" in state.bff_route_allowlist
    assert blueprint.data["node_count"] == 3
    assert blueprint.readonly is True


def test_v9_6_station_agent_profile_is_visible() -> None:
    inspector = next(panel for panel in make_state().panels if panel.panel_id == "agent_station_inspector")

    assert inspector.data["agent_count"] == 3
    assert {profile["agent_id"] for profile in inspector.data["profiles"]} == {"agent-intent", "agent-architect", "agent-security"}


def test_v9_6_runtime_report_and_evidence_chain_are_read_only() -> None:
    state = make_state()
    html_scan = scan_rendered_html(render_workflow_studio_html(state))
    report = next(panel for panel in state.panels if panel.panel_id == "runtime_report")
    evidence = next(panel for panel in state.panels if panel.panel_id == "evidence_chain")

    assert report.readonly is True
    assert evidence.readonly is True
    assert html_scan["hidden_form_present"] is False
    assert html_scan["execution_button_hits"] == []


def test_v9_6_natural_language_optimization_creates_workflow_diff() -> None:
    proposal = make_state().workflow_diff_proposal

    assert proposal.diff_ref.startswith("workflow-diff://v9-6/")
    assert proposal.requires_manual_confirmation is True
    assert proposal.durable_mutation_performed is False
    assert proposal.source == "product_console"


def test_v9_6_manual_confirmation_records_human_authorization_ref() -> None:
    confirmation = make_state().manual_confirmation

    assert confirmation.human_authorization_ref.startswith("human-auth://v9-6/")
    assert confirmation.operation == "workflow.diff.confirm"
    assert confirmation.executes_runtime_action is False
    assert confirmation.audit_ref.startswith("audit://v9-6/manual-confirmation/")


def test_v9_6_manual_confirmation_must_match_current_workflow_diff_proposal() -> None:
    state = make_state()
    stale_confirmation = state.manual_confirmation.__class__(
        human_authorization_ref=state.manual_confirmation.human_authorization_ref,
        tenant_id="other_tenant",
        workspace_id=state.manual_confirmation.workspace_id,
        project_id=state.manual_confirmation.project_id,
        app_id=state.manual_confirmation.app_id,
        actor_id=state.manual_confirmation.actor_id,
        proposal_id="stale-proposal-id",
        operation=state.manual_confirmation.operation,
        target_refs=state.manual_confirmation.target_refs,
        created_at=state.manual_confirmation.created_at,
        expires_at=state.manual_confirmation.expires_at,
        request_id=state.manual_confirmation.request_id,
        correlation_id=state.manual_confirmation.correlation_id,
        audit_ref=state.manual_confirmation.audit_ref,
        source=state.manual_confirmation.source,
        executes_runtime_action=state.manual_confirmation.executes_runtime_action,
    )
    bad_state = state.__class__(
        studio_id=state.studio_id,
        tenant_context=state.tenant_context,
        bff_route_allowlist=state.bff_route_allowlist,
        browser_network_log=state.browser_network_log,
        panels=state.panels,
        workflow_diff_proposal=state.workflow_diff_proposal,
        manual_confirmation=stale_confirmation,
        full_workflow_studio_gate=state.full_workflow_studio_gate,
        global_assertions=state.global_assertions,
        source_refs=state.source_refs,
    )

    with pytest.raises(V96WorkflowStudioError) as excinfo:
        validate_workflow_studio_state(bad_state)

    assert excinfo.value.reason == "confirmation_proposal_mismatch"


def test_v9_6_browser_denylist_blocks_internal_routes() -> None:
    assert browser_route_decision("GET /bff/v9/studio-state")["policy_decision"] == "allow"
    assert browser_route_decision("/v1/rpc")["denial_reason"] == "internal_route_denied"
    assert browser_route_decision("/v1/events/subscribe")["denial_reason"] == "internal_route_denied"
    assert browser_route_decision("/v1/internal/runtime")["denial_reason"] == "internal_route_denied"
    assert browser_route_decision("/v1/internal/workflow-store")["denial_reason"] == "internal_route_denied"


def test_v9_6_hidden_mutation_form_and_false_green_copy_absent() -> None:
    scan = scan_rendered_html(render_workflow_studio_html(make_state()))

    assert scan["status"] == "PASS"
    assert scan["hidden_form_present"] is False
    assert scan["forbidden_copy_hits"] == []
    assert scan["direct_internal_route_hits"] == []


def test_v9_6_source_agent_direct_studio_mutation_denied() -> None:
    with pytest.raises(V96WorkflowStudioError) as excinfo:
        build_workflow_diff_proposal(
            make_context(actor_type="agent"),
            natural_language_goal="直接修改工作流",
            workflow_spec_ref="workflow-spec://v9-6/test",
            target_refs={"workflow_id": "workflow-v9-6"},
        )

    assert excinfo.value.reason == "source_agent_denied"


def test_v9_6_execution_action_or_runtime_truth_panel_is_rejected() -> None:
    state = make_state()
    bad_panel = V96StudioPanel(
        panel_id="runtime_report",
        title="运行报告",
        readonly=True,
        allowed_actions=("view", "Execute"),
        source_refs={},
        data={},
    )
    bad_state = state.__class__(
        studio_id=state.studio_id,
        tenant_context=state.tenant_context,
        bff_route_allowlist=state.bff_route_allowlist,
        browser_network_log=state.browser_network_log,
        panels=(bad_panel,),
        workflow_diff_proposal=state.workflow_diff_proposal,
        manual_confirmation=state.manual_confirmation,
        full_workflow_studio_gate=state.full_workflow_studio_gate,
        global_assertions=state.global_assertions,
        source_refs=state.source_refs,
    )

    with pytest.raises(V96WorkflowStudioError) as excinfo:
        validate_workflow_studio_state(bad_state)

    assert excinfo.value.reason == "execution_action"


def test_v9_6_evidence_script_generates_package() -> None:
    subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_6_workflow_studio_evidence"], check=True)

    required = [
        "index.html",
        "acceptance-data.json",
        "result-summary.md",
        "studio_network_log.json",
        "studio_hidden_form_scan.json",
        "studio_ui_copy_claim_scan.json",
        "manual_confirmation_evidence.json",
        "workflow_diff_proposal.json",
        "studio-state.json",
    ]
    missing = [name for name in required if not (OUT_DIR / name).exists()]
    assert missing == []

    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["stage_id"] == "V9-6"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "real_runtime_fixture"
    assert data["complete_workflow_studio_ready"] is False
