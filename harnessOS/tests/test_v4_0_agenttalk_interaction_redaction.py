"""V4.0-P AgentTalk interaction redaction tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_agenttalk_interaction_dto_error_and_audit_payloads_are_redacted(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_p_redaction"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]

    message = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={
            "content": "Bearer secret-token-value raw_trace_payload raw_artifact_content raw_connector_payload capability_token",
            "created_by": "Authorization: Bearer secret-token-value",
        },
    ).json()
    rejected = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "suggest_patch", "payload": {"raw_connector_payload": "secret-token-value"}},
    ).json()
    state = client.get(f"/bff/instances/{instance_id}/agent/interaction-state{SCOPE_QUERY}").json()
    evidence = client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").json()
    review = client.get(f"/bff/instances/{instance_id}/agent/governance-review{SCOPE_QUERY}").json()

    assert rejected["error"]["code"] == "WORKFLOW_PATCH_INVALID"
    assert state["redaction_status"] == "redacted"
    assert_no_forbidden_text({"message": message, "rejected": rejected, "state": state, "evidence": evidence, "review": review})
