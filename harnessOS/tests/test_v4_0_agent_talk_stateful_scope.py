"""V4.0-I Agent assistant scope and capability tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app
from core.protocol.auth import issue_capability_token

from v4_0_reference_support import LOCAL_ORIGIN, OTHER_SCOPE_QUERY, SCOPE_QUERY, build_gateway, seed_reference_console

SECRET = "v4-i-agent-secret"


def test_agent_routes_enforce_capability_and_scope(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_i_agent_auth"))
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

    no_agent = {"Authorization": f"Bearer {token(('workflows.read',))}", "Origin": LOCAL_ORIGIN}
    read_agent = {"Authorization": f"Bearer {token(('agent_talk.read',))}", "Origin": LOCAL_ORIGIN}
    write_agent = {"Authorization": f"Bearer {token(('agent_talk.write',))}", "Origin": LOCAL_ORIGIN}
    cross_scope = {"Authorization": f"Bearer {token(('agent_talk.read',), project_id='demo_b')}", "Origin": LOCAL_ORIGIN}

    denied = client.get(f"/bff/instances/{instance_id}/agent/session", headers=no_agent).json()
    assert denied["error"]["code"] == "CAPABILITY_DENIED"
    ok = client.get(f"/bff/instances/{instance_id}/agent/session", headers=read_agent).json()
    assert ok["workflow_instance_id"] == instance_id
    write_ok = client.post(
        f"/bff/instances/{instance_id}/agent/messages",
        json={"content": "帮我优化当前节点"},
        headers=write_agent,
    ).json()
    assert write_ok["messages"]
    mismatch = client.get(f"/bff/instances/{instance_id}/agent/session{OTHER_SCOPE_QUERY}", headers=cross_scope).json()
    assert mismatch["error"]["code"] in {"SCOPE_MISMATCH", "WORKFLOW_INSTANCE_NOT_FOUND"}


def test_agent_routes_deny_same_scope_wrong_instance(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="v4_i_agent_owner_a"))
    second = asyncio.run(seed_reference_console(service, template_id="v4_i_agent_owner_b"))
    client = TestClient(create_app(gateway_service=service))
    first_instance = first["instance"]["workflow_instance_id"]

    session = client.get(f"/bff/instances/{first_instance}/agent/session{SCOPE_QUERY}").json()
    suggestions = client.get(f"/bff/instances/{first_instance}/agent/suggestions{SCOPE_QUERY}").json()
    wrong_instance = second["instance"]["workflow_instance_id"]
    dismissed = client.post(
        f"/bff/instances/{wrong_instance}/agent/suggestions/{suggestions[0]['suggestion_id']}/dismiss{SCOPE_QUERY}",
    ).json()

    assert session["workflow_instance_id"] == first_instance
    assert dismissed["error"]["code"] == "METHOD_NOT_FOUND"
