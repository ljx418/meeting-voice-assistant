"""V4.0-L Agent handoff recovery and ownership tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from core.apps.scope import ScopeContext

from v4_0_reference_support import SCOPE, SCOPE_QUERY, build_gateway, seed_reference_console


def test_recovery_read_marks_opened_without_mutation(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_recovery"))
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

    recovered = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}").json()
    patch = service.workflow_repository.get_patch(patch_id, scope=ScopeContext(**SCOPE))
    assert recovered["status"] == "opened"
    assert patch.status == "proposed"


def test_same_scope_wrong_instance_handoff_denied(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_recovery_a"))
    second = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_recovery_b"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = first["instance"]["workflow_instance_id"]
    other_instance_id = second["instance"]["workflow_instance_id"]
    patch_id = first["patch"]["workflow_patch_id"]

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()
    denied = client.get(f"/bff/instances/{other_instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}").json()
    assert denied["error"]["code"] in {"METHOD_NOT_FOUND", "SCOPE_MISMATCH"}
