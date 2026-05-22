"""V4.0-J Agent action proposal BFF route tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str = "v4_j_agent_actions"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def test_agent_action_proposal_lifecycle_routes(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_j_action_routes")
    instance_id = seeded["instance"]["workflow_instance_id"]

    listed = client.get(f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}").json()
    assert listed
    assert {item["policy_class"] for item in listed} <= {"display_only", "navigation", "proposal_only"}
    assert all(item["lifecycle"] == "proposed" for item in listed)

    created = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "title": "跳转编辑面板", "summary": "请用户进入编辑面板确认。"},
    ).json()
    assert created["policy_class"] == "navigation"
    assert created["lifecycle"] == "proposed"

    fetched = client.get(
        f"/bff/instances/{instance_id}/agent/action-proposals/{created['proposal_id']}{SCOPE_QUERY}",
    ).json()
    assert fetched["proposal_id"] == created["proposal_id"]

    dismissed = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{created['proposal_id']}/dismiss{SCOPE_QUERY}",
    ).json()
    assert dismissed["lifecycle"] == "dismissed"
    assert_no_forbidden_text({"listed": listed, "created": created, "dismissed": dismissed})
