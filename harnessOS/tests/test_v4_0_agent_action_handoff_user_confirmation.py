"""V4.0-K handoff user-confirmation guard tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def _handoff_for_patch(client: TestClient, instance_id: str, patch_id: str) -> dict:
    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    return client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()


def test_user_confirmed_patch_apply_requires_complete_handoff_pair(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_k_handoff_apply"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    handoff = _handoff_for_patch(client, instance_id, patch_id)

    source_agent = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "agent", "proposal_id": handoff["proposal_id"], "handoff_id": handoff["handoff_id"]},
    ).json()
    assert source_agent["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

    missing_pair = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel", "proposal_id": handoff["proposal_id"]},
    ).json()
    assert missing_pair["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

    ok = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={
            "workflow_instance_id": instance_id,
            "user_confirmed": True,
            "source": "editing_panel",
            "proposal_id": handoff["proposal_id"],
            "handoff_id": handoff["handoff_id"],
        },
    ).json()
    assert ok["operation"] == "workflow.patch.apply"
    assert ok["resource"]["status"] == "applied"


def test_approval_and_context_execution_accept_user_confirmed_handoff(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_k_handoff_ops"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    approval_id = seeded["approval"]["approval_id"]

    approval_proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_approval_panel", "target_panel": "approval"},
    ).json()
    approval_handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{approval_proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "approval_panel", "approval_id": approval_id},
    ).json()
    approved = client.post(
        f"/bff/instances/{instance_id}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={
            "decision": "approve",
            "source": "approval_panel",
            "user_confirmed": True,
            "proposal_id": approval_handoff["proposal_id"],
            "handoff_id": approval_handoff["handoff_id"],
        },
    ).json()
    assert approved["operation"] == "approval.respond"

    context_proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_context_panel", "target_panel": "context"},
    ).json()
    context_handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{context_proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "context_panel", "target_path": "business.agent_note", "suggested_form_prefill": {"value": "ok"}},
    ).json()
    context = client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json()
    updated = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={
            "op": "set",
            "path": "business.agent_note",
            "value": "ok",
            "expected_revision": context["revision"],
            "source": "context_panel",
            "user_confirmed": True,
            "proposal_id": context_handoff["proposal_id"],
            "handoff_id": context_handoff["handoff_id"],
        },
    ).json()
    assert updated["operation"] == "workflow.context.update"
    assert updated["resource"]["business"]["agent_note"] == "ok"
