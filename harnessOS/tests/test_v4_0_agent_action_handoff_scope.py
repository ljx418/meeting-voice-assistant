"""V4.0-K Agent action handoff scope and capability tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app
from core.protocol.auth import issue_capability_token

from v4_0_reference_support import LOCAL_ORIGIN, OTHER_SCOPE_QUERY, SCOPE_QUERY, build_gateway, seed_reference_console

SECRET = "v4-k-handoff-secret"


def test_handoff_routes_enforce_capability_and_scope(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_k_handoff_scope"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
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

    write_headers = {"Authorization": f"Bearer {token(('agent_actions.write', 'agent_handoffs.write'))}", "Origin": LOCAL_ORIGIN}
    read_headers = {"Authorization": f"Bearer {token(('agent_handoffs.read',))}", "Origin": LOCAL_ORIGIN}
    missing_headers = {"Authorization": f"Bearer {token(('agent_actions.read',))}", "Origin": LOCAL_ORIGIN}
    cross_headers = {"Authorization": f"Bearer {token(('agent_actions.write', 'agent_handoffs.write'), project_id='demo_b')}", "Origin": LOCAL_ORIGIN}

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
        headers=write_headers,
    ).json()

    missing = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
        headers=missing_headers,
    ).json()
    assert missing["error"]["code"] == "CAPABILITY_DENIED"

    cross = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{OTHER_SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
        headers=cross_headers,
    ).json()
    assert cross["error"]["code"] in {"SCOPE_MISMATCH", "WORKFLOW_INSTANCE_NOT_FOUND"}

    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
        headers=write_headers,
    ).json()
    fetched = client.get(
        f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}",
        headers=read_headers,
    ).json()
    assert fetched["handoff_id"] == handoff["handoff_id"]


def test_handoff_expired_is_rejected(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_k_handoff_expired"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    client = TestClient(create_app(gateway_service=service))

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()
    from apps.api.routers import bff

    bff._AGENT_HANDOFF_REPOSITORY.expire(handoff["handoff_id"], reason="test_expired")
    expired = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}").json()
    assert expired["status"] == "expired"
    assert expired["inactive_reason"] == "test_expired"
