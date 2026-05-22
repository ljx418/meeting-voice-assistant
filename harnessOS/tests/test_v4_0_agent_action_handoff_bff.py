"""V4.0-K Agent action handoff BFF route tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str = "v4_k_handoff"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), service, seeded


def test_handoff_creates_dto_only_and_does_not_execute_mutation(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_k_handoff_dto")
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id, "suggested_form_prefill": {"note": "review diff"}},
    ).json()

    assert handoff["proposal_id"] == proposal["proposal_id"]
    assert handoff["target_panel"] == "editing_panel"
    assert handoff["target_resource"]["workflow_patch_id"] == patch_id
    assert handoff["status"] == "active"
    assert handoff["redaction_status"] == "redacted"

    patch_after_handoff = client.get(f"/bff/instances/{instance_id}/patches/{patch_id}/diff{SCOPE_QUERY}").json()
    assert patch_after_handoff["workflow_patch_id"] == patch_id
    assert seeded["patch"]["status"] == "proposed"
    assert_no_forbidden_text({"proposal": proposal, "handoff": handoff, "diff": patch_after_handoff})


def test_handoff_get_requires_instance_ownership(monkeypatch, tmp_path) -> None:
    client, service, first = _client(monkeypatch, tmp_path, "v4_k_handoff_owner_a")
    second = asyncio.run(seed_reference_console(service, template_id="v4_k_handoff_owner_b"))
    first_instance = first["instance"]["workflow_instance_id"]
    second_instance = second["instance"]["workflow_instance_id"]
    patch_id = first["patch"]["workflow_patch_id"]

    proposal = client.post(
        f"/bff/instances/{first_instance}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    handoff = client.post(
        f"/bff/instances/{first_instance}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()

    wrong_instance = client.get(
        f"/bff/instances/{second_instance}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}",
    ).json()
    assert wrong_instance["error"]["code"] == "METHOD_NOT_FOUND"


def test_handoff_target_panel_mismatch_rejected(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_k_handoff_panel")
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    mismatch = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "approval_panel"},
    ).json()
    assert mismatch["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
