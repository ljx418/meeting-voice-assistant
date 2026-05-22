"""V4.0-J Agent action proposal redaction tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_agent_action_proposal_dto_redacts_payload_and_audit(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_j_action_redaction"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]

    response = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={
            "intent_type": "propose_patch",
            "title": "Bearer secret-token-value capability_token",
            "summary": "raw_trace_payload raw_artifact_content raw_connector_payload",
            "payload": {
                "note": "secret-token-value raw_trace_payload raw_artifact_content raw_connector_payload",
            },
        },
    ).json()

    raw = json.dumps(response, ensure_ascii=False)
    assert response["redaction_status"] == "redacted"
    assert_no_forbidden_text(raw)
