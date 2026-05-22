"""V4.0-N canvas editing readiness redaction tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_canvas_patch_payload_rejects_raw_payload_and_authorization_fields(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_n_redaction"))
    client = TestClient(create_app(gateway_service=service))
    template_id = seeded["template"]["workflow_template_id"]

    response = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_connector",
            "payload": {
                "station_id": "station_b",
                "connector_patch": {
                    "Authorization": "Bearer secret-token-value",
                    "raw_connector_payload": "secret-token-value",
                },
            },
        },
    ).json()

    assert response["error"]["code"] == "WORKFLOW_PATCH_INVALID"
    assert_no_forbidden_text(response)


def test_canvas_projection_redacts_runtime_payload_details(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_n_projection_redaction"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]

    projection = client.get(f"/bff/instances/{instance_id}/canvas-projection{SCOPE_QUERY}").json()

    assert projection["redaction_status"] == "redacted"
    assert_no_forbidden_text(projection)
    serialized = str(projection)
    for forbidden in ("raw_artifact_content", "raw_connector_payload", "raw_trace_payload", "Authorization", "Bearer "):
        assert forbidden not in serialized
