"""V4.0-L Agent handoff stale and blocked guard tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def _proposal(client: TestClient, instance_id: str, body: dict) -> dict:
    return client.post(f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}", json=body).json()


def test_editing_handoff_stale_after_patch_status_changes(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_patch_stale"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    proposal = _proposal(client, instance_id, {"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"})
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()
    client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    )
    stale = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}").json()
    assert stale["status"] == "stale"
    assert stale["inactive_reason"] == "patch_status_applied"


def test_high_risk_editing_handoff_is_blocked(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_blocked"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    proposal = _proposal(
        client,
        instance_id,
        {
            "intent_type": "open_editing_panel",
            "workflow_patch_id": patch_id,
            "target_panel": "editing",
            "requires_approval": True,
            "risk_flags": ["approval_removed"],
        },
    )
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()
    blocked = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}").json()
    assert blocked["status"] == "blocked"
    assert blocked["inactive_reason"] == "patch_requires_approval"


def test_context_handoff_stale_after_revision_changes(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_context_stale"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]

    proposal = _proposal(client, instance_id, {"intent_type": "open_context_panel", "target_panel": "context"})
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "context_panel", "target_path": "business.agent_note"},
    ).json()
    context = client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json()
    client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={"op": "set", "path": "business.other_note", "value": "changed", "expected_revision": context["revision"]},
    )
    stale = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}").json()
    assert stale["status"] == "stale"
    assert stale["inactive_reason"] == "context_revision_changed"

