"""V4.6 governed Agent workflow builder tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app
from core.workflows.v4_6_agent_builder import assert_no_forbidden_text, create_builder_session, generate_workflow_draft
from scripts.v4_6_agent_builder_evidence import DEFAULT_OUTPUT_DIR, FORBIDDEN_TERMS, generate_agent_builder_evidence
from v4_0_reference_support import SCOPE_QUERY, build_gateway


REQUEST_PATH = Path("tests/fixtures/v4_6/agent_builder/user_request.md")


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    return TestClient(create_app(gateway_service=build_gateway(tmp_path)))


def test_agent_builder_session_generates_clarifying_questions_without_mutation() -> None:
    session = create_builder_session(user_request=REQUEST_PATH.read_text(encoding="utf-8"), scope={"app_id": "reference_app"})

    assert session["clarifying_questions"]
    assert session["agent_mutation_allowed"] is False
    assert session["agent_capabilities"] == ["propose", "explain", "handoff", "navigate"]
    assert_no_forbidden_text(session)


def test_agent_builder_draft_is_proposal_only() -> None:
    session = create_builder_session(user_request=REQUEST_PATH.read_text(encoding="utf-8"))
    draft = generate_workflow_draft(session)

    assert draft["status"] == "proposed"
    assert draft["agent_mutation_allowed"] is False
    assert all(item["requires_user_confirmed_apply"] is True for item in draft["patch_operations"])
    assert "artifact_publish" in draft["preview_nodes"]
    assert_no_forbidden_text(draft)


def test_agent_builder_bff_flow_is_proposal_explain_handoff_only(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    session = client.post(
        f"/bff/v4_6/agent-builder/sessions{SCOPE_QUERY}",
        json={"user_request": REQUEST_PATH.read_text(encoding="utf-8")},
    ).json()
    draft = client.post(f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/draft{SCOPE_QUERY}", json={}).json()
    explain = client.get(
        f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/explain/{draft['proposal_id']}{SCOPE_QUERY}"
    ).json()
    repair = client.post(
        f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/debug-repair{SCOPE_QUERY}",
        json={"failed_station_id": "markdown_parse"},
    ).json()
    handoff = client.post(
        f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/handoff{SCOPE_QUERY}",
        json={"proposal_id": draft["proposal_id"], "target_panel": "editing_panel"},
    ).json()

    assert draft["status"] == "proposed"
    assert explain["read_only"] is True
    assert repair["status"] == "proposed"
    assert handoff["operation_executed"] is False
    assert handoff["requires_user_confirmation"] is True
    assert_no_forbidden_text({"session": session, "draft": draft, "explain": explain, "repair": repair, "handoff": handoff})


def test_agent_builder_bff_rejects_agent_source_as_mutation_context(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    denied = client.post(
        f"/bff/v4_6/agent-builder/sessions{SCOPE_QUERY}",
        json={"user_request": "test", "source": "agent"},
    ).json()
    assert denied["error"]["code"] == "METHOD_FORBIDDEN"


def test_agent_builder_evidence_package_can_be_rebuilt_and_is_redacted(tmp_path) -> None:
    manifest = generate_agent_builder_evidence(tmp_path)

    assert manifest["status"] == "completed"
    assert "builder_report.html" in manifest["files"]
    required = {
        "tui-transcript.txt",
        "builder-session.json",
        "workflow-draft-proposal.json",
        "workflow-plan-explanation.json",
        "debug-repair-proposal.json",
        "handoff.json",
        "builder_report.html",
        "result-summary.md",
    }
    assert required.issubset({path.name for path in DEFAULT_OUTPUT_DIR.iterdir() if path.is_file()})
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DEFAULT_OUTPUT_DIR.iterdir() if path.is_file())
    for term in FORBIDDEN_TERMS:
        assert term not in combined
    for forbidden_copy in ["自动应用", "自动发布", "Agent 已执行", "Agent 已发布"]:
        assert forbidden_copy not in combined
    assert "<form" not in combined.lower()


def test_agent_builder_bff_has_no_execute_or_direct_v1_route() -> None:
    from apps.api.routers import bff_v46

    text = json.dumps([route.path for route in bff_v46.router.routes])
    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text
    assert "/agent/execute" not in text
    assert "/apply" not in text
    assert "/run" not in text

