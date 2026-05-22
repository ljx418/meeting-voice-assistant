"""V4.0-O controlled node catalog versioning tests."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.api.routers import bff

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def _metadata() -> dict[str, Any]:
    return {
        "node_catalog_id": "character_consistency",
        "node_label": "角色一致性检查",
        **deepcopy(bff.NODE_CATALOG_CONTRACTS["character_consistency"]),
    }


def _payload(metadata: dict[str, Any], instance_id: str) -> dict[str, Any]:
    return {
        "source": "canvas",
        "intent_type": "node_add",
        "operation": "add_station",
        "workflow_instance_id": instance_id,
        "payload": {
            "station": {
                "station_id": "station_catalog_check",
                "name": "角色一致性检查",
                "role": "reviewer",
                "skill_refs": ["video.character_consistency"],
                "connector_refs": [],
                "metadata": metadata,
            }
        },
    }


def test_bff_catalog_returns_controlled_contract_without_raw_payload(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_catalog")
    template_id = seeded["template"]["workflow_template_id"]

    catalog = client.get(f"/bff/workflows/{template_id}/node-catalog{SCOPE_QUERY}").json()

    item = next(entry for entry in catalog if entry["node_template_id"] == "character_consistency")
    assert item["catalog_version"] == "2026-05-21"
    assert item["station_kind"] == "reviewer"
    assert item["allowed_skill_refs"] == ["video.character_consistency"]
    serialized = str(catalog)
    for forbidden in ("Authorization", "token", "raw_trace_payload", "raw_connector_payload", "raw_artifact_content"):
        assert forbidden not in serialized


def test_catalog_version_mismatch_and_unknown_node_block_proposal(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_catalog_mismatch")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]

    mismatch = _metadata()
    mismatch["catalog_version"] = "stale-version"
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_payload(mismatch, instance_id)).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    unknown = _metadata()
    unknown["node_catalog_id"] = "unknown_node"
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_payload(unknown, instance_id)).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"


def test_unsupported_connector_and_skill_refs_are_rejected(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_catalog_refs")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]

    skill_payload = _payload(_metadata(), instance_id)
    skill_payload["payload"]["station"]["skill_refs"] = ["generic.reasoning"]
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=skill_payload).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    connector_payload = _payload(_metadata(), instance_id)
    connector_payload["payload"]["station"]["connector_refs"] = ["http"]
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=connector_payload).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"
