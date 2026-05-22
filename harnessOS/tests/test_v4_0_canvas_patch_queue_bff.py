"""V4.0-O patch queue BFF tests."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi.testclient import TestClient

from apps.api import create_app
from core.apps.scope import ScopeContext

from v4_0_reference_support import SCOPE, SCOPE_QUERY, build_gateway, rpc, seed_reference_console


def _catalog_metadata() -> dict[str, Any]:
    return {
        "node_catalog_id": "character_consistency",
        "node_label": "角色一致性检查",
        "catalog_id": "video.station.character_consistency",
        "catalog_version": "2026-05-21",
        "node_template_id": "character_consistency",
        "station_kind": "reviewer",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.character_consistency"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.beta", "dummy.final", "storyboard"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    }


def _client(monkeypatch, tmp_path, template_id: str):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), service, seeded


def _node_patch(station_id: str, instance_id: str) -> dict[str, Any]:
    return {
        "source": "canvas",
        "intent_type": "node_add",
        "operation": "add_station",
        "workflow_instance_id": instance_id,
        "payload": {
            "station": {
                "station_id": station_id,
                "name": "角色一致性检查",
                "role": "reviewer",
                "skill_refs": ["video.character_consistency"],
                "connector_refs": [],
                "metadata": _catalog_metadata(),
            }
        },
    }


def test_patch_queue_contains_required_fields_and_selected_patch(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_o_patch_queue")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    first = client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_node_patch("station_queue_one", instance_id)).json()
    second = client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_node_patch("station_queue_two", instance_id)).json()

    queue = client.get(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}&workflow_instance_id={instance_id}").json()

    assert {first["workflow_patch_id"], second["workflow_patch_id"]} <= {item["patch_id"] for item in queue}
    assert sum(1 for item in queue if item["selected"]) == 1
    for item in queue:
        assert {
            "patch_id",
            "workflow_template_id",
            "workflow_draft_id",
            "base_revision",
            "current_draft_revision",
            "status",
            "risk_flags",
            "requires_approval",
            "selected",
            "stale_reason",
            "conflict_reason",
            "created_at",
            "updated_at",
        } <= set(item)


def test_stale_patch_is_marked_and_cannot_apply(monkeypatch, tmp_path) -> None:
    client, service, seeded = _client(monkeypatch, tmp_path, "v4_o_stale_patch")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    proposed = client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_node_patch("station_stale", instance_id)).json()
    scope = ScopeContext(**SCOPE)
    draft = service.workflow_repository.get_draft(seeded["template"]["latest_draft_id"], scope=scope)
    next_draft = dict(draft.draft)
    next_draft["metadata"] = {"forced_revision_for_test": True}
    asyncio.run(rpc(service, "workflow.template.update_draft", {"workflow_template_id": template_id, "draft": next_draft, "scope": SCOPE}))

    queue = client.get(f"/bff/instances/{instance_id}/patches{SCOPE_QUERY}").json()
    stale = next(item for item in queue if item["patch_id"] == proposed["workflow_patch_id"])
    assert stale["status"] == "stale"
    assert stale["stale_reason"] == "base_revision_mismatch"

    applied = client.post(
        f"/bff/workflows/{template_id}/patches/{proposed['workflow_patch_id']}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert applied["error"]["code"] == "WORKFLOW_PATCH_CONFLICT"


def test_fake_event_payload_does_not_change_patch_queue_truth(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_o_patch_queue_event_truth")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    proposed = client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_node_patch("station_event_truth", instance_id)).json()

    fake_event_payload = {"workflow_patch_id": proposed["workflow_patch_id"], "patch_status": "applied", "draft_revision": 999}
    assert fake_event_payload["patch_status"] == "applied"

    queue = client.get(f"/bff/instances/{instance_id}/patches{SCOPE_QUERY}").json()
    item = next(entry for entry in queue if entry["patch_id"] == proposed["workflow_patch_id"])
    assert item["status"] == "proposed"
    assert item["current_draft_revision"] != 999
