"""V4.0-O Inspector mapping V2 tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def _inspector_payload(payload: dict) -> dict:
    return {
        "source": "inspector",
        "intent_type": "inspector_update",
        "operation": "update_station_prompt",
        "payload": payload,
    }


def test_inspector_update_allows_prompt_fields_only(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_inspector")
    template_id = seeded["template"]["workflow_template_id"]

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json=_inspector_payload({"station_id": "station_b", "prompt_patch": "增强角色一致性", "prompt_ref": "prompt://station_b"}),
    ).json()

    assert proposed["operation"] == "update_station_prompt"
    assert proposed["source"] == "inspector"


def test_inspector_rejects_unknown_layout_and_sensitive_fields(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_inspector_reject")
    template_id = seeded["template"]["workflow_template_id"]

    cases = [
        {"station_id": "station_b", "prompt_patch": "x", "unknown": "field"},
        {"station_id": "station_b", "prompt_patch": "x", "viewport": {"x": 1}},
        {"station_id": "station_b", "prompt_patch": "x", "token": "secret"},
        {"station_id": "station_b", "prompt_patch": "x", "raw_trace_payload": {"secret": True}},
        {"station_id": "station_b", "prompt_patch": "x", "raw_artifact_content": "raw"},
        {"station_id": "station_b", "prompt_patch": "x", "raw_connector_payload": {"Authorization": "Bearer x"}},
        {"station_id": "station_b", "prompt_patch": "x", "rawTracePayload": {"secret": True}},
        {"station_id": "station_b", "prompt_patch": "x", "rawArtifactContent": "raw"},
        {"station_id": "station_b", "prompt_patch": "x", "rawConnectorPayload": {"Authorization": "Bearer x"}},
    ]
    for payload in cases:
        response = client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=_inspector_payload(payload)).json()
        assert response["error"]["code"] == "WORKFLOW_PATCH_INVALID"


def test_inspector_connector_and_quality_allowlists(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_inspector_allowlists")
    template_id = seeded["template"]["workflow_template_id"]

    bad_connector = {
        "source": "inspector",
        "intent_type": "inspector_update",
        "operation": "update_connector",
        "payload": {"station_id": "station_b", "connector_refs": ["unknown_connector"], "connector_patch": {}},
    }
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=bad_connector).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    bad_quality = {
        "source": "inspector",
        "intent_type": "inspector_update",
        "operation": "update_quality_rule",
        "payload": {"quality_contract_id": "missing", "quality_patch": {"threshold": 2}},
    }
    assert client.post(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}", json=bad_quality).json()["error"]["code"] == "WORKFLOW_PATCH_INVALID"
