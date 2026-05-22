"""V4.0-O canvas projection freshness tests."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi.testclient import TestClient

from apps.api import create_app
from core.apps.scope import ScopeContext

from v4_0_reference_support import SCOPE, SCOPE_QUERY, build_gateway, rpc, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), service, seeded


def _metadata() -> dict[str, Any]:
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


def _patch(station_id: str, instance_id: str) -> dict[str, Any]:
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
                "metadata": _metadata(),
            }
        },
    }


def test_projection_contains_freshness_fields(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_o_projection_fresh")
    instance_id = seeded["instance"]["workflow_instance_id"]

    projection = client.get(f"/bff/instances/{instance_id}/canvas-projection{SCOPE_QUERY}").json()

    assert projection["freshness_state"] == "fresh"
    assert projection["stale_reasons"] == []
    assert projection["source_refs"]["design_structure"]["draft_revision"] == projection["draft_revision"]
    assert projection["board_status_timestamp"]
    assert projection["patch_queue_revision"]


def test_projection_marks_stale_patch_after_draft_revision_change(monkeypatch, tmp_path) -> None:
    client, service, seeded = _client(monkeypatch, tmp_path, "v4_o_projection_stale")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_patch("station_projection_stale", instance_id))
    scope = ScopeContext(**SCOPE)
    draft = service.workflow_repository.get_draft(seeded["template"]["latest_draft_id"], scope=scope)
    next_draft = dict(draft.draft)
    next_draft["metadata"] = {"projection_stale": True}
    asyncio.run(rpc(service, "workflow.template.update_draft", {"workflow_template_id": template_id, "draft": next_draft, "scope": SCOPE}))

    projection = client.get(f"/bff/instances/{instance_id}/canvas-projection{SCOPE_QUERY}").json()

    assert projection["freshness_state"] in {"stale_draft", "stale_patch"}
    assert set(projection["stale_reasons"]) & {"stale_draft", "stale_patch"}
    assert projection["pending_patch"]["status"] == "stale"


def test_fake_event_payload_does_not_change_projection_truth(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_o_projection_event_truth")
    instance_id = seeded["instance"]["workflow_instance_id"]
    projection = client.get(f"/bff/instances/{instance_id}/canvas-projection{SCOPE_QUERY}").json()
    fake_event_payload = {"draft_revision": 999, "station": {"station_id": "forged"}, "edge": {"edge_id": "forged"}}

    assert fake_event_payload["draft_revision"] == 999
    refreshed = client.get(f"/bff/instances/{instance_id}/canvas-projection{SCOPE_QUERY}").json()

    assert refreshed["draft_revision"] == projection["draft_revision"]
    assert all(node["station_id"] != "forged" for node in refreshed["nodes"])
    assert all(edge["edge_id"] != "forged" for edge in refreshed["edges"])
