"""V4.0-L Agent handoff lifecycle route tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def _patch_handoff(client: TestClient, instance_id: str, patch_id: str) -> dict:
    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    return client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()


def test_handoff_open_dismiss_list_and_audit(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_lifecycle"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    client = TestClient(create_app(gateway_service=service))

    handoff = _patch_handoff(client, instance_id, patch_id)
    opened = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}").json()
    assert opened["status"] == "opened"

    listed = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs{SCOPE_QUERY}").json()
    assert [item["handoff_id"] for item in listed] == [handoff["handoff_id"]]

    audit = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}/audit{SCOPE_QUERY}").json()
    assert [item["event_type"] for item in audit] == ["handoff_created", "handoff_opened"]

    dismissed = client.post(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}/dismiss{SCOPE_QUERY}").json()
    assert dismissed["status"] == "dismissed"
    dismissed_again = client.post(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}/dismiss{SCOPE_QUERY}").json()
    assert dismissed_again["status"] == "dismissed"


def test_terminal_handoff_cannot_execute(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_terminal"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    client = TestClient(create_app(gateway_service=service))

    handoff = _patch_handoff(client, instance_id, patch_id)
    client.post(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}/dismiss{SCOPE_QUERY}")
    applied = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={
            "workflow_instance_id": instance_id,
            "user_confirmed": True,
            "source": "editing_panel",
            "proposal_id": handoff["proposal_id"],
            "handoff_id": handoff["handoff_id"],
        },
    ).json()
    assert applied["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

