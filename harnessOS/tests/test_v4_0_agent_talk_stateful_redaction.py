"""V4.0-I Agent assistant redaction tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import FORBIDDEN_TEXT, SCOPE_QUERY, build_gateway, seed_reference_console


def test_agent_state_dto_redacts_raw_payloads(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_i_agent_redaction_file"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]

    response = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={
            "content": "capability_token subscription_token Authorization Bearer secret-token-value raw_trace_payload raw_artifact_content raw_connector_payload",
            "created_by": "secret-token-value",
        },
    ).json()
    suggestions = client.get(f"/bff/instances/{instance_id}/agent/suggestions{SCOPE_QUERY}").json()

    raw = json.dumps({"response": response, "suggestions": suggestions}, ensure_ascii=False)
    for forbidden in FORBIDDEN_TEXT:
        assert forbidden not in raw
    assert "[redacted]" in raw
