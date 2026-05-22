"""V4.0-J Agent action proposal scope and ownership tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app
from core.protocol.auth import issue_capability_token

from v4_0_reference_support import LOCAL_ORIGIN, OTHER_SCOPE_QUERY, SCOPE_QUERY, build_gateway, seed_reference_console

SECRET = "v4-j-agent-action-secret"


def test_agent_action_routes_enforce_capability_and_scope(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_j_action_auth"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    def token(capabilities: tuple[str, ...], project_id: str = "demo_a") -> str:
        return issue_capability_token(
            app_profile=service.app_registry.get("reference_app"),
            project_id=project_id,
            workspace_id="local",
            capabilities=capabilities,
            allowed_origins=(LOCAL_ORIGIN,),
            secret=SECRET,
        )

    no_agent_actions = {"Authorization": f"Bearer {token(('agent_talk.read',))}", "Origin": LOCAL_ORIGIN}
    read_actions = {"Authorization": f"Bearer {token(('agent_actions.read',))}", "Origin": LOCAL_ORIGIN}
    write_actions = {"Authorization": f"Bearer {token(('agent_actions.write',))}", "Origin": LOCAL_ORIGIN}
    cross_scope = {"Authorization": f"Bearer {token(('agent_actions.read',), project_id='demo_b')}", "Origin": LOCAL_ORIGIN}

    denied = client.get(f"/bff/instances/{instance_id}/agent/action-proposals", headers=no_agent_actions).json()
    assert denied["error"]["code"] == "CAPABILITY_DENIED"

    ok = client.get(f"/bff/instances/{instance_id}/agent/action-proposals", headers=read_actions).json()
    assert ok

    created = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals",
        json={"intent_type": "open_editing_panel"},
        headers=write_actions,
    ).json()
    assert created["workflow_instance_id"] == instance_id

    mismatch = client.get(f"/bff/instances/{instance_id}/agent/action-proposals{OTHER_SCOPE_QUERY}", headers=cross_scope).json()
    assert mismatch["error"]["code"] in {"SCOPE_MISMATCH", "WORKFLOW_INSTANCE_NOT_FOUND"}


def test_agent_action_routes_deny_same_scope_wrong_instance(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="v4_j_action_owner_a"))
    second = asyncio.run(seed_reference_console(service, template_id="v4_j_action_owner_b"))
    client = TestClient(create_app(gateway_service=service))

    first_instance = first["instance"]["workflow_instance_id"]
    wrong_instance = second["instance"]["workflow_instance_id"]
    proposals = client.get(f"/bff/instances/{first_instance}/agent/action-proposals{SCOPE_QUERY}").json()

    wrong = client.get(
        f"/bff/instances/{wrong_instance}/agent/action-proposals/{proposals[0]['proposal_id']}{SCOPE_QUERY}",
    ).json()
    assert wrong["error"]["code"] == "METHOD_NOT_FOUND"
