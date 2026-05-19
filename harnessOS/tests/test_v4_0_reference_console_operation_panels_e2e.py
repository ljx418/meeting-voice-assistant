"""V4.0-E operation panel E2E tests against the reference runtime fixture."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_approval_panel_response_advances_workflow_bound_station(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    approval_id = seeded["approval"]["approval_id"]
    client = TestClient(create_app(gateway_service=service))

    before_status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    before_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    assert before_status["status"] == "waiting_approval"
    assert any(station["status"] == "waiting_approval" for station in before_board["stations"])

    denied = client.post(
        f"/bff/instances/{instance_id}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={"decision": "approve", "source": "agent", "user_confirmed": True},
    )
    assert denied.json()["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

    approved = client.post(
        f"/bff/instances/{instance_id}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={"decision": "approve", "source": "approval_panel", "user_confirmed": True},
    ).json()
    assert approved["status"] == "approved"
    assert approved["workflow_side_effect"]["status"] in {"applied", "recovered"}

    after_status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    after_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    assert after_status["status"] == "completed"
    assert not any(station["status"] == "waiting_approval" for station in after_board["stations"])
    assert_no_forbidden_text({"approved": approved, "status": after_status, "board": after_board})


def test_context_update_and_business_event_binding_apply_without_runtime_bypass(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    context = client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json()
    assert context["business"]["selected_scene"] == "scene_001"
    invalid = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={"op": "set", "path": "system.owner", "value": "bad"},
    )
    assert invalid.json()["error"]["code"] == "WORKFLOW_CONTEXT_SCOPE_MISMATCH"
    updated = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={"op": "set", "path": "business.review_note", "value": "ready", "expected_revision": context["revision"]},
    ).json()
    assert updated["resource"]["business"]["review_note"] == "ready"
    stale = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={"op": "set", "path": "business.review_note", "value": "stale", "expected_revision": context["revision"]},
    )
    assert stale.json()["error"]["code"] == "WORKFLOW_CONTEXT_CONFLICT"

    event_body = {
        "event_type": "business.video.scene.selected",
        "event_id": "evt_reference_scene_twice",
        "payload": {"scene_id": "scene_002", "secret": "secret-token-value"},
        "binding": {
            "target_path": "context.business.selected_scene",
            "payload_path": "event.payload.scene_id",
            "mode": "set",
        },
    }
    first = client.post(f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}", json=event_body).json()
    second = client.post(f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}", json=event_body).json()
    assert first["resource"]["context"]["business"]["selected_scene"] == "scene_002"
    assert second["idempotent"] is True
    status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    assert status["status"] == "waiting_approval"
    assert_no_forbidden_text({"first": first, "second": second, "status": status})
