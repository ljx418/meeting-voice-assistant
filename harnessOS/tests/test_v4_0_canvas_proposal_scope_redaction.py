"""V4.0-O canvas proposal redaction and scope tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def test_patch_queue_projection_and_catalog_are_redacted(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_o_redaction")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]

    catalog = client.get(f"/bff/workflows/{template_id}/node-catalog{SCOPE_QUERY}").json()
    projection = client.get(f"/bff/instances/{instance_id}/canvas-projection{SCOPE_QUERY}").json()
    queue = client.get(f"/bff/instances/{instance_id}/patches{SCOPE_QUERY}").json()

    assert_no_forbidden_text({"catalog": catalog, "projection": projection, "queue": queue})
    serialized = str({"catalog": catalog, "projection": projection, "queue": queue})
    for forbidden in ("capability_token", "subscription_token", "Authorization", "Bearer", "raw_trace_payload", "raw_artifact_content", "raw_connector_payload", "raw prompt"):
        assert forbidden not in serialized


def test_same_scope_wrong_template_patch_queue_is_denied(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_o_scope_a"))
    other_seeded = asyncio.run(seed_reference_console(service, template_id="v4_o_scope_b"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    wrong_template_id = other_seeded["template"]["workflow_template_id"]

    response = client.get(f"/bff/workflows/{wrong_template_id}/patches{SCOPE_QUERY}&workflow_instance_id={instance_id}").json()

    assert response["error"]["code"] == "SCOPE_MISMATCH"
