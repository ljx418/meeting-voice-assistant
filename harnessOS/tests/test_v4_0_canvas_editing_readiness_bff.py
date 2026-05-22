"""V4.0-N canvas editing readiness BFF tests."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any

from fastapi.testclient import TestClient

from apps.api import create_app
from core.apps.scope import ScopeContext

from v4_0_reference_support import SCOPE, SCOPE_QUERY, assert_no_forbidden_text, build_gateway, rpc, seed_reference_console


def _catalog_metadata(node_catalog_id: str = "character_consistency") -> dict[str, Any]:
    return {
        "node_catalog_id": node_catalog_id,
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


def _client(monkeypatch, tmp_path, template_id: str = "v4_n_canvas_readiness"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), service, seeded


def test_node_add_intent_uses_controlled_catalog_and_proposal_only(monkeypatch, tmp_path) -> None:
    client, service, seeded = _client(monkeypatch, tmp_path, "v4_n_node_add")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    before_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    before_status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    scope = ScopeContext(**SCOPE)
    before_draft = service.workflow_repository.get_draft(seeded["template"]["latest_draft_id"], scope=scope)

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
                    "metadata": _catalog_metadata(),
                }
            },
        },
    ).json()
    after_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    after_status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    after_draft = service.workflow_repository.get_draft(seeded["template"]["latest_draft_id"], scope=scope)

    assert proposed["operation"] == "add_station"
    assert proposed["source"] == "canvas"
    assert proposed["intent_type"] == "node_add"
    assert before_board["stations"] == after_board["stations"]
    assert before_status == after_status
    assert before_draft.revision == after_draft.revision
    assert_no_forbidden_text({"proposed": proposed, "after_board": after_board})


def test_node_add_rejects_unknown_catalog_unsupported_refs_and_layout(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_n_node_reject")
    template_id = seeded["template"]["workflow_template_id"]

    unsupported_skill = _catalog_metadata()
    unsupported_skill["allowed_skill_refs"] = ["generic.reasoning"]
    payload = {
        "source": "canvas",
        "intent_type": "node_add",
        "operation": "add_station",
        "payload": {
            "station": {
                "station_id": "station_bad",
                "name": "Bad",
                "role": "reviewer",
                "skill_refs": ["generic.reasoning"],
                "connector_refs": [],
                "metadata": unsupported_skill,
            }
        },
    }
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=payload).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    layout_payload = deepcopy(payload)
    layout_payload["payload"]["station"]["metadata"] = _catalog_metadata()
    layout_payload["payload"]["station"]["selectedNode"] = "station_bad"
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=layout_payload).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    unknown_payload = deepcopy(payload)
    unknown_payload["payload"]["station"]["metadata"] = _catalog_metadata("unknown_node")
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=unknown_payload).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"


def test_edge_add_validates_cycle_missing_duplicate_and_contracts(monkeypatch, tmp_path) -> None:
    client, service, seeded = _client(monkeypatch, tmp_path, "v4_n_edge")
    template_id = seeded["template"]["workflow_template_id"]
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

    valid = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "edge_add",
            "operation": "update_edge",
            "payload": {"edge_id": "edge_c_d", "edge_patch": {"action": "add", "from_station_id": "station_c", "to_station_id": "station_d"}},
        },
    ).json()
    assert valid["operation"] == "update_edge"

    cases = [
        {"edge_id": "edge_self", "edge_patch": {"action": "add", "from_station_id": "station_b", "to_station_id": "station_b"}},
        {"edge_id": "edge_dup", "edge_patch": {"action": "add", "from_station_id": "station_a", "to_station_id": "station_b"}},
        {"edge_id": "edge_missing", "edge_patch": {"action": "add", "from_station_id": "station_a", "to_station_id": "station_missing"}},
        {"edge_id": "edge_cycle", "edge_patch": {"action": "add", "from_station_id": "station_c", "to_station_id": "station_a"}},
        {"edge_id": "edge_bad_contract", "edge_patch": {"action": "add", "from_station_id": "station_a", "to_station_id": "station_c"}},
    ]
    for payload in cases:
        response = client.post(
            f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
            json={"source": "canvas", "intent_type": "edge_add", "operation": "update_edge", "payload": payload},
        ).json()
        assert response["error"]["code"] == "WORKFLOW_PATCH_INVALID"


def test_canvas_projection_is_redacted_ui_only_read_model(monkeypatch, tmp_path) -> None:
    client, _service, seeded = _client(monkeypatch, tmp_path, "v4_n_projection")
    instance_id = seeded["instance"]["workflow_instance_id"]

    projection = client.get(f"/bff/instances/{instance_id}/canvas-projection{SCOPE_QUERY}").json()

    assert projection["workflow_instance_id"] == instance_id
    assert projection["draft_revision"] >= 1
    assert projection["source_refs"]["design_structure"]["kind"] == "WorkflowDraft"
    assert projection["source_refs"]["runtime_state"]["kind"] == "BoardDTO/InstanceStatusDTO"
    assert projection["source_refs"]["pending_diff"]["kind"] == "PatchDiffDTO"
    serialized = str(projection)
    for forbidden in ("raw_trace_payload", "raw_connector_payload", "raw_artifact_content", "position", "viewport", "selectedNode"):
        assert forbidden not in serialized
    assert_no_forbidden_text(projection)
