"""V4.0-O canvas edge contract validation tests."""

from __future__ import annotations

import asyncio
from copy import deepcopy

from fastapi.testclient import TestClient

from apps.api import create_app
from core.apps.scope import ScopeContext

from v4_0_reference_support import SCOPE, SCOPE_QUERY, build_gateway, rpc, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    scope = ScopeContext(**SCOPE)
    draft = service.workflow_repository.get_draft(seeded["template"]["latest_draft_id"], scope=scope)
    next_draft = deepcopy(draft.draft)
    next_draft["stations"].append(
        {
            "station_id": "station_d",
            "name": "Final Review",
            "input_contracts": [{"contract_id": "d_in", "artifact_kind": "dummy.final", "direction": "input", "schema_ref": "schema://final"}],
        }
    )
    asyncio.run(rpc(service, "workflow.template.update_draft", {"workflow_template_id": seeded["template"]["workflow_template_id"], "draft": next_draft, "scope": SCOPE}))
    return TestClient(create_app(gateway_service=service)), seeded


def _edge(payload: dict) -> dict:
    return {"source": "canvas", "intent_type": "edge_add", "operation": "update_edge", "payload": payload}


def test_valid_edge_uses_update_edge_only(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_edge_valid")
    template_id = seeded["template"]["workflow_template_id"]

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json=_edge({"edge_id": "edge_c_d", "edge_patch": {"action": "add", "from_station_id": "station_c", "to_station_id": "station_d", "artifact_contract": {"artifact_kind": "dummy.final", "schema_ref": "schema://final"}}}),
    ).json()

    assert proposed["operation"] == "update_edge"


def test_invalid_edges_are_rejected(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_edge_invalid")
    template_id = seeded["template"]["workflow_template_id"]
    cases = [
        {"edge_id": "edge_self", "edge_patch": {"action": "add", "from_station_id": "station_b", "to_station_id": "station_b"}},
        {"edge_id": "edge_dup", "edge_patch": {"action": "add", "from_station_id": "station_a", "to_station_id": "station_b"}},
        {"edge_id": "edge_missing_source", "edge_patch": {"action": "add", "from_station_id": "missing", "to_station_id": "station_b"}},
        {"edge_id": "edge_missing_target", "edge_patch": {"action": "add", "from_station_id": "station_b", "to_station_id": "missing"}},
        {"edge_id": "edge_cycle", "edge_patch": {"action": "add", "from_station_id": "station_c", "to_station_id": "station_a"}},
        {"edge_id": "edge_bad_contract", "edge_patch": {"action": "add", "from_station_id": "station_a", "to_station_id": "station_d", "artifact_contract": {"artifact_kind": "dummy.alpha", "schema_ref": "schema://wrong"}}},
        {"edge_id": "edge_wrong_draft", "edge_patch": {"action": "remove"}},
        {"edge_id": "edge_a_b", "edge_patch": {"action": "update", "artifact_contract": {"artifact_kind": "dummy.final", "schema_ref": "schema://wrong"}}},
    ]
    for payload in cases:
        response = client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_edge(payload)).json()
        assert response["error"]["code"] == "WORKFLOW_PATCH_INVALID"
