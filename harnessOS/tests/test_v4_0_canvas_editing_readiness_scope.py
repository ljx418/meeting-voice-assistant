"""V4.0-N canvas editing readiness scope guard tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import OTHER_SCOPE, OTHER_SCOPE_QUERY, SCOPE_QUERY, build_gateway, seed_reference_console


def test_canvas_patch_wrong_scope_is_denied(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_n_scope_a"))
    asyncio.run(seed_reference_console(service, template_id="v4_n_scope_b", scope=OTHER_SCOPE))
    client = TestClient(create_app(gateway_service=service))
    template_id = seeded["template"]["workflow_template_id"]

    response = client.post(
        f"/bff/workflows/{template_id}/patches{OTHER_SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_station_prompt",
            "payload": {"station_id": "station_b", "prompt_patch": "scope mismatch"},
        },
    ).json()

    assert response["error"]["code"] in {"WORKFLOW_TEMPLATE_NOT_FOUND", "SCOPE_MISMATCH"}


def test_canvas_patch_wrong_template_instance_binding_is_denied(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded_a = asyncio.run(seed_reference_console(service, template_id="v4_n_scope_template_a"))
    seeded_b = asyncio.run(seed_reference_console(service, template_id="v4_n_scope_template_b"))
    client = TestClient(create_app(gateway_service=service))

    response = client.post(
        f"/bff/workflows/{seeded_a['template']['workflow_template_id']}/patches{SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_station_prompt",
            "workflow_instance_id": seeded_b["instance"]["workflow_instance_id"],
            "payload": {"station_id": "station_b", "prompt_patch": "wrong template"},
        },
    ).json()

    assert response["error"]["code"] == "SCOPE_MISMATCH"
