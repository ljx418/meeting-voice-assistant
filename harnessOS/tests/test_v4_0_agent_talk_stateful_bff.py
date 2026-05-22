"""V4.0-I stateful Agent assistant BFF route tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str = "v4_i_agent_talk"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def test_agent_session_message_and_suggestion_routes(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_i_agent_routes")
    instance_id = seeded["instance"]["workflow_instance_id"]

    session = client.get(f"/bff/instances/{instance_id}/agent/session{SCOPE_QUERY}").json()
    assert session["workflow_instance_id"] == instance_id
    assert session["redaction_status"] == "redacted"
    assert session["messages"] == []

    message = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={"content": "帮我优化当前节点", "created_by": "user_console"},
    ).json()
    assert [item["role"] for item in message["messages"]] == ["user", "assistant"]
    assert message["suggestions"]
    assert all(item["action_intent"]["executable"] is False for item in message["suggestions"])
    assert {item["action_intent"]["action"] for item in message["suggestions"]} <= {
        "explain_workflow",
        "show_context_summary",
            "suggest_patch",
            "show_patch_diff",
            "show_approval_notice",
        }

    suggestions = client.get(f"/bff/instances/{instance_id}/agent/suggestions{SCOPE_QUERY}").json()
    assert suggestions
    dismissed = client.post(
        f"/bff/instances/{instance_id}/agent/suggestions/{suggestions[0]['suggestion_id']}/dismiss{SCOPE_QUERY}",
    ).json()
    assert dismissed["status"] == "dismissed"
    assert_no_forbidden_text({"session": session, "message": message, "suggestions": suggestions, "dismissed": dismissed})


def test_agent_message_rejects_executable_action_intent(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_i_agent_non_exec")
    instance_id = seeded["instance"]["workflow_instance_id"]

    blocked = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={"content": "请自动应用", "action_intent": {"action": "apply_patch"}},
    ).json()

    assert blocked["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert_no_forbidden_text(blocked)


def test_agent_routes_are_redacted(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_i_agent_redaction")
    instance_id = seeded["instance"]["workflow_instance_id"]

    message = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={
            "content": "Bearer secret-token-value raw_trace_payload raw_artifact_content raw_connector_payload capability_token",
            "created_by": "Authorization: Bearer secret-token-value",
        },
    ).json()

    assert_no_forbidden_text(message)
