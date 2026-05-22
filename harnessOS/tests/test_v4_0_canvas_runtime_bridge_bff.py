"""V4.0-H canvas-to-runtime bridge BFF tests."""

from __future__ import annotations

import asyncio
from copy import deepcopy

from fastapi.testclient import TestClient

from apps.api import create_app
from core.apps.scope import ScopeContext

from v4_0_reference_support import SCOPE, SCOPE_QUERY, assert_no_forbidden_text, build_gateway, rpc, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str = "v4_h_canvas_bridge"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def _controlled_catalog_metadata() -> dict:
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


def test_node_add_intent_creates_add_station_proposal_without_runtime_mutation(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_h_node_add")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    before_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "node_add",
            "operation": "add_station",
            "workflow_instance_id": instance_id,
            "payload": {
                "station": {
                    "station_id": "station_canvas_review",
                    "name": "角色一致性检查",
                    "role": "reviewer",
                    "skill_refs": ["video.character_consistency"],
                    "connector_refs": [],
                    "metadata": _controlled_catalog_metadata(),
                }
            },
        },
    ).json()
    after_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()

    assert proposed["operation"] == "add_station"
    assert proposed["source"] == "canvas"
    assert proposed["intent_type"] == "node_add"
    assert [station["station"]["station_id"] for station in after_board["stations"]] == [
        station["station"]["station_id"] for station in before_board["stations"]
    ]
    assert_no_forbidden_text({"proposed": proposed, "after_board": after_board})


def test_edge_add_intent_uses_update_edge_action_add_and_validates_edges(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_h_edge_add"))
    client = TestClient(create_app(gateway_service=service))
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    scope = ScopeContext(**SCOPE)
    draft = service.workflow_repository.get_draft(seeded["template"]["latest_draft_id"], scope=scope)
    next_draft = deepcopy(draft.draft)
    next_draft["stations"].append(
        {
            "station_id": "station_d",
            "name": "Final Review",
            "input_contracts": [{"contract_id": "d_in", "artifact_kind": "dummy.final", "direction": "input", "required": True}],
        }
    )
    asyncio.run(rpc(service, "workflow.template.update_draft", {"workflow_template_id": template_id, "draft": next_draft, "scope": SCOPE}))

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "edge_add",
            "operation": "update_edge",
            "workflow_instance_id": instance_id,
                "payload": {
                    "edge_id": "edge_station_c_to_station_d",
                    "edge_patch": {"action": "add", "from_station_id": "station_c", "to_station_id": "station_d", "order": 3},
                },
        },
    ).json()
    assert proposed["operation"] == "update_edge"

    duplicate = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "edge_add",
            "operation": "update_edge",
            "payload": {
                "edge_id": "edge_duplicate",
                "edge_patch": {"action": "add", "from_station_id": "station_a", "to_station_id": "station_b"},
            },
        },
    ).json()
    assert duplicate["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    self_loop = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "edge_add",
            "operation": "update_edge",
            "payload": {
                "edge_id": "edge_self",
                "edge_patch": {"action": "add", "from_station_id": "station_b", "to_station_id": "station_b"},
            },
        },
    ).json()
    assert self_loop["error"]["code"] == "WORKFLOW_PATCH_INVALID"


def test_inspector_update_intent_maps_to_prompt_patch(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_h_inspector")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_station_prompt",
            "workflow_instance_id": instance_id,
            "payload": {"station_id": "station_b", "prompt_patch": "增强角色一致性和镜头衔接"},
        },
    ).json()

    assert proposed["operation"] == "update_station_prompt"
    assert proposed["source"] == "inspector"
    assert proposed["intent_type"] == "inspector_update"


def test_canvas_bridge_rejects_layout_sensitive_and_unsupported_payload(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_h_reject")
    template_id = seeded["template"]["workflow_template_id"]

    layout = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "node_add",
            "operation": "add_station",
            "payload": {
                "station": {
                    "station_id": "station_bad",
                    "name": "Bad",
                    "metadata": {"node_catalog_id": "character_consistency"},
                    "position": {"x": 1, "y": 2},
                }
            },
        },
    ).json()
    assert layout["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    unsupported = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "node_add",
            "operation": "add_station",
            "payload": {
                "station": {
                    "station_id": "station_bad_catalog",
                    "name": "Bad",
                    "metadata": {"node_catalog_id": "unknown_node"},
                }
            },
        },
    ).json()
    assert unsupported["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    secret = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_connector",
            "payload": {"station_id": "station_b", "connector_patch": {"secret": "secret-token-value"}},
        },
    ).json()
    assert secret["error"]["code"] == "WORKFLOW_PATCH_INVALID"
    assert_no_forbidden_text({"layout": layout, "unsupported": unsupported, "secret": secret})
